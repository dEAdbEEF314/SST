# Task: storage

## Goal

Persist processed audio files and metadata into storage (SeaweedFS) in a deterministic and immutable manner.

---

## Input

- audio_file_path: str
- tagging_input: TaggingInput
- metadata: AlbumMetadata
- job_id: str

---

## Output

```python
str  # stored file path
```

---

## Storage Backend

* SeaweedFS (Filer API via HTTP)

---

## Target Path

````

/processed/{app_id}/{normalized_album_title}/{disc_number}-{track_number}-{normalized_title}.mp3

````
id="g92qlj"

---

## Metadata File

For each stored track, a corresponding JSON MUST be created:

```

{track_filename}.json

```
id="xw0yqq"

---

## Processing Steps

1. Normalize album title
2. Normalize track title
3. Zero-pad track number (e.g. 01, 02)
4. Construct deterministic file path
5. Upload audio file
6. Generate metadata JSON
7. Upload metadata file
8. Verify both uploads succeeded

---

## Normalization Rules

- Remove invalid filesystem characters
- Trim whitespace
- Replace separators with safe equivalents (e.g. "/" → "_")

---

## Metadata JSON Structure

MUST include:

- app_id
- game_title
- source
- score (if available)
- tags_applied
- processing_timestamp
- job_id
- track_id

---

## Constraints

- MUST NOT overwrite existing files
- MUST ensure path uniqueness
- MUST ensure atomic consistency (file + metadata)

---

## Atomicity Requirement

- If metadata upload fails → audio MUST NOT be considered stored
- If audio upload fails → metadata MUST NOT be written

---

## Error Handling

### RETRYABLE

- Network failure
- Storage service unavailable
- HTTP 5xx

→ Retry according to retry policy

---

### NON-RETRYABLE

- Invalid path construction
- Invalid file format
- Permission denied

→ FAIL immediately

---

### LOGIC FAILURE

- Missing required metadata
- Inconsistent tagging input

→ SEND TO REVIEW

---

## Logging

MUST include:

- job_id
- track_id
- final path
- upload status (audio / metadata)
- result (SUCCESS / FAIL / REVIEW)

---

## Security

- MUST validate file paths
- MUST prevent directory traversal

---

## Determinism

- Same input MUST produce identical path
- No randomness allowed

---

## Final Rule

If storage consistency cannot be guaranteed:

→ DO NOT STORE  
→ SEND TO REVIEW
