"""Connect to existing Chrome via CDP and upload file"""
import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        # Connect to existing Chrome DevTools
        browser = await p.chromium.connect_over_cdp("http://127.0.0.1:18800")
        
        # Find the douyin tab
        for context in browser.contexts:
            for page in context.pages:
                if 'creator.douyin.com' in page.url:
                    print(f"Found page: {page.url}")
                    
                    # Use Playwright's file chooser handling
                    file_input = page.locator('input[type="file"]')
                    await file_input.set_input_files(r"D:\video-analysis\output\银针试毒v4\v5\final_v9.mp4")
                    print("File set successfully!")
                    
                    # Wait a moment
                    await asyncio.sleep(3)
                    print(f"Page URL now: {page.url}")
                    return
        
        print("Douyin page not found")

asyncio.run(main())
