"""
GUI control window with keyboard shortcuts for delay adjustment.
Uses OpenCV's native GUI without sliders or mouse interaction.
"""

import cv2
import numpy as np
from typing import Callable, Optional


class ControlWindow:
    """
    Creates a control window displaying current frame delay value.
    
    Provides:
    - Large number display showing current value
    - Visual display of frames and seconds
    - Keyboard controls: Up/Down arrows to adjust (handled by main loop)
    - Real-time callbacks on value changes
    """
    
    def __init__(self, window_name: str = "Controls", 
                 min_frames: int = 1, max_frames: int = 300,
                 initial_value: int = 60):
        """
        Initialize the control window with display.
        
        Args:
            window_name (str): Name for the control window
            min_frames (int): Minimum delay in frames
            max_frames (int): Maximum delay in frames
            initial_value (int): Starting delay value
        """
        self.window_name = window_name
        self.min_frames = min_frames
        self.max_frames = max_frames
        self.current_value = initial_value
        self.callback: Optional[Callable[[int], None]] = None
        self.fps = 30  # Default, will be updated
        
        # Create OpenCV window
        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(self.window_name, 400, 250)
        
        # Display initial info
        self._update_display()
    
    def increment_value(self, delta: int) -> None:
        """
        Change the current value by delta and trigger callback.
        
        Args:
            delta: Amount to change (+1 or -1)
        """
        new_value = max(self.min_frames, min(self.max_frames, self.current_value + delta))
        if new_value != self.current_value:
            self.current_value = new_value
            self._update_display()
            if self.callback:
                self.callback(new_value)
    
    def _update_display(self) -> None:
        """Update the display image with current value info."""
        # Create display image with light background
        img = np.ones((250, 400, 3), dtype=np.uint8) * 245
        
        # Calculate display text
        seconds = self.current_value / self.fps if self.fps > 0 else 0
        
        # Draw title
        cv2.putText(
            img, 
            "Frame Delay Control", 
            (80, 35), 
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8, 
            (60, 60, 60), 
            2, 
            cv2.LINE_AA
        )
        
        # Draw large frame number in center
        cv2.putText(
            img, 
            f"{self.current_value}", 
            (150, 120), 
            cv2.FONT_HERSHEY_DUPLEX,
            3.0, 
            (20, 20, 20), 
            5, 
            cv2.LINE_AA
        )
        
        # Draw "frames" label
        cv2.putText(
            img, 
            "frames", 
            (140, 155), 
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7, 
            (100, 100, 100), 
            2, 
            cv2.LINE_AA
        )
        
        # Draw seconds conversion
        cv2.putText(
            img, 
            f"= {seconds:.2f} seconds @ {self.fps} fps", 
            (90, 190), 
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6, 
            (100, 100, 100), 
            1, 
            cv2.LINE_AA
        )
        
        # Draw keyboard instructions
        cv2.putText(
            img, 
            "Use Up/Down arrow keys to adjust", 
            (65, 225), 
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5, 
            (120, 120, 120), 
            1, 
            cv2.LINE_AA
        )
        
        cv2.imshow(self.window_name, img)
    
    def set_callback(self, callback: Callable[[int], None]) -> None:
        """
        Set callback function to be called when value changes.
        
        Args:
            callback: Function that takes the new frame delay value
        """
        self.callback = callback
    
    def get_value(self) -> int:
        """
        Get current delay value from spinbox.
        
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
        clamped = max(self.min_frames, min(value, self.max_frames))
        if clamped != self.current_value:
            self.current_value = clamped
            self._update_display()
    
    def update_display(self, fps: int) -> None:
        """
        Update FPS value for display calculations.
        
        Args:
            fps (int): Current FPS for seconds calculation
        """
        if self.fps != fps:
            self.fps = fps
            self._update_display()
    
    def update(self) -> None:
        """
        Process window events (compatibility method).
        For OpenCV windows, event processing happens in cv2.waitKey().
        """
        pass
    
    def is_running(self) -> bool:
        """
        Check if window is still open.
        
        Returns:
            bool: True if window is active
        """
        # Check if window exists by trying to get window property
        try:
            prop = cv2.getWindowProperty(self.window_name, cv2.WND_PROP_VISIBLE)
            return prop >= 0
        except:
            return False
    
    def destroy(self) -> None:
        """Close and destroy the control window."""
        try:
            cv2.destroyWindow(self.window_name)
        except:
            pass
