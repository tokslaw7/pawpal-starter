from __future__ import annotations

from datetime import date, datetime, time, timedelta
from enum import Enum
from typing import List, Optional


TimeSlot = tuple[time, time]


class TaskType(Enum):
	FEEDING = "FEEDING"
	WALKING = "WALKING"
	GROOMING = "GROOMING"
	MEDICAL = "MEDICAL"
	PLAY = "PLAY"
	CLEANING = "CLEANING"
	TRAINING = "TRAINING"


class PetManagementSystem:
	def __init__(self, system_id: str) -> None:
		"""Initialize the pet management system with a unique ID."""
		self.system_id: str = system_id
		self.owners: List[PetOwner] = []
		self.daily_plans: List[DailyPlan] = []

	def add_pet_owner(self, owner: PetOwner) -> None:
		"""Add a pet owner if they aren't already in the system."""
		if self.get_pet_owner(owner.owner_id) is None:
			self.owners.append(owner)

	def add_pet(self, owner: PetOwner, pet: Pet) -> None:
		"""Add a pet to an owner, creating the owner record if needed."""
		if owner not in self.owners:
			self.add_pet_owner(owner)
		owner.add_pet(pet)

	def add_constraint(self, owner: PetOwner, constraint: Constraint) -> None:
		"""Add a scheduling constraint to an owner."""
		if owner not in self.owners:
			self.add_pet_owner(owner)
		owner.add_constraint(constraint)

	def generate_daily_plan(self, owner: PetOwner, plan_date: date) -> DailyPlan:
		"""Generate a daily plan for an owner by collecting all pet tasks and constraints."""
		plan = DailyPlan(plan_id=f"plan-{owner.owner_id}-{plan_date.isoformat()}", plan_date=plan_date, owner=owner, created_at=datetime.now())
		plan.constraints = list(owner.constraints)
		for pet in owner.pets:
			for task in pet.tasks:
				instance = task.get_instance_for_date(plan_date)
				if instance is not None:
					plan.add_task(instance)
		self.daily_plans.append(plan)
		return plan

	def get_pet_owner(self, owner_id: str) -> Optional[PetOwner]:
		"""Retrieve an owner by owner_id."""
		return next((o for o in self.owners if o.owner_id == owner_id), None)

	def get_daily_plan(self, plan_id: str) -> Optional[DailyPlan]:
		"""Retrieve a daily plan by plan_id."""
		return next((p for p in self.daily_plans if p.plan_id == plan_id), None)


class PetOwner:
	def __init__(self, owner_id: str, name: str, email: str, phone: str) -> None:
		"""Initialize a pet owner profile with contact details, pets, and constraints."""
		self.owner_id: str = owner_id
		self.name: str = name
		self.email: str = email
		self.phone: str = phone
		self.pets: List[Pet] = []
		self.constraints: List[Constraint] = []

	def add_pet(self, pet: Pet) -> None:
		"""Add a pet to this owner's list."""
		if pet not in self.pets:
			self.pets.append(pet)

	def remove_pet(self, pet_id: str) -> None:
		"""Remove a pet from the owner's list by pet_id."""
		self.pets = [pet for pet in self.pets if pet.pet_id != pet_id]

	def add_constraint(self, constraint: Constraint) -> None:
		"""Add a scheduling constraint for the owner."""
		if constraint not in self.constraints:
			self.constraints.append(constraint)

	def get_pets(self) -> List[Pet]:
		"""Return all pets owned by this owner."""
		return self.pets

	def get_constraints(self) -> List[Constraint]:
		"""Return all constraints associated with this owner."""
		return self.constraints


