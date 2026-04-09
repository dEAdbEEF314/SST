# AcoustID Integration Specification

## 1. Overview

AcoustID is used for audio fingerprint-based identification.

---

## 2. Purpose

- Identify tracks via audio fingerprint
- Link recordings to MusicBrainz

---

## 3. Input

- Raw audio file

---

## 4. Process

1. Generate fingerprint (Chromaprint)
2. Submit to AcoustID API
3. Receive candidate matches

---

## 5. Output

```json
{
  "acoustid": "string",
  "recordings": [
    {
      "musicbrainz_recording_id": "string",
      "score": "float"
    }
  ]
}
```

---

## 6. Matching Rules

* Accept multiple candidates
* Do NOT auto-select if ambiguous
* Pass all candidates downstream

---

## 7. Failure Handling

* Retry on network errors
* If no match:
  → continue pipeline without fingerprint

---

## 8. Constraints

* API rate limits apply
* Requires API key

---

## 9. Final Principle

If any uncertainty exists:

→ DO NOT guess
→ SEND TO REVIEW
