"""
theme.py

Central design system for the desktop app: color tokens + one QSS
stylesheet applied once at startup. Keeping this separate from main.py
means the visual language (colors, spacing, radii) is defined in exactly
one place instead of scattered across widget code.

Palette: "aurora dark" — a near-black charcoal/navy base with a two-tone
signature accent (violet for primary actions, cyan for highlights/glow),
chosen so the app doesn't read as generic light-mode business software.
"""

# ----------------------------------------------------------------------
# Accent
# ----------------------------------------------------------------------
VIOLET = "#8B5CF6"
VIOLET_DARK = "#7C3AED"
VIOLET_LIGHT = "#2A2145"
CYAN = "#22D3EE"

# ----------------------------------------------------------------------
# Surfaces
# ----------------------------------------------------------------------
SIDEBAR_BG = "#0A0B10"
SIDEBAR_TEXT = "#8A8FA3"
SIDEBAR_TEXT_ACTIVE = "#FFFFFF"
SIDEBAR_HOVER = "#171A26"

APP_BG = "#0E0F16"
CARD_BG = "#151824"
CARD_BG_HOVER = "#1B1F2E"
CARD_BORDER = "#262B3D"

TEXT_PRIMARY = "#F1F2F6"
TEXT_SECONDARY = "#8A8FA3"

STATUS_COLORS = {
    "VERIFIED": {"bg": "#122B1F", "text": "#4ADE80"},
    "AMOUNT_MISMATCH": {"bg": "#331420", "text": "#FB7185"},
    "MISSING_RECORD": {"bg": "#332711", "text": "#FBBF24"},
    "MANUAL_REVIEW": {"bg": "#1E2233", "text": "#C4B5FD"},
}

STATUS_LABELS = {
    "VERIFIED": "Verified",
    "AMOUNT_MISMATCH": "Mismatch",
    "MISSING_RECORD": "Missing",
    "MANUAL_REVIEW": "Review",
}

STATUS_EMOJI = {
    "VERIFIED": "✅",
    "AMOUNT_MISMATCH": "⚠️",
    "MISSING_RECORD": "❓",
    "MANUAL_REVIEW": "\U0001F50E",
}

TOAST_COLORS = {
    "success": {"bg": "#122B1F", "border": "#22C55E", "text": "#4ADE80"},
    "info": {"bg": "#171A2E", "border": VIOLET, "text": "#E9E6FF"},
}

TOAST_ICONS = {
    "success": "✅",
    "info": "\U0001F4E1",
}

FONT_FAMILY = "Segoe UI, -apple-system, Arial, sans-serif"

