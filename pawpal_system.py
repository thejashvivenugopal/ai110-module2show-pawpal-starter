"""PawPal+ logic layer.

Backend classes for the PawPal+ pet-care planner, generated as a skeleton
from the UML in diagrams/uml.mmd. Method bodies are intentionally left as
stubs (no scheduling logic yet) — they will be implemented incrementally.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Task:
    """A single unit of pet care (walk, feeding, meds, grooming, etc.)."""

    name: str
    duration: int  # minutes
    priority: str  # "high" | "medium" | "low"
    preferred_time: str | None = None
    recurrence: str | None = None  # "daily" | "weekly" | None
    category: str | None = None

    def priority_score(self) -> int:
        """Return a sortable numeric score for this task's priority."""
        raise NotImplementedError

    def is_due_today(self) -> bool:
        """Return True if this task should run today given its recurrence."""
        raise NotImplementedError

    def update(self, **fields) -> None:
        """Update one or more attributes of this task."""
        raise NotImplementedError


@dataclass
class Pet:
    """The animal being cared for; owns its list of care tasks."""

    name: str
    species: str
    notes: str = ""
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Attach a care task to this pet."""
        raise NotImplementedError

    def edit_task(self, task_id: int, **fields) -> None:
        """Modify an existing task."""
        raise NotImplementedError

    def remove_task(self, task_id: int) -> None:
        """Remove a task from this pet."""
        raise NotImplementedError

    def get_tasks(self) -> list[Task]:
        """Return all tasks for this pet."""
        raise NotImplementedError


@dataclass
class Owner:
    """The person using the app and the source of scheduling constraints."""

    name: str
    daily_time_budget: int = 0  # minutes available for pet care today
    preferences: dict = field(default_factory=dict)
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Register a new pet."""
        raise NotImplementedError

    def remove_pet(self, pet: Pet) -> None:
        """Remove a pet."""
        raise NotImplementedError

    def set_time_budget(self, minutes: int) -> None:
        """Update the available time budget."""
        raise NotImplementedError

    def get_pets(self) -> list[Pet]:
        """Return this owner's pets."""
        raise NotImplementedError


@dataclass
class DailyPlan:
    """The scheduler's output: what to do, what was skipped, and why."""

    scheduled_tasks: list = field(default_factory=list)  # (task, start_time) entries
    skipped_tasks: list = field(default_factory=list)  # (task, reason) entries
    total_time_used: int = 0
    reasoning: str = ""

    def add_scheduled(self, task: Task, start_time: str) -> None:
        """Place a task at a start time in the plan."""
        raise NotImplementedError

    def add_skipped(self, task: Task, reason: str) -> None:
        """Record a task that could not be scheduled, with a reason."""
        raise NotImplementedError

    def summary(self) -> str:
        """Return a formatted, human-readable summary of the plan."""
        raise NotImplementedError


class Scheduler:
    """The engine that turns tasks + constraints into a DailyPlan."""

    def __init__(self, time_budget: int, strategy: str = "priority") -> None:
        self.time_budget = time_budget
        self.strategy = strategy

    def sort_tasks(self, tasks: list[Task]) -> list[Task]:
        """Order tasks by priority (with sensible tie-breaks)."""
        raise NotImplementedError

    def filter_by_time(self, tasks: list[Task]) -> list[Task]:
        """Drop tasks that do not fit within the time budget."""
        raise NotImplementedError

    def resolve_conflicts(self, tasks: list[Task]) -> list[Task]:
        """Handle tasks competing for the same preferred time slot."""
        raise NotImplementedError

    def generate_plan(self, tasks: list[Task]) -> DailyPlan:
        """Main entry point: produce a DailyPlan from a list of tasks."""
        raise NotImplementedError

    def explain(self) -> str:
        """Produce the reasoning text for the most recent plan."""
        raise NotImplementedError
