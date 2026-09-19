#!/usr/bin/env -S PYTHONDONTWRITEBYTECODE=1 uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["crawl4ai>=0.8.9"]
# ///
# SPDX-License-Identifier: MIT OR Apache-2.0
"""
Render a URL in a headless browser and save a screenshot (PNG). Use for static
snapshots of a rendered page: verify a render, capture responsive viewports,
or focus on one component. The `crwl` CLI has no screenshot flag — this is the
screenshot path.

NOT for interactive debugging (clicks, console, network) — delegate that to
`browser-testing`, which resolves whatever browser bridge this host has.

Usage:
  ./screenshot.py <url> --out shot.png [options]

Options:
  --out PATH            Output PNG path (default: screenshot.png)
  --viewport WxH        Browser viewport, e.g. 1280x800 (default: 1280x800)
  --full-page          Capture the full scrollable page (default: viewport only)
  --element "<css>"     Scroll this element into view and focus on it.
                        NOTE: scopes the markdown and scrolls the element into
                        the viewport — it is NOT a pixel-tight element crop.
  --wait SECONDS        Extra settle time before the shot (default: 0)
  --md PATH             Also save the page markdown to PATH
  --no-bypass-cache     Use cache instead of forcing a fresh fetch

Examples:
  ./screenshot.py http://localhost:3000 --out home.png
  ./screenshot.py https://example.com --viewport 375x812 --full-page --out mobile.png
  ./screenshot.py http://localhost:3000 --element ".pricing-card" --out card.png --md card.md
"""

import argparse
import asyncio
import base64
import sys
from pathlib import Path

from crawl4ai import AsyncWebCrawler, BrowserConfig, CacheMode, CrawlerRunConfig


def parse_viewport(value: str) -> tuple[int, int]:
    try:
        w, h = value.lower().split("x", 1)
        return int(w), int(h)
    except (ValueError, AttributeError):
        print(f"FAILED: --viewport must be WxH (e.g. 1280x800), got: {value!r}")
        sys.exit(2)


async def shoot(args: argparse.Namespace) -> int:
    width, height = parse_viewport(args.viewport)

    browser_config = BrowserConfig(
        headless=True,
        viewport_width=width,
        viewport_height=height,
    )

    cfg = dict(
        cache_mode=CacheMode.ENABLED if args.no_bypass_cache else CacheMode.BYPASS,
        remove_overlay_elements=True,
        wait_for_images=True,
        screenshot=True,
        # full page when --full-page, else a viewport-bounded shot
        force_viewport_screenshot=not args.full_page,
    )
    if args.wait:
        cfg["screenshot_wait_for"] = float(args.wait)
    if args.element:
        cfg["css_selector"] = args.element
        # bring the element into the viewport for the viewport-bounded shot
        cfg["js_code"] = (
            f"document.querySelector({args.element!r})?.scrollIntoView("
            "{block: 'center', behavior: 'instant'});"
        )

    crawler_config = CrawlerRunConfig(**cfg)

    async with AsyncWebCrawler(config=browser_config) as crawler:
        result = await crawler.arun(url=args.url, config=crawler_config)

        if not result.success:
            print(f"FAILED: {result.error_message}")
            return 1

        if not result.screenshot:
            print("FAILED: no screenshot returned (page may have blocked rendering)")
            return 1

        data = (
            base64.b64decode(result.screenshot)
            if isinstance(result.screenshot, str)
            else result.screenshot
        )
        out = Path(args.out)
        out.write_bytes(data)
        print(f"OK: screenshot -> {out}  ({len(data)} bytes, {width}x{height}"
              f"{', full-page' if args.full_page else ''})")

        if args.md:
            md = getattr(result.markdown, "raw_markdown", None) or str(result.markdown)
            md_path = Path(args.md)
            md_path.write_text(md)
            print(f"OK: markdown -> {md_path}  ({len(md)} chars)")

        return 0


def main() -> None:
    p = argparse.ArgumentParser(description="Save a rendered-page screenshot via crawl4ai.")
    p.add_argument("url")
    p.add_argument("--out", default="screenshot.png")
    p.add_argument("--viewport", default="1280x800")
    p.add_argument("--full-page", action="store_true")
    p.add_argument("--element", default=None)
    p.add_argument("--wait", type=float, default=0)
    p.add_argument("--md", default=None)
    p.add_argument("--no-bypass-cache", action="store_true")
    args = p.parse_args()
    sys.exit(asyncio.run(shoot(args)))


if __name__ == "__main__":
    main()
