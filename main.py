from datetime import datetime, time, date

from pawpal_system import (
    PetManagementSystem,
    PetOwner,
    Pet,
    PetCareTask,
    Constraint,
    TaskType,
)


def main() -> None:
    # create system
    system = PetManagementSystem(system_id="sys-1")

    # create owner
    owner = PetOwner(owner_id="owner-1", name="Alex", email="alex@example.com", phone="123-456-7890")
    system.add_pet_owner(owner)

    # create pets
    pet1 = Pet(
        pet_id="pet-1",
        name="Milo",
        species="Dog",
        breed="Beagle",
        age=3,
        weight=20.0,
        special_needs="None",
        owner=owner,
    )

    pet2 = Pet(
        pet_id="pet-2",
        name="Whiskers",
        species="Cat",
        breed="Siamese",
        age=4,
        weight=8.0,
        special_needs="Allergy-sensitive food",
        owner=owner,
    )

    owner.add_pet(pet1)
    owner.add_pet(pet2)

    # create constraints
    owner_constraint = Constraint(
        constraint_id="c-1",
        description="Work hours, no task in this block",
        constraint_type="time-block",
        start_time=time(hour=9, minute=0),
        end_time=time(hour=17, minute=0),
        owner=owner,
        is_active=True,
    )
    owner.add_constraint(owner_constraint)

    # create tasks (intentionally out of chronological order to verify sort)
    task3 = PetCareTask(
        task_id="task-3",
        task_type=TaskType.MEDICAL,
        pet=pet2,
        description="Medicine dose",
        duration=10,
        priority=9,
        status="PENDING",
        assigned_time=datetime.combine(date.today(), time(hour=18, minute=0)),
    )

    task1 = PetCareTask(
        task_id="task-1",
        task_type=TaskType.FEEDING,
        pet=pet1,
        description="Morning feeding",
        duration=15,
        priority=5,
        status="PENDING",
        assigned_time=datetime.combine(date.today(), time(hour=8, minute=0)),
    )

    task2 = PetCareTask(
        task_id="task-2",
        task_type=TaskType.WALKING,
        pet=pet1,
        description="Morning walk (same start as feeding to test conflicts)",
        duration=30,
        priority=7,
        status="PENDING",
        assigned_time=datetime.combine(date.today(), time(hour=8, minute=0)),
    )

    task4 = PetCareTask(
        task_id="task-4",
        task_type=TaskType.GROOMING,
        pet=pet1,
        description="Evening brushing",
        duration=20,
        priority=4,
        status="PENDING",
        assigned_time=datetime.combine(date.today(), time(hour=19, minute=0)),
    )

    pet2.add_task(task3)
    pet1.add_task(task1)
    pet1.add_task(task2)
    pet1.add_task(task4)

    # add tasks to schedule generating structures
    daily_plan = system.generate_daily_plan(owner, date.today())

    # print today's schedule (sorted by assigned time via generate_schedule)
    print("Today's Schedule (sorted):")
    print(daily_plan.generate_schedule())

    # validate constraints and conflicts
    valid = daily_plan.validate_against_constraints()
    print(f"Constraints and conflict check passed: {valid}")

    # show filtered views
    print("\nPending tasks for Milo:")
    for t in daily_plan.filter_tasks(pet_id="pet-1", status="PENDING"):
        print(f"  - {t.assigned_time.time()} {t.task_type.name} ({t.description})")

    print("\nMarking first task completed and filtering completed tasks:")
    if daily_plan.tasks:
        daily_plan.tasks[0].mark_complete()
    for t in daily_plan.filter_by_status("COMPLETED"):
        print(f"  - {t.assigned_time.time()} {t.task_type.name} ({t.description})")

    conflicts = daily_plan.detect_conflicts()
    print(f"\nDetected conflicts: {len(conflicts)}")
    if conflicts:
        print("WARNING: schedule has overlapping tasks that need rescheduling.")
    for a, b in conflicts:
        print(f"  - {a.task_id} overlaps with {b.task_id}")



if __name__ == "__main__":
    main()
