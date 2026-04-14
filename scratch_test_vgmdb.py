import sys
import os
import requests
sys.path.append(os.path.join(os.getcwd(), 'vendor/vgmdb'))
from vgmdb.parsers.search import parse_page

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

def search_vgmdb(query):
    # Important: VGMdb's search works best without special characters sometimes, but we will test real queries.
    url = f"https://vgmdb.net/search?q={requests.utils.quote(query)}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9"
    }
    
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return {"error": f"HTTP {response.status_code}"}
        
    try:
        data = parse_page(response.text)
        return {"results": data.get("albums", [])}
    except Exception as e:
        return {"error": str(e)}

for q in QUERIES:
    print(f"\n--- QUERY: {q} ---")
    res = search_vgmdb(q)
    
    if "error" in res:
        print(f"Error: {res['error']}")
        continue
        
    albums = res["results"]
    print(f"Found {len(albums)} albums.")
    for i, meta in enumerate(albums[:3]):
        # Depending on hufman/vgmdb format, titles might be a dict containing 'en', 'ja', 'ja-latn', or a string
        titles = meta.get('titles', {})
        cat = meta.get('catalog', 'N/A')
        rel_date = meta.get('release_date', 'N/A')
        title_str = next(iter(titles.values())) if titles else "Unknown"
        print(f"  {i+1}. {title_str} [{cat}] ({rel_date})")

