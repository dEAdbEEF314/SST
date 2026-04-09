# Error Model

## Overview

All errors in SST MUST be explicitly classified into a predefined category.

No unclassified or generic exceptions are allowed.

---

## Error Categories

### 1. RETRYABLE

Represents temporary failures that may succeed upon retry.

#### Examples

- HTTP 429 (rate limit)
- HTTP 5xx (server errors)
- Network timeout
- Connection failure
- Temporary DNS resolution failure

#### Behavior

- MUST retry according to retry policy
- MUST apply exponential backoff
- MUST include jitter (±20%)

---

### 2. NON_RETRYABLE

Represents permanent failures that will not succeed on retry.

#### Examples

- HTTP 404 (resource not found)
- Invalid API response schema
- Parsing failure
- Missing required fields
- Unsupported format

#### Behavior

- MUST fail immediately
- MUST NOT retry
- MUST log detailed reason

---

### 3. LOGIC_FAILURE

Represents semantic or decision-level failures.

#### Examples

- Low confidence score
- Conflicting metadata between sources
- Multiple equally valid candidates
- Ambiguous identification
- Incomplete normalization

#### Behavior

- MUST NOT retry
- MUST SEND TO REVIEW
- MUST include full context for inspection

---

## Error Model Definition

```python
from pydantic import BaseModel
from typing import Literal

class ErrorModel(BaseModel):
    type: Literal["RETRYABLE", "NON_RETRYABLE", "LOGIC_FAILURE"]
    message: str
    retry_count: int = 0
```

---

## Error Handling Rules

* Every error MUST be classified before handling
* No raw exceptions should propagate without classification
* Logging MUST include:

  * error type
  * message
  * retry_count

---

## Retry Interaction

* Only RETRYABLE errors trigger retry logic
* NON_RETRYABLE and LOGIC_FAILURE MUST NOT be retried

---

## Logging Requirements

Each error MUST be logged with:

* job_id
* track_id (if available)
* step
* error.type
* error.message

---

## Final Rule

If error classification is uncertain:

→ DO NOT guess
→ SEND TO REVIEW