STYLESHEET = f"""
* {{
    font-family: {FONT_FAMILY};
}}

QMainWindow, QWidget#ContentArea {{
    background: {APP_BG};
}}

QScrollArea {{
    border: none;
    background: transparent;
}}

QWidget#Sidebar {{
    background: {SIDEBAR_BG};
    border-right: 1px solid {CARD_BORDER};
}}

QLabel#AppTitle {{
    color: {SIDEBAR_TEXT_ACTIVE};
    font-size: 16px;
    font-weight: 600;
}}

QLabel#AppSubtitle {{
    color: {SIDEBAR_TEXT};
    font-size: 11px;
}}

QPushButton#NavButton {{
    background: transparent;
    color: {SIDEBAR_TEXT};
    border: none;
    text-align: left;
    padding: 11px 18px;
    font-size: 13px;
    font-weight: 500;
    border-radius: 8px;
}}

QPushButton#NavButton:hover {{
    background: {SIDEBAR_HOVER};
    color: {SIDEBAR_TEXT_ACTIVE};
}}

QPushButton#NavButton:checked {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {VIOLET_DARK}, stop:1 {VIOLET});
    color: {SIDEBAR_TEXT_ACTIVE};
}}

QLabel#PageTitle {{
    color: {TEXT_PRIMARY};
    font-size: 22px;
    font-weight: 700;
}}

QLabel#PageSubtitle {{
    color: {TEXT_SECONDARY};
    font-size: 13px;
}}

QGroupBox {{
    background: {CARD_BG};
    border: 1px solid {CARD_BORDER};
    border-radius: 12px;
    margin-top: 14px;
    padding: 14px;
    font-weight: 600;
    color: {TEXT_PRIMARY};
    font-size: 13px;
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 6px;
    color: {TEXT_PRIMARY};
}}

QPushButton {{
    background: {CARD_BG_HOVER};
    color: {TEXT_PRIMARY};
    border: 1px solid {CARD_BORDER};
    border-radius: 7px;
    padding: 7px 14px;
    font-size: 12px;
    font-weight: 500;
}}

QPushButton:hover {{
    background: #232838;
    border-color: {VIOLET};
}}

QPushButton:disabled {{
    color: #4B5065;
    background: #14151D;
    border-color: {CARD_BORDER};
}}

QPushButton[class="primary"] {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {VIOLET_DARK}, stop:1 {VIOLET});
    color: white;
    border: none;
    padding: 10px 22px;
    font-size: 13px;
    font-weight: 600;
}}

QPushButton[class="primary"]:hover {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {VIOLET}, stop:1 {CYAN});
}}

QPushButton[class="primary"]:disabled {{
    background: #2C2A3E;
    color: #6B6F82;
}}

QPushButton[class="danger"] {{
    background: #331420;
    color: #FB7185;
    border: 1px solid #4C1D2B;
    padding: 10px 22px;
    font-size: 13px;
    font-weight: 600;
}}

QPushButton[class="danger"]:hover {{
    background: #4C1D2B;
    border-color: #FB7185;
}}

QPushButton[class="danger"]:disabled {{
    background: #1A1B24;
    color: #4B5065;
    border-color: {CARD_BORDER};
}}

QListWidget {{
    background: {CARD_BG};
    border: 1px dashed {CARD_BORDER};
    border-radius: 8px;
    padding: 4px;
    font-size: 12px;
    color: {TEXT_PRIMARY};
}}

QListWidget[dragActive="true"] {{
    border: 2px dashed {CYAN};
    background: {VIOLET_LIGHT};
}}

QListWidget::item {{
    padding: 6px 8px;
    border-radius: 5px;
}}

QListWidget::item:selected {{
    background: {VIOLET_LIGHT};
    color: {CYAN};
}}

QListWidget::item:hover {{
    background: {CARD_BG_HOVER};
}}

QTableWidget {{
    background: {CARD_BG};
    border: 1px solid {CARD_BORDER};
    border-radius: 10px;
    gridline-color: {CARD_BORDER};
    font-size: 12px;
    color: {TEXT_PRIMARY};
    selection-background-color: {VIOLET_LIGHT};
    selection-color: {TEXT_PRIMARY};
}}

QTableWidget::item {{
    padding: 6px;
}}

QHeaderView::section {{
    background: #10121B;
    color: {TEXT_SECONDARY};
    border: none;
    border-bottom: 1px solid {CARD_BORDER};
    padding: 8px;
    font-weight: 600;
    font-size: 11px;
}}

QProgressBar {{
    background: #1B1E2B;
    border: none;
    border-radius: 6px;
    height: 12px;
    text-align: center;
    font-size: 10px;
    color: {TEXT_SECONDARY};
}}

QProgressBar::chunk {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {VIOLET_DARK}, stop:1 {CYAN});
    border-radius: 6px;
}}

QDoubleSpinBox, QLineEdit {{
    background: {CARD_BG_HOVER};
    border: 1px solid {CARD_BORDER};
    border-radius: 6px;
    padding: 5px 8px;
    color: {TEXT_PRIMARY};
    font-size: 12px;
}}

QDoubleSpinBox:focus, QLineEdit:focus {{
    border: 1px solid {VIOLET};
}}

QComboBox {{
    background: {CARD_BG_HOVER};
    border: 1px solid {CARD_BORDER};
    border-radius: 6px;
    padding: 5px 8px;
    color: {TEXT_PRIMARY};
    font-size: 12px;
}}

QComboBox:hover {{
    border-color: {VIOLET};
}}

QComboBox::drop-down {{
    border: none;
}}

QComboBox QAbstractItemView {{
    background: {CARD_BG};
    border: 1px solid {CARD_BORDER};
    color: {TEXT_PRIMARY};
    outline: none;
    selection-background-color: {VIOLET_LIGHT};
    selection-color: {TEXT_PRIMARY};
}}

QLabel {{
    color: {TEXT_PRIMARY};
}}

QLabel#StatusLine {{
    color: {TEXT_SECONDARY};
    font-size: 12px;
}}

QSplitter::handle {{
    background: {APP_BG};
    width: 10px;
}}

QScrollBar:vertical {{
    background: transparent;
    width: 10px;
}}

QScrollBar::handle:vertical {{
    background: #363B4E;
    border-radius: 5px;
    min-height: 30px;
}}

QScrollBar::handle:vertical:hover {{
    background: {VIOLET};
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}

QMessageBox {{
    background: {CARD_BG};
}}

QMessageBox QLabel {{
    color: {TEXT_PRIMARY};
}}

QInputDialog {{
    background: {CARD_BG};
}}

QToolTip {{
    background: {CARD_BG_HOVER};
    color: {TEXT_PRIMARY};
    border: 1px solid {CARD_BORDER};
    padding: 4px 8px;
    border-radius: 4px;
}}

QWidget#StatTile {{
    background: {CARD_BG_HOVER};
    border: 1px solid {CARD_BORDER};
    border-radius: 10px;
}}

QLabel#StatTileValue {{
    font-size: 22px;
    font-weight: 700;
}}

QLabel#StatTileLabel {{
    color: {TEXT_SECONDARY};
    font-size: 11px;
    font-weight: 600;
}}

QWidget#Toast {{
    border-radius: 10px;
}}

QLabel#ToastLabel {{
    color: {TEXT_PRIMARY};
    font-size: 12px;
    font-weight: 500;
}}
"""


