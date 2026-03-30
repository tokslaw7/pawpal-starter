# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

My initial UML followed a domain-first approach where each core class represented a real planning concept.

Classes and responsibilities:

- `PetManagementSystem`: top-level coordinator that stores owners/plans and generates day-specific plans.
- `PetOwner`: owner profile and aggregate root for pets and owner constraints.
- `Pet`: pet profile with pet-specific task list.
- `PetCareTask`: unit of work (type, duration, priority, status, schedule metadata, recurrence).
- `Constraint`: owner-level scheduling rule with active/inactive state and allowed/blocked time-window behavior.
- `DailyPlan`: date-scoped plan that contains instantiated tasks plus operations for sorting, filtering, conflict detection, schedule generation, and validation.

I also used `TaskType` as an enum to keep task categories explicit and consistent across the system.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

Yes, the design evolved during implementation.

One important change was separating recurring task definitions from daily task instances. Instead of reusing the same `PetCareTask` object directly inside every day plan, `generate_daily_plan` now calls `get_instance_for_date` to clone date-specific instances. This kept source task definitions clean and made daily plan behavior deterministic and easier to test.

Another change was improving conflict logic from a simplistic check idea to true overlap detection using task start + duration with sorted-forward scanning and early break. This improved correctness while keeping runtime and code complexity reasonable.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

The scheduler currently considers:

- Time assignment and chronological ordering of tasks.
- Task duration when evaluating overlaps.
- Task priority (including urgency behavior such as high-priority/medical tasks).
- Recurrence rules (`DAILY`, `WEEKLY`, `MONTHLY`) with optional recurrence end dates.
- Owner constraints through allowed or blocked time windows.
- Task status filtering for execution review (`PENDING`, `COMPLETED`, etc.).

I prioritized constraints by impact on user trust and schedule correctness:

1. Prevent impossible schedules first (overlaps and hard constraint violations).
2. Preserve predictable recurrence behavior.
3. Support prioritization/optimization as a secondary ordering strategy.

This order reflects that a schedule must be valid before it is optimized.

**b. Tradeoffs**

- One tradeoff in this scheduler is using a simpler conflict rule that only checks exact task start-time matches instead of fully evaluating overlapping durations between tasks.
- This is reasonable for this project because it keeps the logic easy to understand and implement quickly, while still catching the most obvious collisions that a pet owner would want to fix first.

A key tradeoff was choosing a straightforward pairwise overlap check inside each daily plan instead of implementing a more advanced global optimization/scheduling solver.

Why this was reasonable:

- It is easy to explain, test, and maintain.
- It catches real timing conflicts accurately using duration-aware overlap checks.
- It supports the project scope and timeline without adding heavy algorithmic complexity.

What it does not do yet:

- It does not automatically reassign or rebalance tasks after conflicts are found.
- It does not optimize across multiple owners, resources, or long planning horizons.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

I used Copilot as a development copilot in three phases:

1. Design phase: brainstormed class boundaries, method responsibilities, and recurrence/constraint strategy.
2. Build phase: generated and refined method skeletons and docstrings, then iterated on edge-case handling.
3. Verification phase: generated and improved targeted tests (conflicts, recurrence expansion, completion behavior, filtering).

Most helpful prompt style:

- "Given this class model, suggest minimal methods to keep single responsibility."
- "Find edge cases in recurrence or conflict detection and propose test cases."
- "Refactor this method for readability without changing behavior."

The most effective Copilot features for this scheduler were chat-based architectural brainstorming, inline code completion for method scaffolding, and test-case generation support.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

I rejected a suggestion that risked over-coupling scheduling logic by blending recurring-definition state with per-day execution state in the same object flow.

To keep the design clean, I preserved a clear boundary:

- Source task definitions remain attached to pets.
- Daily plans receive date-specific task instances.

I verified this decision by running focused tests around daily plan generation, recurrence behavior, and conflict detection to ensure no regressions and predictable IDs/time mapping.

Using separate chat sessions helped organization significantly:

- Session 1 (architecture): class model and contracts only.
- Session 2 (implementation): method-level coding and refactors.
- Session 3 (testing): test coverage, assertions, and edge-case review.

This separation reduced context drift, prevented mixing strategy decisions with low-level debugging, and made each AI interaction easier to evaluate.

Lead architect summary:

I treated AI as a high-speed implementation partner, but I remained the lead architect by defining the system boundaries, accepting only suggestions that matched the design principles, and enforcing verification through tests before adopting changes.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

I tested the behaviors that most affect scheduler correctness:

- Task completion updates (`status` and `completed_time`).
- Pet task collection updates when tasks are added.
- Daily plan generation with sorting/filtering behavior.
- Recurring daily task auto-generation after completion.
- Overlap conflict detection for timed tasks.

These tests were important because they validate both domain correctness (task lifecycle) and planning correctness (time ordering/conflict handling), which are the core value of the system.

**b. Confidence**
- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

I am reasonably confident for the implemented scope because core workflows are covered by automated tests and the main scheduling paths were validated end-to-end.

If I had more time, I would add edge-case tests for:

- Boundary-time overlaps (exact end/start adjacency and same-minute tasks).
- Monthly recurrence on day 29/30/31.
- Tasks with missing assigned times and zero/negative durations.
- Multiple simultaneous constraints with mixed allow/blocked windows.
- Time zone and daylight-saving transitions.

---

## 5. Reflection

**a. What went well**
- What part of this project are you most satisfied with?

I am most satisfied with the clean domain model and how recurrence, conflict detection, and constraint validation are separated into understandable units. That made both debugging and testing much easier.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

In another iteration, I would add automatic conflict resolution (suggested alternative slots), stronger optimization rules, and richer user preferences so the scheduler can proactively rebalance tasks rather than only report issues.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

My key takeaway is that AI tools are most powerful when paired with deliberate architectural leadership: define boundaries first, use AI for acceleration inside those boundaries, and rely on tests as the final gate for correctness.
