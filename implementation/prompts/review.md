# Review Prompt

## Purpose

This prompt is used when the system cannot deterministically resolve metadata.

It ensures that ambiguous or conflicting cases are handled safely without guessing.

---

## Input

- Candidate list (with scores)
- Source labels (vgmdb / musicbrainz / steam)
- Extracted metadata fields
- Conflict details (if any)

---

## Instructions

You MUST:

- Analyze all candidates and their scores
- Identify inconsistencies between sources
- Highlight conflicting fields explicitly
- Evaluate whether a deterministic resolution is possible

---

## Constraints

- DO NOT generate new metadata
- DO NOT guess missing values
- DO NOT merge conflicting data blindly
- DO NOT prioritize lower-ranked sources without justification

---

## Decision Logic

### RESOLVED

Return this ONLY if:

- One candidate is clearly superior based on score and consistency
- No critical conflicts exist
- Decision is deterministic

### REVIEW_REQUIRED

Return this if:

- Scores are too close
- Critical fields conflict (e.g. album title, artist, track count)
- Metadata is incomplete
- Any uncertainty exists

---

## Output Format

```json
{
  "decision": "RESOLVED | REVIEW_REQUIRED",
  "reason": "string",
  "selected_source": "vgmdb | musicbrainz | steam | null",
  "conflicts": [
    {
      "field": "string",
      "values": ["value1", "value2"]
    }
  ]
}
```

---

## Conflict Definition

A conflict is defined as:

* Different values for the same critical field
* Missing vs present mismatch
* Structural inconsistency (e.g. track count mismatch)

---

## Critical Fields

* album_title
* album_artist
* composer
* release_year
* total_tracks

---

## Non-Ambiguity Rule

If any uncertainty exists:

→ REVIEW_REQUIRED

---

## Final Rule

Safety over completeness.

When in doubt:

→ DO NOT resolve
→ RETURN REVIEW_REQUIRED
