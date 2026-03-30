import streamlit as st
from datetime import date, datetime

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

from pawpal_system import (
    PetManagementSystem,
    PetOwner,
    Pet,
    PetCareTask,
    TaskType,
)

st.divider()

st.subheader("Quick Demo Inputs (UI only)")
owner_name = st.text_input("Owner name", value="Jordan")
pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])

st.markdown("### Tasks")
st.caption("Add a few tasks. In your final version, these should feed into your scheduler.")

if "tasks" not in st.session_state:
    st.session_state.tasks = []

col1, col2, col3 = st.columns(3)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

if st.button("Add task"):
    st.session_state.tasks.append(
        {"title": task_title, "duration_minutes": int(duration), "priority": priority}
    )

if st.session_state.tasks:
    st.write("Current tasks:")
    st.table(st.session_state.tasks)
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")
st.caption("This button should call your scheduling logic once you implement it.")


def to_task_row(task: PetCareTask) -> dict[str, str | int]:
    assigned = task.assigned_time.strftime("%H:%M") if task.assigned_time else "Unassigned"
    return {
        "Time": assigned,
        "Task": task.description,
        "Type": task.task_type.name,
        "Pet": task.pet.name,
        "Duration (min)": task.duration,
        "Priority": task.priority,
        "Status": task.status,
    }

if st.button("Generate schedule"):
    if not st.session_state.tasks:
        st.warning("Add at least one task before generating a schedule.")
        st.stop()

    system = PetManagementSystem(system_id="sys-1")
    owner = PetOwner(owner_id="owner-1", name=owner_name, email="noreply@example.com", phone="000-000-0000")
    system.add_pet_owner(owner)

    pet = Pet(
        pet_id="pet-1",
        name=pet_name,
        species=species,
        breed="Unknown",
        age=1,
        weight=5.0,
        special_needs="None",
        owner=owner,
    )
    owner.add_pet(pet)

    for idx, task_data in enumerate(st.session_state.tasks, start=1):
        title_lower = task_data["title"].lower()
        task_type = TaskType.FEEDING if "feed" in title_lower else TaskType.WALKING
        task = PetCareTask(
            task_id=f"task-{idx}",
            task_type=task_type,
            pet=pet,
            description=task_data["title"],
            duration=task_data["duration_minutes"],
            priority=9 if task_data["priority"] == "high" else 5,
            status="PENDING",
            assigned_time=datetime.now(),
        )
        pet.add_task(task)

    plan = system.generate_daily_plan(owner, date.today())

    # Use the system's chronological sorting method for schedule display.
    plan.sort_tasks_by_time()
    sorted_tasks = plan.tasks
    pending_tasks = plan.filter_by_status("PENDING")
    completed_tasks = plan.filter_by_status("COMPLETED")
    conflicts = plan.detect_conflicts()

    st.success("Schedule generated and sorted by time.")
    st.write("Sorted schedule")
    st.table([to_task_row(task) for task in sorted_tasks])

    st.write("Pending tasks")
    st.table([to_task_row(task) for task in pending_tasks])

    st.write("Completed tasks")
    if completed_tasks:
        st.table([to_task_row(task) for task in completed_tasks])
    else:
        st.info("No completed tasks yet.")

    if conflicts:
        st.warning(f"Detected {len(conflicts)} scheduling conflict(s).")
        conflict_rows = []
        for first, second in conflicts:
            first_time = first.assigned_time.strftime("%H:%M") if first.assigned_time else "Unassigned"
            second_time = second.assigned_time.strftime("%H:%M") if second.assigned_time else "Unassigned"
            conflict_rows.append(
                {
                    "Task A": f"{first_time} - {first.description}",
                    "Task B": f"{second_time} - {second.description}",
                }
            )
        st.table(conflict_rows)
    else:
        st.info("No scheduling conflicts detected.")

    if plan.validate_against_constraints():
        st.info("Constraints check passed")
    else:
        st.warning("Some tasks violate constraints")
