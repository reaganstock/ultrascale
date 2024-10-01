import asyncio
from playwright.async_api import async_playwright
import time

async def run(playwright):

    print("Choose login method for Slack:")
    print("1. Workspace, Email and Password")
    print("2. Workspace and Email")
    choice = input("Enter the number of your choice: ")

    workspace = input("Please enter your workspace: ")
    username = input("Please enter your workspace email: ")

    browser = await playwright.chromium.launch(headless=False, timeout=60000)  # Await the launch
    context = await browser.new_context()
    page = await context.new_page() 
    
    if choice == '1':
        password = input("Enter your password: ")
        await page.goto(f"https://{workspace}.slack.com/signin")
        await page.get_by_placeholder("name@work-email.com").fill(username)
        await page.get_by_role("link", name="sign in with a password").click()
        await page.get_by_placeholder("Your password").fill(password)
        await page.get_by_placeholder("Your password").press("Enter")
    elif choice == '2':
        await page.goto(f"https://{workspace}.slack.com/signin")
        await page.get_by_placeholder("name@work-email.com").fill(username)
        await page.get_by_placeholder("name@work-email.com").press("Enter")
        if await page.get_by_role("heading", name="Check your email for a code").is_visible():
            verification_code = input("Enter the verification code sent to your phone: ")
            filtered_code = verification_code.replace('-', '')  # Remove dashes
            for i in range(len(filtered_code)):
                await page.get_by_label(f"digit {i + 1} of").click()  # Click on the digit input
                await page.keyboard.type(filtered_code[i])  # Type the corresponding digit
            await page.keyboard.press('Enter')
            print("Verification code entered successfully.")
            time.sleep(30)
    else:
        print("Invalid choice. Exiting.")
        return

    await page.goto("https://slack.com/workspace-signin")
    await page.get_by_placeholder("your-workspace").fill(workspace)
    await page.get_by_placeholder("your-workspace").press("Enter")
    await page.get_by_placeholder("name@work-email.com").fill(username)
    await page.get_by_placeholder("name@work-email.com").press("Enter")
    time.sleep(10)

    if await page.get_by_role("heading", name="Check your email for a code").is_visible():
        verification_code = input("Please enter your verification code:")  
        filtered_code = verification_code.replace('-', '')  # Remove dashes
        for i in range(len(filtered_code)):
            await page.get_by_label(f"digit {i + 1} of").click()  # Click on the digit input
            await page.keyboard.type(filtered_code[i])  # Type the corresponding digit
        await page.keyboard.press('Enter') 
        print("Verification code entered successfully.")
        time.sleep(15)
    if await page.get_by_role("heading", name="Enter your authentication code").is_visible():
        verification_code = input("Please enter the verification code sent to your phone:")  
        filtered_code = verification_code.replace('-', '')  # Remove dashes
        for i in range(len(filtered_code)):
            await page.get_by_label(f"digit {i + 1} of").click()  # Click on the digit input
            await page.keyboard.type(filtered_code[i])  # Type the corresponding digit
        await page.keyboard.press('Enter') 
        print("Verification code entered successfully.")
        time.sleep(15)

    time.sleep(5)
    await page.goto(f"https://{workspace}.slack.com/")
    time.sleep(15)
    print("You've logged in successfully")
    await context.storage_state(path="ig.json")

    await context.close()
    await browser.close()

# Run the main function
async def main() -> None:
    async with async_playwright() as playwright:
        await run(playwright)

asyncio.run(main())




