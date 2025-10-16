# GitHub Copilot Instructions

## Code Documentation Standards

### Function Comments
- **REQUIRED**: Add docstrings to ALL functions and methods
- Include purpose, parameters, return values, and exceptions
- Use Google-style or NumPy-style docstrings

Example:
```python
def process_frame(frame, threshold=30):
    """
    Processes a video frame for motion detection.
    
    Args:
        frame (numpy.ndarray): Input frame from video stream
        threshold (int): Pixel difference threshold (default: 30)
    
    Returns:
        numpy.ndarray: Processed frame with motion highlighted
    
    Raises:
        ValueError: If frame is empty or invalid
    """
```

### Logic Comments
- **REQUIRED**: Add inline comments for medium to advanced logic
- Explain WHY, not WHAT (the code shows what)
- Comment complex algorithms, non-obvious optimizations, or workarounds
- Document any mathematical operations or OpenCV-specific techniques

Example:
```python
# Invert the delayed frame to create contrast with current frame
# This makes static pixels cancel out when blended at 50% opacity
inverted = cv2.bitwise_not(delayed_frame)
```

### Comment When:
- Using non-trivial OpenCV functions
- Implementing mathematical transformations
- Handling edge cases or special conditions
- Using buffer management or timing logic
- Applying image processing techniques (blending, masking, etc.)

## Chat Response Standards

### Concise Responses
- Keep explanations brief and focused
- Avoid lengthy preambles or unnecessary context

### Code Block Limits
- **NEVER show entire code blocks longer than 20 lines**
- For larger changes, show:
  - Simplified pseudocode, OR
  - High-level structure/outline, OR
  - Only the specific changed section with context

### Instead of Full Code, Show:

**Pseudocode:**
```
function extract_motion:
    1. Get current frame
    2. Get delayed frame from buffer
    3. Calculate difference
    4. Apply blending
    5. Return result
```

**Structure:**
```python
class MotionExtractor:
    def __init__(self, delay): ...
    def add_frame(self, frame): ...
    def extract_motion(self): ...
    # ... other methods
```

**Focused snippet (with context):**
```python
# In extract_motion method, add blending logic:
diff = cv2.absdiff(current, delayed)
inverted = cv2.bitwise_not(delayed)
result = cv2.addWeighted(diff, 0.5, inverted, 0.5, 0)
```

## Code Quality

- Follow PEP 8 style guidelines
- Use type hints where helpful
- Keep functions focused and single-purpose
- Use meaningful variable names
- Handle errors gracefully with try/except blocks
- Validate inputs at function boundaries

## Testing

- Write unit tests for core functionality
- Test edge cases (empty frames, invalid inputs)
- Use pytest for test structure
- Mock camera/video sources in tests

## Development Workflow

- **ALWAYS test functionality with the user before updating documentation**
- Confirm features work as expected in real usage
- Only update README/docs after user verification
- Ask for feedback before finalizing changes
