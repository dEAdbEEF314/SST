from pydantic import BaseModel
from typing import Literal, Dict, Optional

class Candidate(BaseModel):
    source: Literal["vgmdb", "musicbrainz"]
    score: float
    metadata: Dict

class Track(BaseModel):
    title: str
    artist: str
    track_number: int
    disc_number: int = 1
    duration: Optional[int] = None  # seconds

class AlbumMetadata(BaseModel):
    album_title: str
    album_artist: str
    composer: Optional[str] = None
    release_year: Optional[int] = None
    genre: Optional[str] = None
    total_tracks: Optional[int] = None
    disc_total: int = 1
    source: Literal["vgmdb", "musicbrainz", "steam"]

class IdentificationResult(BaseModel):
    success: bool
    best_candidate: Optional[Candidate] = None
    candidates: list[Candidate]
    reason: Optional[str] = None  # e.g. "low_confidence", "conflict"

class TaggingInput(BaseModel):
    track: Track
    album: AlbumMetadata
    app_id: int
    game_title: str
    source_url: Optional[str] = None

ProcessingState = Literal[
    "INGESTED",
    "IDENTIFIED",
    "ENRICHED",
    "TAGGED",
    "STORED",
    "FAILED"
]

class LoggingRecord(BaseModel):
    job_id: str
    track_id: Optional[str] = None
    step: str
    result: Literal["SUCCESS", "FAIL", "RETRY", "REVIEW"]
    error: Optional[str] = None
