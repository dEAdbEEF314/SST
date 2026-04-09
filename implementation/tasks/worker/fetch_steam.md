# Task: fetch_steam_metadata

## Goal

Fetch metadata for a given Steam AppID using the Steam Storefront API.

This metadata is used for soundtrack detection and fallback enrichment.

---

## Input

- app_id: int

---

## Output

```python
dict  # validated Steam metadata
```

---

## External API

* Steam Storefront API
* Endpoint:

GET [https://store.steampowered.com/api/appdetails?appids={app_id}](https://store.steampowered.com/api/appdetails?appids={app_id})

---

## Expected Response Structure

```json
{
  "{app_id}": {
    "success": true,
    "data": {
      "name": "string",
      "type": "string",
      "genres": [...],
      "categories": [...],
      "detailed_description": "string"
    }
  }
}
```

---

## Processing Steps

1. Send GET request with app_id
2. Validate response structure
3. Check `success == true`
4. Extract `data` field
5. Return normalized metadata dict

---

## Normalization

* Convert text fields to lowercase where appropriate
* Ensure all expected keys exist (set to None if missing)
* Flatten nested fields if needed

---

## Required Fields (if available)

* name
* type
* genres
* categories
* detailed_description

---

## Constraints

* MUST NOT assume missing fields
* MUST validate JSON structure before use
* MUST NOT modify semantic meaning of data

---

## Error Handling

### RETRYABLE

* HTTP 429 (rate limit)
* HTTP 5xx
* Network timeout
* Connection failure

→ MUST retry using retry policy

---

### NON-RETRYABLE

* HTTP 404
* success == false
* Missing root structure
* Invalid JSON schema

→ FAIL immediately

---

### LOGIC FAILURE

* Critical fields missing (e.g. name and type both missing)

→ SEND TO REVIEW

---

## Logging

MUST include:

* job_id
* app_id
* API response status
* success flag
* extracted fields summary

---

## Rate Limiting

* MUST respect API limits
* SHOULD apply backoff when receiving 429

---

## Security

* No authentication required
* MUST NOT inject user-controlled data into URL without validation

---

## Final Rule

If response structure is unclear or incomplete:

→ DO NOT guess
→ SEND TO REVIEW
