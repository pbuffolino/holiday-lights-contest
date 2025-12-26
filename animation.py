"""
Template animation file.
Replace this with your own animation class, or use --sample to run a sample animation.
"""
from lib.base_animation import BaseAnimation
from typing import Optional
import numpy as np

# Write your animation here!


class MyAnimation(BaseAnimation):
    """
    Example animation template.
    Modify this class to create your own animation.
    """

    def __init__(self, frameBuf: np.ndarray, *, fps: Optional[int] = 30) -> None:
        super().__init__(frameBuf, fps=fps)
        self.index = 0

    def renderNextFrame(self) -> None:
        """
        Called every frame. Update self.frameBuf with RGB values (0-255).
        frameBuf is a numpy array of shape (NUM_PIXELS, 3).
        """
        NUM_PIXELS = len(self.frameBuf)

        # Example: simple color cycling
        for i in range(NUM_PIXELS):
            hue = (i + self.index) / NUM_PIXELS
            self.frameBuf[i] = [
                int(255 * (0.5 + 0.5 * np.sin(hue * 2 * np.pi))),
                int(255 * (0.5 + 0.5 * np.sin(hue * 2 * np.pi + 2 * np.pi / 3))),
                int(255 * (0.5 + 0.5 * np.sin(hue * 2 * np.pi + 4 * np.pi / 3)))
            ]

        self.index += 1
