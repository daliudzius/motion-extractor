"""
Unit tests for ControlsManager class (GUI-based controls).
"""

import pytest
from src.controls_manager import ControlsManager


class TestControlsManager:
    """Test suite for ControlsManager with GUI spinbox."""
    
    def test_initialization(self):
        """Test that ControlsManager initializes with default values."""
        controls = ControlsManager(fps=30, initial_delay_frames=60)
        assert controls.delay_frames == 60
        assert controls.fps == 30
        assert controls.min_delay == 0
        assert controls.max_delay == 300  # 10 seconds at 30 fps
    
    def test_set_delay_from_spinbox(self):
        """Test setting delay directly from spinbox input."""
        controls = ControlsManager(fps=30, initial_delay_frames=60)
        controls.set_delay_frames(120)
        assert controls.delay_frames == 120
    
    def test_increase_delay(self):
        """Test increasing delay by one frame."""
        controls = ControlsManager(fps=30, initial_delay_frames=60)
        controls.increase_delay()
        assert controls.delay_frames == 61
    
    def test_decrease_delay(self):
        """Test decreasing delay by one frame."""
        controls = ControlsManager(fps=30, initial_delay_frames=60)
        controls.decrease_delay()
        assert controls.delay_frames == 59
    
    def test_decrease_delay_at_minimum(self):
        """Test that delay doesn't go below minimum."""
        controls = ControlsManager(fps=30, initial_delay_frames=0)
        controls.decrease_delay()
        assert controls.delay_frames == 0
    
    def test_increase_delay_at_maximum(self):
        """Test that delay doesn't exceed maximum."""
        controls = ControlsManager(fps=30, initial_delay_frames=300)
        controls.increase_delay()
        assert controls.delay_frames == 300
    
    def test_set_delay_frames(self):
        """Test directly setting delay in frames."""
        controls = ControlsManager(fps=30)
        controls.set_delay_frames(120)
        assert controls.delay_frames == 120
    
    def test_set_delay_frames_clamps_to_range(self):
        """Test that setting delay clamps to valid range."""
        controls = ControlsManager(fps=30)
        
        controls.set_delay_frames(-10)
        assert controls.delay_frames == 0
        
        controls.set_delay_frames(500)
        assert controls.delay_frames == 300
    
    def test_get_delay_seconds(self):
        """Test converting frames to seconds."""
        controls = ControlsManager(fps=30, initial_delay_frames=90)
        assert controls.get_delay_seconds() == 3.0
    
    def test_get_display_text(self):
        """Test getting formatted display text."""
        controls = ControlsManager(fps=30, initial_delay_frames=90)
        text = controls.get_display_text()
        
        assert "3.0s" in text or "90" in text
        assert "frames" in text.lower() or "delay" in text.lower()
