import asyncio
from playwright.async_api import async_playwright
import time
import json
import random
import os

async def add_human_delay(page, min_delay=500, max_delay=2000):
    delay = random.randint(min_delay, max_delay)
    await page.wait_for_timeout(delay)

async def human_type(page, selector, text):
    await page.focus(selector)
    for char in text:
        await page.type(selector, char, delay=random.randint(50, 200))
    await add_human_delay(page, 200, 500)

async def save_session(context, filename):
    state = await context.storage_state()
    with open(filename, 'w') as f:
        json.dump(state, f)
    print(f"Session saved to {filename}")

async def load_session(browser, filename):
    try:
        with open(filename, 'r') as f:
            state = json.load(f)
        context = await browser.new_context(storage_state=state)
        print(f"Session loaded from {filename}")
        return context
    except FileNotFoundError:
        print(f"No session file found at {filename}")
        return None

async def wait_for_selector(page, selector, timeout=30000):
    try:
        await page.wait_for_selector(selector, timeout=timeout)
        return True
    except:
        return False

async def verify_login(page):
    return await wait_for_selector(page, 'div[data-testid="SideNav_AccountSwitcher_Button"]', timeout=10000)

async def x_login(page, username, password):
    await page.goto("https://x.com/")
    await page.wait_for_load_state("networkidle")
    await page.get_by_test_id("loginButton").click()
    await human_type(page, 'input[autocomplete="username"]', username)
    await page.get_by_label("Phone, email, or username").press("Enter")
    await page.wait_for_load_state("networkidle")
    if await page.get_by_role("heading", name="Enter your phone number or").is_visible():
        phone_number_or_username = input("Enter your phone number or username: ")
        await human_type(page, 'input[data-testid="ocfEnterTextTextInput"]', phone_number_or_username)
        await page.keyboard.press('Enter')
        await page.wait_for_load_state("networkidle")
        print("Phone number or username entered successfully.")
    await human_type(page, 'input[name="password"]', password)
    await page.get_by_label("Password", exact=True).press("Enter")
    await page.wait_for_load_state("networkidle")

async def main(account_name, proxy=None):
    auth_file = f'{account_name}_x_auth.json'
    credentials_file = f'{account_name}_x_credentials.json'

    async with async_playwright() as p:
        browser = await p.firefox.launch(headless=False, proxy=proxy, timeout=60000)
        
        # Try to load saved session
        context = await load_session(browser, auth_file)
        if context:
            page = await context.new_page()
            await page.goto("https://x.com/")
            if await verify_login(page):
                print("Login successful using saved session")
                time.sleep(5)
                await context.close()
                await browser.close()
                return
            else:
                print("Saved session invalid, proceeding with manual login")
                await context.close()
        
        # If no valid session, proceed with manual login
        context = await browser.new_context()
        page = await context.new_page()

        if os.path.exists(credentials_file):
            with open(credentials_file, 'r') as f:
                credentials = json.load(f)
            username = credentials['username']
            password = credentials['password']
        else:
            username = input("Please enter your username, phone number, or email: ")
            password = input("Enter your password: ")

        await x_login(page, username, password)

        if await page.get_by_text("Enter your verification code").is_visible():
            verification_code = input("Enter the verification code: ")
            await human_type(page, 'input[data-testid="ocfEnterTextTextInput"]', verification_code)
            await page.keyboard.press('Enter')
            await page.wait_for_load_state("networkidle")
            print("Verification code entered successfully.")

        # Verify login
        if await verify_login(page):
            print("Login successful")
            await save_session(context, auth_file)
            
            # Save credentials
            with open(credentials_file, 'w') as f:
                json.dump({'username': username, 'password': password}, f)
            print(f"Credentials saved to {credentials_file}")

            # Verify stored session
            new_context = await browser.new_context(storage_state=auth_file)
            new_page = await new_context.new_page()
            await new_page.goto("https://x.com/")
            if await verify_login(new_page):
                print("Stored session verified successfully")
            else:
                print("Stored session verification failed")
            await new_context.close()
        else:
            print("Login failed")

        time.sleep(10)
        print("Session complete")
        time.sleep(5)

        await context.close()
        await browser.close()

# Usage
asyncio.run(main("x_user", {"server": "proxy_address", "username": "proxy_user", "password": "proxy_pass"}))