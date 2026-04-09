# ARCHITECTURE

## Components

- Scout VM
- Core VM (Prefect)
- Worker Container
- LLM Node
- SeaweedFS

## Flow

Scout → Ingest → Worker → LLM → Storage

## Key Characteristics

- Stateless processing
- Idempotent jobs
- Deterministic decisions

## Failure Handling

- Retryable → retry
- Logic failure → review