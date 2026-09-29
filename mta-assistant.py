"""
MTA Assistant - v1.10.3  ( Made By AmooReza )
A PySide6 Windows application for MTA:SA players.
"""

import csv
import io
import json
import os
import sys
import shutil
import time
import urllib.request
import urllib.error
import winreg
from datetime import datetime
from pathlib import Path

from PySide6.QtCore import Qt, QStandardPaths, QThread, Signal, QSize, QUrl, QTimer, QMarginsF
from PySide6.QtGui import (
    QAction, QIcon, QPixmap, QTextDocument, QDesktopServices,
    QPageSize, QPageLayout, QCursor, QIntValidator
)
from PySide6.QtPrintSupport import QPrinter
from PySide6.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFileDialog, QMessageBox, QMainWindow, QWidget,
    QStackedWidget, QTableWidget, QTableWidgetItem, QHeaderView, QFrame,
    QRadioButton, QButtonGroup, QProgressBar, QScrollArea, QGridLayout,
    QCheckBox
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
APP_VERSION = "1.10.3"
APP_AUTHOR = "AmooReza"
APP_TITLE = f"{APP_NAME} — v{APP_VERSION}  ( Made By {APP_AUTHOR} )"

GITHUB_REPO = "ZvanTors/MTA-Assistant"
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"

REG_PATH = r"Software\MTA Assistant"
REG_VALUE_FOLDER = "MTAFolder"
REG_VALUE_NAME = "GameName"
REG_VALUE_FACTION = "Faction"
REG_VALUE_RANK = "Rank"
REG_VALUE_THEME = "Theme"
REG_VALUE_SKIPPED_VERSION = "SkippedVersion"
REG_VALUE_COMPRESSION = "CompressionLevel"

COMPRESSION_LEVELS = [250, 200, 150]
DEFAULT_COMPRESSION = 250

HINT_COLOR = "#6b7c93"

# --- Static factions ---
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

TAXI_RANKS = {
    "Rank 1": [("Shift", "shift", 7500), ("Service", "service", 6000)],
    "Rank 2": [("Shift", "shift", 7500), ("Service", "service", 8500)],
    "Rank 3": [("Shift", "shift", 7500), ("Service", "service", 10600)],
    "Rank 4": [("Shift", "shift", 7500), ("Service", "service", 13300)],
    "Rank 5": [("Shift", "shift", 7500), ("Service", "service", 15000)],
}

NEW_REPORTER_RANKS = {
    "Rank 1": [("SP", "sp", 25000), ("Day", "day", 9000),  ("Night", "night", 4000)],
    "Rank 2": [("SP", "sp", 25000), ("Day", "day", 1000),  ("Night", "night", 4000)],
    "Rank 3": [("SP", "sp", 25000), ("Day", "day", 12000), ("Night", "night", 5000)],
    "Rank 4": [("SP", "sp", 25000), ("Day", "day", 14000), ("Night", "night", 5000)],
    "Rank 5": [("SP", "sp", 25000), ("Day", "day", 15000), ("Night", "night", 6000)],
}

RANK_BASED_FACTIONS = {
    "Medic": MEDIC_RANKS,
    "Hitman Agency": HITMAN_RANKS,
    "Taxi": TAXI_RANKS,
    "New Reporter": NEW_REPORTER_RANKS,
}

COMING_SOON_FACTIONS = {
    "School Instructor": [
        ("Mojavez",  "mojavez"),
        ("Tamdid",   "tamdid"),
        ("Slot-Gun", "slot-gun"),
        ("Test",     "test"),
    ],
    "Mechanic": [
        ("Tuning",  "tuning"),
        ("towcar",  "towcar"),
        ("Repair",  "repair"),
        ("Refill",  "refill"),
        ("Service", "service"),
    ],
}

ALL_FACTION_NAMES = [
    "Police Department",
    "Police Federal",
    "National Guard",
    "Taxi",
    "Hitman Agency",
    "Medic",
    "School Instructor",
    "New Reporter",
    "Mechanic",
]

DEFAULT_FACTION = "Police Federal"
DEFAULT_RANK = "Rank 1"
DEFAULT_THEME = "light"

STAT_BAR_PALETTE = [
    "#3498db", "#e74c3c", "#27ae60",
    "#f39c12", "#9b59b6", "#1abc9c", "#e67e22",
]

# --- Fine Calculator (Police Department only) ---
FINE_BASE = 5000
FINE_STEP = 2000
FINE_SPEED_STEP = 20

FINE_LOCATIONS = [
    ("LS City", 120, "Los Santos city limits"),
    ("LV City", 170, "Las Venturas city limits"),
    ("SF City", 180, "San Fierro city limits"),
    ("Heavy Traffic Areas", 100, "Crossroads, Civilian Spawn, License route"),
    ("Highway / Outside Cities", 240, "Roads and highways around the cities"),
]

PD_FACTION_NAME = "Police Department"


def is_coming_soon(faction: str) -> bool:
    return faction in COMING_SOON_FACTIONS


def get_prices(faction: str, rank: str | None = None):
    if faction in RANK_BASED_FACTIONS:
        ranks = RANK_BASED_FACTIONS[faction]
        r = rank if rank in ranks else next(iter(ranks.keys()))
        return ranks[r]
    if faction in FACTIONS:
        return FACTIONS[faction]
    return []


def faction_requires_rank(faction: str) -> bool:
    return faction in RANK_BASED_FACTIONS


def get_faction_folder_specs(faction: str):
    if faction in COMING_SOON_FACTIONS:
        return list(COMING_SOON_FACTIONS[faction])
    if faction in RANK_BASED_FACTIONS:
        ranks = RANK_BASED_FACTIONS[faction]
        first_rank_prices = next(iter(ranks.values()))
        return [(n, k) for n, k, _ in first_rank_prices]
    if faction in FACTIONS:
        return [(n, k) for n, k, _ in FACTIONS[faction]]
    return []


def calculate_fine(limit_kmh: int, speed_kmh: int):
    """
    Returns a dict with details of the fine, or None if no violation.
    Formula: base $5000 + every 20 km/h over the limit adds $2000.
    """
    if speed_kmh <= limit_kmh:
        return None
    excess = speed_kmh - limit_kmh
    steps = excess // FINE_SPEED_STEP
    extra = steps * FINE_STEP
    total = FINE_BASE + extra
    return {
        "limit": limit_kmh,
        "speed": speed_kmh,
        "excess": excess,
        "steps": steps,
        "base": FINE_BASE,
        "extra": extra,
        "total": total,
    }


# ---------------------------------------------------------------------------
# Version helpers
# ---------------------------------------------------------------------------
def parse_version(v: str) -> tuple:
    v = (v or "").strip().lstrip("vV")
    parts = []
    for chunk in v.split("."):
        num = ""
        for ch in chunk:
            if ch.isdigit():
                num += ch
            else:
                break
        parts.append(int(num) if num else 0)
    return tuple(parts)


def is_newer_version(latest: str, current: str) -> bool:
    return parse_version(latest) > parse_version(current)


def format_size(bytes_: int) -> str:
    if bytes_ < 1024:
        return f"{bytes_} B"
    if bytes_ < 1024 * 1024:
        return f"{bytes_ / 1024:.1f} KB"
    if bytes_ < 1024 * 1024 * 1024:
        return f"{bytes_ / (1024 * 1024):.1f} MB"
    return f"{bytes_ / (1024 * 1024 * 1024):.2f} GB"


def format_eta(seconds: float) -> str:
    if seconds <= 1:
        return "less than a second"
    if seconds < 60:
        return f"~{int(seconds)} seconds"
    if seconds < 3600:
        m = int(seconds // 60)
        s = int(seconds % 60)
        return f"~{m}m {s}s"
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    return f"~{h}h {m}m"


# ---------------------------------------------------------------------------
# Resource path
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


def get_saved_theme() -> str:
    value = _read_value(REG_VALUE_THEME)
    if value in ("light", "dark"):
        return value
    return DEFAULT_THEME


def save_theme(theme: str) -> None:
    _write_value(REG_VALUE_THEME, theme)


def get_skipped_version() -> str | None:
    return _read_value(REG_VALUE_SKIPPED_VERSION)


def save_skipped_version(version: str) -> None:
    _write_value(REG_VALUE_SKIPPED_VERSION, version)


def get_saved_compression() -> int:
    value = _read_value(REG_VALUE_COMPRESSION)
    try:
        n = int(value) if value else DEFAULT_COMPRESSION
    except (ValueError, TypeError):
        n = DEFAULT_COMPRESSION
    if n not in COMPRESSION_LEVELS:
        n = DEFAULT_COMPRESSION
    return n


def save_compression(kb: int) -> None:
    if kb not in COMPRESSION_LEVELS:
        kb = DEFAULT_COMPRESSION
    _write_value(REG_VALUE_COMPRESSION, str(kb))


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


def _list_pngs_for_category(base_folder: str, key: str) -> list[Path]:
    screenshots_dir = Path(base_folder) / "screenshots"
    if not screenshots_dir.is_dir():
        return []
    try:
        subdirs = _collect_category_dirs(screenshots_dir)
    except OSError:
        return []
    cat = subdirs.get(key)
    if cat is None:
        return []
    result: list[Path] = []
    try:
        result.extend(
            sorted(f for f in cat.iterdir()
                   if f.is_file() and f.suffix.lower() == ".png")
        )
    except OSError:
        pass
    nested = _find_nested(cat, key)
    if nested is not None:
        try:
            result.extend(
                sorted(f for f in nested.iterdir()
                       if f.is_file() and f.suffix.lower() == ".png")
            )
        except OSError:
            pass
    return result


def estimate_png_size(base_folder: str, faction: str, rank: str | None = None) -> int:
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
        if cat is None:
            continue
        try:
            for f in cat.iterdir():
                if f.is_file() and f.suffix.lower() == ".png":
                    try:
                        total += f.stat().st_size
                    except OSError:
                        pass
        except OSError:
            pass
    return total


def estimate_output_size(total_png_bytes: int, file_count: int, max_kb: int) -> int:
    worst_case = file_count * max_kb * 1024
    likely = min(total_png_bytes, worst_case) if total_png_bytes > 0 else worst_case
    return int(likely * 1.05)


def create_faction_folders(base_folder: str, faction: str):
    screenshots_dir = Path(base_folder) / "screenshots"
    if not screenshots_dir.is_dir():
        try:
            screenshots_dir.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            return 0, 0, f"Failed to create 'screenshots' folder:\n{exc}"

    specs = get_faction_folder_specs(faction)
    if not specs:
        return 0, 0, f"Unknown faction: {faction}"

    try:
        existing = _collect_category_dirs(screenshots_dir)
    except OSError as exc:
        return 0, 0, f"Failed to read the screenshots folder:\n{exc}"

    created = 0
    skipped = 0
    errors: list[str] = []

    for display_name, key in specs:
        if key in existing:
            skipped += 1
            continue
        try:
            (screenshots_dir / display_name).mkdir(parents=True, exist_ok=True)
            created += 1
        except OSError as exc:
            errors.append(f"{display_name}: {exc}")

    if errors:
        return created, skipped, "\n".join(errors)
    return created, skipped, None


# ---------------------------------------------------------------------------
# Image processing
# ---------------------------------------------------------------------------
def compress_to_jpg(src_png: Path, dst_jpg: Path, max_bytes: int) -> None:
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
# Export helpers
# ---------------------------------------------------------------------------
def export_report_csv(path: str, faction_display: str, results,
                      total_count: int, total_amount: int) -> None:
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["MTA Assistant — Work Report"])
        writer.writerow(["Generated", datetime.now().strftime("%Y-%m-%d %H:%M")])
        writer.writerow(["Faction", faction_display])
        writer.writerow([])
        writer.writerow(["Category", "Screenshots", "Unit Price", "Total"])
        for name, count, price, subtotal in results:
            writer.writerow([name, count, price, subtotal])
        writer.writerow([])
        writer.writerow(["TOTAL", total_count, "", total_amount])


def export_report_pdf(path: str, faction_display: str, game_name: str,
                      results, total_count: int, total_amount: int) -> None:
    rows_html = "".join(
        f"<tr>"
        f"<td style='padding:8px; border-bottom:1px solid #e1e8ed;'>{name}</td>"
        f"<td style='padding:8px; text-align:center; border-bottom:1px solid #e1e8ed;'>{count}</td>"
        f"<td style='padding:8px; text-align:right; border-bottom:1px solid #e1e8ed;'>${price:,}</td>"
        f"<td style='padding:8px; text-align:right; border-bottom:1px solid #e1e8ed;'>${subtotal:,}</td>"
        f"</tr>"
        for name, count, price, subtotal in results
    )

    html = f"""
    <html>
    <head><meta charset="utf-8"></head>
    <body style="font-family: 'Segoe UI', Arial, sans-serif; color:#2c3e50;">
      <h1 style="color:#3498db; margin-bottom:4px;">MTA Assistant</h1>
      <h2 style="color:#34495e; margin-top:0;">Work Report</h2>
      <p style="color:#6b7c93; margin:2px 0;">
        <b>Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M')}<br>
        <b>Player:</b> {game_name or '(not set)'}<br>
        <b>Faction:</b> {faction_display}
      </p>
      <br>
      <table style="width:100%; border-collapse:collapse; border:1px solid #e1e8ed;">
        <thead>
          <tr style="background:#3498db; color:white;">
            <th style="padding:10px; text-align:left;">Category</th>
            <th style="padding:10px; text-align:center;">Screenshots</th>
            <th style="padding:10px; text-align:right;">Unit Price</th>
            <th style="padding:10px; text-align:right;">Total</th>
          </tr>
        </thead>
        <tbody>
          {rows_html}
        </tbody>
      </table>
      <br>
      <table style="width:100%; background:#eaf4fc; border-radius:6px;">
        <tr>
          <td style="padding:12px; font-weight:bold;">Total Screenshots: {total_count:,}</td>
          <td style="padding:12px; text-align:right; font-weight:bold;">Total Amount: ${total_amount:,}</td>
        </tr>
      </table>
      <br><br>
      <p style="color:#95a5a6; font-size:10px; text-align:center;">
        Made with ♥ by {APP_AUTHOR} — MTA Assistant v{APP_VERSION}
      </p>
    </body>
    </html>
    """

    printer = QPrinter(QPrinter.HighResolution)
    printer.setOutputFormat(QPrinter.PdfFormat)
    printer.setOutputFileName(path)
    printer.setPageSize(QPageSize(QPageSize.A4))
    printer.setPageMargins(QMarginsF(15, 15, 15, 15), QPageLayout.Millimeter)

    doc = QTextDocument()
    doc.setHtml(html)
    doc.print_(printer)


