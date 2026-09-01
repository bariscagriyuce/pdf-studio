"""Koyu / açık tema paletleri ve stil sayfası."""
from __future__ import annotations

DARK = {
    "name": "dark",
    "bg": "#1c1f26", "bg2": "#232733", "bg3": "#2b3040", "panel": "#20242e",
    "border": "#39405233", "line": "#394052",
    "text": "#dce1ec", "dim": "#98a1b5", "muted": "#6b7280",
    "accent": "#4f8cff", "accent2": "#3d6fd4", "danger": "#e5484d",
    "ok": "#3fb950", "warn": "#d99a2b",
    "canvas": "#14161c", "page_shadow": "#00000099", "icon": "#c7cedd",
    "sel": "#4f8cff55",
}

LIGHT = {
    "name": "light",
    "bg": "#f2f3f7", "bg2": "#ffffff", "bg3": "#e6e9f0", "panel": "#fafbfd",
    "border": "#00000018", "line": "#d3d8e3",
    "text": "#1b1f2a", "dim": "#525a6b", "muted": "#8b93a5",
    "accent": "#2f6fed", "accent2": "#1e57c8", "danger": "#d0343a",
    "ok": "#2c9c46", "warn": "#b7791f",
    "canvas": "#9aa1ae", "page_shadow": "#00000055", "icon": "#3a4252",
    "sel": "#2f6fed44",
}

THEMES = {"dark": DARK, "light": LIGHT}


