# Pipeline Domain Specification

## 1. Overview

This document defines the SST pipeline architecture.

The pipeline transforms raw inputs into fully tagged, validated soundtrack metadata.

---

## 2. Pipeline Stages

```

INPUT → SCOUT → IDENTIFY → FETCH → MERGE → SCORE → REVIEW → EXPORT

```

---

## 3. Stage Definitions

### 3.1 INPUT

- Accepts:
  - Audio files
  - Folder structures
  - Steam app IDs

---

### 3.2 SCOUT

Detects candidate metadata sources.

#### Responsibilities

- Extract audio fingerprints (AcoustID)
- Detect embedded metadata
- Identify Steam soundtrack relationships

---

### 3.3 IDENTIFY

Determines candidate releases.

#### Responsibilities

- Query MusicBrainz
- Match fingerprints to recordings
- Resolve album candidates

---

### 3.4 FETCH

Fetches full metadata from sources.

#### Sources

- MusicBrainz
- VGMdb
- Steam API

---

### 3.5 MERGE

Combines metadata from multiple sources.

#### Rules

- Priority-based merge
- Preserve source attribution
- Resolve conflicts deterministically

---

### 3.6 SCORE

Assigns confidence scores.

#### Metrics

- Track match ratio
- Fingerprint accuracy
- Metadata completeness

---

### 3.7 REVIEW

Handles uncertainty.

#### Rule

If confidence < threshold:

→ SEND TO REVIEW

---

### 3.8 EXPORT

Outputs final metadata.

#### Targets

- ID3 tags
- FLAC tags
- JSON output

---

## 4. Failure Handling

- No silent failure
- All errors logged
- Retry where applicable

---

## 5. Final Principle

If any uncertainty exists:

→ DO NOT guess  
→ SEND TO REVIEW
