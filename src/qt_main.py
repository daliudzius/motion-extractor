"""
PyQt5 entry point for the motion extraction demo.

Run this module to launch the unified window that embeds both the
video preview and delay controls implemented with PyQt5 widgets.
"""

from __future__ import annotations

import sys
from typing import Tuple

from config import Config
from qt_window import CameraSettings, MotionSettings, run_app


def _resolve_initial_delay(config: Config, fps: int) -> Tuple[int, float]:
    """Translate configuration values into frame and second delays."""

    configured_frames = config.get("motion", "delay_frames")
    if configured_frames is not None:
        frames = int(configured_frames)
        return frames, frames / fps if fps else 0.0

    configured_seconds = config.get("motion", "delay_seconds")
    if configured_seconds is not None:
        seconds = float(configured_seconds)
        return max(0, int(round(seconds * fps))), seconds

    frames = 5
    return frames, frames / fps if fps else 0.0


def main() -> int:
    """Launch the PyQt5 motion extraction window."""

    config = Config()

    camera_settings = CameraSettings(
        source=config.get("camera", "source", 0),
        width=config.get("camera", "width"),
        height=config.get("camera", "height"),
    )

    fps = int(config.get("motion", "fps", 30)) or 30
    delay_frames, _ = _resolve_initial_delay(config, fps)

    motion_settings = MotionSettings(
        fps=fps,
        delay_frames=delay_frames,
        blend_alpha=float(config.get("motion", "blend_alpha", 0.5)),
    )

    window_title = config.get("display", "window_name", "Motion Extraction")

    return run_app(camera_settings, motion_settings, window_title)


if __name__ == "__main__":
    sys.exit(main())
