"""
Motion extraction module for real-time video processing.
"""

import cv2
import numpy as np
from collections import deque
from typing import Optional, Tuple


class MotionExtractor:
    """
    Extracts motion from video frames by comparing current frames with delayed frames.
    
    The algorithm works by maintaining a buffer of previous frames and comparing
    the current frame with a frame from N seconds ago. Static pixels are removed
    through frame inversion and blending.
    """
    
    def __init__(self, delay_seconds: float = 2.0, fps: int = 30, blend_alpha: float = 0.5):
        """
        Initialize the motion extractor.
        
        Args:
            delay_seconds (float): Time delay for frame comparison (0-10 seconds)
            fps (int): Expected frames per second of the video stream
            blend_alpha (float): Blending factor for frame overlay (0.0-1.0)
        
        Raises:
            ValueError: If parameters are out of valid ranges
        """
        if not 0 <= delay_seconds <= 10:
            raise ValueError("delay_seconds must be between 0 and 10")
        if not 0 < blend_alpha <= 1:
            raise ValueError("blend_alpha must be between 0 and 1")
            
        self.delay_seconds = delay_seconds
        self.fps = fps
        self.blend_alpha = blend_alpha
        
        # Calculate buffer size needed for the delay
        # Add extra frames to ensure we always have enough
        self.buffer_size = int(delay_seconds * fps) + 1
        self.frame_buffer = deque(maxlen=self.buffer_size)
        
    def add_frame(self, frame: np.ndarray) -> None:
        """
        Add a frame to the processing buffer.
        
        Args:
            frame (np.ndarray): Input frame from video stream
            
        Raises:
            ValueError: If frame is None or empty
        """
        if frame is None or frame.size == 0:
            raise ValueError("Frame cannot be None or empty")
        
        self.frame_buffer.append(frame.copy())
    
    def extract_motion(self) -> Optional[np.ndarray]:
        """
        Extract motion by comparing current frame with delayed frame.
        
        Returns:
            np.ndarray: Processed frame with only moving pixels visible,
                       or None if buffer is not yet full
        """
        # Need at least 2 frames to compare
        if len(self.frame_buffer) < 2:
            return None
        
        current_frame = self.frame_buffer[-1]
        
        # Get the delayed frame (oldest frame in buffer)
        delayed_frame = self.frame_buffer[0]
        
        # Invert the delayed frame for complementary blending. When combined with
        # the current frame at 50% opacity, static regions neutralize to mid-gray.
        inverted_delayed = cv2.bitwise_not(delayed_frame)
        base_blend = cv2.addWeighted(current_frame, 0.5, inverted_delayed, 0.5, 0)
        
        # Calculate absolute difference between current and delayed frames to
        # highlight pixel changes across the delay window.
        frame_diff = cv2.absdiff(current_frame, delayed_frame)
        
        # Build a motion mask so highlights only impact changing regions. The
        # threshold can be tuned to control sensitivity.
        frame_diff_gray = cv2.cvtColor(frame_diff, cv2.COLOR_BGR2GRAY)
        _, motion_mask = cv2.threshold(frame_diff_gray, 25, 255, cv2.THRESH_BINARY)
        motion_mask_bgr = cv2.cvtColor(motion_mask, cv2.COLOR_GRAY2BGR)
        motion_highlight = cv2.bitwise_and(frame_diff, motion_mask_bgr)
        
        # Blend masked motion highlights on top of the gray base. Static regions
        # remain neutral gray while movement retains the dynamic overlay.
        motion_extracted = cv2.addWeighted(
            base_blend, 1.0,
            motion_highlight, self.blend_alpha,
            0
        )
        
        return motion_extracted
    
    def reset(self) -> None:
        """Clear the frame buffer and reset the extractor state."""
        self.frame_buffer.clear()
    
    def update_delay_frames(self, new_delay_frames: int) -> None:
        """
        Update the delay in frames, smoothly adjusting the buffer size.
        
        This allows real-time delay adjustment without disrupting playback.
        If reducing delay, keeps most recent frames. If increasing, extends buffer.
        
        Args:
            new_delay_frames (int): New delay in frames
        """
        # Calculate new buffer size (add 1 for safety)
        new_buffer_size = new_delay_frames + 1
        
        if new_buffer_size == self.buffer_size:
            return  # No change needed
        
        # Store current frames in a list to preserve them
        current_frames = list(self.frame_buffer)
        
        # Update buffer size and delay
        self.buffer_size = new_buffer_size
        self.delay_seconds = new_delay_frames / self.fps
        
        # Create new buffer with updated max length
        self.frame_buffer = deque(maxlen=self.buffer_size)
        
        # Restore frames (deque will auto-trim if new size is smaller)
        # If buffer shrinks, oldest frames are automatically dropped
        for frame in current_frames:
            self.frame_buffer.append(frame)
    
    def get_current_delay_frames(self) -> int:
        """
        Get the current delay setting in frames.
        
        Returns:
            int: Current delay in frames
        """
        return self.buffer_size - 1
