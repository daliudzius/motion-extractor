# Motion Extractor

Real-time motion extraction from live camera streams using OpenCV - isolates moving objects by removing static background elements through frame differencing.

## Quick Start

```bash
# 1. Clone and navigate
git clone https://github.com/daliudzius/motion-extractor.git
cd motion-extractor

# 2. Set up environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run
python src/main.py
```

## Controls

- **Up/Down Arrow** - Adjust delay (1-300 frames)
- **Q** - Quit

Two windows open: Motion output + Control panel showing current delay.

## Features

- Live camera processing with adjustable delay (0-10 seconds)
- Real-time motion visualization through frame blending
- On-screen overlay with delay info and camera name
- Configurable via `config/settings.json`

## How It Works

Compares current frame with a delayed frame from buffer, applies differencing and blending at 50% opacity to highlight only pixels that changed over time.

## Development

```bash
pytest              # Run tests
```

## License

MIT
