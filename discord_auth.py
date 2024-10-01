import asyncio
import time
from playwright.async_api import Playwright, async_playwright, expect
import tracemalloc
tracemalloc.start()

async def run(playwright: Playwright) -> None:
    print("Choose login method for Discord:")
    print("1. QR Code")
    print("2. Email/Phone and Password")
    choice = input("Enter the number of your choice: ")

    browser = await playwright.firefox.launch(headless=False)
    context = await browser.new_context()
    page = await context.new_page()

    if choice == '1':
        await page.goto("https://discord.com/login")
        print("Please scan the QR code displayed on the screen.")
        time.sleep(20)
        await page.locator(".qrCodeOverlay_c6cd4b").screenshot(path="discord_qr.png")
        print("QR code screenshot saved as 'discord_qr.png'. Please relay this to the user.")
        await asyncio.sleep(30)  # Wait for the user to scan the QR code
    elif choice == '2':
        email = input("Please enter your email or phone number: ")
        password = input("Enter your password: ")
        await page.goto("https://discord.com/login")
        
        await page.wait_for_load_state("networkidle")
        await page.get_by_label("Email or Phone Number*").fill(email)
        await page.get_by_label("Password*").fill(password)
        await page.get_by_label("Password*").press("Enter")
        
        time.sleep(10)
        if await page.is_visible("text=Enter the 6-digit code"):
            verification_code = input("Enter the 6-digit verification code: ")
            await page.get_by_label("Enter the 6-digit code").fill(verification_code)
            await page.get_by_label("Enter the 6-digit code").press("Enter")
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