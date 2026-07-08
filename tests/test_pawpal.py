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


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

def test_pet_with_no_tasks_produces_empty_plan():
    """A pet (and owner) with no tasks yields an empty, non-crashing plan."""
    owner = Owner(name="Alex", daily_time_budget=60)
    owner.add_pet(Pet(name="Biscuit", species="dog"))

    plan = Scheduler.for_owner(owner).plan_for_owner(owner)

    assert plan.scheduled_tasks == []
    assert plan.skipped_tasks == []
    assert plan.total_time_used == 0


def test_scheduler_skips_tasks_that_exceed_budget():
    """Tasks that don't fit the time budget are skipped, not scheduled."""
    scheduler = Scheduler(time_budget=30)
    tasks = [
        Task(name="Short walk", duration=20, priority="high"),
        Task(name="Long groom", duration=40, priority="high"),  # too big
    ]

    plan = scheduler.generate_plan(tasks)

    scheduled_names = [t.name for t, _ in plan.scheduled_tasks]
    skipped_names = [t.name for t, _ in plan.skipped_tasks]
    assert scheduled_names == ["Short walk"]
    assert "Long groom" in skipped_names


def test_detect_conflicts_empty_when_no_overlap():
    """detect_conflicts() returns no warnings when all times differ."""
    scheduler = Scheduler(time_budget=120)
    tasks = [
        Task(name="A", duration=10, priority="low", preferred_time="08:00"),
        Task(name="B", duration=10, priority="low", preferred_time="09:00"),
    ]

    assert scheduler.detect_conflicts(tasks) == []


def test_completed_task_is_not_due_today():
    """A completed task is excluded from today's plan."""
    task = Task(name="Walk", duration=20, priority="high", recurrence="daily")
    assert task.is_due_today() is True

    task.mark_complete()

    assert task.is_due_today() is False


def test_completing_weekly_task_queues_next_week():
    """Completing a weekly task queues a follow-up seven days later."""
    pet = Pet(name="Miso", species="cat")
    groom = pet.add_task(
        Task(name="Groom", duration=15, priority="low",
             recurrence="weekly", due_date=date.today())
    )

    follow_up = pet.mark_task_complete(groom.id)

    assert follow_up is not None
    assert follow_up.due_date == date.today() + timedelta(days=7)


def test_completing_one_off_task_queues_nothing():
    """Completing a non-recurring task does not create a follow-up."""
    pet = Pet(name="Biscuit", species="dog")
    vet = pet.add_task(Task(name="Vet visit", duration=60, priority="high"))

    follow_up = pet.mark_task_complete(vet.id)

    assert follow_up is None
    assert len(pet.get_tasks()) == 1
