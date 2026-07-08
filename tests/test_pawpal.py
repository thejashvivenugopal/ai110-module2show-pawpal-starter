"""Quick behavior tests for the PawPal+ logic layer."""

from datetime import date, timedelta

from pawpal_system import Owner, Pet, Scheduler, Task


def test_mark_complete_changes_status():
    """Calling mark_complete() flips a task's completion status to True."""
    task = Task(name="Evening walk", duration=20, priority="high")
    assert task.completed is False

    task.mark_complete()

    assert task.completed is True


def test_adding_task_increases_pet_task_count():
    """Adding a task to a Pet increases that pet's task count by one."""
    pet = Pet(name="Biscuit", species="Golden Retriever")
    assert len(pet.get_tasks()) == 0

    pet.add_task(Task(name="Feeding", duration=10, priority="high"))

    assert len(pet.get_tasks()) == 1


def test_sort_by_time_orders_chronologically():
    """sort_by_time() orders tasks by preferred_time, undated ones last."""
    scheduler = Scheduler(time_budget=120)
    tasks = [
        Task(name="Evening", duration=10, priority="low", preferred_time="18:00"),
        Task(name="Morning", duration=10, priority="low", preferred_time="08:00"),
        Task(name="Anytime", duration=10, priority="low"),  # no preferred_time
        Task(name="Noon", duration=10, priority="low", preferred_time="12:00"),
    ]

    ordered = [t.name for t in scheduler.sort_by_time(tasks)]

    assert ordered == ["Morning", "Noon", "Evening", "Anytime"]


def test_filter_by_status_returns_only_matching_tasks():
    """filter_by_status() returns tasks matching the requested completion flag."""
    scheduler = Scheduler(time_budget=120)
    done = Task(name="Done", duration=10, priority="low", completed=True)
    pending = Task(name="Pending", duration=10, priority="low")

    result = scheduler.filter_by_status([done, pending], completed=False)

    assert result == [pending]


def test_detect_conflicts_flags_same_time_tasks():
    """detect_conflicts() warns when two tasks share a preferred time."""
    scheduler = Scheduler(time_budget=120)
    tasks = [
        Task(name="Walk", duration=30, priority="high", preferred_time="09:00"),
        Task(name="Feed", duration=10, priority="medium", preferred_time="09:00"),
        Task(name="Nap", duration=10, priority="low", preferred_time="14:00"),
    ]

    warnings = scheduler.detect_conflicts(tasks)

    assert len(warnings) == 1
    assert "09:00" in warnings[0]


def test_completing_daily_task_queues_next_occurrence():
    """Completing a daily task adds a follow-up due one day later."""
    pet = Pet(name="Biscuit", species="dog")
    walk = pet.add_task(
        Task(name="Walk", duration=30, priority="high",
             recurrence="daily", due_date=date.today())
    )

    follow_up = pet.mark_task_complete(walk.id)

    assert walk.completed is True
    assert follow_up is not None
    assert follow_up.completed is False
    assert follow_up.due_date == date.today() + timedelta(days=1)
    assert len(pet.get_tasks()) == 2


def test_owner_get_all_tasks_aggregates_across_pets():
    """Owner.get_all_tasks() collects tasks from every pet."""
    owner = Owner(name="Alex")
    dog = Pet(name="Biscuit", species="dog")
    cat = Pet(name="Miso", species="cat")
    owner.add_pet(dog)
    owner.add_pet(cat)
    dog.add_task(Task(name="Walk", duration=30, priority="high"))
    cat.add_task(Task(name="Feed", duration=10, priority="medium"))

    assert len(owner.get_all_tasks()) == 2
    assert len(owner.get_tasks_for_pet("Biscuit")) == 1
