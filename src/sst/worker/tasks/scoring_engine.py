import logging
from typing import List, Optional
from sst.contracts.interfaces import Candidate

logger = logging.getLogger(__name__)

def evaluate_candidates(candidates: List[Candidate], expected_title: str) -> Optional[Candidate]:
    """
    Deterministic scoring engine.
    Computes confidence score based on overlap with expected strings.
    If multiple pass 0.55 or none pass, returns None (REVIEW).
    """
    logger.info(f"Evaluating {len(candidates)} candidates against expected title: {expected_title}")
    
    if not candidates:
        return None
        
    expected_lower = expected_title.lower()
    
    for cand in candidates:
        title_lower = cand.metadata.title.lower()
        score = 0.0
        
        # Exact substring match
        if expected_lower in title_lower or title_lower in expected_lower:
            score += 0.6
            
        # Source hierarchy boosters
        if cand.source == "Steam":
            score += 0.3
        elif cand.source == "VGMdb":
            score += 0.4 # Tied to MB Link, exceptionally high quality
        elif cand.source == "MusicBrainz":
            score += 0.2
            
        cand.confidence_score = score
        
    # Sort candidates by descending score
    candidates.sort(key=lambda x: x.confidence_score, reverse=True)
    
    best = candidates[0]
    
    if best.confidence_score < 0.55:
        logger.warning(f"Best candidate scored {best.confidence_score:.2f} < 0.55. Sending to REVIEW.")
        return None

    # Check for ambiguous margin
    if len(candidates) > 1:
        runner_up = candidates[1]
        if (best.confidence_score - runner_up.confidence_score) < 0.05:
            logger.warning("Unsafe margin between top candidates. Uncertainty exists -> REVIEW.")
            return None
            
    logger.info(f"Selected Best Candidate: {best.metadata.title} (Score: {best.confidence_score:.2f})")
    return best
