# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Smarter Scheduling

Recent scheduling improvements include:

- Time-based sorting so daily plans are shown in chronological order.
- Task filtering by pet and completion status (for example, pending vs completed).
- Recurring task support (daily, weekly, monthly) with daily auto-rescheduling on completion.
- Conflict detection for overlapping task durations, with clear warnings when tasks collide.
- Constraint-aware validation that checks both owner constraints and schedule conflicts.

## Testing Pawpal+

Run the automated tests with:

python -m pytest

Current tests focus on core scheduling reliability, including:

- Marking tasks complete and recording completion timestamps.
- Adding tasks to pets and confirming task list updates.
- Generating/sorting daily plans, filtering by pet/status, and including recurring tasks.
- Auto-creating the next daily recurring task after completion.
- Detecting overlaps between scheduled tasks to surface conflicts.

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.
