# Steam API Integration Specification

## 1. Overview

Steam API provides soundtrack metadata tied to games.

---

## 2. Purpose

- Identify soundtrack albums
- Retrieve track lists and metadata

---

## 3. Input

- Steam App ID

---

## 4. Data Sources

- Steam Store API
- Steam Web API

---

## 5. Retrieved Data

- Soundtrack title
- Track names
- Game association
- Release info

---

## 6. Limitations

- Metadata may be incomplete
- No standardized schema
- Track durations often missing

---

## 7. Matching Rules

- Match by app ID
- Cross-reference with MusicBrainz

---

## 8. Failure Handling

- If API unavailable:
  → skip and continue

---

## 9. Final Principle

If any uncertainty exists:

→ DO NOT guess  
→ SEND TO REVIEW