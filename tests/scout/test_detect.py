import pytest
from unittest.mock import patch
from sst.scout.detect import detect_soundtrack
from sst.utils.steam_api import SteamAPIException
from sst.contracts.error_model import ErrorModel

@patch("sst.scout.detect.fetch_app_details")
def test_detect_soundtrack_pure_music(mock_fetch):
    mock_fetch.return_value = {
        "type": "music",
        "name": "Super Game Soundtrack",
        "genres": ["music", "adventure"],
        "detailed_description": "Contains the full flac soundtrack."
    }
    # type=music(+100), name=soundtrack(+60), genre=music(+15), desc=soundtrack(+10), desc=flac(+10)
    # Score = 195 >= 50
    assert detect_soundtrack(1234, "Super Game Soundtrack") == True

@patch("sst.scout.detect.fetch_app_details")
def test_detect_soundtrack_artbook(mock_fetch):
    mock_fetch.return_value = {
        "type": "dlc",
        "name": "Super Game Artbook",
        "genres": ["adventure"]
    }
    # dlc(+5), name=artbook(-50), non_audio DLC(-30)
    # Score = -75 < 50
    assert detect_soundtrack(1235, "Super Game Artbook") == False

@patch("sst.scout.detect.fetch_app_details")
def test_detect_soundtrack_missing_api(mock_fetch):
    # Testing when API fails, it falls back to basic name evaluation
    mock_fetch.side_effect = SteamAPIException(ErrorModel(type="RETRYABLE", message="timeout"))
    
    # basic_name="soundtrack" -> missing type, but wait...
    # Score = 60 (name=soundtrack) >= 50.
    assert detect_soundtrack(1236, "Game Soundtrack OST") == True

@patch("sst.scout.detect.fetch_app_details")
def test_detect_soundtrack_dlc_audio(mock_fetch):
    mock_fetch.return_value = {
        "type": "dlc",
        "name": "Super Game OST",
        "categories": [{"description": "downloadable content"}]
    }
    # type=dlc(+5), name=ost(+40) -> Score = 45 < 50
    # "ost" guarantees no non-audio penalty (-30) is applied.
    assert detect_soundtrack(1237, "Super Game OST") == False

@patch("sst.scout.detect.fetch_app_details")
def test_detect_soundtrack_fullgame(mock_fetch):
    mock_fetch.return_value = {
        "type": "dlc",
        "name": "Super Game - Original Music",
        "fullgame": {"appid": 123},
        "detailed_description": "mp3 and flac available"
    }
    # type=dlc(+5), fullgame(+20), mp3/flac(+10), total 35. Still candidate.
    assert detect_soundtrack(1238, "Super Game - Original Music") == False
