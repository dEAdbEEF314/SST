from playwright.sync_api import sync_playwright
from playwright_stealth import stealth

def test_stealth():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        stealth(page)
        
        url = "https://vgmdb.net/search?q=Celeste"
        response = page.goto(url, wait_until="domcontentloaded")
        print(response.status)
        if "Just a moment..." in page.content():
            print("Failed: Cloudflare challenge triggered.")
        else:
            print("Success")
            
        browser.close()

if __name__ == "__main__":
    test_stealth()
