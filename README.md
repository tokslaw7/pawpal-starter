# PawPal+

PawPal+ is a pet care planning application with a Python scheduling engine and a Streamlit interface.
It helps a pet owner organize daily care tasks, account for timing constraints, detect schedule conflicts,
and review actionable plan output in a clean UI.

## Table of Contents

- [Overview](#overview)
- [Core Features](#core-features)
- [System Design](#system-design)
- [Installation](#installation)
- [Usage](#usage)
- [Demo (Final Streamlit App)](#demo-final-streamlit-app)
- [Testing](#testing)

## Overview

PawPal+ models a complete planning workflow:

1. Store owner, pet, task, and constraint data.
2. Expand recurring tasks into date-specific daily task instances.
3. Sort, filter, and validate daily plans.
4. Surface conflicts and status summaries in Streamlit.

## Core Features

### Scheduling Algorithms

- Date-based task instancing:
	`PetManagementSystem.generate_daily_plan` creates a day-specific plan by calling `PetCareTask.get_instance_for_date` for each task.
- Recurrence evaluation:
	`PetCareTask.occurs_on` supports `DAILY`, `WEEKLY`, and `MONTHLY` recurrence rules with optional end-date boundaries.
- Auto-rescheduling on completion:
	`PetCareTask.mark_complete` sets task status/time and creates the next daily occurrence when recurrence rules allow.
- Chronological ordering:
	`DailyPlan.sort_tasks_by_time` sorts by `assigned_time` and moves unassigned tasks to the end.
- Conflict detection:
	`DailyPlan.detect_conflicts` identifies overlapping timed tasks using sorted-forward comparison with early stopping.
- Constraint validation:
	`DailyPlan.validate_against_constraints` verifies both no time overlaps and no owner-constraint violations.

### Plan Review Utilities

- Filter by pet and status: `DailyPlan.filter_tasks`.
- Filter by status only: `DailyPlan.filter_by_status`.
- Human-readable schedule export: `DailyPlan.generate_schedule`.

### Streamlit Experience

- Quick input flow for owner, pet, and tasks.
- Professional schedule presentation using `st.success`, `st.warning`, `st.info`, and `st.table`.
- Separate table views for sorted schedule, pending tasks, completed tasks, and conflict pairs.

## System Design

- Backend domain model: `pawpal_system.py`
- Streamlit app: `app.py`
- Tests: `tests/test_pawpal.py`
- Updated UML doc: `pawpal2_design.md`

## Installation

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

Run the Streamlit app:

```bash
streamlit run app.py
```

## Demo (Final Streamlit App)

The final Streamlit demo is implemented in `app.py`.

Demo flow:

1. Enter owner and pet details.
2. Add one or more tasks with duration and priority.
3. Click **Generate schedule**.
4. Review output sections:
	 - Sorted schedule table
	 - Pending tasks table
	 - Completed tasks table
	 - Conflict warning + conflict details table (if overlaps exist)
	 - Constraint validation status

## Testing

Run all tests:

```bash
python -m pytest
```

Current automated tests validate:

- Task completion status and timestamp assignment.
- Pet task collection updates.
- Daily plan generation with sorting/filtering behavior.
- Recurring daily task auto-generation after completion.
- Conflict detection for overlapping tasks.
