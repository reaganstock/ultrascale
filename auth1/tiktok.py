import asyncio
import email
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
    return await wait_for_selector(page, 'span[data-e2e="profile-icon"]', timeout=10000)

async def tiktok_login(page, login_method):
    await page.goto("https://www.tiktok.com/login")
    
    if login_method == '1':
        await page.get_by_role("link", name="Use QR code").click()
        print("Please scan the QR code displayed on the screen.")
        time.sleep(5)
        await page.locator("canvas").screenshot(path="tiktok_qr.png")
        print("QR code screenshot saved as 'tiktok_qr.png'. Please scan it with your TikTok app.")
        await asyncio.sleep(30)  # Wait for the user to scan the QR code
    elif login_method == '2':
        await page.get_by_role("link", name="Use phone / email / username").click()
        country = input("Enter your country (e.g., United States): ")
        phone_number = input("Enter your phone number (without country code): ")

        await page.get_by_label("US +1 phone country code.").click()
        await page.get_by_placeholder("Search").fill(country)
        await page.get_by_text(f"{country} +").click()
        
        await human_type(page, 'input[placeholder="Phone number"]', phone_number)
        await page.get_by_role("button", name="Send code").click()
        
        print("Verification code sent. Please check your phone.")
        verification_code = input("Enter the 6-digit verification code: ")
        await human_type(page, 'input[placeholder="Enter 6-digit code"]', verification_code)
        await page.get_by_placeholder("Enter 6-digit code").press("Enter")
    elif login_method == '3':
        await page.get_by_role("link", name="Log in with email or username").click()
        email = input("Enter your email or username: ")
        password = input("Enter your password: ")
        await human_type(page, 'input[placeholder="Email or username"]', email)
        await human_type(page, 'input[placeholder="Password"]', password)
        await page.get_by_placeholder("Password").press("Enter")

async def main(account_name, proxy=None):
    auth_file = f'{account_name}_tiktok_auth.json'
    credentials_file = f'{account_name}_tiktok_credentials.json'

    async with async_playwright() as p:
        browser = await p.firefox.launch(headless=False, proxy=proxy)
        
        # Try to load saved session
        context = await load_session(browser, auth_file)
        if context:
            page = await context.new_page()
            await page.goto("https://www.tiktok.com/")
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

        print("Choose login method for TikTok:")
        print("1. QR Code")
        print("2. Phone Number")
        print("3. Email and Password")
        login_method = input("Enter the number of your choice: ")

        await tiktok_login(page, login_method)

        # Check for 2-step verification
        try:
            if await page.get_by_text("-step verification").is_visible(timeout=10000):
                print("2-step verification required.") 
                verification_code = input("Enter the 6-digit verification code: ")
                await human_type(page, 'input[placeholder="Enter 6-digit code"]', verification_code)
                await page.get_by_placeholder("Enter 6-digit code").press("Enter")
        except:
            print("No 2-step verification required or it was not detected.")

        # Verify login
        if await verify_login(page):
            print("Login successful")
            await save_session(context, auth_file)
            
            # Save credentials (for email/password method only)
            if login_method == '3':
                with open(credentials_file, 'w') as f:
                    json.dump({'username': username, 'password': password}, f)
                print(f"Credentials saved to {credentials_file}")

            # Verify stored session
            new_context = await browser.new_context(storage_state=auth_file)
            new_page = await new_context.new_page()
            await new_page.goto("https://www.tiktok.com/")
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
asyncio.run(main("tiktok_user", {"server": "proxy_address", "username": "proxy_user", "password": "proxy_pass"}))