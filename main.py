"""PawPal+ demo script.

A temporary "testing ground" that wires the logic layer together and prints
a daily schedule to the terminal. Run it with:

    python main.py
"""

from pawpal_system import Owner, Pet, Scheduler, Task


def build_demo_owner() -> Owner:
    """Create a sample owner with two pets and several care tasks."""
    owner = Owner(name="Alex", daily_time_budget=90)

    biscuit = Pet(name="Biscuit", species="Golden Retriever")
    miso = Pet(name="Miso", species="Cat")
    owner.add_pet(biscuit)
    owner.add_pet(miso)

    # Dog tasks — note the different preferred times and priorities.
    biscuit.add_task(
        Task(name="Morning walk", duration=30, priority="high",
             preferred_time="08:00", recurrence="daily", category="walk")
    )
    biscuit.add_task(
        Task(name="Breakfast", duration=10, priority="high",
             preferred_time="08:30", category="feeding")
    )
    biscuit.add_task(
        Task(name="Grooming", duration=40, priority="low",
             preferred_time="17:00", category="grooming")
    )

    # Cat tasks.
    miso.add_task(
        Task(name="Feed Miso", duration=10, priority="medium",
             preferred_time="09:00", category="feeding")
    )
    miso.add_task(
        Task(name="Play/enrichment", duration=20, priority="medium",
             preferred_time="18:00", category="enrichment")
    )

    return owner


def main() -> None:
    owner = build_demo_owner()

    print("=" * 44)
    print(f"PawPal+ — Today's Schedule for {owner.name}")
    print(f"Pets: {', '.join(p.name for p in owner.get_pets())}")
    print(f"Time budget: {owner.daily_time_budget} min")
    print("=" * 44)

    scheduler = Scheduler.for_owner(owner)
    plan = scheduler.plan_for_owner(owner)

    print(plan.summary())


if __name__ == "__main__":
    main()
