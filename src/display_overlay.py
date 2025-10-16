"""
On-screen display module for showing control information.
"""

import cv2
import numpy as np
from typing import List, Tuple


class DisplayOverlay:
    """
    Renders informational overlays on video frames.
    
    Shows control instructions and current parameter values in a clean,
    readable format over the video feed.
    """
    
    def __init__(self, font_scale: float = 0.6, font_thickness: int = 2,
                 bg_opacity: float = 0.7):
        """
        Initialize the display overlay.
        
        Args:
            font_scale (float): Size of text (default: 0.6)
            font_thickness (int): Thickness of text lines (default: 2)
            bg_opacity (float): Background box opacity (0.0-1.0)
        """
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.font_scale = font_scale
        self.font_thickness = font_thickness
        self.bg_opacity = bg_opacity
        
        # Colors (BGR format)
        self.text_color = (255, 255, 255)  # White
        self.bg_color = (0, 0, 0)  # Black
        self.highlight_color = (0, 255, 255)  # Yellow
    
    def add_text_with_background(self, frame: np.ndarray, text: str, 
                                  position: Tuple[int, int],
                                  color: Tuple[int, int, int] = None) -> None:
        """
        Add text with semi-transparent background for readability.
        
        Args:
            frame (np.ndarray): Frame to draw on (modified in-place)
            text (str): Text to display
            position (tuple): (x, y) position for bottom-left of text
            color (tuple, optional): Text color in BGR
        """
        if color is None:
            color = self.text_color
        
        # Get text size for background box
        (text_width, text_height), baseline = cv2.getTextSize(
            text, self.font, self.font_scale, self.font_thickness
        )
        
        x, y = position
        padding = 5
        
        # Create background rectangle coordinates
        box_coords = (
            (x - padding, y - text_height - padding),
            (x + text_width + padding, y + baseline + padding)
        )
        
        # Draw semi-transparent background
        overlay = frame.copy()
        cv2.rectangle(overlay, box_coords[0], box_coords[1], self.bg_color, -1)
        cv2.addWeighted(overlay, self.bg_opacity, frame, 1 - self.bg_opacity, 0, frame)
        
        # Draw text
        cv2.putText(frame, text, position, self.font, self.font_scale,
                   color, self.font_thickness, cv2.LINE_AA)
    
    def render_bottom_info(self, frame: np.ndarray, delay_text: str,
                          camera_name: str = "") -> np.ndarray:
        """
        Render information overlay across the bottom of the frame.
        
        Layout:
        - Bottom-left: Current delay information

        Args:
            frame (np.ndarray): Input frame
            delay_text (str): Current delay information
            camera_name (str): Unused parameter kept for backward compatibility
        
        Returns:
            np.ndarray: Frame with overlay rendered
        """
        # Work on a copy to avoid modifying original
        display_frame = frame.copy()
        
        height = frame.shape[0]
        
    # Camera name overlay intentionally removed; UI now shows it via status bar.

    # Bottom-left: Delay info
        delay_y = height - 15
        self.add_text_with_background(
            display_frame, delay_text, (10, delay_y), self.highlight_color
        )
        
        return display_frame
