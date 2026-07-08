"""PawPal+ logic layer.

Backend classes for the PawPal+ pet-care planner. The design follows the UML
in diagrams/uml.mmd:

    Owner  1 --> *  Pet  1 --> *  Task
    Scheduler reads Tasks (via the Owner) and produces a DailyPlan.

The Scheduler is kept separate from the data classes so the scheduling logic
can be unit-tested in isolation.
"""

from __future__ import annotations

from dataclasses import dataclass, field

# Numeric weight for each priority level (higher = more important).
PRIORITY_WEIGHTS = {"high": 3, "medium": 2, "low": 1}

# Default time of day (minutes since midnight) to start scheduling from.
DEFAULT_START_MINUTES = 8 * 60  # 08:00


def _format_time(minutes_since_midnight: int) -> str:
    """Turn minutes-since-midnight into an ``HH:MM`` string."""
    hours, minutes = divmod(minutes_since_midnight, 60)
    return f"{hours:02d}:{minutes:02d}"


@dataclass
class Task:
    """A single unit of pet care (walk, feeding, meds, grooming, etc.)."""

    name: str  # what the task is, e.g. "Morning walk"
    duration: int  # minutes the task takes
    priority: str  # "high" | "medium" | "low"
    id: int | None = None  # assigned by Pet.add_task when added
    completed: bool = False  # completion status
    preferred_time: str | None = None  # optional "HH:MM"
    recurrence: str | None = None  # frequency: "daily" | "weekly" | None
    category: str | None = None  # walk / feeding / meds / grooming / ...

    def priority_score(self) -> int:
        """Return a sortable numeric score for this task's priority."""
        return PRIORITY_WEIGHTS.get(self.priority.lower(), 0)

    def is_due_today(self) -> bool:
        """Return True if this task should be considered for today's plan.

        With no calendar/date model yet, a daily task (or one with no
        recurrence) is always due, and a weekly task is assumed due on the
        day the plan is generated. Completed tasks are not due again.
        """
        if self.completed:
            return False
        return self.recurrence in (None, "", "daily", "weekly")

    def mark_complete(self, done: bool = True) -> None:
        """Set the task's completion status."""
        self.completed = done

    def update(self, **fields) -> None:
        """Update one or more attributes of this task."""
        for key, value in fields.items():
            if not hasattr(self, key):
                raise AttributeError(f"Task has no attribute {key!r}")
            setattr(self, key, value)


@dataclass
class Pet:
    """The animal being cared for; owns its list of care tasks."""

    name: str
    species: str
    notes: str = ""
    tasks: list[Task] = field(default_factory=list)

    def _next_task_id(self) -> int:
        """Return the next free task id for this pet."""
        existing = [t.id for t in self.tasks if t.id is not None]
        return (max(existing) + 1) if existing else 1

    def add_task(self, task: Task) -> Task:
        """Attach a care task to this pet, assigning an id if needed."""
        if task.id is None:
            task.id = self._next_task_id()
        self.tasks.append(task)
        return task

    def _find_task(self, task_id: int) -> Task | None:
        """Return the task with the given id, or None if not found."""
        return next((t for t in self.tasks if t.id == task_id), None)

    def edit_task(self, task_id: int, **fields) -> None:
        """Modify an existing task by id."""
        task = self._find_task(task_id)
        if task is None:
            raise KeyError(f"No task with id {task_id}")
        task.update(**fields)

    def remove_task(self, task_id: int) -> None:
        """Remove a task from this pet by id."""
        if self._find_task(task_id) is None:
            raise KeyError(f"No task with id {task_id}")
        self.tasks = [t for t in self.tasks if t.id != task_id]

    def get_tasks(self) -> list[Task]:
        """Return all tasks for this pet."""
        return list(self.tasks)


@dataclass
class Owner:
    """The person using the app and the source of scheduling constraints."""

    name: str
    daily_time_budget: int = 0  # minutes available for pet care today
    preferences: dict = field(default_factory=dict)
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> Pet:
        """Register a new pet."""
        self.pets.append(pet)
        return pet

    def remove_pet(self, pet: Pet) -> None:
        """Remove a pet."""
        self.pets = [p for p in self.pets if p is not pet]

    def set_time_budget(self, minutes: int) -> None:
        """Update the available time budget."""
        self.daily_time_budget = minutes

    def get_pets(self) -> list[Pet]:
        """Return this owner's pets."""
        return list(self.pets)

    def get_all_tasks(self) -> list[Task]:
        """Aggregate every task across all of this owner's pets.

        This is how the Scheduler retrieves work to plan without needing to
        know about the Owner -> Pet -> Task structure itself.
        """
        return [task for pet in self.pets for task in pet.get_tasks()]


