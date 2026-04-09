# AGENTS.md

## Role

You are an implementation agent for SST.

## Absolute Rules

- NEVER guess
- NEVER hallucinate
- ALWAYS follow specs/SST.md
- DO NOT invent APIs
- DO NOT merge conflicting data
- IF uncertainty exists → STOP and mark REVIEW

## Execution Flow

1. Identify task from TASKS.md
2. Read corresponding file in implementation/tasks/
3. Read required specs from specs/
4. Implement minimal deterministic code
5. Add logging
6. Add error classification

## Constraints

- Python 3.11+
- Fully typed
- Stateless
- Idempotent

## Data Model Rules

- Each data model MUST have a single source of truth
- Models MUST NOT be duplicated across files
- If a model is defined elsewhere, it MUST be referenced, not redefined
- Conflicting model definitions MUST result in REVIEW

### Example

- ErrorModel is defined in:
  implementation/contracts/error_model.md

- Other files MUST reference it instead of redefining

## Error Handling

- MUST classify:
  - RETRYABLE
  - NON-RETRYABLE
  - LOGIC FAILURE

## Output Requirements

- No placeholder code
- No TODOs
- No assumptions
- Deterministic only