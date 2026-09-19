"""
main.py

Desktop GUI (PySide6). This is the ONLY file that should import Qt —
everything it does is: collect input file paths, call pipeline.run_batch()
on a background thread, and render the results it gets back. No
extraction/matching/decision logic lives here. Visual styling lives in
theme.py.

Run with:  python main.py
"""

import os
import sys
import json

from PySide6.QtCore import (
    Qt, QThread, Signal, QObject, QRectF, QSize, QTimer,
    QPropertyAnimation, QEasingCurve,
)
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QListWidget, QListWidgetItem, QLabel, QStackedWidget,
    QTableWidget, QTableWidgetItem, QProgressBar, QFileDialog, QMessageBox,
    QInputDialog, QLineEdit, QSplitter, QGroupBox,
    QButtonGroup, QStyledItemDelegate, QGraphicsDropShadowEffect,
    QGraphicsOpacityEffect, QSpacerItem, QSizePolicy, QScrollArea, QFrame,
)
from PySide6.QtGui import QColor, QPainter, QBrush, QFont, QPixmap, QIcon

import paths
import pipeline
import verifier
import database
import report_export
import notifier
import theme

IMAGE_EXTS = (".jpg", ".jpeg", ".png", ".bmp")
IMAGE_FILTER = "Images (*.jpg *.jpeg *.png *.bmp)"
CONFIG_PATH = os.path.join(paths.app_data_dir(), "config.json")

RESULT_COLUMNS = [
    ("serial_number", "Serial No."),
    ("status", "Status"),
    ("job_card_client", "Client"),
    ("job_card_service_total", "Job Card Total"),
    ("account_book_total", "Account Book Total"),
    ("account_book_line_count", "Ledger Lines"),
    ("source_image", "Source File"),
    ("reason", "Reason"),
]
STATUS_COLUMN_INDEX = 1


def _result_cell_item(key, value):
    """Builds one results-table cell. source_image is stored as a full
    path — shown as just the filename, with the full path available as
    a tooltip, so a batch of many similarly-named files still stays
    readable in the table."""
    if key == "source_image" and value:
        item = QTableWidgetItem(os.path.basename(str(value)))
        item.setToolTip(str(value))
    else:
        item = QTableWidgetItem("" if value is None else str(value))
    return item


class StatusBadgeDelegate(QStyledItemDelegate):
    """Paints the Status column as a rounded, colored pill instead of a
    flat text cell — small touch, but it's the difference between a
    spreadsheet-looking table and a dashboard-looking one."""

    def paint(self, painter, option, index):
        status = index.data()
        colors = theme.STATUS_COLORS.get(status, {"bg": "#E5E7EB", "text": "#374151"})

        painter.save()
        painter.setRenderHint(QPainter.Antialiasing)
        rect = option.rect.adjusted(8, 6, -8, -6)
        painter.setBrush(QBrush(QColor(colors["bg"])))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(QRectF(rect), 9, 9)

        painter.setPen(QColor(colors["text"]))
        font = QFont(painter.font())
        font.setBold(True)
        font.setPointSize(9)
        painter.setFont(font)
        emoji = theme.STATUS_EMOJI.get(status, "")
        label = theme.STATUS_LABELS.get(status, status or "")
        painter.drawText(rect, Qt.AlignCenter, f"{emoji}  {label}".strip())
        painter.restore()


def add_shadow(widget, blur=24, y_offset=4, alpha=30):
    effect = QGraphicsDropShadowEffect(widget)
    effect.setBlurRadius(blur)
    effect.setOffset(0, y_offset)
    effect.setColor(QColor(17, 24, 39, alpha))
    widget.setGraphicsEffect(effect)


def primary_button(text):
    btn = QPushButton(text)
    btn.setProperty("class", "primary")
    btn.setCursor(Qt.PointingHandCursor)
    return btn


def secondary_button(text):
    btn = QPushButton(text)
    btn.setCursor(Qt.PointingHandCursor)
    return btn


def danger_button(text):
    btn = QPushButton(text)
    btn.setProperty("class", "danger")
    btn.setCursor(Qt.PointingHandCursor)
    return btn


