import asyncio
import time
from playwright.async_api import async_playwright

async def login_pinterest():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, timeout=60000)
        context = await browser.new_context()
        page = await context.new_page()

        await page.goto("https://www.pinterest.com/login/")

        email = input("Enter your email: ")
        password = input("Enter your password: ")

        await page.get_by_placeholder("Email").fill(email)
        await page.get_by_placeholder("Password").fill(password)
        await page.get_by_placeholder("Password").press("Enter")

        await page.wait_for_load_state("networkidle")

        if await page.get_by_role("heading", name="Two-factor authentication").is_visible():
            verification_code = input("Enter the verification code: ")
            await page.get_by_placeholder("Verification code").fill(verification_code)
            await page.get_by_placeholder("Verification code").press("Enter")

        await page.wait_for_selector('button[aria-label="Home"]', timeout=60000)
        
        print("Successfully logged in to Pinterest!")
        session_id = await context.storage_state(path="pinterest_session.json")
        print(f"Session saved to pinterest_session.json")

        await context.close()
        await browser.close()

asyncio.run(login_pinterest())