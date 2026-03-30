# PawPal+ Updated UML (Code-Aligned)

This design reflects the final implementation in pawpal_system.py, including recurrence support, conflict detection, sorting, and filtering methods.

## UML Diagram Image

![PawPal+ UML Summary](docs/pawpal2_uml_summary.svg)

![UML FINAL](uml_final.png)


## Mermaid Source (Editable)

```mermaid
classDiagram
    class TaskType {
        <<enum>>
        FEEDING
        WALKING
        GROOMING
        MEDICAL
        PLAY
        CLEANING
        TRAINING
    }

    class PetManagementSystem {
        -system_id: str
        -owners: List~PetOwner~
        -daily_plans: List~DailyPlan~
        +add_pet_owner(owner: PetOwner): None
        +add_pet(owner: PetOwner, pet: Pet): None
        +add_constraint(owner: PetOwner, constraint: Constraint): None
        +generate_daily_plan(owner: PetOwner, plan_date: date): DailyPlan
        +get_pet_owner(owner_id: str): Optional~PetOwner~
        +get_daily_plan(plan_id: str): Optional~DailyPlan~
    }

    class PetOwner {
        -owner_id: str
        -name: str
        -email: str
        -phone: str
        -pets: List~Pet~
        -constraints: List~Constraint~
        +add_pet(pet: Pet): None
        +remove_pet(pet_id: str): None
        +add_constraint(constraint: Constraint): None
        +get_pets(): List~Pet~
        +get_constraints(): List~Constraint~
    }

    class Pet {
        -pet_id: str
        -name: str
        -species: str
        -breed: str
        -age: int
        -weight: float
        -special_needs: str
        -owner: PetOwner
        -tasks: List~PetCareTask~
        +get_name(): str
        +get_species(): str
        +get_special_needs(): str
        +add_task(task: PetCareTask): None
        +remove_task(task_id: str): None
    }

    class PetCareTask {
        -task_id: str
        -task_type: TaskType
        -pet: Pet
        -description: str
        -duration: int
        -priority: int
        -status: str
        -assigned_time: Optional~datetime~
        -completed_time: Optional~datetime~
        -recurrence: Optional~str~
        -recurrence_end_date: Optional~date~
        +mark_complete(): Optional~PetCareTask~
        +update_status(status: str): None
        +get_priority(): int
        +is_urgent(): bool
        +get_end_time(): Optional~datetime~
        +occurs_on(target_date: date): bool
        +get_instance_for_date(target_date: date): Optional~PetCareTask~
    }

    class Constraint {
        -constraint_id: str
        -description: str
        -constraint_type: str
        -start_time: time
        -end_time: time
        -owner: PetOwner
        -is_active: bool
        -allow_window: bool
        +is_violated(task: PetCareTask): bool
        +get_available_time_slots(): List~TimeSlot~
    }

    class DailyPlan {
        -plan_id: str
        -date: date
        -owner: PetOwner
        -tasks: List~PetCareTask~
        -constraints: List~Constraint~
        -created_at: datetime
        +add_task(task: PetCareTask): None
        +remove_task(task_id: str): None
        +optimize_plan(): None
        +sort_tasks_by_time(): None
        +filter_tasks(pet_id: Optional~str~, status: Optional~str~): List~PetCareTask~
        +filter_by_status(status: str): List~PetCareTask~
        +detect_conflicts(): List~Tuple~PetCareTask, PetCareTask~~
        +validate_conflicts(): bool
        +generate_schedule(): str
        +validate_against_constraints(): bool
    }

    PetManagementSystem "1" --> "*" PetOwner
    PetManagementSystem "1" --> "*" DailyPlan
    PetOwner "1" --> "*" Pet
    PetOwner "1" --> "*" Constraint
    Pet "1" --> "*" PetCareTask
    PetCareTask "1" --> "1" TaskType
    DailyPlan "1" --> "*" PetCareTask
    DailyPlan "1" --> "*" Constraint
    DailyPlan "1" --> "1" PetOwner
```
