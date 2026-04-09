# LLM Node Design

## Overview

LLM Node is responsible for metadata normalization and validation.

## Responsibilities

- Normalize metadata across sources
- Validate consistency
- Detect conflicts
- Enforce non-ambiguity rules

## Input

- Multiple metadata candidates
- Source labels
- Scores

## Output

- Validated metadata OR
- REVIEW decision

## Rules

- NEVER generate new metadata
- NEVER guess missing values
- ONLY validate and normalize

## Dual Provider Strategy

- Use two independent LLM providers
- Compare outputs
- If disagreement → REVIEW

## Normalization Tasks

- Title normalization
- Artist normalization
- Language prioritization

## Validation Rules

- Reject conflicting fields
- Reject low-confidence matches
- Enforce source priority

## Failure Conditions

- Inconsistent metadata
- Ambiguous match
- Missing critical fields

→ SEND TO REVIEW

## Determinism Constraint

- Prompts MUST be fixed
- No randomness allowed