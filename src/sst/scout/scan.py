import os
import glob
import logging
from typing import List, Dict, Any
from dotenv import load_dotenv

from sst.utils.vdf_parser import parse_acf
from sst.scout.detect import detect_soundtrack

load_dotenv()
logger = logging.getLogger(__name__)

def scan_steam_library() -> List[Dict[str, Any]]:
    library_path = os.getenv("STEAM_LIBRARY_PATH")
    if not library_path:
        logger.error("STEAM_LIBRARY_PATH is not set in .env")
        return []
        
    if not os.path.isdir(library_path):
        logger.error(f"STEAM_LIBRARY_PATH does not exist: {library_path}")
        return []
        
    acf_pattern = os.path.join(library_path, "appmanifest_*.acf")
    acf_files = glob.glob(acf_pattern)
    
    candidates = []
    
    for acf_file in acf_files:
        try:
            with open(acf_file, 'r', encoding='utf-8') as f:
                content = f.read()
        except IOError as e:
            logger.warning(f"Could not read {acf_file}: {e}")
            continue
            
        metadata = parse_acf(content)
        app_id_str = metadata.get("appid")
        name = metadata.get("name", "")
        install_dir = metadata.get("installdir", "")
        
        if not app_id_str or not app_id_str.isdigit():
            logger.warning(f"Invalid appid in {acf_file}")
            continue
            
        app_id = int(app_id_str)
        
        is_soundtrack = detect_soundtrack(app_id, name)
        
        if is_soundtrack:
            audio_files = []
            
            common_path = os.path.join(library_path, "common", install_dir)
            music_path = os.path.join(library_path, "music", install_dir)
            
            search_paths = [common_path, music_path]
            
            for path in search_paths:
                if os.path.isdir(path):
                    for root, _, files in os.walk(path):
                        for file in files:
                            if file.lower().endswith(('.mp3', '.flac', '.wav', '.ogg', '.m4a')):
                                audio_files.append(os.path.join(root, file))
            
            candidates.append({
                "app_id": app_id,
                "name": name,
                "install_dir": install_dir,
                "audio_files": audio_files
            })
            
    return candidates
