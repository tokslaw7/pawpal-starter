# app.py
from pawpal_system import PetManagementSystem, PetOwner, Pet, PetCareTask, Constraint, TaskType

class AppMemory:
    def __init__(self):
        self.data = {
            "owners": {},
            "pets": {},
            "tasks": {},
            "daily_plans": {},
        }

    def add_owner(self, owner):
        self.data["owners"][owner.owner_id] = owner

    def add_pet(self, pet):
        self.data["pets"][pet.pet_id] = pet

    def add_task(self, task):
        self.data["tasks"][task.task_id] = task

    def set_daily_plan(self, plan):
        self.data["daily_plans"][plan.plan_id] = plan

    def get_snapshot(self):
        return self.data.copy()

def main():
    mem = AppMemory()
    system = PetManagementSystem(system_id="sys-1")

    owner = PetOwner("owner-1", "Alex", "alex@example.com", "123-456-7890")
    system.add_pet_owner(owner)
    mem.add_owner(owner)

    # ... create pets/tasks/... then record:
    pet = Pet("pet-1", "Milo", "Dog", "Beagle", 3, 20.0, "None", owner)
    owner.add_pet(pet)
    mem.add_pet(pet)

    task = PetCareTask("task-1", TaskType.FEEDING, pet, "Morning feeding", 15, 5, "PENDING", datetime.combine(date.today(), time(hour=8)))
    pet.add_task(task)
    mem.add_task(task)

    plan = system.generate_daily_plan(owner, date.today())
    mem.set_daily_plan(plan)

    print("Memory snapshot:", mem.get_snapshot())
    # ...