@dataclass
class DailyPlan:
    """The scheduler's output: what to do, what was skipped, and why."""

    scheduled_tasks: list = field(default_factory=list)  # (task, start_time) entries
    skipped_tasks: list = field(default_factory=list)  # (task, reason) entries
    total_time_used: int = 0
    reasoning: str = ""

    def add_scheduled(self, task: Task, start_time: str) -> None:
        """Place a task at a start time in the plan."""
        self.scheduled_tasks.append((task, start_time))
        self.total_time_used += task.duration

    def add_skipped(self, task: Task, reason: str) -> None:
        """Record a task that could not be scheduled, with a reason."""
        self.skipped_tasks.append((task, reason))

    def summary(self) -> str:
        """Return a formatted, human-readable summary of the plan."""
        lines: list[str] = []
        if self.scheduled_tasks:
            lines.append("Today's plan:")
            for task, start_time in self.scheduled_tasks:
                lines.append(
                    f"  {start_time} — {task.name} "
                    f"({task.duration} min) [priority: {task.priority}]"
                )
        else:
            lines.append("Today's plan: (nothing scheduled)")

        if self.skipped_tasks:
            lines.append("")
            lines.append("Skipped:")
            for task, reason in self.skipped_tasks:
                lines.append(f"  {task.name} — {reason}")

        lines.append("")
        lines.append(f"Total time used: {self.total_time_used} min")
        if self.reasoning:
            lines.append(f"Reasoning: {self.reasoning}")
        return "\n".join(lines)


class Scheduler:
    """The "brain": retrieves, organizes, and plans tasks across pets."""

    def __init__(self, time_budget: int, strategy: str = "priority") -> None:
        self.time_budget = time_budget
        self.strategy = strategy

    @classmethod
    def for_owner(cls, owner: Owner, strategy: str = "priority") -> "Scheduler":
        """Build a scheduler from an owner's daily time budget.

        Keeps the owner's budget as the single source of truth instead of
        letting the scheduler carry a separate, potentially stale value.
        """
        return cls(owner.daily_time_budget, strategy)

    def sort_tasks(self, tasks: list[Task]) -> list[Task]:
        """Order tasks by priority (desc), tie-breaking by shorter duration.

        Shorter high-value tasks come first so we fit as much important work
        as possible into a limited budget.
        """
        return sorted(
            tasks,
            key=lambda t: (-t.priority_score(), t.duration, t.name),
        )

    def filter_by_time(self, tasks: list[Task]) -> list[Task]:
        """Greedily keep tasks (already sorted) that fit the time budget."""
        kept: list[Task] = []
        remaining = self.time_budget
        for task in tasks:
            if task.duration <= remaining:
                kept.append(task)
                remaining -= task.duration
        return kept

    def resolve_conflicts(self, tasks: list[Task]) -> list[Task]:
        """Resolve tasks competing for the same preferred time slot.

        When two tasks request the same ``preferred_time``, the higher-
        priority one keeps the slot and the others fall back to automatic
        placement (their ``preferred_time`` is cleared).
        """
        claimed: dict[str, Task] = {}
        for task in tasks:
            slot = task.preferred_time
            if slot is None:
                continue
            holder = claimed.get(slot)
            if holder is None:
                claimed[slot] = task
            elif task.priority_score() > holder.priority_score():
                holder.preferred_time = None
                claimed[slot] = task
            else:
                task.preferred_time = None
        return tasks

    def generate_plan(self, tasks: list[Task]) -> DailyPlan:
        """Main entry point: produce a DailyPlan from a list of tasks.

        Steps: drop tasks that aren't due today, resolve time conflicts,
        sort by priority, then greedily schedule until the time budget runs
        out. Populates the plan's ``reasoning`` field so the plan owns its
        own explanation and the scheduler stays stateless.
        """
        plan = DailyPlan()

        # 1. Separate out tasks that shouldn't be planned today.
        due: list[Task] = []
        for task in tasks:
            if not task.is_due_today():
                reason = "already completed" if task.completed else "not due today"
                plan.add_skipped(task, reason)
            else:
                due.append(task)

        # 2. Resolve preferred-time conflicts, then order by priority.
        self.resolve_conflicts(due)
        ordered = self.sort_tasks(due)

        # 3. Greedily place tasks until the budget is exhausted.
        cursor = self._start_minutes()
        remaining = self.time_budget
        scheduled_count = 0
        for task in ordered:
            if task.duration <= remaining:
                plan.add_scheduled(task, _format_time(cursor))
                cursor += task.duration
                remaining -= task.duration
                scheduled_count += 1
            else:
                plan.add_skipped(task, "not enough time left in budget")

        # 4. Explain the outcome.
        plan.reasoning = (
            f"Scheduled {scheduled_count} of {len(due)} due task(s) "
            f"by priority within a {self.time_budget}-minute budget; "
            f"{self.time_budget - remaining} min used."
        )
        return plan

    def plan_for_owner(self, owner: Owner) -> DailyPlan:
        """Retrieve all of an owner's tasks and generate a daily plan."""
        return self.generate_plan(owner.get_all_tasks())

    def _start_minutes(self) -> int:
        """Where the day's schedule starts (minutes since midnight)."""
        return DEFAULT_START_MINUTES
