# Brick Breaker - Holiday Lights Contest Project Summary

**Project:** Brick Breaker Game for 500-LED Christmas Tree  
**Designed by:** Pat ([@seeknay747 on TikTok](https://www.tiktok.com/@seeknay747))  
**Created with:** Cursor AI Assistant  
**Version:** 2.1 (Grid-Based)  
**Purpose:** For fun and learning - NOT a contest entry

---

## Project Overview

An automated Brick Breaker game that runs on a 3D Christmas tree with 500 programmable LEDs. The game plays itself with an AI-controlled paddle and uses a **grid-based system** that properly maps the tree's 3D structure into a playable 2D game space.

### Key Features

- **64 Grid-Based Bricks** (8 angular sections × 8 height bands) with red/green checkerboard pattern
- **Cylindrical Coordinate System** for accurate 3D-to-2D mapping
- **Face-Aware Gameplay** - visible face (±72°) rotates slowly around tree
- **AI-Controlled Paddle** that tracks the ball automatically
- **Win/Loss Animations** - rainbow wave for wins, white wash for losses
- **Auto-Reset** - continuous gameplay with automatic restart

---

## Current Configuration

### Game Statistics
- **Total LEDs:** 500
- **Total Bricks:** 64 (8 sections × 8 bands)
- **Brick Coverage:** Upper 2/3 of tree (33% to 100% height)
- **Color Scheme:** Alternating red and green (checkerboard pattern)
- **Frame Rate:** 30 FPS
- **Visible Face:** ±72° (144° total visible)

### Game Parameters
```python
fps = 30                    # Frame rate
ball_speed = 0.02          # Ball movement speed
paddle_speed = 0.025       # Paddle AI tracking speed
paddle_width = 0.8         # Paddle width in radians (~45°)
num_sections = 8           # Angular sections (45° each)
num_bands = 8              # Height bands
rotation_speed = 0.002     # Visible face rotation speed
```

---

## Technical Implementation

### Grid-Based Architecture

The game uses a **TRUE 3D GRID system** that divides the tree into:
- **Angular Sections:** 8 sections (45° each, like pizza slices when viewed from above)
- **Height Bands:** 8 horizontal layers covering upper 2/3 of tree
- **Grid Cells:** Each brick = one cell (section × band)
- **Spatial Mapping:** LEDs assigned to bricks based on their 3D position (angle, height)

### Coordinate System

- **Cylindrical Coordinates:** (r, θ, z) for proper angular calculations
- **Ball/Paddle Tracking:** Position tracked in (angle, z) space
- **Collision Detection:** Uses angular distance with wraparound handling
- **Visible Face:** Only sections within ±72° of viewing angle are playable

### Game Mechanics

- **Ball Physics:** Velocity-based movement with bounce physics
- **Paddle AI:** Tracks ball with lag, stays within visible face
- **Collision System:** Angular distance calculations with cooldown to prevent multi-hits
- **Lives System:** 3 chances before game over
- **Win Condition:** All 64 bricks destroyed

---

## Running the Project

### Quick Start
```bash
# Setup (first time)
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run the game
python run_animation.py
```

### Custom Parameters
```bash
# Faster gameplay
python run_animation.py --args '{"ball_speed": 0.025}'

# More bricks (finer grid)
python run_animation.py --args '{"num_bands": 10, "num_sections": 12}'

# Wider paddle
python run_animation.py --args '{"paddle_width": 1.0}'

# Faster rotation
python run_animation.py --args '{"rotation_speed": 0.005}'
```

---

## Project Structure

```
holiday-lights-contest/
├── animation.py              # Main Brick Breaker implementation (v2.1)
├── run_animation.py          # Entry point script
├── INSTRUCTIONS.md           # Development documentation
├── README.md                 # Public contest README
├── PROJECT_SUMMARY.md        # This file
├── requirements.txt          # Python dependencies
│
├── lib/                      # Framework (do not modify)
│   ├── base_animation.py     # BaseAnimation class
│   ├── matplotlib_controller.py # 3D visualization
│   └── constants.py          # NUM_PIXELS = 500
│
├── utils/                    # Utility modules
│   ├── colors.py            # HSV/RGB conversion
│   ├── geometry.py          # POINTS_3D (500x3 array)
│   └── validation.py        # Parameter validation
│
└── samples/                  # Example animations
    ├── down_the_line.py
    ├── red_green_swap.py
    └── sweeping_planes.py
```

---

## Design Philosophy

### Why Grid-Based Approach Works

1. **Spatial Accuracy:** Uses actual 3D coordinates (angle, height) instead of LED string order
2. **Proper Collision Detection:** Ball bounces off bricks that are actually adjacent in 3D space
3. **Face-Aware Rendering:** Only visible face is playable, creating traditional 2D game feel
4. **Visual Clarity:** Checkerboard pattern clearly shows grid structure
5. **Scalable:** Easy to adjust grid density (sections/bands) for different gameplay

### Key Innovation

Previous versions used sequential LED indices, which didn't match the tree's 3D structure. This version uses **cylindrical coordinates** to properly map the conical tree surface into a playable 2D game grid, ensuring collisions work correctly in 3D space.

---

## Special Animations

### Win Animation (Rainbow Wave)
- Rotating rainbow effect around tree
- Pulsing brightness for dynamic feel
- Duration: 3 seconds (90 frames at 30 FPS)

### Loss Animation (White Wash)
- Cascading white wave from top to bottom
- Smooth gradient transition
- Duration: 4 seconds (120 frames at 30 FPS)