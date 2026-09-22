"""
MTA Assistant - v1.6.0  ( Made By AmooReza )
A PySide6 Windows application for MTA:SA players.
"""

import io
import sys
import shutil
import winreg
from pathlib import Path

from PySide6.QtCore import Qt, QStandardPaths, QThread, Signal
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFileDialog, QMessageBox, QMainWindow, QWidget,
    QStackedWidget, QTableWidget, QTableWidgetItem, QHeaderView, QFrame,
    QRadioButton, QButtonGroup, QProgressBar
)

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
APP_NAME = "MTA Assistant"
APP_VERSION = "1.6.0"
APP_AUTHOR = "AmooReza"
APP_TITLE = f"{APP_NAME} — v{APP_VERSION}  ( Made By {APP_AUTHOR} )"

REG_PATH = r"Software\MTA Assistant"
REG_VALUE_FOLDER = "MTAFolder"
REG_VALUE_NAME = "GameName"
REG_VALUE_FACTION = "Faction"
REG_VALUE_RANK = "Rank"

MAX_IMAGE_BYTES = 250 * 1024  # 250 KB

# --- Static factions (fixed prices per category) ---
FACTIONS = {
    "Police Federal": [
        ("Arrest",  "arrest",  5000),
        ("Kill",    "kill",    2000),
        ("Shift",   "shift",   5000),
        ("TakeGun", "takegun", 8000),
        ("Wanted",  "wanted",  6000),
    ],
    "National Guard": [
        ("Shift",   "shift",   7500),
        ("Arrest",  "arrest",  2000),
        ("Wanted",  "wanted",  2000),
        ("TakeGun", "takegun", 2000),
        ("Kill",    "kill",    4000),
    ],
    "Police Department": [
        ("Wanted",  "wanted",  2000),
        ("Kill",    "kill",    1000),
        ("Arrest",  "arrest",  6000),
        ("Shift",   "shift",   8000),
        ("TakeGun", "takegun", 3000),
        ("Ticket",  "ticket",  10000),
    ],
}

# --- Rank-based factions (prices depend on rank) ---
MEDIC_RANKS = {
    "Rank 1": [("Heal", "heal", 6300), ("Service", "service", 5000)],
    "Rank 2": [("Heal", "heal", 7000), ("Service", "service", 6000)],
    "Rank 3": [("Heal", "heal", 8000), ("Service", "service", 6000)],
    "Rank 4": [("Heal", "heal", 9500), ("Service", "service", 7500)],
    "Rank 5": [("Heal", "heal", 11000), ("Service", "service", 9000)],
}

HITMAN_RANKS = {
    "Rank 1": [("Contract", "contract", 15000)],
    "Rank 2": [("Contract", "contract", 20000)],
    "Rank 3": [("Contract", "contract", 30000)],
    "Rank 4": [("Contract", "contract", 35000)],
    "Rank 5": [("Contract", "contract", 45000)],
}

# Taxi is a hybrid: Shift has a fixed price ($7,500) for all ranks,
# while Service changes with rank.
TAXI_RANKS = {
    "Rank 1": [("Shift", "shift", 7500), ("Service", "service", 6000)],
    "Rank 2": [("Shift", "shift", 7500), ("Service", "service", 8500)],
    "Rank 3": [("Shift", "shift", 7500), ("Service", "service", 10600)],
    "Rank 4": [("Shift", "shift", 7500), ("Service", "service", 13300)],
    "Rank 5": [("Shift", "shift", 7500), ("Service", "service", 15000)],
}

RANK_BASED_FACTIONS = {
    "Medic": MEDIC_RANKS,
    "Hitman Agency": HITMAN_RANKS,
    "Taxi": TAXI_RANKS,
}

ALL_FACTION_NAMES = list(FACTIONS.keys()) + list(RANK_BASED_FACTIONS.keys())

DEFAULT_FACTION = "Police Federal"
DEFAULT_RANK = "Rank 1"


def get_prices(faction: str, rank: str | None = None):
    if faction in RANK_BASED_FACTIONS:
        ranks = RANK_BASED_FACTIONS[faction]
        r = rank if rank in ranks else next(iter(ranks.keys()))
        return ranks[r]
    return FACTIONS.get(faction, FACTIONS[DEFAULT_FACTION])


def faction_requires_rank(faction: str) -> bool:
    return faction in RANK_BASED_FACTIONS


# ---------------------------------------------------------------------------
# Resource path helper (works both as script and as frozen exe)
# ---------------------------------------------------------------------------
def resource_path(relative: str) -> Path:
    base = getattr(sys, "_MEIPASS", None)
    if base:
        p = Path(base) / relative
        if p.exists():
            return p
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent / relative
    return Path(__file__).parent / relative


# ---------------------------------------------------------------------------
# Registry helpers
# ---------------------------------------------------------------------------
def _read_value(name: str) -> str | None:
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH) as key:
            value, _ = winreg.QueryValueEx(key, name)
            return value or None
    except (FileNotFoundError, OSError):
        return None


def _write_value(name: str, value: str) -> None:
    with winreg.CreateKey(winreg.HKEY_CURRENT_USER, REG_PATH) as key:
        winreg.SetValueEx(key, name, 0, winreg.REG_SZ, value)


def get_saved_folder() -> str | None:
    return _read_value(REG_VALUE_FOLDER)


def save_folder(folder: str) -> None:
    _write_value(REG_VALUE_FOLDER, folder)


def get_saved_name() -> str | None:
    return _read_value(REG_VALUE_NAME)


def save_name(name: str) -> None:
    _write_value(REG_VALUE_NAME, name)


def get_saved_faction() -> str | None:
    value = _read_value(REG_VALUE_FACTION)
    if value == "Federal":
        return "Police Federal"
    if value and value in ALL_FACTION_NAMES:
        return value
    return None


def save_faction(faction: str) -> None:
    _write_value(REG_VALUE_FACTION, faction)


def get_saved_rank() -> str | None:
    value = _read_value(REG_VALUE_RANK)
    if value and value in MEDIC_RANKS:
        return value
    return None


def save_rank(rank: str) -> None:
    _write_value(REG_VALUE_RANK, rank)


# ---------------------------------------------------------------------------
# Filesystem helpers
# ---------------------------------------------------------------------------
def _count_pngs(folder: Path) -> int:
    try:
        return sum(
            1 for f in folder.iterdir()
            if f.is_file() and f.suffix.lower() == ".png"
        )
    except OSError:
        return 0


def _find_nested(parent: Path, key: str) -> Path | None:
    try:
        for entry in parent.iterdir():
            if entry.is_dir() and entry.name.lower() == key:
                return entry
    except OSError:
        pass
    return None


