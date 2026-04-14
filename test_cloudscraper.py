import cloudscraper
scraper = cloudscraper.create_scraper()
res = scraper.get("https://vgmdb.net/search?q=Celeste")
print(res.status_code)
if res.status_code == 200:
    print(res.text[:200])
