"""
Anti-detect helpers for Playwright.

This module provides utilities to reduce detection surface when automating
with Playwright by patching navigator properties, languages, plugins, timezone,
and providing randomized viewport values.

Usage:
  await context.add_init_script(stealth_script(...))
  or call `await apply_stealth(context, options)` which injects the init script.

Limitations: these are heuristics and do NOT guarantee invisibility. Sites
use many signals (behavioral, networking, fingerprinting) that are hard to
fully replicate. Use responsibly and only on accounts you control.
"""
from typing import Optional, Dict, Any
import random
import json

def _rand_choice(seq):
    return random.choice(seq)


COMMON_LANGUAGES = [
    ["en-US", "en"],
    ["en-GB", "en"],
    ["vi-VN", "vi", "en-US"],
    ["fr-FR", "fr"],
]


def random_viewport() -> Dict[str, Any]:
    """Return a randomized viewport dict for Playwright context.

    Returns keys: width, height, deviceScaleFactor, isMobile
    """
    widths = [1366, 1440, 1536, 1600, 1024, 1280]
    heights = [768, 900, 960, 1024, 800]
    width = _rand_choice(widths)
    height = _rand_choice(heights)
    dpr = random.choice([1, 1, 1, 1.25, 1.5])
    is_mobile = random.random() < 0.08  # mostly desktop
    return {
        "width": width,
        "height": height,
        "deviceScaleFactor": dpr,
        "isMobile": is_mobile,
    }


def stealth_script(languages: Optional[list] = None, timezone: Optional[str] = None, plugins_count: int = 3) -> str:
    """Return a JavaScript string to be used with `context.add_init_script()`.

    - `languages`: list of language codes (eg ['en-US','en'])
    - `timezone`: IANA timezone string (eg 'Asia/Ho_Chi_Minh')
    - `plugins_count`: number of fake plugins to expose
    """
    langs = languages or _rand_choice(COMMON_LANGUAGES)
    tz = timezone or _rand_choice(["Asia/Ho_Chi_Minh", "America/New_York", "Europe/London"])

    # Create fake plugins metadata
    plugins = []
    for i in range(plugins_count):
        plugins.append({
            "name": f"Chrome PDF Plugin {i}",
            "filename": f"internal-pdf-plugin-{i}.so",
            "description": "Portable Document Format",
        })

    script = f"""
(function(){{
  try {{
    // Pass the webdriver check
    Object.defineProperty(navigator, 'webdriver', {{get: () => false}});

    // Languages
    Object.defineProperty(navigator, 'languages', {{get: () => {json.dumps(langs)}}});

    // Plugins
    const fakePlugins = {json.dumps(plugins)};
    function makePluginArray(arr) {{
      const pluginArray = [];
      for (const p of arr) {{
        pluginArray.push(p);
      }}
      pluginArray.refresh = function(){{}};
      return pluginArray;
    }}
    Object.defineProperty(navigator, 'plugins', {{get: () => makePluginArray(fakePlugins)}});

    // Mock permissions.query to not leak headless state
    const originalQuery = window.navigator.permissions.query;
    if (originalQuery) {{
      window.navigator.permissions.query = (parameters) => (
        parameters.name === 'notifications' ? Promise.resolve({ state: Notification.permission }) : originalQuery(parameters)
      );
    }}

    // Fake chrome runtime
    window.chrome = window.chrome || {{ runtime: {{}} }};

    // Overwrite plugins/mimetypes lookup
    Object.defineProperty(navigator, 'mimeTypes', {{get: () => []}});

    // Timezone spoof
    const tz = '{tz}';
    try {{
      const _Date = Date;
      Date.prototype.getTimezoneOffset = function() {{
        // best-effort: return offset for timezone (approx by using Intl)
        try {{
          const opts = Intl.DateTimeFormat().resolvedOptions();
          return new Date().getTimezoneOffset();
        }} catch(e) {{ return _Date.prototype.getTimezoneOffset.call(this); }}
      }};
      Intl.DateTimeFormat = (function(orig){{
         return function(locale, opts) {{
           opts = opts || {{}};
           opts.timeZone = opts.timeZone || tz;
           return orig.call(this, locale, opts);
         }}
      }})(Intl.DateTimeFormat);
      Intl.DateTimeFormat.prototype = Intl.DateTimeFormat.prototype;
    }} catch(e){{}}

  }} catch(e){{}}
}})();
"""
    return script


def explain_detection() -> str:
    return (
        "Facebook and other sites combine many signals to detect automation: "
        "navigator.webdriver flag, missing plugins/mimeTypes, unexpected languages, "
        "unusual mouse/keyboard patterns, headless-specific behaviors, timing and network fingerprints. "
        "Playwright can be detected via injected attributes, missing browser features, or unusual behavior. "
        "Stealth reduces surface by patching obvious JS-accessible signals and by simulating human-like input, but it cannot fully replicate a real browser fingerprint or human behavior. "
        "Use with caution; frequent updates and monitoring are required."
    )
