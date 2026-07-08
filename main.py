"""PawPal+ demo script.

A temporary "testing ground" that wires the logic layer together and prints
a daily schedule to the terminal, plus demos for the smarter-scheduling
features (sort-by-time, filtering, conflict detection, recurring tasks).

Run it with:

    python main.py
"""

from pawpal_system import Owner, Pet, Scheduler, Task


def build_demo_owner() -> Owner:
    """Create a sample owner with two pets and several care tasks.

    Tasks are deliberately added out of chronological order so the
    sort-by-time demo has something to reorder. Two tasks share 09:00 to
    exercise conflict detection.
    """
    owner = Owner(name="Alex", daily_time_budget=90)

    biscuit = Pet(name="Biscuit", species="Golden Retriever")
    miso = Pet(name="Miso", species="Cat")
    owner.add_pet(biscuit)
    owner.add_pet(miso)

    # Added out of order on purpose (17:00 before 08:00).
    biscuit.add_task(
        Task(name="Grooming", duration=40, priority="low",
             preferred_time="17:00", category="grooming")
    )
    biscuit.add_task(
        Task(name="Morning walk", duration=30, priority="high",
             preferred_time="08:00", recurrence="daily", category="walk")
    )
    biscuit.add_task(
        Task(name="Breakfast", duration=10, priority="high",
             preferred_time="09:00", category="feeding")
    )

    # Miso's feeding also wants 09:00 -> conflict with Biscuit's breakfast.
    miso.add_task(
        Task(name="Feed Miso", duration=10, priority="medium",
             preferred_time="09:00", category="feeding")
    )
    miso.add_task(
        Task(name="Play/enrichment", duration=20, priority="medium",
             preferred_time="18:00", category="enrichment")
    )

    return owner


def demo_schedule(owner: Owner, scheduler: Scheduler) -> None:
    """Print the generated daily schedule."""
    print("=" * 44)
    print(f"PawPal+ — Today's Schedule for {owner.name}")
    print(f"Pets: {', '.join(p.name for p in owner.get_pets())}")
    print(f"Time budget: {owner.daily_time_budget} min")
    print("=" * 44)
    print(scheduler.plan_for_owner(owner).summary())


def demo_sorting_and_filtering(owner: Owner, scheduler: Scheduler) -> None:
    """Show sort-by-time and the status / pet filters."""
    all_tasks = owner.get_all_tasks()

    print("\n" + "-" * 44)
    print("Tasks sorted by time:")
    for t in scheduler.sort_by_time(all_tasks):
        print(f"  {t.preferred_time or '--:--'} — {t.name}")

    pending = scheduler.filter_by_status(all_tasks, completed=False)
    print(f"\nPending (not completed) tasks: {len(pending)}")

    biscuit_tasks = owner.get_tasks_for_pet("Biscuit")
    print("Biscuit's tasks only:", ", ".join(t.name for t in biscuit_tasks))


def demo_conflicts(owner: Owner, scheduler: Scheduler) -> None:
    """Show lightweight conflict detection."""
    print("\n" + "-" * 44)
    warnings = scheduler.detect_conflicts(owner.get_all_tasks())
    if warnings:
        print("Schedule conflicts detected:")
        for w in warnings:
            print(f"  ⚠️  {w}")
    else:
        print("No conflicts detected.")


def demo_recurring(owner: Owner) -> None:
    """Show that completing a daily task queues the next occurrence."""
    print("\n" + "-" * 44)
    biscuit = owner.get_pets()[0]
    walk = next(t for t in biscuit.get_tasks() if t.name == "Morning walk")
    before = len(biscuit.get_tasks())
    follow_up = biscuit.mark_task_complete(walk.id)
    after = len(biscuit.get_tasks())
    print(f"Completed '{walk.name}' (daily). Tasks: {before} -> {after}")
    if follow_up is not None:
        print(f"  Next occurrence queued for: {follow_up.due_date}")


def main() -> None:
    owner = build_demo_owner()
    scheduler = Scheduler.for_owner(owner)

    demo_schedule(owner, scheduler)
    demo_sorting_and_filtering(owner, scheduler)
    demo_conflicts(owner, scheduler)
    demo_recurring(owner)


if __name__ == "__main__":
    main()
