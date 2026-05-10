Playwright Installation & Notes

Install Playwright in your Python environment:

```powershell
python -m pip install playwright
python -m playwright install
```

- The `python -m playwright install` command downloads browser binaries (Chromium, Firefox, WebKit). Run it once per environment.
- To run Playwright headlessly, configure `headless=True` when launching contexts.
- On Windows, Playwright may require additional system dependencies; follow the Playwright docs if you encounter errors:
  https://playwright.dev/python/docs/intro

Running Playwright-based poster from the app requires these binaries to be installed; otherwise automation calls will fail with an error indicating missing browsers.