# ---------------------------------------------------------------------------
# Convert worker
# ---------------------------------------------------------------------------
class ConvertWorker(QThread):
    progress = Signal(int, int)
    finished_ok = Signal(str, str)
    failed = Signal(str)

    def __init__(self, base_folder: str, game_name: str, faction: str,
                 rank: str | None = None, max_kb: int = DEFAULT_COMPRESSION,
                 parent=None):
        super().__init__(parent)
        self.base_folder = base_folder
        self.game_name = game_name
        self.faction = faction
        self.rank = rank
        self.max_kb = max_kb

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

        max_bytes = self.max_kb * 1024
        done = 0
        for display_name, key, _ in get_prices(self.faction, self.rank):
            dst_dir = target / display_name
            try:
                dst_dir.mkdir(parents=True, exist_ok=True)
            except OSError as exc:
                self.failed.emit(f"Failed to create '{display_name}' folder:\n{exc}")
                return

            cat = subdirs.get(key)
            if cat is None:
                continue

            try:
                pngs = [f for f in cat.iterdir()
                        if f.is_file() and f.suffix.lower() == ".png"]
            except OSError:
                pngs = []

            for png in pngs:
                dst_jpg = dst_dir / (png.stem + ".jpg")
                try:
                    compress_to_jpg(png, dst_jpg, max_bytes=max_bytes)
                except Exception as exc:
                    self.failed.emit(f"Failed to process '{png.name}':\n{exc}")
                    return
                done += 1
                self.progress.emit(done, total)

        zip_base = desktop / self.game_name
        zip_path = Path(f"{zip_base}.zip")
        try:
            if zip_path.exists():
                zip_path.unlink()
            shutil.make_archive(
                base_name=str(zip_base), format="zip",
                root_dir=str(desktop), base_dir=target.name,
            )
        except OSError as exc:
            self.failed.emit(
                "The folder was created successfully, but zipping it failed:\n"
                f"{exc}"
            )
            return

        self.finished_ok.emit(str(target), str(zip_path))


