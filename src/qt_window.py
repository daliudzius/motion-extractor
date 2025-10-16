"""
PyQt5 window and worker implementation for motion extraction.

This module replaces separate OpenCV and control windows with a single PyQt5 GUI
that shows the motion-extracted video feed and exposes delay controls below the
preview.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from typing import Optional

import cv2
import numpy as np
from PyQt5.QtCore import QObject, Qt, QThread, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QShortcut,
    QSpinBox,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)

from camera_stream import CameraStream
from motion_extractor import MotionExtractor


@dataclass
class CameraSettings:
    """Typed container for camera configuration values."""

    source: int | str
    width: Optional[int]
    height: Optional[int]


@dataclass
class MotionSettings:
    """Typed container for motion extraction configuration values."""

    fps: int
    delay_frames: int
    blend_alpha: float


class MotionExtractorWorker(QObject):
    """Background worker that owns camera capture and motion processing."""

    frame_ready = pyqtSignal(QImage)
    status_message = pyqtSignal(str)
    error_message = pyqtSignal(str)
    fps_detected = pyqtSignal(int)
    camera_ready = pyqtSignal(str)

    def __init__(
        self,
        camera_settings: CameraSettings,
        motion_settings: MotionSettings,
    ) -> None:
        super().__init__()
        self._camera_settings = camera_settings
        self._motion_settings = motion_settings

        self._camera: Optional[CameraStream] = None
        self._extractor: Optional[MotionExtractor] = None
        self._running = False
        self._camera_name = ""
        self._fps = motion_settings.fps

    @pyqtSlot()
    def run(self) -> None:
        """Begin the capture loop once the worker thread starts."""

        if self._running:
            return

        self._running = True
        self.status_message.emit("Starting camera stream...")

        try:
            self._camera = CameraStream(
                source=self._camera_settings.source,
                width=self._camera_settings.width,
                height=self._camera_settings.height,
            )

            if not self._camera.start():
                self.error_message.emit("Could not open camera source")
                self._running = False
                return

            detected_fps = int(self._camera.get_fps()) or self._motion_settings.fps
            if detected_fps <= 0:
                detected_fps = self._motion_settings.fps
            self.fps_detected.emit(detected_fps)
            self._fps = detected_fps

            self._camera_name = self._camera.get_device_name()
            if self._camera_name:
                self.camera_ready.emit(self._camera_name)

            initial_delay_frames = max(0, self._motion_settings.delay_frames)
            delay_seconds = initial_delay_frames / detected_fps if detected_fps else 0

            self._extractor = MotionExtractor(
                delay_seconds=delay_seconds,
                fps=detected_fps,
                blend_alpha=self._motion_settings.blend_alpha,
            )

            while self._running:
                frame = self._camera.read_frame()
                if frame is None:
                    self.status_message.emit("End of stream")
                    break

                try:
                    self._extractor.add_frame(frame)
                except ValueError as exc:
                    # Skip invalid frames but keep the loop alive.
                    self.status_message.emit(f"Frame dropped: {exc}")
                    continue

                motion_frame = self._extractor.extract_motion()
                if motion_frame is None:
                    continue

                # No overlay - status bar shows all info
                qt_image = self._convert_to_qimage(motion_frame)
                self.frame_ready.emit(qt_image)

                QThread.msleep(1)

        except Exception as exc:  # pylint: disable=broad-except
            self.error_message.emit(str(exc))
        finally:
            self._shutdown()
            self._running = False
            self.status_message.emit("Worker stopped")

    @pyqtSlot(int)
    def set_delay_frames(self, frames: int) -> None:
        """Update the delay setting from the UI spinbox."""

        if not self._extractor:
            return

        self._extractor.update_delay_frames(frames)

    @pyqtSlot()
    def stop(self) -> None:
        """Signal the capture loop to exit."""

        self._running = False

    def _shutdown(self) -> None:
        """Release camera resources and notify OpenCV."""

        if self._camera is not None:
            self._camera.stop()
            self._camera = None

        cv2.destroyAllWindows()

    @staticmethod
    def _convert_to_qimage(frame: np.ndarray) -> QImage:
        """Convert a BGR OpenCV frame into a QImage copy for display."""

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        height, width, channel_count = rgb_frame.shape
        bytes_per_line = channel_count * width
        image = QImage(
            rgb_frame.data,
            width,
            height,
            bytes_per_line,
            QImage.Format_RGB888,
        )
        # Copy to detach from the numpy buffer owned by OpenCV.
        return image.copy()


class MotionExtractorWindow(QMainWindow):
    """Main window that hosts the video preview and delay controls."""

    def __init__(
        self,
        camera_settings: CameraSettings,
        motion_settings: MotionSettings,
        window_title: str,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)

        self.setWindowTitle(window_title)
        self._camera_settings = camera_settings
        self._motion_settings = motion_settings
        self._window_title = window_title
        self._camera_name = ""
        self._detected_fps = motion_settings.fps

        self._video_label = QLabel("Starting camera...")
        self._video_label.setAlignment(Qt.AlignCenter)
        self._video_label.setMinimumSize(640, 480)

        self._delay_label = QLabel(self._format_delay_seconds(motion_settings.delay_frames))
        self._delay_spinbox = QSpinBox()
        self._delay_spinbox.setRange(0, motion_settings.fps * 10)
        self._delay_spinbox.setValue(motion_settings.delay_frames)
        self._delay_spinbox.setSuffix(" frames")
        self._delay_spinbox.setSingleStep(1)
        self._delay_spinbox.setAccelerated(True)

        controls_row = QWidget()
        controls_layout = QHBoxLayout(controls_row)
        controls_layout.setContentsMargins(0, 0, 0, 0)
        controls_layout.addWidget(QLabel("Delay:"))
        controls_layout.addWidget(self._delay_spinbox)
        controls_layout.addWidget(self._delay_label)
        controls_layout.addStretch()

        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        main_layout.addWidget(self._video_label)
        main_layout.addWidget(controls_row)
        self.setCentralWidget(central_widget)

        self._status_bar = QStatusBar()
        self.setStatusBar(self._status_bar)

        self._thread = QThread(self)
        self._worker = MotionExtractorWorker(camera_settings, motion_settings)
        self._worker.moveToThread(self._thread)

        self._thread.started.connect(self._worker.run)
        self._worker.frame_ready.connect(self._update_frame)
        self._worker.status_message.connect(self._handle_status_message)
        self._worker.error_message.connect(self._handle_error)
        self._worker.fps_detected.connect(self._update_fps)
        self._worker.camera_ready.connect(self._update_camera_name)
        self._delay_spinbox.valueChanged.connect(self._handle_delay_change)

        # Provide keyboard shortcuts for quick exit.
        QShortcut(Qt.CTRL + Qt.Key_Q, self, activated=self.close)
        QShortcut(Qt.Key_Escape, self, activated=self.close)

        self._thread.start()

    def closeEvent(self, event) -> None:  # type: ignore[override]
        """Ensure the worker stops before the window closes."""

        if self._thread.isRunning():
            self._worker.stop()
            self._thread.quit()
            self._thread.wait(2000)

        super().closeEvent(event)

    @pyqtSlot(QImage)
    def _update_frame(self, image: QImage) -> None:
        """Update the QLabel pixmap when the worker emits a new frame."""

        pixmap = QPixmap.fromImage(image)
        scaled = pixmap.scaled(
            self._video_label.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation,
        )
        self._video_label.setPixmap(scaled)

    @pyqtSlot(int)
    def _update_fps(self, fps: int) -> None:
        """Adjust control limits based on actual camera FPS."""

        self._motion_settings.fps = max(1, fps)
        self._detected_fps = self._motion_settings.fps
        self._delay_spinbox.setMaximum(self._motion_settings.fps * 10)
        self._update_delay_seconds_label()
        self._refresh_status_message()

    @pyqtSlot(int)
    def _handle_delay_change(self, value: int) -> None:
        """Propagate new delay to the worker and update seconds label."""

        self._motion_settings.delay_frames = value
        self._update_delay_seconds_label()
        self._worker.set_delay_frames(value)

    def _update_delay_seconds_label(self) -> None:
        """Display the delay in seconds alongside the frame count."""

        self._delay_label.setText(self._format_delay_seconds(self._delay_spinbox.value()))

    def _format_delay_seconds(self, frames: int) -> str:
        """Format helper for the seconds label."""

        seconds = frames / self._motion_settings.fps if self._motion_settings.fps else 0
        return f"≈ {seconds:.2f}s"

    @pyqtSlot(str)
    def _handle_error(self, message: str) -> None:
        """Show a modal error dialog and stop processing."""

        self._status_bar.showMessage(message)
        QMessageBox.critical(self, self._window_title, message)
        self.close()

    @pyqtSlot(str)
    def _handle_status_message(self, message: str) -> None:
        """Display transient worker status messages."""

        # Show temporary status messages directly without mixing with persistent info
        self._status_bar.showMessage(message, 3000)  # Clear after 3 seconds

    @pyqtSlot(str)
    def _update_camera_name(self, name: str) -> None:
        """Store the active camera name and refresh the status bar."""

        self._camera_name = name
        self._refresh_status_message()

    def _refresh_status_message(self) -> None:
        """Compose the status bar message with camera name and detected FPS."""

        parts = []
        if self._camera_name:
            parts.append(f"Camera: {self._camera_name}")
        if self._detected_fps:
            parts.append(f"{self._detected_fps} FPS detected")

        if parts:
            self._status_bar.showMessage("  |  ".join(parts))
        else:
            self._status_bar.clearMessage()


def run_app(
    camera_settings: CameraSettings,
    motion_settings: MotionSettings,
    window_title: str,
) -> int:
    """Convenience runner that instantiates QApplication if needed."""

    app = QApplication.instance()
    owns_application = False

    if app is None:
        # Lazily create the application if client code hasn't already done so.
        app = QApplication(sys.argv)
        owns_application = True

    window = MotionExtractorWindow(camera_settings, motion_settings, window_title)
    window.show()

    if owns_application:
        return app.exec_()

    return 0
