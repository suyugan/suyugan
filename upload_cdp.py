"""Use CDP directly to set file on input"""
import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp("http://127.0.0.1:18800")
        
        for context in browser.contexts:
            for page in context.pages:
                if 'creator.douyin.com' in page.url:
                    print(f"Found page: {page.url}")
                    
                    cdp = await page.context.new_cdp_session(page)
                    
                    # Get the file input node
                    doc = await cdp.send("DOM.getDocument")
                    result = await cdp.send("DOM.querySelector", {
                        "nodeId": doc["root"]["nodeId"],
                        "selector": "input[type=file]"
                    })
                    node_id = result["nodeId"]
                    print(f"File input nodeId: {node_id}")
                    
                    # Set files directly via CDP (no size limit for local files)
                    await cdp.send("DOM.setFileInputFiles", {
                        "files": [r"D:\video-analysis\output\银针试毒v4\v5\final_v9.mp4"],
                        "nodeId": node_id
                    })
                    print("File set via CDP!")
                    
                    await asyncio.sleep(5)
                    print(f"Page URL: {page.url}")
                    return
        
        print("Page not found")

asyncio.run(main())
