# PawPal+ Project Reflection

## 1. System Design

**Core user actions**

PawPal+ is built around three core actions a pet owner should be able to perform:

1. **Add a pet (and owner) profile.** The user enters basic information about themselves and their pet — owner name, pet name, species or breed, and any care preferences or constraints, such as how much time they have available each day. This profile is the foundation everything else builds on, since the app plans care around a specific pet.

2. **Add a care task for the pet.** The user records something the pet needs done — a walk, feeding, medication, grooming, enrichment, and so on. Each task includes at minimum a duration and a priority, and optionally a preferred time or a recurrence pattern. These tasks are the raw material the scheduler reasons over.

3. **Generate and view today's daily plan.** The user asks the app to produce a daily schedule from their task list while respecting constraints like available time and task priority. The app displays the ordered plan clearly and, ideally, explains why it chose that arrangement — for example, placing high-priority tasks first or dropping a low-priority task when time runs out. This is the app's main payoff: turning tasks and constraints into an actionable plan.

**a. Initial design**

My initial design centers on four core classes plus one output object:

- **Owner** — represents the app user and is the source of scheduling
  constraints. It holds the owner's name, a daily time budget (minutes
  available for pet care), a preferences dictionary, and the list of pets
  they own. Its job is to manage pets and expose the constraints the
  scheduler must respect.

- **Pet** — represents the animal being cared for. It holds the pet's name,
  species, free-text notes, and its own list of care tasks. Its
  responsibility is to own and manage that task list (add, edit, remove).

- **Task** — represents a single unit of care (walk, feeding, meds, grooming,
  enrichment). It holds a name, duration in minutes, priority, and optional
  preferred time, recurrence, and category. It is responsible for describing
  itself and answering small questions about itself (its priority score,
  whether it is due today).

- **Scheduler** — the engine that turns a list of tasks plus constraints into
  a plan. It is responsible for the core logic: sorting tasks by priority,
  filtering out tasks that don't fit the time budget, resolving time
  conflicts, and generating the final plan. I deliberately kept it separate
  from Pet/Task so the scheduling logic can be unit-tested in isolation.

- **DailyPlan** — the scheduler's output. It holds the scheduled tasks, the
  skipped tasks, total time used, and a reasoning string, so the app can both
  show the plan and explain why it made those choices.

Relationships: an Owner owns many Pets, a Pet has many Tasks, and the
Scheduler reads Tasks and produces a DailyPlan.


**b. Design changes**

Yes. After reviewing the skeleton with my AI assistant, I made three changes:

1. I added an `id` field to `Task`. The Pet class referenced tasks by
   `task_id` in edit/remove, but Task had no identifier, so there was nothing
   to look up. Adding an id makes the Pet–Task relationship actually usable.

2. I tied the Scheduler to the Owner's constraints instead of storing a
   separate time budget. Previously the Owner's `daily_time_budget` and the
   Scheduler's `time_budget` could disagree; now the scheduler is created from
   the owner's budget so there is a single source of truth.

3. I removed `Scheduler.explain()` and moved the reasoning into
   `DailyPlan.reasoning`, populated during `generate_plan()`. The original
   design implied the scheduler remembered its last plan, which added hidden
   state; letting the plan own its own explanation is simpler and keeps the
   scheduler stateless.


---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler considers three constraints: available time (the owner's daily
time budget), task priority (high/medium/low), and whether a task is due today
(completion status + recurrence). Priority matters most — tasks are sorted
high-to-low and placed greedily — because a busy owner most wants to guarantee
the important care happens (a walk, medication) even if lower-value tasks like
grooming get dropped when time runs short.

**b. Tradeoffs**

My conflict detection only flags tasks that share the exact same
`preferred_time` (an exact string match on "HH:MM"). It does not consider a
task's duration, so two tasks that overlap in real time — for example a
30-minute task at 08:00 and another at 08:15 — are not reported as
conflicting, even though they physically overlap.

This is a reasonable tradeoff for this scenario because the detection stays
lightweight and predictable: it never blocks or crashes the schedule, it just
returns a warning string the UI can show. A busy pet owner mainly needs a
quick heads-up that they double-booked a slot, not a full calendar-style
overlap solver. If the app grew, I would upgrade it to compare start time +
duration ranges for true overlap detection.

---

## 3. AI Collaboration

**a. How you used AI**

