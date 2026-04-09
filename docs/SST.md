# SST integration specification

Last updated: 2026-04-09

---

## 1. Purpose

SST (Steam Soundtrack Tagger) is a distributed processing system that automatically identifies soundtrack audio files purchased on Steam, enriches metadata, applies tags, and stores them.

This project focuses on:

- Steam-purchased soundtracks only
- Accuracy over speed
- Deterministic behavior (no guessing)
- Clear separation of failure cases into review
- High automation with minimal manual intervention

---

## 2. Scope

### 2.1 Target

- Soundtracks from Steam Library (installed only)
- Local audio sources processed and stored via SeaweedFS

### 2.2 Non-target

- Non-Steam audio sources
- Non-installed / non-local files
- Real-time streaming
- Single-source decision making

---

## 3. Overall architecture

- Scout VM: Steam library scan, ACF parsing
- Core VM: Prefect orchestration
- Worker Container: metadata resolution, tagging
- LLM Node: normalization & validation
- SeaweedFS: storage

---

## 4. End-to-end processing

### 4.1 Scout ingest

1. Scan `steamapps/appmanifest_*.acf`
2. Extract AppID
3. Detect soundtrack (scoring)
4. Collect audio files
5. Normalize structure
6. Upload to ingest

---

### 4.2 Worker pipeline

1. Get Steam metadata (Storefront API)
2. Soundtrack detection (scoring)
3. VGMdb search
4. VGMdb scoring
5. If high confidence → adopt
6. Else → MusicBrainz search (normalized)
7. MusicBrainz scoring
8. If both < 0.55 → review
9. LAST RESORT: AcoustID (conditional only)
10. LLM validation (dual provider)
11. Format conversion
12. Tag writing
13. Store (archive/review)

---

## 5. State transition

- INGESTED
- IDENTIFIED
- ENRICHED
- TAGGED
- STORED
- FAILED

---

## 6. Identification Strategy

### 6.1 Source Priority

1. VGMdb
2. MusicBrainz
3. Steam
4. filename

---

### 6.2 Soundtrack Detection Algorithm

#### Scoring

- type == music → +100
- name contains "soundtrack" → +60
- name contains "ost" → +40
- fullgame exists → +20
- genre contains music → +15
- description contains soundtrack → +10
- description contains audio format → +10
- DLC category → +5

#### Penalties

- artbook → -50
- demo → -50
- non-audio DLC → -30

#### Thresholds

- ≥ 50 → accept
- 30–49 → candidate
- < 30 → reject

---

### 6.3 MusicBrainz Search Normalization

- Remove: soundtrack / ost / original soundtrack
- Remove brackets
- Trim spaces

---

### 6.4 MusicBrainz Scoring

- DigitalMedia → +30
- No Bandcamp → +10
- Track count match → +40
- Date match → +20
- Artist match → +50

---

### 6.5 AcoustID Policy

- Use ONLY when:
  - VGMdb < 0.55 AND MB < 0.55
- Partial → Full fallback
- Low reliability

---

### 6.6 Filename Parsing

- Extract track number and title
- Supported formats:
  - 01 - Title
  - 01.Title
  - 01_Title

If parsing fails or structure is complex:
→ send to review

---

## 7. Tagging specification (ID3v2.3)

### Core mapping

- TIT2: Title (VGMdb > MB > filename)
- TPE1: Performer (VGMdb > MB)
- TCOM: Composer (PRIMARY)
- TALB: Album (VGMdb > MB > Steam)
- TPE2: Album Artist
- TCON: MUST include "Steam; VGM; [Genre]"
- TIT1: "[Game Title] | Steam"
- COMM: "[Game Title] | tags | AppID | URL"
- TDRC: Year
- TRCK: n/total
- TPOS: disc/total (1/1 required)

---

### TSRC (ISRC)

- Source: MusicBrainz only
- If missing → leave empty
- Never guess

---

### Language Strategy

Priority:

1. user config
2. English
3. original

Apply to:

- album
- title
- artist

TLAN: ISO 639-2

---

## 8. Additional Sources

### Steam description

- Use for composer fallback
- Low reliability

### VGMdb

- Primary metadata
- Catalog number

### AcoustID

- Last resort only

---

## 9. Unsupported Sources

- Spotify
- YouTube
- Apple Music

---

## 10. Non-Ambiguity Rules

- NEVER guess metadata
- NEVER hallucinate
- ALWAYS follow priority
- IF uncertain → review
- DO NOT merge conflicting data blindly

---

## 11. Priority Rules

### Source priority

- VGMdb > MusicBrainz > Steam > filename

### Conflict resolution

- Higher score wins
- If difference < 0.05 → review

---

## 12. Format Conversion

- Lossless → AIFF
- OGG → MP3 320kbps
- MP3 unchanged

---

## 13. Quality Criteria

- ≥ 90% correct identification
- Album match correct
- No tagging errors

---

## 14. Execution Environment

- Python 3.11+
- Prefect 3.x
- Docker
- Stateless / Idempotent

---

## 15. Logging

Must include:

- job_id
- track_id
- step
- result
- error

---

## 16. Retry and Failure Handling

### 16.1 Error Classification

Errors MUST be classified before handling:

#### RETRYABLE

- HTTP 429 (rate limit)
- HTTP 5xx
- Network timeout
- Connection failure
- Temporary DNS failure

→ MUST retry

---

#### NON-RETRYABLE

- HTTP 404
- Invalid response schema
- Parsing failure

→ FAIL immediately

---

#### LOGIC FAILURE

- Low confidence score
- Conflicting metadata
- Ambiguous match

→ SEND TO REVIEW

---

### 16.2 Retry Strategy

For RETRYABLE errors:

- Attempt 1: immediate
- Attempt 2: +60 seconds
- Attempt 3: +300 seconds
- Attempt 4: +600 seconds

Max attempts: 4

---

### 16.3 Backoff Policy

- Exponential backoff MUST be used
- Add random jitter (±20%)
- Respect external API rate limits if known

---

### 16.4 Final Fallback

If all retries fail:

→ SEND TO REVIEW

---

## 17. Final Principle

If any uncertainty exists:

→ DO NOT guess  
→ SEND TO REVIEW