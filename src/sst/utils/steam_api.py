import requests
from typing import Dict, Any

from sst.contracts.error_model import ErrorModel

class SteamAPIException(Exception):
    def __init__(self, error: ErrorModel):
        self.error = error
        super().__init__(error.message)

def fetch_app_details(app_id: int) -> Dict[str, Any]:
    """
    Fetch and validate Steam app details from the Storefront API.
    Returns normalized metadata dict or raises SteamAPIException with ErrorModel.
    """
    url = f"https://store.steampowered.com/api/appdetails?appids={app_id}"
    
    try:
        response = requests.get(url, timeout=10)
    except requests.exceptions.Timeout:
        raise SteamAPIException(ErrorModel(type="RETRYABLE", message="Network timeout"))
    except requests.exceptions.ConnectionError:
        raise SteamAPIException(ErrorModel(type="RETRYABLE", message="Connection failure"))
    except requests.exceptions.RequestException as e:
        raise SteamAPIException(ErrorModel(type="RETRYABLE", message=str(e)))
        
    if response.status_code == 429:
        raise SteamAPIException(ErrorModel(type="RETRYABLE", message="HTTP 429 Rate limited"))
    elif response.status_code >= 500:
        raise SteamAPIException(ErrorModel(type="RETRYABLE", message=f"HTTP {response.status_code} Server Error"))
    elif response.status_code == 404:
        raise SteamAPIException(ErrorModel(type="NON_RETRYABLE", message="HTTP 404 Not found"))
    elif response.status_code != 200:
        raise SteamAPIException(ErrorModel(type="RETRYABLE", message=f"HTTP {response.status_code}"))
        
    try:
        data = response.json()
    except ValueError:
        raise SteamAPIException(ErrorModel(type="NON_RETRYABLE", message="Invalid JSON schema"))
        
    if not isinstance(data, dict):
        raise SteamAPIException(ErrorModel(type="NON_RETRYABLE", message="Missing root structure"))
        
    app_data = data.get(str(app_id))
    if not isinstance(app_data, dict):
        raise SteamAPIException(ErrorModel(type="NON_RETRYABLE", message="Missing root structure for app_id"))
        
    success = app_data.get("success")
    if not success:
        raise SteamAPIException(ErrorModel(type="NON_RETRYABLE", message="success == false"))
        
    extracted_data = app_data.get("data")
    if not isinstance(extracted_data, dict):
        raise SteamAPIException(ErrorModel(type="NON_RETRYABLE", message="Missing data object"))
    
    # Normalization
    result = {}
    result["name"] = extracted_data.get("name")
    result["type"] = extracted_data.get("type", "").lower() if extracted_data.get("type") else None
    
    # Genres
    genres = extracted_data.get("genres", [])
    result["genres"] = [g.get("description", "").lower() for g in genres if isinstance(g, dict)] if genres else []
    
    # Categories
    categories = extracted_data.get("categories", [])
    result["categories"] = [c.get("description", "").lower() for c in categories if isinstance(c, dict)] if categories else []
    
    # Description
    result["detailed_description"] = extracted_data.get("detailed_description", "").lower() if extracted_data.get("detailed_description") else None
    
    # Fullgame
    result["fullgame"] = extracted_data.get("fullgame")

    
    # Check logic failure explicitly (critical fields missing)
    if not result["name"] and not result["type"]:
        raise SteamAPIException(ErrorModel(type="LOGIC_FAILURE", message="name and type both missing", retry_count=0))
        
    return result