class Pet:
	def __init__(
		self,
		pet_id: str,
		name: str,
		species: str,
		breed: str,
		age: int,
		weight: float,
		special_needs: str,
		owner: PetOwner,
	) -> None:
		"""Initialize a pet profile and bind it to an owner."""
		self.pet_id: str = pet_id
		self.name: str = name
		self.species: str = species
		self.breed: str = breed
		self.age: int = age
		self.weight: float = weight
		self.special_needs: str = special_needs
		self.owner: PetOwner = owner
		self.tasks: List[PetCareTask] = []

	def get_name(self) -> str:
		"""Return the pet's name."""
		return self.name

	def get_species(self) -> str:
		"""Return the pet's species."""
		return self.species

	def get_special_needs(self) -> str:
		"""Return the pet's special needs description."""
		return self.special_needs

	def add_task(self, task: PetCareTask) -> None:
		"""Add a care task to this pet."""
		self.tasks.append(task)

	def remove_task(self, task_id: str) -> None:
		"""Remove a task from this pet by task ID."""
		self.tasks = [task for task in self.tasks if task.task_id != task_id]


class PetCareTask:
	def __init__(
		self,
		task_id: str,
		task_type: TaskType,
		pet: Pet,
		description: str,
		duration: int,
		priority: int,
		status: str,
		assigned_time: Optional[datetime] = None,
		completed_time: Optional[datetime] = None,
		recurrence: Optional[str] = None,
		recurrence_end_date: Optional[date] = None,
	) -> None:
		self.task_id: str = task_id
		self.task_type: TaskType = task_type
		self.pet: Pet = pet
		self.description: str = description
		self.duration: int = duration
		self.priority: int = priority
		self.status: str = status
		self.assigned_time: Optional[datetime] = assigned_time
		self.completed_time: Optional[datetime] = completed_time
		self.recurrence: Optional[str] = recurrence
		self.recurrence_end_date: Optional[date] = recurrence_end_date

	def mark_complete(self) -> None:
		"""Mark this task as completed and record completion time."""
		self.status = "COMPLETED"
		self.completed_time = datetime.now()

	def update_status(self, status: str) -> None:
		"""Update the status of this task."""
		self.status = status

	def get_priority(self) -> int:
		"""Return this task's priority ranking."""
		return self.priority

	def is_urgent(self) -> bool:
		"""Determine whether this task is urgent with priority or medical type."""
		return self.priority >= 8 or self.task_type == TaskType.MEDICAL

	def get_end_time(self) -> Optional[datetime]:
		"""Return the expected end datetime for this task (assigned_time + duration)."""
		if self.assigned_time is None:
			return None
		return self.assigned_time + timedelta(minutes=self.duration)

	def occurs_on(self, target_date: date) -> bool:
		"""Return whether this task instance should occur on a given date."""
		if self.assigned_time is None:
			return False
		start_date = self.assigned_time.date()
		if target_date < start_date:
			return False
		if self.recurrence_end_date and target_date > self.recurrence_end_date:
			return False
		if self.recurrence is None:
			return target_date == start_date
		if self.recurrence.upper() == "DAILY":
			return True
		if self.recurrence.upper() == "WEEKLY":
			return (target_date - start_date).days % 7 == 0
		if self.recurrence.upper() == "MONTHLY":
			return start_date.day == target_date.day
		return False

	def get_instance_for_date(self, target_date: date) -> Optional["PetCareTask"]:
		"""Return a cloned task instance for the requested date if it occurs."""
		if not self.occurs_on(target_date):
			return None
		new_time = datetime.combine(target_date, self.assigned_time.time()) if self.assigned_time else None
		return PetCareTask(
			task_id=f"{self.task_id}-{target_date.isoformat()}",
			task_type=self.task_type,
			pet=self.pet,
			description=self.description,
			duration=self.duration,
			priority=self.priority,
			status=self.status,
			assigned_time=new_time,
			completed_time=self.completed_time,
			recurrence=self.recurrence,
			recurrence_end_date=self.recurrence_end_date,
		)


