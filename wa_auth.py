import asyncio
import time
from playwright.async_api import Playwright, async_playwright, expect
import tracemalloc
tracemalloc.start()

async def run(playwright: Playwright) -> None:
    print("Choose login method for WhatsApp:")
    print("1. QR Code")
    print("2. Phone Number")
    choice = input("Enter the number of your choice: ")

    browser = await playwright.chromium.launch(headless=False)
    context = await browser.new_context()
    page = await context.new_page()

    if choice == '1':
        await page.goto("https://web.whatsapp.com/")
        print("Please scan the QR code displayed on the screen.")
        time.sleep(5)
        await page.get_by_label("Scan this QR code to link a").screenshot(path="whatsapp_qr.png")
        print("QR code screenshot saved as 'whatsapp_qr.png'. Please relay this to the user.")
        await asyncio.sleep(30)  # Wait for the user to scan the QR code
    elif choice == '2':
        country_code = input("Please enter your country code (e.g., +1 for USA): ")
        phone_number = input("Please enter your phone number (without country code): ")
        await page.goto("https://web.whatsapp.com/")
        
        await page.wait_for_load_state("networkidle")
        await page.get_by_role("button", name="Link with phone number", exact=True).click()
        time.sleep(5)
        
        await page.get_by_label("Type your phone number.").click()
        await page.get_by_label("Type your phone number.").fill(country_code+phone_number)
        await page.get_by_label("Type your phone number.").press("Enter")
        
        time.sleep(10)
        print("Phone number submitted successfully.")
        text = await page.inner_text('div[aria-details="link-device-phone-number-code-screen-instructions"]')
        text1 = (text.replace("\n", "").replace("-", "").upper())
        code = text1[:4] + "-" + text1[4:]
        print(f"The code displayed on the screen is: {code}")
        print("Enter the 8-character code displayed on the screen from your WhatsApp account.")
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