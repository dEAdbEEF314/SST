import sys
import os
import time
import random
sys.path.append(os.path.join(os.getcwd(), 'vendor/vgmdb'))
from vgmdb.parsers.search import parse_page
from playwright.sync_api import sync_playwright
import urllib.parse

QUERIES = [
    # 1. Alphanumeric
    "art of rally OST",
    "The Messenger Soundtrack - Disc I: The Past [8-Bit]",
    "Crypt of the NecroDancer: AMPLIFIED OST - FamilyJules and A_Rival",
    # 2. Japanese
    "神威 Original Soundtrack",
    "式神の城II - サウンドトラック",
    "『Ghostwire: Tokyo』 - 蜘蛛の糸サウンドトラック",
    # 3. Short/General
    "Incredibox Tracks",
    "The Spike Soundtrack",
    "20XX Soundtrack",
    "DOOM Soundtrack"
]

def search_vgmdb_with_playwright():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) width/1920 height/1080 AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        
        for q in QUERIES:
            print(f"\n--- QUERY: {q} ---")
            url = f"https://vgmdb.net/search?q={urllib.parse.quote(q)}"
            
            try:
                # Wait before each request to be polite
                time.sleep(random.uniform(2.5, 4.0))
                
                response = page.goto(url, wait_until="domcontentloaded", timeout=15000)
                if not response.ok:
                    print(f"Error: {response.status} {response.status_text}")
                    continue
                
                # CloudFlare might challenge us. Let's wait a tiny bit to make sure it's the actual page
                page.wait_for_timeout(1000)
                
                html_source = page.content()
                
                if "Just a moment..." in html_source and "cloudflare" in html_source.lower():
                    print("Error: Caught by CloudFlare Challenge!")
                    continue
                    
                data = parse_page(html_source)
                albums = data.get("albums", [])
                
                print(f"Found {len(albums)} albums.")
                for i, meta in enumerate(albums[:3]):
                    titles = meta.get('titles', {})
                    cat = meta.get('catalog', 'N/A')
                    rel_date = meta.get('release_date', 'N/A')
                    title_str = next(iter(titles.values())) if titles else "Unknown"
                    print(f"  {i+1}. {title_str} [{cat}] ({rel_date})")
                    
            except Exception as e:
                print(f"Error executing query {q}: {e}")
                
        browser.close()

if __name__ == "__main__":
    search_vgmdb_with_playwright()
