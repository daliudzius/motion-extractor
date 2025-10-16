"""
Interactive controls management for real-time parameter adjustment.
"""

from typing import Optional


class ControlsManager:
    """
    Manages GUI-based real-time control of motion extraction parameters.
    
    Provides direct frame delay input via GUI spinbox controls.
    """
    
    def __init__(self, fps: int = 30, initial_delay_frames: int = 60, 
                 min_delay: int = 0, max_delay: Optional[int] = None):
        """
        Initialize the controls manager.
        
        Args:
            fps (int): Frames per second of the video stream
            initial_delay_frames (int): Starting delay in frames
            min_delay (int): Minimum allowed delay in frames
            max_delay (int, optional): Maximum delay in frames (default: 10 seconds worth)
        """
        self.fps = fps
        self.min_delay = min_delay
        # Default max: 10 seconds worth of frames
        self.max_delay = max_delay if max_delay is not None else fps * 10
        
        self.delay_frames = initial_delay_frames
        self._clamp_delay()
    
    def _clamp_delay(self) -> None:
        """Ensure delay stays within valid range."""
        self.delay_frames = max(self.min_delay, min(self.delay_frames, self.max_delay))
    
    def increase_delay(self, amount: int = 1) -> None:
        """
        Increase delay by specified number of frames.
        
        Args:
            amount (int): Number of frames to increase (default: 1)
        """
        self.delay_frames += amount
        self._clamp_delay()
    
    def decrease_delay(self, amount: int = 1) -> None:
        """
        Decrease delay by specified number of frames.
        
        Args:
            amount (int): Number of frames to decrease (default: 1)
        """
        self.delay_frames -= amount
        self._clamp_delay()
    
    def set_delay_frames(self, frames: int) -> None:
        """
        Set delay to specific number of frames.
        
        Args:
            frames (int): Target delay in frames
        """
        self.delay_frames = frames
        self._clamp_delay()
    
    def set_delay_seconds(self, seconds: float) -> None:
        """
        Set delay in seconds (converts to frames internally).
        
        Args:
            seconds (float): Target delay in seconds
        """
        self.delay_frames = int(seconds * self.fps)
        self._clamp_delay()
    
    def get_delay_seconds(self) -> float:
        """
        Get current delay in seconds.
        
        Returns:
            float: Current delay in seconds
        """
        return self.delay_frames / self.fps
    
    def get_display_text(self) -> str:
        """
        Get formatted text for on-screen display.
        
        Returns:
            str: Formatted display text showing current delay
        """
        seconds = self.get_delay_seconds()
        return f"Delay: {self.delay_frames} frames ({seconds:.1f}s)"
