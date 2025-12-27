# Holiday Lights Contest - Development Instructions

**Current Project:** Brick Breaker Game  
**Designed by:** Pat "seeknay" (from TikTok)  
**Created with:** Cursor AI Assistant  
**Purpose:** For fun and learning - NOT a contest entry

---

## Project Overview

This is a Python-based animation framework for creating 3D light animations for a programmable Christmas tree with 500 LEDs. The current implementation is a fully playable Brick Breaker game that showcases advanced 3D spatial programming, game physics, and AI-controlled gameplay.

This project was created as a learning experience exploring LED programming, spatial algorithms, and AI-assisted development. Feel free to use and learn from this code!

**Key Details:**
- **NUM_PIXELS**: 500 (hardcoded in `lib/constants.py`)
- **Python Version**: 3.10 or higher
- **Main Dependencies**: numpy, matplotlib, typeguard
- **Contest Deadline**: January 11, 2026 at 11:59 pm (not participating for prizes)

## Project Structure

```
.
├── animation.py              # Main animation file (current: Brick Breaker game)
├── run_animation.py          # Entry point script
├── samples/                  # Example animations
│   ├── down_the_line.py     # 1D animation with decay
│   ├── red_green_swap.py    # Simple alternating pattern
│   └── sweeping_planes.py   # 3D geometric animation
├── utils/                    # Utility functions
│   ├── colors.py            # Color conversion utilities
│   ├── geometry.py          # 3D point coordinates (POINTS_3D)
│   ├── validation.py        # Parameter validation helpers
│   └── points/
│       └── 3dpoints.npy     # 3D coordinate data (500, 3) array
├── lib/                      # Framework library (don't modify)
│   ├── base_animation.py    # BaseAnimation class
│   ├── base_controller.py   # BaseController class
│   ├── matplotlib_controller.py # Matplotlib visualization
│   └── constants.py         # NUM_PIXELS = 500
├── tree_points.json          # 3D points exported for web viewer
├── brickbreaker_viewer.html  # Web-based game viewer (Three.js)
├── requirements.txt
└── README.md
```

## Core Architecture

### BaseAnimation Class (`lib/base_animation.py`)

All animations must inherit from `BaseAnimation`. Key methods and properties:

**Required Methods:**
- `__init__(self, frameBuf: np.ndarray, *, fps: Optional[int] = None, ...)`
  - `frameBuf`: numpy array of shape `(500, 3)` for RGB values (0-255)
  - `fps`: Optional frames per second (None = run as fast as possible)
  - Additional parameters must be keyword-only (use `*` separator)
  
- `renderNextFrame(self) -> None`
  - Called every frame
  - Update `self.frameBuf` with RGB values (0-255)
  - Shape: `(NUM_PIXELS, 3)` where each row is `[R, G, B]`

**Optional Methods:**
- `shutdown(self)`: Cleanup when animation stops
- `validate_parameters(cls, parameters)`: Custom parameter validation

**Properties:**
- `self.frameBuf`: The pixel buffer (numpy array, shape `(500, 3)`)
- `self.fps`: Frames per second (None or int)
- `self.period`: Time per frame in seconds (1/fps if fps is set, else 0)

**Class Methods:**
- `get_default_parameters(cls)`: Returns dict of default parameter values
- `validate_parameters(cls, parameters)`: Validates parameters (can override)
- `serialize_parameters(cls, parameters)`: Serialize for storage
- `deserialize_parameters(cls, parameters)`: Deserialize from storage

### Animation Execution Flow

1. `run_animation.py` loads animation class from `animation.py` or sample
2. Creates `MatplotlibController` instance
3. Controller creates animation instance with `frameBuf` and parameters
4. Controller calls `renderNextFrame()` in a loop
5. Each frame is displayed in matplotlib 3D scatter plot
6. Frame rate is controlled by `fps` parameter

## Creating Animations

### Basic Animation Template

```python
from lib.base_animation import BaseAnimation
from typing import Optional
import numpy as np

class MyAnimation(BaseAnimation):
    def __init__(self, frameBuf: np.ndarray, *, fps: Optional[int] = 30):
        super().__init__(frameBuf, fps=fps)
        self.t = 0  # Frame counter

    def renderNextFrame(self) -> None:
        # Update self.frameBuf with RGB values (0-255)
        for i in range(len(self.frameBuf)):
            self.frameBuf[i] = [255, 0, 0]  # Red
        self.t += 1
```

