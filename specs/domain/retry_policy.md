# Retry Policy

## RETRYABLE

- HTTP 429
- HTTP 5xx
- Timeout
- Network failure

## NON-RETRYABLE

- HTTP 404
- Invalid schema
- Parsing failure

## LOGIC FAILURE

- Low confidence
- Conflicts

## Strategy

- 1: immediate
- 2: +60s
- 3: +300s
- 4: +600s

- Max: 4 attempts
- Exponential backoff
- ±20% jitter

## Final

→ REVIEW