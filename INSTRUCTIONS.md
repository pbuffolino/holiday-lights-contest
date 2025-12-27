# Animation Framework - Development Instructions

**Purpose:** This document provides instructions for creating 3D light animations for a 500-LED Christmas tree using Python.

**Framework:** Python-based animation system with matplotlib visualization  
**Target:** 500 programmable LEDs arranged in 3D space  
**Python Version:** 3.10+  
**Dependencies:** numpy, matplotlib, typeguard

---

## Quick Start

1. Create animation class in `animation.py` that inherits from `BaseAnimation`
2. Implement `renderNextFrame()` to update `self.frameBuf` with RGB values (0-255)
3. Run: `python run_animation.py`

---

## Core Framework

### BaseAnimation Class

**Location:** `lib/base_animation.py`  
**Requirement:** All animations must inherit from this class

**Required Implementation:**
```python
from lib.base_animation import BaseAnimation
from typing import Optional
import numpy as np

class MyAnimation(BaseAnimation):
    def __init__(self, frameBuf: np.ndarray, *, fps: Optional[int] = None):
        super().__init__(frameBuf, fps=fps)
        # Initialize your animation state here
        
    def renderNextFrame(self) -> None:
        # Update self.frameBuf with RGB values (0-255)
        # Shape: (500, 3) where each row is [R, G, B]
        pass
```

**Key Properties:**
- `self.frameBuf`: Numpy array `(500, 3)` - update this each frame with RGB values (0-255)
- `self.fps`: Frames per second (None = run as fast as possible)
- `self.period`: Time per frame in seconds

**Parameter Rules:**
- All custom parameters must be keyword-only (after `*` separator)
- Provide sensible defaults
- Use type hints

**Parameter Validation:**
```python
@classmethod
def validate_parameters(cls, parameters):
    super().validate_parameters(parameters)
    full_parameters = {**cls.get_default_parameters(), **parameters}
    # Add custom validation here
```

---

## Available Utilities

### Color Utilities (`utils/colors.py`)

**HSV/RGB Conversion:**
- `hsv_to_rgb(h, s, v)` → `[R, G, B]` (0-255)
  - `h`: hue (0-1), `s`: saturation (0-1), `v`: value/brightness (0-1)
- `rgb_to_hsv(r, g, b)` → `(h, s, v)` (0-1)
- `rgb_to_hsv_numpy(rgb)` → HSV array `(N, 3)`
- `hsv_to_rgb_numpy(hsv)` → RGB array `(N, 3)`

**Helper Functions:**
- `randomColor()` → Random RGB tuple `[R, G, B]` (0-255)
- `rainbowFrame(t, NUM_PIXELS)` → List of RGB tuples for rainbow gradient
- `brightnessFrame(color, NUM_PIXELS)` → Brightness gradient
- `decayPixel(r, g, b, decayRate)` → Decayed color (HSV brightness decay)
- `desaturatePixel(r, g, b, desaturationRate)` → Desaturated color

### Geometry Utilities (`utils/geometry.py`)

**3D Coordinates:**
- `POINTS_3D`: Numpy array `(500, 3)` with (x, y, z) coordinates for each LED
  - Each row is `[x, y, z]` coordinate
  - Use for 3D spatial animations

**Common 3D Operations:**
```python
from utils.geometry import POINTS_3D
import numpy as np

# Center points at origin
centered = POINTS_3D - np.mean(POINTS_3D, axis=0)

# Distance from origin
distances = np.linalg.norm(POINTS_3D, axis=1)

# Distance from point
distances = np.linalg.norm(POINTS_3D - point, axis=1)

# Plane distance
distances = np.abs(np.dot(POINTS_3D, plane_normal) + d)

# Sphere distance
distances = np.linalg.norm(POINTS_3D - center, axis=1) - radius
```

**Coordinate System:**
- **X**: Front-to-back (depth)
- **Y**: Left-to-right (horizontal)
- **Z**: Bottom-to-top (vertical height)
- **Typical ranges**: Y: [-0.4, 0.4], Z: [-0.45, 0.6]

### Validation Utilities (`utils/validation.py`)

- `is_valid_rgb_color(color)` → bool: Validates RGB tuple/list of 3 integers [0, 255]
- `is_valid_inclusive_range(r, m, M)` → bool: Validates range within bounds

---

## Common Animation Patterns

### Solid Color
```python
def renderNextFrame(self):
    self.frameBuf[:] = self.color
```

### Color Cycle (Rainbow)
```python
from utils.colors import hsv_to_rgb

def renderNextFrame(self):
    for i in range(len(self.frameBuf)):
        hue = (i + self.t) / len(self.frameBuf)
        self.frameBuf[i] = hsv_to_rgb(hue, 1.0, 1.0)
    self.t += 1
```

### Distance-Based (3D)
```python
from utils.geometry import POINTS_3D

def renderNextFrame(self):
    center = np.array([0, 0, 0])
    distances = np.linalg.norm(POINTS_3D - center, axis=1)
    self.frameBuf[distances < self.radius] = self.color
    self.frameBuf[distances >= self.radius] = [0, 0, 0]
```

### Decay Effect
```python
def renderNextFrame(self):
    # Apply decay to all pixels
    self.frameBuf = (self.frameBuf * self.decay).astype(np.uint8)
    # Add new light
    self.frameBuf[self.current_pixel] = self.color
```

