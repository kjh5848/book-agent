#!/usr/bin/env python3
"""
This script captures the Ollama API response using Playwright
and saves it as a PNG screenshot showing the browser view of the JSON response.
"""
import asyncio
import sys

async def main():
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        print("Error: playwright not installed", file=sys.stderr)
        sys.exit(1)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1280, "height": 720})

        try:
            # Navigate to Ollama API endpoint
            await page.goto("http://localhost:11434/api/tags", wait_until="networkidle")

            # Take screenshot
            output_path = "/Users/nomadlab/Desktop/김주혁/workspace/coding-study/집필에이전트-claude/projects/RAG기술서_v4/assets/CH02/02_ollama-api-browser.png"
            await page.screenshot(path=output_path, full_page=False)

            print(f"SUCCESS: Screenshot saved to {output_path}")

        except Exception as e:
            print(f"ERROR: {e}", file=sys.stderr)
            sys.exit(1)
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
