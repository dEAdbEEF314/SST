# SST (Steam Soundtrack Tagger)

Deterministic soundtrack identification and tagging system for Steam-purchased audio.

## Principles

- Accuracy over speed
- Deterministic behavior
- No guessing
- Strict failure separation (REVIEW)

## Structure

- specs/          → Source of truth (WHAT)
- design/         → System design (HOW)
- implementation/ → Executable tasks for AI
- tests/          → Validation

## Entry Points

- AGENTS.md       → AI behavior rules
- TASKS.md        → Execution plan

## Workflow

1. Read TASKS.md
2. Select task
3. Follow corresponding file in implementation/tasks/
4. Follow specs strictly
5. Implement code

## Requirements

- Python 3.11+
- Prefect 3.x
- Docker