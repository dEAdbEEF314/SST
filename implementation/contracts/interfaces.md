# Interfaces

## Overview

This file defines the core data models (contracts) used across the SST system.

Rules:

- MUST be used consistently across all tasks
- MUST remain deterministic and minimal
- MUST be fully typed (Python 3.11+)
- MUST NOT be modified without corresponding spec updates

---

## Candidate

Represents a metadata candidate from an external source.

```python
from pydantic import BaseModel
from typing import Literal, Dict, Optional

class Candidate(BaseModel):
    source: Literal["vgmdb", "musicbrainz"]
    score: float
    metadata: Dict
```

---

## Track

Represents a single audio track.

```python id="track_model_01"
class Track(BaseModel):
    title: str
    artist: str
    track_number: int
    disc_number: int = 1
    duration: Optional[int] = None  # seconds
```

---

## AlbumMetadata

Represents normalized album-level metadata.

```python id="album_model_01"
class AlbumMetadata(BaseModel):
    album_title: str
    album_artist: str
    composer: Optional[str] = None
    release_year: Optional[int] = None
    genre: Optional[str] = None
    total_tracks: Optional[int] = None
    disc_total: int = 1
    source: Literal["vgmdb", "musicbrainz", "steam"]
```

---

## IdentificationResult

Represents the result of the identification phase.

```python id="ident_result_01"
class IdentificationResult(BaseModel):
    success: bool
    best_candidate: Optional[Candidate] = None
    candidates: list[Candidate]
    reason: Optional[str] = None  # e.g. "low_confidence", "conflict"
```

---

## TaggingInput

Represents the input required for tagging.

```python id="tagging_input_01"
class TaggingInput(BaseModel):
    track: Track
    album: AlbumMetadata
    app_id: int
    game_title: str
    source_url: Optional[str] = None
```

---

## ProcessingState

Represents the system state machine.

```python id="processing_state_01"
from typing import Literal

ProcessingState = Literal[
    "INGESTED",
    "IDENTIFIED",
    "ENRICHED",
    "TAGGED",
    "STORED",
    "FAILED"
]
```

---

## ErrorModel

ErrorModel is defined in:

→ implementation/contracts/error_model.md

This file MUST NOT redefine ErrorModel.

---

## LoggingRecord

Represents structured logging data.

```python id="logging_record_01"
class LoggingRecord(BaseModel):
    job_id: str
    track_id: Optional[str] = None
    step: str
    result: Literal["SUCCESS", "FAIL", "RETRY", "REVIEW"]
    error: Optional[str] = None
```

---

## Final Rule

All interfaces MUST remain stable and explicit.

If any ambiguity exists:

→ DO NOT modify
→ SEND TO REVIEW
