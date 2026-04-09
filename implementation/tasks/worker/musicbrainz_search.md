# Task: search_musicbrainz

## Goal

Search MusicBrainz with normalized query.

## Input

- album_name: str

## Output

- List[Candidate]

## Rules

- Apply normalization before search

## Scoring

- Track count match
- Artist match
- Date match

## Failure

- Low score → REVIEW