I used my AI coding assistant across every phase, but for different jobs.
Early on it was a brainstorming partner: helping me list the core objects and
turn them into a Mermaid UML diagram. During implementation, its agent/editing
mode was the most effective feature — it could scaffold the class skeletons
from the UML and later flesh out multiple methods across files at once
(for example, adding recurrence required coordinated changes to `Task` and
`Pet`). It was also useful for generating tests quickly and for explaining
Python details I was unsure about, like using a `lambda` key to sort "HH:MM"
strings and using `timedelta` to compute the next due date.

The most helpful prompts were specific and grounded in my actual code — e.g.
"based on my skeletons, how should the Scheduler retrieve all tasks from the
Owner's pets?" and "suggest a lightweight conflict-detection strategy that
returns a warning instead of crashing." Open-ended prompts gave generic
answers; prompts that referenced my files gave answers I could use directly.

Keeping separate chat sessions per phase helped me stay organized: the
design conversation didn't get tangled with the testing conversation, so each
session kept a clean, focused context and I could revisit a phase's reasoning
without scrolling past unrelated code.

**b. Judgment and verification**

The clearest example was `Scheduler.resolve_conflicts()`. The AI-suggested
version resolved same-time conflicts by *mutating* the lower-priority task and
clearing its `preferred_time`. When I ran the demo, this silently corrupted my
data — a later "sort by time" showed a task with no time, and conflict
detection then found nothing because the conflicting time had been erased. I
rejected that approach: `generate_plan()` didn't even use `preferred_time` for
placement, so the mutation was both harmful and pointless. I replaced it with a
non-destructive `detect_conflicts()` that only *reports* conflicts as warning
strings, and I verified the fix by re-running `main.py` and adding a unit test
that asserts a same-time conflict is flagged. I evaluated AI suggestions by
running the code, reading the actual output, and writing tests rather than
trusting that plausible-looking code was correct.

---

## 4. Testing and Verification

**a. What you tested**

I tested the core scheduling behaviors and their edge cases (13 tests total):
task completion flipping status, adding a task growing a pet's task count,
sort-by-time returning chronological order (with untimed tasks last), filtering
by completion status, cross-pet task aggregation, conflict detection flagging
duplicate times (and staying silent when there are none), the scheduler
skipping tasks that exceed the time budget, completed tasks being excluded from
today's plan, an empty pet/owner producing a safe empty plan, and recurrence
creating the correct follow-up (next day for daily, +7 days for weekly, nothing
for a one-off).

These were important because they are exactly the behaviors a pet owner relies
on: that the right tasks get scheduled in the right order, that nothing
silently overflows the day, and that recurring care doesn't get lost after
being completed once. Testing conflict detection and recurrence also protected
me from regressions after I refactored the conflict logic.

**b. Confidence**

I'm fairly confident (about 4 out of 5). Every core path is covered by a
passing test, including the edge cases most likely to break. I'm holding back
one point because conflict detection only catches exact time matches, not
overlapping durations, and recurrence assumes the plan is generated on the
task's due day. If I had more time I'd test overlapping-duration conflicts
(e.g. a 30-minute 08:00 task vs. an 08:15 task), weekly recurrence landing on a
specific weekday, invalid inputs (negative durations, malformed times), and
very large task lists to confirm the greedy scheduler still behaves.

---

## 5. Reflection

**a. What went well**

I'm most satisfied with how clean the separation of concerns turned out. Keeping
the `Scheduler` stateless and separate from `Owner`/`Pet`/`Task` made the logic
easy to test in isolation and easy to wire into both a CLI demo and a Streamlit
UI without changing the backend. The design-first workflow (UML → skeletons →
logic → tests → UI) meant that by the time I reached the UI, the hard thinking
was already done and the app "just worked."

**b. What you would improve**

If I had another iteration I'd give the scheduler a real notion of time: place
tasks at their actual `preferred_time` (honoring the clock) instead of packing
them sequentially from 08:00, and upgrade conflict detection to compare
start-time-plus-duration ranges for true overlap. I'd also add a proper date
model so weekly recurrence targets a specific weekday, and add edit/delete
controls and persistence (saving the owner's data between sessions) in the UI.

**c. Key takeaway**

The biggest thing I learned is what it means to be the "lead architect" when
working with a powerful AI. The AI is excellent at producing plausible code
fast, but plausible is not the same as correct — the `resolve_conflicts`
mutation looked reasonable and still corrupted my data. My job was to own the
design decisions, run and read the actual output, and write tests that hold the
AI's suggestions accountable. Used that way, AI made me much faster; used
uncritically, it would have quietly introduced bugs. Keeping focused,
file-specific prompts and separate chat sessions per phase was what let me stay
in that driver's seat.