def _collect_category_dirs(screenshots_dir: Path) -> dict[str, Path]:
    result: dict[str, Path] = {}
    for entry in screenshots_dir.iterdir():
        if entry.is_dir():
            result.setdefault(entry.name.lower(), entry)
    return result


# ---------------------------------------------------------------------------
# Image processing
# ---------------------------------------------------------------------------
def compress_to_jpg(src_png: Path, dst_jpg: Path, max_bytes: int = MAX_IMAGE_BYTES) -> None:
    img = Image.open(src_png)

    if img.mode in ("RGBA", "LA"):
        bg = Image.new("RGB", img.size, (255, 255, 255))
        bg.paste(img, mask=img.split()[-1])
        img = bg
    elif img.mode == "P":
        img = img.convert("RGBA")
        bg = Image.new("RGB", img.size, (255, 255, 255))
        bg.paste(img, mask=img.split()[-1])
        img = bg
    elif img.mode != "RGB":
        img = img.convert("RGB")

    work = img
    quality = 92

    while True:
        buf = io.BytesIO()
        work.save(buf, format="JPEG", quality=quality, optimize=True)
        size = buf.tell()
        if size <= max_bytes:
            break

        if quality > 50:
            quality -= 7
        else:
            new_w = max(int(work.width * 0.85), 320)
            new_h = max(int(work.height * 0.85), 320)
            if (new_w, new_h) == (work.width, work.height):
                buf = io.BytesIO()
                work.save(buf, format="JPEG", quality=35, optimize=True)
                break
            work = work.resize((new_w, new_h), Image.LANCZOS)
            quality = 85

    dst_jpg.parent.mkdir(parents=True, exist_ok=True)
    with open(dst_jpg, "wb") as f:
        f.write(buf.getvalue())


# ---------------------------------------------------------------------------
# Report calculation
# ---------------------------------------------------------------------------
def calculate_report(base_folder: str, faction: str, rank: str | None = None):
    screenshots_dir = Path(base_folder) / "screenshots"
    if not screenshots_dir.is_dir():
        return None, (
            "The 'screenshots' folder was not found at:\n"
            f"{screenshots_dir}\n\n"
            "Please make sure the selected MTA:SA folder contains a "
            "'screenshots' directory."
        )

    try:
        subdirs = _collect_category_dirs(screenshots_dir)
    except OSError as exc:
        return None, f"Failed to read the screenshots folder:\n{exc}"

    results = []
    for display_name, key, price in get_prices(faction, rank):
        folder = subdirs.get(key)
        count = 0
        if folder is not None:
            count += _count_pngs(folder)
            nested = _find_nested(folder, key)
            if nested is not None:
                count += _count_pngs(nested)
        results.append((display_name, count, price, count * price))

    return results, None


def count_total_pngs(base_folder: str, faction: str, rank: str | None = None) -> int:
    screenshots_dir = Path(base_folder) / "screenshots"
    if not screenshots_dir.is_dir():
        return 0
    try:
        subdirs = _collect_category_dirs(screenshots_dir)
    except OSError:
        return 0
    total = 0
    for _, key, _ in get_prices(faction, rank):
        cat = subdirs.get(key)
        if cat is not None:
            total += _count_pngs(cat)
    return total


# ---------------------------------------------------------------------------
# Convert worker thread
# ---------------------------------------------------------------------------
class ConvertWorker(QThread):
    progress = Signal(int, int)
    finished_ok = Signal(str, str)
    failed = Signal(str)

    def __init__(self, base_folder: str, game_name: str, faction: str,
                 rank: str | None = None, parent=None):
        super().__init__(parent)
        self.base_folder = base_folder
        self.game_name = game_name
        self.faction = faction
        self.rank = rank

    def run(self) -> None:
        if not PIL_AVAILABLE:
            self.failed.emit(
                "The 'Pillow' library is required for this feature but is "
                "not installed.\n\nPlease run:  pip install Pillow"
            )
            return

        screenshots_dir = Path(self.base_folder) / "screenshots"
        if not screenshots_dir.is_dir():
            self.failed.emit(
                "The 'screenshots' folder was not found at:\n"
                f"{screenshots_dir}"
            )
            return

        try:
            subdirs = _collect_category_dirs(screenshots_dir)
        except OSError as exc:
            self.failed.emit(f"Failed to read the screenshots folder:\n{exc}")
            return

        total = 0
        for _, key, _ in get_prices(self.faction, self.rank):
            cat = subdirs.get(key)
            if cat is not None:
                total += _count_pngs(cat)

        if total == 0:
            self.failed.emit(
                "No PNG screenshots were found inside any category folder.\n"
                "Nothing was created on the Desktop."
            )
            return

        self.progress.emit(0, total)

        desktop_path = QStandardPaths.writableLocation(QStandardPaths.DesktopLocation)
        if not desktop_path:
            self.failed.emit("Could not determine the Desktop folder location.")
            return
        desktop = Path(desktop_path)
        if not desktop.is_dir():
            self.failed.emit(f"Desktop folder not found:\n{desktop}")
            return

        target = desktop / self.game_name
        try:
            target.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            self.failed.emit(f"Failed to create the folder on the Desktop:\n{exc}")
            return

        done = 0
        for display_name, key, _ in get_prices(self.faction, self.rank):
            dst_dir = target / display_name
            try:
                dst_dir.mkdir(parents=True, exist_ok=True)
            except OSError as exc:
                self.failed.emit(
                    f"Failed to create '{display_name}' folder:\n{exc}"
                )
                return

            cat = subdirs.get(key)
            if cat is None:
                continue

            try:
                pngs = [
                    f for f in cat.iterdir()
                    if f.is_file() and f.suffix.lower() == ".png"
                ]
            except OSError:
                pngs = []

            for png in pngs:
                dst_jpg = dst_dir / (png.stem + ".jpg")
                try:
                    compress_to_jpg(png, dst_jpg)
                except Exception as exc:
                    self.failed.emit(
                        f"Failed to process '{png.name}':\n{exc}"
                    )
                    return
                done += 1
                self.progress.emit(done, total)

        zip_base = desktop / self.game_name
        zip_path = Path(f"{zip_base}.zip")
        try:
            if zip_path.exists():
                zip_path.unlink()
            shutil.make_archive(
                base_name=str(zip_base),
                format="zip",
                root_dir=str(desktop),
                base_dir=target.name,
            )
        except OSError as exc:
            self.failed.emit(
                "The folder was created successfully, but zipping it failed:\n"
                f"{exc}"
            )
            return

        self.finished_ok.emit(str(target), str(zip_path))


