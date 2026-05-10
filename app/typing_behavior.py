"""
Human-like typing helpers for Playwright.

`human_type` types text into an element with randomized per-character delays
and occasional small pauses to mimic real typing.
"""
import random
import asyncio


async def human_type(element, text: str, min_delay: float = 0.03, max_delay: float = 0.18):
    """Type text into a Playwright element or page using keyboard with variable delay.

    `element` may be a `Locator` or `Page`; if it's a locator, call `fill`/`type` accordingly.
    """
    # If element has type() method (Locator), use it directly with average delay
    avg = (min_delay + max_delay) / 2
    try:
        # try to use locator.type if available
        typ = getattr(element, 'type', None)
        if callable(typ):
            for ch in text:
                await element.type(ch, delay=int((min_delay + random.random() * (max_delay - min_delay)) * 1000))
                # occasional pause
                if random.random() < 0.02:
                    await asyncio.sleep(0.05 + random.random() * 0.2)
            return
    except Exception:
        pass

    # Fallback: send keys via keyboard on page
    keyboard = getattr(element, 'keyboard', None)
    if keyboard is None and hasattr(element, 'page'):
        keyboard = element.page.keyboard

    if keyboard is None:
        # last resort: element.fill
        try:
            await element.fill(text)
            return
        except Exception:
            return

    for ch in text:
        await keyboard.insertText(ch)
        await asyncio.sleep(min_delay + random.random() * (max_delay - min_delay))
        if random.random() < 0.02:
            await asyncio.sleep(0.05 + random.random() * 0.3)
