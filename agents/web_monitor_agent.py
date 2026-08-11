from playwright.sync_api import sync_playwright
import argparse
import time
import json
import os


def monitor(url: str, outdir: str, timeout: int = 60, headless: bool = True):
    os.makedirs(outdir, exist_ok=True)
    log = {"console": [], "errors": [], "responses": []}

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        context = browser.new_context()
        page = context.new_page()

        def on_console(msg):
            try:
                log["console"].append({"type": msg.type, "text": msg.text})
            except Exception:
                pass

        def on_page_error(exception):
            try:
                log["errors"].append({"error": str(exception)})
            except Exception:
                pass

        def on_response(response):
            try:
                log["responses"].append({"url": response.url, "status": response.status, "ok": response.ok})
            except Exception:
                pass

        page.on("console", on_console)
        page.on("pageerror", on_page_error)
        page.on("response", on_response)

        try:
            page.goto(url, timeout=timeout * 1000)
            page.wait_for_load_state("networkidle", timeout=timeout * 1000)
        except Exception as e:
            log["errors"].append({"error": f"navigate/error: {e}"})

        # short extra wait for async activity
        time.sleep(2)

        ts = int(time.time())
        screenshot_path = os.path.join(outdir, f"screenshot_{ts}.png")
        html_path = os.path.join(outdir, f"page_{ts}.html")
        log_path = os.path.join(outdir, f"monitor_log_{ts}.json")

        try:
            page.screenshot(path=screenshot_path, full_page=True)
        except Exception as e:
            log["errors"].append({"error": f"screenshot/error: {e}"})

        try:
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(page.content())
        except Exception as e:
            log["errors"].append({"error": f"save-html/error: {e}"})

        try:
            with open(log_path, "w", encoding="utf-8") as f:
                json.dump(log, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print("Failed to write log:", e)

        browser.close()

    print(f"Monitoring finished. Outputs: {outdir}")


def main():
    parser = argparse.ArgumentParser(description="Web page monitor agent using Playwright")
    parser.add_argument("url", help="URL to open (e.g. http://localhost:8000)")
    parser.add_argument("--outdir", default="monitor_output", help="Directory to write logs and screenshots")
    parser.add_argument("--timeout", type=int, default=60, help="Timeout seconds for navigation and load")
    parser.add_argument("--headless", action="store_true", help="Run browser headless (default False if flag present)")

    args = parser.parse_args()

    # note: when flag present -> True
    monitor(args.url, args.outdir, timeout=args.timeout, headless=args.headless)


if __name__ == "__main__":
    main()