# ---------------------------------------------------------------------------
# Update checker
# ---------------------------------------------------------------------------
class UpdateChecker(QThread):
    update_available = Signal(str, str, str)
    no_update = Signal()
    check_failed = Signal(str)

    def __init__(self, current_version: str, parent=None):
        super().__init__(parent)
        self.current_version = current_version

    def run(self) -> None:
        try:
            req = urllib.request.Request(
                GITHUB_API_URL,
                headers={
                    "User-Agent": f"{APP_NAME}/{APP_VERSION}",
                    "Accept": "application/vnd.github+json",
                },
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                raw = resp.read().decode("utf-8")
            data = json.loads(raw)
        except Exception as exc:
            self.check_failed.emit(str(exc))
            return

        latest_tag = (data.get("tag_name") or "").strip()
        if not latest_tag:
            self.check_failed.emit("No tag_name in release response.")
            return

        latest_version = latest_tag.lstrip("vV")
        if not is_newer_version(latest_version, self.current_version):
            self.no_update.emit()
            return

        release_url = data.get("html_url") or f"https://github.com/{GITHUB_REPO}/releases"

        download_url = ""
        for asset in data.get("assets", []) or []:
            name = (asset.get("name") or "").lower()
            if name.endswith(".exe"):
                url = asset.get("browser_download_url") or ""
                if url.startswith("https://"):
                    download_url = url
                    break

        if not download_url:
            download_url = release_url

        self.update_available.emit(latest_version, download_url, release_url)


# ---------------------------------------------------------------------------
# Stylesheets — Light & Dark
# ---------------------------------------------------------------------------
QSS_LIGHT = """
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
        background: #3498db; color: white; border: none;
        border-radius: 6px; padding: 8px 18px; font-weight: 600;
    }
    QPushButton:hover { background: #2980b9; }
    QPushButton:pressed { background: #2471a3; }
    QPushButton:disabled { background: #bdc3c7; }
    QPushButton#secondaryButton { background: #ecf0f1; color: #2c3e50; }
    QPushButton#secondaryButton:hover { background: #dfe4e6; }
    QPushButton#backButton {
        background: #ecf0f1; color: #2c3e50; padding: 6px 14px; font-weight: 500;
    }
    QPushButton#backButton:hover { background: #dfe4e6; }
    QPushButton#dangerButton { background: #e74c3c; color: white; }
    QPushButton#dangerButton:hover { background: #c0392b; }
    QPushButton#dangerButton:pressed { background: #a93226; }
    QPushButton#dangerButton:disabled { background: #e6b0aa; }
    QLineEdit {
        background: #ffffff; border: 1px solid #d6dee6; border-radius: 6px;
        padding: 6px 10px; selection-background-color: #3498db;
    }
    QLineEdit:focus { border: 1px solid #3498db; }
    QRadioButton { color: #2c3e50; spacing: 10px; }
    QRadioButton::indicator {
        width: 16px; height: 16px; border: 2px solid #b0bec5;
        border-radius: 9px; background: white;
    }
    QRadioButton::indicator:hover { border-color: #3498db; }
    QRadioButton::indicator:checked { border: 5px solid #3498db; background: white; }
    QCheckBox { color: #2c3e50; spacing: 8px; }
    QCheckBox::indicator {
        width: 16px; height: 16px; border: 2px solid #b0bec5;
        border-radius: 4px; background: white;
    }
    QCheckBox::indicator:hover { border-color: #3498db; }
    QCheckBox::indicator:checked { background: #3498db; border-color: #3498db; }
    QFrame#card {
        background: #ffffff; border: 1px solid #e1e8ed; border-radius: 10px;
    }
    QProgressBar {
        background: #ecf0f1; border: 1px solid #d6dee6; border-radius: 6px;
        text-align: center; color: #2c3e50; font-weight: 600; height: 22px;
    }
    QProgressBar::chunk { background: #3498db; border-radius: 5px; }
    QTableWidget {
        background: #ffffff; border: 1px solid #e1e8ed; border-radius: 8px;
        gridline-color: #eef2f5; alternate-background-color: #f7fafc;
        font-size: 13px;
    }
    QTableWidget::item { padding: 6px; }
    QTableWidget::item:selected { background: #eaf4fc; color: #2c3e50; }
    QHeaderView::section {
        background: #3498db; color: white; padding: 10px;
        border: none; font-weight: bold;
    }
    QHeaderView::section:first { border-top-left-radius: 8px; }
    QHeaderView::section:last { border-top-right-radius: 8px; }
    QScrollArea { background: #f7f9fb; border: none; }
    QScrollArea > QWidget > QWidget { background: #f7f9fb; }
    QLabel#summaryLabel {
        font-size: 15px; font-weight: bold; color: #2c3e50;
        background: #eaf4fc; padding: 12px 16px; border-radius: 8px;
    }
    QLabel#hintLabel { color: #6b7c93; }
"""

QSS_DARK = """
    QMainWindow, QDialog { background: #1a1a2e; }
    QWidget { font-family: "Segoe UI"; font-size: 13px; color: #e8e8f0; }
    QMenuBar { background: #252540; border-bottom: 1px solid #353555; color: #e8e8f0; }
    QMenuBar::item { padding: 6px 12px; background: transparent; }
    QMenuBar::item:selected { background: #353555; border-radius: 4px; }
    QMenu { background: #252540; border: 1px solid #353555; padding: 4px; color: #e8e8f0; }
    QMenu::item { padding: 6px 22px; border-radius: 4px; }
    QMenu::item:selected { background: #353555; }
    QMenu::item:disabled { color: #555570; }
    QPushButton {
        background: #4a9eff; color: white; border: none;
        border-radius: 6px; padding: 8px 18px; font-weight: 600;
    }
    QPushButton:hover { background: #3a8eef; }
    QPushButton:pressed { background: #2a7edf; }
    QPushButton:disabled { background: #3a3a4e; color: #777788; }
    QPushButton#secondaryButton { background: #353555; color: #e8e8f0; }
    QPushButton#secondaryButton:hover { background: #404060; }
    QPushButton#backButton {
        background: #353555; color: #e8e8f0; padding: 6px 14px; font-weight: 500;
    }
    QPushButton#backButton:hover { background: #404060; }
    QPushButton#dangerButton { background: #e74c3c; color: white; }
    QPushButton#dangerButton:hover { background: #c0392b; }
    QPushButton#dangerButton:pressed { background: #a93226; }
    QPushButton#dangerButton:disabled { background: #5a3a3a; color: #a08080; }
    QLineEdit {
        background: #252540; border: 1px solid #353555; border-radius: 6px;
        padding: 6px 10px; color: #e8e8f0; selection-background-color: #4a9eff;
    }
    QLineEdit:focus { border: 1px solid #4a9eff; }
    QRadioButton { color: #e8e8f0; spacing: 10px; }
    QRadioButton::indicator {
        width: 16px; height: 16px; border: 2px solid #555570;
        border-radius: 9px; background: #252540;
    }
    QRadioButton::indicator:hover { border-color: #4a9eff; }
    QRadioButton::indicator:checked { border: 5px solid #4a9eff; background: #252540; }
    QCheckBox { color: #e8e8f0; spacing: 8px; }
    QCheckBox::indicator {
        width: 16px; height: 16px; border: 2px solid #555570;
        border-radius: 4px; background: #252540;
    }
    QCheckBox::indicator:hover { border-color: #4a9eff; }
    QCheckBox::indicator:checked { background: #4a9eff; border-color: #4a9eff; }
    QFrame#card {
        background: #252540; border: 1px solid #353555; border-radius: 10px;
    }
    QProgressBar {
        background: #353555; border: 1px solid #454565; border-radius: 6px;
        text-align: center; color: #e8e8f0; font-weight: 600; height: 22px;
    }
    QProgressBar::chunk { background: #4a9eff; border-radius: 5px; }
    QTableWidget {
        background: #252540; border: 1px solid #353555; border-radius: 8px;
        gridline-color: #353555; alternate-background-color: #2a2a48;
        font-size: 13px; color: #e8e8f0;
    }
    QTableWidget::item { padding: 6px; }
    QTableWidget::item:selected { background: #353570; color: #ffffff; }
    QHeaderView::section {
        background: #4a9eff; color: white; padding: 10px;
        border: none; font-weight: bold;
    }
    QHeaderView::section:first { border-top-left-radius: 8px; }
    QHeaderView::section:last { border-top-right-radius: 8px; }
    QScrollArea { background: #1a1a2e; border: none; }
    QScrollArea > QWidget > QWidget { background: #1a1a2e; }
    QLabel { color: #e8e8f0; }
    QLabel#summaryLabel {
        font-size: 15px; font-weight: bold; color: #e8e8f0;
        background: #353555; padding: 12px 16px; border-radius: 8px;
    }
    QLabel#hintLabel { color: #9aa3b2; }
"""


# ---------------------------------------------------------------------------
# Centered Dialog base
# ---------------------------------------------------------------------------
class CenteredDialog(QDialog):
    """QDialog that automatically centers itself on its parent (or the
    screen under the mouse cursor) when shown."""

    def showEvent(self, event):
        super().showEvent(event)
        QTimer.singleShot(0, self._center_on_parent)

    def _center_on_parent(self) -> None:
        parent = self.parentWidget()
        if parent is not None and parent.isVisible():
            try:
                parent_rect = parent.frameGeometry()
                self_rect = self.frameGeometry()
                self_rect.moveCenter(parent_rect.center())
                self.move(self_rect.topLeft())
                return
            except Exception:
                pass
        screen = QApplication.screenAt(QCursor.pos()) or QApplication.primaryScreen()
        if screen is not None:
            geo = screen.availableGeometry()
            self_rect = self.frameGeometry()
            self_rect.moveCenter(geo.center())
            self.move(self_rect.topLeft())


# ---------------------------------------------------------------------------
# Update dialog
# ---------------------------------------------------------------------------
class UpdateDialog(CenteredDialog):
    def __init__(self, parent, latest_version: str,
                 download_url: str, release_url: str):
        super().__init__(parent)
        self.latest_version = latest_version
        self.download_url = download_url
        self.release_url = release_url
        self.skip_version = False

        self.setWindowTitle("Update Available")
        self.setModal(True)
        self.setMinimumWidth(500)
        self._build_ui()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(14)

        title = QLabel("🎉 A new version is available!")
        title.setStyleSheet("font-size: 17px; font-weight: bold;")
        root.addWidget(title)

        info = QLabel(
            f"<b>Current version:</b> v{APP_VERSION}<br>"
            f"<b>Latest version:</b> v{self.latest_version}<br><br>"
            "Would you like to download the latest version now?"
        )
        info.setWordWrap(True)
        root.addWidget(info)

        self.skip_check = QCheckBox("Skip this version")
        root.addWidget(self.skip_check)

        btns = QHBoxLayout()
        btns.addStretch()

        later_btn = QPushButton("Later")
        later_btn.setObjectName("secondaryButton")
        later_btn.setMinimumHeight(36)
        later_btn.setMinimumWidth(100)
        later_btn.clicked.connect(self.reject)
        btns.addWidget(later_btn)

        download_btn = QPushButton("Download Now")
        download_btn.setMinimumHeight(36)
        download_btn.setMinimumWidth(140)
        download_btn.setDefault(True)
        download_btn.clicked.connect(self._on_download)
        btns.addWidget(download_btn)

        root.addLayout(btns)

    def _on_download(self) -> None:
        QDesktopServices.openUrl(QUrl(self.download_url))
        self.accept()

    def _capture_skip(self) -> None:
        self.skip_version = self.skip_check.isChecked()

    def accept(self) -> None:
        self._capture_skip()
        super().accept()

    def reject(self) -> None:
        self._capture_skip()
        super().reject()

    def closeEvent(self, event) -> None:
        self._capture_skip()
        super().closeEvent(event)


# ---------------------------------------------------------------------------
# Setup Wizard
# ---------------------------------------------------------------------------
class SetupWizard(CenteredDialog):
    def __init__(self, parent, initial_folder: str = "",
                 initial_faction: str | None = None,
                 initial_rank: str | None = None,
                 initial_theme: str = "light"):
        super().__init__(parent)
        self.setWindowTitle("Welcome to MTA Assistant")
        self.setModal(True)
        self.resize(700, 560)

        self.folder_value = initial_folder or ""
        self.faction_value = initial_faction or DEFAULT_FACTION
        self.rank_value = initial_rank or DEFAULT_RANK
        self.game_name_value = ""
        self.theme_value = initial_theme if initial_theme in ("light", "dark") else "light"

        self.setStyleSheet(QSS_DARK if self.theme_value == "dark" else QSS_LIGHT)

        self._build_ui()
        self._rebuild_rank_radios()
        self._rebuild_summary()
        self._update_nav()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 20)
        root.setSpacing(12)

        self.title_label = QLabel("🎮 Welcome to MTA Assistant")
        self.title_label.setStyleSheet("font-size: 22px; font-weight: bold;")
        root.addWidget(self.title_label)

        self.subtitle_label = QLabel("Let's get you set up in a few quick steps.")
        self.subtitle_label.setObjectName("hintLabel")
        root.addWidget(self.subtitle_label)

        self.progress_label = QLabel("")
        self.progress_label.setAlignment(Qt.AlignCenter)
        self.progress_label.setObjectName("hintLabel")
        root.addWidget(self.progress_label)

        self.stack = QStackedWidget()
        self.page_folder = self._build_folder_page()
        self.page_faction = self._build_faction_page()
        self.page_rank = self._build_rank_page()
        self.page_profile = self._build_profile_page()
        self.page_finish = self._build_finish_page()
        self.stack.addWidget(self.page_folder)
        self.stack.addWidget(self.page_faction)
        self.stack.addWidget(self.page_rank)
        self.stack.addWidget(self.page_profile)
        self.stack.addWidget(self.page_finish)
        root.addWidget(self.stack, 1)

        nav = QHBoxLayout()
        self.btn_back = QPushButton("←  Back")
        self.btn_back.setObjectName("secondaryButton")
        self.btn_back.setMinimumHeight(40)
        self.btn_back.setMinimumWidth(130)
        self.btn_back.clicked.connect(self._go_back)
        nav.addWidget(self.btn_back)
        nav.addStretch()
        self.btn_next = QPushButton("Next  →")
        self.btn_next.setMinimumHeight(40)
        self.btn_next.setMinimumWidth(150)
        self.btn_next.clicked.connect(self._go_next)
        nav.addWidget(self.btn_next)
        root.addLayout(nav)

    def _build_folder_page(self) -> QWidget:
        page = QWidget()
        v = QVBoxLayout(page)
        v.setSpacing(14)

        t = QLabel("Step 1 — MTA:SA Folder")
        t.setStyleSheet("font-size: 16px; font-weight: bold;")
        v.addWidget(t)

        hint = QLabel(
            "Select the installation folder of MTA:SA — the one that "
            "contains the 'screenshots' directory."
        )
        hint.setWordWrap(True)
        hint.setObjectName("hintLabel")
        v.addWidget(hint)

        row = QHBoxLayout()
        self.wizard_folder_edit = QLineEdit(self.folder_value)
        self.wizard_folder_edit.setPlaceholderText(
            r"C:\Program Files (x86)\MTA San Andreas 1.6"
        )
        self.wizard_folder_edit.setMinimumHeight(38)
        self.wizard_folder_edit.textChanged.connect(self._on_folder_changed)
        browse = QPushButton("Browse...")
        browse.setMinimumHeight(38)
        browse.clicked.connect(self._browse_wizard_folder)
        row.addWidget(self.wizard_folder_edit, 1)
        row.addWidget(browse)
        v.addLayout(row)

        self.folder_error = QLabel("")
        self.folder_error.setStyleSheet("color: #c0392b; font-size: 12px;")
        self.folder_error.setWordWrap(True)
        v.addWidget(self.folder_error)

        v.addStretch()
        return page

    def _build_faction_page(self) -> QWidget:
        page = QWidget()
        v = QVBoxLayout(page)
        v.setSpacing(12)

        t = QLabel("Step 2 — Your Faction")
        t.setStyleSheet("font-size: 16px; font-weight: bold;")
        v.addWidget(t)

        hint = QLabel(
            "Pick your faction. Prices and category folders depend on this."
        )
        hint.setWordWrap(True)
        hint.setObjectName("hintLabel")
        v.addWidget(hint)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        container = QWidget()
        cv = QVBoxLayout(container)
        cv.setSpacing(4)

        self.wizard_faction_group = QButtonGroup(self)
        self.wizard_faction_radios: dict[str, QRadioButton] = {}
        for name in ALL_FACTION_NAMES:
            rb = QRadioButton(name)
            rb.setMinimumHeight(34)
            rb.setChecked(name == self.faction_value)
            rb.toggled.connect(
                lambda checked: self._on_faction_changed() if checked else None
            )
            self.wizard_faction_group.addButton(rb)
            self.wizard_faction_radios[name] = rb
            cv.addWidget(rb)
        cv.addStretch()
        scroll.setWidget(container)
        v.addWidget(scroll, 1)
        return page

    def _build_rank_page(self) -> QWidget:
        page = QWidget()
        v = QVBoxLayout(page)
        v.setSpacing(12)

        t = QLabel("Step 3 — Your Rank")
        t.setStyleSheet("font-size: 16px; font-weight: bold;")
        v.addWidget(t)

        self.wizard_rank_notice = QLabel("")
        self.wizard_rank_notice.setWordWrap(True)
        self.wizard_rank_notice.setStyleSheet(
            "background: rgba(0,0,0,0.04); padding: 10px; border-radius: 6px;"
        )
        v.addWidget(self.wizard_rank_notice)

        self.rank_scroll = QScrollArea()
        self.rank_scroll.setWidgetResizable(True)
        self.rank_container = QWidget()
        self.rank_container_layout = QVBoxLayout(self.rank_container)
        self.rank_container_layout.setSpacing(4)
        self.rank_scroll.setWidget(self.rank_container)
        v.addWidget(self.rank_scroll, 1)

        self.wizard_rank_group = QButtonGroup(self)
        self.wizard_rank_radios: dict[str, QRadioButton] = {}
        return page

    def _build_profile_page(self) -> QWidget:
        page = QWidget()
        v = QVBoxLayout(page)
        v.setSpacing(12)

        t = QLabel("Step 4 — Your Profile")
        t.setStyleSheet("font-size: 16px; font-weight: bold;")
        v.addWidget(t)

        hint = QLabel("Your in-game name and app theme. Both can be changed later.")
        hint.setWordWrap(True)
        hint.setObjectName("hintLabel")
        v.addWidget(hint)

        name_lbl = QLabel("In-game Name (optional)")
        name_lbl.setStyleSheet("font-weight: bold; margin-top: 6px;")
        v.addWidget(name_lbl)

        self.wizard_name_edit = QLineEdit("")
        self.wizard_name_edit.setPlaceholderText("(AmooReza)")
        self.wizard_name_edit.setMinimumHeight(38)
        v.addWidget(self.wizard_name_edit)

        theme_lbl = QLabel("Theme")
        theme_lbl.setStyleSheet("font-weight: bold; margin-top: 10px;")
        v.addWidget(theme_lbl)

        self.wizard_theme_group = QButtonGroup(self)
        self.wizard_theme_radios: dict[str, QRadioButton] = {}
        for theme_name, label in (("light", "Light"), ("dark", "Dark")):
            rb = QRadioButton(label)
            rb.setMinimumHeight(34)
            rb.setChecked(theme_name == self.theme_value)
            rb.toggled.connect(
                lambda checked, t=theme_name: self._on_theme_changed(t) if checked else None
            )
            self.wizard_theme_group.addButton(rb)
            self.wizard_theme_radios[theme_name] = rb
            v.addWidget(rb)

        v.addStretch()
        return page

    def _build_finish_page(self) -> QWidget:
        page = QWidget()
        v = QVBoxLayout(page)
        v.setSpacing(14)

        t = QLabel("✅  All set!")
        t.setStyleSheet("font-size: 20px; font-weight: bold;")
        v.addWidget(t)

        hint = QLabel("Here's a summary of your setup:")
        hint.setObjectName("hintLabel")
        v.addWidget(hint)

        self.summary_label = QLabel()
        self.summary_label.setWordWrap(True)
        self.summary_label.setStyleSheet(
            "background: rgba(0,0,0,0.04); padding: 18px; border-radius: 8px;"
        )
        v.addWidget(self.summary_label)

        done_hint = QLabel(
            "You can change any of these settings later from the Settings menu."
        )
        done_hint.setWordWrap(True)
        done_hint.setObjectName("hintLabel")
        v.addWidget(done_hint)

        v.addStretch()
        return page

    def _get_selected_faction(self) -> str:
        for name, rb in self.wizard_faction_radios.items():
            if rb.isChecked():
                return name
        return self.faction_value

    def _get_active_pages(self) -> list[int]:
        pages = [0, 1]
        if faction_requires_rank(self._get_selected_faction()):
            pages.append(2)
        pages.append(3)
        pages.append(4)
        return pages

    def _rebuild_rank_radios(self) -> None:
        for rb in list(self.wizard_rank_radios.values()):
            try:
                self.wizard_rank_group.removeButton(rb)
            except Exception:
                pass
            rb.setParent(None)
            rb.deleteLater()
        self.wizard_rank_radios.clear()

        while self.rank_container_layout.count():
            item = self.rank_container_layout.takeAt(0)
            w = item.widget()
            if w is not None:
                w.deleteLater()

        faction = self._get_selected_faction()
        if not faction_requires_rank(faction):
            self.wizard_rank_notice.setText(
                f"'{faction}' does not use ranks. You can continue to the next step."
            )
            self.rank_scroll.setVisible(False)
            return

        self.rank_scroll.setVisible(True)
        self.wizard_rank_notice.setText(
            f"'{faction}' supports 5 ranks, each with its own price list."
        )

        ranks = RANK_BASED_FACTIONS.get(faction, {})
        first_rank = next(iter(ranks.keys()), None)
        any_checked = False

        for rank_name, prices in ranks.items():
            price_str = "  |  ".join(f"{n} ${p:,}" for n, _, p in prices)
            label = f"{rank_name}   —   {price_str}"
            rb = QRadioButton(label)
            rb.setMinimumHeight(36)
            if self.rank_value == rank_name:
                rb.setChecked(True)
                any_checked = True
            elif rank_name == first_rank and not any_checked:
                rb.setChecked(True)
                self.rank_value = rank_name
                any_checked = True
            self.wizard_rank_group.addButton(rb)
            self.wizard_rank_radios[rank_name] = rb
            self.rank_container_layout.addWidget(rb)

        self.rank_container_layout.addStretch()

    def _rebuild_summary(self) -> None:
        faction = self._get_selected_faction()
        name = self.wizard_name_edit.text().strip() if hasattr(self, "wizard_name_edit") else ""
        name_display = name if name else "(not set)"
        theme = "Dark" if self.theme_value == "dark" else "Light"

        lines = [
            f"<b>MTA Folder:</b>&nbsp; {self.folder_value or '(not set)'}",
            f"<b>Faction:</b>&nbsp; {faction}",
        ]
        if faction_requires_rank(faction):
            lines.append(f"<b>Rank:</b>&nbsp; {self.rank_value}")
        lines.append(f"<b>Game Name:</b>&nbsp; {name_display}")
        lines.append(f"<b>Theme:</b>&nbsp; {theme}")

        self.summary_label.setText("<br>".join(lines))

    def _update_nav(self) -> None:
        idx = self.stack.currentIndex()
        active = self._get_active_pages()
        try:
            pos = active.index(idx)
        except ValueError:
            pos = 0

        self.btn_back.setEnabled(pos > 0)
        self.btn_next.setText("Finish  ✓" if idx == 4 else "Next  →")

        if idx == 4:
            self.progress_label.setText("Ready to finish")
        else:
            self.progress_label.setText(f"Step {pos + 1} of {len(active) - 1}")

    def _go_next(self) -> None:
        idx = self.stack.currentIndex()

        if idx == 0:
            if not self._validate_folder():
                return
        elif idx == 1:
            if not self._validate_faction():
                return
            self._rebuild_rank_radios()
            self._rebuild_summary()
        elif idx == 2:
            if not self._validate_rank():
                return
        elif idx == 3:
            if not self._validate_profile():
                return
            self._rebuild_summary()
        elif idx == 4:
            if self._validate_all():
                self.accept()
            return

        active = self._get_active_pages()
        try:
            pos = active.index(idx)
        except ValueError:
            pos = 0
        if pos + 1 < len(active):
            self.stack.setCurrentIndex(active[pos + 1])
            self._update_nav()

    def _go_back(self) -> None:
        idx = self.stack.currentIndex()
        active = self._get_active_pages()
        try:
            pos = active.index(idx)
        except ValueError:
            pos = 0
        if pos > 0:
            self.stack.setCurrentIndex(active[pos - 1])
            self._update_nav()

    def _validate_folder(self) -> bool:
        path = self.wizard_folder_edit.text().strip()
        if not path:
            self.folder_error.setText("Please select a folder.")
            return False
        if not Path(path).is_dir():
            self.folder_error.setText("The selected folder does not exist.")
            return False
        self.folder_value = path
        self.folder_error.setText("")
        return True

    def _validate_faction(self) -> bool:
        for name, rb in self.wizard_faction_radios.items():
            if rb.isChecked():
                self.faction_value = name
                return True
        return False

    def _validate_rank(self) -> bool:
        faction = self._get_selected_faction()
        if not faction_requires_rank(faction):
            return True
        for name, rb in self.wizard_rank_radios.items():
            if rb.isChecked():
                self.rank_value = name
                return True
        QMessageBox.warning(self, "Rank", "Please select a rank.")
        return False

    def _validate_profile(self) -> bool:
        name = self.wizard_name_edit.text().strip()
        if name:
            forbidden = set('\\/:*?"<>|')
            if any(ch in forbidden for ch in name):
                QMessageBox.warning(
                    self, "Invalid Name",
                    "The name contains characters that are not allowed in "
                    "Windows folder names:\n\\ / : * ? \" < > |"
                )
                return False
        self.game_name_value = name
        for theme_name, rb in self.wizard_theme_radios.items():
            if rb.isChecked():
                self.theme_value = theme_name
                break
        return True

    def _validate_all(self) -> bool:
        if not self._validate_folder():
            self.stack.setCurrentIndex(0); self._update_nav(); return False
        if not self._validate_faction():
            self.stack.setCurrentIndex(1); self._update_nav(); return False
        if not self._validate_rank():
            active = self._get_active_pages()
            if 2 in active:
                self.stack.setCurrentIndex(2); self._update_nav()
            return False
        if not self._validate_profile():
            self.stack.setCurrentIndex(3); self._update_nav(); return False
        return True

    def _on_folder_changed(self, text: str) -> None:
        self.folder_value = text.strip()

    def _on_faction_changed(self) -> None:
        self.faction_value = self._get_selected_faction()

    def _on_theme_changed(self, theme: str) -> None:
        self.theme_value = theme
        self.setStyleSheet(QSS_DARK if theme == "dark" else QSS_LIGHT)

    def _browse_wizard_folder(self) -> None:
        start = self.wizard_folder_edit.text().strip()
        if not start or not Path(start).is_dir():
            start = str(Path.home())
        folder = QFileDialog.getExistingDirectory(self, "Select MTA:SA Folder", start)
        if folder:
            self.wizard_folder_edit.setText(folder)


