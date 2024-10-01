import asyncio
from playwright.async_api import async_playwright
import time
import json
import random

async def add_human_delay(page, min_delay=500, max_delay=1500):
    delay = random.randint(min_delay, max_delay)
    await page.wait_for_timeout(delay)

async def save_credentials(platform, username, password):
    with open(f"{platform.lower()}_credentials.json", "w") as f:
        json.dump({"username": username, "password": password}, f)

async def load_credentials(platform):
    try:
        with open(f"{platform.lower()}_credentials.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return None

async def main():
    platform = input("Enter the platform (e.g., Instagram, Facebook, X, LinkedIn, TikTok, Reddit, Discord, Slack, Pinterest, Skool): ")
    
    credentials = await load_credentials(platform)
    if credentials:
        username = credentials["username"]
        password = credentials["password"]
        print(f"Loaded saved credentials for {platform}")
    else:
        username = input("Enter your username: ")
        password = input("Enter your password: ")
        await save_credentials(platform, username, password)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        await page.goto("https://www.instagram.com/accounts/login/")
        await add_human_delay(page)
        await page.fill('input[name="username"]', username)
        await add_human_delay(page)
        await page.fill('input[name="password"]', password)
        await add_human_delay(page)
        await page.click('button[type="submit"]')
        await page.wait_for_load_state("networkidle")
        
        if await page.is_visible("text=Enter the code"):
            verification_code = input("Enter the verification code: ")
            await page.get_by_label("Security Code").fill(verification_code)
            await page.keyboard.press('Enter')
            await page.wait_for_load_state("networkidle")
            print("Verification code entered successfully.")
        
        # Wait for the home icon to be visible to confirm successful login
        try:
            await page.wait_for_selector('svg[aria-label="Home"]', timeout=30000)
            print("You've logged in successfully")
            session_id = await context.storage_state(path=f"{platform.lower()}_session.json")
            print(f"Session saved to {platform.lower()}_session.json")
        except:
            print("Login might have failed. Please check manually.")

        # Keep the browser open for a while to inspect the result
        time.sleep(20)

        await context.close()
        await browser.close()

# Run the main function
asyncio.run(main())