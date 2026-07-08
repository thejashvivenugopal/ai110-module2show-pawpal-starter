import streamlit as st

# Step 1: bring the backend classes into the UI layer.
from pawpal_system import Owner, Pet, Scheduler, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")
st.caption("Plan your pets' daily care tasks by priority and available time.")

# ---------------------------------------------------------------------------
# Step 2: application "memory".
# Streamlit reruns this whole script on every interaction, so we keep a single
# Owner instance in st.session_state instead of recreating (and emptying) it
# on each rerun. The `not in` check ensures we only build it once per session.
# ---------------------------------------------------------------------------
if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="Jordan", daily_time_budget=120)

owner = st.session_state.owner

# ---------------------------------------------------------------------------
# Owner settings
# ---------------------------------------------------------------------------
st.subheader("👤 Owner")
owner.name = st.text_input("Owner name", value=owner.name)
owner.set_time_budget(
    st.number_input(
        "Daily time budget (minutes)",
        min_value=0,
        max_value=1440,
        value=owner.daily_time_budget,
        step=10,
    )
)

st.divider()

# ---------------------------------------------------------------------------
# Step 3a: Add a pet -> Owner.add_pet(Pet(...))
# ---------------------------------------------------------------------------
st.subheader("🐕 Pets")

with st.form("add_pet_form", clear_on_submit=True):
    pet_name = st.text_input("Pet name", value="Mochi")
    species = st.selectbox("Species", ["dog", "cat", "other"])
    notes = st.text_input("Notes (optional)", value="")
    add_pet_clicked = st.form_submit_button("Add pet")

    if add_pet_clicked:
        if pet_name.strip():
            owner.add_pet(Pet(name=pet_name.strip(), species=species, notes=notes))
            st.success(f"Added {pet_name.strip()} to {owner.name}'s pets.")
        else:
            st.error("Please enter a pet name.")

pets = owner.get_pets()
if pets:
    st.write("**Current pets:** " + ", ".join(f"{p.name} ({p.species})" for p in pets))
else:
    st.info("No pets yet. Add one above.")

st.divider()

# ---------------------------------------------------------------------------
# Step 3b: Add a task to a pet -> Pet.add_task(Task(...))
# ---------------------------------------------------------------------------
st.subheader("✅ Tasks")

if not pets:
    st.info("Add a pet before adding tasks.")
else:
    # Select by index so pets with the same name aren't ambiguous.
    pet_index = st.selectbox(
        "Add task to which pet?",
        range(len(pets)),
        format_func=lambda i: f"{pets[i].name} ({pets[i].species})",
    )
    selected_pet = pets[pet_index]

    with st.form("add_task_form", clear_on_submit=True):
        title = st.text_input("Task title", value="Morning walk")
        col1, col2 = st.columns(2)
        with col1:
            duration = st.number_input(
                "Duration (minutes)", min_value=1, max_value=240, value=20
            )
        with col2:
            priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

        col3, col4 = st.columns(2)
        with col3:
            preferred_time = st.text_input("Preferred time (optional, HH:MM)", value="")
        with col4:
            recurrence = st.selectbox("Frequency", ["none", "daily", "weekly"])

        add_task_clicked = st.form_submit_button("Add task")

        if add_task_clicked:
            if title.strip():
                selected_pet.add_task(
                    Task(
                        name=title.strip(),
                        duration=int(duration),
                        priority=priority,
                        preferred_time=preferred_time.strip() or None,
                        recurrence=None if recurrence == "none" else recurrence,
                    )
                )
                st.success(f"Added '{title.strip()}' to {selected_pet.name}.")
            else:
                st.error("Please enter a task title.")

    # Show the selected pet's current tasks.
    tasks = selected_pet.get_tasks()
    if tasks:
        st.write(f"**{selected_pet.name}'s tasks:**")
        st.table(
            [
                {
                    "Task": t.name,
                    "Duration (min)": t.duration,
                    "Priority": t.priority,
                    "Preferred": t.preferred_time or "—",
                    "Frequency": t.recurrence or "one-off",
                    "Done": "✅" if t.completed else "",
                }
                for t in tasks
            ]
        )
    else:
        st.caption("No tasks yet for this pet.")

st.divider()

# ---------------------------------------------------------------------------
# Step 3c: Generate the schedule -> Scheduler.plan_for_owner(owner)
# ---------------------------------------------------------------------------
st.subheader("📅 Today's Schedule")

if st.button("Generate schedule", type="primary"):
    if not owner.get_all_tasks():
        st.warning("Add at least one task before generating a schedule.")
    else:
        scheduler = Scheduler.for_owner(owner)
        plan = scheduler.plan_for_owner(owner)

        if plan.scheduled_tasks:
            st.table(
                [
                    {
                        "Time": start_time,
                        "Task": task.name,
                        "Duration (min)": task.duration,
                        "Priority": task.priority,
                    }
                    for task, start_time in plan.scheduled_tasks
                ]
            )
        else:
            st.info("Nothing could be scheduled within the time budget.")

        if plan.skipped_tasks:
            st.write("**Skipped:**")
            for task, reason in plan.skipped_tasks:
                st.write(f"- {task.name} — {reason}")

        st.caption(f"Total time used: {plan.total_time_used} min")
        if plan.reasoning:
            st.info(f"Why this plan: {plan.reasoning}")
