import asyncio
import time
from playwright.async_api import Playwright, async_playwright, expect
import tracemalloc
tracemalloc.start()

async def run(playwright: Playwright) -> None:

    print("Choose login method for Telegram:")
    print("1. QR Code")
    print("2. Phone Number")
    choice = input("Enter the number of your choice: ")

    browser = await playwright.chromium.launch(headless=False)
    context = await browser.new_context()
    page = await context.new_page()



    if choice == '1':
        await page.goto("https://web.telegram.org/a/")
        print("Please scan the QR code displayed on the screen.")
        time.sleep(20)
        await page.locator("#auth-qr-form div").nth(2).screenshot(path="qr_code.png")
        print("QR code screenshot saved as 'qr_code.png'. Please relay this to the user.")
        await asyncio.sleep(30)  # Wait for the user to scan the QR code
    elif choice == '2':
        country_code = input("Please enter your country code (e.g., +1 for USA): ")
        phone_number = input("Please enter your phone number (without country code): ")
        await page.goto("https://web.telegram.org/a/")
        
        # Click on the country code dropdown
        time.sleep(15)
        await page.wait_for_load_state("networkidle")
        await page.get_by_role("button", name="Log in by phone Number").click()
        time.sleep(5)
        # Fill in the phone numbert
       ## await page.get_by_label("Your phone number").click
        time.sleep(10)
       ## await page.press("Backspace", "Backspace", "Backspace", "Backspace," "Backspace")
        await page.get_by_label("Your phone number").fill(country_code + phone_number)
        await page.get_by_label("Your phone number").press("Enter")
        time.sleep(10)
        print("Phone number submitted successfully. Please check your Telegram app for the verification code.")
        if page.get_by_text("We've sent the code").is_visible():
            verification_code = input("Enter the verification code: ")
            await page.get_by_label("Code").fill(verification_code)
            time.sleep(30)
   

    else:
        print("Invalid choice. Exiting.")
        await context.close()
        await browser.close()
        return
    
    print("You've successfully logged in!")

    # Additional logic can be added here if needed

    await context.close()
    await browser.close()

async def main() -> None:
    async with async_playwright() as playwright:
        await run(playwright)

asyncio.run(main())