# ---------------------------------------------------------------------------
# Preview dialog
# ---------------------------------------------------------------------------
class PreviewDialog(CenteredDialog):
    def __init__(self, parent, faction_display: str, game_name: str,
                 total_files: int, total_png_bytes: int,
                 estimated_bytes: int, max_kb: int,
                 free_bytes: int, target_path: Path):
        super().__init__(parent)
        self.setWindowTitle("Preview Work Report")
        self.setModal(True)
        self.setMinimumWidth(560)
        self.faction_display = faction_display
        self.game_name = game_name
        self.total_files = total_files
        self.total_png_bytes = total_png_bytes
        self.estimated_bytes = estimated_bytes
        self.max_kb = max_kb
        self.free_bytes = free_bytes
        self.target_path = target_path
        self._build_ui()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(14)

        title = QLabel("📋 Review before creating")
        title.setStyleSheet("font-size: 17px; font-weight: bold;")
        root.addWidget(title)

        hint = QLabel("Make sure everything looks right. Click Create to start.")
        hint.setWordWrap(True)
        hint.setObjectName("hintLabel")
        root.addWidget(hint)

        card = QFrame()
        card.setObjectName("card")
        v = QVBoxLayout(card)
        v.setContentsMargins(18, 16, 18, 16)
        v.setSpacing(8)

        def row(label, value, value_color=None):
            h = QHBoxLayout()
            l = QLabel(label)
            l.setStyleSheet("font-weight: bold;")
            l.setMinimumWidth(180)
            val = QLabel(str(value))
            val.setWordWrap(True)
            if value_color:
                val.setStyleSheet(f"color: {value_color};")
            h.addWidget(l)
            h.addWidget(val, 1)
            v.addLayout(h)

        row("Faction", self.faction_display)
        row("Game Name", self.game_name or "(not set)")
        row("Total screenshots", f"{self.total_files:,}")
        row("Current size (PNG)", format_size(self.total_png_bytes))
        row("Compression", f"max {self.max_kb} KB per image")
        row("Estimated output", format_size(self.estimated_bytes),
            value_color="#27ae60")

        if self.free_bytes > 0:
            free_color = "#27ae60"
            if self.estimated_bytes > self.free_bytes * 0.9:
                free_color = "#c0392b"
            elif self.estimated_bytes > self.free_bytes * 0.5:
                free_color = "#e67e22"
            row("Free disk space", format_size(self.free_bytes),
                value_color=free_color)

        row("Target folder", str(self.target_path))
        root.addWidget(card)

        btns = QHBoxLayout()
        btns.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("secondaryButton")
        cancel_btn.setMinimumHeight(40)
        cancel_btn.setMinimumWidth(120)
        cancel_btn.clicked.connect(self.reject)
        btns.addWidget(cancel_btn)

        create_btn = QPushButton("Create  ✓")
        create_btn.setMinimumHeight(40)
        create_btn.setMinimumWidth(160)
        create_btn.setDefault(True)
        create_btn.clicked.connect(self.accept)
        btns.addWidget(create_btn)

        root.addLayout(btns)


# ---------------------------------------------------------------------------
# Folder picker dialog
# ---------------------------------------------------------------------------
class FolderPickerDialog(CenteredDialog):
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
            "the 'screenshots' directory."
        )
        hint.setWordWrap(True)
        hint.setObjectName("hintLabel")
        root.addWidget(hint)

        row = QHBoxLayout()
        row.setSpacing(8)
        self.path_edit = QLineEdit(initial)
        self.path_edit.setPlaceholderText(r"C:\Program Files (x86)\MTA San Andreas 1.6")
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
        folder = QFileDialog.getExistingDirectory(self, "Select MTA:SA Folder", start)
        if folder:
            self.path_edit.setText(folder)

    def _confirm(self) -> None:
        path = self.path_edit.text().strip()
        if not path:
            QMessageBox.warning(self, "Invalid Path", "Please select a folder first.")
            return
        if not Path(path).is_dir():
            QMessageBox.warning(self, "Invalid Path", "The selected folder does not exist.")
            return
        self.selected_path = path
        self.accept()


# ---------------------------------------------------------------------------
# Faction picker dialog
# ---------------------------------------------------------------------------
class FactionDialog(CenteredDialog):
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
        hint.setObjectName("hintLabel")
        root.addWidget(hint)

        self.group = QButtonGroup(self)
        self.radios: dict[str, QRadioButton] = {}

        for name in ALL_FACTION_NAMES:
            rb = QRadioButton(name)
            rb.setMinimumHeight(36)
            rb.setStyleSheet("QRadioButton { padding: 8px 12px; font-size: 14px; }")
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
        QMessageBox.warning(self, "Invalid Selection", "Please select a faction.")


# ---------------------------------------------------------------------------
# Rank picker dialog
# ---------------------------------------------------------------------------
class RankDialog(CenteredDialog):
    def __init__(self, parent=None, faction: str = "Medic",
                 initial: str | None = None):
        super().__init__(parent)
        self.rank_value: str | None = None
        self.faction_name = faction
        self.setWindowTitle(f"Select Your {faction} Rank")
        self.setModal(True)
        self.setMinimumWidth(620)
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
            "Prices depend on your rank. You can change this later in Settings."
        )
        hint.setWordWrap(True)
        hint.setObjectName("hintLabel")
        root.addWidget(hint)

        self.group = QButtonGroup(self)
        self.radios: dict[str, QRadioButton] = {}
        first_rank = next(iter(ranks.keys()), None)

        for rank_name, prices in ranks.items():
            price_str = "  |  ".join(f"{n} ${p:,}" for n, _, p in prices)
            label = f"{rank_name}   —   {price_str}"
            rb = QRadioButton(label)
            rb.setMinimumHeight(38)
            rb.setStyleSheet("QRadioButton { padding: 8px 12px; font-size: 13px; }")
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
        QMessageBox.warning(self, "Invalid Selection", "Please select a rank.")


# ---------------------------------------------------------------------------
# Game-name dialog
# ---------------------------------------------------------------------------
class GameNameDialog(CenteredDialog):
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
        hint.setObjectName("hintLabel")
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
            QMessageBox.warning(self, "Invalid Name", "Please enter your in-game name.")
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
# Progress dialog (with ETA)
# ---------------------------------------------------------------------------
class ProgressDialog(CenteredDialog):
    def __init__(self, parent, total: int):
        super().__init__(parent)
        self.setWindowTitle("Creating Work Report")
        self.setModal(True)
        self.setMinimumWidth(460)
        self.setWindowFlag(Qt.WindowCloseButtonHint, False)

        self._start_time = time.monotonic()
        self._total = max(total, 1)

        root = QVBoxLayout(self)
        root.setContentsMargins(22, 22, 22, 22)
        root.setSpacing(12)

        title = QLabel("Compressing screenshots...")
        title.setStyleSheet("font-size: 15px; font-weight: bold;")
        root.addWidget(title)

        hint = QLabel(
            "Please wait while PNG files are converted to JPG and packed "
            "into a zip file."
        )
        hint.setWordWrap(True)
        hint.setObjectName("hintLabel")
        root.addWidget(hint)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, self._total)
        self.progress_bar.setValue(0)
        self.progress_bar.setMinimumHeight(22)
        root.addWidget(self.progress_bar)

        self.label = QLabel(f"0 / {total} files")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("font-weight: 600;")
        root.addWidget(self.label)

        self.eta_label = QLabel("⏱  Estimating...")
        self.eta_label.setAlignment(Qt.AlignCenter)
        self.eta_label.setObjectName("hintLabel")
        root.addWidget(self.eta_label)

    def update_progress(self, done: int, total: int) -> None:
        self.progress_bar.setRange(0, max(total, 1))
        self.progress_bar.setValue(done)
        self.label.setText(f"{done} / {total} files")

        if done <= 0 or total <= 0:
            self.eta_label.setText("⏱  Estimating...")
            return

        elapsed = time.monotonic() - self._start_time
        if done >= total:
            self.eta_label.setText(f"✅  Finished in {format_eta(elapsed).lstrip('~')}")
            return

        per_file = elapsed / done
        remaining = per_file * (total - done)
        if remaining < 0.5:
            self.eta_label.setText("⏱  Almost done...")
        else:
            self.eta_label.setText(f"⏱  {format_eta(remaining)} remaining")