def build_palette():
    """
    A QPalette built from the same color tokens as STYLESHEET above. QSS
    styles most widgets fully, but a few things fall outside it — some
    disabled-state colors, tooltips, and parts of native dialogs — and
    those fall back to Qt's default palette, which on Windows/macOS is
    partly derived from the OS's light/dark setting. Setting this
    palette explicitly (in main.py, alongside app.setStyle("Fusion"))
    means those leftover bits match the app's own "aurora dark" colors
    regardless of the system theme.
    """
    from PySide6.QtGui import QPalette, QColor

    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(APP_BG))
    palette.setColor(QPalette.WindowText, QColor(TEXT_PRIMARY))
    palette.setColor(QPalette.Base, QColor(CARD_BG))
    palette.setColor(QPalette.AlternateBase, QColor(CARD_BG_HOVER))
    palette.setColor(QPalette.ToolTipBase, QColor(CARD_BG_HOVER))
    palette.setColor(QPalette.ToolTipText, QColor(TEXT_PRIMARY))
    palette.setColor(QPalette.Text, QColor(TEXT_PRIMARY))
    palette.setColor(QPalette.Button, QColor(CARD_BG_HOVER))
    palette.setColor(QPalette.ButtonText, QColor(TEXT_PRIMARY))
    palette.setColor(QPalette.BrightText, QColor("#FFFFFF"))
    palette.setColor(QPalette.Highlight, QColor(VIOLET))
    palette.setColor(QPalette.HighlightedText, QColor("#FFFFFF"))
    palette.setColor(QPalette.PlaceholderText, QColor(TEXT_SECONDARY))
    palette.setColor(QPalette.Disabled, QPalette.Text, QColor("#4B5065"))
    palette.setColor(QPalette.Disabled, QPalette.ButtonText, QColor("#4B5065"))
    palette.setColor(QPalette.Disabled, QPalette.WindowText, QColor("#4B5065"))
    return palette


def make_app_icon():
    """Generates the app's icon in code: a rounded square with a
    violet-to-cyan gradient and a white checkmark, matching the app's
    dark "aurora" palette. No external image asset needed."""
    from PySide6.QtGui import QPixmap, QPainter, QColor, QPen, QIcon, QLinearGradient
    from PySide6.QtCore import Qt, QRectF, QPointF

    size = 128
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)

    gradient = QLinearGradient(0, 0, size, size)
    gradient.setColorAt(0.0, QColor(VIOLET_DARK))
    gradient.setColorAt(1.0, QColor(CYAN))
    painter.setBrush(gradient)
    painter.setPen(Qt.NoPen)
    painter.drawRoundedRect(QRectF(4, 4, size - 8, size - 8), 28, 28)

    pen = QPen(QColor("white"))
    pen.setWidth(10)
    pen.setCapStyle(Qt.RoundCap)
    pen.setJoinStyle(Qt.RoundJoin)
    painter.setPen(pen)
    painter.drawPolyline([
        QPointF(size * 0.28, size * 0.52),
        QPointF(size * 0.44, size * 0.68),
        QPointF(size * 0.74, size * 0.34),
    ])
    painter.end()
    return QIcon(pixmap)
