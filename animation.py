"""
Brick Breaker Game on the Christmas Tree!
- Platform at the bottom moves left/right
- Ball bounces and breaks bricks
- Bricks are sequential groups of lights that alternate colors
"""
from lib.base_animation import BaseAnimation
from typing import Optional
from utils.geometry import POINTS_3D
import numpy as np

class BrickBreaker(BaseAnimation):
    """
    Classic Brick Breaker game displayed on the tree.
    Uses YZ plane (front view) for game coordinates.
    """
    
    def __init__(self, frameBuf: np.ndarray, *, 
                 fps: Optional[int] = 30,
                 ball_speed: float = 0.015,
                 paddle_speed: float = 0.02,
                 paddle_width: float = 0.25,
                 lights_per_brick: int = 5,
                 rotation_speed: float = 0.003):
        super().__init__(frameBuf, fps=fps)
        
        self.ball_speed = ball_speed
        self.paddle_speed = paddle_speed
        self.paddle_width = paddle_width
        self.lights_per_brick = lights_per_brick
        self.rotation_speed = rotation_speed  # Rotation speed around tree
        
        # Center the points
        self.center = np.mean(POINTS_3D, axis=0)
        self.centered = POINTS_3D - self.center
        
        # Store full 3D coordinates
        self.x = self.centered[:, 0]  # front-to-back
        self.y = self.centered[:, 1]  # left-to-right
        self.z = self.centered[:, 2]  # vertical
        
        # Calculate angles in XY plane for rotation
        self.xy_angles = np.arctan2(self.y, self.x)  # Angle around tree
        self.xy_distances = np.sqrt(self.x**2 + self.y**2)  # Distance from center in XY plane
        
        # Initial rotation angle - start on first face
        self.game_count = 0  # Track number of games to cycle through faces
        self.faces_per_cycle = 6  # Number of different faces to cycle through
        # Set initial rotation to first face
        self.rotation_angle = 0.0
        
        # Normalize to game coordinates (will be recalculated based on visible face)
        self.z_min, self.z_max = self.z.min(), self.z.max()
        
        # Find unique Z coordinates (rows) for snapping paddle to a single row
        z_rounded = np.round(self.z, decimals=3)
        self.unique_z_rows = np.unique(z_rounded)
        self.z_row_spacing = np.min(np.diff(np.sort(self.unique_z_rows))) if len(self.unique_z_rows) > 1 else 0.01
        
        # Game boundaries - use reasonable defaults for projected coordinates
        # Projected Y will be in range approximately [-0.4, 0.4] based on tree radius
        self.left_wall = -0.35
        self.right_wall = 0.35
        self.top_wall = self.z_max - 0.05
        self.bottom = self.z_min + 0.05
        
        # Paddle - snap to nearest row
        target_paddle_z = self.z_min + 0.12  # Desired position
        self.paddle_z = self._snap_to_row(target_paddle_z)  # Snapped to actual row
        self.paddle_y = 0.0  # Horizontal position (center)
        self.paddle_height = self.z_row_spacing * 0.8  # Very small, just for collision detection
        self.paddle_direction = 1  # 1 = right, -1 = left
        
        # Ball
        self.ball_y = 0.0
        self.ball_z = self.paddle_z + 0.15
        self.ball_vy = ball_speed * 0.7  # Horizontal velocity
        self.ball_vz = ball_speed  # Vertical velocity
        self.ball_radius = 0.05  # Larger ball for visibility
        
        # Bricks: sequential groups of lights
        # Create bricks from sequential light indices
        # Only create bricks in the upper portion of the tree
        num_lights = len(POINTS_3D)
        
        # Filter lights to only use those in the upper 60% of the tree
        upper_threshold = self.z_min + (self.z_max - self.z_min) * 0.4
        upper_indices = np.where(self.z >= upper_threshold)[0]
        
        # Create bricks from filtered indices
        self.bricks = []
        num_full_bricks = len(upper_indices) // lights_per_brick
        
        for i in range(num_full_bricks):
            start_idx = i * lights_per_brick
            end_idx = start_idx + lights_per_brick
            brick_indices = upper_indices[start_idx:end_idx].tolist()
            
            # Calculate brick properties
            brick_z_values = self.z[brick_indices]
            brick_y_values = self.y[brick_indices]
            
            self.bricks.append({
                'indices': brick_indices,
                'active': True,
                'z_min': np.min(brick_z_values),
                'z_max': np.max(brick_z_values),
                'z_center': np.mean(brick_z_values),
                'y_min': np.min(brick_y_values),
                'y_max': np.max(brick_y_values),
                'y_center': np.mean(brick_y_values),
            })
        
        # Colors - alternate red and green
        self.bg_color = np.array([5, 5, 20])  # Dark blue background
        self.paddle_color = np.array([255, 255, 255])  # White paddle
        self.ball_color = np.array([255, 255, 0])  # Yellow ball
        # Bricks alternate red and green
        self.brick_colors = [
            np.array([255, 0, 0]),    # Red
            np.array([0, 255, 0]),     # Green
        ]
        
        self.game_over = False
        self.won = False
        self.lost = False
        self.win_animation_frames = 0  # Track win animation duration
        self.loss_animation_frames = 0  # Track loss animation duration
        self.ball_fall_count = 0  # Track number of times ball has fallen
        self.last_brick_hit = -1  # Track last brick hit to prevent multiple hits
        self.brick_hit_cooldown = 0  # Cooldown frames before another brick can be hit
        self.frame_count = 0
        
        print(f"Brick Breaker initialized!")
        print(f"Game area: Y=[{self.left_wall:.2f}, {self.right_wall:.2f}], Z=[{self.bottom:.2f}, {self.top_wall:.2f}]")
        print(f"Total bricks: {len(self.bricks)} ({lights_per_brick} lights per brick)")
        print(f"Paddle snapped to Z={self.paddle_z:.4f}, row spacing={self.z_row_spacing:.4f}")
        print(f"Rotation speed: {rotation_speed}")
    
    def _get_visible_face_coordinates(self):
        """Calculate which lights are on the visible face and their projected coordinates."""
        # Calculate relative angle from current rotation
        relative_angles = self.xy_angles - self.rotation_angle
        # Normalize to [-pi, pi]
        relative_angles = np.arctan2(np.sin(relative_angles), np.cos(relative_angles))
        
        # Define visible face as lights within ±90 degrees of front (0 degrees)
        # Use a wider angle for smoother transitions
        face_angle_tolerance = np.pi * 0.6  # 108 degrees visible arc
        visible = np.abs(relative_angles) < face_angle_tolerance
        
        # Project visible lights: use distance * sin(angle) as horizontal position
        # This creates a curved "front view" that rotates around the tree
        projected_y = self.xy_distances * np.sin(relative_angles)
        
        return visible, projected_y
    
    def _snap_to_row(self, z_position):
        """Snap a Z position to the nearest actual row of lights."""
        if len(self.unique_z_rows) == 0:
            return z_position
        idx = np.argmin(np.abs(self.unique_z_rows - z_position))
        return self.unique_z_rows[idx]
    
    def _move_paddle(self):
        """Move paddle automatically (follows ball with some lag)."""
        # Simple AI: move toward ball
        if self.ball_y > self.paddle_y + 0.02:
            self.paddle_y += self.paddle_speed
        elif self.ball_y < self.paddle_y - 0.02:
            self.paddle_y -= self.paddle_speed
        
        # Clamp to boundaries
        half_width = self.paddle_width / 2
        self.paddle_y = np.clip(self.paddle_y, self.left_wall + half_width, self.right_wall - half_width)
    
    def _move_ball(self):
        """Move ball and handle collisions."""
        # Move ball
        self.ball_y += self.ball_vy
        self.ball_z += self.ball_vz
        
        # Wall collisions
        if self.ball_y <= self.left_wall or self.ball_y >= self.right_wall:
            self.ball_vy = -self.ball_vy
            self.ball_y = np.clip(self.ball_y, self.left_wall, self.right_wall)
        
        if self.ball_z >= self.top_wall:
            self.ball_vz = -self.ball_vz
            self.ball_z = self.top_wall
        
        # Paddle collision - use reasonable collision zone for gameplay
        # Visual paddle is on single row, but collision zone is slightly larger
        collision_height = 0.04  # Reasonable collision zone
        if (self.ball_z <= self.paddle_z + collision_height and 
            self.ball_z >= self.paddle_z - self.ball_radius and
            abs(self.ball_y - self.paddle_y) < self.paddle_width / 2):
            self.ball_vz = abs(self.ball_vz)  # Bounce up
            # Add some angle based on where ball hits paddle
            hit_pos = (self.ball_y - self.paddle_y) / (self.paddle_width / 2)
            self.ball_vy = hit_pos * self.ball_speed
        
        # Brick collisions - with cooldown to prevent multiple hits
        if self.brick_hit_cooldown > 0:
            self.brick_hit_cooldown -= 1
        else:
            for i, brick in enumerate(self.bricks):
                if not brick['active']:
                    continue
                
                # Check if ball is within the brick's Z and Y range
                # Add some tolerance for better collision detection
                z_tolerance = 0.03
                y_tolerance = 0.05
                
                if (self.ball_z >= brick['z_min'] - z_tolerance and 
                    self.ball_z <= brick['z_max'] + z_tolerance and
                    self.ball_y >= brick['y_min'] - y_tolerance and
                    self.ball_y <= brick['y_max'] + y_tolerance):
                    brick['active'] = False
                    self.ball_vz = -self.ball_vz
                    self.last_brick_hit = i
                    self.brick_hit_cooldown = 5  # 5 frame cooldown before next brick can be hit
                    break
        
        # Ball falls below paddle - loss every third time, otherwise reset
        if self.ball_z < self.bottom - 0.1:
            # Only if not already won or lost
            if not self.won and not self.lost:
                self.ball_fall_count += 1
                # Loss on every 3rd fall
                if self.ball_fall_count % 3 == 0:
                    self.lost = True
                    self.loss_animation_frames = 0  # Start loss animation
                else:
                    self._reset_ball()
            else:
                self._reset_ball()
        
        # Check win condition
        if not any(brick['active'] for brick in self.bricks) and not self.won:
            self.won = True
            self.win_animation_frames = 0  # Start win animation
    
    def _reset_ball(self):
        """Reset ball to starting position."""
        self.ball_y = self.paddle_y
        self.ball_z = self.paddle_z + 0.1
        self.ball_vz = abs(self.ball_vz)  # Go up
    
    def _reset_game(self):
        """Reset the entire game."""
        # Reset all bricks to active
        for brick in self.bricks:
            brick['active'] = True
        
        self._reset_ball()
        self.won = False
        self.lost = False
        self.win_animation_frames = 0
        self.loss_animation_frames = 0
        self.ball_fall_count = 0  # Reset fall count for new game
        self.last_brick_hit = -1  # Reset brick hit tracking
        self.brick_hit_cooldown = 0  # Reset cooldown
        
        # Start each new game on a different face
        self.game_count += 1
        # Rotate to a new face (distribute evenly around the tree)
        face_angle = (2 * np.pi / self.faces_per_cycle) * (self.game_count % self.faces_per_cycle)
        self.rotation_angle = face_angle
    
    def renderNextFrame(self) -> None:
        """Render one frame of the game."""
        self.frame_count += 1
        
        # Update rotation angle
        self.rotation_angle += self.rotation_speed
        if self.rotation_angle > 2 * np.pi:
            self.rotation_angle -= 2 * np.pi
        elif self.rotation_angle < 0:
            self.rotation_angle += 2 * np.pi
        
        # Handle loss animation
        if self.lost:
            self.loss_animation_frames += 1
            loss_duration = 120  # 4 seconds at 30fps
            
            if self.loss_animation_frames >= loss_duration:
                # Animation complete, reset game
                self._reset_game()
            else:
                # Show loss effect
                self._render_loss_effect()
                return
        
        # Handle win animation
        if self.won:
            self.win_animation_frames += 1
            win_duration = 90  # 3 seconds at 30fps
            
            if self.win_animation_frames >= win_duration:
                # Animation complete, reset game
                self._reset_game()
            else:
                # Show win celebration effect
                self._render_win_celebration()
                return
        
        # Get visible face coordinates
        visible, projected_y = self._get_visible_face_coordinates()
        
        # Update game state
        self._move_paddle()
        self._move_ball()
        
        # Clear to background
        self.frameBuf[:] = self.bg_color
        
        # Draw bricks - each brick is a specific set of sequential light indices
        for i, brick in enumerate(self.bricks):
            if not brick['active']:
                continue
            
            # Set color for all lights in this brick
            # Alternate red and green based on brick index
            color = self.brick_colors[i % len(self.brick_colors)]
            for light_idx in brick['indices']:
                self.frameBuf[light_idx] = color
        
        # Draw paddle - use projected Y coordinate for horizontal position
        # Increase z tolerance to ensure visibility (allow for slight variations)
        z_tolerance = max(self.z_row_spacing * 1.5, 0.03)  # More lenient tolerance to catch nearby lights
        in_paddle = (
            visible &
            (np.abs(projected_y - self.paddle_y) < self.paddle_width / 2) &
            (np.abs(self.z - self.paddle_z) < z_tolerance)
        )
        self.frameBuf[in_paddle] = self.paddle_color
        
        # Draw ball - use projected coordinates
        ball_dist = np.sqrt((projected_y - self.ball_y)**2 + (self.z - self.ball_z)**2)
        in_ball = visible & (ball_dist < self.ball_radius)
        self.frameBuf[in_ball] = self.ball_color
    
    def _render_win_celebration(self):
        """Render a celebration effect when the game is won."""
        from utils.colors import hsv_to_rgb_numpy
        
        # Create a smooth rainbow effect with slow transitions
        center_y = 0.0
        center_z = (self.z_min + self.z_max) / 2
        
        # Calculate distance from center for each point (vectorized)
        distances = np.sqrt((self.y - center_y)**2 + (self.z - center_z)**2)
        max_dist = np.max(distances)
        
        # Calculate angles for rainbow effect (vectorized)
        angles = np.arctan2(self.z - center_z, self.y - center_y)
        
        # Slow hue rotation - much slower transition
        hue_rotation_speed = 0.005  # Very slow rotation
        hue_base = (angles / (2 * np.pi) + self.win_animation_frames * hue_rotation_speed) % 1.0
        
        # Create slow expanding waves
        wave_speed = 0.003  # Much slower wave expansion
        wave_offset = self.win_animation_frames * wave_speed
        wave_period = max_dist * 2.0  # Longer period for smoother transitions
        
        # Three expanding waves offset from each other
        wave1_dist = (wave_offset) % wave_period
        wave2_dist = (wave_offset + max_dist * 0.4) % wave_period
        wave3_dist = (wave_offset + max_dist * 0.8) % wave_period
        
        # Distance from each wave (vectorized)
        wave1_diff = np.abs(distances - wave1_dist)
        wave2_diff = np.abs(distances - wave2_dist)
        wave3_diff = np.abs(distances - wave3_dist)
        
        # Wider, smoother waves with gradual falloff
        wave_width = 0.25  # Wider waves for smoother transitions
        brightness1 = np.maximum(0, 1.0 - (wave1_diff / wave_width))
        brightness2 = np.maximum(0, 1.0 - (wave2_diff / wave_width))
        brightness3 = np.maximum(0, 1.0 - (wave3_diff / wave_width))
        
        # Combine waves smoothly
        brightness = np.maximum(np.maximum(brightness1, brightness2), brightness3)
        
        # Very gentle pulsing - much slower and subtler
        pulse_speed = 0.03  # Very slow pulse
        pulse = 0.7 + 0.3 * np.sin(self.win_animation_frames * pulse_speed)
        final_brightness = brightness * pulse
        
        # Ensure minimum brightness so it's always visible
        final_brightness = np.maximum(final_brightness, 0.3)
        
        # Create HSV array
        saturation = np.ones_like(hue_base) * 0.9  # Slightly less saturated for smoother look
        hsv = np.column_stack([hue_base, saturation, final_brightness])
        
        # Convert to RGB (vectorized)
        rgb = hsv_to_rgb_numpy(hsv)
        self.frameBuf[:] = (rgb * 255).astype(np.uint8)
    
    def _render_loss_effect(self):
        """Render a white wash effect from top to bottom when the game is lost."""
        # Calculate progress of the wash (0.0 at top, 1.0 at bottom)
        # Animation duration is 120 frames, so we want a slow wash
        progress = self.loss_animation_frames / 120.0  # 0 to 1 over 4 seconds
        
        # Normalize Z coordinates to 0-1 range for easier calculation
        z_range = self.z_max - self.z_min
        z_normalized = (self.z - self.z_min) / z_range  # 0 at bottom, 1 at top
        
        # Invert so 0 is at top, 1 is at bottom
        z_from_top = 1.0 - z_normalized
        
        # Create white wash: lights above the progress line turn white
        # Use a smooth transition band for the wash edge
        wash_bandwidth = 0.15  # Width of the transition band
        wash_position = progress * (1.0 + wash_bandwidth)  # Extend slightly beyond 1.0
        
        # Calculate brightness based on position relative to wash
        # Lights above the wash are fully white, lights below fade out
        distance_from_wash = wash_position - z_from_top
        
        # Brightness: 1.0 if above wash, fade to 0.0 in the band, 0.0 below
        brightness = np.clip(1.0 - (distance_from_wash / wash_bandwidth), 0.0, 1.0)
        
        # Apply white color with calculated brightness
        # brightness is shape (500,), need to broadcast to (500, 3)
        white_color = np.array([255, 255, 255])
        self.frameBuf[:] = (white_color * brightness[:, np.newaxis]).astype(np.uint8)
