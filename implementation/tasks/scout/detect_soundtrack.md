# Task: detect_soundtrack

## Goal

Determine whether a given Steam app represents a soundtrack.

This decision MUST be deterministic and based on scoring rules.

---

## Input

- app_id: int
- steam_metadata: dict

### Expected Fields (if available)

- type
- name
- genres
- categories
- detailed_description

---

## Output

```python
bool  # True = soundtrack, False = not soundtrack
```

---

## Method

Apply scoring rules defined in:

→ specs/data/scoring_rules.md

---

## Scoring Rules

### Positive Signals

* type == "music" → +100
* name contains "soundtrack" → +60
* name contains "ost" → +40
* fullgame exists → +20
* genre contains "music" → +15
* description contains "soundtrack" → +10
* description contains audio format (mp3, flac, wav) → +10
* DLC category → +5

---

### Negative Signals

* name contains "artbook" → -50
* name contains "demo" → -50
* non-audio DLC → -30

---

## Thresholds

* score ≥ 50 → True (soundtrack)
* score 30–49 → Candidate (treated as False at this stage)
* score < 30 → False

---

## Normalization

Before evaluation:

* Convert all text to lowercase
* Trim whitespace
* Normalize unicode (if needed)

---

## Rules

* MUST NOT guess missing fields
* MUST only use available metadata
* MUST be deterministic

---

## Edge Cases

* Missing metadata → return False
* Ambiguous naming → rely strictly on score
* Conflicting signals → use final score only

---

## Logging

MUST log:

* app_id
* computed score
* decision (True / False)
* contributing factors

---

## Failure Handling

* Missing required structure → NON-RETRYABLE
* Invalid data type → NON-RETRYABLE

---

## Final Rule

If scoring cannot be computed:

→ DO NOT guess
→ RETURN False
