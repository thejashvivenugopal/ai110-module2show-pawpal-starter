# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Paste a sample of your app's CLI or Streamlit output here so a reader can see what a generated plan looks like:

```
============================================
PawPal+ — Today's Schedule for Alex
Pets: Biscuit, Miso
Time budget: 90 min
============================================
Today's plan:
  08:00 — Breakfast (10 min) [priority: high]
  08:10 — Morning walk (30 min) [priority: high]
  08:40 — Feed Miso (10 min) [priority: medium]
  08:50 — Play/enrichment (20 min) [priority: medium]

Skipped:
  Grooming — not enough time left in budget

Total time used: 70 min
Reasoning: Scheduled 4 of 5 due task(s) by priority within a 90-minute budget; 70 min used. Time conflicts: Conflict at 09:00: Breakfast, Feed Miso.

--------------------------------------------
Tasks sorted by time:
  08:00 — Morning walk
  09:00 — Breakfast
  09:00 — Feed Miso
  17:00 — Grooming
  18:00 — Play/enrichment

Pending (not completed) tasks: 5
Biscuit's tasks only: Grooming, Morning walk, Breakfast

--------------------------------------------
Schedule conflicts detected:
  ⚠️  Conflict at 09:00: Breakfast, Feed Miso

--------------------------------------------
Completed 'Morning walk' (daily). Tasks: 3 -> 4
  Next occurrence queued for: 2026-07-08
```

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
============================= test session starts ==============================
platform darwin -- Python 3.14.0, pytest-9.1.1, pluggy-1.6.0
collected 7 items

tests/test_pawpal.py .......                                             [100%]

============================== 7 passed in 0.01s ===============================
```

## 📐 Smarter Scheduling

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_tasks()`, `Scheduler.sort_by_time()` | Sort by priority (then shorter duration), or chronologically by `preferred_time` ("HH:MM") |
| Filtering | `Scheduler.filter_by_status()`, `Scheduler.filter_by_time()`, `Owner.get_tasks_for_pet()` | Filter by completion status, by time budget, or by pet name |
| Conflict handling | `Scheduler.detect_conflicts()` | Lightweight exact-time-match detection; returns warning strings instead of crashing |
| Recurring tasks | `Task.next_occurrence()`, `Pet.mark_task_complete()` | Completing a daily/weekly task auto-queues the next occurrence via `timedelta` |

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
