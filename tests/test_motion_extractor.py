"""
Unit tests for MotionExtractor class.
"""

import pytest
import numpy as np
from src.motion_extractor import MotionExtractor


class TestMotionExtractor:
    """Test suite for MotionExtractor."""
    
    def test_initialization(self):
        """Test that MotionExtractor initializes with valid parameters."""
        extractor = MotionExtractor(delay_seconds=2.0, fps=30)
        assert extractor.delay_seconds == 2.0
        assert extractor.fps == 30
        assert len(extractor.frame_buffer) == 0
    
    def test_invalid_delay(self):
        """Test that invalid delay raises ValueError."""
        with pytest.raises(ValueError):
            MotionExtractor(delay_seconds=15.0)
    
    def test_add_frame(self):
        """Test adding frames to buffer."""
        extractor = MotionExtractor(delay_seconds=1.0, fps=30)
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        extractor.add_frame(frame)
        assert len(extractor.frame_buffer) == 1
    
    def test_add_invalid_frame(self):
        """Test that adding None frame raises ValueError."""
        extractor = MotionExtractor()
        with pytest.raises(ValueError):
            extractor.add_frame(None)
    
    def test_extract_motion_insufficient_frames(self):
        """Test that extract_motion returns None with insufficient frames."""
        extractor = MotionExtractor(delay_seconds=1.0, fps=30)
        result = extractor.extract_motion()
        assert result is None
    
    def test_extract_motion_with_frames(self):
        """Test motion extraction with valid frames."""
        extractor = MotionExtractor(delay_seconds=0.1, fps=30)
        
        # Add two different frames
        frame1 = np.zeros((100, 100, 3), dtype=np.uint8)
        frame2 = np.ones((100, 100, 3), dtype=np.uint8) * 255
        
        extractor.add_frame(frame1)
        extractor.add_frame(frame2)
        
        result = extractor.extract_motion()
        assert result is not None
        assert result.shape == frame1.shape

    def test_static_pixels_render_gray(self):
        """Static frames should neutralize to gray when blended with inverted overlay."""
        extractor = MotionExtractor(delay_seconds=0.1, fps=30, blend_alpha=0.5)

        frame = np.full((60, 60, 3), 50, dtype=np.uint8)
        extractor.add_frame(frame)
        extractor.add_frame(frame.copy())

        result = extractor.extract_motion()
        assert result is not None
        # Expect nearly mid-gray (127) within a small tolerance due to rounding.
        assert np.all((result >= 126) & (result <= 129))
    
    def test_reset(self):
        """Test that reset clears the buffer."""
        extractor = MotionExtractor()
        frame = np.zeros((100, 100, 3), dtype=np.uint8)
        
        extractor.add_frame(frame)
        assert len(extractor.frame_buffer) > 0
        
        extractor.reset()
        assert len(extractor.frame_buffer) == 0