def page_header(title, subtitle):
    container = QWidget()
    v = QVBoxLayout(container)
    v.setContentsMargins(0, 0, 0, 0)
    v.setSpacing(2)
    title_label = QLabel(title)
    title_label.setObjectName("PageTitle")
    subtitle_label = QLabel(subtitle)
    subtitle_label.setObjectName("PageSubtitle")
    v.addWidget(title_label)
    v.addWidget(subtitle_label)
    return container


def _thumbnail_item(path):
    """Builds a list item showing a small image thumbnail (when the file
    decodes as an image) next to the filename, instead of a bare path —
    lets a user visually confirm what they actually loaded."""
    item = QListWidgetItem(os.path.basename(path))
    pixmap = QPixmap(path)
    if not pixmap.isNull():
        item.setIcon(QIcon(pixmap.scaled(
            44, 44, Qt.KeepAspectRatio, Qt.SmoothTransformation,
        )))
    item.setToolTip(path)
    item.setData(Qt.UserRole, path)
    return item


class DropListWidget(QListWidget):
    """A QListWidget that also accepts drag-and-drop of image files and
    whole folders, as an alternative to the Add Folder / Add Files
    buttons. Drag state is exposed as a "dragActive" dynamic property so
    theme.py's QSS can highlight the drop zone while a drag is over it."""

    filesDropped = Signal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setIconSize(QSize(44, 44))
        self.setSpacing(2)

    def _set_drag_active(self, active):
        self.setProperty("dragActive", active)
        self.style().unpolish(self)
        self.style().polish(self)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            self._set_drag_active(True)
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        event.acceptProposedAction()

    def dragLeaveEvent(self, event):
        self._set_drag_active(False)

    def dropEvent(self, event):
        self._set_drag_active(False)
        found = []
        for url in event.mimeData().urls():
            local = url.toLocalFile()
            if not local:
                continue
            if os.path.isdir(local):
                found.extend(
                    os.path.join(local, f) for f in sorted(os.listdir(local))
                    if f.lower().endswith(IMAGE_EXTS)
                )
            elif local.lower().endswith(IMAGE_EXTS):
                found.append(local)
        if found:
            self.filesDropped.emit(found)
        event.acceptProposedAction()


class Toast(QWidget):
    """A lightweight, self-dismissing notification that slides/fades in
    near the top-right corner of the window — used for routine feedback
    (files added, export saved, a clean all-verified run) so it doesn't
    interrupt the user the way a modal dialog does. Modal QMessageBoxes
    are kept for anything that needs acknowledgement (errors, abnormal
    verification results)."""

    def __init__(self, parent, text, kind="info", duration_ms=3200):
        super().__init__(parent, Qt.FramelessWindowHint | Qt.Tool | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        self.setAttribute(Qt.WA_DeleteOnClose)

        colors = theme.TOAST_COLORS.get(kind, theme.TOAST_COLORS["info"])

        card = QWidget(self)
        card.setObjectName("Toast")
        card.setStyleSheet(
            f"QWidget#Toast {{ background: {colors['bg']}; "
            f"border: 1px solid {colors['border']}; border-radius: 10px; }}"
        )
        inner = QHBoxLayout(card)
        inner.setContentsMargins(16, 12, 18, 12)
        icon = theme.TOAST_ICONS.get(kind, "")
        label = QLabel(f"{icon}  {text}".strip())
        label.setObjectName("ToastLabel")
        label.setStyleSheet(f"color: {colors['text']}; font-size: 12px; font-weight: 500;")
        label.setWordWrap(True)
        inner.addWidget(label)
        add_shadow(card, blur=28, y_offset=6, alpha=140)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(card)
        self.setMaximumWidth(360)
        self.adjustSize()

        self._position(parent)

        self._opacity = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self._opacity)
        self._fade_in = QPropertyAnimation(self._opacity, b"opacity", self)
        self._fade_in.setDuration(220)
        self._fade_in.setStartValue(0.0)
        self._fade_in.setEndValue(1.0)
        self._fade_in.setEasingCurve(QEasingCurve.OutCubic)

        self.show()
        self._fade_in.start()
        QTimer.singleShot(duration_ms, self._fade_out)

    def _position(self, parent):
        top_right = parent.geometry().topRight()
        anchor = parent.mapToGlobal(top_right)
        self.move(anchor.x() - self.width() - 28, anchor.y() + 56)

    def _fade_out(self):
        anim = QPropertyAnimation(self._opacity, b"opacity", self)
        anim.setDuration(320)
        anim.setStartValue(1.0)
        anim.setEndValue(0.0)
        anim.setEasingCurve(QEasingCurve.InCubic)
        anim.finished.connect(self.close)
        self._fade_out_anim = anim
        anim.start()


