import os
import time
import logging
from typing import List, Dict, Any
from prefect import task
import urllib.parse
from sst.contracts.interfaces import Candidate, AlbumMetadata, Track
try:
    from sst.worker.tasks.metadata_vgmdb import fetch_vgmdb_album_task
except ImportError:
    fetch_vgmdb_album_task = None

logger = logging.getLogger(__name__)

MB_BASE = "https://musicbrainz.org/ws/2"

@task(name="Search MusicBrainz Metadata", retries=2, retry_delay_seconds=3)
def search_musicbrainz_task(local_title: str) -> List[Candidate]:
    """
    Queries MusicBrainz API for Release Groups matching the given title.
    Politely respects MusicBrainz rate limiting (1 request per second).
    If a VGMdb URL-relation is found in the Release, it fetches it via the connected VGMdb manual task.
    """
    import requests
    logger.info(f"Querying MusicBrainz for '{local_title}'...")
    user_agent = os.getenv("USER_AGENT", "SteamSoundtrackTagger-Scout/0.1.0 ( your@email.com )")
    headers = {"User-Agent": user_agent, "Accept": "application/json"}
    
    # 1. Search Release Groups
    # url encode the local title safely
    query = urllib.parse.quote(local_title)
    search_url = f"{MB_BASE}/release-group?query={query}&limit=3"
    
    candidates = []
    
    try:
        response = requests.get(search_url, headers=headers, timeout=15)
        time.sleep(1) # MusicBrainz rate limit policy
        
        if response.status_code != 200:
            logger.error(f"MB Search returned HTTP {response.status_code}")
            return []
            
        data = response.json()
        rgs = data.get("release-groups", [])
        
        for rg in rgs:
            rgid = rg.get("id")
            
            # Fetch the specific release details with url relationships to check for VGMdb links!
            rel_url = f"{MB_BASE}/release-group/{rgid}?inc=url-rels+releases&fmt=json"
            rel_res = requests.get(rel_url, headers=headers, timeout=15)
            time.sleep(1) # Polite delay
            
            if rel_res.status_code != 200:
                continue
                
            rg_details = rel_res.json()
            
            # Find VGMdb URL from relations
            vgmdb_url = None
            for relation in rg_details.get("relations", []):
                target_url = relation.get("url", {}).get("resource", "")
                if "vgmdb.net/" in target_url:
                    vgmdb_url = target_url
                    break
                    
            vgmdb_candidate = None
            if vgmdb_url and fetch_vgmdb_album_task:
                # If MB has safely linked VGMdb, use Playwright to pull it specifically.
                logger.info(f"MusicBrainz linked VGMdb! Attempting to fetch explicitly: {vgmdb_url}")
                vgmdb_candidate = fetch_vgmdb_album_task.fn(url=vgmdb_url)
                
            if vgmdb_candidate:
                # Prioritize the extremely rich VGMdb candidate over the sparse MB one
                candidates.append(vgmdb_candidate)
                continue
                
            meta = AlbumMetadata(
                title=rg.get("title", ""),
                track_count=0,
                release_date=rg.get("first-release-date", ""),
                tracks=[]
            )
            
            candidates.append(Candidate(
                source="MusicBrainz",
                confidence_score=0.7, # Exact matches are bumped up later by the scoring engine
                metadata=meta,
                raw_data=rg_details
            ))
            
        return candidates
        
    except Exception as e:
        logger.error(f"MusicBrainz task failed: {e}")
        return []