# ---------------------------------------------------------------------------
# Screenshot preview dialog
# ---------------------------------------------------------------------------
class ScreenshotPreviewDialog(CenteredDialog):
    THUMB_W = 200
    THUMB_H = 140

    def __init__(self, parent, category_name: str, png_files: list[Path]):
        super().__init__(parent)
        self.category_name = category_name
        self.png_files = png_files
        self.setWindowTitle(f"Screenshots — {category_name}  ({len(png_files)} files)")
        self.setModal(True)
        self.resize(880, 620)

        root = QVBoxLayout(self)
        root.setContentsMargins(20, 20, 20, 20)
        root.setSpacing(12)

        header = QLabel(f"<b>{category_name}</b> — {len(png_files)} screenshot(s)")
        header.setStyleSheet("font-size: 15px;")
        root.addWidget(header)

        hint = QLabel("Double-click a thumbnail to open it in your default viewer.")
        hint.setObjectName("hintLabel")
        root.addWidget(hint)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        container = QWidget()
        grid = QGridLayout(container)
        grid.setContentsMargins(6, 6, 6, 6)
        grid.setSpacing(12)

        cols = 3
        for i, png in enumerate(png_files):
            grid.addWidget(self._make_thumbnail(png), i // cols, i % cols)

        grid.setRowStretch(grid.rowCount(), 1)
        scroll.setWidget(container)
        root.addWidget(scroll, 1)

        close_btn = QPushButton("Close")
        close_btn.setObjectName("secondaryButton")
        close_btn.setMinimumHeight(34)
        close_btn.setMinimumWidth(120)
        close_btn.clicked.connect(self.accept)
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_row.addWidget(close_btn)
        root.addLayout(btn_row)

    def _make_thumbnail(self, png_path: Path) -> QWidget:
        box = QFrame()
        box.setObjectName("card")
        box.setFixedSize(self.THUMB_W + 16, self.THUMB_H + 40)
        v = QVBoxLayout(box)
        v.setContentsMargins(6, 6, 6, 6)
        v.setSpacing(4)

        img_label = QLabel()
        img_label.setFixedSize(self.THUMB_W, self.THUMB_H)
        img_label.setAlignment(Qt.AlignCenter)
        img_label.setStyleSheet("background: rgba(0,0,0,0.05); border-radius: 4px;")

        pix = QPixmap(str(png_path))
        if not pix.isNull():
            img_label.setPixmap(pix.scaled(
                QSize(self.THUMB_W, self.THUMB_H),
                Qt.KeepAspectRatio, Qt.SmoothTransformation,
            ))
        else:
            img_label.setText("(cannot load)")

        v.addWidget(img_label)

        name_label = QLabel(png_path.name)
        name_label.setAlignment(Qt.AlignCenter)
        name_label.setObjectName("hintLabel")
        name_label.setStyleSheet("font-size: 11px;")
        name_label.setFixedHeight(18)
        v.addWidget(name_label)

        box.setCursor(Qt.PointingHandCursor)
        box.mouseDoubleClickEvent = lambda ev, p=png_path: self._open_file(p)
        img_label.mouseDoubleClickEvent = lambda ev, p=png_path: self._open_file(p)

        return box

    def _open_file(self, path: Path) -> None:
        try:
            os.startfile(str(path))
        except Exception as exc:
            QMessageBox.warning(
                self, "Cannot Open File",
                f"Failed to open:\n{path}\n\nError: {exc}"
            )


# ---------------------------------------------------------------------------
# Main Window
# ---------------------------------------------------------------------------
class MainWindow(QMainWindow):
    def __init__(self, mta_folder: str, game_name: str | None,
                 faction: str, rank: str | None, theme: str,
                 compression_kb: int = DEFAULT_COMPRESSION):
        super().__init__()
        self.mta_folder = mta_folder
        self.game_name = game_name or ""
        self.faction = faction
        self.rank = rank or DEFAULT_RANK
        self.theme = theme if theme in ("light", "dark") else DEFAULT_THEME
        self.compression_kb = compression_kb if compression_kb in COMPRESSION_LEVELS else DEFAULT_COMPRESSION

        self._convert_worker: ConvertWorker | None = None
        self._convert_dialog: ProgressDialog | None = None
        self._update_checker: UpdateChecker | None = None
        self._last_results: list | None = None
        self._initial_centering_done = False

        self.setWindowTitle(APP_TITLE)
        self.setMinimumSize(1020, 900)
        self.resize(1100, 940)

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.home_page = self._create_home_page()
        self.tools_page = self._create_tools_page()
        self.report_page = self._create_report_page()
        self.stats_page = self._create_stats_page()
        self.fine_calc_page = self._create_fine_calc_page()
        self.settings_page = self._create_settings_page()

        self.stack.addWidget(self.home_page)
        self.stack.addWidget(self.tools_page)
        self.stack.addWidget(self.report_page)
        self.stack.addWidget(self.stats_page)
        self.stack.addWidget(self.fine_calc_page)
        self.stack.addWidget(self.settings_page)

        self._build_menu()
        self._apply_style()
        self._refresh_labels()
        self._update_theme_button_text()

    # ---------------- Window centering ----------------
    def showEvent(self, event):
        super().showEvent(event)
        if not self._initial_centering_done:
            self._initial_centering_done = True
            QTimer.singleShot(0, self._center_on_screen)

    def _center_on_screen(self) -> None:
        screen = QApplication.screenAt(QCursor.pos()) or QApplication.primaryScreen()
        if screen is None:
            return
        geo = screen.availableGeometry()
        w = min(self.width(), geo.width() - 40)
        h = min(self.height(), geo.height() - 40)
        self.resize(w, h)
        rect = self.frameGeometry()
        rect.moveCenter(geo.center())
        self.move(rect.topLeft())

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

        act_missing = QAction("Create Missing Category Folders", self)
        act_missing.triggered.connect(self.create_category_folders)
        tools_menu.addAction(act_missing)

        self.act_fine = QAction("🚔 Calculate Fine", self)
        self.act_fine.triggered.connect(self.open_fine_calculator)
        tools_menu.addAction(self.act_fine)

        tools_menu.addSeparator()

        act_stats = QAction("📊 Faction Stats Dashboard", self)
        act_stats.triggered.connect(self.open_stats)
        tools_menu.addAction(act_stats)

        tools_menu.addSeparator()

        act_export_csv = QAction("Export Report to CSV...", self)
        act_export_csv.triggered.connect(self.export_csv)
        tools_menu.addAction(act_export_csv)

        act_export_pdf = QAction("Export Report to PDF...", self)
        act_export_pdf.triggered.connect(self.export_pdf)
        tools_menu.addAction(act_export_pdf)

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

        settings_menu.addSeparator()

        self.act_theme = QAction("Toggle Dark Mode", self)
        self.act_theme.triggered.connect(self.toggle_theme)
        settings_menu.addAction(self.act_theme)

        help_menu = menubar.addMenu("Help")
        act_check_updates = QAction("Check for Updates...", self)
        act_check_updates.triggered.connect(self.check_for_updates_manual)
        help_menu.addAction(act_check_updates)

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
        title.setStyleSheet("font-size: 32px; font-weight: bold;")
        layout.addWidget(title)

        subtitle = QLabel(f"Version {APP_VERSION}   •   Made By {APP_AUTHOR}")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setObjectName("hintLabel")
        subtitle.setStyleSheet("font-size: 13px;")
        layout.addWidget(subtitle)

        layout.addSpacing(16)

        def make_card(title_text):
            box = QFrame()
            box.setObjectName("card")
            v = QVBoxLayout(box)
            v.setContentsMargins(18, 14, 18, 14)
            v.setSpacing(4)
            t = QLabel(title_text)
            t.setStyleSheet("font-weight: bold; font-size: 12px;")
            val = QLabel()
            val.setWordWrap(True)
            val.setStyleSheet("font-size: 13px;")
            v.addWidget(t)
            v.addWidget(val)
            return box, val

        self.home_folder_card, self.home_folder_label = make_card("Current MTA:SA Folder")
        layout.addWidget(self.home_folder_card)

        self.home_faction_card, self.home_faction_label = make_card("Current Faction")
        layout.addWidget(self.home_faction_card)

        self.home_rank_card, self.home_rank_label = make_card("Current Rank")
        layout.addWidget(self.home_rank_card)

        self.home_name_card, self.home_name_label = make_card("Current Game Name")
        layout.addWidget(self.home_name_card)

        layout.addSpacing(16)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(16)

        tools_btn = QPushButton("🛠  Tools")
        tools_btn.setMinimumHeight(90)
        tools_btn.setStyleSheet("font-size: 16px; font-weight: bold;")
        tools_btn.clicked.connect(lambda: self.stack.setCurrentWidget(self.tools_page))

        stats_btn = QPushButton("📊  Stats")
        stats_btn.setMinimumHeight(90)
        stats_btn.setStyleSheet("font-size: 16px; font-weight: bold;")
        stats_btn.clicked.connect(self.open_stats)

        settings_btn = QPushButton("⚙  Settings")
        settings_btn.setMinimumHeight(90)
        settings_btn.setStyleSheet("font-size: 16px; font-weight: bold;")
        settings_btn.clicked.connect(lambda: self.stack.setCurrentWidget(self.settings_page))

        btn_row.addWidget(tools_btn)
        btn_row.addWidget(stats_btn)
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
        back.clicked.connect(lambda: self.stack.setCurrentWidget(self.home_page))
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
        self.calc_desc.setObjectName("hintLabel")
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
            "Converts every PNG screenshot into a compressed JPG, places "
            "them in a Desktop folder named after your in-game name, and "
            "compresses it into a .zip file. A preview dialog shows the "
            "details before starting."
        )
        d2.setWordWrap(True)
        d2.setObjectName("hintLabel")
        info2.addWidget(t2)
        info2.addWidget(d2)
        c2.addLayout(info2, 1)
        create_btn = QPushButton("Create Work Report")
        create_btn.setMinimumHeight(44)
        create_btn.setMinimumWidth(210)
        create_btn.clicked.connect(self.create_report_folder)
        c2.addWidget(create_btn, 0, Qt.AlignVCenter)
        layout.addWidget(card2)

        # Card 3 — Missing folders
        card3 = QFrame()
        card3.setObjectName("card")
        c3 = QHBoxLayout(card3)
        c3.setContentsMargins(22, 22, 22, 22)
        c3.setSpacing(20)
        info3 = QVBoxLayout()
        info3.setSpacing(6)
        t3 = QLabel("Create Missing Category Folders")
        t3.setStyleSheet("font-size: 16px; font-weight: bold;")
        d3 = QLabel(
            "Automatically creates any missing category folders for your "
            "current faction inside the screenshots directory."
        )
        d3.setWordWrap(True)
        d3.setObjectName("hintLabel")
        info3.addWidget(t3)
        info3.addWidget(d3)
        c3.addLayout(info3, 1)
        folders_btn = QPushButton("Create Folders")
        folders_btn.setMinimumHeight(44)
        folders_btn.setMinimumWidth(210)
        folders_btn.clicked.connect(self.create_category_folders)
        c3.addWidget(folders_btn, 0, Qt.AlignVCenter)
        layout.addWidget(card3)

        # Card 4 — Fine Calculator (Police Department only)
        self.fine_card = QFrame()
        self.fine_card.setObjectName("card")
        fc = QHBoxLayout(self.fine_card)
        fc.setContentsMargins(22, 22, 22, 22)
        fc.setSpacing(20)

        fine_info = QVBoxLayout()
        fine_info.setSpacing(6)
        fine_title = QLabel("🚔  Calculate Fine")
        fine_title.setStyleSheet("font-size: 16px; font-weight: bold;")
        fine_desc = QLabel(
            "Calculate the speed violation fine for a player. "
            "Choose a location, enter the driver's speed, and get the "
            "total fine based on the standard formula."
        )
        fine_desc.setWordWrap(True)
        fine_desc.setObjectName("hintLabel")
        fine_info.addWidget(fine_title)
        fine_info.addWidget(fine_desc)
        fc.addLayout(fine_info, 1)

        fine_btn = QPushButton("Open Fine Calculator")
        fine_btn.setMinimumHeight(44)
        fine_btn.setMinimumWidth(210)
        fine_btn.clicked.connect(self.open_fine_calculator)
        fc.addWidget(fine_btn, 0, Qt.AlignVCenter)

        layout.addWidget(self.fine_card)

        # Card 5 — Clear (danger)
        card5 = QFrame()
        card5.setObjectName("card")
        c5 = QHBoxLayout(card5)
        c5.setContentsMargins(22, 22, 22, 22)
        c5.setSpacing(20)
        info5 = QVBoxLayout()
        info5.setSpacing(6)
        t5 = QLabel("Clear Work Reports")
        t5.setStyleSheet("font-size: 16px; font-weight: bold; color: #c0392b;")
        d5 = QLabel(
            "Permanently deletes all files inside the category folders. "
            "Folder structure is preserved. This action cannot be undone."
        )
        d5.setWordWrap(True)
        d5.setObjectName("hintLabel")
        info5.addWidget(t5)
        info5.addWidget(d5)
        c5.addLayout(info5, 1)
        clear_btn = QPushButton("Clear Work Reports")
        clear_btn.setObjectName("dangerButton")
        clear_btn.setMinimumHeight(44)
        clear_btn.setMinimumWidth(210)
        clear_btn.clicked.connect(self.clear_reports)
        c5.addWidget(clear_btn, 0, Qt.AlignVCenter)
        layout.addWidget(card5)

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
        back.clicked.connect(lambda: self.stack.setCurrentWidget(self.tools_page))
        header.addWidget(back)
        header.addStretch()

        self.btn_export_csv = QPushButton("Export CSV")
        self.btn_export_csv.setObjectName("secondaryButton")
        self.btn_export_csv.setMinimumHeight(32)
        self.btn_export_csv.clicked.connect(self.export_csv)
        header.addWidget(self.btn_export_csv)

        self.btn_export_pdf = QPushButton("Export PDF")
        self.btn_export_pdf.setObjectName("secondaryButton")
        self.btn_export_pdf.setMinimumHeight(32)
        self.btn_export_pdf.clicked.connect(self.export_pdf)
        header.addWidget(self.btn_export_pdf)

        refresh_btn = QPushButton("Recalculate")
        refresh_btn.setMinimumHeight(32)
        refresh_btn.clicked.connect(self.run_report)
        header.addWidget(refresh_btn)
        layout.addLayout(header)

        title = QLabel("Work Report")
        title.setStyleSheet("font-size: 22px; font-weight: bold;")
        layout.addWidget(title)

        self.report_info = QLabel()
        self.report_info.setObjectName("hintLabel")
        self.report_info.setWordWrap(True)
        layout.addWidget(self.report_info)

        preview_hint = QLabel("💡 Double-click a row to preview its screenshots.")
        preview_hint.setObjectName("hintLabel")
        preview_hint.setStyleSheet("font-size: 12px;")
        layout.addWidget(preview_hint)

        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(
            ["Folder", "Screenshots", "Unit Price", "Total"]
        )
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        self.table.verticalHeader().setDefaultSectionSize(36)
        self.table.cellDoubleClicked.connect(self._on_row_double_clicked)
        layout.addWidget(self.table, 1)

        self.summary_label = QLabel()
        self.summary_label.setObjectName("summaryLabel")
        self.summary_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        layout.addWidget(self.summary_label)

        return page

    def _create_stats_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 24, 30, 30)
        layout.setSpacing(14)

        header = QHBoxLayout()
        back = QPushButton("←  Back")
        back.setObjectName("backButton")
        back.clicked.connect(lambda: self.stack.setCurrentWidget(self.home_page))
        header.addWidget(back)
        header.addStretch()

        refresh_btn = QPushButton("Refresh")
        refresh_btn.setMinimumHeight(32)
        refresh_btn.clicked.connect(self.refresh_stats)
        header.addWidget(refresh_btn)
        layout.addLayout(header)

        title = QLabel("📊  Faction Stats Dashboard")
        title.setStyleSheet("font-size: 22px; font-weight: bold;")
        layout.addWidget(title)

        self.stats_info = QLabel()
        self.stats_info.setObjectName("hintLabel")
        self.stats_info.setWordWrap(True)
        layout.addWidget(self.stats_info)

        cards_row = QHBoxLayout()
        cards_row.setSpacing(12)

        self.stat_files_card, self.stat_files_value = self._make_stat_card(
            "📸  Total Screenshots", "0"
        )
        self.stat_amount_card, self.stat_amount_value = self._make_stat_card(
            "💰  Total Amount", "$0"
        )
        self.stat_active_card, self.stat_active_value = self._make_stat_card(
            "📁  Active Categories", "0"
        )
        self.stat_top_card, self.stat_top_value = self._make_stat_card(
            "🏆  Top Category", "—"
        )

        cards_row.addWidget(self.stat_files_card)
        cards_row.addWidget(self.stat_amount_card)
        cards_row.addWidget(self.stat_active_card)
        cards_row.addWidget(self.stat_top_card)
        layout.addLayout(cards_row)

        breakdown_title = QLabel("Category Breakdown")
        breakdown_title.setStyleSheet("font-size: 16px; font-weight: bold; margin-top: 6px;")
        layout.addWidget(breakdown_title)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.breakdown_container = QWidget()
        self.breakdown_layout = QVBoxLayout(self.breakdown_container)
        self.breakdown_layout.setContentsMargins(0, 0, 0, 0)
        self.breakdown_layout.setSpacing(8)
        scroll.setWidget(self.breakdown_container)
        layout.addWidget(scroll, 1)

        return page

    def _make_stat_card(self, title: str, initial_value: str):
        card = QFrame()
        card.setObjectName("card")
        card.setMinimumHeight(110)
        v = QVBoxLayout(card)
        v.setContentsMargins(18, 14, 18, 14)
        v.setSpacing(6)

        t = QLabel(title)
        t.setObjectName("hintLabel")
        t.setStyleSheet("font-size: 12px; font-weight: 600;")
        v.addWidget(t)

        val = QLabel(initial_value)
        val.setStyleSheet("font-size: 22px; font-weight: bold;")
        val.setWordWrap(True)
        v.addWidget(val)

        return card, val

    def _create_fine_calc_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 24, 30, 30)
        layout.setSpacing(16)

        # Header
        header = QHBoxLayout()
        back = QPushButton("←  Back")
        back.setObjectName("backButton")
        back.clicked.connect(lambda: self.stack.setCurrentWidget(self.tools_page))
        header.addWidget(back)
        header.addStretch()
        layout.addLayout(header)

        title = QLabel("🚔  Fine Calculator")
        title.setStyleSheet("font-size: 22px; font-weight: bold;")
        layout.addWidget(title)

        info = QLabel(
            "Calculate the speed violation fine for a player. "
            "Formula: $5,000 base + $2,000 for every 20 KM/H over the limit."
        )
        info.setWordWrap(True)
        info.setObjectName("hintLabel")
        layout.addWidget(info)

        # Scrollable content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        content = QWidget()
        cv = QVBoxLayout(content)
        cv.setContentsMargins(0, 0, 0, 0)
        cv.setSpacing(14)

        # --- Location card ---
        loc_card = QFrame()
        loc_card.setObjectName("card")
        lcv = QVBoxLayout(loc_card)
        lcv.setContentsMargins(22, 22, 22, 22)
        lcv.setSpacing(10)

        loc_title = QLabel("1.  Location")
        loc_title.setStyleSheet("font-size: 15px; font-weight: bold;")
        lcv.addWidget(loc_title)

        loc_hint = QLabel("Pick the area where the violation happened.")
        loc_hint.setObjectName("hintLabel")
        loc_hint.setStyleSheet("font-size: 12px;")
        lcv.addWidget(loc_hint)

        self.fine_location_group = QButtonGroup(self)
        self.fine_location_radios: dict[str, QRadioButton] = {}
        first_key = FINE_LOCATIONS[0][0]

        for name, limit, desc in FINE_LOCATIONS:
            rb = QRadioButton(f"{name}   —   {limit} KM/H")
            rb.setMinimumHeight(36)
            rb.setStyleSheet("QRadioButton { padding: 8px 12px; font-size: 14px; }")
            rb.setChecked(name == first_key)
            rb.toggled.connect(self._on_fine_input_changed)
            self.fine_location_group.addButton(rb)
            self.fine_location_radios[name] = rb
            lcv.addWidget(rb)

            desc_lbl = QLabel(f"     {desc}")
            desc_lbl.setObjectName("hintLabel")
            desc_lbl.setStyleSheet("font-size: 11px; margin-left: 26px;")
            lcv.addWidget(desc_lbl)

        cv.addWidget(loc_card)

        # --- Speed card ---
        speed_card = QFrame()
        speed_card.setObjectName("card")
        scv = QVBoxLayout(speed_card)
        scv.setContentsMargins(22, 22, 22, 22)
        scv.setSpacing(10)

        speed_title = QLabel("2.  Driver's Speed")
        speed_title.setStyleSheet("font-size: 15px; font-weight: bold;")
        scv.addWidget(speed_title)

        speed_hint = QLabel("Enter the speed recorded by the camera (KM/H).")
        speed_hint.setObjectName("hintLabel")
        speed_hint.setStyleSheet("font-size: 12px;")
        scv.addWidget(speed_hint)

        speed_row = QHBoxLayout()
        self.fine_speed_edit = QLineEdit()
        self.fine_speed_edit.setPlaceholderText("e.g. 140")
        self.fine_speed_edit.setMinimumHeight(38)
        self.fine_speed_edit.setMaximumWidth(220)
        validator = QIntValidator(0, 999, self)
        self.fine_speed_edit.setValidator(validator)
        self.fine_speed_edit.textChanged.connect(self._on_fine_input_changed)
        speed_row.addWidget(self.fine_speed_edit)
        unit_lbl = QLabel("KM/H")
        unit_lbl.setStyleSheet("font-weight: bold;")
        speed_row.addWidget(unit_lbl)
        speed_row.addStretch()
        scv.addLayout(speed_row)

        cv.addWidget(speed_card)

        # --- Action buttons ---
        action_row = QHBoxLayout()
        action_row.setSpacing(10)

        calc_btn = QPushButton("Calculate Fine")
        calc_btn.setMinimumHeight(44)
        calc_btn.setMinimumWidth(180)
        calc_btn.clicked.connect(self._on_fine_calculate)
        action_row.addWidget(calc_btn)

        reset_btn = QPushButton("Reset")
        reset_btn.setObjectName("secondaryButton")
        reset_btn.setMinimumHeight(44)
        reset_btn.setMinimumWidth(120)
        reset_btn.clicked.connect(self._on_fine_reset)
        action_row.addWidget(reset_btn)

        action_row.addStretch()
        cv.addLayout(action_row)

        # --- Result card ---
        self.fine_result_card = QFrame()
        self.fine_result_card.setObjectName("card")
        self.fine_result_card.setVisible(False)
        rcv = QVBoxLayout(self.fine_result_card)
        rcv.setContentsMargins(22, 20, 22, 20)
        rcv.setSpacing(8)

        self.fine_result_title = QLabel("Result")
        self.fine_result_title.setStyleSheet("font-size: 15px; font-weight: bold;")
        rcv.addWidget(self.fine_result_title)

        self.fine_result_details = QLabel()
        self.fine_result_details.setWordWrap(True)
        self.fine_result_details.setStyleSheet("font-size: 13px;")
        rcv.addWidget(self.fine_result_details)

        self.fine_result_total = QLabel()
        self.fine_result_total.setStyleSheet(
            "font-size: 24px; font-weight: bold; padding: 12px 0;"
        )
        rcv.addWidget(self.fine_result_total)

        cv.addWidget(self.fine_result_card)

        cv.addStretch()
        scroll.setWidget(content)
        layout.addWidget(scroll, 1)

        return page

    def _create_settings_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 24, 30, 30)
        layout.setSpacing(14)

        header = QHBoxLayout()
        back = QPushButton("←  Back")
        back.setObjectName("backButton")
        back.clicked.connect(lambda: self.stack.setCurrentWidget(self.home_page))
        header.addWidget(back)
        header.addStretch()
        layout.addLayout(header)

        title = QLabel("Settings")
        title.setStyleSheet("font-size: 22px; font-weight: bold;")
        layout.addWidget(title)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        container = QWidget()
        v = QVBoxLayout(container)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(14)

        def make_setting_card(label_text, button_text, slot):
            card = QFrame()
            card.setObjectName("card")
            cv = QVBoxLayout(card)
            cv.setContentsMargins(22, 22, 22, 22)
            cv.setSpacing(12)
            lbl = QLabel(label_text)
            lbl.setStyleSheet("font-weight: bold;")
            cv.addWidget(lbl)
            val = QLabel()
            val.setWordWrap(True)
            val.setStyleSheet(
                "background: rgba(0,0,0,0.04); padding:12px;"
                "border-radius:6px; border: 1px solid rgba(0,0,0,0.08);"
            )
            cv.addWidget(val)
            btn = QPushButton(button_text)
            btn.setMinimumHeight(38)
            btn.setMinimumWidth(180)
            btn.clicked.connect(slot)
            cv.addWidget(btn, 0, Qt.AlignLeft)
            return card, val, btn

        self.settings_folder_card, self.settings_folder_label, _ = make_setting_card(
            "MTA:SA Folder", "Change Folder...", self.change_folder
        )
        v.addWidget(self.settings_folder_card)

        self.settings_faction_card, self.settings_faction_label, _ = make_setting_card(
            "Faction", "Change Faction...", self.change_faction
        )
        v.addWidget(self.settings_faction_card)

        self.settings_rank_card, self.settings_rank_label, _ = make_setting_card(
            "Rank", "Change Rank...", self.change_rank
        )
        v.addWidget(self.settings_rank_card)

        self.settings_name_card, self.settings_name_label, _ = make_setting_card(
            "Game Name", "Change Game Name...", self.change_name
        )
        v.addWidget(self.settings_name_card)

        comp_card = QFrame()
        comp_card.setObjectName("card")
        ccv = QVBoxLayout(comp_card)
        ccv.setContentsMargins(22, 22, 22, 22)
        ccv.setSpacing(10)

        comp_lbl = QLabel("Compression Level")
        comp_lbl.setStyleSheet("font-weight: bold;")
        ccv.addWidget(comp_lbl)

        comp_hint = QLabel(
            "Maximum size of each JPG after conversion. Lower values save "
            "space but reduce image quality."
        )
        comp_hint.setWordWrap(True)
        comp_hint.setObjectName("hintLabel")
        comp_hint.setStyleSheet("font-size: 12px;")
        ccv.addWidget(comp_hint)

        self.compression_group = QButtonGroup(self)
        self.compression_radios: dict[int, QRadioButton] = {}
        for kb in COMPRESSION_LEVELS:
            label = f"{kb} KB per image"
            if kb == DEFAULT_COMPRESSION:
                label += "  (default)"
            rb = QRadioButton(label)
            rb.setMinimumHeight(32)
            rb.setChecked(kb == self.compression_kb)
            rb.toggled.connect(
                lambda checked, k=kb: self._on_compression_changed(k) if checked else None
            )
            self.compression_group.addButton(rb)
            self.compression_radios[kb] = rb
            ccv.addWidget(rb)

        v.addWidget(comp_card)

        self.settings_theme_card, self.settings_theme_label, self.settings_theme_btn = make_setting_card(
            "Appearance", "Switch Theme", self.toggle_theme
        )
        v.addWidget(self.settings_theme_card)

        v.addStretch()
        scroll.setWidget(container)
        layout.addWidget(scroll, 1)

        return page

    # ---------------- Logic ----------------
    def _refresh_labels(self) -> None:
        self.home_folder_label.setText(self.mta_folder)
        self.settings_folder_label.setText(self.mta_folder)

        self.home_faction_label.setText(self.faction)
        self.settings_faction_label.setText(self.faction)

        is_ranked = faction_requires_rank(self.faction)
        coming_soon = is_coming_soon(self.faction)

        self.home_rank_card.setVisible(is_ranked)
        self.settings_rank_card.setVisible(is_ranked)
        self.act_rank.setEnabled(is_ranked)

        if is_ranked:
            self.home_rank_label.setText(self.rank)
            self.settings_rank_label.setText(self.rank)

        name_display = self.game_name if self.game_name else "(not set yet)"
        self.home_name_label.setText(name_display)
        self.settings_name_label.setText(name_display)

        theme_display = "Dark" if self.theme == "dark" else "Light"
        self.settings_theme_label.setText(f"Current theme: {theme_display}")

        if coming_soon:
            folder_names = [name for name, _ in COMING_SOON_FACTIONS[self.faction]]
            self.calc_desc.setText(
                f"Faction: {self.faction}\n"
                f"Supported folders: {' • '.join(folder_names)}\n\n"
                f"⚠  Prices for this faction have not been announced yet. "
                f"This feature will be added in a future update."
            )
            self._refresh_fine_visibility()
            return

        prices = get_prices(self.faction, self.rank)
        parts = [f"{name} ${price:,}" for name, _, price in prices]

        header = f"Faction: {self.faction}"
        if is_ranked:
            header += f" ({self.rank})"

        self.calc_desc.setText(
            f"{header} — counts PNG screenshots and applies the following "
            f"prices:\n" + "  •  ".join(parts)
        )

        self._refresh_fine_visibility()

    def _faction_display(self) -> str:
        if faction_requires_rank(self.faction):
            return f"{self.faction} ({self.rank})"
        return self.faction

    def run_report(self) -> None:
        if is_coming_soon(self.faction):
            QMessageBox.information(
                self, "Coming Soon",
                f"Prices for '{self.faction}' have not been announced yet.\n\n"
                "This feature will be added in a future update.\n\n"
                "You can change your faction anytime from Settings."
            )
            return

        results, error = calculate_report(self.mta_folder, self.faction, self.rank)
        if error:
            QMessageBox.warning(self, "Report Error", error)
            return

        self._last_results = results
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
        self.report_info.setText(
            f"Faction: {self._faction_display()}      |      "
            f"Screenshots directory:  {screenshots_dir}"
        )
        self.summary_label.setText(
            f"Total Screenshots: {total_count:,}      |      "
            f"Total Amount: ${total_amount:,}"
        )

    def _on_row_double_clicked(self, row: int, col: int) -> None:
        item = self.table.item(row, 0)
        if item is None:
            return
        display_name = item.text()

        key = None
        for name, k, _ in get_prices(self.faction, self.rank):
            if name == display_name:
                key = k
                break
        if key is None:
            for cn, k in COMING_SOON_FACTIONS.get(self.faction, []):
                if cn == display_name:
                    key = k
                    break
        if key is None:
            return

        pngs = _list_pngs_for_category(self.mta_folder, key)
        if not pngs:
            QMessageBox.information(
                self, "No Screenshots",
                f"No PNG screenshots were found for '{display_name}'."
            )
            return

        ScreenshotPreviewDialog(self, display_name, pngs).exec()

    # ---------------- Fine Calculator ----------------
    def _get_selected_fine_location(self):
        for name, limit, _ in FINE_LOCATIONS:
            rb = self.fine_location_radios.get(name)
            if rb is not None and rb.isChecked():
                return name, limit
        return FINE_LOCATIONS[0][0], FINE_LOCATIONS[0][1]

    def _on_fine_input_changed(self, *args) -> None:
        if hasattr(self, "fine_result_card"):
            self.fine_result_card.setVisible(False)

    def _on_fine_reset(self) -> None:
        if hasattr(self, "fine_speed_edit"):
            self.fine_speed_edit.clear()
        first_name = FINE_LOCATIONS[0][0]
        rb = self.fine_location_radios.get(first_name)
        if rb is not None:
            rb.setChecked(True)
        if hasattr(self, "fine_result_card"):
            self.fine_result_card.setVisible(False)

    def _on_fine_calculate(self) -> None:
        name, limit = self._get_selected_fine_location()

        text = self.fine_speed_edit.text().strip()
        if not text:
            QMessageBox.warning(
                self, "Missing Speed",
                "Please enter the driver's speed in KM/H."
            )
            return

        try:
            speed = int(text)
        except ValueError:
            QMessageBox.warning(
                self, "Invalid Speed",
                "Please enter a valid number for the speed."
            )
            return

        if speed < 0 or speed > 999:
            QMessageBox.warning(
                self, "Invalid Speed",
                "Speed must be between 0 and 999 KM/H."
            )
            return

        result = calculate_fine(limit, speed)

        if result is None:
            self.fine_result_title.setText(f"Result — {name}")
            self.fine_result_details.setText(
                f"Speed limit:     <b>{limit} KM/H</b><br>"
                f"Driver's speed:  <b>{speed} KM/H</b><br><br>"
                f"No speed violation detected."
            )
            self.fine_result_total.setText("✅  No Fine")
            self.fine_result_total.setStyleSheet(
                "font-size: 24px; font-weight: bold; padding: 12px 0;"
                "color: #27ae60;"
            )
        else:
            self.fine_result_title.setText(f"Result — {name}")
            self.fine_result_details.setText(
                f"Speed limit:     <b>{result['limit']} KM/H</b><br>"
                f"Driver's speed:  <b>{result['speed']} KM/H</b><br>"
                f"Excess:          <b>{result['excess']} KM/H</b><br><br>"
                f"Base fine:       <b>${result['base']:,}</b><br>"
                f"Additional:      <b>{result['steps']} × ${FINE_STEP:,} = "
                f"${result['extra']:,}</b>"
            )
            self.fine_result_total.setText(f"💰  Total Fine:  ${result['total']:,}")
            self.fine_result_total.setStyleSheet(
                "font-size: 24px; font-weight: bold; padding: 12px 0;"
                "color: #e74c3c;"
            )

        self.fine_result_card.setVisible(True)

    def open_fine_calculator(self) -> None:
        if self.faction != PD_FACTION_NAME:
            QMessageBox.information(
                self, "Police Department Only",
                "The Fine Calculator is only available for the "
                "Police Department faction."
            )
            return
        self._on_fine_reset()
        self.stack.setCurrentWidget(self.fine_calc_page)

    def _refresh_fine_visibility(self) -> None:
        is_pd = (self.faction == PD_FACTION_NAME)
        if hasattr(self, "fine_card"):
            self.fine_card.setVisible(is_pd)
        if hasattr(self, "act_fine"):
            self.act_fine.setEnabled(is_pd)

    # ---------------- Stats Dashboard ----------------
    def open_stats(self) -> None:
        self.stack.setCurrentWidget(self.stats_page)
        self.refresh_stats()

    def refresh_stats(self) -> None:
        while self.breakdown_layout.count():
            item = self.breakdown_layout.takeAt(0)
            w = item.widget()
            if w is not None:
                w.deleteLater()

        if is_coming_soon(self.faction):
            self.stats_info.setText(
                f"Faction: {self.faction} — Prices not yet announced."
            )
            self.stat_files_value.setText("—")
            self.stat_amount_value.setText("—")
            self.stat_active_value.setText("—")
            self.stat_top_value.setText("—")
            empty = QLabel("Stats are not available for coming-soon factions.")
            empty.setObjectName("hintLabel")
            empty.setAlignment(Qt.AlignCenter)
            empty.setStyleSheet("padding: 30px;")
            self.breakdown_layout.addWidget(empty)
            self.breakdown_layout.addStretch()
            return

        results, error = calculate_report(self.mta_folder, self.faction, self.rank)
        if error:
            self.stats_info.setText(error)
            self.stat_files_value.setText("—")
            self.stat_amount_value.setText("—")
            self.stat_active_value.setText("—")
            self.stat_top_value.setText("—")
            empty = QLabel("Could not read screenshots folder.")
            empty.setObjectName("hintLabel")
            empty.setAlignment(Qt.AlignCenter)
            empty.setStyleSheet("padding: 30px;")
            self.breakdown_layout.addWidget(empty)
            self.breakdown_layout.addStretch()
            return

        total_files = sum(r[1] for r in results)
        total_amount = sum(r[3] for r in results)
        active = [r for r in results if r[1] > 0]
        top_name = "—"
        if active:
            top = max(active, key=lambda r: r[1])
            top_name = top[0]

        self.stat_files_value.setText(f"{total_files:,}")
        self.stat_amount_value.setText(f"${total_amount:,}")
        self.stat_active_value.setText(str(len(active)))
        self.stat_top_value.setText(top_name)

        self.stats_info.setText(
            f"Faction: {self._faction_display()}      |      "
            f"Screenshots directory:  {Path(self.mta_folder) / 'screenshots'}"
        )

        max_count = max((r[1] for r in results), default=0)
        if max_count == 0:
            empty = QLabel("No screenshots found for this faction.")
            empty.setObjectName("hintLabel")
            empty.setAlignment(Qt.AlignCenter)
            empty.setStyleSheet("padding: 30px;")
            self.breakdown_layout.addWidget(empty)
            self.breakdown_layout.addStretch()
            return

        for i, (name, count, price, subtotal) in enumerate(results):
            color = STAT_BAR_PALETTE[i % len(STAT_BAR_PALETTE)]
            row = QFrame()
            row.setObjectName("card")
            h = QHBoxLayout(row)
            h.setContentsMargins(14, 10, 14, 10)
            h.setSpacing(12)

            name_lbl = QLabel(name)
            name_lbl.setMinimumWidth(110)
            name_lbl.setStyleSheet("font-weight: bold;")
            h.addWidget(name_lbl)

            bar = QProgressBar()
            bar.setRange(0, max_count)
            bar.setValue(count)
            bar.setTextVisible(False)
            bar.setMinimumHeight(20)
            bar.setStyleSheet(f"""
                QProgressBar {{
                    background: rgba(128,128,128,0.18);
                    border: none;
                    border-radius: 10px;
                }}
                QProgressBar::chunk {{
                    background: {color};
                    border-radius: 10px;
                }}
            """)
            h.addWidget(bar, 1)

            count_lbl = QLabel(f"{count:,}")
            count_lbl.setMinimumWidth(60)
            count_lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            count_lbl.setStyleSheet("font-weight: 600;")
            h.addWidget(count_lbl)

            amount_lbl = QLabel(f"${subtotal:,}")
            amount_lbl.setMinimumWidth(110)
            amount_lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            amount_lbl.setStyleSheet("font-weight: 600;")
            h.addWidget(amount_lbl)

            self.breakdown_layout.addWidget(row)

        self.breakdown_layout.addStretch()

    # ---------------- Export ----------------
    def _ensure_report(self) -> bool:
        if not self._last_results:
            QMessageBox.information(
                self, "No Report",
                "Please calculate the work report first."
            )
            return False
        return True

    def export_csv(self) -> None:
        if not self._ensure_report():
            return

        default_name = f"MTA_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        path, _ = QFileDialog.getSaveFileName(
            self, "Save CSV Report",
            str(Path.home() / "Desktop" / default_name),
            "CSV Files (*.csv)"
        )
        if not path:
            return

        results = self._last_results
        total_count = sum(r[1] for r in results)
        total_amount = sum(r[3] for r in results)

        try:
            export_report_csv(path, self._faction_display(), results,
                              total_count, total_amount)
        except Exception as exc:
            QMessageBox.critical(self, "Export Error", f"Failed to export CSV:\n{exc}")
            return

        QMessageBox.information(self, "Export Successful",
                                f"CSV report saved to:\n{path}")

    def export_pdf(self) -> None:
        if not self._ensure_report():
            return

        default_name = f"MTA_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        path, _ = QFileDialog.getSaveFileName(
            self, "Save PDF Report",
            str(Path.home() / "Desktop" / default_name),
            "PDF Files (*.pdf)"
        )
        if not path:
            return

        results = self._last_results
        total_count = sum(r[1] for r in results)
        total_amount = sum(r[3] for r in results)

        try:
            export_report_pdf(path, self._faction_display(),
                              self.game_name or "(not set)",
                              results, total_count, total_amount)
        except Exception as exc:
            QMessageBox.critical(self, "Export Error", f"Failed to export PDF:\n{exc}")
            return

        QMessageBox.information(self, "Export Successful",
                                f"PDF report saved to:\n{path}")

    # ---------------- Auto-Update ----------------
    def check_for_updates_manual(self) -> None:
        checker = UpdateChecker(APP_VERSION, self)
        self._update_checker = checker

        def on_available(latest, dl_url, rel_url):
            dlg = UpdateDialog(self, latest, dl_url, rel_url)
            dlg.exec()
            if dlg.skip_version:
                try:
                    save_skipped_version(latest)
                except OSError:
                    pass

        def on_no_update():
            QMessageBox.information(
                self, "No Updates",
                f"You're already using the latest version (v{APP_VERSION})."
            )

        def on_failed(msg):
            QMessageBox.warning(
                self, "Update Check Failed",
                "Could not check for updates. Please check your internet "
                f"connection.\n\nDetails:\n{msg}"
            )

        checker.update_available.connect(on_available)
        checker.no_update.connect(on_no_update)
        checker.check_failed.connect(on_failed)
        checker.start()

    def check_for_updates_silent(self) -> None:
        skipped = get_skipped_version()
        checker = UpdateChecker(APP_VERSION, self)
        self._update_checker = checker

        def on_available(latest, dl_url, rel_url):
            if skipped and not is_newer_version(latest, skipped):
                return
            dlg = UpdateDialog(self, latest, dl_url, rel_url)
            dlg.exec()
            if dlg.skip_version:
                try:
                    save_skipped_version(latest)
                except OSError:
                    pass

        def on_no_update():
            pass

        def on_failed(msg):
            print(f"[AutoUpdate] Check failed: {msg}")

        checker.update_available.connect(on_available)
        checker.no_update.connect(on_no_update)
        checker.check_failed.connect(on_failed)
        checker.start()

    # ---------------- Theme ----------------
    def _update_theme_button_text(self) -> None:
        if self.theme == "dark":
            self.act_theme.setText("Switch to Light Mode")
            if hasattr(self, "settings_theme_btn"):
                self.settings_theme_btn.setText("Switch to Light Mode")
        else:
            self.act_theme.setText("Switch to Dark Mode")
            if hasattr(self, "settings_theme_btn"):
                self.settings_theme_btn.setText("Switch to Dark Mode")

    def toggle_theme(self) -> None:
        self.theme = "dark" if self.theme == "light" else "light"
        try:
            save_theme(self.theme)
        except OSError:
            pass
        self._apply_style()
        self._refresh_labels()
        self._update_theme_button_text()
        self.refresh_stats()

    def _apply_style(self) -> None:
        self.setStyleSheet(QSS_DARK if self.theme == "dark" else QSS_LIGHT)

    # ---------------- Compression ----------------
    def _on_compression_changed(self, kb: int) -> None:
        self.compression_kb = kb
        try:
            save_compression(kb)
        except OSError:
            pass

    # ---------------- Create Missing Folders ----------------
    def create_category_folders(self) -> None:
        specs = get_faction_folder_specs(self.faction)
        if not specs:
            QMessageBox.warning(
                self, "Unknown Faction",
                f"No folder specifications found for faction '{self.faction}'."
            )
            return

        folder_list = "\n".join(f"  •  {name}" for name, _ in specs)
        confirm = QMessageBox(self)
        confirm.setIcon(QMessageBox.Question)
        confirm.setWindowTitle("Create Missing Folders")
        confirm.setText("Create missing category folders?")
        confirm.setInformativeText(
            f"The following folders will be created inside:\n"
            f"{Path(self.mta_folder) / 'screenshots'}\n\n"
            f"{folder_list}\n\n"
            "Existing folders will be left untouched."
        )
        yes_btn = confirm.addButton("Create", QMessageBox.YesRole)
        no_btn = confirm.addButton("Cancel", QMessageBox.NoRole)
        confirm.setDefaultButton(yes_btn)
        confirm.exec()

        if confirm.clickedButton() is not yes_btn:
            return

        created, skipped, error = create_faction_folders(self.mta_folder, self.faction)

        if error and created == 0:
            QMessageBox.warning(self, "Create Folders Failed",
                                f"Could not create folders:\n{error}")
            return
        if error:
            QMessageBox.warning(
                self, "Partially Completed",
                f"Created {created} folder(s), skipped {skipped}.\n"
                f"Some errors occurred:\n\n{error}"
            )
            return
        QMessageBox.information(
            self, "Folders Ready",
            f"Done!\n\nCreated: {created}\nAlready existed: {skipped}"
        )

    # ---------------- Folder / Faction / Rank / Name ----------------
    def _ensure_game_name(self) -> str | None:
        if self.game_name:
            return self.game_name
        dlg = GameNameDialog(self, self.game_name)
        if dlg.exec() != QDialog.Accepted or not dlg.name_value:
            return None
        try:
            save_name(dlg.name_value)
        except OSError as exc:
            QMessageBox.critical(self, "Registry Error",
                                 f"Failed to save the game name:\n{exc}")
            return None
        self.game_name = dlg.name_value
        self._refresh_labels()
        return self.game_name

    def create_report_folder(self) -> None:
        if is_coming_soon(self.faction):
            QMessageBox.information(
                self, "Coming Soon",
                f"Prices for '{self.faction}' have not been announced yet.\n\n"
                "This feature will be added in a future update.\n\n"
                "You can change your faction anytime from Settings."
            )
            return

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

        total_files = count_total_pngs(self.mta_folder, self.faction, self.rank)
        if total_files == 0:
            QMessageBox.warning(
                self, "Create Report Error",
                "No PNG screenshots were found inside any category folder.\n"
                "Nothing was created on the Desktop."
            )
            return

        total_png_bytes = estimate_png_size(self.mta_folder, self.faction, self.rank)
        estimated_bytes = estimate_output_size(total_png_bytes, total_files, self.compression_kb)

        desktop_path = QStandardPaths.writableLocation(QStandardPaths.DesktopLocation)
        if not desktop_path:
            QMessageBox.warning(self, "Error", "Could not determine Desktop location.")
            return
        desktop = Path(desktop_path)
        if not desktop.is_dir():
            QMessageBox.warning(self, "Error", f"Desktop folder not found:\n{desktop}")
            return

        try:
            free_bytes = shutil.disk_usage(desktop).free
        except OSError:
            free_bytes = 0

        if free_bytes > 0 and estimated_bytes > free_bytes * 0.9:
            QMessageBox.warning(
                self, "Not Enough Disk Space",
                "There may not be enough free disk space to complete this task.\n\n"
                f"<b>Estimated output:</b> {format_size(estimated_bytes)}<br>"
                f"<b>Free space on Desktop drive:</b> {format_size(free_bytes)}<br><br>"
                "Please free up some space and try again."
            )
            return

        preview = PreviewDialog(
            self,
            faction_display=self._faction_display(),
            game_name=name,
            total_files=total_files,
            total_png_bytes=total_png_bytes,
            estimated_bytes=estimated_bytes,
            max_kb=self.compression_kb,
            free_bytes=free_bytes,
            target_path=desktop / name,
        )
        if preview.exec() != QDialog.Accepted:
            return

        self._convert_dialog = ProgressDialog(self, total_files)
        worker = ConvertWorker(
            self.mta_folder, name, self.faction, self.rank,
            max_kb=self.compression_kb, parent=self
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

        QMessageBox.information(
            self, "Work Report Created",
            "The work report was created successfully.\n\n"
            f"Faction: {self._faction_display()}\n"
            f"Compression: max {self.compression_kb} KB per image\n\n"
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
        if is_coming_soon(self.faction):
            QMessageBox.information(
                self, "Coming Soon",
                f"Prices for '{self.faction}' have not been announced yet.\n\n"
                "This feature will be added in a future update.\n\n"
                "You can change your faction anytime from Settings."
            )
            return

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

        deleted, error = clear_work_reports(self.mta_folder, self.faction, self.rank)

        if error and deleted == 0:
            QMessageBox.warning(self, "Clear Work Reports",
                                f"Deletion failed:\n{error}")
            return
        if error:
            QMessageBox.warning(
                self, "Partially Completed",
                f"Deleted {deleted} file(s), but some errors occurred:\n\n{error}"
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
            QMessageBox.critical(self, "Registry Error",
                                 f"Failed to save the folder:\n{exc}")
            return
        self.mta_folder = dlg.selected_path
        self._refresh_labels()
        QMessageBox.information(self, "Saved",
                                "The MTA:SA folder has been updated successfully.")

    def change_faction(self) -> None:
        dlg = FactionDialog(self, self.faction)
        if dlg.exec() != QDialog.Accepted or not dlg.faction_value:
            return

        new_faction = dlg.faction_value
        try:
            save_faction(new_faction)
        except OSError as exc:
            QMessageBox.critical(self, "Registry Error",
                                 f"Failed to save the faction:\n{exc}")
            return
        self.faction = new_faction

        if faction_requires_rank(new_faction):
            rank_dlg = RankDialog(self, new_faction, self.rank)
            if rank_dlg.exec() == QDialog.Accepted and rank_dlg.rank_value:
                try:
                    save_rank(rank_dlg.rank_value)
                except OSError as exc:
                    QMessageBox.critical(self, "Registry Error",
                                         f"Failed to save the rank:\n{exc}")
                    return
                self.rank = rank_dlg.rank_value
            elif not self.rank:
                self.rank = DEFAULT_RANK
                try:
                    save_rank(self.rank)
                except OSError:
                    pass

        self._refresh_labels()
        QMessageBox.information(self, "Saved", f"Faction changed to {self.faction}.")

    def change_rank(self) -> None:
        if not faction_requires_rank(self.faction):
            QMessageBox.information(
                self, "Rank",
                "The current faction does not use ranks.\n"
                "Ranks are only available for rank-based factions."
            )
            return
        dlg = RankDialog(self, self.faction, self.rank)
        if dlg.exec() != QDialog.Accepted or not dlg.rank_value:
            return
        try:
            save_rank(dlg.rank_value)
        except OSError as exc:
            QMessageBox.critical(self, "Registry Error",
                                 f"Failed to save the rank:\n{exc}")
            return
        self.rank = dlg.rank_value
        self._refresh_labels()
        QMessageBox.information(self, "Saved", f"Rank changed to {self.rank}.")

    def change_name(self) -> None:
        dlg = GameNameDialog(self, self.game_name)
        if dlg.exec() != QDialog.Accepted or not dlg.name_value:
            return
        try:
            save_name(dlg.name_value)
        except OSError as exc:
            QMessageBox.critical(self, "Registry Error",
                                 f"Failed to save the game name:\n{exc}")
            return
        self.game_name = dlg.name_value
        self._refresh_labels()
        QMessageBox.information(self, "Saved",
                                "The game name has been updated successfully.")

    def show_about(self) -> None:
        QMessageBox.information(
            self,
            f"About {APP_NAME}",
            f"<b>{APP_NAME}</b> — v{APP_VERSION}<br>"
            f"<i>Made By {APP_AUTHOR}</i><br><br>"
            "A small utility for MTA:SA players.<br>"
            "• Stores the MTA:SA folder, faction, rank, and game name in the "
            "Windows registry.<br>"
            "• Calculates a work report using faction- and rank-specific prices.<br>"
            "• Converts PNG screenshots to JPG with adjustable compression.<br>"
            "• Creates a zipped work report on the Desktop with a preview "
            "and disk-space check before starting.<br>"
            "• 🚔 Fine Calculator for Police Department (speed violations).<br>"
            "• Faction Stats Dashboard with visual category breakdown.<br>"
            "• Progress dialog with live ETA.<br>"
            "• Exports reports to CSV or PDF.<br>"
            "• Previews screenshots by double-clicking a category row.<br>"
            "• Supports both Light and Dark themes.<br>"
            "• Automatically checks for updates on launch."
        )


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

    folder = get_saved_folder()
    faction = get_saved_faction()
    rank = get_saved_rank()
    game_name = get_saved_name()
    theme = get_saved_theme()
    compression_kb = get_saved_compression()

    is_first_launch = (not folder or not Path(folder).is_dir()) and not faction

    if is_first_launch:
        wizard = SetupWizard(
            None,
            initial_folder=folder or "",
            initial_faction=faction,
            initial_rank=rank,
            initial_theme=theme,
        )
        if wizard.exec() != QDialog.Accepted:
            return 0

        folder = wizard.folder_value
        faction = wizard.faction_value
        rank = wizard.rank_value
        game_name = wizard.game_name_value
        theme = wizard.theme_value

        try:
            save_folder(folder)
            save_faction(faction)
            if faction_requires_rank(faction) and rank:
                save_rank(rank)
            if game_name:
                save_name(game_name)
            save_theme(theme)
        except OSError as exc:
            QMessageBox.critical(
                None, "Registry Error",
                f"Failed to save setup to the registry:\n{exc}"
            )
            return 1
    else:
        if not folder or not Path(folder).is_dir():
            dlg = FolderPickerDialog(None, folder or "")
            if dlg.exec() != QDialog.Accepted or not dlg.selected_path:
                return 0
            try:
                save_folder(dlg.selected_path)
            except OSError as exc:
                QMessageBox.critical(None, "Registry Error",
                                     f"Failed to save the folder:\n{exc}")
                return 1
            folder = dlg.selected_path

        if not faction:
            dlg = FactionDialog(None, None)
            if dlg.exec() != QDialog.Accepted or not dlg.faction_value:
                return 0
            try:
                save_faction(dlg.faction_value)
            except OSError as exc:
                QMessageBox.critical(None, "Registry Error",
                                     f"Failed to save the faction:\n{exc}")
                return 1
            faction = dlg.faction_value

        if faction_requires_rank(faction) and not rank:
            dlg = RankDialog(None, faction, None)
            if dlg.exec() != QDialog.Accepted or not dlg.rank_value:
                return 0
            try:
                save_rank(dlg.rank_value)
            except OSError as exc:
                QMessageBox.critical(None, "Registry Error",
                                     f"Failed to save the rank:\n{exc}")
                return 1
            rank = dlg.rank_value

        game_name = get_saved_name()
        theme = get_saved_theme()
        compression_kb = get_saved_compression()

    window = MainWindow(folder, game_name, faction, rank, theme, compression_kb)
    if icon_path.exists():
        window.setWindowIcon(QIcon(str(icon_path)))
    window.show()

    QTimer.singleShot(2000, window.check_for_updates_silent)

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())