def stylesheet(p: dict) -> str:
    return f"""
* {{ outline: none; }}
QWidget {{ background: {p['bg']}; color: {p['text']};
           font-size: 13px; }}
QMainWindow::separator {{ background: {p['line']}; width: 1px; height: 1px; }}

QToolBar {{ background: {p['bg2']}; border: none; border-bottom: 1px solid {p['line']};
            padding: 4px 6px; spacing: 3px; }}
QToolBar::separator {{ background: {p['line']}; width: 1px; margin: 5px 6px; }}
QToolButton {{ background: transparent; border: 1px solid transparent; border-radius: 7px;
               padding: 5px; color: {p['text']}; }}
QToolButton:hover {{ background: {p['bg3']}; }}
QToolButton:pressed {{ background: {p['accent2']}; }}
QToolButton:checked {{ background: {p['accent']}; color: #ffffff; }}
QToolButton[section="true"], QToolButton[section="true"]:checked,
QToolButton[section="true"]:pressed {{ background: transparent;
    color: {p['dim']}; border: none; }}
QToolButton::menu-indicator {{ image: none; width: 0; }}

QMenuBar {{ background: {p['bg2']}; border-bottom: 1px solid {p['line']}; padding: 2px; }}
QMenuBar::item {{ padding: 5px 11px; border-radius: 6px; background: transparent; }}
QMenuBar::item:selected {{ background: {p['bg3']}; }}
QMenu {{ background: {p['bg2']}; border: 1px solid {p['line']}; border-radius: 9px;
         padding: 5px; }}
QMenu::item {{ padding: 6px 26px 6px 26px; border-radius: 6px; }}
QMenu::item:selected {{ background: {p['accent']}; color: #fff; }}
QMenu::separator {{ height: 1px; background: {p['line']}; margin: 5px 8px; }}
QMenu::icon {{ padding-left: 8px; }}

QDockWidget {{ titlebar-close-icon: none; titlebar-normal-icon: none;
               font-weight: 600; }}
QDockWidget::title {{ background: {p['bg2']}; padding: 7px 10px;
                      border-bottom: 1px solid {p['line']}; }}

QTabWidget::pane {{ border: none; background: {p['panel']}; }}
QTabBar {{ background: {p['bg2']}; }}
QTabBar::tab {{ background: transparent; padding: 7px 12px; border: none;
                color: {p['dim']}; margin: 3px 1px; border-radius: 7px; }}
QTabBar::tab:selected {{ background: {p['bg3']}; color: {p['text']}; }}
QTabBar::tab:hover:!selected {{ color: {p['text']}; }}

QLineEdit, QPlainTextEdit, QTextEdit, QSpinBox, QDoubleSpinBox, QComboBox {{
    background: {p['bg3']}; border: 1px solid {p['line']}; border-radius: 7px;
    padding: 5px 8px; selection-background-color: {p['accent']}; color: {p['text']}; }}
QLineEdit:focus, QPlainTextEdit:focus, QTextEdit:focus, QSpinBox:focus,
QDoubleSpinBox:focus, QComboBox:focus {{ border: 1px solid {p['accent']}; }}
QComboBox::drop-down {{ border: none; width: 20px; }}
QComboBox QAbstractItemView {{ background: {p['bg2']}; border: 1px solid {p['line']};
    selection-background-color: {p['accent']}; border-radius: 8px; padding: 4px; }}
QSpinBox::up-button, QSpinBox::down-button,
QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {{ width: 15px; border: none;
    background: transparent; }}

QPushButton {{ background: {p['bg3']}; border: 1px solid {p['line']}; border-radius: 7px;
               padding: 6px 14px; }}
QPushButton:hover {{ background: {p['line']}; }}
QPushButton:pressed {{ background: {p['accent2']}; color: #fff; }}
QPushButton:disabled {{ color: {p['muted']}; }}
QPushButton[accent="true"] {{ background: {p['accent']}; color: #fff; border: none;
                              font-weight: 600; }}
QPushButton[accent="true"]:hover {{ background: {p['accent2']}; }}
QPushButton[danger="true"] {{ background: {p['danger']}; color: #fff; border: none; }}

QListView, QTreeView, QTableView, QListWidget, QTreeWidget, QTableWidget {{
    background: {p['panel']}; border: none; alternate-background-color: {p['bg2']};
    selection-background-color: {p['accent']}; selection-color: #fff; }}
QHeaderView::section {{ background: {p['bg2']}; border: none;
    border-bottom: 1px solid {p['line']}; padding: 6px; color: {p['dim']}; }}
QTreeView::item, QListWidget::item {{ padding: 4px; border-radius: 6px; }}
QTreeView::item:hover, QListWidget::item:hover {{ background: {p['bg3']}; }}

QScrollBar:vertical {{ background: transparent; width: 11px; margin: 2px; }}
QScrollBar::handle:vertical {{ background: {p['line']}; border-radius: 5px; min-height: 30px; }}
QScrollBar::handle:vertical:hover {{ background: {p['dim']}; }}
QScrollBar:horizontal {{ background: transparent; height: 11px; margin: 2px; }}
QScrollBar::handle:horizontal {{ background: {p['line']}; border-radius: 5px; min-width: 30px; }}
QScrollBar::handle:horizontal:hover {{ background: {p['dim']}; }}
QScrollBar::add-line, QScrollBar::sub-line {{ height: 0; width: 0; }}
QScrollBar::add-page, QScrollBar::sub-page {{ background: none; }}

QStatusBar {{ background: {p['bg2']}; border-top: 1px solid {p['line']}; color: {p['dim']}; }}
QStatusBar::item {{ border: none; }}

QSlider::groove:horizontal {{ height: 4px; background: {p['line']}; border-radius: 2px; }}
QSlider::handle:horizontal {{ background: {p['accent']}; width: 14px; height: 14px;
    margin: -5px 0; border-radius: 7px; }}

QGroupBox {{ border: 1px solid {p['line']}; border-radius: 9px; margin-top: 14px;
             padding-top: 8px; font-weight: 600; }}
QGroupBox::title {{ subcontrol-origin: margin; left: 11px; padding: 0 5px;
                    color: {p['dim']}; }}

QCheckBox::indicator, QRadioButton::indicator {{ width: 16px; height: 16px;
    border: 1px solid {p['line']}; border-radius: 4px; background: {p['bg3']}; }}
QRadioButton::indicator {{ border-radius: 8px; }}
QCheckBox::indicator:checked, QRadioButton::indicator:checked {{
    background: {p['accent']}; border-color: {p['accent']}; }}

QProgressBar {{ background: {p['bg3']}; border: none; border-radius: 6px; height: 8px;
                text-align: center; }}
QProgressBar::chunk {{ background: {p['accent']}; border-radius: 6px; }}

QToolTip {{ background: {p['bg2']}; color: {p['text']}; border: 1px solid {p['line']};
            padding: 5px 8px; border-radius: 6px; }}

QSplitter::handle {{ background: {p['line']}; }}
QLabel[hint="true"] {{ color: {p['dim']}; }}
QLabel[title="true"] {{ font-weight: 700; font-size: 14px; }}
"""
