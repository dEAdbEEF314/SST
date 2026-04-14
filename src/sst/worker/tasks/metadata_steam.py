import logging
from typing import List
from prefect import task
from sst.contracts.interfaces import Candidate, AlbumMetadata, Track

logger = logging.getLogger(__name__)

@task(name="Search Steam Metadata")
def search_steam_task(app_id: int) -> List[Candidate]:
    """
    Queries the public unauthenticated Steam Store API for AppDetails.
    """
    import requests
    logger.info(f"Querying Steam Store API for AppID {app_id}...")
    url = f"https://store.steampowered.com/api/appdetails?appids={app_id}"
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            logger.error(f"Steam API returned HTTP {response.status_code}")
            return []
            
        data = response.json()
        if not data or str(app_id) not in data or not data[str(app_id)].get("success"):
            logger.warning(f"Steam API returned no success for AppID {app_id}")
            return []
            
        app_data = data[str(app_id)]["data"]
        # Convert to Candidate
        # Steam API provides the game banner title, but not individual tracks natively
        # So we leave tracks empty.
        meta = AlbumMetadata(
            title=app_data.get("name", "Unknown Steam Title"),
            track_count=0,
            release_date=app_data.get("release_date", {}).get("date", ""),
            tracks=[]
        )
        
        cand = Candidate(
            source="Steam",
            confidence_score=0.9, # High confidence it perfectly matches the Steam ID
            metadata=meta,
            raw_data=app_data
        )
        return [cand]
        
    except Exception as e:
        logger.error(f"Steam task failed: {e}")
        return []
