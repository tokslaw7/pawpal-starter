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

    # create tasks
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
        description="Morning walk",
        duration=30,
        priority=7,
        status="PENDING",
        assigned_time=datetime.combine(date.today(), time(hour=8, minute=30)),
    )

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

    pet1.add_task(task1)
    pet1.add_task(task2)
    pet2.add_task(task3)

    # add tasks to schedule generating structures
    daily_plan = system.generate_daily_plan(owner, date.today())

    # print today's schedule
    print("Today's Schedule:")
    print(daily_plan.generate_schedule())

    # validate constraints
    valid = daily_plan.validate_against_constraints()
    print(f"Constraints valid: {valid}")


if __name__ == "__main__":
    main()
