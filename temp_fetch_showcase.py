import sys
sys.stdout.reconfigure(encoding='utf-8')
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto('https://laolin.ai/showcase', timeout=30000)
    page.wait_for_timeout(8000)  # Wait for dynamic content
    
    print('Title:', page.title())
    
    # Get text content
    text = page.inner_text('body')
    print(f'Text length: {len(text)}')
    print('---Preview---')
    print(text[:5000])
    
    # Save full HTML
    with open(r'C:\Users\Administrator\.openclaw\workspace\wechat-ocr\showcase.html', 'w', encoding='utf-8') as f:
        f.write(page.content())
    
    # Save text
    with open(r'C:\Users\Administrator\.openclaw\workspace\wechat-ocr\showcase.txt', 'w', encoding='utf-8') as f:
        f.write(text)
    
    print('\nSaved HTML and text files')
    browser.close()