# ---------------------------------------------------------------------------
# Clear work reports
# ---------------------------------------------------------------------------
def clear_work_reports(base_folder: str, faction: str, rank: str | None = None):
    screenshots_dir = Path(base_folder) / "screenshots"
    if not screenshots_dir.is_dir():
        return None, (
            "The 'screenshots' folder was not found at:\n"
            f"{screenshots_dir}"
        )

    try:
        subdirs = _collect_category_dirs(screenshots_dir)
    except OSError as exc:
        return None, f"Failed to read the screenshots folder:\n{exc}"

    deleted = 0
    errors: list[str] = []

    for display_name, key, _ in get_prices(faction, rank):
        cat = subdirs.get(key)
        if cat is None:
            continue
        try:
            for item in cat.rglob("*"):
                if item.is_file():
                    try:
                        item.unlink()
                        deleted += 1
                    except OSError as exc:
                        errors.append(f"{item.name}: {exc}")
        except OSError as exc:
            errors.append(f"{display_name}: {exc}")

    if errors:
        summary = "\n".join(errors[:5])
        if len(errors) > 5:
            summary += f"\n... and {len(errors) - 5} more errors."
        return deleted, summary

    return deleted, None


# ---------------------------------------------------------------------------
# Folder picker dialog
# ---------------------------------------------------------------------------
class FolderPickerDialog(QDialog):
    def __init__(self, parent=None, initial: str = ""):
        super().__init__(parent)
        self.selected_path: str | None = None
        self.setWindowTitle("Enter MTA:SA Folder Address")
        self.setModal(True)
        self.setMinimumWidth(580)
        self._build_ui(initial)

    def _build_ui(self, initial: str) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(22, 22, 22, 22)
        root.setSpacing(14)

        title = QLabel("Enter the MTA:SA folder address")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        root.addWidget(title)

        hint = QLabel(
            "Select the installation folder of MTA:SA — the one that contains "
            "the 'screenshots' directory. This path will be stored in the "
            "Windows registry for future runs."
        )
        hint.setWordWrap(True)
        hint.setStyleSheet("color: #6b7c93;")
        root.addWidget(hint)

        row = QHBoxLayout()
        row.setSpacing(8)
        self.path_edit = QLineEdit(initial)
        self.path_edit.setPlaceholderText(
            r"C:\Program Files (x86)\MTA San Andreas 1.6"
        )
        self.path_edit.setMinimumHeight(34)
        browse_btn = QPushButton("Browse...")
        browse_btn.setMinimumHeight(34)
        browse_btn.clicked.connect(self._browse)
        row.addWidget(self.path_edit, 1)
        row.addWidget(browse_btn)
        root.addLayout(row)

        btns = QHBoxLayout()
        btns.addStretch()
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("secondaryButton")
        cancel_btn.setMinimumHeight(34)
        cancel_btn.clicked.connect(self.reject)
        confirm_btn = QPushButton("Confirm")
        confirm_btn.setMinimumHeight(34)
        confirm_btn.setDefault(True)
        confirm_btn.clicked.connect(self._confirm)
        btns.addWidget(cancel_btn)
        btns.addWidget(confirm_btn)
        root.addLayout(btns)

    def _browse(self) -> None:
        start = self.path_edit.text().strip()
        if not start or not Path(start).is_dir():
            start = str(Path.home())
        folder = QFileDialog.getExistingDirectory(
            self, "Select MTA:SA Folder", start
        )
        if folder:
            self.path_edit.setText(folder)

    def _confirm(self) -> None:
        path = self.path_edit.text().strip()
        if not path:
            QMessageBox.warning(self, "Invalid Path",
                                "Please select a folder first.")
            return
        if not Path(path).is_dir():
            QMessageBox.warning(self, "Invalid Path",
                                "The selected folder does not exist.")
            return
        self.selected_path = path
        self.accept()


# ---------------------------------------------------------------------------
# Faction picker dialog
# ---------------------------------------------------------------------------
class FactionDialog(QDialog):
    def __init__(self, parent=None, initial: str | None = None):
        super().__init__(parent)
        self.faction_value: str | None = None
        self.setWindowTitle("Select Your Faction")
        self.setModal(True)
        self.setMinimumWidth(460)
        self._build_ui(initial)

    def _build_ui(self, initial: str | None) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(22, 22, 22, 22)
        root.setSpacing(14)

        title = QLabel("Select your faction")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        root.addWidget(title)

        hint = QLabel(
            "The prices used in the work report depend on your faction. "
            "You can change this later in Settings."
        )
        hint.setWordWrap(True)
        hint.setStyleSheet("color: #6b7c93;")
        root.addWidget(hint)

        self.group = QButtonGroup(self)
        self.radios: dict[str, QRadioButton] = {}

        for name in ALL_FACTION_NAMES:
            label = name
            if faction_requires_rank(name):
                label = f"{name}  (rank-based)"
            rb = QRadioButton(label)
            rb.setMinimumHeight(36)
            rb.setStyleSheet(
                "QRadioButton { padding: 8px 12px; font-size: 14px; }"
                "QRadioButton::indicator { width: 16px; height: 16px; }"
            )
            if initial == name:
                rb.setChecked(True)
            elif initial is None and name == DEFAULT_FACTION:
                rb.setChecked(True)
            self.group.addButton(rb)
            self.radios[name] = rb
            root.addWidget(rb)

        btns = QHBoxLayout()
        btns.addStretch()
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("secondaryButton")
        cancel_btn.setMinimumHeight(34)
        cancel_btn.clicked.connect(self.reject)
        confirm_btn = QPushButton("Confirm")
        confirm_btn.setMinimumHeight(34)
        confirm_btn.setDefault(True)
        confirm_btn.clicked.connect(self._confirm)
        btns.addWidget(cancel_btn)
        btns.addWidget(confirm_btn)
        root.addLayout(btns)

    def _confirm(self) -> None:
        for name, rb in self.radios.items():
            if rb.isChecked():
                self.faction_value = name
                self.accept()
                return
        QMessageBox.warning(self, "Invalid Selection",
                            "Please select a faction.")


