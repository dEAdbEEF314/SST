import logging
from sst.utils.steam_api import fetch_app_details, SteamAPIException
from sst.contracts.error_model import ErrorModel

logger = logging.getLogger(__name__)

def detect_soundtrack(app_id: int, basic_name: str) -> bool:
    """
    Determine whether a given Steam app represents a soundtrack.
    Returns True if score >= 50, otherwise False.
    """
    try:
        steam_metadata = fetch_app_details(app_id)
    except SteamAPIException as e:
        logger.warning(f"Failed to fetch metadata for {app_id}: {e.error.message}")
        steam_metadata = {}
        
    score = 0
    factors = []
    
    # Normalization: lower, trim
    name = (steam_metadata.get("name") or basic_name or "").lower().strip()
    app_type = (steam_metadata.get("type") or "").lower().strip()
    genres = steam_metadata.get("genres", [])
    categories = steam_metadata.get("categories", [])
    desc = (steam_metadata.get("detailed_description") or "").lower().strip()
    
    if not name and not app_type:
        logger.warning(f"Missing required structure for AppID: {app_id}")
        return False
        
    # Positive Signals
    if steam_metadata.get("fullgame"):
        score += 20
        factors.append("+20 fullgame")

    if app_type == "music":
        score += 100
        factors.append("+100 type=music")
        
    if "soundtrack" in name:
        score += 60
        factors.append("+60 name=soundtrack")
    if "ost" in name:
        score += 40
        factors.append("+40 name=ost")
        
    if any("music" in g for g in genres):
        score += 15
        factors.append("+15 genre=music")
        
    if "soundtrack" in desc:
        score += 10
        factors.append("+10 desc=soundtrack")
    if any(fmt in desc for fmt in ["mp3", "flac", "wav"]):
        score += 10
        factors.append("+10 desc=audio_format")
        
    is_dlc = False
    if app_type == "dlc" or any("dlc" in c or "downloadable content" in c for c in categories):
        score += 5
        factors.append("+5 dlc_category")
        is_dlc = True
        
    # Negative Signals
    if "artbook" in name:
        score -= 50
        factors.append("-50 name=artbook")
    if "demo" in name:
        score -= 50
        factors.append("-50 name=demo")
    
    # non-audio DLC
    if is_dlc and "music" not in app_type and "soundtrack" not in name and "ost" not in name:
        score -= 30
        factors.append("-30 non-audio")
        
    decision = score >= 50
    
    logger.info(f"AppID: {app_id} | Score: {score} | Decision: {decision} | Factors: {factors}")
    
    return decision