### Animation with Custom Parameters

```python
from lib.base_animation import BaseAnimation
from typing import Optional, Collection
from utils.validation import is_valid_rgb_color

class SolidColor(BaseAnimation):
    def __init__(self, frameBuf, *, fps: Optional[int] = None,
                 color: Collection[int] = (255, 255, 255)):
        super().__init__(frameBuf, fps=fps)
        self.color = color

    def renderNextFrame(self):
        self.frameBuf[:] = self.color

    @classmethod
    def validate_parameters(cls, parameters):
        super().validate_parameters(parameters)
        full_parameters = {**cls.get_default_parameters(), **parameters}
        color = full_parameters['color']
        if not is_valid_rgb_color(color):
            raise TypeError("color must be a valid rgb color tuple")
```

**Key Points:**
- All custom parameters must be keyword-only (after `*`)
- Use `validate_parameters()` for custom validation
- Access defaults with `cls.get_default_parameters()`
- Merge user parameters: `{**cls.get_default_parameters(), **parameters}`

## Available Utilities

### Color Utilities (`utils/colors.py`)

**HSV/RGB Conversion:**
- `hsv_to_rgb(h, s, v)` → `[R, G, B]` (0-255)
  - `h`: hue (0-1)
  - `s`: saturation (0-1)
  - `v`: value/brightness (0-1)
  
- `rgb_to_hsv(r, g, b)` → `(h, s, v)` (0-1)
  - Input: RGB values (0-255)

**Numpy Array Versions:**
- `rgb_to_hsv_numpy(rgb)` → HSV array (shape `(N, 3)`)
- `hsv_to_rgb_numpy(hsv)` → RGB array (shape `(N, 3)`)

**Helper Functions:**
- `randomColor()` → Random RGB tuple `[R, G, B]` (0-255)
- `rainbowFrame(t, NUM_PIXELS)` → List of RGB tuples for rainbow gradient
- `brightnessFrame(color, NUM_PIXELS)` → Brightness gradient from color
- `decayPixel(r, g, b, decayRate)` → Decayed color (HSV brightness decay)
- `desaturatePixel(r, g, b, desaturationRate)` → Desaturated color

### Geometry Utilities (`utils/geometry.py`)

- `POINTS_3D`: Numpy array of shape `(500, 3)` containing (x, y, z) coordinates for each pixel
  - Each row is `[x, y, z]` coordinate
  - Use for 3D spatial animations

**Common 3D Patterns:**
- **Centering points**: `CENTERED_POINTS_3D = POINTS_3D - np.mean(POINTS_3D, axis=0)`
- **Distance from origin**: `distances = np.linalg.norm(POINTS_3D, axis=1)`
- **Distance from point**: `distances = np.linalg.norm(POINTS_3D - point, axis=1)`
- **Plane distance**: `distances = np.abs(np.dot(POINTS_3D, plane_normal) + d)`
- **Sphere**: `distances = np.linalg.norm(POINTS_3D - center, axis=1) - radius`

### Validation Utilities (`utils/validation.py`)

- `is_valid_rgb_color(color)` → bool
  - Checks if color is tuple/list of 3 integers in range [0, 255]
  
- `is_valid_inclusive_range(r, m, M)` → bool
  - Validates range `r` is within bounds `[m, M]`

## Sample Animations Analysis

### 1. `red_green_swap.py` - Simple 1D Pattern

**Pattern**: Alternates red/green based on frame and pixel index
- Even frames: even indices = red, odd indices = green
- Odd frames: even indices = green, odd indices = red

**Key Techniques:**
- Simple boolean logic for pattern
- Frame counter (`self.t`)
- Direct RGB tuple assignment

### 2. `down_the_line.py` - 1D Animation with Decay

**Pattern**: Moving light that travels down the line with color decay

**Key Techniques:**
- Multiple pixels lit simultaneously (`rate` parameter)
- Color decay: `frameBuf[i] = tuple(int(c * decay) for c in frameBuf[i])`
- Random color generation: `randomColor()` from utils
- Parameter validation for `rate > 0` and `decay in [0, 1)`

