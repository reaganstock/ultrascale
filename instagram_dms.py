import csv
import json
import os
import asyncio
import random
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError

class InstagramDMAutomation:
    def __init__(self, csv_file, username_column, message_column, account_name):
        self.csv_file = csv_file
        self.username_column = username_column
        self.message_column = message_column
        self.account_name = account_name
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

    async def load_session(self):
        auth_file = f"{self.account_name}_instagram_auth.json"
        cred_file = f"{self.account_name}_instagram_credentials.json"

        print(f"Looking for auth file: {auth_file}")
        if os.path.exists(auth_file):
            print(f"Found auth file: {auth_file}")
            try:
                with open(auth_file, 'r') as f:
                    storage_state = json.load(f)
                self.context = await self.browser.new_context(storage_state=auth_file)
                self.page = await self.context.new_page()
                await self.page.goto("https://www.instagram.com/")
                if "login" not in self.page.url:
                    print("Session loaded successfully")
                    return True
                else:
                    print("Session expired or invalid, falling back to credentials")
            except Exception as e:
                print(f"Error loading auth file: {e}")
        else:
            print(f"Auth file not found: {auth_file}")

        print(f"Looking for credentials file: {cred_file}")
        if os.path.exists(cred_file):
            print(f"Found credentials file: {cred_file}")
            try:
                with open(cred_file, 'r') as f:
                    credentials = json.load(f)
                await self.login(credentials['username'], credentials['password'])
                return True
            except Exception as e:
                print(f"Error loading credentials file: {e}")
        else:
            print(f"Credentials file not found: {cred_file}")

        print("No valid session or credentials found")
        return False

    async def login(self, username, password):
        self.page = await self.context.new_page()
        await self.page.goto("https://www.instagram.com/")
        await self.page.get_by_label("Phone number, username, or email").fill(username)
        await self.page.get_by_label("Password").fill(password)
        await self.page.get_by_role("button", name="Log in").click()
        await self.page.wait_for_url("https://www.instagram.com/")
        
        # Save the session
        storage_state = await self.context.storage_state()
        with open(f"{self.account_name}_instagram_auth.json", 'w') as f:
            json.dump(storage_state, f)

    async def send_dms(self):
        with open(self.csv_file, 'r') as file:
            csv_reader = csv.reader(file)
            headers = next(csv_reader)  # Read the header row
            
            # Determine if we're using numeric indices or column names
            use_numeric = self.username_column.isdigit() and self.message_column.isdigit()
            
            if use_numeric:
                username_index = int(self.username_column) - 1
                message_index = int(self.message_column) - 1
            else:
                username_index = headers.index(self.username_column)
                message_index = headers.index(self.message_column)
            
            for row in csv_reader:
                username = row[username_index]
                message = row[message_index]
                await self.send_dm(username, message)

    async def send_dm(self, username, message):
        try:
            # Only navigate to inbox if we're not already there
            if "direct/inbox" not in self.page.url:
                await self.page.goto("https://www.instagram.com/direct/inbox/")
                await asyncio.sleep(random.uniform(3, 5))  # Random delay between 3-5 seconds

            # Click "New message" button
            new_message_button = self.page.get_by_role("button", name="New message")
            await new_message_button.click()
            await asyncio.sleep(random.uniform(1, 2))  # Random delay between 1-2 seconds

            # Wait for the search box to appear in the new message dialog
            search_box = self.page.get_by_placeholder("Search...")
            await search_box.wait_for()
            await search_box.click()
            await asyncio.sleep(random.uniform(0.5, 1))  # Short delay before typing

            # Clear the search box before typing (in case there's any text)
            await search_box.fill("")
            await asyncio.sleep(random.uniform(0.5, 1))

            # Type username with human-like delays
            for char in username:
                await search_box.type(char, delay=random.uniform(100, 300))
                await asyncio.sleep(random.uniform(0.1, 0.3))  # Short delay between characters

            await asyncio.sleep(random.uniform(1, 2))  # Wait for search results

            # Wait for and click the exact username match
            exact_username_selector = f'div[role="dialog"] span.x1lliihq:text-is("{username}")'
            username_element = await self.page.wait_for_selector(exact_username_selector, timeout=5000, state="visible")
            
            if username_element:
                await username_element.click()
                await asyncio.sleep(random.uniform(1, 2))  # Delay after clicking username

                # Click the "Chat" button
                chat_button = self.page.get_by_role("button", name="Chat")
                await chat_button.wait_for()
                await chat_button.click()
                await asyncio.sleep(random.uniform(1, 2))  # Delay before typing message

                # Find and click the message input field
                message_box = self.page.get_by_label("Message", exact=True)
                await message_box.wait_for()
                await message_box.click()

                # Type message with human-like delays
                for char in message:
                    await message_box.type(char, delay=random.uniform(50, 200))
                    await asyncio.sleep(random.uniform(0.05, 0.2))  # Short delay between characters

                await asyncio.sleep(random.uniform(1, 2))  # Delay before sending message
                await self.page.keyboard.press("Enter")

                await asyncio.sleep(5)  # 5-second delay after sending message
                print(f"Successfully sent DM to {username}")
            else:
                print(f"User {username} not found in search results")

        except PlaywrightTimeoutError:
            print(f"User {username} not found in search results")
        except Exception as e:
            print(f"Unexpected error sending DM to {username}: {str(e)}")
        finally:
            # Always backspace all characters, whether user was found or not
            for _ in range(len(username)):
                await search_box.press("Backspace")
                await asyncio.sleep(random.uniform(0.05, 0.1))
            
            # Close the new message dialog
            close_button = self.page.get_by_role("button", name="Close")
            if await close_button.is_visible():
                await close_button.click()
            
            await asyncio.sleep(random.uniform(1, 2))  # Short delay before next action

    async def close(self):
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

async def main():
    account_name = input("Enter your Instagram account name: ")
    csv_file = input("Enter the path to your CSV file: ")
    username_column = input("Enter the column name for usernames: ")
    message_column = input("Enter the column name for messages: ")

    async with async_playwright() as playwright:
        automation = InstagramDMAutomation(csv_file, username_column, message_column, account_name)
        automation.playwright = playwright
        automation.browser = await playwright.chromium.launch(headless=False)
        automation.context = await automation.browser.new_context()

        if await automation.load_session():
            await automation.send_dms()
        else:
            print("Failed to load session or login. Please check your credentials.")

        await automation.close()

if __name__ == "__main__":
    asyncio.run(main())