STATUS_ORDER = ["VERIFIED", "AMOUNT_MISMATCH", "MISSING_RECORD", "MANUAL_REVIEW"]


class StatTile(QWidget):
    """One colored stat tile ('12 ✅ Verified') for the dashboard summary
    strip. Reads its color/label/emoji straight from theme.py so a status
    always looks the same everywhere it appears (badge, table, tile)."""

    def __init__(self, status, count):
        super().__init__()
        self.setObjectName("StatTile")
        colors = theme.STATUS_COLORS.get(status, {"bg": "#1E2233", "text": theme.TEXT_PRIMARY})

        v = QVBoxLayout(self)
        v.setContentsMargins(16, 12, 16, 12)
        v.setSpacing(2)

        value_label = QLabel(str(count))
        value_label.setObjectName("StatTileValue")
        value_label.setStyleSheet(f"color: {colors['text']};")
        emoji = theme.STATUS_EMOJI.get(status, "")
        label_text = theme.STATUS_LABELS.get(status, status)
        caption_label = QLabel(f"{emoji}  {label_text}".strip())
        caption_label.setObjectName("StatTileLabel")

        v.addWidget(value_label)
        v.addWidget(caption_label)


def build_stat_strip(counts: dict) -> QWidget:
    """A horizontal row of StatTiles for VERIFIED/AMOUNT_MISMATCH/
    MISSING_RECORD/MANUAL_REVIEW, in that fixed order, so a run's shape
    is visible at a glance instead of only as table rows to scroll."""
    row = QWidget()
    h = QHBoxLayout(row)
    h.setContentsMargins(0, 0, 0, 12)
    h.setSpacing(10)
    for status in STATUS_ORDER:
        h.addWidget(StatTile(status, counts.get(status, 0)))
    h.addStretch()
    return row


def fade_in(widget, duration_ms=360):
    """Fades a widget in from 0 to full opacity — used after a batch run
    finishes so the results card doesn't just snap into place."""
    effect = QGraphicsOpacityEffect(widget)
    widget.setGraphicsEffect(effect)
    anim = QPropertyAnimation(effect, b"opacity", widget)
    anim.setDuration(duration_ms)
    anim.setStartValue(0.0)
    anim.setEndValue(1.0)
    anim.setEasingCurve(QEasingCurve.OutCubic)
    widget._fade_anim = anim  # keep a reference so it isn't garbage-collected mid-flight
    anim.start()


# ----------------------------------------------------------------------
# API key handling — lazy, GUI-friendly.
# ----------------------------------------------------------------------
def load_saved_api_key() -> str | None:
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r") as f:
                return json.load(f).get("gemini_api_key")
        except (json.JSONDecodeError, OSError):
            return None
    return None


def save_api_key(key: str) -> None:
    with open(CONFIG_PATH, "w") as f:
        json.dump({"gemini_api_key": key}, f)


def ensure_api_key(parent) -> bool:
    if os.environ.get("GEMINI_API_KEY"):
        return True

    saved = load_saved_api_key()
    if saved:
        os.environ["GEMINI_API_KEY"] = saved
        return True

    key, ok = QInputDialog.getText(
        parent,
        "Gemini API Key Required",
        "Enter your Gemini API key\n(get a free one at https://aistudio.google.com/app/apikey):",
        QLineEdit.Normal,
    )
    if ok and key.strip():
        os.environ["GEMINI_API_KEY"] = key.strip()
        save_api_key(key.strip())
        import vision_extractor
        vision_extractor.reset_client()
        return True
    return False