**Parameters:**
- `rate: int = 10`: Number of pixels to light up
- `decay: float = 0.9`: Decay factor per frame (0-1)

### 3. `sweeping_planes.py` - 3D Geometric Animation

**Pattern**: Colored planes sweep through 3D space

**Key Techniques:**
- **3D coordinate usage**: `POINTS_3D` from `utils.geometry`
- **Centering points**: `CENTERED_POINTS_3D = POINTS_3D - mid_point`
- **Plane distance calculation**: `np.abs(np.dot(points, plane_normal) + d)`
- **Bandwidth filtering**: `within = distances < bandwidth`
- **Decay for non-lit pixels**: `frameBuf[~within] *= decay`
- **Plane movement**: `point += plane * speed`
- **Random plane generation**: Normalized random vector on sphere

**Parameters:**
- `speed: float = 0.01`: Plane movement speed
- `bandwidth: float = 0.2`: Thickness of lit band
- `decay: float = 0.85`: Decay for non-lit pixels

### 4. `animation.py` (Current) - Brick Breaker Game

**Pattern**: Classic Brick Breaker game on the tree using YZ plane projection with rotating gameplay

**Key Techniques:**
- **Sequential Brick Structure**: Bricks are groups of consecutive light indices (5 lights per brick)
- **YZ Plane Projection**: Uses Y (horizontal) and Z (vertical) coordinates for 2D game logic
- **Rotating Gameplay**: Game rotates around tree, cycling through 6 different faces between games
- **3D Spatial Collision**: Each brick has Y and Z bounds for precise collision detection
- **Game state management**: Ball position/velocity, paddle position, individual brick states
- **Collision detection**: Ball vs walls, paddle, and individual bricks
- **Auto-paddle AI**: Paddle follows ball with configurable lag
- **Win/Loss Animations**: Rainbow wave effect for wins, white wash for losses

**Current Configuration:**
- **47 bricks** (5 lights each) distributed in upper 60% of tree
- **Colors**: Alternating red and green (brick index % 2)
- **Paddle**: Width 0.25, AI-controlled, follows ball
- **Ball**: Speed 0.015, radius 0.05, bounces off walls/paddle/bricks
- **Lives**: Ball can fall 3 times before game over
- **Auto-reset**: Game automatically restarts after win/loss animations

**Parameters:**
- `fps: int = 30`: Frame rate
- `ball_speed: float = 0.015`: Ball movement speed
- `paddle_speed: float = 0.02`: Paddle AI movement speed
- `paddle_width: float = 0.25`: Paddle width in game coordinates
- `lights_per_brick: int = 5`: Number of lights per brick
- `rotation_speed: float = 0.003`: Rotation speed around tree

**Game Elements:**
- **Paddle** (white): Horizontal bar at bottom, AI-controlled to follow ball
- **Ball** (yellow): Bounces around, breaks bricks on contact
- **Bricks** (red/green): Sequential groups of 5 lights that alternate colors
- **Win animation**: Rainbow wave effect with smooth color transitions (3 seconds)
- **Loss animation**: White wash cascading from top to bottom (4 seconds)

**Implementation Details:**
- Bricks created from sequential light indices in upper tree portion
- Each brick tracks: indices, active state, z_min, z_max, y_min, y_max
- Collision uses spatial bounds rather than Z-slice detection
- Rotation uses angle tracking and projects visible face to game plane
- Win/loss states trigger special animations before auto-reset

## Running Animations

### Basic Commands

```bash
# Run animation.py with defaults
python run_animation.py

# Run with custom parameters (JSON format)
python run_animation.py --args '{"fps": 60, "color": [255, 0, 0]}'

# Change background color
python run_animation.py --background white

# Skip parameter validation
python run_animation.py --no_validation

# List available samples
python run_animation.py --list-samples

# Run a sample directly
python run_animation.py --sample red_green_swap
python run_animation.py --sample down_the_line
python run_animation.py --sample sweeping_planes

# Run Brick Breaker game (current animation.py)
python run_animation.py

# Brick Breaker with custom parameters
python run_animation.py --args '{"ball_speed": 0.02}'        # Faster ball
python run_animation.py --args '{"lights_per_brick": 8}'     # Larger bricks (fewer total)
python run_animation.py --args '{"paddle_width": 0.3}'       # Wider paddle
python run_animation.py --args '{"rotation_speed": 0.005}'   # Faster rotation
```

