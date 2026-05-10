"""
Human-like mouse movement helpers for Playwright.

Provides `human_move` which moves the mouse along small randomized steps
between start and end over a duration to mimic human motion.
"""
import random
import math
import asyncio
from typing import Tuple


def _interpolate(a, b, t):
    return a + (b - a) * t


async def human_move(mouse, start: Tuple[int, int], end: Tuple[int, int], duration: float = 0.6, steps: int = None):
    """Move `mouse` from `start` to `end` in a human-like way.

    - `mouse` is `page.mouse` from Playwright
    - `start` and `end` are (x,y)
    - `duration` seconds total
    - `steps` optional number of intermediate moves
    """
    if steps is None:
        steps = max(6, int(duration * 15 + random.random() * 5))

    await mouse.move(start[0], start[1])
    for i in range(1, steps + 1):
        t = i / steps
        # ease-in-out
        ease = 0.5 - 0.5 * math.cos(math.pi * t)
        nx = _interpolate(start[0], end[0], ease)
        ny = _interpolate(start[1], end[1], ease)
        # add small jitter
        jitter = (random.uniform(-1.2, 1.2), random.uniform(-1.2, 1.2))
        await mouse.move(nx + jitter[0], ny + jitter[1])
        await asyncio.sleep(duration / steps * (0.8 + random.random() * 0.8))