# ----------------------------------------------------------------------
# Background worker so batch processing never freezes the UI thread.
# ----------------------------------------------------------------------
class BatchWorker(QObject):
    progress = Signal(int, int, str)
    finished = Signal(dict)
    failed = Signal(str)

    def __init__(self, job_card_paths, account_book_paths, confidence_threshold):
        super().__init__()
        self.job_card_paths = job_card_paths
        self.account_book_paths = account_book_paths
        self.confidence_threshold = confidence_threshold
        self._stop_requested = False

    def request_stop(self):
        """Called from the GUI thread when the user clicks Stop. Just
        flips a plain bool — CPython's GIL makes a single bool flag safe
        to read/write across threads without a lock for this purpose."""
        self._stop_requested = True

    def run(self):
        try:
            outcome = pipeline.run_batch(
                self.job_card_paths,
                self.account_book_paths,
                confidence_threshold=self.confidence_threshold,
                progress_callback=lambda done, total, msg: self.progress.emit(done, total, msg),
                should_stop=lambda: self._stop_requested,
            )
            self.finished.emit(outcome)
        except Exception as e:
            self.failed.emit(str(e))


# ----------------------------------------------------------------------
# "New Run" page
# ----------------------------------------------------------------------
class NewRunPage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.job_card_paths = []
        self.account_book_paths = []
        self.last_results = []
        self.thread = None
        self.worker = None

        page_layout = QVBoxLayout(self)
        page_layout.setContentsMargins(0, 0, 0, 0)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.viewport().setStyleSheet(f"background: {theme.APP_BG};")
        page_layout.addWidget(scroll)

        content = QWidget()
        content.setObjectName("ContentArea")
        scroll.setWidget(content)
        outer = QVBoxLayout(content)
        outer.setContentsMargins(28, 24, 28, 24)
        outer.setSpacing(16)

        outer.addWidget(page_header(
            "New Verification Run",
            "Add job card and account book images, then run the check.",
        ))

        input_splitter = QSplitter(Qt.Horizontal)
        input_splitter.setChildrenCollapsible(False)
        job_card_group = self._build_input_group("Job Cards", "job_card_paths", "job_card_list")
        account_group = self._build_input_group("Account Book Pages", "account_book_paths", "account_book_list")
        add_shadow(job_card_group)
        add_shadow(account_group)
        input_splitter.addWidget(job_card_group)
        input_splitter.addWidget(account_group)
        input_splitter.setSizes([1, 1])
        outer.addWidget(input_splitter)

        controls_card = QGroupBox("Run Settings")
        add_shadow(controls_card)
        controls_layout = QVBoxLayout(controls_card)

        settings_row = QHBoxLayout()
        conf_label = QLabel(
            f"Confidence threshold: {verifier.CONFIDENCE_THRESHOLD_DEFAULT:.0%} "
            "(fixed — anything the AI is less sure of than this is always sent to Manual Review)"
        )
        conf_label.setObjectName("PageSubtitle")
        settings_row.addWidget(conf_label)
        settings_row.addStretch()
        controls_layout.addLayout(settings_row)

        run_row = QHBoxLayout()
        self.run_button = primary_button("▶️  Run Verification")
        self.run_button.clicked.connect(self.start_run)
        run_row.addWidget(self.run_button)
        self.stop_button = danger_button("⏹️ Stop")
        self.stop_button.clicked.connect(self.stop_run)
        self.stop_button.setEnabled(False)
        run_row.addWidget(self.stop_button)
        self.export_excel_button = secondary_button("📊 Export Excel")
        self.export_excel_button.clicked.connect(self.export_excel)
        self.export_excel_button.setEnabled(False)
        run_row.addWidget(self.export_excel_button)
        self.export_pdf_button = secondary_button("📄 Export PDF")
        self.export_pdf_button.clicked.connect(self.export_pdf)
        self.export_pdf_button.setEnabled(False)
        run_row.addWidget(self.export_pdf_button)
        run_row.addStretch()
        controls_layout.addLayout(run_row)

        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(False)
        controls_layout.addWidget(self.progress_bar)
        self.status_label = QLabel("Ready.")
        self.status_label.setObjectName("StatusLine")
        controls_layout.addWidget(self.status_label)

        outer.addWidget(controls_card)

        results_card = QGroupBox("Results")
        add_shadow(results_card)
        results_layout = QVBoxLayout(results_card)
        self.stat_strip_container = QVBoxLayout()
        self.stat_strip_container.setContentsMargins(0, 0, 0, 0)
        results_layout.addLayout(self.stat_strip_container)
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(len(RESULT_COLUMNS))
        self.results_table.setHorizontalHeaderLabels([label for _, label in RESULT_COLUMNS])
        self.results_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.results_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.results_table.verticalHeader().setVisible(False)
        self.results_table.setShowGrid(False)
        self.results_table.verticalHeader().setDefaultSectionSize(38)
        self.results_table.setItemDelegateForColumn(STATUS_COLUMN_INDEX, StatusBadgeDelegate())
        self.results_table.setMinimumHeight(320)
        results_layout.addWidget(self.results_table)
        self.results_card = results_card
        outer.addWidget(results_card)

    def _build_input_group(self, title, path_attr, list_attr):
        group = QGroupBox(title)
        v = QVBoxLayout(group)

        list_widget = DropListWidget()
        list_widget.filesDropped.connect(lambda paths: self._add_paths(path_attr, list_widget, paths))
        setattr(self, list_attr, list_widget)
        v.addWidget(list_widget)

        hint = QLabel("📥 Drag & drop images or a folder here")
        hint.setObjectName("PageSubtitle")
        v.addWidget(hint)

        btn_row = QHBoxLayout()
        add_folder_btn = secondary_button("📁 Add Folder")
        add_files_btn = secondary_button("🖼️ Add Files")
        clear_btn = secondary_button("🗑️ Clear")
        btn_row.addWidget(add_folder_btn)
        btn_row.addWidget(add_files_btn)
        btn_row.addWidget(clear_btn)
        v.addLayout(btn_row)

        add_folder_btn.clicked.connect(lambda: self._add_folder(path_attr, list_widget))
        add_files_btn.clicked.connect(lambda: self._add_files(path_attr, list_widget))
        clear_btn.clicked.connect(lambda: self._clear(path_attr, list_widget))
        return group

    def _add_paths(self, path_attr, list_widget, new_paths):
        existing = set(getattr(self, path_attr))
        added = [p for p in new_paths if p not in existing]
        if not added:
            return
        getattr(self, path_attr).extend(added)
        for p in added:
            list_widget.addItem(_thumbnail_item(p))
        self.main_window.show_toast(f"Added {len(added)} image(s).", kind="info")

    def _add_folder(self, path_attr, list_widget):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if not folder:
            return
        found = sorted(
            os.path.join(folder, f) for f in os.listdir(folder)
            if f.lower().endswith(IMAGE_EXTS)
        )
        self._add_paths(path_attr, list_widget, found)

    def _add_files(self, path_attr, list_widget):
        files, _ = QFileDialog.getOpenFileNames(self, "Select Images", "", IMAGE_FILTER)
        if not files:
            return
        self._add_paths(path_attr, list_widget, files)

    def _clear(self, path_attr, list_widget):
        setattr(self, path_attr, [])
        list_widget.clear()

    def start_run(self):
        if not self.job_card_paths:
            QMessageBox.warning(self, "No Job Cards", "Add at least one job card image first.")
            return
        if not self.account_book_paths:
            QMessageBox.warning(self, "No Account Book Pages", "Add at least one account book image first.")
            return
        if not ensure_api_key(self):
            return

        self.run_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.export_excel_button.setEnabled(False)
        self.export_pdf_button.setEnabled(False)
        self.progress_bar.setValue(0)
        self.progress_bar.setMaximum(len(self.job_card_paths) + len(self.account_book_paths))
        self.status_label.setText("Processing...")

        self.thread = QThread()
        self.worker = BatchWorker(
            list(self.job_card_paths),
            list(self.account_book_paths),
            verifier.CONFIDENCE_THRESHOLD_DEFAULT,
        )
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.progress.connect(self.on_progress)
        self.worker.finished.connect(self.on_finished)
        self.worker.failed.connect(self.on_failed)
        self.worker.finished.connect(self.thread.quit)
        self.worker.failed.connect(self.thread.quit)
        self.thread.start()

    def stop_run(self):
        if self.worker:
            self.worker.request_stop()
        self.stop_button.setEnabled(False)
        self.status_label.setText("Stopping... (finishing the image currently in progress)")

    def on_progress(self, done, total, message):
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(done)
        self.status_label.setText(message)

    def on_finished(self, outcome):
        self.run_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        results = outcome["results"]
        self.last_results = results
        failed = outcome["failed_extractions"]
        stopped_early = outcome.get("stopped_early", False)

        self.render_results(results)
        self.export_excel_button.setEnabled(bool(results))
        self.export_pdf_button.setEnabled(bool(results))
        fade_in(self.results_card)

        if stopped_early:
            status_text = f"Stopped early by user. {len(results)} result(s) saved as Run #{outcome['run_id']}."
        else:
            status_text = f"Done. Run #{outcome['run_id']} saved."
        if failed:
            status_text += f" {len(failed)} image(s) failed to extract — see popup."
        self.status_label.setText(status_text)

        if failed:
            failed_text = "\n".join(f"  • {f['image']}: {f['error']}" for f in failed)
            QMessageBox.warning(
                self, "Some Images Failed to Process",
                f"{len(failed)} image(s) could not be read/extracted:\n\n{failed_text}",
            )

        if stopped_early:
            self.main_window.show_toast(
                f"Stopped early — {len(results)} result(s) saved as Run #{outcome['run_id']}.",
                kind="info",
            )
        else:
            abnormal_count = sum(1 for r in results if r.get("status") in notifier.ABNORMAL_STATUSES)
            if results and not failed and abnormal_count == 0:
                self.main_window.show_toast(
                    f"All {len(results)} job card(s) verified. Run #{outcome['run_id']} saved.",
                    kind="success",
                )
            else:
                notifier.show_batch_summary_popup(results, parent=self)
        self.main_window.refresh_history_page()

    def on_failed(self, error_message):
        self.run_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.status_label.setText("Run failed.")
        QMessageBox.critical(self, "Run Failed", error_message)

    def _clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def render_results(self, results):
        self._clear_layout(self.stat_strip_container)
        self.stat_strip_container.addWidget(build_stat_strip(pipeline.summarize(results)))

        self.results_table.setRowCount(len(results))
        for row_idx, result in enumerate(results):
            for col_idx, (key, _) in enumerate(RESULT_COLUMNS):
                item = _result_cell_item(key, result.get(key))
                if col_idx != STATUS_COLUMN_INDEX:
                    item.setForeground(QColor(theme.TEXT_PRIMARY))
                self.results_table.setItem(row_idx, col_idx, item)
        self.results_table.resizeColumnsToContents()
        self.results_table.horizontalHeader().setStretchLastSection(True)

    def export_excel(self):
        path, _ = QFileDialog.getSaveFileName(self, "Export Excel", "verification_report.xlsx", "Excel Files (*.xlsx)")
        if path:
            report_export.export_excel(self.last_results, path)
            self.main_window.show_toast(f"Excel report saved to {path}", kind="success")

    def export_pdf(self):
        path, _ = QFileDialog.getSaveFileName(self, "Export PDF", "verification_report.pdf", "PDF Files (*.pdf)")
        if path:
            report_export.export_pdf(self.last_results, path)
            self.main_window.show_toast(f"PDF report saved to {path}", kind="success")


