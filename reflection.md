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

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
