#!/usr/bin/env python3
"""
YT-DLP GUI — Interface graphique PyQt6
Lancement : python3 ytdlp_gui.py
Dépendances : pip install PyQt6 yt-dlp
"""

import os
import re
import shlex
import shutil
import subprocess
import sys
import threading
import time
from pathlib import Path

from PyQt6.QtCore import (
    Qt, QThread, pyqtSignal, QTimer, QPropertyAnimation,
    QEasingCurve, QRect, QSize,
)
from PyQt6.QtGui import (
    QColor, QFont, QFontDatabase, QIcon, QPalette,
    QTextCharFormat, QTextCursor, QPainter, QBrush, QPen,
    QLinearGradient, QRadialGradient,
)
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QLabel, QLineEdit, QPushButton, QComboBox,
    QCheckBox, QTextEdit, QScrollArea, QFrame, QSizePolicy,
    QSpacerItem, QProgressBar, QGroupBox, QFileDialog,
    QTabWidget, QSpinBox, QSlider, QMessageBox, QListWidget,
    QListWidgetItem, QSplitter,
)

# ─────────────────────────────────────────────────────────────────────────────
#  PALETTE & STYLE
# ─────────────────────────────────────────────────────────────────────────────

STYLE = """
QMainWindow, QWidget#root {
    background-color: #080c10;
}

/* ── Scrollbar ── */
QScrollBar:vertical {
    background: #0d1117;
    width: 7px;
    border-radius: 3px;
}
QScrollBar::handle:vertical {
    background: #1e2d3d;
    border-radius: 3px;
    min-height: 30px;
}
QScrollBar::handle:vertical:hover { background: #2a3f55; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }

QScrollBar:horizontal {
    background: #0d1117;
    height: 7px;
    border-radius: 3px;
}
QScrollBar::handle:horizontal {
    background: #1e2d3d;
    border-radius: 3px;
    min-width: 30px;
}
QScrollBar::handle:horizontal:hover { background: #2a3f55; }
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; }

/* ── Cards / Frames ── */
QFrame#card {
    background-color: #0f1520;
    border: 1px solid #1a2535;
    border-radius: 12px;
}

/* ── Labels ── */
QLabel { color: #d6e4f0; background: transparent; }
QLabel#tag {
    color: #00d4ff;
    font-size: 9px;
    letter-spacing: 3px;
}
QLabel#dim { color: #6a8399; }
QLabel#muted { color: #2d3f52; }

/* ── Inputs ── */
QLineEdit {
    background-color: #0d1117;
    border: 1px solid #1a2535;
    border-radius: 8px;
    color: #d6e4f0;
    padding: 9px 13px;
    font-family: 'JetBrains Mono', 'Courier New', monospace;
    font-size: 12px;
    selection-background-color: #1e4060;
}
QLineEdit:focus {
    border-color: #00d4ff;
    background-color: #0d1520;
}
QLineEdit::placeholder { color: #2d3f52; }

/* ── ComboBox ── */
QComboBox {
    background-color: #0d1117;
    border: 1px solid #1a2535;
    border-radius: 8px;
    color: #d6e4f0;
    padding: 8px 13px;
    font-size: 12px;
    min-height: 20px;
}
QComboBox:focus { border-color: #00d4ff; }
QComboBox::drop-down {
    border: none;
    width: 28px;
}
QComboBox::down-arrow {
    image: none;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 5px solid #6a8399;
    margin-right: 10px;
}
QComboBox QAbstractItemView {
    background-color: #141d2e;
    border: 1px solid #243347;
    border-radius: 8px;
    color: #d6e4f0;
    selection-background-color: #1e3a50;
    padding: 4px;
    outline: none;
}

/* ── CheckBox ── */
QCheckBox {
    color: #8bafc7;
    font-size: 12px;
    spacing: 8px;
}
QCheckBox::indicator {
    width: 16px; height: 16px;
    border-radius: 4px;
    border: 1px solid #243347;
    background: #0d1117;
}
QCheckBox::indicator:checked {
    background: #00d4ff;
    border-color: #00d4ff;
    image: none;
}
QCheckBox::indicator:checked:after { content: '✓'; }

/* ── SpinBox ── */
QSpinBox {
    background-color: #0d1117;
    border: 1px solid #1a2535;
    border-radius: 8px;
    color: #d6e4f0;
    padding: 8px 13px;
    font-size: 12px;
    font-family: 'JetBrains Mono', monospace;
}
QSpinBox:focus { border-color: #00d4ff; }
QSpinBox::up-button, QSpinBox::down-button {
    background: #141d2e;
    border: none;
    width: 22px;
}
QSpinBox::up-button:hover, QSpinBox::down-button:hover {
    background: #1e2d3d;
}

/* ── Progress Bar ── */
QProgressBar {
    background-color: #1a2535;
    border-radius: 4px;
    text-align: center;
    color: transparent;
    min-height: 7px;
    max-height: 7px;
}
QProgressBar::chunk {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
        stop:0 #0099cc, stop:1 #00d4ff);
    border-radius: 4px;
}

/* ── Terminal ── */
QTextEdit#terminal {
    background-color: #020508;
    border: 1px solid #1a2535;
    border-radius: 10px;
    color: #8bafc7;
    font-family: 'JetBrains Mono', 'Courier New', monospace;
    font-size: 11px;
    padding: 12px;
    selection-background-color: #1e3a50;
}

/* ── Tab Widget ── */
QTabWidget::pane {
    border: 1px solid #1a2535;
    border-radius: 0 10px 10px 10px;
    background: #0f1520;
}
QTabBar::tab {
    background: #0d1117;
    border: 1px solid #1a2535;
    border-bottom: none;
    border-radius: 8px 8px 0 0;
    color: #6a8399;
    padding: 8px 20px;
    font-size: 11px;
    margin-right: 3px;
    font-family: 'JetBrains Mono', monospace;
    letter-spacing: 1px;
}
QTabBar::tab:selected {
    background: #0f1520;
    color: #00d4ff;
    border-color: #1a2535;
}
QTabBar::tab:hover:!selected { color: #d6e4f0; }

/* ── List Widget ── */
QListWidget {
    background: #0d1117;
    border: 1px solid #1a2535;
    border-radius: 8px;
    color: #d6e4f0;
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    padding: 4px;
    outline: none;
}
QListWidget::item {
    padding: 7px 10px;
    border-radius: 6px;
    border: none;
}
QListWidget::item:selected {
    background: #1e3a50;
    color: #00d4ff;
}
QListWidget::item:hover:!selected { background: #141d2e; }

/* ── Group Box ── */
QGroupBox {
    color: #00d4ff;
    font-size: 9px;
    letter-spacing: 3px;
    border: 1px solid #1a2535;
    border-radius: 10px;
    margin-top: 14px;
    padding: 16px 12px 12px 12px;
    background: #0f1520;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 14px;
    padding: 0 6px;
    background: #0f1520;
    color: #00d4ff;
}
"""

