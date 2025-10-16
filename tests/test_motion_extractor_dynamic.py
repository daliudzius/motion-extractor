"""
Unit tests for MotionExtractor dynamic delay updates.
"""

import pytest
import numpy as np
from src.motion_extractor import MotionExtractor


class TestMotionExtractorDynamicDelay:
    """Test suite for dynamic delay functionality."""

    def test_update_delay_frames(self):
        """Test updating delay frames dynamically."""
        extractor = MotionExtractor(delay_seconds=1.0, fps=30)
        initial_buffer_size = extractor.buffer_size

        # Update to 2 seconds worth of frames
        extractor.update_delay_frames(60)

        assert extractor.buffer_size == 61  # 60 frames + 1
        assert extractor.buffer_size != initial_buffer_size

    def test_update_delay_preserves_frames(self):
        """Test that updating delay preserves existing frames."""
        extractor = MotionExtractor(delay_seconds=1.0, fps=30)

        # Add some frames
        for i in range(10):
            frame = np.ones((100, 100, 3), dtype=np.uint8) * i
            extractor.add_frame(frame)

        initial_frame_count = len(extractor.frame_buffer)

        # Increase delay
        extractor.update_delay_frames(60)

        # Should preserve frames if new buffer is larger
        assert len(extractor.frame_buffer) == initial_frame_count

    def test_update_delay_decreases_buffer(self):
        """Test that decreasing delay properly trims buffer."""
        extractor = MotionExtractor(delay_seconds=2.0, fps=30)

        # Add many frames
        for i in range(70):
            frame = np.ones((100, 100, 3), dtype=np.uint8) * (i % 255)
            extractor.add_frame(frame)

        # Decrease delay to 1 second (30 frames)
        extractor.update_delay_frames(30)

        # Buffer should be trimmed to new max size + 1
        assert len(extractor.frame_buffer) <= 31

    def test_get_current_delay_frames(self):
        """Test retrieving current delay in frames."""
        extractor = MotionExtractor(delay_seconds=2.0, fps=30)

        # Initial delay: 2 seconds * 30 fps = 60 frames
        assert extractor.get_current_delay_frames() == 60

    def test_extract_motion_with_updated_delay(self):
        """Test that motion extraction works after delay update."""
        extractor = MotionExtractor(delay_seconds=0.5, fps=30)

        # Add frames
        for i in range(20):
            frame = np.ones((100, 100, 3), dtype=np.uint8) * (i * 10)
            extractor.add_frame(frame)

        # Update delay
        extractor.update_delay_frames(10)

        # Should still extract motion
        result = extractor.extract_motion()
        assert result is not None
        assert result.shape == (100, 100, 3)
