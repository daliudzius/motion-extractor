"""
Unit tests for CameraStream class.
"""

from src.camera_stream import CameraStream


class TestCameraStream:
    """Test suite for CameraStream."""

    def test_initialization(self):
        """Test that CameraStream initializes correctly."""
        stream = CameraStream(source=0, width=640, height=480)
        assert stream.source == 0
        assert stream.width == 640
        assert stream.height == 480
        assert stream.is_running is False

    def test_get_fps_default(self):
        """Test default FPS when stream not started."""
        stream = CameraStream()
        assert stream.get_fps() == 30.0

    def test_get_resolution_no_capture(self):
        """Test resolution returns (0,0) when not capturing."""
        stream = CameraStream()
        assert stream.get_resolution() == (0, 0)

    def test_context_manager(self):
        """Test that CameraStream works as context manager."""
        # Note: This may fail if no camera available
        # In real tests, you'd mock cv2.VideoCapture
        with CameraStream(source=0) as stream:
            # Should attempt to start
            pass
        # Should be stopped after exiting context
        assert stream.is_running is False
