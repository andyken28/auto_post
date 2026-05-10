# Anti-detect design and limitations

## How Facebook detects automation

- `navigator.webdriver`: browsers controlled by automation often expose this flag.
- Missing or inconsistent `navigator.plugins` and `navigator.mimeTypes` values.
- `navigator.languages` that don't match Accept-Language headers.
- Headless-specific characteristics (GPU, User-Agent mismatches, missing features).
- Behavioral signals: mouse movement patterns, typing speed, idle times.
- Network/timing/fingerprint signals: resource timing, canvas/audio fingerprints.

## Where Playwright is detected

- JS-visible properties (navigator.webdriver, chrome runtime) are common checks.
- Unusual or absent plugins, mimeTypes, or languages.
- Predictable or synthetic event timing and mouse/keyboard events.
- Capabilities or features that differ slightly from a real Chrome build.

## What stealth functions do

- Inject an init script that overrides `navigator.webdriver`, `navigator.languages`, `navigator.plugins`, and `navigator.mimeTypes`.
- Provide randomized viewport values (size, DPR, mobile flag) to reduce uniform fingerprints.
- Provide helpers to simulate human mouse movements and typing behavior.
- Spoof timezone and Intl.DateTimeFormat to match expected timezones.

## What stealth cannot fully do

- It cannot perfectly replicate an up-to-date genuine browser fingerprint (canvas/audio/fingerprinting can still reveal differences).
- It cannot mimic long-term human behavior across sessions unless you store and replay realistic behavior traces.
- It's a cat-and-mouse game: sites update detection methods; stealth code needs frequent maintenance.

Use these tools to reduce obvious signals but test thoroughly and avoid high-risk abuse.