# ─────────────────────────────────────────────────────────────────────────────
#  CUSTOM WIDGETS
# ─────────────────────────────────────────────────────────────────────────────

class AccentButton(QPushButton):
    """Cyan gradient primary button."""
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setMinimumHeight(46)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._update_style(False)

    def _update_style(self, hovered):
        shadow = "0 14px 40px rgba(0,212,255,0.35)" if hovered else ""
        self.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 #0099cc, stop:1 #00d4ff);
                color: #000;
                border: none;
                border-radius: 10px;
                font-family: 'JetBrains Mono', monospace;
                font-size: 13px;
                font-weight: bold;
                letter-spacing: 2px;
                padding: 0 24px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 #00aee0, stop:1 #33ddff);
            }}
            QPushButton:pressed {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 #007aa3, stop:1 #00aacc);
            }}
            QPushButton:disabled {{
                background: #1a2535;
                color: #2d3f52;
            }}
        """)


class GhostButton(QPushButton):
    """Outlined ghost button."""
    def __init__(self, text, color="#00d4ff", parent=None):
        super().__init__(text, parent)
        self.color = color
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                border: 1px solid #243347;
                border-radius: 8px;
                color: #6a8399;
                font-family: 'JetBrains Mono', monospace;
                font-size: 11px;
                letter-spacing: 1px;
                padding: 7px 16px;
            }}
            QPushButton:hover {{
                border-color: {color};
                color: {color};
                background: rgba(0,212,255,0.07);
            }}
            QPushButton:pressed {{
                background: rgba(0,212,255,0.14);
            }}
        """)


class ToggleChip(QPushButton):
    """Toggle chip button (like HTML toggles)."""
    def __init__(self, text, key, parent=None):
        super().__init__(text, parent)
        self.key = key
        self.setCheckable(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._set_style()
        self.toggled.connect(lambda _: self._set_style())

    def _set_style(self):
        on = self.isChecked()
        if on:
            self.setStyleSheet("""
                QPushButton {
                    background: rgba(0,212,255,0.12);
                    border: 1px solid #00d4ff;
                    border-radius: 8px;
                    color: #00d4ff;
                    font-family: 'JetBrains Mono', monospace;
                    font-size: 11px;
                    letter-spacing: 1px;
                    padding: 7px 14px;
                }
                QPushButton:hover { background: rgba(0,212,255,0.18); }
            """)
        else:
            self.setStyleSheet("""
                QPushButton {
                    background: #141d2e;
                    border: 1px solid #243347;
                    border-radius: 8px;
                    color: #6a8399;
                    font-family: 'JetBrains Mono', monospace;
                    font-size: 11px;
                    letter-spacing: 1px;
                    padding: 7px 14px;
                }
                QPushButton:hover { border-color: #00aee0; color: #d6e4f0; }
            """)


class SectionLabel(QLabel):
    """Section header with cyan tag style."""
    def __init__(self, text, parent=None):
        super().__init__(text.upper(), parent)
        self.setStyleSheet("""
            QLabel {
                color: #00d4ff;
                font-family: 'JetBrains Mono', monospace;
                font-size: 9px;
                letter-spacing: 3px;
                background: transparent;
            }
        """)


class Card(QFrame):
    """Dark card container."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("card")
        self.setStyleSheet("""
            QFrame#card {
                background-color: #0f1520;
                border: 1px solid #1a2535;
                border-radius: 12px;
            }
        """)
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(24, 20, 24, 20)
        self._layout.setSpacing(14)

    def layout(self):
        return self._layout


class FieldLabel(QLabel):
    def __init__(self, text, parent=None):
        super().__init__(text.upper(), parent)
        self.setStyleSheet("""
            QLabel {
                color: #6a8399;
                font-family: 'JetBrains Mono', monospace;
                font-size: 9px;
                letter-spacing: 2px;
                background: transparent;
            }
        """)


class CounterBox(QFrame):
    """Stats counter box."""
    def __init__(self, label, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QFrame {
                background: #0d1117;
                border: 1px solid #1a2535;
                border-radius: 10px;
            }
        """)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(14, 10, 14, 10)
        lay.setSpacing(3)
        self.val_label = QLabel("—")
        self.val_label.setStyleSheet("""
            QLabel {
                color: #00d4ff;
                font-family: 'JetBrains Mono', monospace;
                font-size: 22px;
                font-weight: bold;
                background: transparent;
            }
        """)
        self.lbl = QLabel(label.upper())
        self.lbl.setStyleSheet("""
            QLabel {
                color: #6a8399;
                font-family: 'JetBrains Mono', monospace;
                font-size: 9px;
                letter-spacing: 2px;
                background: transparent;
            }
        """)
        lay.addWidget(self.val_label)
        lay.addWidget(self.lbl)

    def set_value(self, v, green=False):
        self.val_label.setText(str(v))
        color = "#39d98a" if green else "#00d4ff"
        self.val_label.setStyleSheet(f"""
            QLabel {{
                color: {color};
                font-family: 'JetBrains Mono', monospace;
                font-size: 22px;
                font-weight: bold;
                background: transparent;
            }}
        """)


