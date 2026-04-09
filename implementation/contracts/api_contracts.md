# API Contracts

## Overview

This document defines all external API interaction contracts.

Rules:

- MUST follow official API specifications
- MUST NOT assume undocumented fields
- MUST validate all responses
- MUST classify errors

---

## Steam Storefront API

### Endpoint

GET /appdetails?appids={app_id}

### Response Handling

- Validate JSON structure
- Extract:
  - name
  - type
  - genres
  - detailed_description

### Errors

- 429 → RETRYABLE
- 5xx → RETRYABLE
- 404 → NON-RETRYABLE

---

## MusicBrainz API

### Endpoint

GET /ws/2/release/?query={query}&fmt=json

### Headers

- User-Agent REQUIRED

### Response Handling

- Extract:
  - title
  - artist-credit
  - date
  - track-count

### Constraints

- MUST normalize query before request

---

## VGMdb

### Rule

- No official API guaranteed
- DO NOT scrape

### Behavior

→ If no API access available:
→ STOP and mark REVIEW

---

## AcoustID API

### Endpoint

POST /lookup

### Required

- API key
- Fingerprint
- Duration

### Usage Policy

- LAST RESORT ONLY
- Only when both VGMdb and MusicBrainz fail

---

## Validation Rules

- All responses MUST be schema-validated
- Missing required fields → NON-RETRYABLE
- Unexpected structure → NON-RETRYABLE

---

## Final Rule

If API behavior is unclear:

→ DO NOT guess  
→ SEND TO REVIEW