# Web Monitor Agent

This agent monitors a web page using Playwright (Python). It captures console messages, page errors, network responses, a screenshot and the page HTML.

Installation

1. Create a Python environment (recommended).
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Install Playwright browsers:

```bash
playwright install
```

Usage

```bash
python agents/web_monitor_agent.py http://localhost:8000 --outdir=monitor_out --timeout=60 --headless
```

Outputs

- `monitor_out/` directory containing:
  - `screenshot_<ts>.png` — full-page screenshot
  - `page_<ts>.html` — saved HTML
  - `monitor_log_<ts>.json` — collected console/errors/responses

Notes

- If your project runs a local dev server (e.g. `npm run dev`), start it before running the agent.
- For debugging, omit `--headless` to see the browser window.
