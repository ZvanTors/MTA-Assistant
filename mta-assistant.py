"""
MTA Assistant - v1.0.0  ( Made By AmooReza )
A PySide6 Windows application for MTA:SA players.
"""

import sys
import shutil
import winreg
from pathlib import Path

from PySide6.QtCore import Qt, QStandardPaths
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFileDialog, QMessageBox, QMainWindow, QWidget,
    QStackedWidget, QTableWidget, QTableWidgetItem, QHeaderView, QFrame
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
APP_NAME = "MTA Assistant"
APP_VERSION = "1.0.0"
APP_AUTHOR = "AmooReza"
APP_TITLE = f"{APP_NAME} — v{APP_VERSION}  ( Made By {APP_AUTHOR} )"

REG_PATH = r"Software\MTA Assistant"
REG_VALUE_FOLDER = "MTAFolder"
REG_VALUE_NAME = "GameName"

PRICES = [
    ("Arrest",  "arrest",  5000),
    ("Kill",    "kill",    2000),
    ("Shift",   "shift",   5000),
    ("TakeGun", "takegun", 8000),
    ("Wanted",  "wanted",  6000),
]


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
# Report calculation
# ---------------------------------------------------------------------------
def calculate_report(base_folder: str):
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
    for display_name, key, price in PRICES:
        folder = subdirs.get(key)
        count = 0
        if folder is not None:
            count += _count_pngs(folder)
            nested = _find_nested(folder, key)
            if nested is not None:
                count += _count_pngs(nested)
        results.append((display_name, count, price, count * price))

    return results, None


