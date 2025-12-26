# Tarabyte Holiday Lights Contest

In honor of the holidays, Tara and family are launching a competition to see who can write the best animation for their programmable Christmas Tree.

## Competition Details

**Submission Deadline:** January 11, 2026 at 11:59 pm

### How to Submit

You can submit your animation in one of two ways:

1. **Google Form**: Submit your code via the Google Form (link to be provided)
2. **Pull Request**: Fork this repository, create your animation in `animation.py`, and open a Pull Request

### Submission Guidelines

- **Multiple Submissions Welcome**: You can submit as many animations as you like! Just make separate submissions for each one.
- **Screen Recording**: Including a screen recording of your animation running in the simulator would be awesome (highly encouraged if you can!)
- **Configuration Notes**: Please let us know if there's a particular configuration to run your animation with (e.g., specific FPS, parameters, etc.)

### What Happens Next

- We'll try all submissions on the actual tree
- Our favorite animations will be featured on TikTok
- The community will vote on their favorites
- **Top 3 winners will receive prizes!**

# Tree Lights Animation Runner

A simplified animation runner for creating and visualizing 3D light animations using matplotlib. This repository contains everything you need to create and run a single animation.

## Requirements

- Python 3.10 or higher
- pip (Python package manager)

## Quick Start

1. **Set up a virtual environment (recommended):**

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Create your animation:**

   - Write your animation class in `animation.py`
   - You can run sample animations: `python run_animation.py --sample moving_rainbow`

4. **Run your animation:**
   ```bash
   python run_animation.py
   ```

## Creating Your Animation

Edit the called `animation.py` directly:

```python
from lib.base_animation import BaseAnimation
from typing import Optional
import numpy as np

class MyAnimation(BaseAnimation):
    def __init__(self, frameBuf, *, fps: Optional[int] = 30):
        super().__init__(frameBuf, fps=fps)
        self.t = 0

    def renderNextFrame(self):
        # Update self.frameBuf with RGB values (0-255)
        # frameBuf is a numpy array of shape (NUM_PIXELS, 3)
        for i in range(len(self.frameBuf)):
            # Your animation logic here
            self.frameBuf[i] = [255, 0, 0]  # Red
        self.t += 1
```

### Key Points:

- **`frameBuf`**: A numpy array of shape `(500, 3)` containing RGB values (0-255) for each pixel
- **`fps`**: Optional frames per second (None = run as fast as possible)
- **`renderNextFrame()`**: Called every frame - update `self.frameBuf` here
- **Parameters**: Add optional parameters with defaults in `__init__` (use keyword-only args with `*`)

### Example with Parameters:

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

## Running Animations

### Basic Usage

```bash
# Run with default parameters
python run_animation.py

# Run with custom parameters (JSON format)
python run_animation.py --args '{"fps": 60, "color": [255, 0, 0]}'

# Change background color
python run_animation.py --background white

```

### Using Sample Animations

```bash
# List available samples
python run_animation.py --list-samples

# Run a sample directly
python run_animation.py --sample red_green_swap
```

## Available Utilities

### Color Utilities (`utils/colors.py`)

- `hsv_to_rgb(h, s, v)` - Convert HSV to RGB
- `rgb_to_hsv(r, g, b)` - Convert RGB to HSV
- `randomColor()` - Generate a random color
- `rainbowFrame(t, NUM_PIXELS)` - Generate rainbow gradient
- `brightnessFrame(color, NUM_PIXELS)` - Generate brightness gradient

### Geometry Utilities (`utils/geometry.py`)

- `POINTS_3D` - Numpy array of shape `(500, 3)` with 3D coordinates for each pixel

## Creating 3D Animations

You can create animations that take advantage of the 3D spatial coordinates of the lights using `POINTS_3D` from `utils.geometry`. This allows you to create effects based on the physical position of lights in 3D space, such as planes, spheres, or distance-based patterns.

### Example: Sweeping Planes

The `sweeping_planes.py` sample demonstrates how to use 3D coordinates to create geometric effects:

```python
from utils.geometry import POINTS_3D
import numpy as np

class SweepingPlanes(BaseAnimation):
    def __init__(self, frameBuf, *, fps: Optional[int] = 60,
                 speed: float = 0.01, bandwidth: float = 0.2):
        super().__init__(frameBuf, fps=fps)
        # Center the points at the origin
        min_pt = np.min(POINTS_3D, axis=0)
        max_pt = np.max(POINTS_3D, axis=0)
        mid_point = (max_pt + min_pt) / 2
        self.CENTERED_POINTS_3D = POINTS_3D - mid_point

    def renderNextFrame(self):
        # Calculate distances from a plane
        distances = np.abs(np.dot(self.CENTERED_POINTS_3D, self.plane) + d)
        within = distances < self.bandwidth
        self.frameBuf[within] = self.color
        # ... move the plane through space
```

### Key Concepts for 3D Animations:

- **`POINTS_3D`**: Array of shape `(500, 3)` containing (x, y, z) coordinates for each pixel
- **Distance calculations**: Use `np.linalg.norm()` or dot products to calculate distances from planes, spheres, or other geometric shapes
- **Centering**: You may want to center the points around the origin for easier calculations
- **Spatial patterns**: Create effects based on distance, angle, or position relative to geometric shapes

See `samples/sweeping_planes.py` for a complete example of a 3D plane-based animation.

### Validation Utilities (`utils/validation.py`)

- `is_valid_rgb_color(color)` - Validate RGB color tuple

## Sample Animations

The `samples/` folder contains example animations:

- **down_the_line.py** - 1D animation with pixels moving down the line with color decay
- **red_green_swap.py** - Simple 1D animation alternating red and green colors
- **sweeping_planes.py** - 3D animation using geometric planes that sweep through the tree

## Project Structure

```
.
├── animation.py              # Your animation (create this, or use --sample to run samples directly)
├── run_animation.py          # Main script
├── samples/                  # Example animations
│   ├── down_the_line.py
│   ├── red_green_swap.py
│   └── sweeping_planes.py
├── utils/                    # Utility functions
│   ├── colors.py            # Color utilities
│   ├── geometry.py          # 3D point coordinates
│   ├── validation.py        # Validation helpers
│   └── points/
│       └── 3dpoints.npy     # 3D coordinate data
├── lib/                      # Framework library (you don't need to modify these)
│   ├── base_animation.py    # BaseAnimation class
│   ├── base_controller.py   # BaseController class
│   ├── matplotlib_controller.py # Matplotlib visualization
│   └── constants.py        # NUM_PIXELS = 500
├── requirements.txt
└── README.md
```

## Notes

- The animation runs in a matplotlib 3D scatter plot window
- Press Ctrl+C to stop the animation
- `NUM_PIXELS` is hardcoded to 500 in `lib/constants.py`, this matches the physical tree
- All animations must inherit from `BaseAnimation`
- Parameters are validated by default (use `--no_validation` to skip)
