# Task: normalization

## Goal

Normalize metadata across multiple sources into a consistent format.

---

## Input

- List of candidates
- Raw metadata from:
  - VGMdb
  - MusicBrainz
  - Steam

---

## Output

- Normalized metadata (AlbumMetadata)

---

## Responsibilities

- Normalize titles
- Normalize artist names
- Apply language priority
- Standardize formatting

---

## Rules

- MUST NOT create new metadata
- MUST NOT infer missing values
- MUST NOT override higher-priority source data

---

## Language Strategy

Priority:

1. User config
2. English
3. Original

---

## Normalization Steps

1. Trim whitespace
2. Remove redundant labels (e.g. "Original Soundtrack")
3. Standardize casing
4. Normalize separators (e.g. "-", ":")

---

## Conflict Handling

- If fields differ between sources:
  - Apply source priority
  - If unclear → REVIEW

---

## Failure Conditions

- Missing required fields
- Conflicting critical fields
- Ambiguous normalization

→ SEND TO REVIEW

---

## Determinism

- No randomness
- Same input MUST produce same output