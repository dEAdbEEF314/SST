
# MusicBrainz Integration Specification

## 1. Overview

MusicBrainz is the primary structured metadata source.

---

## 2. Purpose

- Retrieve album and track metadata
- Resolve recordings and releases

---

## 3. Query Methods

- By recording ID (from AcoustID)
- By search (album name, artist)
- By release ID

---

## 4. Retrieved Data

- Release title
- Tracklist
- Artists
- Dates
- ISRCs

---

## 5. Output Mapping

Maps to internal metadata schema.

---

## 6. Matching Rules

- Prefer exact matches
- Track count must align
- Duration similarity required

---

## 7. Rate Limiting

- Must respect MusicBrainz API policies
- Use caching where possible

---

## 8. Failure Handling

- Retry on transient errors
- If no match:
  → fallback to other sources

---

## 9. Final Principle

If any uncertainty exists:

→ DO NOT guess  
→ SEND TO REVIEW
