import streamlit as st
from datetime import date, datetime, time

from pawpal_system import (
    PetManagementSystem,
    PetOwner,
    Pet,
    PetCareTask,
    TaskType,
)

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="wide")

st.title("🐾 PawPal+")
st.caption("Pet care scheduling — detect conflicts, validate constraints, plan your day.")

# ── Session state defaults ────────────────────────────────────────────────────
if "tasks" not in st.session_state:
    st.session_state.tasks = []

TASK_TYPE_OPTIONS = [t.name for t in TaskType]
PRIORITY_MAP = {"Low (1)": 1, "Medium (5)": 5, "High (8)": 8, "Urgent (10)": 10}


def load_demo():
    st.session_state.owner_name = "Jordan"
    st.session_state.pet_name = "Milo"
    st.session_state.species = "dog"
    st.session_state.tasks = [
        {"title": "Morning walk",     "type": "WALKING",  "time": "07:00", "duration": 30, "priority": 8},
        {"title": "Breakfast feeding","type": "FEEDING",  "time": "08:00", "duration": 15, "priority": 9},
        {"title": "Play fetch",       "type": "PLAY",     "time": "07:20", "duration": 20, "priority": 5},
        {"title": "Evening groom",    "type": "GROOMING", "time": "18:00", "duration": 25, "priority": 3},
        {"title": "Vet checkup",      "type": "MEDICAL",  "time": "10:00", "duration": 45, "priority": 10},
    ]


# ── Sidebar: owner & pet setup ────────────────────────────────────────────────
with st.sidebar:
    st.header("Owner & Pet")

    if st.button("Load demo data", use_container_width=True):
        load_demo()

    owner_name = st.text_input("Owner name", value=st.session_state.get("owner_name", "Jordan"), key="owner_name")
    pet_name   = st.text_input("Pet name",   value=st.session_state.get("pet_name",   "Mochi"),  key="pet_name")
    species    = st.selectbox("Species", ["dog", "cat", "rabbit", "bird", "other"],
                              index=["dog","cat","rabbit","bird","other"].index(
                                  st.session_state.get("species", "dog")), key="species")

    st.divider()
    st.header("Add Task")

    task_title    = st.text_input("Title", value="Morning walk")
    task_type_sel = st.selectbox("Type", TASK_TYPE_OPTIONS)
    task_time     = st.time_input("Start time", value=time(8, 0))
    task_duration = st.number_input("Duration (min)", min_value=1, max_value=480, value=20)
    task_priority = st.select_slider("Priority", options=list(PRIORITY_MAP.keys()), value="High (8)")

    if st.button("Add task", use_container_width=True, type="primary"):
        st.session_state.tasks.append({
            "title":    task_title,
            "type":     task_type_sel,
            "time":     task_time.strftime("%H:%M"),
            "duration": int(task_duration),
            "priority": PRIORITY_MAP[task_priority],
        })
        st.rerun()

    if st.session_state.tasks:
        if st.button("Clear all tasks", use_container_width=True):
            st.session_state.tasks = []
            st.rerun()

# ── Main area ─────────────────────────────────────────────────────────────────
col_left, col_right = st.columns([1, 2])

with col_left:
    st.subheader("Scheduled tasks")
    if not st.session_state.tasks:
        st.info("No tasks yet. Add one in the sidebar or load demo data.")
    else:
        for i, t in enumerate(st.session_state.tasks):
            with st.container(border=True):
                badge_col, info_col, del_col = st.columns([1, 3, 1])
                with badge_col:
                    st.markdown(f"**{t['time']}**")
                with info_col:
                    st.markdown(f"**{t['title']}** · {t['type'].capitalize()} · {t['duration']} min · Priority {t['priority']}")
                with del_col:
                    if st.button("✕", key=f"del_{i}"):
                        st.session_state.tasks.pop(i)
                        st.rerun()

with col_right:
    st.subheader("Schedule output")

    if st.button("Generate schedule", type="primary", use_container_width=True):
        if not st.session_state.tasks:
            st.warning("Add at least one task before generating a schedule.")
            st.stop()

        # ── Build system objects ──────────────────────────────────────────────
        system = PetManagementSystem(system_id="sys-1")
        owner  = PetOwner(owner_id="owner-1", name=owner_name,
                          email="noreply@example.com", phone="000-000-0000")
        system.add_pet_owner(owner)

        pet = Pet(pet_id="pet-1", name=pet_name, species=species,
                  breed="Unknown", age=3, weight=5.0,
                  special_needs="None", owner=owner)
        owner.add_pet(pet)

        today = date.today()
        for idx, td in enumerate(st.session_state.tasks, start=1):
            h, m = map(int, td["time"].split(":"))
            assigned_dt = datetime.combine(today, time(h, m))
            task = PetCareTask(
                task_id=f"task-{idx}",
                task_type=TaskType[td["type"]],
                pet=pet,
                description=td["title"],
                duration=td["duration"],
                priority=td["priority"],
                status="PENDING",
                assigned_time=assigned_dt,
            )
            pet.add_task(task)

        plan = system.generate_daily_plan(owner, today)
        plan.sort_tasks_by_time()

        # ── Helper ────────────────────────────────────────────────────────────
        def task_row(task: PetCareTask) -> dict:
            assigned = task.assigned_time.strftime("%H:%M") if task.assigned_time else "—"
            end      = task.get_end_time()
            end_str  = end.strftime("%H:%M") if end else "—"
            return {
                "Start":    assigned,
                "End":      end_str,
                "Task":     task.description,
                "Type":     task.task_type.name,
                "Duration": f"{task.duration} min",
                "Priority": task.priority,
                "Status":   task.status,
            }

        # ── Full schedule ─────────────────────────────────────────────────────
        st.markdown(f"**{today.strftime('%A, %B %d %Y')} — {pet_name}'s day**")
        st.table([task_row(t) for t in plan.tasks])

        # ── Conflicts ─────────────────────────────────────────────────────────
        conflicts = plan.detect_conflicts()
        if conflicts:
            st.warning(f"⚠️ {len(conflicts)} scheduling conflict(s) detected")
            rows = []
            for a, b in conflicts:
                a_time = a.assigned_time.strftime("%H:%M") if a.assigned_time else "—"
                b_time = b.assigned_time.strftime("%H:%M") if b.assigned_time else "—"
                rows.append({
                    "Task A": f"{a_time}  {a.description}",
                    "Task B": f"{b_time}  {b.description}",
                    "Overlap": f"{a.description} runs until {a.get_end_time().strftime('%H:%M') if a.get_end_time() else '?'}, {b.description} starts at {b_time}",
                })
            st.table(rows)
        else:
            st.success("No scheduling conflicts detected.")

        # ── Constraints ───────────────────────────────────────────────────────
        if plan.validate_against_constraints():
            st.success("All constraints satisfied.")
        else:
            st.warning("Some tasks violate owner constraints.")

        # ── Stats ─────────────────────────────────────────────────────────────
        pending   = plan.filter_by_status("PENDING")
        completed = plan.filter_by_status("COMPLETED")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total tasks",  len(plan.tasks))
        m2.metric("Pending",      len(pending))
        m3.metric("Completed",    len(completed))
        m4.metric("Conflicts",    len(conflicts))
