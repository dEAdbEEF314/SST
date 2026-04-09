# ID3 Mapping Specification

## Overview

This document defines the exact mapping from SST metadata to ID3v2.3 tags.

All tagging MUST strictly follow this specification.

---

## Standard

- ID3 Version: 2.3
- Encoding: UTF-16 (preferred) or ISO-8859-1 if required

---

## Core Tag Mapping

### TIT2 (Title)

- Source Priority:
  1. VGMdb
  2. MusicBrainz
  3. filename

---

### TPE1 (Performer)

- Source Priority:
  1. VGMdb
  2. MusicBrainz

---

### TCOM (Composer)

- PRIMARY FIELD
- Source Priority:
  1. VGMdb
  2. MusicBrainz
  3. Steam (fallback only)

---

### TALB (Album)

- Source Priority:
  1. VGMdb
  2. MusicBrainz
  3. Steam

---

### TPE2 (Album Artist)

- SHOULD match album-level artist
- Source Priority:
  1. VGMdb
  2. MusicBrainz

---

### TCON (Genre)

MUST include:

```

Steam; VGM; {Genre}

```
id="f8i5xg"

- Genre derived from metadata if available
- MUST NOT omit "Steam" or "VGM"

---

### TIT1 (Content Group)

Format:

```

{Game Title} | Steam

```
id="y2mxq5"

---

### COMM (Comment)

Format:

```

{Game Title} | tags | {AppID} | {URL}

```
id="4kmoyl"

---

### TDRC (Year)

- Source Priority:
  1. VGMdb
  2. MusicBrainz

- MUST be 4-digit year

---

### TRCK (Track Number)

Format:

```

{track_number}/{total_tracks}

```
id="oax4fp"

- Track number MUST be zero-padded

---

### TPOS (Disc Number)

Format:

```

{disc_number}/{total_discs}

```
id="i3c3af"

- MUST always exist
- Default: 1/1

---

## TSRC (ISRC)

- Source: MusicBrainz ONLY
- If unavailable → leave empty
- MUST NOT guess

---

## TLAN (Language)

- ISO 639-2 format

### Priority

1. User configuration
2. English
3. Original language

---

## Language Application

Fields affected:

- Title
- Album
- Artist

---

## Normalization Rules

- Trim whitespace
- Remove redundant labels (e.g. "Original Soundtrack")
- Preserve official naming when available

---

## Constraints

- MUST NOT invent metadata
- MUST NOT merge conflicting sources
- MUST follow source priority strictly

---

## Failure Conditions

- Missing required fields (Title, Album, Artist)
- Conflicting critical metadata

→ SEND TO REVIEW

---

## Determinism

- Same input MUST produce identical tags
- No randomness allowed

---

## Final Rule

If any tag value is uncertain:

→ DO NOT WRITE TAG  
→ SEND TO REVIEW
