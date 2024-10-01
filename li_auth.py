import asyncio
from playwright.async_api import async_playwright
import time
async def main():
    username = input("Please enter your phone number or email:")
    password = input("Enter your password: ")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, timeout=60000)
        context = await browser.new_context()
        page = await context.new_page()

        await page.goto("https://www.linkedin.com/login/")
        await page.get_by_label("Email or phone").fill(username)
        await page.get_by_label("Password").fill(password)
        await page.get_by_label("Password").press("Enter")
        await page.wait_for_load_state("networkidle")
        time.sleep(25)
        if await page.get_by_role("heading", name="Enter your phone number to").is_visible():
            phone_number = input("Enter your phone number: ")
            await page.get_by_label("Please enter your phone").fill(phone_number)
            await page.keyboard.press('Enter')
            await page.wait_for_load_state("networkidle")
            print("Phone number entered successfully.")
            
        if await page.get_by_role("heading", name="Enter the code").is_visible():
            verification_code = input("Enter the verification code: ")
            await page.get_by_label("Please enter the code here").fill(verification_code)
            await page.keyboard.press('Enter')
            await page.wait_for_load_state("networkidle")
            print("Verification code entered successfully.")
            time.sleep(10)
            print("You've logged in successfully")
            session_id = await context.storage_state(path="ig.json")
            print(f"Session ID: {session_id}")
        time.sleep(20)

        await context.close()
        await browser.close()

# Run the main function
asyncio.run(main())