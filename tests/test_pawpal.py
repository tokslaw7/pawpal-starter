from datetime import datetime, date, time
import sys
from pathlib import Path

# Ensure local package path is available when running tests.
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pawpal_system import Pet, PetCareTask, PetOwner, TaskType


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