### Command-Line Arguments

- `--args`: JSON string with animation parameters
- `--no_validation`: Skip parameter validation
- `--sample <name>`: Run sample animation by name
- `--list-samples`: List all available samples
- `--background <color>`: Background color (default: 'gray')

## Best Practices

### 1. Parameter Design
- Always use keyword-only arguments (after `*`)
- Provide sensible defaults
- Validate parameters in `validate_parameters()` method
- Use type hints for better IDE support

### 2. Performance
- Use numpy vectorized operations when possible
- Avoid Python loops for pixel updates when you can use array operations
- Example: `self.frameBuf[:] = color` (vectorized) vs loop

### 3. Color Management
- RGB values must be integers in range [0, 255]
- Use HSV for smooth color transitions
- Use `hsv_to_rgb()` for color generation
- Consider brightness/decay in HSV space

### 4. 3D Animations
- Center points around origin for easier calculations
- Use `np.linalg.norm()` for distances
- Use dot products for plane calculations
- Consider bandwidth/thickness for geometric effects

### 5. Frame Timing
- Use `self.t` or similar counter for time-based animations
- Consider `self.fps` for animation speed
- Use `self.period` if you need frame timing info

### 6. Code Organization
- Import utilities from `utils/` modules
- Use constants from `lib.constants` (NUM_PIXELS)
- Follow sample animation patterns
- Add docstrings to animation classes

## Common Patterns

### Pattern 1: Solid Color
```python
def renderNextFrame(self):
    self.frameBuf[:] = self.color
```

### Pattern 2: Color Cycle
```python
def renderNextFrame(self):
    for i in range(len(self.frameBuf)):
        hue = (i + self.t) / len(self.frameBuf)
        self.frameBuf[i] = hsv_to_rgb(hue, 1.0, 1.0)
    self.t += 1
```

### Pattern 3: Moving Wave
```python
def renderNextFrame(self):
    for i in range(len(self.frameBuf)):
        phase = (i + self.t * self.speed) / len(self.frameBuf)
        brightness = 0.5 + 0.5 * np.sin(phase * 2 * np.pi)
        self.frameBuf[i] = [int(c * brightness) for c in self.color]
    self.t += 1
```

### Pattern 4: Distance-Based (3D)
```python
from utils.geometry import POINTS_3D
import numpy as np

def renderNextFrame(self):
    center = np.array([0, 0, 0])
    distances = np.linalg.norm(POINTS_3D - center, axis=1)
    within = distances < self.radius
    self.frameBuf[within] = self.color
    self.frameBuf[~within] = 0
```

### Pattern 5: Decay Effect
```python
def renderNextFrame(self):
    # Apply decay to all pixels
    self.frameBuf = (self.frameBuf * self.decay).astype(np.uint8)
    # Add new light
    self.frameBuf[self.current_pixel] = self.color
```

### Pattern 6: YZ Plane Projection (Front View)
```python
from utils.geometry import POINTS_3D
import numpy as np

def __init__(self, frameBuf, *, fps=30):
    super().__init__(frameBuf, fps=fps)
    # Center points and extract YZ coordinates
    self.center = np.mean(POINTS_3D, axis=0)
    self.centered = POINTS_3D - self.center
    self.y = self.centered[:, 1]  # Horizontal
    self.z = self.centered[:, 2]  # Vertical

def renderNextFrame(self):
    # Draw horizontal bar at height z=0.2
    bar_height = 0.2
    bar_thickness = 0.05
    in_bar = np.abs(self.z - bar_height) < bar_thickness
    self.frameBuf[:] = [0, 0, 0]  # Background
    self.frameBuf[in_bar] = [255, 0, 0]  # Red bar
```

### Pattern 7: Game Loop Structure
```python
def __init__(self, frameBuf, *, fps=30):
    super().__init__(frameBuf, fps=fps)
    self.game_state = "playing"  # playing, won, lost
    self.frame = 0

def _update_game_logic(self):
    """Separate game logic from rendering."""
    # Move objects, check collisions, update state
    pass

def _render_frame(self):
    """Render current game state to frameBuf."""
    self.frameBuf[:] = self.bg_color
    # Draw game objects based on state
    pass

def renderNextFrame(self):
    self.frame += 1
    self._update_game_logic()
    self._render_frame()
```

