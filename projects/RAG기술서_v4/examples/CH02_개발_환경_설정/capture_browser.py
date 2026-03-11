#!/usr/bin/env python3
import asyncio
from playwright.async_api import async_playwright
import sys

async def capture_ollama_api():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        try:
            await page.goto("http://localhost:11434/api/tags", wait_until="networkidle")
            output_path = "/Users/nomadlab/Desktop/김주혁/workspace/coding-study/집필에이전트-claude/projects/RAG기술서_v4/assets/CH02/02_ollama-api-browser.png"
            await page.screenshot(path=output_path)
            print(f"Screenshot saved to {output_path}")
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(capture_ollama_api())