# ─────────────────────────────────────────────────────────────────────────────
#  DOWNLOAD WORKER
# ─────────────────────────────────────────────────────────────────────────────

PROGRESS_RE = re.compile(
    r'\[download\]\s+([\d.]+)%\s+of\s+~?([\d.]+\S*)\s+at\s+([\d.]+\S+/s)\s+ETA\s+([\d:]+)'
)
ITEM_RE = re.compile(r'\[download\] Downloading item (\d+) of (\d+)')


def find_ytdlp():
    candidates = ["yt-dlp", str(Path.home()/".local/bin/yt-dlp"),
                  "/usr/local/bin/yt-dlp", "/opt/homebrew/bin/yt-dlp"]
    for c in candidates:
        if shutil.which(c):
            return c
    try:
        r = subprocess.run([sys.executable, "-m", "yt_dlp", "--version"],
                           capture_output=True, timeout=5)
        if r.returncode == 0:
            return f"{sys.executable} -m yt_dlp"
    except Exception:
        pass
    return None


class DownloadWorker(QThread):
    log_line    = pyqtSignal(str)
    progress    = pyqtSignal(float, str, str, str)   # pct, speed, eta, size
    item_update = pyqtSignal(int, int)                # current, total
    done_inc    = pyqtSignal()
    finished    = pyqtSignal(bool, str)               # success, message

    def __init__(self, urls, args):
        super().__init__()
        self.urls = urls
        self.args = args
        self._proc = None
        self._abort = False

    def abort(self):
        self._abort = True
        if self._proc:
            try:
                self._proc.terminate()
            except Exception:
                pass

    def run(self):
        ytdlp = find_ytdlp()
        if not ytdlp:
            self.log_line.emit("[ERROR] yt-dlp introuvable. pip install yt-dlp")
            self.finished.emit(False, "yt-dlp introuvable")
            return

        cmd = (ytdlp.split() if " " in ytdlp else [ytdlp]) + self.args + self.urls
        self.log_line.emit("[CMD] " + " ".join(cmd))
        self.log_line.emit("[INFO] Démarrage...")

        try:
            self._proc = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, bufsize=1,
            )
            last_pct = 0.0
            for line in self._proc.stdout:
                if self._abort:
                    break
                line = line.rstrip()
                if not line:
                    continue
                self.log_line.emit(line)

                m = PROGRESS_RE.search(line)
                if m:
                    pct = float(m.group(1))
                    if pct != last_pct:
                        last_pct = pct
                        self.progress.emit(pct, m.group(3), m.group(4), m.group(2))

                mi = ITEM_RE.search(line)
                if mi:
                    self.item_update.emit(int(mi.group(1)), int(mi.group(2)))

                if "[download] 100%" in line or "[Merger]" in line:
                    self.done_inc.emit()

            self._proc.wait()
            if self._abort:
                self.finished.emit(False, "Annulé par l'utilisateur")
            elif self._proc.returncode == 0:
                self.log_line.emit("[OK] ✓ Téléchargement terminé avec succès.")
                self.finished.emit(True, "Terminé")
            else:
                self.log_line.emit(f"[ERR] Erreur (code {self._proc.returncode})")
                self.finished.emit(False, f"Erreur code {self._proc.returncode}")
        except Exception as e:
            self.log_line.emit(f"[ERROR] {e}")
            self.finished.emit(False, str(e))


