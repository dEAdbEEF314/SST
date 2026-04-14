import os
import instructor
from litellm import completion
from typing import List, Dict, Any
from pydantic import BaseModel, Field
from sst.contracts.interfaces import Candidate, AlbumMetadata, Track

class NormalizationDecision(BaseModel):
    normalized_metadata: AlbumMetadata = Field(..., description="The highly strictly normalized metadata based on the source priority and language priority.")
    confidence: float = Field(..., description="Confidence score from 0.0 to 1.0 of how cleanly the data merged without contradictions.")
    rationale: str = Field(..., description="Short explanation of how the title/language was selected.")

def normalize_metadata_task(candidates: List[Candidate], target_language: str = None) -> NormalizationDecision:
    """
    Passes candidates to the unified LLM to deterministically normalize the data into a single AlbumMetadata object.
    Temperature is locked to 0.0 to strictly prevent hallucinations/guessing.
    """
    if not candidates:
        raise ValueError("LOGIC FAILURE: No candidates provided for normalization.")

    if not target_language:
        target_language = os.getenv("TARGET_LANGUAGE", "en")
        
    model_name = os.getenv("LLM_MODEL", "gemini/gemini-1.5-pro-latest")
    
    # Initialize instructor with litellm
    client = instructor.from_litellm(completion)
    
    # Dump candidates into pure JSON for the prompt context
    cands_dump = [cand.model_dump() for cand in candidates]
    
    prompt = f"""
    You are a strict data normalizer for a video game soundtrack pipeline.
    Your job is to normalize multiple candidate data sources into a single, clean `AlbumMetadata` object.
    
    INPUT CANDIDATES (Ranked implicitly by system logic):
    {cands_dump}
    
    RULES DEFINED BY SPEC:
    1. **Language Priority Strategy**: 
       First try to output strings in `{target_language}`. 
       If `{target_language}` is not available or incomplete, fallback to English ("en"). 
       If English is incomplete, fallback to the Original language string.
    2. MUST NOT create new metadata or infer missing values not present in the inputs.
    3. MUST NOT override fields confirmed by higher-priority sources unless fixing casing/whitespaces.
    4. NORMALIZATION STEPS:
       - Trim all whitespace.
       - Remove redundant suffix labels (e.g., remove "Original Soundtrack", "OST", "Digital Soundtrack").
       - Standardize casing to proper title case where applicable.
       - Normalize separators (e.g., use a single hyphen "-" or colon ":" consistently, replacing em-dashes).
       
    Conflict Handling:
    - If fields differ, generally trust the highest detailed source (VGMdb > MusicBrainz > Steam).
    - Rate the `confidence` score lower if sources deeply conflict on critical things like Track Count.
    """
    
    try:
        decision = client.chat.completions.create(
            model=model_name,
            temperature=0.0,
            response_model=NormalizationDecision,
            messages=[
                {"role": "system", "content": "You are deterministic execution node. Strict adherence to instructions is mandatory."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=8192,
        )
        return decision
    except Exception as e:
        raise ValueError(f"NON_RETRYABLE: LLM Normalization Failed: {e}")
