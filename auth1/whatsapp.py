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
    return await wait_for_selector(page, 'div[aria-label="Chat list"]', timeout=10000)

async def whatsapp_login(page, login_method):
    await page.goto("https://web.whatsapp.com/")
    
    if login_method == '1':
        print("Please scan the QR code displayed on the screen.")
        time.sleep(5)
        await page.get_by_label("Scan this QR code to link a").screenshot(path="whatsapp_qr.png")
        print("QR code screenshot saved as 'whatsapp_qr.png'. Please scan it with your WhatsApp app.")
        await asyncio.sleep(30)  # Wait for the user to scan the QR code
    elif login_method == '2':
        country_code = input("Please enter your country code (e.g., +1 for USA): ")
        phone_number = input("Please enter your phone number (without country code): ")
        
        await page.wait_for_load_state("networkidle")
        await page.get_by_role("button", name="Link with phone number", exact=True).click()
        time.sleep(5)
        
        await human_type(page, 'input[aria-label="Type your phone number."]', country_code+phone_number)
        await page.get_by_label("Type your phone number.").press("Enter")
        
        time.sleep(10)
        print("Phone number submitted successfully.")
        text = await page.inner_text('div[aria-details="link-device-phone-number-code-screen-instructions"]')
        text1 = (text.replace("\n", "").replace("-", "").upper())
        code = text1[:4] + "-" + text1[4:]
        print(f"The code displayed on the screen is: {code}")
        print("Enter the 8-character code displayed on the screen from your WhatsApp account.")
        time.sleep(30)

async def main(account_name, proxy=None):
    auth_file = f'{account_name}_whatsapp_auth.json'

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, proxy=proxy)
        
        # Try to load saved session
        context = await load_session(browser, auth_file)
        if context:
            page = await context.new_page()
            await page.goto("https://web.whatsapp.com/")
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

        print("Choose login method for WhatsApp:")
        print("1. QR Code")
        print("2. Phone Number")
        login_method = input("Enter the number of your choice: ")

        await whatsapp_login(page, login_method)

        # Verify login
        if await verify_login(page):
            print("Login successful")
            await save_session(context, auth_file)

            # Verify stored session
            new_context = await browser.new_context(storage_state=auth_file)
            new_page = await new_context.new_page()
            await new_page.goto("https://web.whatsapp.com/")
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
asyncio.run(main("whatsapp_user", {"server": "proxy_address", "username": "proxy_user", "password": "proxy_pass"}))