### Moving Wave
```python
def renderNextFrame(self):
    for i in range(len(self.frameBuf)):
        phase = (i + self.t * self.speed) / len(self.frameBuf)
        brightness = 0.5 + 0.5 * np.sin(phase * 2 * np.pi)
        self.frameBuf[i] = [int(c * brightness) for c in self.color]
    self.t += 1
```

### Game Loop Structure
```python
def renderNextFrame(self):
    self.frame += 1
    self._update_game_logic()  # Move objects, check collisions
    self._render_frame()        # Draw to frameBuf
```

---

## Best Practices

### Performance
- **Use numpy vectorized operations** instead of Python loops when possible
- Example: `self.frameBuf[:] = color` (vectorized) vs `for i in range(len(self.frameBuf)): ...`
- Use boolean indexing: `self.frameBuf[mask] = color`

### Color Management
- RGB values must be **integers in range [0, 255]**
- Use HSV for smooth color transitions
- Convert to uint8 when needed: `.astype(np.uint8)`

### 3D Animations
- Center points around origin for easier calculations
- Use `np.linalg.norm()` for distance calculations
- Use dot products for plane calculations
- Consider bandwidth/thickness for geometric effects

### Frame Timing
- Use `self.t` or similar counter for time-based animations
- Use `self.fps` to control animation speed
- Use `self.period` for frame timing calculations

### Code Organization
- Import utilities from `utils/` modules
- Use `NUM_PIXELS` from `lib.constants` (value: 500)
- Add docstrings to animation classes
- Follow sample animation patterns in `samples/` directory

---

## Running Animations

### Basic Commands
```bash
# Run animation.py with defaults
python run_animation.py

# Run with custom parameters (JSON format)
python run_animation.py --args '{"fps": 60, "color": [255, 0, 0]}'

# Run a sample animation
python run_animation.py --sample red_green_swap

# List available samples
python run_animation.py --list-samples

# Change background color
python run_animation.py --background white

# Skip parameter validation (not recommended)
python run_animation.py --no_validation
```

### Command-Line Arguments
- `--args`: JSON string with animation parameters
- `--sample <name>`: Run sample animation by name
- `--list-samples`: List all available samples
- `--background <color>`: Background color (default: 'gray')
- `--no_validation`: Skip parameter validation

---

## Sample Animations Reference

**Location:** `samples/` directory

1. **`red_green_swap.py`** - Simple alternating pattern based on frame and pixel index
2. **`down_the_line.py`** - Moving light with color decay effect
3. **`sweeping_planes.py`** - 3D geometric planes sweeping through space

**Study these examples** to understand common patterns and techniques.

---

## Troubleshooting

**"No animation class found"**
- Ensure class inherits from `BaseAnimation`
- Ensure class is not named `BaseAnimation`
- Check file has exactly one animation class

**"Unknown parameter"**
- Check parameter is in `__init__` defaults
- Verify parameter name spelling
- Use `--no_validation` to skip (not recommended)

**Colors not displaying**
- Ensure RGB values are integers [0, 255]
- Check `frameBuf` shape is `(500, 3)`
- Verify values are not floats > 1.0

**Animation too fast/slow**
- Set `fps` parameter: `--args '{"fps": 30}'`

**3D coordinates not working**
- Import: `from utils.geometry import POINTS_3D`
- Shape is `(500, 3)`, not `(3, 500)`
- Use `axis=1` for row-wise operations

**Pattern looks wrapped or distorted**
- Tree is 3D spiral, not flat surface
- Center points first: `POINTS_3D - np.mean(POINTS_3D, axis=0)`
- Use Y for horizontal, Z for vertical positioning

---

## Project Structure

```
.
├── animation.py              # Your animation (edit this)
├── run_animation.py          # Entry point script
├── samples/                  # Example animations
│   ├── down_the_line.py
│   ├── red_green_swap.py
│   └── sweeping_planes.py
├── utils/                    # Utility functions
│   ├── colors.py            # Color conversion
│   ├── geometry.py          # POINTS_3D (500x3 array)
│   └── validation.py        # Parameter validation
├── lib/                      # Framework (don't modify)
│   ├── base_animation.py    # BaseAnimation class
│   ├── matplotlib_controller.py # Visualization
│   └── constants.py         # NUM_PIXELS = 500
└── requirements.txt
```

---

## Important Notes

- **NUM_PIXELS**: Hardcoded to 500 in `lib/constants.py`
- **frameBuf shape**: Always `(500, 3)` - one row per LED, RGB values
- **RGB range**: Must be integers [0, 255]
- **Animation runs**: In matplotlib 3D scatter plot window
- **Stop animation**: Press Ctrl+C
- **Parameter validation**: Enabled by default

---

## Development Workflow

1. **Setup**: `python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt`
2. **Create**: Edit `animation.py` or copy from `samples/`
3. **Test**: `python run_animation.py`
4. **Iterate**: Modify and re-run (Ctrl+C to stop)
5. **Customize**: `python run_animation.py --args '{"fps": 60, "speed": 0.02}'`

---

*Use this document as a reference when creating new animations. Refer to sample animations for working examples.*
