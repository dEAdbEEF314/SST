# System Design

## Overview

SST is a distributed, deterministic processing system for identifying and tagging Steam soundtrack audio files.

## Design Principles

- Deterministic behavior
- Stateless processing
- Idempotent operations
- Strict separation of concerns
- No implicit assumptions

## Components

### 1. Scout VM

- Scans Steam library
- Extracts AppID
- Detects soundtrack candidates
- Pushes ingest jobs

### 2. Core VM (Prefect)

- Orchestrates workflows
- Manages retries and state transitions
- Dispatches tasks to workers

### 3. Worker Containers

- Execute metadata resolution
- Perform scoring
- Apply tagging
- Handle file transformation

### 4. LLM Node

- Normalization
- Validation
- Conflict detection

### 5. Storage (SeaweedFS)

- Stores processed files
- Stores review cases
- Maintains archive

## Data Flow

1. Scout detects soundtrack
2. Ingest job created
3. Worker resolves metadata
4. LLM validates
5. Tagging applied
6. Stored or sent to review

## Failure Handling

- Retryable → automatic retry
- Logic failure → REVIEW
- Non-retryable → FAIL

## Guarantees

- No guessing
- No silent failures
- Full traceability via logs