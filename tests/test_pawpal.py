from datetime import datetime, date, time, timedelta
import sys
from pathlib import Path

# Ensure local package path is available when running tests.
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pawpal_system import Pet, PetCareTask, PetOwner, PetManagementSystem, TaskType


def test_task_completion_marks_status_completed() -> None:
    owner = PetOwner(owner_id="owner-1", name="Alex", email="alex@example.com", phone="123-456-7890")
    pet = Pet(
        pet_id="pet-1",
        name="Milo",
        species="Dog",
        breed="Beagle",
        age=3,
        weight=20.0,
        special_needs="None",
        owner=owner,
    )

    task = PetCareTask(
        task_id="task-1",
        task_type=TaskType.FEEDING,
        pet=pet,
        description="Morning feeding",
        duration=15,
        priority=5,
        status="PENDING",
        assigned_time=datetime.combine(date.today(), time(hour=8, minute=0)),
    )

    task.mark_complete()

    assert task.status == "COMPLETED"
    assert task.completed_time is not None


def test_pet_add_task_increases_task_count() -> None:
    owner = PetOwner(owner_id="owner-1", name="Alex", email="alex@example.com", phone="123-456-7890")
    pet = Pet(
        pet_id="pet-2",
        name="Whiskers",
        species="Cat",
        breed="Siamese",
        age=4,
        weight=8.0,
        special_needs="Allergy-sensitive food",
        owner=owner,
    )

    initial_task_count = len(pet.tasks)

    task = PetCareTask(
        task_id="task-2",
        task_type=TaskType.MEDICAL,
        pet=pet,
        description="Daily meds",
        duration=10,
        priority=8,
        status="PENDING",
        assigned_time=datetime.combine(date.today(), time(hour=8, minute=30)),
    )

    pet.add_task(task)

    assert len(pet.tasks) == initial_task_count + 1
    assert pet.tasks[0] == task


def test_sort_tasks_by_time_and_filter_conflicts_and_recurring() -> None:
    owner = PetOwner(owner_id="owner-1", name="Alex", email="alex@example.com", phone="123-456-7890")
    pet = Pet(
        pet_id="pet-3",
        name="Buddy",
        species="Dog",
        breed="Labrador",
        age=5,
        weight=25.0,
        special_needs="None",
        owner=owner,
    )
    owner.add_pet(pet)

    task1 = PetCareTask(
        task_id="task-3",
        task_type=TaskType.WALKING,
        pet=pet,
        description="Morning walk",
        duration=30,
        priority=6,
        status="PENDING",
        assigned_time=datetime.combine(date.today(), time(hour=7, minute=0)),
    )

    task2 = PetCareTask(
        task_id="task-4",
        task_type=TaskType.FEEDING,
        pet=pet,
        description="Breakfast",
        duration=20,
        priority=8,
        status="PENDING",
        assigned_time=datetime.combine(date.today(), time(hour=7, minute=15)),
    )

    task3 = PetCareTask(
        task_id="task-5",
        task_type=TaskType.MEDICAL,
        pet=pet,
        description="Daily meds",
        duration=10,
        priority=9,
        status="PENDING",
        assigned_time=datetime.combine(date.today(), time(hour=7, minute=10)),
        recurrence="DAILY",
        recurrence_end_date=date.today(),
    )

    pet.add_task(task1)
    pet.add_task(task2)
    pet.add_task(task3)

    system = PetManagementSystem(system_id="sys-1")
    system.add_pet_owner(owner)
    plan = system.generate_daily_plan(owner, date.today())

    # Tasks should be created and sorted by time in schedule output
    schedule_lines = plan.generate_schedule().splitlines()
    assert "07:00" in schedule_lines[0]

    # Recurring task included
    assert any("Daily meds" in line for line in schedule_lines)

    # Conflicts: task1 and task2 overlap at 7:15
    conflicts = plan.detect_conflicts()
    assert len(conflicts) >= 1

    # Filter by pet/status
    dog_tasks = plan.filter_tasks(pet_id="pet-3", status="PENDING")
    assert len(dog_tasks) == 3

    # Filter by explicit status helper
    completed = plan.filter_by_status("COMPLETED")
    assert len(completed) == 0

    # Mark task inside plan as completed
    first_plan_task = plan.tasks[0]
    first_plan_task.mark_complete()
    assert len(plan.filter_by_status("COMPLETED")) == 1


def test_daily_task_completion_creates_next_occurrence() -> None:
    owner = PetOwner(owner_id="owner-4", name="Casey", email="casey@example.com", phone="987-654-3210")
    pet = Pet(
        pet_id="pet-4",
        name="Luna",
        species="Cat",
        breed="Maine Coon",
        age=2,
        weight=10.0,
        special_needs="Indoor only",
        owner=owner,
    )
    owner.add_pet(pet)

    base_task = PetCareTask(
        task_id="task-6",
        task_type=TaskType.MEDICAL,
        pet=pet,
        description="Daily vitamins",
        duration=10,
        priority=6,
        status="PENDING",
        assigned_time=datetime.combine(date.today(), time(hour=20, minute=0)),
        recurrence="DAILY",
        recurrence_end_date=date.today() + timedelta(days=2),
    )

    pet.add_task(base_task)
    new_task = base_task.mark_complete()

    assert base_task.status == "COMPLETED"
    assert new_task is not None
    assert new_task.task_id == f"task-6-{(date.today()+timedelta(days=1)).isoformat()}"
    assert new_task.assigned_time.date() == date.today() + timedelta(days=1)
    assert any(t.task_id == new_task.task_id for t in pet.tasks)


def test_detect_task_conflicts() -> None:
    owner = PetOwner(owner_id="owner-5", name="Jordan", email="jordan@example.com", phone="111-222-3333")
    pet = Pet(
        pet_id="pet-5",
        name="Nova",
        species="Dog",
        breed="Mixed",
        age=4,
        weight=22.0,
        special_needs="None",
        owner=owner,
    )
    owner.add_pet(pet)

    # 09:00-09:30 overlaps with 09:15-09:25; 10:00 task does not overlap.
    t1 = PetCareTask(
        task_id="task-7",
        task_type=TaskType.WALKING,
        pet=pet,
        description="Morning walk",
        duration=30,
        priority=5,
        status="PENDING",
        assigned_time=datetime.combine(date.today(), time(hour=9, minute=0)),
    )
    t2 = PetCareTask(
        task_id="task-8",
        task_type=TaskType.FEEDING,
        pet=pet,
        description="Breakfast",
        duration=10,
        priority=6,
        status="PENDING",
        assigned_time=datetime.combine(date.today(), time(hour=9, minute=15)),
    )
    t3 = PetCareTask(
        task_id="task-9",
        task_type=TaskType.GROOMING,
        pet=pet,
        description="Brushing",
        duration=15,
        priority=3,
        status="PENDING",
        assigned_time=datetime.combine(date.today(), time(hour=10, minute=0)),
    )

    pet.add_task(t1)
    pet.add_task(t2)
    pet.add_task(t3)

    system = PetManagementSystem(system_id="sys-2")
    system.add_pet_owner(owner)
    plan = system.generate_daily_plan(owner, date.today())

    conflicts = plan.detect_conflicts()
    assert len(conflicts) == 1

    a, b = conflicts[0]
    assert {a.task_id, b.task_id} == {"task-7-" + date.today().isoformat(), "task-8-" + date.today().isoformat()}