# ─────────────────────────────────────────────────────────────────────────────
#  MAIN WINDOW
# ─────────────────────────────────────────────────────────────────────────────

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("YT-DLP // GUI")
        self.setMinimumSize(980, 760)
        self.resize(1080, 860)
        self.setStyleSheet(STYLE + "QMainWindow { background: #080c10; }")

        self._worker   = None
        self._start_ts = 0
        self._elapsed_timer = QTimer()
        self._elapsed_timer.timeout.connect(self._tick_elapsed)
        self._done_count = 0
        self._total_urls = 0

        self._build_ui()

    # ── UI Construction ───────────────────────────────────────────────────

    def _build_ui(self):
        root = QWidget()
        root.setObjectName("root")
        root.setStyleSheet("background: #080c10;")
        self.setCentralWidget(root)

        outer = QVBoxLayout(root)
        outer.setContentsMargins(28, 24, 28, 24)
        outer.setSpacing(0)

        # Header
        outer.addLayout(self._build_header())
        outer.addSpacing(20)

        # Splitter: left config | right progress+terminal
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setStyleSheet("QSplitter::handle { background: #1a2535; width: 2px; }")
        splitter.setHandleWidth(2)

        # Left scroll area
        left_scroll = QScrollArea()
        left_scroll.setWidgetResizable(True)
        left_scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        left_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        left_widget = QWidget()
        left_widget.setStyleSheet("background: transparent;")
        left_lay = QVBoxLayout(left_widget)
        left_lay.setContentsMargins(0, 0, 10, 0)
        left_lay.setSpacing(12)

        left_lay.addWidget(self._build_url_card())
        left_lay.addWidget(self._build_format_card())
        left_lay.addWidget(self._build_options_card())
        left_lay.addWidget(self._build_output_card())
        left_lay.addWidget(self._build_advanced_card())
        left_lay.addStretch()

        left_scroll.setWidget(left_widget)

        # Right pane
        self.right_widget = QWidget()
        self.right_widget.setStyleSheet("background: transparent;")
        right_lay = QVBoxLayout(self.right_widget)
        right_lay.setContentsMargins(10, 0, 0, 0)
        right_lay.setSpacing(12)
        right_lay.addWidget(self._build_action_card())
        right_lay.addWidget(self._build_progress_card(), 1)

        splitter.addWidget(left_scroll)
        splitter.addWidget(self.right_widget)
        splitter.setSizes([560, 480])
        self.splitter = splitter

        outer.addWidget(splitter, 1)

    def _build_header(self):
        lay = QHBoxLayout()

        # Brand
        brand = QVBoxLayout()
        brand.setSpacing(4)
        tag = QLabel("// TÉLÉCHARGEUR UNIVERSEL //")
        tag.setStyleSheet("""
            color: #00d4ff; font-family: 'JetBrains Mono', monospace;
            font-size: 9px; letter-spacing: 3px; background: transparent;
        """)
        title = QLabel("YT-DLP // GUI")
        title.setStyleSheet("""
            color: #d6e4f0; font-family: 'JetBrains Mono', monospace;
            font-size: 28px; font-weight: bold; background: transparent;
        """)
        brand.addWidget(tag)
        brand.addWidget(title)
        lay.addLayout(brand)
        lay.addStretch()

        self.toggle_panel_btn = GhostButton("⇤ Réduire", "#00d4ff")
        self.toggle_panel_btn.setFixedWidth(100)
        self.toggle_panel_btn.clicked.connect(self._toggle_progress_panel)
        lay.addWidget(self.toggle_panel_btn)
        return lay

    def _build_url_card(self):
        card = Card()
        card.layout().addWidget(SectionLabel("URLs"))

        # Input row
        row = QHBoxLayout()
        row.setSpacing(8)
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText(
            "https://youtube.com/watch?v=...  ou playlist, SoundCloud, Twitch, Vimeo...")
        self.url_input.returnPressed.connect(self._add_url)
        row.addWidget(self.url_input)

        add_btn = GhostButton("＋ AJOUTER", "#00d4ff")
        add_btn.setFixedWidth(110)
        add_btn.setMinimumHeight(38)
        add_btn.clicked.connect(self._add_url)
        row.addWidget(add_btn)
        card.layout().addLayout(row)

        # URL list
        self.url_list = QListWidget()
        self.url_list.setFixedHeight(110)
        self.url_list.setStyleSheet("""
            QListWidget {
                background: #0d1117; border: 1px solid #1a2535;
                border-radius: 8px; font-family: 'JetBrains Mono', monospace;
                font-size: 11px; color: #d6e4f0; padding: 4px; outline: none;
            }
            QListWidget::item { padding: 6px 10px; border-radius: 6px; }
            QListWidget::item:selected { background: #1e3a50; color: #00d4ff; }
            QListWidget::item:hover:!selected { background: #141d2e; }
        """)
        card.layout().addWidget(self.url_list)

        # Remove btn
        remove_row = QHBoxLayout()
        remove_row.addStretch()
        rm_btn = GhostButton("✕ SUPPRIMER SÉLECTION", "#ff5c5c")
        rm_btn.clicked.connect(self._remove_selected_url)
        remove_row.addWidget(rm_btn)
        card.layout().addLayout(remove_row)

        return card

    def _build_format_card(self):
        card = Card()
        card.layout().addWidget(SectionLabel("Format & Qualité"))

        grid = QGridLayout()
        grid.setSpacing(12)
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)

        # Mode
        grid.addWidget(FieldLabel("Mode"), 0, 0)
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["🎬  Vidéo", "🎵  Audio seulement"])
        self.mode_combo.currentIndexChanged.connect(self._on_mode_change)
        grid.addWidget(self.mode_combo, 1, 0)

        # Quality
        grid.addWidget(FieldLabel("Qualité vidéo"), 0, 1)
        self.quality_combo = QComboBox()
        self.quality_combo.addItems([
            "Meilleure (auto)",
            "4K (2160p)",
            "1440p",
            "1080p",
            "720p",
            "480p",
            "360p",
            "Minimum",
        ])
        self.quality_combo.setCurrentIndex(3)  # 1080p default
        grid.addWidget(self.quality_combo, 1, 1)

        # Container
        grid.addWidget(FieldLabel("Conteneur"), 2, 0)
        self.container_combo = QComboBox()
        self.container_combo.addItems([
            "Auto (format original)",
            "MP4", "MKV", "WebM", "MOV", "AVI",
        ])
        grid.addWidget(self.container_combo, 3, 0)

        # Audio format (hidden by default)
        self.audio_fmt_label = FieldLabel("Format audio")
        grid.addWidget(self.audio_fmt_label, 2, 0)
        self.audio_fmt_combo = QComboBox()
        self.audio_fmt_combo.addItems([
            "Source (ne pas convertir)",
            "MP3", "M4A (AAC)", "FLAC", "Opus", "WAV", "Vorbis", "AAC",
        ])
        grid.addWidget(self.audio_fmt_combo, 3, 0)
        self.audio_fmt_label.hide()
        self.audio_fmt_combo.hide()

        # Audio quality
        self.audio_q_label = FieldLabel("Qualité audio")
        grid.addWidget(self.audio_q_label, 2, 1)
        self.audio_q_combo = QComboBox()
        self.audio_q_combo.addItems(["320 kbps", "256 kbps", "192 kbps", "128 kbps", "96 kbps", "Auto"])
        self.audio_q_combo.setCurrentIndex(2)
        grid.addWidget(self.audio_q_combo, 3, 1)
        self.audio_q_label.hide()
        self.audio_q_combo.hide()

        # Rate limit
        grid.addWidget(FieldLabel("Limite de débit"), 4, 0)
        self.rate_input = QLineEdit()
        self.rate_input.setPlaceholderText("ex: 5M, 500K  (vide = illimité)")
        grid.addWidget(self.rate_input, 5, 0)

        # Concurrent fragments
        grid.addWidget(FieldLabel("Fragments simultanés"), 4, 1)
        self.frag_combo = QComboBox()
        self.frag_combo.addItems(["1", "2", "4", "8", "16"])
        self.frag_combo.setCurrentIndex(2)
        grid.addWidget(self.frag_combo, 5, 1)

        card.layout().addLayout(grid)
        return card

    def _build_options_card(self):
        card = Card()
        card.layout().addWidget(SectionLabel("Options"))

        self.toggles = {}
        chips = [
            ("🖼  Thumbnail intégrée",  "embed_thumbnail",  False),
            ("🏷  Métadonnées",          "add_metadata",     True),
            ("💬  Sous-titres",          "subs",             False),
            ("📎  Embed sous-titres",    "embed_subs",       False),
            ("✂️  SponsorBlock",         "sponsorblock",     False),
            ("💾  Sauver thumbnail",     "write_thumbnail",  False),
            ("🎵  Vidéo seule (no playlist)", "no_playlist", False),
        ]

        wrap = QWidget()
        wrap.setStyleSheet("background: transparent;")
        flow = QHBoxLayout(wrap)
        flow.setContentsMargins(0, 0, 0, 0)
        flow.setSpacing(8)
        flow.setAlignment(Qt.AlignmentFlag.AlignLeft)

        row1 = QHBoxLayout()
        row1.setSpacing(8)
        row2 = QHBoxLayout()
        row2.setSpacing(8)
        rows_lay = QVBoxLayout()
        rows_lay.setSpacing(8)

        for i, (text, key, default) in enumerate(chips):
            chip = ToggleChip(text, key)
            chip.setChecked(default)
            self.toggles[key] = chip
            if i < 4:
                row1.addWidget(chip)
            else:
                row2.addWidget(chip)

        row1.addStretch()
        row2.addStretch()
        rows_lay.addLayout(row1)
        rows_lay.addLayout(row2)
        card.layout().addLayout(rows_lay)

        # Subs lang row
        self.subs_row = QWidget()
        self.subs_row.setStyleSheet("background: transparent;")
        subs_lay = QHBoxLayout(self.subs_row)
        subs_lay.setContentsMargins(0, 4, 0, 0)
        subs_lay.setSpacing(12)
        subs_lay.addWidget(FieldLabel("Langues sous-titres :"))
        self.subs_lang_input = QLineEdit("fr,en")
        self.subs_lang_input.setFixedWidth(180)
        self.subs_lang_input.setPlaceholderText("fr,en,es")
        subs_lay.addWidget(self.subs_lang_input)
        subs_lay.addStretch()
        self.subs_row.hide()
        card.layout().addWidget(self.subs_row)

        self.toggles["subs"].toggled.connect(
            lambda on: self.subs_row.setVisible(on))

        return card

    def _build_output_card(self):
        card = Card()
        card.layout().addWidget(SectionLabel("Sortie"))

        grid = QGridLayout()
        grid.setSpacing(12)
        grid.setColumnStretch(0, 1)

        # Output dir
        grid.addWidget(FieldLabel("Dossier de destination"), 0, 0, 1, 2)
        dir_row = QHBoxLayout()
        self.out_dir_input = QLineEdit(str(Path.home() / "Downloads" / "yt-dlp"))
        dir_row.addWidget(self.out_dir_input)
        browse_btn = GhostButton("📁 PARCOURIR")
        browse_btn.setFixedWidth(120)
        browse_btn.clicked.connect(self._browse_dir)
        dir_row.addWidget(browse_btn)
        grid.addLayout(dir_row, 1, 0, 1, 2)

        # Template
        grid.addWidget(FieldLabel("Template de nom"), 2, 0)
        self.tmpl_combo = QComboBox()
        self.tmpl_combo.addItems([
            "%(title)s.%(ext)s",
            "%(uploader)s - %(title)s.%(ext)s",
            "%(playlist_index)s - %(title)s.%(ext)s",
            "%(upload_date)s - %(title)s.%(ext)s",
            "Personnalisé...",
        ])
        self.tmpl_combo.currentIndexChanged.connect(self._on_tmpl_change)
        grid.addWidget(self.tmpl_combo, 3, 0)

        # Custom template
        self.custom_tmpl_label = FieldLabel("Template personnalisé")
        self.custom_tmpl_input = QLineEdit("%(title)s.%(ext)s")
        self.custom_tmpl_label.hide()
        self.custom_tmpl_input.hide()
        grid.addWidget(self.custom_tmpl_label, 2, 1)
        grid.addWidget(self.custom_tmpl_input, 3, 1)

        card.layout().addLayout(grid)
        return card

    def _build_advanced_card(self):
        card = Card()
        header = QHBoxLayout()
        header.setSpacing(10)
        title = QLabel("AVANCÉ")
        title.setStyleSheet("""
            QLabel {
                color: #00d4ff;
                font-family: 'JetBrains Mono', monospace;
                font-size: 11px;
                letter-spacing: 2px;
                background: transparent;
            }
        """)
        header.addWidget(title)
        header.addStretch()
        card.layout().addLayout(header)

        self.advanced_content = QWidget()
        content_layout = QGridLayout(self.advanced_content)
        content_layout.setSpacing(12)
        content_layout.setColumnStretch(0, 1)
        content_layout.setColumnStretch(1, 1)

        # Playlist range
        content_layout.addWidget(FieldLabel("Début playlist"), 0, 0)
        content_layout.addWidget(FieldLabel("Fin playlist"), 0, 1)
        self.pl_start = QSpinBox()
        self.pl_start.setMinimum(1)
        self.pl_start.setMaximum(99999)
        self.pl_start.setValue(1)
        self.pl_end = QSpinBox()
        self.pl_end.setMinimum(1)
        self.pl_end.setMaximum(99999)
        self.pl_end.setValue(9999)
        content_layout.addWidget(self.pl_start, 1, 0)
        content_layout.addWidget(self.pl_end, 1, 1)

        # Cookies
        content_layout.addWidget(FieldLabel("Cookies depuis navigateur"), 2, 0)
        self.cookies_browser = QComboBox()
        self.cookies_browser.addItems(["— aucun —", "chrome", "firefox", "safari", "edge", "brave", "opera"])
        content_layout.addWidget(self.cookies_browser, 3, 0)

        content_layout.addWidget(FieldLabel("Fichier cookies"), 2, 1)
        self.cookies_file = QLineEdit()
        self.cookies_file.setPlaceholderText("chemin/vers/cookies.txt")
        content_layout.addWidget(self.cookies_file, 3, 1)

        # Proxy
        content_layout.addWidget(FieldLabel("Proxy"), 4, 0)
        self.proxy_input = QLineEdit()
        self.proxy_input.setPlaceholderText("http://127.0.0.1:8080")
        content_layout.addWidget(self.proxy_input, 5, 0)

        # Extra args
        content_layout.addWidget(FieldLabel("Arguments supplémentaires"), 6, 0, 1, 2)
        self.extra_args = QLineEdit()
        self.extra_args.setPlaceholderText("--no-overwrites --ignore-errors ...")
        content_layout.addWidget(self.extra_args, 7, 0, 1, 2)

        self.advanced_content.setVisible(True)
        card.layout().addWidget(self.advanced_content)

        return card

    def _build_action_card(self):
        card = Card()

        # Download button
        self.dl_btn = AccentButton("▶  LANCER LE TÉLÉCHARGEMENT")
        self.dl_btn.clicked.connect(self._start_download)
        card.layout().addWidget(self.dl_btn)

        # Abort button (hidden)
        self.abort_btn = GhostButton("⬛  ANNULER", "#ff5c5c")
        self.abort_btn.setMinimumHeight(42)
        self.abort_btn.clicked.connect(self._abort_download)
        self.abort_btn.hide()
        card.layout().addWidget(self.abort_btn)

        # Status label
        self.status_label = QLabel("Prêt")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("""
            QLabel {
                color: #6a8399;
                font-family: 'JetBrains Mono', monospace;
                font-size: 11px;
                letter-spacing: 1px;
                background: transparent;
                padding: 4px;
            }
        """)
        card.layout().addWidget(self.status_label)

        return card

    def _build_progress_card(self):
        card = Card()
        card.layout().addWidget(SectionLabel("Progression & Terminal"))

        # Counters row
        counters = QHBoxLayout()
        counters.setSpacing(10)
        self.ctr_total   = CounterBox("Total")
        self.ctr_done    = CounterBox("Terminés")
        self.ctr_current = CounterBox("En cours")
        self.ctr_size    = CounterBox("Taille")
        for c in [self.ctr_total, self.ctr_done, self.ctr_current, self.ctr_size]:
            counters.addWidget(c)
        card.layout().addLayout(counters)

        # Progress bar
        pb_label_row = QHBoxLayout()
        self.pb_label = QLabel("En attente...")
        self.pb_label.setStyleSheet("color:#6a8399;font-family:'JetBrains Mono',monospace;font-size:11px;background:transparent;")
        self.pb_pct   = QLabel("0%")
        self.pb_pct.setStyleSheet("color:#00d4ff;font-family:'JetBrains Mono',monospace;font-size:13px;font-weight:bold;background:transparent;")
        pb_label_row.addWidget(self.pb_label)
        pb_label_row.addStretch()
        pb_label_row.addWidget(self.pb_pct)
        card.layout().addLayout(pb_label_row)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 1000)
        self.progress_bar.setValue(0)
        card.layout().addWidget(self.progress_bar)

        # Stats row
        stats_row = QHBoxLayout()
        stats_row.setSpacing(20)
        self.stat_speed   = self._stat_chip("VITESSE", "—")
        self.stat_eta     = self._stat_chip("ETA", "—")
        self.stat_elapsed = self._stat_chip("ELAPSED", "—")
        for s in [self.stat_speed, self.stat_eta, self.stat_elapsed]:
            stats_row.addWidget(s)
        stats_row.addStretch()

        # Clear terminal btn
        clear_btn = GhostButton("CLEAR")
        clear_btn.setFixedWidth(80)
        clear_btn.clicked.connect(self._clear_terminal)
        stats_row.addWidget(clear_btn)
        card.layout().addLayout(stats_row)

        # Terminal
        self.terminal = QTextEdit()
        self.terminal.setObjectName("terminal")
        self.terminal.setReadOnly(True)
        self.terminal.setMinimumHeight(280)
        card.layout().addWidget(self.terminal, 1)

        return card

    def _stat_chip(self, label, value):
        w = QWidget()
        w.setStyleSheet("background: transparent;")
        lay = QHBoxLayout(w)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(6)
        lbl = QLabel(label)
        lbl.setStyleSheet("color:#2d3f52;font-family:'JetBrains Mono',monospace;font-size:9px;letter-spacing:2px;background:transparent;")
        val = QLabel(value)
        val.setObjectName(f"stat_{label}")
        val.setStyleSheet("color:#d6e4f0;font-family:'JetBrains Mono',monospace;font-size:11px;background:transparent;")
        lay.addWidget(lbl)
        lay.addWidget(val)
        # Store ref
        w._val_label = val
        return w

    # ── Logic ─────────────────────────────────────────────────────────────

    def _add_url(self):
        url = self.url_input.text().strip()
        if not url:
            return
        if url.startswith("www."):
            url = "https://" + url
        if not url.startswith(("http://", "https://")):
            self._log("[WARN] URL invalide (doit commencer par http ou www)")
            self.url_input.clear()
            return
        for i in range(self.url_list.count()):
            if self.url_list.item(i).text() == url:
                self.url_input.clear()
                return
        self.url_list.addItem(url)
        self.url_input.clear()

    def _remove_selected_url(self):
        for item in self.url_list.selectedItems():
            self.url_list.takeItem(self.url_list.row(item))

    def _browse_dir(self):
        d = QFileDialog.getExistingDirectory(self, "Choisir le dossier de destination",
                                              str(Path.home() / "Downloads"))
        if d:
            self.out_dir_input.setText(d)

    def _on_mode_change(self):
        audio = self.mode_combo.currentIndex() == 1
        self.quality_combo.setVisible(not audio)
        self.container_combo.setVisible(not audio)
        self.audio_fmt_label.setVisible(audio)
        self.audio_fmt_combo.setVisible(audio)
        self.audio_q_label.setVisible(audio)
        self.audio_q_combo.setVisible(audio)

    def _on_tmpl_change(self):
        custom = self.tmpl_combo.currentIndex() == 4
        self.custom_tmpl_label.setVisible(custom)
        self.custom_tmpl_input.setVisible(custom)

    def _build_args(self):
        args = []
        audio = self.mode_combo.currentIndex() == 1

        # Format
        qual_map = {
            0: "bestvideo+bestaudio/best",
            1: "bestvideo[height<=2160]+bestaudio/best",
            2: "bestvideo[height<=1440]+bestaudio/best",
            3: "bestvideo[height<=1080]+bestaudio/best",
            4: "bestvideo[height<=720]+bestaudio/best",
            5: "bestvideo[height<=480]+bestaudio/best",
            6: "bestvideo[height<=360]+bestaudio/best",
            7: "worstvideo+worstaudio/worst",
        }
        if audio:
            args += ["-f", "bestaudio/best", "-x"]
            fmt_map = {
                0: None,
                1: "mp3",
                2: "m4a",
                3: "flac",
                4: "opus",
                5: "wav",
                6: "vorbis",
                7: "aac",
            }
            audio_fmt = fmt_map[self.audio_fmt_combo.currentIndex()]
            if audio_fmt:
                args += ["--audio-format", audio_fmt]
            q_map = {0:"320",1:"256",2:"192",3:"128",4:"96",5:"0"}
            args += ["--audio-quality", q_map[self.audio_q_combo.currentIndex()]]
        else:
            args += ["-f", qual_map[self.quality_combo.currentIndex()]]
            cont_map = {
                0: None,
                1: "mp4",
                2: "mkv",
                3: "webm",
                4: "mov",
                5: "avi",
            }
            video_out = cont_map[self.container_combo.currentIndex()]
            if video_out:
                args += ["--merge-output-format", video_out]

        # Output
        out_dir = self.out_dir_input.text().strip() or str(Path.home() / "Downloads" / "yt-dlp")
        if self.tmpl_combo.currentIndex() == 4:
            tmpl = self.custom_tmpl_input.text() or "%(title)s.%(ext)s"
        else:
            tmpl = self.tmpl_combo.currentText()
        args += ["-o", os.path.join(os.path.expanduser(out_dir), tmpl)]

        # Rate
        rate = self.rate_input.text().strip()
        if rate:
            args += ["-r", rate]

        # Fragments
        args += ["--concurrent-fragments", self.frag_combo.currentText()]

        # Toggles
        if self.toggles["embed_thumbnail"].isChecked():
            args += ["--embed-thumbnail"]
        if self.toggles["add_metadata"].isChecked():
            args += ["--add-metadata"]
        if self.toggles["subs"].isChecked():
            args += ["--write-subs", "--write-auto-subs",
                     "--sub-langs", self.subs_lang_input.text() or "fr,en"]
        if self.toggles["embed_subs"].isChecked():
            args += ["--embed-subs"]
        if self.toggles["sponsorblock"].isChecked():
            args += ["--sponsorblock-remove", "all"]
        if self.toggles["write_thumbnail"].isChecked():
            args += ["--write-thumbnail"]
        if self.toggles["no_playlist"].isChecked():
            args += ["--no-playlist"]
        else:
            args += ["--playlist-start", str(self.pl_start.value()),
                     "--playlist-end",   str(self.pl_end.value())]

        # Cookies
        cb = self.cookies_browser.currentIndex()
        if cb > 0:
            browsers = ["chrome","firefox","safari","edge","brave","opera"]
            args += ["--cookies-from-browser", browsers[cb-1]]
        cf = self.cookies_file.text().strip()
        if cf:
            args += ["--cookies", cf]

        # Proxy
        px = self.proxy_input.text().strip()
        if px:
            args += ["--proxy", px]

        # Extra
        extra = self.extra_args.text().strip()
        if extra:
            args += shlex.split(extra)

        args += ["--progress", "--newline"]
        return args

    def _start_download(self):
        urls = [self.url_list.item(i).text() for i in range(self.url_list.count())]
        if not urls:
            QMessageBox.warning(self, "Aucune URL", "Ajoutez au moins une URL.")
            return

        self._total_urls = len(urls)
        self._done_count = 0
        self._start_ts   = time.time()

        # Reset UI
        self.progress_bar.setValue(0)
        self.pb_pct.setText("0%")
        self.pb_label.setText("Téléchargement en cours...")
        self.ctr_total.set_value(self._total_urls)
        self.ctr_done.set_value(0, green=True)
        self.ctr_current.set_value("1/" + str(self._total_urls))
        self.ctr_size.set_value("—")
        self.stat_speed._val_label.setText("—")
        self.stat_eta._val_label.setText("—")
        self.stat_elapsed._val_label.setText("0s")
        self._set_status("running", "● EN COURS")
        self.terminal.clear()

        self.dl_btn.setEnabled(False)
        self.dl_btn.setText("⟳  TÉLÉCHARGEMENT EN COURS...")
        self.abort_btn.show()

        # Reset progress bar style
        self.progress_bar.setStyleSheet("")

        args = self._build_args()
        self._worker = DownloadWorker(urls, args)
        self._worker.log_line.connect(self._on_log)
        self._worker.progress.connect(self._on_progress)
        self._worker.item_update.connect(self._on_item_update)
        self._worker.done_inc.connect(self._on_done_inc)
        self._worker.finished.connect(self._on_finished)
        self._worker.start()
        self._elapsed_timer.start(1000)

    def _abort_download(self):
        if self._worker:
            self._worker.abort()

    def _on_log(self, line):
        self._append_terminal(line)

    def _on_progress(self, pct, speed, eta, size):
        self.progress_bar.setValue(int(pct * 10))
        self.pb_pct.setText(f"{pct:.1f}%")
        self.stat_speed._val_label.setText(speed)
        self.stat_eta._val_label.setText(eta)
        self.ctr_size.set_value(size)

    def _on_item_update(self, cur, tot):
        self.ctr_current.set_value(f"{cur}/{tot}")

    def _on_done_inc(self):
        self._done_count = min(self._done_count + 1, self._total_urls)
        self.ctr_done.set_value(self._done_count, green=True)

    def _on_finished(self, success, msg):
        self._elapsed_timer.stop()
        self.dl_btn.setEnabled(True)
        self.dl_btn.setText("▶  LANCER LE TÉLÉCHARGEMENT")
        self.abort_btn.hide()

        if success:
            self.progress_bar.setValue(1000)
            self.pb_pct.setText("100%")
            self.pb_label.setText("Téléchargement terminé !")
            self.progress_bar.setStyleSheet("""
                QProgressBar::chunk {
                    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                        stop:0 #00cc66, stop:1 #39d98a);
                    border-radius: 4px;
                }
            """)
            self._set_status("done", "✓  TERMINÉ")
            self.stat_eta._val_label.setText("—")
            self.ctr_done.set_value(self._total_urls, green=True)
        else:
            self.progress_bar.setStyleSheet("""
                QProgressBar::chunk { background: #ff5c5c; border-radius: 4px; }
            """)
            self._set_status("error", f"✗  ERREUR — {msg}")

    def _set_status(self, kind, text):
        colors = {
            "running": "#00d4ff",
            "done":    "#39d98a",
            "error":   "#ff5c5c",
        }
        c = colors.get(kind, "#6a8399")
        self.status_label.setText(text)
        self.status_label.setStyleSheet(f"""
            QLabel {{
                color: {c};
                font-family: 'JetBrains Mono', monospace;
                font-size: 11px;
                letter-spacing: 1px;
                background: rgba(0,0,0,0.2);
                border: 1px solid {c}40;
                border-radius: 6px;
                padding: 5px 14px;
            }}
        """)

    def _tick_elapsed(self):
        s = int(time.time() - self._start_ts)
        m = s // 60
        sec = s % 60
        self.stat_elapsed._val_label.setText(
            f"{m}m {sec:02d}s" if m else f"{sec}s")

    def _append_terminal(self, line):
        cursor = self.terminal.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)

        fmt = QTextCharFormat()
        if line.startswith("[CMD]"):
            fmt.setForeground(QColor("#2d4a5f"))
        elif line.startswith("[YTDLP-GUI]") or line.startswith("[INFO]"):
            fmt.setForeground(QColor("#00d4ff"))
        elif line.startswith("[OK]") or "✓" in line:
            fmt.setForeground(QColor("#39d98a"))
        elif line.startswith("[ERROR]") or "ERROR" in line:
            fmt.setForeground(QColor("#ff5c5c"))
        elif "[warning]" in line.lower() or "WARNING" in line:
            fmt.setForeground(QColor("#f5c542"))
        elif line.startswith("[download]"):
            fmt.setForeground(QColor("#5cb8e4"))
        elif "Destination" in line or "Merging" in line:
            fmt.setForeground(QColor("#8ecfa0"))
        else:
            fmt.setForeground(QColor("#8bafc7"))

        cursor.setCharFormat(fmt)
        cursor.insertText(line + "\n")

        # Auto-scroll
        sb = self.terminal.verticalScrollBar()
        sb.setValue(sb.maximum())

        # Keep max lines
        doc = self.terminal.document()
        if doc.blockCount() > 800:
            c2 = QTextCursor(doc)
            c2.movePosition(QTextCursor.MoveOperation.Start)
            c2.movePosition(QTextCursor.MoveOperation.Down,
                            QTextCursor.MoveMode.KeepAnchor, 100)
            c2.removeSelectedText()

    def _clear_terminal(self):
        self.terminal.clear()

    def _toggle_progress_panel(self):
        visible = self.right_widget.isVisible()
        self.right_widget.setVisible(not visible)
        if visible:
            self.toggle_panel_btn.setText("⇥ Afficher")
            self.splitter.setSizes([self.width(), 0])
        else:
            self.toggle_panel_btn.setText("⇤ Réduire")
            self.splitter.setSizes([560, 480])

    def _log(self, line):
        self._append_terminal(line)

    def closeEvent(self, event):
        if self._worker and self._worker.isRunning():
            self._worker.abort()
            self._worker.wait(2000)
        event.accept()


# ─────────────────────────────────────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("YT-DLP GUI")
    app.setApplicationDisplayName("YT-DLP // GUI")

    # Dark palette
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window,          QColor("#080c10"))
    palette.setColor(QPalette.ColorRole.WindowText,      QColor("#d6e4f0"))
    palette.setColor(QPalette.ColorRole.Base,            QColor("#0d1117"))
    palette.setColor(QPalette.ColorRole.AlternateBase,   QColor("#0f1520"))
    palette.setColor(QPalette.ColorRole.Text,            QColor("#d6e4f0"))
    palette.setColor(QPalette.ColorRole.Button,          QColor("#141d2e"))
    palette.setColor(QPalette.ColorRole.ButtonText,      QColor("#d6e4f0"))
    palette.setColor(QPalette.ColorRole.Highlight,       QColor("#1e3a50"))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor("#00d4ff"))
    palette.setColor(QPalette.ColorRole.ToolTipBase,     QColor("#0f1520"))
    palette.setColor(QPalette.ColorRole.ToolTipText,     QColor("#d6e4f0"))
    app.setPalette(palette)
    app.setStyle("Fusion")

    win = MainWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()