## Development Workflow

1. **Setup Environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Create Animation**
   - Edit `animation.py` with your animation class
   - Or copy a sample: `cp samples/sweeping_planes.py animation.py`

3. **Test Animation**
   ```bash
   python run_animation.py
   ```

4. **Iterate**
   - Modify `animation.py`
   - Re-run to see changes
   - Press Ctrl+C to stop

5. **Test with Parameters**
   ```bash
   python run_animation.py --args '{"fps": 60, "speed": 0.02}'
   ```

6. **Submission**
   - Submit via Google Form or Pull Request
   - Include screen recording if possible
   - Note any special configuration requirements

## Web-Based Debugging (Optional)

For faster iteration, you can use a web-based Three.js viewer instead of matplotlib:

### Setup Web Viewer

1. **Export tree coordinates to JSON** (one-time):
   ```python
   import json
   import numpy as np
   from utils.geometry import POINTS_3D
   
   points_list = POINTS_3D.tolist()
   with open('tree_points.json', 'w') as f:
       json.dump(points_list, f)
   ```

2. **Start local server**:
   ```bash
   python3 -m http.server 8000 &
   ```

3. **Create HTML viewer** (see `brickbreaker_viewer.html` for example)

4. **Open in browser**: `http://localhost:8000/your_viewer.html`

### Benefits
- **Faster iteration**: No matplotlib window startup time
- **Interactive controls**: Rotate, zoom, adjust parameters in real-time
- **Visual debugging**: Immediate feedback on pattern changes

### Tree Coordinate System
- **X**: Front-to-back (use for "front face" filtering)
- **Y**: Left-to-right (horizontal position)
- **Z**: Bottom-to-top (vertical height)
- **Center**: `np.mean(POINTS_3D, axis=0)`
- **Typical ranges**: Y: [-0.4, 0.4], Z: [-0.45, 0.6]

## Troubleshooting

### Common Issues

1. **"No animation class found"**
   - Ensure class inherits from `BaseAnimation`
   - Ensure class is not named `BaseAnimation`
   - Check file has exactly one animation class

2. **"Unknown parameter"**
   - Parameter not in `__init__` defaults
   - Check parameter name spelling
   - Use `--no_validation` to skip (not recommended)

3. **Colors not displaying**
   - Ensure RGB values are integers [0, 255]
   - Check `frameBuf` shape is `(500, 3)`
   - Verify values are not floats > 1.0

4. **Animation too fast/slow**
   - Set `fps` parameter
   - Use `--args '{"fps": 30}'` for 30 FPS

5. **3D coordinates not working**
   - Import: `from utils.geometry import POINTS_3D`
   - Shape is `(500, 3)`, not `(3, 500)`
   - Use `axis=1` for row-wise operations

6. **Pattern looks "wrapped" or distorted**
   - The tree is a 3D spiral, not a flat surface
   - Use YZ plane projection for "front view" patterns
   - Center points first: `centered = POINTS_3D - np.mean(POINTS_3D, axis=0)`
   - Use Y for horizontal, Z for vertical positioning

7. **Game elements not visible**
   - Increase element sizes (ball_radius, paddle_width, brick_height)
   - Check Z coordinate bounds match tree geometry
   - Print debug info: `print(f"Lit pixels: {(frameBuf.sum(axis=1) > 0).sum()}")`

## Submission Guidelines

- **Multiple submissions welcome**: Submit as many as you like
- **Screen recording**: Highly encouraged
- **Configuration notes**: Document any special parameters
- **Submission methods**:
  1. Google Form
  2. Pull Request (fork repo, edit `animation.py`, open PR)

## Notes

- Animation runs in matplotlib 3D scatter plot window
- Press Ctrl+C to stop animation
- `NUM_PIXELS` is hardcoded to 500 (matches physical tree)
- All animations must inherit from `BaseAnimation`
- Parameters are validated by default (use `--no_validation` to skip)
- Background color defaults to 'gray' but can be changed