# ---------------------------------------------------------------------------
# Rank picker dialog (for rank-based factions)
# ---------------------------------------------------------------------------
class RankDialog(QDialog):
    def __init__(self, parent=None, faction: str = "Medic",
                 initial: str | None = None):
        super().__init__(parent)
        self.rank_value: str | None = None
        self.faction_name = faction
        self.setWindowTitle(f"Select Your {faction} Rank")
        self.setModal(True)
        self.setMinimumWidth(560)
        self._build_ui(initial)

    def _build_ui(self, initial: str | None) -> None:
        ranks = RANK_BASED_FACTIONS.get(self.faction_name, {})

        root = QVBoxLayout(self)
        root.setContentsMargins(22, 22, 22, 22)
        root.setSpacing(14)

        title = QLabel(f"Select your {self.faction_name} rank")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        root.addWidget(title)

        hint = QLabel(
            "Prices depend on your rank. You can change this later in "
            "Settings."
        )
        hint.setWordWrap(True)
        hint.setStyleSheet("color: #6b7c93;")
        root.addWidget(hint)

        self.group = QButtonGroup(self)
        self.radios: dict[str, QRadioButton] = {}

        first_rank = next(iter(ranks.keys()), None)

        for rank_name, prices in ranks.items():
            price_str = "  |  ".join(f"{n} ${p:,}" for n, _, p in prices)
            label = f"{rank_name}   —   {price_str}"
            rb = QRadioButton(label)
            rb.setMinimumHeight(38)
            rb.setStyleSheet(
                "QRadioButton { padding: 8px 12px; font-size: 13px; }"
                "QRadioButton::indicator { width: 16px; height: 16px; }"
            )
            if initial == rank_name:
                rb.setChecked(True)
            elif initial is None and rank_name == first_rank:
                rb.setChecked(True)
            self.group.addButton(rb)
            self.radios[rank_name] = rb
            root.addWidget(rb)

        btns = QHBoxLayout()
        btns.addStretch()
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("secondaryButton")
        cancel_btn.setMinimumHeight(34)
        cancel_btn.clicked.connect(self.reject)
        confirm_btn = QPushButton("Confirm")
        confirm_btn.setMinimumHeight(34)
        confirm_btn.setDefault(True)
        confirm_btn.clicked.connect(self._confirm)
        btns.addWidget(cancel_btn)
        btns.addWidget(confirm_btn)
        root.addLayout(btns)

    def _confirm(self) -> None:
        for name, rb in self.radios.items():
            if rb.isChecked():
                self.rank_value = name
                self.accept()
                return
        QMessageBox.warning(self, "Invalid Selection",
                            "Please select a rank.")


# ---------------------------------------------------------------------------
# Game-name input dialog
# ---------------------------------------------------------------------------
class GameNameDialog(QDialog):
    def __init__(self, parent=None, initial: str = ""):
        super().__init__(parent)
        self.name_value: str | None = None
        self.setWindowTitle("Enter Your Game Name")
        self.setModal(True)
        self.setMinimumWidth(500)
        self._build_ui(initial)

    def _build_ui(self, initial: str) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(22, 22, 22, 22)
        root.setSpacing(14)

        title = QLabel("Enter your in-game name")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        root.addWidget(title)

        hint = QLabel(
            "A folder with exactly this name will be created on your Desktop, "
            "the converted & compressed images will be placed inside it, and "
            "the folder will then be compressed into a .zip file right next to "
            "it. The name is saved in the registry."
        )
        hint.setWordWrap(True)
        hint.setStyleSheet("color: #6b7c93;")
        root.addWidget(hint)

        self.name_edit = QLineEdit(initial)
        self.name_edit.setPlaceholderText("(AmooReza)")
        self.name_edit.setMinimumHeight(34)
        root.addWidget(self.name_edit)

        btns = QHBoxLayout()
        btns.addStretch()
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("secondaryButton")
        cancel_btn.setMinimumHeight(34)
        cancel_btn.clicked.connect(self.reject)
        confirm_btn = QPushButton("Confirm")
        confirm_btn.setMinimumHeight(34)
        confirm_btn.setDefault(True)
        confirm_btn.clicked.connect(self._confirm)
        btns.addWidget(cancel_btn)
        btns.addWidget(confirm_btn)
        root.addLayout(btns)

    def _confirm(self) -> None:
        name = self.name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "Invalid Name",
                                "Please enter your in-game name.")
            return
        forbidden = set('\\/:*?"<>|')
        if any(ch in forbidden for ch in name):
            QMessageBox.warning(
                self, "Invalid Name",
                "The name contains characters that are not allowed in "
                "Windows folder names:\n\\ / : * ? \" < > |"
            )
            return
        self.name_value = name
        self.accept()


# ---------------------------------------------------------------------------
# Progress dialog
# ---------------------------------------------------------------------------
class ProgressDialog(QDialog):
    def __init__(self, parent, total: int):
        super().__init__(parent)
        self.setWindowTitle("Creating Work Report")
        self.setModal(True)
        self.setMinimumWidth(460)
        self.setWindowFlag(Qt.WindowCloseButtonHint, False)

        root = QVBoxLayout(self)
        root.setContentsMargins(22, 22, 22, 22)
        root.setSpacing(14)

        title = QLabel("Compressing screenshots...")
        title.setStyleSheet("font-size: 15px; font-weight: bold;")
        root.addWidget(title)

        hint = QLabel(
            "Please wait while PNG files are converted to JPG (max 250 KB) "
            "and packed into a zip file."
        )
        hint.setWordWrap(True)
        hint.setStyleSheet("color: #6b7c93;")
        root.addWidget(hint)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, max(total, 1))
        self.progress_bar.setValue(0)
        self.progress_bar.setMinimumHeight(22)
        root.addWidget(self.progress_bar)

        self.label = QLabel(f"0 / {total} files")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("color: #2c3e50; font-weight: 600;")
        root.addWidget(self.label)

    def update_progress(self, done: int, total: int) -> None:
        self.progress_bar.setRange(0, max(total, 1))
        self.progress_bar.setValue(done)
        self.label.setText(f"{done} / {total} files")