class Constraint:
	def __init__(
		self,
		constraint_id: str,
		description: str,
		constraint_type: str,
		start_time: time,
		end_time: time,
		owner: PetOwner,
		is_active: bool,
		allow_window: bool = True,
	) -> None:
		self.constraint_id: str = constraint_id
		self.description: str = description
		self.constraint_type: str = constraint_type
		self.start_time: time = start_time
		self.end_time: time = end_time
		self.owner: PetOwner = owner
		self.is_active: bool = is_active
		self.allow_window: bool = allow_window

	def is_violated(self, task: PetCareTask) -> bool:
		"""Evaluate whether a task violates this constraint."""
		if not self.is_active or task.assigned_time is None:
			return False

		in_window = self.start_time <= task.assigned_time.time() <= self.end_time
		if self.allow_window:
			# Allowed window: violation if task is outside
			return not in_window
		else:
			# Protected (blocked) window: violation if task is inside
			return in_window

	def get_available_time_slots(self) -> List[TimeSlot]:
		"""Get available time slots for this constraint, if it defines an allow window."""
		if not self.is_active:
			return []
		if self.allow_window:
			return [(self.start_time, self.end_time)]
		# blocked windows are not available slots
		return []


class DailyPlan:
	def __init__(
		self,
		plan_id: str,
		plan_date: date,
		owner: PetOwner,
		created_at: datetime,
	) -> None:
		"""Initialize a daily plan for an owner with tasks and constraints."""
		self.plan_id: str = plan_id
		self.date: date = plan_date
		self.owner: PetOwner = owner
		self.tasks: List[PetCareTask] = []
		self.constraints: List[Constraint] = []
		self.created_at: datetime = created_at

	def add_task(self, task: PetCareTask) -> None:
		"""Add a task to the daily plan if not already present."""
		if task not in self.tasks:
			self.tasks.append(task)

	def remove_task(self, task_id: str) -> None:
		"""Remove a task from the daily plan by task ID."""
		self.tasks = [task for task in self.tasks if task.task_id != task_id]

	def optimize_plan(self) -> None:
		"""Optimize task order based on task priority and duration."""
		self.tasks.sort(key=lambda t: (-t.priority, t.task_type.name, t.duration))

	def sort_tasks_by_time(self) -> None:
		"""Sort tasks by assigned datetime to produce time-ordered schedule."""
		self.tasks.sort(key=lambda t: (t.assigned_time or datetime.max))

	def filter_tasks(self, pet_id: Optional[str] = None, status: Optional[str] = None) -> List[PetCareTask]:
		"""Filter tasks by pet and/or status."""
		return [
			t for t in self.tasks
			if (pet_id is None or t.pet.pet_id == pet_id)
			and (status is None or t.status.upper() == status.upper())
		]

	def detect_conflicts(self) -> List[tuple[PetCareTask, PetCareTask]]:
		"""Detect overlapping task time conflicts. Returns a list of conflicting pairs."""
		conflicts: List[tuple[PetCareTask, PetCareTask]] = []
		tasks_with_time = [t for t in self.tasks if t.assigned_time is not None and t.duration > 0]
		tasks_with_time.sort(key=lambda t: t.assigned_time)
		for i in range(len(tasks_with_time)):
			current = tasks_with_time[i]
			current_end = current.get_end_time()
			for next_task in tasks_with_time[i + 1 :]:
				if next_task.assigned_time >= current_end:
					break
				conflicts.append((current, next_task))
		return conflicts

	def validate_conflicts(self) -> bool:
		"""Return False if any time conflicts are detected."""
		return len(self.detect_conflicts()) == 0

	def generate_schedule(self) -> str:
		"""Generate a human-readable schedule string for today."""
		self.sort_tasks_by_time()
		lines = []
		for t in self.tasks:
			when = t.assigned_time.isoformat() if t.assigned_time else "unassigned"
			lines.append(f"{when} - {t.task_type.name}: {t.description} ({t.pet.name}) [{t.status}]")
		return "\n".join(lines)

	def validate_against_constraints(self) -> bool:
		"""Validate tasks against all constraints and return True if none are violated."""
		if not self.validate_conflicts():
			return False
		for task in self.tasks:
			if any(constraint.is_violated(task) for constraint in self.constraints):
				return False
		return True
