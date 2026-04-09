# Worker Design

## Overview

Workers are stateless processing units responsible for metadata resolution and tagging.

## Responsibilities

- Fetch metadata (Steam, MusicBrainz, VGMdb)
- Score candidates
- Select best match
- Apply tagging
- Handle conversion

## Pipeline

1. Fetch Steam metadata
2. Run soundtrack detection scoring
3. Query VGMdb
4. Score VGMdb results
5. If insufficient → query MusicBrainz
6. Score MusicBrainz results
7. If both fail → AcoustID fallback
8. Send to LLM validation
9. Apply tags
10. Store result

## Constraints

- MUST be stateless
- MUST be idempotent
- MUST not cache implicit state

## Error Handling

- Classify errors strictly
- Apply retry policy
- Send ambiguous cases to REVIEW

## Logging

Each step MUST log:

- job_id
- track_id
- step
- result
- error (if any)

## Performance

- Parallel execution allowed
- No shared mutable state