# ---------------------------------------------------------------------------
# Main Window
# ---------------------------------------------------------------------------
class MainWindow(QMainWindow):
    def __init__(self, mta_folder: str, game_name: str | None,
                 faction: str, rank: str | None):
        super().__init__()
        self.mta_folder = mta_folder
        self.game_name = game_name or ""
        self.faction = faction
        self.rank = rank or DEFAULT_RANK

        self._convert_worker: ConvertWorker | None = None
        self._convert_dialog: ProgressDialog | None = None

        self.setWindowTitle(APP_TITLE)
        self.setMinimumSize(960, 820)
        self.resize(1040, 860)

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.home_page = self._create_home_page()
        self.tools_page = self._create_tools_page()
        self.report_page = self._create_report_page()
        self.settings_page = self._create_settings_page()

        self.stack.addWidget(self.home_page)
        self.stack.addWidget(self.tools_page)
        self.stack.addWidget(self.report_page)
        self.stack.addWidget(self.settings_page)

        self._build_menu()
        self._apply_style()
        self._refresh_labels()

    # ---------------- Menu ----------------
    def _build_menu(self) -> None:
        menubar = self.menuBar()

        tools_menu = menubar.addMenu("Tools")
        act_report = QAction("Calculating the work report", self)
        act_report.triggered.connect(self.run_report)
        tools_menu.addAction(act_report)

        act_create = QAction("Create Work Report", self)
        act_create.triggered.connect(self.create_report_folder)
        tools_menu.addAction(act_create)

        tools_menu.addSeparator()

        act_clear = QAction("Clear Work Reports", self)
        act_clear.triggered.connect(self.clear_reports)
        tools_menu.addAction(act_clear)

        settings_menu = menubar.addMenu("Settings")
        act_folder = QAction("Change MTA:SA Folder...", self)
        act_folder.triggered.connect(self.change_folder)
        settings_menu.addAction(act_folder)

        act_name = QAction("Change Game Name...", self)
        act_name.triggered.connect(self.change_name)
        settings_menu.addAction(act_name)

        act_faction = QAction("Change Faction...", self)
        act_faction.triggered.connect(self.change_faction)
        settings_menu.addAction(act_faction)

        self.act_rank = QAction("Change Rank...", self)
        self.act_rank.triggered.connect(self.change_rank)
        settings_menu.addAction(self.act_rank)

        help_menu = menubar.addMenu("Help")
        act_about = QAction(f"About {APP_NAME}", self)
        act_about.triggered.connect(self.show_about)
        help_menu.addAction(act_about)

    # ---------------- Pages ----------------
    def _create_home_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(60, 40, 60, 40)
        layout.setSpacing(12)

        title = QLabel(APP_NAME)
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(
            "font-size: 32px; font-weight: bold; color: #2c3e50;"
        )
        layout.addWidget(title)

        subtitle = QLabel(f"Version {APP_VERSION}   •   Made By {APP_AUTHOR}")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: #95a5a6; font-size: 13px;")
        layout.addWidget(subtitle)

        layout.addSpacing(16)

        def make_card(title_text):
            box = QFrame()
            box.setObjectName("card")
            v = QVBoxLayout(box)
            v.setContentsMargins(18, 14, 18, 14)
            v.setSpacing(4)
            t = QLabel(title_text)
            t.setStyleSheet(
                "font-weight: bold; color: #34495e; font-size: 12px;"
            )
            val = QLabel()
            val.setWordWrap(True)
            val.setStyleSheet("color: #2c3e50; font-size: 13px;")
            v.addWidget(t)
            v.addWidget(val)
            return box, val

        self.home_folder_card, self.home_folder_label = make_card(
            "Current MTA:SA Folder"
        )
        layout.addWidget(self.home_folder_card)

        self.home_faction_card, self.home_faction_label = make_card(
            "Current Faction"
        )
        layout.addWidget(self.home_faction_card)

        self.home_rank_card, self.home_rank_label = make_card(
            "Current Rank"
        )
        layout.addWidget(self.home_rank_card)

        self.home_name_card, self.home_name_label = make_card(
            "Current Game Name"
        )
        layout.addWidget(self.home_name_card)

        layout.addSpacing(16)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(20)

        tools_btn = QPushButton("Tools")
        tools_btn.setMinimumHeight(90)
        tools_btn.setStyleSheet("font-size: 17px; font-weight: bold;")
        tools_btn.clicked.connect(
            lambda: self.stack.setCurrentWidget(self.tools_page)
        )

        settings_btn = QPushButton("Settings")
        settings_btn.setMinimumHeight(90)
        settings_btn.setStyleSheet("font-size: 17px; font-weight: bold;")
        settings_btn.clicked.connect(
            lambda: self.stack.setCurrentWidget(self.settings_page)
        )

        btn_row.addWidget(tools_btn)
        btn_row.addWidget(settings_btn)
        layout.addLayout(btn_row)

        layout.addStretch()
        return page

    def _create_tools_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 24, 30, 30)
        layout.setSpacing(16)

        header = QHBoxLayout()
        back = QPushButton("←  Back")
        back.setObjectName("backButton")
        back.clicked.connect(
            lambda: self.stack.setCurrentWidget(self.home_page)
        )
        header.addWidget(back)
        header.addStretch()
        layout.addLayout(header)

        title = QLabel("Tools")
        title.setStyleSheet("font-size: 22px; font-weight: bold;")
        layout.addWidget(title)

        # Card 1 — Calculate
        card1 = QFrame()
        card1.setObjectName("card")
        c1 = QHBoxLayout(card1)
        c1.setContentsMargins(22, 22, 22, 22)
        c1.setSpacing(20)
        info1 = QVBoxLayout()
        info1.setSpacing(6)
        t1 = QLabel("Calculating the work report")
        t1.setStyleSheet("font-size: 16px; font-weight: bold;")
        self.calc_desc = QLabel()
        self.calc_desc.setWordWrap(True)
        self.calc_desc.setStyleSheet("color: #6b7c93;")
        info1.addWidget(t1)
        info1.addWidget(self.calc_desc)
        c1.addLayout(info1, 1)
        run_btn = QPushButton("Calculate Work Report")
        run_btn.setMinimumHeight(44)
        run_btn.setMinimumWidth(210)
        run_btn.clicked.connect(self.run_report)
        c1.addWidget(run_btn, 0, Qt.AlignVCenter)
        layout.addWidget(card1)

        # Card 2 — Create
        card2 = QFrame()
        card2.setObjectName("card")
        c2 = QHBoxLayout(card2)
        c2.setContentsMargins(22, 22, 22, 22)
        c2.setSpacing(20)
        info2 = QVBoxLayout()
        info2.setSpacing(6)
        t2 = QLabel("Create Work Report")
        t2.setStyleSheet("font-size: 16px; font-weight: bold;")
        d2 = QLabel(
            "Converts every PNG screenshot from the category folders into a "
            "JPG file with a maximum size of 250 KB, places them in a Desktop "
            "folder named after your in-game name, and finally compresses "
            "that folder into a .zip file right next to it."
        )
        d2.setWordWrap(True)
        d2.setStyleSheet("color: #6b7c93;")
        info2.addWidget(t2)
        info2.addWidget(d2)
        c2.addLayout(info2, 1)
        create_btn = QPushButton("Create Work Report")
        create_btn.setMinimumHeight(44)
        create_btn.setMinimumWidth(210)
        create_btn.clicked.connect(self.create_report_folder)
        c2.addWidget(create_btn, 0, Qt.AlignVCenter)
        layout.addWidget(card2)

        # Card 3 — Clear (DANGER)
        card3 = QFrame()
        card3.setObjectName("card")
        c3 = QHBoxLayout(card3)
        c3.setContentsMargins(22, 22, 22, 22)
        c3.setSpacing(20)
        info3 = QVBoxLayout()
        info3.setSpacing(6)
        t3 = QLabel("Clear Work Reports")
        t3.setStyleSheet("font-size: 16px; font-weight: bold; color: #c0392b;")
        d3 = QLabel(
            "Permanently deletes all files inside the category folders. "
            "Folder structure is preserved. This action cannot be undone."
        )
        d3.setWordWrap(True)
        d3.setStyleSheet("color: #6b7c93;")
        info3.addWidget(t3)
        info3.addWidget(d3)
        c3.addLayout(info3, 1)
        clear_btn = QPushButton("Clear Work Reports")
        clear_btn.setObjectName("dangerButton")
        clear_btn.setMinimumHeight(44)
        clear_btn.setMinimumWidth(210)
        clear_btn.clicked.connect(self.clear_reports)
        c3.addWidget(clear_btn, 0, Qt.AlignVCenter)
        layout.addWidget(card3)

        layout.addStretch()
        return page

    def _create_report_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 24, 30, 30)
        layout.setSpacing(14)

        header = QHBoxLayout()
        back = QPushButton("←  Back")
        back.setObjectName("backButton")
        back.clicked.connect(
            lambda: self.stack.setCurrentWidget(self.tools_page)
        )
        header.addWidget(back)
        header.addStretch()
        refresh_btn = QPushButton("Recalculate")
        refresh_btn.setMinimumHeight(32)
        refresh_btn.clicked.connect(self.run_report)
        header.addWidget(refresh_btn)
        layout.addLayout(header)

        title = QLabel("Work Report")
        title.setStyleSheet("font-size: 22px; font-weight: bold;")
        layout.addWidget(title)

        self.report_info = QLabel()
        self.report_info.setStyleSheet("color: #6b7c93;")
        self.report_info.setWordWrap(True)
        layout.addWidget(self.report_info)

        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(
            ["Folder", "Screenshots", "Unit Price", "Total"]
        )
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionMode(QTableWidget.NoSelection)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        self.table.verticalHeader().setDefaultSectionSize(36)
        layout.addWidget(self.table, 1)

        self.summary_label = QLabel()
        self.summary_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.summary_label.setStyleSheet(
            "font-size: 15px; font-weight: bold; color: #2c3e50;"
            "background: #eaf4fc; padding: 12px 16px; border-radius: 8px;"
        )
        layout.addWidget(self.summary_label)

        return page

    def _create_settings_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 24, 30, 30)
        layout.setSpacing(16)

        header = QHBoxLayout()
        back = QPushButton("←  Back")
        back.setObjectName("backButton")
        back.clicked.connect(
            lambda: self.stack.setCurrentWidget(self.home_page)
        )
        header.addWidget(back)
        header.addStretch()
        layout.addLayout(header)

        title = QLabel("Settings")
        title.setStyleSheet("font-size: 22px; font-weight: bold;")
        layout.addWidget(title)

        def make_setting_card(label_text, button_text, slot):
            card = QFrame()
            card.setObjectName("card")
            v = QVBoxLayout(card)
            v.setContentsMargins(22, 22, 22, 22)
            v.setSpacing(12)
            lbl = QLabel(label_text)
            lbl.setStyleSheet("font-weight: bold; color: #34495e;")
            v.addWidget(lbl)
            val = QLabel()
            val.setWordWrap(True)
            val.setStyleSheet(
                "color: #2c3e50; background:#f4f6f8; padding:12px;"
                "border-radius:6px; border: 1px solid #e1e8ed;"
            )
            v.addWidget(val)
            btn = QPushButton(button_text)
            btn.setMinimumHeight(38)
            btn.setMinimumWidth(180)
            btn.clicked.connect(slot)
            v.addWidget(btn, 0, Qt.AlignLeft)
            return card, val

        self.settings_folder_card, self.settings_folder_label = make_setting_card(
            "MTA:SA Folder", "Change Folder...", self.change_folder
        )
        layout.addWidget(self.settings_folder_card)

        self.settings_faction_card, self.settings_faction_label = make_setting_card(
            "Faction", "Change Faction...", self.change_faction
        )
        layout.addWidget(self.settings_faction_card)

        self.settings_rank_card, self.settings_rank_label = make_setting_card(
            "Rank", "Change Rank...", self.change_rank
        )
        layout.addWidget(self.settings_rank_card)

        self.settings_name_card, self.settings_name_label = make_setting_card(
            "Game Name", "Change Game Name...", self.change_name
        )
        layout.addWidget(self.settings_name_card)

        layout.addStretch()
        return page

    # ---------------- Logic ----------------
    def _refresh_labels(self) -> None:
        self.home_folder_label.setText(self.mta_folder)
        self.settings_folder_label.setText(self.mta_folder)

        self.home_faction_label.setText(self.faction)
        self.settings_faction_label.setText(self.faction)

        is_ranked = faction_requires_rank(self.faction)

        self.home_rank_card.setVisible(is_ranked)
        self.settings_rank_card.setVisible(is_ranked)
        self.act_rank.setEnabled(is_ranked)

        if is_ranked:
            self.home_rank_label.setText(self.rank)
            self.settings_rank_label.setText(self.rank)

        name_display = self.game_name if self.game_name else "(not set yet)"
        self.home_name_label.setText(name_display)
        self.settings_name_label.setText(name_display)

        prices = get_prices(self.faction, self.rank)
        parts = [f"{name} ${price:,}" for name, _, price in prices]

        header = f"Faction: {self.faction}"
        if is_ranked:
            header += f" ({self.rank})"

        self.calc_desc.setText(
            f"{header} — counts PNG screenshots and applies the following "
            f"prices:\n" + "  •  ".join(parts)
        )

    def run_report(self) -> None:
        results, error = calculate_report(
            self.mta_folder, self.faction, self.rank
        )
        if error:
            QMessageBox.warning(self, "Report Error", error)
            return

        self.stack.setCurrentWidget(self.report_page)
        self.table.setRowCount(0)

        total_count = 0
        total_amount = 0

        for row, (name, count, price, subtotal) in enumerate(results):
            self.table.insertRow(row)

            item_name = QTableWidgetItem(name)
            item_name.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 0, item_name)

            item_count = QTableWidgetItem(str(count))
            item_count.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 1, item_count)

            item_price = QTableWidgetItem(f"${price:,}")
            item_price.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 2, item_price)

            item_total = QTableWidgetItem(f"${subtotal:,}")
            item_total.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 3, item_total)

            total_count += count
            total_amount += subtotal

        screenshots_dir = Path(self.mta_folder) / "screenshots"
        faction_display = self.faction
        if faction_requires_rank(self.faction):
            faction_display = f"{self.faction} ({self.rank})"
        self.report_info.setText(
            f"Faction: {faction_display}      |      "
            f"Screenshots directory:  {screenshots_dir}"
        )
        self.summary_label.setText(
            f"Total Screenshots: {total_count:,}      |      "
            f"Total Amount: ${total_amount:,}"
        )

    def _ensure_game_name(self) -> str | None:
        if self.game_name:
            return self.game_name

        dlg = GameNameDialog(self, self.game_name)
        if dlg.exec() != QDialog.Accepted or not dlg.name_value:
            return None
        try:
            save_name(dlg.name_value)
        except OSError as exc:
            QMessageBox.critical(
                self, "Registry Error",
                f"Failed to save the game name in the registry:\n{exc}"
            )
            return None
        self.game_name = dlg.name_value
        self._refresh_labels()
        return self.game_name

    def create_report_folder(self) -> None:
        if self._convert_worker is not None and self._convert_worker.isRunning():
            QMessageBox.information(
                self, "Please Wait",
                "A work report is already being created. Please wait for it "
                "to finish."
            )
            return

        name = self._ensure_game_name()
        if not name:
            return

        total = count_total_pngs(self.mta_folder, self.faction, self.rank)
        if total == 0:
            QMessageBox.warning(
                self, "Create Report Error",
                "No PNG screenshots were found inside any category folder.\n"
                "Nothing was created on the Desktop."
            )
            return

        self._convert_dialog = ProgressDialog(self, total)

        worker = ConvertWorker(
            self.mta_folder, name, self.faction, self.rank, self
        )
        self._convert_worker = worker

        worker.progress.connect(self._convert_dialog.update_progress)
        worker.finished_ok.connect(self._on_convert_finished)
        worker.failed.connect(self._on_convert_failed)

        worker.start()
        self._convert_dialog.exec()

    def _on_convert_finished(self, target: str, zip_path: str) -> None:
        if self._convert_dialog is not None:
            self._convert_dialog.accept()
            self._convert_dialog = None

        if self._convert_worker is not None:
            self._convert_worker.wait()
            self._convert_worker = None

        faction_display = self.faction
        if faction_requires_rank(self.faction):
            faction_display = f"{self.faction} ({self.rank})"

        QMessageBox.information(
            self, "Work Report Created",
            "The work report was created successfully.\n\n"
            f"Faction: {faction_display}\n"
            "All PNG screenshots were converted to JPG (max 250 KB each).\n\n"
            f"Folder:\n{target}\n\n"
            f"Zip:\n{zip_path}"
        )

    def _on_convert_failed(self, message: str) -> None:
        if self._convert_dialog is not None:
            self._convert_dialog.reject()
            self._convert_dialog = None

        if self._convert_worker is not None:
            self._convert_worker.wait()
            self._convert_worker = None

        QMessageBox.warning(self, "Create Report Error", message)

    def clear_reports(self) -> None:
        screenshots_dir = Path(self.mta_folder) / "screenshots"
        if not screenshots_dir.is_dir():
            QMessageBox.warning(
                self, "Clear Work Reports",
                "The 'screenshots' folder was not found at:\n"
                f"{screenshots_dir}"
            )
            return

        confirm = QMessageBox(self)
        confirm.setIcon(QMessageBox.Warning)
        confirm.setWindowTitle("Confirm Deletion")
        confirm.setText("Are you sure?")
        confirm.setInformativeText(
            "This will permanently delete all files inside the category "
            "folders and their nested same-named folders.\n\n"
            "Folder structure will be preserved, but this action cannot be "
            "undone."
        )
        yes_btn = confirm.addButton("Yes, delete", QMessageBox.YesRole)
        no_btn = confirm.addButton("No, cancel", QMessageBox.NoRole)
        confirm.setDefaultButton(no_btn)
        confirm.exec()

        if confirm.clickedButton() is not yes_btn:
            return

        deleted, error = clear_work_reports(
            self.mta_folder, self.faction, self.rank
        )

        if error and deleted == 0:
            QMessageBox.warning(
                self, "Clear Work Reports",
                f"Deletion failed:\n{error}"
            )
            return

        if error:
            QMessageBox.warning(
                self, "Partially Completed",
                f"Deleted {deleted} file(s), but some errors occurred:\n\n"
                f"{error}"
            )
            return

        QMessageBox.information(
            self, "Clear Work Reports",
            f"Done. {deleted} file(s) were deleted successfully."
        )

    def change_folder(self) -> None:
        dlg = FolderPickerDialog(self, self.mta_folder)
        if dlg.exec() != QDialog.Accepted or not dlg.selected_path:
            return
        try:
            save_folder(dlg.selected_path)
        except OSError as exc:
            QMessageBox.critical(
                self, "Registry Error",
                f"Failed to save the folder in the registry:\n{exc}"
            )
            return
        self.mta_folder = dlg.selected_path
        self._refresh_labels()
        QMessageBox.information(
            self, "Saved",
            "The MTA:SA folder has been updated successfully."
        )

    def change_faction(self) -> None:
        dlg = FactionDialog(self, self.faction)
        if dlg.exec() != QDialog.Accepted or not dlg.faction_value:
            return

        new_faction = dlg.faction_value
        try:
            save_faction(new_faction)
        except OSError as exc:
            QMessageBox.critical(
                self, "Registry Error",
                f"Failed to save the faction in the registry:\n{exc}"
            )
            return
        self.faction = new_faction

        if faction_requires_rank(new_faction):
            rank_dlg = RankDialog(self, new_faction, self.rank)
            if rank_dlg.exec() == QDialog.Accepted and rank_dlg.rank_value:
                try:
                    save_rank(rank_dlg.rank_value)
                except OSError as exc:
                    QMessageBox.critical(
                        self, "Registry Error",
                        f"Failed to save the rank in the registry:\n{exc}"
                    )
                    return
                self.rank = rank_dlg.rank_value
            else:
                if not self.rank:
                    self.rank = DEFAULT_RANK
                    try:
                        save_rank(self.rank)
                    except OSError:
                        pass

        self._refresh_labels()
        QMessageBox.information(
            self, "Saved",
            f"Faction changed to {self.faction}."
        )

    def change_rank(self) -> None:
        if not faction_requires_rank(self.faction):
            QMessageBox.information(
                self, "Rank",
                "The current faction does not use ranks.\n"
                "Ranks are only available for rank-based factions such as "
                "Medic, Hitman Agency or Taxi."
            )
            return

        dlg = RankDialog(self, self.faction, self.rank)
        if dlg.exec() != QDialog.Accepted or not dlg.rank_value:
            return
        try:
            save_rank(dlg.rank_value)
        except OSError as exc:
            QMessageBox.critical(
                self, "Registry Error",
                f"Failed to save the rank in the registry:\n{exc}"
            )
            return
        self.rank = dlg.rank_value
        self._refresh_labels()
        QMessageBox.information(
            self, "Saved",
            f"Rank changed to {self.rank}."
        )

    def change_name(self) -> None:
        dlg = GameNameDialog(self, self.game_name)
        if dlg.exec() != QDialog.Accepted or not dlg.name_value:
            return
        try:
            save_name(dlg.name_value)
        except OSError as exc:
            QMessageBox.critical(
                self, "Registry Error",
                f"Failed to save the game name in the registry:\n{exc}"
            )
            return
        self.game_name = dlg.name_value
        self._refresh_labels()
        QMessageBox.information(
            self, "Saved",
            "The game name has been updated successfully."
        )

    def show_about(self) -> None:
        QMessageBox.information(
            self,
            f"About {APP_NAME}",
            f"<b>{APP_NAME}</b> — v{APP_VERSION}<br>"
            f"<i>Made By {APP_AUTHOR}</i><br><br>"
            "A small utility for MTA:SA players.<br>"
            "• Stores the MTA:SA folder, faction, rank and game name in the "
            "Windows registry.<br>"
            "• Calculates a work report using faction- and rank-specific "
            "prices.<br>"
            "• Converts PNG screenshots to JPG (max 250 KB each) and creates "
            "a zipped work report on the Desktop.<br>"
            "• Clears all screenshots from the category folders."
        )

    # ---------------- Style ----------------
    def _apply_style(self) -> None:
        self.setStyleSheet("""
            QMainWindow, QDialog { background: #f7f9fb; }
            QWidget { font-family: "Segoe UI"; font-size: 13px; color: #2c3e50; }

            QMenuBar { background: #ffffff; border-bottom: 1px solid #e1e8ed; }
            QMenuBar::item { padding: 6px 12px; background: transparent; }
            QMenuBar::item:selected { background: #eaf4fc; border-radius: 4px; }
            QMenu { background: #ffffff; border: 1px solid #e1e8ed; padding: 4px; }
            QMenu::item { padding: 6px 22px; border-radius: 4px; }
            QMenu::item:selected { background: #eaf4fc; }
            QMenu::item:disabled { color: #b0bec5; }

            QPushButton {
                background: #3498db;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 18px;
                font-weight: 600;
            }
            QPushButton:hover { background: #2980b9; }
            QPushButton:pressed { background: #2471a3; }
            QPushButton:disabled { background: #bdc3c7; }

            QPushButton#secondaryButton {
                background: #ecf0f1;
                color: #2c3e50;
            }
            QPushButton#secondaryButton:hover { background: #dfe4e6; }

            QPushButton#backButton {
                background: #ecf0f1;
                color: #2c3e50;
                padding: 6px 14px;
                font-weight: 500;
            }
            QPushButton#backButton:hover { background: #dfe4e6; }

            QPushButton#dangerButton {
                background: #e74c3c;
                color: white;
            }
            QPushButton#dangerButton:hover { background: #c0392b; }
            QPushButton#dangerButton:pressed { background: #a93226; }
            QPushButton#dangerButton:disabled { background: #e6b0aa; }

            QLineEdit {
                background: #ffffff;
                border: 1px solid #d6dee6;
                border-radius: 6px;
                padding: 6px 10px;
                selection-background-color: #3498db;
            }
            QLineEdit:focus { border: 1px solid #3498db; }

            QRadioButton {
                color: #2c3e50;
                spacing: 10px;
            }
            QRadioButton::indicator {
                width: 16px; height: 16px;
                border: 2px solid #b0bec5;
                border-radius: 9px;
                background: white;
            }
            QRadioButton::indicator:hover { border-color: #3498db; }
            QRadioButton::indicator:checked {
                border: 5px solid #3498db;
                background: white;
            }

            QFrame#card {
                background: #ffffff;
                border: 1px solid #e1e8ed;
                border-radius: 10px;
            }

            QProgressBar {
                background: #ecf0f1;
                border: 1px solid #d6dee6;
                border-radius: 6px;
                text-align: center;
                color: #2c3e50;
                font-weight: 600;
                height: 22px;
            }
            QProgressBar::chunk {
                background: #3498db;
                border-radius: 5px;
            }

            QTableWidget {
                background: #ffffff;
                border: 1px solid #e1e8ed;
                border-radius: 8px;
                gridline-color: #eef2f5;
                alternate-background-color: #f7fafc;
                font-size: 13px;
            }
            QTableWidget::item { padding: 6px; }
            QHeaderView::section {
                background: #3498db;
                color: white;
                padding: 10px;
                border: none;
                font-weight: bold;
            }
            QHeaderView::section:first { border-top-left-radius: 8px; }
            QHeaderView::section:last  { border-top-right-radius: 8px; }
        """)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)

    icon_path = resource_path("logo.ico")
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))

    # 1) Folder
    folder = get_saved_folder()
    if not folder or not Path(folder).is_dir():
        dlg = FolderPickerDialog(None, folder or "")
        if dlg.exec() != QDialog.Accepted or not dlg.selected_path:
            return 0
        try:
            save_folder(dlg.selected_path)
        except OSError as exc:
            QMessageBox.critical(
                None, "Registry Error",
                f"Failed to save the folder in the registry:\n{exc}"
            )
            return 1
        folder = dlg.selected_path

    # 2) Faction
    faction = get_saved_faction()
    if not faction:
        dlg = FactionDialog(None, None)
        if dlg.exec() != QDialog.Accepted or not dlg.faction_value:
            return 0
        try:
            save_faction(dlg.faction_value)
        except OSError as exc:
            QMessageBox.critical(
                None, "Registry Error",
                f"Failed to save the faction in the registry:\n{exc}"
            )
            return 1
        faction = dlg.faction_value

    # 3) Rank (only for rank-based factions, only if not already saved)
    rank = get_saved_rank()
    if faction_requires_rank(faction) and not rank:
        dlg = RankDialog(None, faction, None)
        if dlg.exec() != QDialog.Accepted or not dlg.rank_value:
            return 0
        try:
            save_rank(dlg.rank_value)
        except OSError as exc:
            QMessageBox.critical(
                None, "Registry Error",
                f"Failed to save the rank in the registry:\n{exc}"
            )
            return 1
        rank = dlg.rank_value

    # 4) Game name (on demand)
    game_name = get_saved_name()

    window = MainWindow(folder, game_name, faction, rank)
    if icon_path.exists():
        window.setWindowIcon(QIcon(str(icon_path)))
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())