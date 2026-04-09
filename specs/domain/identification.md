# Identification Strategy

## Source Priority

1. VGMdb
2. MusicBrainz
3. Steam
4. filename

## Rules

- Higher score wins
- If difference < 0.05 → REVIEW
- NEVER merge conflicting data

## MusicBrainz Normalization

- Remove:
  - soundtrack
  - ost
  - original soundtrack
- Remove brackets
- Trim spaces