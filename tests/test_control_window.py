"""
Tests for ControlWindow class.
"""

from src.control_window import ControlWindow


class TestControlWindow:
    """Test suite for ControlWindow functionality."""

    def test_initialization(self):
        """Test control window initializes with correct default values."""
        control = ControlWindow(
            window_name="Test Control", min_frames=1, max_frames=300, initial_value=60
        )

        assert control.window_name == "Test Control"
        assert control.min_frames == 1
        assert control.max_frames == 300
        assert control.current_value == 60
        assert control.fps == 30
        assert control.callback is None

        control.destroy()

    def test_get_value(self):
        """Test getting current delay value."""
        control = ControlWindow(initial_value=45)

        assert control.get_value() == 45

        control.destroy()

    def test_set_value(self):
        """Test setting delay value programmatically."""
        control = ControlWindow(min_frames=10, max_frames=100, initial_value=50)

        # Set valid value
        control.set_value(75)
        assert control.get_value() == 75

        # Test clamping to max
        control.set_value(150)
        assert control.get_value() == 100

        # Test clamping to min
        control.set_value(5)
        assert control.get_value() == 10

        control.destroy()

    def test_increment_value(self):
        """Test incrementing value with up/down controls."""
        control = ControlWindow(min_frames=1, max_frames=100, initial_value=50)

        # Increment up
        control.increment_value(1)
        assert control.get_value() == 51

        # Increment down
        control.increment_value(-1)
        assert control.get_value() == 50

        # Test max boundary
        control.set_value(100)
        control.increment_value(1)
        assert control.get_value() == 100  # Should not exceed max

        # Test min boundary
        control.set_value(1)
        control.increment_value(-1)
        assert control.get_value() == 1  # Should not go below min

        control.destroy()

    def test_callback_on_increment(self):
        """Test callback is triggered when value changes via increment."""
        control = ControlWindow(initial_value=30)

        callback_values = []

        def test_callback(value):
            callback_values.append(value)

        control.set_callback(test_callback)

        # Increment should trigger callback
        control.increment_value(1)
        assert len(callback_values) == 1
        assert callback_values[0] == 31

        # Increment down should also trigger
        control.increment_value(-1)
        assert len(callback_values) == 2
        assert callback_values[1] == 30

        # No change should not trigger callback
        control.set_value(30)
        assert len(callback_values) == 2  # Should not increase

        control.destroy()

    def test_update_display_fps(self):
        """Test updating FPS value for display calculations."""
        control = ControlWindow(initial_value=60)

        assert control.fps == 30  # Default value

        # Update FPS should work without errors
        control.update_display(fps=60)
        assert control.fps == 60

        # Same FPS should not cause issues
        control.update_display(fps=60)
        assert control.fps == 60

        control.destroy()

    def test_is_running(self):
        """Test window running state check."""
        control = ControlWindow()

        # Should be running after initialization
        assert control.is_running() is True

        # After destroy, should not be running
        control.destroy()
        # Note: OpenCV window check may not work in headless environment
        # so we don't assert False here

    def test_update_method(self):
        """Test update method exists and doesn't error."""
        control = ControlWindow()

        # Should not raise any errors
        control.update()

        control.destroy()
