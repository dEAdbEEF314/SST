import os
import sys
import logging
from typing import List, Optional
from prefect import task
import urllib.parse
from pydantic import BaseModel
from sst.contracts.interfaces import Candidate, AlbumMetadata, Track

logger = logging.getLogger(__name__)

# Append vendor parser
sys.path.append(os.path.join(os.getcwd(), 'vendor/vgmdb'))
try:
    from vgmdb.parsers.search import parse_page as parse_search_page
    from vgmdb.parsers.album import parse_page as parse_album_page
except ImportError:
    logger.warning("VGMdb parsers not found. Ensure vendor/vgmdb is initialized.")

@task(name="Fetch VGMdb Metadata (Playwright)", retries=0)
def fetch_vgmdb_album_task(url: str) -> Optional[Candidate]:
    """
    STRICTLY MANUAL / CONDITIONAL USAGE ONLY.
    Uses Playwright to bypass Cloudflare and fetch an explicitly provided VGMdb album URL.
    Returns a Candidate object if successful.
    """
    from playwright.sync_api import sync_playwright

    logger.info(f"Attempting manual/targeted VGMdb fetch via Playwright: {url}")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        
        try:
            response = page.goto(url, wait_until="domcontentloaded", timeout=20000)
            if not response or not response.ok:
                logger.warning(f"VGMdb Fetch Failed: HTTP {response.status if response else 'Unknown'}")
                return None
                
            # Allow potential Cloudflare challenge to clear
            page.wait_for_timeout(2000)
            html_source = page.content()
            
            if "Just a moment..." in html_source and "cloudflare" in html_source.lower():
                logger.error("VGMdb Fetch Blocked by Cloudflare Challenge.")
                return None
                
            data = parse_album_page(html_source)
            
            # Map parsed data -> Candidate
            titles = data.get('names', {})
            rel_date = data.get('release_date', '')
            
            # Pick English or Romaji title if defined safely
            title_str = titles.get('en', titles.get('ja-latn', list(titles.values())[0] if titles else "Unknown"))
            
            track_count = 0
            if 'discs' in data:
                track_count = sum(len(disc.get('tracks', [])) for disc in data['discs'])
                
            if not track_count:
                return None
            
            metadata = AlbumMetadata(
                title=title_str,
                track_count=track_count,
                release_date=rel_date,
                tracks=[] # Explicitly mapped later if needed
            )
            
            return Candidate(
                source="VGMdb",
                confidence_score=0.8,
                metadata=metadata,
                raw_data=data
            )
            
        except Exception as e:
            logger.error(f"VGMdb Playwright Error: {e}")
            return None
        finally:
            browser.close()
