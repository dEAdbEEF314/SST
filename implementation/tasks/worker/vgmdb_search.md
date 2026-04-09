# Task: search_vgmdb

## Goal

Search VGMdb and return candidates.

## Input

- album_name: str

## Output

- List[Candidate]

## Rules

- Use official API only
- If unavailable → STOP (REVIEW)

## Scoring

See specs/data/scoring_rules.md

## Error Handling

- 429 → retry
- 404 → fail
- ambiguous → review