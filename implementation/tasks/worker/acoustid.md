# Task: acoustid_fallback

## Goal

Use AcoustID as a last-resort identification method when all primary sources fail.

This task MUST only run under strict conditions.

---

## Preconditions

This task MUST execute ONLY if:

- VGMdb best score < 0.55
AND
- MusicBrainz best score < 0.55

If this condition is not met:

→ DO NOT EXECUTE  
→ RETURN without action

---

## Input

- audio_file_path: str
- duration: int (seconds)

---

## Output

- List[Candidate]

---

## External API

- AcoustID API
- Endpoint: /lookup

---

## Required Parameters

- api_key
- fingerprint
- duration

---

## Processing Steps

1. Generate fingerprint from audio file
2. Send request to AcoustID API
3. Parse response
4. Extract candidate matches
5. Convert to Candidate model

---

## Candidate Construction

Each candidate MUST include:

- source = "musicbrainz" (AcoustID resolves to MusicBrainz IDs)
- score (derived from AcoustID confidence)
- metadata (raw extracted data)

---

## Constraints

- MUST NOT override higher-priority sources
- MUST NOT be used as primary identification
- MUST treat results as low-confidence

---

## Scoring

- Use AcoustID confidence as base score
- Apply penalty if partial match
- Normalize score to [0, 1]

---

## Failure Handling

### RETRYABLE

- HTTP 429
- HTTP 5xx
- Network timeout

→ Retry according to retry policy

---

### NON-RETRYABLE

- Invalid fingerprint
- Missing duration
- Invalid response schema

→ FAIL immediately

---

### LOGIC FAILURE

- No matches found
- Multiple ambiguous matches

→ SEND TO REVIEW

---

## Logging

MUST include:

- job_id
- track_id
- fingerprint status
- number of candidates
- best score

---

## Security

- API key MUST be read from config
- MUST NOT hardcode credentials

---

## Final Rule

AcoustID is a fallback of last resort.

If results are unclear:

→ DO NOT trust  
→ SEND TO REVIEW