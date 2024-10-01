import asyncio
from playwright.async_api import async_playwright
import time
async def main():
    username = input("Please enter your email: ")
    password = input("Enter your password: ")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, timeout=60000)
        context = await browser.new_context()
        page = await context.new_page()

        await page.goto("https://www.skool.com/login")
        await page.locator("#email").fill(username)
        await page.locator("#password").fill(password)
        await page.locator("#password").press("Enter")
        await page.wait_for_load_state("networkidle")
        time.sleep(10)
        print("You've logged in successfully")
        session_id = await context.storage_state(path="ig.json")
        print(f"Session ID: {session_id}")
        await page.get_by_role("button", name="Trust this device").click()
        time.sleep(20)

        await context.close()
        await browser.close()

# Run the main function
asyncio.run(main())

