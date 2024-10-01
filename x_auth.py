import asyncio
from playwright.async_api import async_playwright
import time
async def main():
    username = input("Please enter your username, phone number, or email:")
    password = input("Enter your password: ")


    async with async_playwright() as p:
        browser = await p.firefox.launch(headless=False, timeout=60000)
        context = await browser.new_context()
        page = await context.new_page()
        await context.tracing.start(screenshots=True, snapshots=True, sources=True)

        await page.goto("https://x.com/")
        await page.wait_for_load_state("networkidle")
        await page.get_by_test_id("loginButton").click()
        await page.get_by_label("Phone, email, or username").fill(username)
        await page.get_by_label("Phone, email, or username").press("Enter")
        await page.wait_for_load_state("networkidle")
        if await page.get_by_role("heading", name="Enter your phone number or").is_visible():
            phone_number_or_username = input("Enter your phone number or username: ")
            await page.locator("label div").nth(3).fill(phone_number_or_username)
            await page.keyboard.press('Enter')
            await page.wait_for_load_state("networkidle")
            print("Phone number or username entered successfully.")
        await page.get_by_label("Password", exact=True).fill(password)
        await page.get_by_label("Password", exact=True).press("Enter")
        await page.wait_for_load_state("networkidle")
        time.sleep(5) 

        if await page.get_by_text("Enter your verification code").is_visible():
            verification_code = input("Enter the verification code: ")
            await page.locator("label div").nth(3).fill(verification_code)
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




