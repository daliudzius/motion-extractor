"""
OpenCV-based control window with spinbox for delay adjustment.

This module provides a simple OpenCV GUI with a spinbox control for adjusting
the delay parameter in the original (non-PyQt5) implementation.
"""

import cv2
from typing import Optional, Callable


class ControlWindow:
    """
    OpenCV-based control window for adjusting motion extraction delay.

    Provides a GUI with a spinbox control that allows users to adjust
    the frame delay parameter in real-time.
    """

    def __init__(
        self,
        window_name: str = "Delay Control",
        min_frames: int = 0,
        max_frames: int = 300,
        initial_value: int = 60,
    ):
        """
        Initialize the control window.

        Args:
            window_name (str): Name of the control window
            min_frames (int): Minimum delay value in frames
            max_frames (int): Maximum delay value in frames
            initial_value (int): Initial delay value in frames
        """
        self.window_name = window_name
        self.min_frames = min_frames
        self.max_frames = max_frames
        self.current_value = self._clamp_value(initial_value)
        self.fps = 30  # Default FPS
        self.callback: Optional[Callable[[int], None]] = None

        # Create OpenCV window with trackbar
        cv2.namedWindow(self.window_name)
        cv2.createTrackbar(
            "Delay (frames)",
            self.window_name,
            self.current_value,
            self.max_frames,
            self._on_trackbar_change,
        )
        # Set minimum value
        cv2.setTrackbarMin("Delay (frames)", self.window_name, self.min_frames)

    def _clamp_value(self, value: int) -> int:
        """Clamp value to valid range."""
        return max(self.min_frames, min(value, self.max_frames))

    def _on_trackbar_change(self, value: int) -> None:
        """
        Handle trackbar value changes.

        Args:
            value (int): New trackbar value
        """
        old_value = self.current_value
        self.current_value = self._clamp_value(value)

        # Only trigger callback if value actually changed
        if self.callback is not None and self.current_value != old_value:
            self.callback(self.current_value)

    def get_value(self) -> int:
        """
        Get current delay value.

        Returns:
            int: Current delay in frames
        """
        return self.current_value

    def set_value(self, value: int) -> None:
        """
        Set delay value programmatically.

        Args:
            value (int): New delay value in frames
        """
        self.current_value = self._clamp_value(value)
        cv2.setTrackbarPos("Delay (frames)", self.window_name, self.current_value)

    def increment_value(self, amount: int) -> None:
        """
        Increment or decrement the delay value.

        Args:
            amount (int): Amount to change (positive to increase, negative to decrease)
        """
        new_value = self.current_value + amount
        self.set_value(new_value)

        # Trigger callback if value changed
        if self.callback is not None and self.current_value != (self.current_value - amount):
            self.callback(self.current_value)

    def set_callback(self, callback: Callable[[int], None]) -> None:
        """
        Set callback function to be called when value changes.

        Args:
            callback (Callable[[int], None]): Function to call with new value
        """
        self.callback = callback

    def update_display(self, fps: int) -> None:
        """
        Update the displayed FPS value.

        Args:
            fps (int): Current frames per second
        """
        self.fps = fps

    def update(self) -> None:
        """Update the window display (call in main loop)."""
        # OpenCV trackbar handles its own updates
        pass

    def is_running(self) -> bool:
        """
        Check if the control window is still open.

        Returns:
            bool: True if window is open, False otherwise
        """
        # Check if window exists by trying to get window property
        # Returns -1 if window doesn't exist
        try:
            result = cv2.getWindowProperty(self.window_name, cv2.WND_PROP_VISIBLE)
            return result >= 0
        except cv2.error:
            return False

    def destroy(self) -> None:
        """Close and destroy the control window."""
        try:
            cv2.destroyWindow(self.window_name)
        except cv2.error:
            # Window may already be closed
            pass
