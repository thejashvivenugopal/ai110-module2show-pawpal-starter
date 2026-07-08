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

## ✨ Features

- **Owner & multi-pet management** — one owner can track several pets, each with its own task list.
- **Care tasks** — every task has a duration, priority (high/medium/low), optional preferred time, frequency, and completion status.
- **Priority scheduling** — tasks are ordered high-to-low priority (shorter tasks break ties) and packed greedily into the owner's daily time budget.
- **Sort by time** — view tasks in chronological order by their preferred "HH:MM" time.
- **Filtering** — filter tasks by completion status (pending vs. all) or scope them to a single pet.
- **Conflict warnings** — the scheduler flags when two tasks want the same time slot and surfaces a warning (it never crashes the plan).
- **Daily/weekly recurrence** — completing a recurring task automatically queues its next occurrence (next day or next week).
- **Explainable plans** — every generated schedule includes reasoning (what was scheduled, what was skipped and why, and any conflicts).
- **Streamlit UI + CLI demo** — an interactive web app (`app.py`) and a terminal demo (`main.py`), backed by an automated test suite.

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

Run the full automated test suite with:

```bash
python -m pytest

# Run with coverage:
python -m pytest --cov
```

**What the tests cover** (13 tests in `tests/test_pawpal.py`):

- **Task basics** — completion status flips correctly; adding a task grows a pet's task count.
- **Sorting correctness** — `sort_by_time()` returns tasks in chronological order (untimed tasks last).
- **Filtering** — filter by completion status, and aggregate/scope tasks by pet.
- **Recurrence logic** — completing a *daily* task queues a follow-up for the next day; a *weekly* task for +7 days; a one-off task queues nothing.
- **Conflict detection** — duplicate preferred times are flagged; distinct times produce no warnings.
- **Scheduling constraints** — tasks over the time budget are skipped; completed tasks are not planned; an empty pet/owner yields a safe empty plan.

Sample test output:

```
============================= test session starts ==============================
platform darwin -- Python 3.14.0, pytest-9.1.1, pluggy-1.6.0
collected 13 items

tests/test_pawpal.py .............                                       [100%]

============================== 13 passed in 0.02s ==============================
```

**Confidence level: ★★★★☆ (4/5).** The core scheduling behaviors — sorting,
filtering, recurrence, conflict detection, and budget limits — are all covered
by passing tests, including key edge cases (empty pets, over-budget tasks,
same-time conflicts). One star is held back because conflict detection only
catches exact time matches (not overlapping durations), and recurrence assumes
the plan is generated on the task's due day, so there is room to harden the
date/overlap handling before I'd call it production-ready.

## 📐 Smarter Scheduling

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_tasks()`, `Scheduler.sort_by_time()` | Sort by priority (then shorter duration), or chronologically by `preferred_time` ("HH:MM") |
| Filtering | `Scheduler.filter_by_status()`, `Scheduler.filter_by_time()`, `Owner.get_tasks_for_pet()` | Filter by completion status, by time budget, or by pet name |
| Conflict handling | `Scheduler.detect_conflicts()` | Lightweight exact-time-match detection; returns warning strings instead of crashing |
| Recurring tasks | `Task.next_occurrence()`, `Pet.mark_task_complete()` | Completing a daily/weekly task auto-queues the next occurrence via `timedelta` |

## 📸 Demo Walkthrough

Launch the interactive app with:

```bash
streamlit run app.py
```

### Main UI features and available actions

- **Owner panel** — set the owner's name and a daily time budget (in minutes).
- **Pets panel** — add pets (name, species, notes); the list updates instantly.
- **Tasks panel** — pick a pet, add tasks (title, duration, priority, optional
  preferred time, and frequency). Tasks display sorted by time, with a
  Pending/All filter, and a **Mark complete** control.
- **Schedule panel** — a "Generate schedule" button produces today's plan as a
  table, with conflict warnings, skipped tasks, and the scheduler's reasoning.

### Example workflow

1. **Enter owner info** — set the name to "Alex" and a daily time budget of 90 minutes.
2. **Add a pet** — add "Biscuit" (dog). It appears under *Current pets*.
3. **Add tasks** — add "Morning walk" (30 min, high, 08:00, daily),
   "Breakfast" (10 min, high, 09:00), and "Grooming" (40 min, low).
4. **Review tasks** — they display sorted by time; toggle Pending/All to filter.
5. **Generate the schedule** — click *Generate schedule* to see today's ordered
   plan, any conflicts, and why each task was included or skipped.
6. **Mark a task complete** — completing the daily walk queues tomorrow's walk
   automatically.

### Key Scheduler behaviors shown

- **Priority + time-budget scheduling** — high-priority tasks are placed first;
  tasks that don't fit the budget are skipped with a reason.
- **Sort by time** — tasks and the schedule are shown in chronological order.
- **Conflict warnings** — two tasks at the same preferred time raise a warning.
- **Recurrence** — completing a daily/weekly task auto-creates the next one.

### Sample CLI output (`python main.py`)

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

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
