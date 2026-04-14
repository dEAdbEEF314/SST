from prefect import flow, get_run_logger
from typing import Optional, List

from sst.worker.tasks.metadata_steam import fetch_steam_metadata_task
from sst.worker.tasks.metadata_vgmdb import search_vgmdb_task
from sst.worker.tasks.metadata_musicbrainz import search_musicbrainz_task
from sst.worker.tasks.scoring_engine import score_candidates_task, ScoringTarget
from sst.worker.tasks.acoustid_fallback import acoustid_fallback_task
from sst.worker.tasks.apply_tags import apply_tags_task
from sst.worker.tasks.storage_seaweed import store_results_task
from sst.worker.tasks.convert_audio import convert_lossless_to_aiff_task

@flow(name="Worker Pipeline: Process Album")
def process_album_flow(app_id: int, audio_file_paths: List[str], job_id: str, local_album_title: str):
    logger = get_run_logger()
    local_track_count = len(audio_file_paths)
    logger.info(f"Starting pipeline for Job: {job_id}, App: {app_id}, Tracks: {local_track_count}")
    
    # 1. Gather constraints (Ideally from Steam Metadata or local ACF if Steam fails)
    try:
        steam_meta = fetch_steam_metadata_task(app_id)
        # Refine target using Steam data if available
        target_title = steam_meta.get("name", local_album_title)
    except Exception as e:
        logger.warning(f"Steam Metadata failed, falling back to local ACF defaults. Error: {e}")
        target_title = local_album_title
        
    target = ScoringTarget(album_title=target_title, track_count=local_track_count)
    candidates = []
    
    # 2. Query VGMdb (Cached for the entire album run by executing once)
    try:
        vgmdb_cands = search_vgmdb_task(target_title)
        candidates.extend(vgmdb_cands)
    except Exception as e:
        logger.warning(f"VGMdb task skipped/failed: {e}")
        
    # 3. Score VGMdb
    vgmdb_result = score_candidates_task(candidates, target)
    best_candidate = vgmdb_result.best_candidate
    status = "SUCCESS" if vgmdb_result.success else "REVIEW"
    
    # 4. If VGMdb insufficient, query MusicBrainz
    if not vgmdb_result.success:
        logger.info("VGMdb result insufficient. Querying MusicBrainz.")
        try:
            mb_cands = search_musicbrainz_task(target_title)
            candidates.extend(mb_cands)
        except Exception as e:
            logger.warning(f"MusicBrainz task failed: {e}")
            
        mb_result = score_candidates_task(candidates, target)
        if mb_result.success:
            best_candidate = mb_result.best_candidate
            status = "SUCCESS"
        else:
            # 5. Fallback strictly to AcoustID using the FIRST track's fingerprint
            logger.info("MusicBrainz result insufficient. Falling back to AcoustID.")
            try:
                acoustid_cands = acoustid_fallback_task(audio_file_paths[0])
                candidates.extend(acoustid_cands)
                acoustid_result = score_candidates_task(candidates, target)
                if acoustid_result.success:
                    best_candidate = acoustid_result.best_candidate
                    status = "SUCCESS"
                else:
                    logger.error(f"LOGIC FAILURE: No confident candidate found across all sources. Reason: {acoustid_result.reason}")
                    best_candidate = acoustid_result.best_candidate
                    status = "REVIEW"
            except Exception as e:
                logger.error(f"LOGIC FAILURE: Fallback failed: {e}")
                status = "REVIEW"
                
    if not best_candidate:
        logger.error("LOGIC FAILURE: Engine returned no candidate. Pushing tracks to REVIEW unconditionally.")
        status = "REVIEW"
        
    is_success = (status == "SUCCESS")
    uploaded_paths = []
    
    # Loop over all local tracks for this album
    for track_index, file_path in enumerate(sorted(audio_file_paths)):
        logger.info(f"Processing Track {track_index + 1}/{local_track_count}: {file_path}")
        
        # 6. Audio Conversion (Lossless -> AIFF 24/48max)
        try:
            current_audio_path = convert_lossless_to_aiff_task(file_path)
        except Exception as e:
            logger.error(f"Audio conversion failed on {file_path}: {e}")
            return {"status": "REVIEW", "failed_on": "conversion"}
            
        if best_candidate and is_success:
            # 7. Apply ID3 tags if we have a confident match
            try:
                apply_tags_task(current_audio_path, best_candidate.metadata, track_index)
            except Exception as e:
                logger.error(f"Tagging failed on {current_audio_path}. REVIEW. Error: {e}")
                is_success = False

        # 8. Store results to SeaweedFS archive/ or review/
        try:
            meta_payload = best_candidate.metadata if best_candidate else None
            path = store_results_task(current_audio_path, meta_payload, track_index, app_id, job_id, is_success)
            uploaded_paths.append(path)
        except Exception as e:
            logger.error(f"Storage failed on {current_audio_path}. Error: {e}")
            return {"status": "REVIEW", "failed_on": "storage"}
            
    logger.info(f"Successfully finished job {job_id}. Processed {len(uploaded_paths)} files. Final Status: {status}")
    return {"status": "SUCCESS" if is_success else "REVIEW", "destinations": uploaded_paths}