# ---------------------------------------------------------------------------
# Create work report (copy nested folders to Desktop + zip)
# ---------------------------------------------------------------------------
def create_work_report(base_folder: str, game_name: str):
    """
    Creates  <Desktop>/<game_name>/  with the copied category folders,
    then compresses it into  <Desktop>/<game_name>.zip  next to it.

    Returns (target_path, zip_path, error).
    """
    screenshots_dir = Path(base_folder) / "screenshots"
    if not screenshots_dir.is_dir():
        return None, None, (
            "The 'screenshots' folder was not found at:\n"
            f"{screenshots_dir}"
        )

    desktop_path = QStandardPaths.writableLocation(QStandardPaths.DesktopLocation)
    if not desktop_path:
        return None, None, "Could not determine the Desktop folder location."
    desktop = Path(desktop_path)
    if not desktop.is_dir():
        return None, None, f"Desktop folder not found:\n{desktop}"

    target = desktop / game_name
    try:
        target.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        return None, None, f"Failed to create the folder on the Desktop:\n{exc}"

    try:
        subdirs = _collect_category_dirs(screenshots_dir)
    except OSError as exc:
        return None, None, f"Failed to read the screenshots folder:\n{exc}"

    copied: list[str] = []
    for display_name, key, _ in PRICES:
        cat = subdirs.get(key)
        if cat is None:
            continue
        nested = _find_nested(cat, key)
        source = nested if nested is not None else cat
        dst = target / display_name
        try:
            shutil.copytree(source, dst, dirs_exist_ok=True)
            copied.append(display_name)
        except OSError as exc:
            return None, None, f"Failed to copy '{display_name}':\n{exc}"

    if not copied:
        return None, None, (
            "No category folders were found inside the screenshots folder "
            "to copy."
        )

    # --- Zip the folder next to it (overwrite if exists) ---
    zip_base = desktop / game_name
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
        # Folder is safe; only the zip failed.
        return target, None, (
            f"The folder was created successfully, but zipping it failed:\n{exc}"
        )

    return target, zip_path, None


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
            "the copied category folders will be placed inside it, and the "
            "folder will then be compressed into a .zip file right next to it. "
            "Parentheses, uppercase letters and special characters are kept "
            "exactly as you type them. The name is saved in the registry."
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
# Main Window
# ---------------------------------------------------------------------------
class MainWindow(QMainWindow):
    def __init__(self, mta_folder: str, game_name: str | None):
        super().__init__()
        self.mta_folder = mta_folder
        self.game_name = game_name or ""

        self.setWindowTitle(APP_TITLE)
        self.setMinimumSize(940, 660)
        self.resize(1020, 700)

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

        settings_menu = menubar.addMenu("Settings")
        act_folder = QAction("Change MTA:SA Folder...", self)
        act_folder.triggered.connect(self.change_folder)
        settings_menu.addAction(act_folder)

        act_name = QAction("Change Game Name...", self)
        act_name.triggered.connect(self.change_name)
        settings_menu.addAction(act_name)

        help_menu = menubar.addMenu("Help")
        act_about = QAction(f"About {APP_NAME}", self)
        act_about.triggered.connect(self.show_about)
        help_menu.addAction(act_about)

    # ---------------- Pages ----------------
    def _create_home_page(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(60, 50, 60, 50)
        layout.setSpacing(16)

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

        layout.addSpacing(24)

        folder_box = QFrame()
        folder_box.setObjectName("card")
        fb_layout = QVBoxLayout(folder_box)
        fb_layout.setContentsMargins(18, 14, 18, 14)
        fb_layout.setSpacing(4)
        fb_title = QLabel("Current MTA:SA Folder")
        fb_title.setStyleSheet(
            "font-weight: bold; color: #34495e; font-size: 12px;"
        )
        self.home_folder_label = QLabel()
        self.home_folder_label.setWordWrap(True)
        self.home_folder_label.setStyleSheet("color: #2c3e50; font-size: 13px;")
        fb_layout.addWidget(fb_title)
        fb_layout.addWidget(self.home_folder_label)
        layout.addWidget(folder_box)

        name_box = QFrame()
        name_box.setObjectName("card")
        nb_layout = QVBoxLayout(name_box)
        nb_layout.setContentsMargins(18, 14, 18, 14)
        nb_layout.setSpacing(4)
        nb_title = QLabel("Current Game Name")
        nb_title.setStyleSheet(
            "font-weight: bold; color: #34495e; font-size: 12px;"
        )
        self.home_name_label = QLabel()
        self.home_name_label.setWordWrap(True)
        self.home_name_label.setStyleSheet("color: #2c3e50; font-size: 13px;")
        nb_layout.addWidget(nb_title)
        nb_layout.addWidget(self.home_name_label)
        layout.addWidget(name_box)

        layout.addSpacing(24)

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
        d1 = QLabel(
            "Counts PNG screenshots inside the Arrest, Kill, Shift, TakeGun "
            "and Wanted folders, and calculates the total earnings for each "
            "category and for the whole report."
        )
        d1.setWordWrap(True)
        d1.setStyleSheet("color: #6b7c93;")
        info1.addWidget(t1)
        info1.addWidget(d1)
        c1.addLayout(info1, 1)
        run_btn = QPushButton("Calculate Work Report")
        run_btn.setMinimumHeight(44)
        run_btn.setMinimumWidth(210)
        run_btn.clicked.connect(self.run_report)
        c1.addWidget(run_btn, 0, Qt.AlignVCenter)
        layout.addWidget(card1)

        # Card 2 — Create report folder + zip
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
            "Creates a folder named after your in-game name on the Desktop, "
            "copies each category's nested same-named folder (with all of its "
            "contents) inside it, and then automatically compresses the folder "
            "into a .zip file right next to it."
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

        card1 = QFrame()
        card1.setObjectName("card")
        c1 = QVBoxLayout(card1)
        c1.setContentsMargins(22, 22, 22, 22)
        c1.setSpacing(12)

        lbl1 = QLabel("MTA:SA Folder")
        lbl1.setStyleSheet("font-weight: bold; color: #34495e;")
        c1.addWidget(lbl1)

        self.settings_folder_label = QLabel()
        self.settings_folder_label.setWordWrap(True)
        self.settings_folder_label.setStyleSheet(
            "color: #2c3e50; background:#f4f6f8; padding:12px;"
            "border-radius:6px; border: 1px solid #e1e8ed;"
        )
        c1.addWidget(self.settings_folder_label)

        change_folder_btn = QPushButton("Change Folder...")
        change_folder_btn.setMinimumHeight(38)
        change_folder_btn.setMinimumWidth(180)
        change_folder_btn.clicked.connect(self.change_folder)
        c1.addWidget(change_folder_btn, 0, Qt.AlignLeft)
        layout.addWidget(card1)

        card2 = QFrame()
        card2.setObjectName("card")
        c2 = QVBoxLayout(card2)
        c2.setContentsMargins(22, 22, 22, 22)
        c2.setSpacing(12)

        lbl2 = QLabel("Game Name")
        lbl2.setStyleSheet("font-weight: bold; color: #34495e;")
        c2.addWidget(lbl2)

        self.settings_name_label = QLabel()
        self.settings_name_label.setWordWrap(True)
        self.settings_name_label.setStyleSheet(
            "color: #2c3e50; background:#f4f6f8; padding:12px;"
            "border-radius:6px; border: 1px solid #e1e8ed;"
        )
        c2.addWidget(self.settings_name_label)

        change_name_btn = QPushButton("Change Game Name...")
        change_name_btn.setMinimumHeight(38)
        change_name_btn.setMinimumWidth(180)
        change_name_btn.clicked.connect(self.change_name)
        c2.addWidget(change_name_btn, 0, Qt.AlignLeft)
        layout.addWidget(card2)

        layout.addStretch()
        return page

    # ---------------- Logic ----------------
    def _refresh_labels(self) -> None:
        self.home_folder_label.setText(self.mta_folder)
        self.settings_folder_label.setText(self.mta_folder)

        name_display = self.game_name if self.game_name else "(not set yet)"
        self.home_name_label.setText(name_display)
        self.settings_name_label.setText(name_display)

    def run_report(self) -> None:
        results, error = calculate_report(self.mta_folder)
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
        self.report_info.setText(f"Screenshots directory:  {screenshots_dir}")
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
        name = self._ensure_game_name()
        if not name:
            return

        target, zip_path, error = create_work_report(self.mta_folder, name)

        if target is None:
            QMessageBox.warning(self, "Create Report Error", error)
            return

        if zip_path is None:
            # Folder created, but zip failed.
            QMessageBox.warning(
                self, "Zip Error",
                f"The folder was created at:\n{target}\n\n"
                f"But the .zip file could not be created:\n{error}"
            )
            return

        QMessageBox.information(
            self, "Work Report Created",
            "The work report was created successfully.\n\n"
            f"Folder:\n{target}\n\n"
            f"Zip:\n{zip_path}"
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
            "• Stores the MTA:SA folder and the game name in the Windows "
            "registry.<br>"
            "• Calculates a work report from the screenshots folder.<br>"
            "• Creates a Desktop folder named after your in-game name, "
            "copies the nested category folders into it, and automatically "
            "compresses it into a .zip file."
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

            QLineEdit {
                background: #ffffff;
                border: 1px solid #d6dee6;
                border-radius: 6px;
                padding: 6px 10px;
                selection-background-color: #3498db;
            }
            QLineEdit:focus { border: 1px solid #3498db; }

            QFrame#card {
                background: #ffffff;
                border: 1px solid #e1e8ed;
                border-radius: 10px;
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

    game_name = get_saved_name()

    window = MainWindow(folder, game_name)
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())