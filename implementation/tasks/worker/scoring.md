# Task: scoring

## Goal

Score and rank metadata candidates from multiple sources in a deterministic way.

This task selects the best candidate or determines that the result is ambiguous.

---

## Input

- candidates: List[Candidate]

---

## Output

```python
IdentificationResult
```

---

## Scoring Sources

* VGMdb
* MusicBrainz
* (Optional) AcoustID-derived candidates

---

## Scoring Rules

### Base Score

Each candidate MUST already include a base score derived from its source-specific logic.

---

### Additional Scoring (MusicBrainz)

* Format == DigitalMedia → +30
* No Bandcamp → +10
* Track count match → +40
* Release date match → +20
* Artist match → +50

---

### Normalization

* Normalize all scores to range [0, 1]
* If raw scoring is additive → convert to normalized scale

---

## Ranking

1. Sort candidates by score (descending)
2. Identify top candidate
3. Compare with second-best

---

## Decision Rules

### ACCEPT

Return success if:

* Top candidate score ≥ minimum_confidence (default: 0.55)
  AND
* (Top - Second) ≥ confidence_review_delta (default: 0.05)

---

### REVIEW

Return REVIEW if:

* Top score < minimum_confidence
* Difference between top two < 0.05
* Conflicting metadata detected

---

### FAIL

Return FAIL if:

* No candidates exist

---

## Conflict Detection

Conflict occurs if:

* Album title mismatch
* Artist mismatch
* Track count mismatch

If conflict detected:

→ REVIEW

---

## Output Construction

```python
IdentificationResult(
    success=bool,
    best_candidate=Candidate | None,
    candidates=List[Candidate],
    reason=str | None
)
```

---

## Constraints

* MUST NOT modify candidate metadata
* MUST NOT merge candidates
* MUST NOT infer missing values

---

## Logging

MUST include:

* number of candidates
* scores
* selected candidate
* decision (SUCCESS / REVIEW / FAIL)

---

## Failure Handling

### LOGIC FAILURE

* Ambiguous candidates
* Conflicting high-score results

→ SEND TO REVIEW

---

### NON-RETRYABLE

* Invalid candidate structure

→ FAIL immediately

---

## Determinism

* Same input MUST produce same output
* No randomness allowed

---

## Final Rule

If decision is not clearly deterministic:

→ DO NOT select
→ SEND TO REVIEW
