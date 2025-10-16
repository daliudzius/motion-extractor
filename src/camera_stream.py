"""
Camera and video stream handling module.
"""

import cv2
import numpy as np
from typing import Optional, Union


class CameraStream:
    """
    Manages video input from cameras, video files, or other sources.
    
    Provides a unified interface for accessing different video sources
    with consistent frame retrieval and error handling.
    """
    
    def __init__(self, source: Union[int, str] = 0, width: Optional[int] = None, 
                 height: Optional[int] = None):
        """
        Initialize the camera stream.
        
        Args:
            source (int | str): Camera index (0 for default) or video file path
            width (int, optional): Desired frame width (None for default)
            height (int, optional): Desired frame height (None for default)
            
        Raises:
            RuntimeError: If camera/video source cannot be opened
        """
        self.source = source
        self.capture = None
        self.width = width
        self.height = height
        self.is_running = False
        
    def start(self) -> bool:
        """
        Open and start the video stream.
        
        Returns:
            bool: True if stream started successfully, False otherwise
        """
        self.capture = cv2.VideoCapture(self.source)
        
        if not self.capture.isOpened():
            return False
        
        # Set resolution if specified
        if self.width is not None:
            self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        if self.height is not None:
            self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
            
        self.is_running = True
        return True
    
    def read_frame(self) -> Optional[np.ndarray]:
        """
        Read a single frame from the stream.
        
        Returns:
            np.ndarray: Frame from video stream, or None if read failed
        """
        if not self.is_running or self.capture is None:
            return None
        
        ret, frame = self.capture.read()
        
        if not ret:
            return None
            
        return frame
    
    def get_fps(self) -> float:
        """
        Get the frames per second of the video stream.
        
        Returns:
            float: FPS value, or 30.0 as default if unavailable
        """
        if self.capture is None:
            return 30.0
            
        fps = self.capture.get(cv2.CAP_PROP_FPS)
        # Return default if FPS is not available or invalid
        return fps if fps > 0 else 30.0
    
    def get_resolution(self) -> tuple[int, int]:
        """
        Get current frame width and height.
        
        Returns:
            tuple[int, int]: (width, height) of frames
        """
        if self.capture is None:
            return (0, 0)
            
        width = int(self.capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
        return (width, height)
    
    def get_device_name(self) -> str:
        """
        Get a shortened device name for display.
        
        Returns:
            str: Device name (e.g., "Cam 0", "video.mp4")
        """
        if isinstance(self.source, int):
            return f"Cam {self.source}"
        elif isinstance(self.source, str):
            # Extract filename from path
            import os
            filename = os.path.basename(self.source)
            # Shorten if too long
            if len(filename) > 20:
                return filename[:17] + "..."
            return filename
        return "Unknown"
    
    def stop(self) -> None:
        """Release the video stream and cleanup resources."""
        if self.capture is not None:
            self.capture.release()
            self.capture = None
        self.is_running = False
    
    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - cleanup resources."""
        self.stop()
