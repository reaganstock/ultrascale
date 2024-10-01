import asyncio
import time
from playwright.async_api import Playwright, async_playwright, expect

async def run(playwright: Playwright) -> None:
    browser = await playwright.firefox.launch(headless=False)
    context = await browser.new_context()
    page = await context.new_page()

    await page.goto("https://www.tiktok.com/login")

    print("Choose login method for TikTok:")
    print("1. QR Code")
    print("2. Phone Number")
    print("3. Email and Password")
    choice = input("Enter the number of your choice: ")

    if choice == '1':
        await page.get_by_role("link", name="Use QR code").click()
        print("Please scan the QR code displayed on the screen.")
        time.sleep(5)
        await page.locator("canvas").screenshot(path="tiktok_qr.png")
        print("QR code screenshot saved as 'tiktok_qr.png'. Please scan it with your TikTok app.")
        await asyncio.sleep(30)  # Wait for the user to scan the QR code

    elif choice == '2':
        await page.get_by_role("link", name="Use phone / email / username").click()
        country = input("Enter your country (e.g., United States): ")
        phone_number = input("Enter your phone number (without country code): ")

        await page.get_by_label("US +1 phone country code.").click()
        await page.get_by_placeholder("Search").fill(country)
        await page.get_by_text(f"{country} +").click()
        
        await page.get_by_placeholder("Phone number").fill(phone_number)
        await page.get_by_role("button", name="Send code").click()
        
        print("Verification code sent. Please check your phone.")
        verification_code = input("Enter the 6-digit verification code: ")
        await page.get_by_placeholder("Enter 6-digit code").fill(verification_code)
        await page.get_by_placeholder("Enter 6-digit code").press("Enter")

    elif choice == '3':
        await page.get_by_role("link", name="Log in with email or username").click()
        email = input("Enter your email or username: ")
        password = input("Enter your password: ")
        await page.get_by_placeholder("Email or username").fill(email)
        await page.get_by_placeholder("Password").fill(password)
        await page.get_by_placeholder("Password").press("Enter")

    else:
        print("Invalid choice. Exiting.")
        await context.close()
        await browser.close()
        return

    # Check for 2-step verification
    try:
        if await page.get_by_text("-step verification").is_visible(timeout=10000):
            print("2-step verification required.") 
            verification_code = input("Enter the 6-digit verification code: ")
            await page.get_by_placeholder("Enter 6-digit code").fill(verification_code)
            await page.get_by_placeholder("Enter 6-digit code").press("Enter")
    except:
        print("No 2-step verification required or it was not detected.")

    # Wait for successful login
    try:
        await page.wait_for_selector('span[data-e2e="profile-icon"]', timeout=60000)
        print("Successfully logged in to TikTok!")
    except:
        print("Login might have failed or took too long. Please check manually.")

    # Save the session
    await context.storage_state(path="tiktok_session.json")
    print("Session saved to tiktok_session.json")

    time.sleep(10)  # Give some time to see the logged-in state
    await context.close()
    await browser.close()

async def main() -> None:
    async with async_playwright() as playwright:
        await run(playwright)

asyncio.run(main())