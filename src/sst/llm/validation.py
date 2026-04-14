import os
import instructor
from litellm import completion
from typing import List
from pydantic import BaseModel, Field
from sst.contracts.interfaces import Candidate, AlbumMetadata

class ValidationDecision(BaseModel):
    is_valid: bool = Field(..., description="True if the metadata is safe to write directly to audio ID3 tags. False if there are conflicts.")
    is_ambiguous: bool = Field(..., description="True if the normalizer lacked sufficient data to confidently identify the album.")
    has_conflicts: bool = Field(..., description="True if multiple sources provided substantially different track lists, years, or titles.")
    failure_reason: str = Field(None, description="If is_valid is False, the explicit reason why.")

def validate_metadata_task(normalized_data: AlbumMetadata, raw_candidates: List[Candidate]) -> ValidationDecision:
    """
    Validates the normalized payload against the original source structures to catch logic failures or conflicts.
    """
    model_name = os.getenv("LLM_MODEL", "gemini/gemini-1.5-pro-latest")
    client = instructor.from_litellm(completion)
    
    cands_dump = [cand.model_dump() for cand in raw_candidates]
    norm_dump = normalized_data.model_dump()
    
    prompt = f"""
    You are a strict data validator checking the integrity of a normalized `AlbumMetadata` object against its raw, unnormalized sources.
    
    NORMALIZED OUTPUT TO CHECK:
    {norm_dump}
    
    RAW SOURCE CANDIDATES:
    {cands_dump}
    
    VALIDATION RULES:
    1. Cross-check sources. Do the required fields fundamentally exist and line up?
    2. Check for conflicts. Did two sources assert wildly different track counts (e.g. 50 vs 12)? If so, `has_conflicts = True`.
    3. If the data is incredibly sparse (e.g. only a title, no artists, no tracks), mark `is_ambiguous = True`.
    4. If ANY conflicts exist or ambiguity is present, `is_valid` MUST be False.
    """
    
    try:
        decision = client.chat.completions.create(
            model=model_name,
            temperature=0.0,
            response_model=ValidationDecision,
            messages=[
                {"role": "system", "content": "You are a deterministic validation node. Output pure facts based on the payload."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2048,
        )
        return decision
    except Exception as e:
        raise ValueError(f"NON_RETRYABLE: LLM Validation Failed: {e}")
