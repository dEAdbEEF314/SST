# Storage Design

## Overview

SeaweedFS is used as the primary storage system for SST.

The storage layer is responsible for:

- Persisting processed audio files
- Storing metadata alongside files
- Isolating ambiguous cases for manual review
- Maintaining deterministic, immutable storage behavior

---

## Design Principles

- Write-once (immutable storage)
- No in-place mutation
- Full traceability
- Deterministic file paths
- Separation of processed vs review data

---

## Storage Backend

- System: SeaweedFS
- Mode: Filer + Volume servers
- Access: HTTP API (preferred)

---

## Directory Structure

```

/ingest/
/processed/
/review/
/archive/

```

---

## Processed Data Layout

```

/processed/{app_id}/{normalized_album_title}/{disc_number}-{track_number}-{normalized_title}.mp3

```

### Rules

- `normalized_album_title` MUST be filesystem-safe
- `normalized_title` MUST remove invalid characters
- Track numbers MUST be zero-padded (e.g. 01, 02)
- Disc number MUST always be present (default: 1)

---

## Ingest Layout

```

/ingest/{job_id}/raw/

```

### Contents

- Original audio files
- Raw directory structure (unchanged)
- Temporary processing artifacts

---

## Review Layout

```

/review/{job_id}/

```

### MUST Include

- Original files
- All candidate metadata (JSON)
- Scoring results
- Error logs
- Reason for review

---

## Archive Layout

```

/archive/{app_id}/{timestamp}/

```

### Purpose

- Store previous versions
- Enable rollback
- Preserve history

---

## Metadata Storage

Each processed track MUST have a corresponding metadata file:

```

{track_filename}.json

```

### Metadata JSON MUST include:

- source (vgmdb / musicbrainz / steam)
- score
- applied tags
- processing timestamp
- job_id
- track_id
- validation result

---

## Access Pattern

- Processed data → read-heavy
- Ingest data → write-heavy
- Review data → read/write (manual inspection)

---

## Constraints

- MUST NOT overwrite existing processed files
- MUST use unique job_id for ingest and review
- MUST ensure atomic write (file + metadata)

---

## Failure Handling

If storage fails:

- Classify error (retryable / non-retryable)
- Retry if applicable
- If persistent failure → SEND TO REVIEW

---

## Future Extensions

- Content-addressable storage (hash-based paths)
- Deduplication layer
- Metadata indexing (external DB)

---

## Final Rule

Storage MUST NOT introduce ambiguity.

If any uncertainty exists:

→ DO NOT STORE  
→ SEND TO REVIEW
