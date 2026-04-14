from prefect import flow, get_run_logger
from typing import Optional, List

from sst.worker.tasks.metadata_steam import search_steam_task
from sst.worker.tasks.metadata_musicbrainz import search_musicbrainz_task
from sst.worker.tasks.scoring_engine import evaluate_candidates
from sst.worker.tasks.acoustid_fallback import acoustid_identify_task
from sst.worker.tasks.apply_tags import apply_tags_task
from sst.worker.tasks.storage_seaweed import store_results_task
from sst.worker.tasks.convert_audio import convert_lossless_to_aiff_task
from sst.llm.normalization import normalize_metadata_task
from sst.llm.validation import validate_metadata_task
from sst.contracts.interfaces import Candidate

@flow(name="Worker Pipeline: Process Album")
def process_album_flow(app_id: int, audio_file_paths: List[str], job_id: str, local_album_title: str):
    logger = get_run_logger()
    local_track_count = len(audio_file_paths)
    logger.info(f"Starting pipeline for Job: {job_id}, App: {app_id}, Tracks: {local_track_count}")
    
    # 1. Gather baseline constraints from Steam
    try:
        steam_cands = search_steam_task(app_id)
        if steam_cands:
            target_title = steam_cands[0].metadata.title
        else:
            target_title = local_album_title
    except Exception as e:
        logger.warning(f"Steam Metadata failed, falling back to local ACF defaults. Error: {e}")
        steam_cands = []
        target_title = local_album_title
        
    candidates = list(steam_cands)
    
    # 2. Query MusicBrainz
    try:
        mb_cands = search_musicbrainz_task(target_title)
        candidates.extend(mb_cands)
    except Exception as e:
        logger.warning(f"MusicBrainz task failed: {e}")
        
    # 3. Evaluate Steam + MusicBrainz candidates deterministically
    best_candidate = evaluate_candidates(candidates, target_title)
    
    # 4. Fallback strictly to AcoustID if metadata is insufficient
    if not best_candidate:
        logger.info("MusicBrainz/Steam result insufficient. Falling back to AcoustID.")
        try:
            acoustid_ident = acoustid_identify_task(audio_file_paths[0])
            if acoustid_ident:
                # If we had a real acoustid pipeline it would append candidates here
                pass
            best_candidate = evaluate_candidates(candidates, target_title) # Re-evaluate
        except Exception as e:
            logger.error(f"LOGIC FAILURE: Fallback failed: {e}")
            
    if not best_candidate:
        logger.error("LOGIC FAILURE: Engine returned no confident candidate. Pushing tracks to REVIEW unconditionally.")
        status = "REVIEW"
        final_metadata = None
    else:
        # Phase 3 LLM Tasks: Normalization & Validation
        logger.info("Normalizing candidate metadata via LLM...")
        try:
            norm_decision = normalize_metadata_task(candidates)
            final_metadata = norm_decision.normalized_metadata
            logger.info(f"LLM Normalization complete. Confidence: {norm_decision.confidence}. Rationale: {norm_decision.rationale}")
            
            logger.info("Validating unified metadata via LLM...")
            val_decision = validate_metadata_task(final_metadata, candidates)
            if not val_decision.is_valid:
                logger.error(f"LLM Validation failed: {val_decision.failure_reason}. Rerouting to REVIEW.")
                status = "REVIEW"
            else:
                status = "SUCCESS"
        except Exception as e:
            logger.error(f"LLM Task Failed. Error: {e}. Falling back to REVIEW.")
            status = "REVIEW"
            final_metadata = best_candidate.metadata
        
    is_success = (status == "SUCCESS")
    uploaded_paths = []
    
    # Loop over all local tracks for this album
    for track_index, file_path in enumerate(sorted(audio_file_paths)):
        logger.info(f"Processing Track {track_index + 1}/{local_track_count}: {file_path}")
        
        # Audio Conversion (Lossless -> AIFF 24/48max)
        try:
            current_audio_path = convert_lossless_to_aiff_task(file_path)
        except Exception as e:
            logger.error(f"Audio conversion failed on {file_path}: {e}")
            return {"status": "REVIEW", "failed_on": "conversion"}
            
        if final_metadata and is_success:
            # Apply ID3 tags if we have a confident match
            try:
                apply_tags_task(current_audio_path, final_metadata, track_index + 1)
            except Exception as e:
                logger.error(f"Tagging failed on {current_audio_path}. REVIEW. Error: {e}")
                is_success = False

        # Store results to SeaweedFS archive/ or review/
        try:
            meta_payload = final_metadata if final_metadata else None
            path = store_results_task(current_audio_path, meta_payload, track_index, app_id, job_id, is_success)
            uploaded_paths.append(path)
        except Exception as e:
            logger.error(f"Storage failed on {current_audio_path}. Error: {e}")
            return {"status": "REVIEW", "failed_on": "storage"}
            
    logger.info(f"Successfully finished job {job_id}. Processed {len(uploaded_paths)} files. Final Status: {status}")
    return {"status": "SUCCESS" if is_success else "REVIEW", "destinations": uploaded_paths}
