# Metadata Schema Specification

## 1. Overview

This document defines the canonical metadata schema used within the SST (Steam Soundtrack Tagger) system.

The schema standardizes how soundtrack metadata is represented, normalized, and stored across all pipeline stages.

---

## 2. Core Principles

- **Deterministic**: Same input must always produce identical metadata
- **Extensible**: New fields can be added without breaking compatibility
- **Source-Agnostic**: Supports multiple metadata providers
- **Tagging-Oriented**: Optimized for ID3/FLAC tagging use cases

---

## 3. Root Structure

```json
{
  "album": {},
  "tracks": [],
  "identifiers": {},
  "credits": {},
  "assets": {},
  "source": {},
  "confidence": {}
}
```

---

## 4. Album Object

```json
{
  "title": "string",
  "sort_title": "string",
  "artist": "string",
  "album_artist": "string",
  "year": "integer",
  "release_date": "YYYY-MM-DD",
  "label": "string",
  "catalog_number": "string",
  "genre": ["string"],
  "total_tracks": "integer",
  "disc_total": "integer"
}
```

### Notes

* `sort_title`: normalized (no articles, consistent casing)
* `genre`: multiple allowed
* `year`: derived from `release_date` if missing

---

## 5. Tracks Array

```json
[
  {
    "track_number": "integer",
    "disc_number": "integer",
    "title": "string",
    "sort_title": "string",
    "artist": "string",
    "duration": "float",
    "isrc": "string",
    "acoustid": "string"
  }
]
```

### Notes

* `duration`: seconds (float)
* `acoustid`: used for fingerprint matching
* `artist`: overrides album artist if needed

---

## 6. Identifiers Object

```json
{
  "musicbrainz_release_id": "string",
  "musicbrainz_recording_ids": ["string"],
  "vgmdb_album_id": "string",
  "steam_app_id": "string",
  "steam_soundtrack_id": "string",
  "barcode": "string"
}
```

### Notes

* All identifiers are optional but strongly recommended
* Multiple recording IDs correspond to track list order

---

## 7. Credits Object

```json
{
  "composers": ["string"],
  "arrangers": ["string"],
  "performers": ["string"],
  "organizations": ["string"]
}
```

### Notes

* Arrays allow multiple contributors
* Order is not significant

---

## 8. Assets Object

```json
{
  "cover_art": {
    "url": "string",
    "local_path": "string",
    "checksum": "string"
  }
}
```

### Notes

* `checksum`: used for deduplication
* `local_path`: used after download stage

---

## 9. Source Object

```json
{
  "primary": "string",
  "secondary": ["string"],
  "raw": {}
}
```

### Notes

* `primary`: selected authoritative source
* `secondary`: fallback or merged sources
* `raw`: unprocessed source payload (for debugging)

---

## 10. Confidence Object

```json
{
  "overall": "float",
  "album_match": "float",
  "track_match": "float",
  "fingerprint_match": "float"
}
```

### Notes

* Values range: `0.0 - 1.0`
* Used for decision making in pipeline

---

## 11. Normalization Rules

### Strings

* Trim whitespace
* Normalize Unicode (NFKC)
* Remove control characters

### Titles

* Preserve original casing
* Generate `sort_title`:

  * Remove leading articles (a, an, the)
  * Lowercase
  * Normalize punctuation

### Dates

* Prefer full `YYYY-MM-DD`
* Fallback to `YYYY`

---

## 12. Tag Mapping (ID3/FLAC)

| Schema Field    | ID3 Frame | FLAC Vorbis |
| --------------- | --------- | ----------- |
| album.title     | TALB      | ALBUM       |
| album.artist    | TPE2      | ALBUMARTIST |
| tracks[].title  | TIT2      | TITLE       |
| tracks[].artist | TPE1      | ARTIST      |
| track_number    | TRCK      | TRACKNUMBER |
| disc_number     | TPOS      | DISCNUMBER  |
| year            | TYER      | DATE        |
| genre           | TCON      | GENRE       |

---

## 13. Validation Rules

* `album.title` MUST exist
* `tracks.length` MUST match `album.total_tracks` if defined
* `track_number` MUST be sequential per disc
* `confidence.overall` MUST exist

---

## 14. Extensibility

Future extensions MUST:

* Avoid breaking existing keys
* Use new top-level fields or nested namespaces
* Maintain backward compatibility

---

## 15. Final Principle

If any uncertainty exists:

→ DO NOT guess
→ SEND TO REVIEW
