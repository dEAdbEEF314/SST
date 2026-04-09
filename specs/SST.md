# SST Specification (Root)

Last updated: 2026-04-09

---

## 1. Purpose

This document is the **root specification** for SST (Steam Soundtrack Tagger).

It defines:

- System-wide rules
- Cross-domain constraints
- Source of truth relationships
- Deterministic guarantees

All detailed behavior is defined in sub-specs under:

- `specs/domain/`
- `specs/data/`
- `specs/integrations/`

This file MUST be treated as the **entry point for all specifications**.

---

## 2. Core Principles

All components in SST MUST follow these principles:

### 2.1 Determinism

- Same input MUST produce identical output
- No randomness allowed
- No implicit state

---

### 2.2 No Guessing

- Missing data MUST NOT be inferred
- Unknown values MUST remain empty
- Ambiguity MUST result in REVIEW

---

### 2.3 Strict Failure Separation

All failures MUST be classified:

- RETRYABLE → retry
- NON-RETRYABLE → fail
- LOGIC FAILURE → review

---

### 2.4 Source Priority Enforcement

Global priority:

1. VGMdb  
2. MusicBrainz  
3. Steam  
4. filename  

- Lower-priority sources MUST NOT override higher ones
- Conflicts MUST NOT be merged blindly

---

### 2.5 Idempotency

- All operations MUST be repeatable
- No duplicate side effects
- Storage MUST be immutable

---

## 3. Specification Hierarchy

```

specs/SST.md              ← ROOT (this file)
├── domain/               ← Behavior & logic
├── data/                 ← Data models & mappings
└── integrations/         ← External systems

```

---

### 3.1 Domain Specifications

Defines system behavior:

- `pipeline.md` → pipeline stages
- `state_machine.md` → lifecycle states
- `identification.md` → matching strategy
- `tagging.md` → tagging rules
- `retry_policy.md` → retry logic

---

### 3.2 Data Specifications

Defines structure and transformation:

- `metadata_schema.md` → canonical schema
- `id3_mapping.md` → tagging mapping
- `scoring_rules.md` → scoring system

---

### 3.3 Integration Specifications

Defines external dependencies:

- `steam_api.md`
- `musicbrainz.md`
- `vgmdb.md`
- `acoustid.md`

---

## 4. System Flow (Abstract)

```

INPUT
→ SCOUT
→ IDENTIFY
→ FETCH
→ MERGE
→ SCORE
→ VALIDATE (LLM)
→ TAG
→ STORE | REVIEW | FAIL

```

Detailed behavior MUST follow:

→ `specs/domain/pipeline.md`

---

## 5. State Machine

System states:

- INGESTED
- IDENTIFIED
- ENRICHED
- TAGGED
- STORED
- FAILED

Transitions MUST follow:

→ `specs/domain/state_machine.md`

---

## 6. Identification Rules (Global)

- MUST follow source priority
- MUST use scoring-based decisions
- MUST NOT merge conflicting candidates
- MUST send ambiguous cases to REVIEW

Detailed rules:

→ `specs/domain/identification.md`  
→ `specs/data/scoring_rules.md`

---

## 7. Tagging Rules (Global)

- MUST follow ID3v2.3 mapping strictly
- MUST NOT write uncertain values
- MUST respect language priority

Detailed mapping:

→ `specs/domain/tagging.md`  
→ `specs/data/id3_mapping.md`

---

## 8. Data Consistency Rules

- All metadata MUST conform to canonical schema
- Schema is defined in:

→ `specs/data/metadata_schema.md`

Constraints:

- Required fields MUST exist
- Track counts MUST match
- Identifiers MUST remain consistent

---

## 9. Integration Rules

For ALL external APIs:

- MUST validate responses
- MUST NOT assume undocumented fields
- MUST classify errors

Per-service specs:

- Steam → `integrations/steam_api.md`
- MusicBrainz → `integrations/musicbrainz.md`
- VGMdb → `integrations/vgmdb.md`
- AcoustID → `integrations/acoustid.md`

---

## 10. Retry & Error Handling

Global rules:

- Only RETRYABLE errors trigger retries
- Retry policy MUST follow:

→ `specs/domain/retry_policy.md`

- LOGIC FAILURE MUST go to REVIEW
- NON-RETRYABLE MUST fail immediately

---

## 11. Review System

A case MUST be sent to REVIEW if:

- Confidence is low
- Multiple candidates are similar
- Critical fields conflict
- Required metadata is missing

Rule:

```

IF uncertainty exists → REVIEW

```

---

## 12. Storage Guarantees

- Storage MUST be deterministic
- Storage MUST be immutable
- File paths MUST be reproducible

Details defined in:

→ design/storage_design.md (implementation reference)

---

## 13. LLM Constraints

LLM usage is STRICTLY LIMITED:

- ONLY normalization and validation
- MUST NOT generate new data
- MUST NOT guess
- MUST be deterministic

Details:

→ implementation/tasks/llm/*  
→ design/llm_node_design.md

---

## 14. Logging Requirements

All components MUST log:

- job_id
- track_id (if available)
- step
- result
- error (if any)

No silent failures allowed.

---

## 15. Implementation Contract

All implementations MUST:

- Follow this spec AND sub-specs
- Not redefine data models
- Not introduce new behavior without spec update

If conflict exists:

```

STOP → REVIEW

```

---

## 16. Final Rule

This system prioritizes **correctness over completion**.

If any uncertainty exists at any stage:

```

DO NOT guess
DO NOT proceed
SEND TO REVIEW

```