# ----------------------------------------------------------------------
# "History" page
# ----------------------------------------------------------------------
class HistoryPage(QWidget):
    def __init__(self):
        super().__init__()
        outer = QVBoxLayout(self)
        outer.setContentsMargins(28, 24, 28, 24)
        outer.setSpacing(16)

        outer.addWidget(page_header("Run History", "Browse every past verification run."))

        splitter = QSplitter(Qt.Horizontal)

        self.runs_list = QListWidget()
        self.runs_list.currentRowChanged.connect(self.show_run)
        splitter.addWidget(self.runs_list)

        results_pane = QWidget()
        results_pane_layout = QVBoxLayout(results_pane)
        results_pane_layout.setContentsMargins(0, 0, 0, 0)
        self.stat_strip_container = QVBoxLayout()
        self.stat_strip_container.setContentsMargins(0, 0, 0, 0)
        results_pane_layout.addLayout(self.stat_strip_container)

        self.results_table = QTableWidget()
        self.results_table.setColumnCount(len(RESULT_COLUMNS))
        self.results_table.setHorizontalHeaderLabels([label for _, label in RESULT_COLUMNS])
        self.results_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.results_table.verticalHeader().setVisible(False)
        self.results_table.setShowGrid(False)
        self.results_table.verticalHeader().setDefaultSectionSize(38)
        self.results_table.setItemDelegateForColumn(STATUS_COLUMN_INDEX, StatusBadgeDelegate())
        results_pane_layout.addWidget(self.results_table)
        splitter.addWidget(results_pane)

        splitter.setSizes([260, 740])
        outer.addWidget(splitter, stretch=1)
        self.runs = []
        self.refresh()

    def refresh(self):
        database.init_db()
        self.runs = database.list_runs()
        self.runs_list.clear()
        for run in self.runs:
            counts = run["status_counts"]
            summary = "  ·  ".join(f"{k}: {v}" for k, v in counts.items()) or "no results"
            self.runs_list.addItem(f"Run #{run['run_id']}\n{run['run_timestamp']}\n{summary}")

    def _clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def show_run(self, row_idx):
        if row_idx < 0 or row_idx >= len(self.runs):
            self.results_table.setRowCount(0)
            self._clear_layout(self.stat_strip_container)
            return
        run = self.runs[row_idx]
        run_id = run["run_id"]
        self._clear_layout(self.stat_strip_container)
        self.stat_strip_container.addWidget(build_stat_strip(run["status_counts"]))

        results = database.get_run_results(run_id)
        self.results_table.setRowCount(len(results))
        for row_idx2, result in enumerate(results):
            for col_idx, (key, _) in enumerate(RESULT_COLUMNS):
                item = _result_cell_item(key, result.get(key))
                self.results_table.setItem(row_idx2, col_idx, item)
        self.results_table.resizeColumnsToContents()
        self.results_table.horizontalHeader().setStretchLastSection(True)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LedgerLens — Job Card & Account Book Reconciliation")
        self.setWindowIcon(theme.make_app_icon())
        self.resize(1180, 760)
        self.setMinimumSize(900, 600)

        central = QWidget()
        central.setObjectName("ContentArea")
        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(self._build_sidebar())

        self.stack = QStackedWidget()
        self.new_run_page = NewRunPage(self)
        self.history_page = HistoryPage()
        self.stack.addWidget(self.new_run_page)
        self.stack.addWidget(self.history_page)
        root.addWidget(self.stack, stretch=1)

        self.setCentralWidget(central)

    def _build_sidebar(self):
        sidebar = QWidget()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(220)
        v = QVBoxLayout(sidebar)
        v.setContentsMargins(18, 24, 18, 18)
        v.setSpacing(4)

        title = QLabel("✨ LedgerLens")
        title.setObjectName("AppTitle")
        title.setWordWrap(True)
        subtitle = QLabel("Job Card ↔ Account Book")
        subtitle.setObjectName("AppSubtitle")
        v.addWidget(title)
        v.addWidget(subtitle)
        v.addSpacing(28)

        self.nav_group = QButtonGroup(self)
        self.nav_group.setExclusive(True)

        new_run_btn = QPushButton("🆕  New Run")
        new_run_btn.setObjectName("NavButton")
        new_run_btn.setCheckable(True)
        new_run_btn.setChecked(True)
        new_run_btn.setCursor(Qt.PointingHandCursor)
        new_run_btn.clicked.connect(lambda: self.switch_page(0))

        history_btn = QPushButton("🕘  History")
        history_btn.setObjectName("NavButton")
        history_btn.setCheckable(True)
        history_btn.setCursor(Qt.PointingHandCursor)
        history_btn.clicked.connect(lambda: self.switch_page(1))

        self.nav_group.addButton(new_run_btn)
        self.nav_group.addButton(history_btn)
        v.addWidget(new_run_btn)
        v.addWidget(history_btn)

        v.addItem(QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding))

        footer = QLabel("⚡ v1.0 · Gemini Vision")
        footer.setObjectName("AppSubtitle")
        v.addWidget(footer)

        return sidebar

    def switch_page(self, index):
        self.stack.setCurrentIndex(index)
        if index == 1:
            self.history_page.refresh()

    def refresh_history_page(self):
        self.history_page.refresh()

    def show_toast(self, text, kind="info"):
        self._toast = Toast(self, text, kind=kind)


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(theme.STYLESHEET)
    window = MainWindow()
    window.showMaximized()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
