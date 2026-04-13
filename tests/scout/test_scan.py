import os
import tempfile
from unittest.mock import patch
from sst.scout.scan import scan_steam_library

@patch("sst.scout.scan.detect_soundtrack")
def test_scan_steam_library_success(mock_detect):
    mock_detect.return_value = True
    
    with tempfile.TemporaryDirectory() as temp_dir:
        os.environ["STEAM_LIBRARY_PATH"] = temp_dir
        
        acf_path = os.path.join(temp_dir, "appmanifest_123.acf")
        with open(acf_path, "w") as f:
            f.write('"AppState"\n{\n"appid"\t"123"\n"name"\t"Game"\n"installdir"\t"GameDir"\n}')
            
        os.makedirs(os.path.join(temp_dir, "common", "GameDir", "audio"))
        with open(os.path.join(temp_dir, "common", "GameDir", "audio", "track.mp3"), "w") as f:
            f.write("fake mp3")
            
        os.makedirs(os.path.join(temp_dir, "music", "GameDir"))
        with open(os.path.join(temp_dir, "music", "GameDir", "track.flac"), "w") as f:
            f.write("fake flac")
            
        result = scan_steam_library()
        
        assert len(result) == 1
        cand = result[0]
        assert cand["app_id"] == 123
        assert cand["name"] == "Game"
        assert len(cand["audio_files"]) == 2
        
@patch("sst.scout.scan.detect_soundtrack")
def test_scan_steam_library_not_soundtrack(mock_detect):
    mock_detect.return_value = False
    
    with tempfile.TemporaryDirectory() as temp_dir:
        os.environ["STEAM_LIBRARY_PATH"] = temp_dir
        
        acf_path = os.path.join(temp_dir, "appmanifest_123.acf")
        with open(acf_path, "w") as f:
            f.write('"AppState"\n{\n"appid"\t"123"\n"name"\t"Game"\n"installdir"\t"GameDir"\n}')
            
        result = scan_steam_library()
        
        assert len(result) == 0
