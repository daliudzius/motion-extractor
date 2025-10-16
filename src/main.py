"""
Main application entry point for motion extraction.
"""

import cv2
from camera_stream import CameraStream
from motion_extractor import MotionExtractor
from controls_manager import ControlsManager
from control_window import ControlWindow
from display_overlay import DisplayOverlay
from config import Config


def main():
    """
    Run the motion extraction application with GUI spinbox controls.

    Displays motion-extracted video with info overlay across the bottom.
    Uses a separate control window with spinbox for delay adjustment.

    Controls:
        - Control window spinbox: Adjust delay in frames
        - Q: Quit
    """
    # Load configuration
    config = Config()

    # Initialize camera stream
    camera = CameraStream(
        source=config.get("camera", "source", 0),
        width=config.get("camera", "width"),
        height=config.get("camera", "height"),
    )

    if not camera.start():
        print("Error: Could not open camera")
        return

    fps = int(camera.get_fps())
    if fps <= 0:
        fps = config.get("motion", "fps", 30)

    # Prefer explicit frame-based delay from config, falling back to seconds or
    # the new default of five frames. Five frames ensures a subtle time offset
    # while keeping the interface responsive.
    configured_frames = config.get("motion", "delay_frames")
    configured_seconds = config.get("motion", "delay_seconds")
    if configured_frames is not None:
        initial_frames = int(configured_frames)
        initial_delay = initial_frames / fps
    elif configured_seconds is not None:
        initial_delay = float(configured_seconds)
        initial_frames = max(0, int(round(initial_delay * fps)))
    else:
        initial_frames = 5
        initial_delay = initial_frames / fps

    # Initialize motion extractor
    extractor = MotionExtractor(
        delay_seconds=initial_delay, fps=fps, blend_alpha=config.get("motion", "blend_alpha", 0.5)
    )

    # Initialize controls manager (for state tracking)
    controls = ControlsManager(fps=fps, initial_delay_frames=initial_frames)

    # Initialize GUI control window with spinbox
    control_win = ControlWindow(
        window_name="Delay Control",
        min_frames=0,
        max_frames=fps * 10,  # 10 seconds max
        initial_value=initial_frames,
    )

    # Set callback for control window updates
    def on_delay_change(new_frames: int):
        """Update delay when spinbox value changes."""
        controls.set_delay_frames(new_frames)
        extractor.update_delay_frames(new_frames)
        print(f"Delay updated: {controls.get_display_text()}")

    control_win.set_callback(on_delay_change)

    # Initialize display overlay
    overlay = DisplayOverlay()

    window_name = config.get("display", "window_name", "Motion Extraction")
    show_preview = config.get("display", "show_preview", True)
    camera_name = camera.get_device_name()

    print(f"Starting motion extraction (delay: {initial_delay}s)")
    print(f"Camera: {camera_name}")
    print("Use Up/Down arrow keys to adjust delay, Q to quit")

    try:
        while control_win.is_running():
            # Read frame from camera
            frame = camera.read_frame()
            if frame is None:
                print("End of stream")
                break

            # Add frame to extractor
            extractor.add_frame(frame)

            # Extract motion
            motion_frame = extractor.extract_motion()

            # Display result if available
            if show_preview and motion_frame is not None:
                # Add overlay with info across bottom
                delay_text = controls.get_display_text()
                display_frame = overlay.render_bottom_info(motion_frame, delay_text, camera_name)
                cv2.imshow(window_name, display_frame)

            # Update control window FPS display
            control_win.update_display(fps)

            # Check for keyboard input (wait 1ms for responsiveness)
            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break
            elif key == 82 or key == 0:  # Up arrow (different codes on different platforms)
                control_win.increment_value(1)
            elif key == 84 or key == 1:  # Down arrow
                control_win.increment_value(-1)

    finally:
        # Cleanup
        control_win.destroy()
        camera.stop()
        cv2.destroyAllWindows()
        print("Motion extraction stopped")


if __name__ == "__main__":
    main()
