# AIBDD

> Most AI coding workflows fail in the same place: the agent starts writing code before the system has a real spec.

AIBDD is built to fix that.

AIBDD turns raw product intent into boundary-aware discovery, executable acceptance criteria, path-based test plans, implementation tasks, and disciplined `RED -> GREEN -> REFACTOR` execution. Instead of asking an agent to guess from a paragraph and good intentions, it gives the agent a chain of explicit artifacts, each with one job, one owner, and one way to prove it is correct.

This is not vibe coding with better prompts.

This is acceptance-driven software delivery with specs as truth.

This repository is the workflow SSOT for that system. It contains the AIBDD skill family that moves a project from kickoff to discovery, planning, test-plan synthesis, task generation, implementation, evaluation, and reconciliation.

## Why AIBDD Hits Hard

Most teams already know AI can write code. That is not the hard part anymore.

The hard part is getting the right code, in the right boundary, with the right acceptance target, without silently dropping requirements or smearing one change across the whole system. That is where AIBDD is strong.

It gives you:

- **Specs as truth**: artifacts are not passive documentation. They are versioned, executable, and downstream-visible.
- **Specs as guard**: implementation is judged against acceptance artifacts, not against "looks done to me."
- **Separation of concerns**: activity, feature rules, technical plan, DSL, test plan, and tasks each own a precise slice of truth.
- **Traceability end to end**: intent can be followed into flow, flow into acceptance, acceptance into tasks, and tasks into execution.
- **Human control without chaos**: the workflow is human-in-the-loop, but not human-do-everything.
- **Less guessing, more asking**: when information is missing, the system is designed to clarify instead of hallucinate.
- **Reconcile instead of rot**: when upstream requirements change, AIBDD can cascade the correction from the earliest affected planner.
- **Rewind instead of panic**: you can safely roll the pipeline back to a known phase boundary instead of manually undoing downstream damage.

If ordinary AI coding feels magical right up until it becomes expensive, flaky, and hard to trust, AIBDD is the counter-move.

## Who This Is For

- **Founders and product builders** who want AI to build from acceptance truth, not from ambiguous feature blur.
- **Tech leads and architects** who need boundary-aware planning, auditable handoffs, and fewer accidental cross-layer leaks.
- **PMs, BAs, and spec owners** who want a workflow where business intent survives contact with implementation.
- **Teams already using AI coding agents** but tired of reruns, shallow fixes, and "green" outputs that were never truly grounded.

## Quick Start

1. Run `/aibdd-kickoff` (Pick the tech-stack, full-loaded with aibdd configuration)
2. Run `/aibdd-discovery` (Address what you wanna build)
3. Run `/aibdd-plan` (No arguments needed)
4. Run `/aibdd-tasks`  (No arguments needed)
5. Run `/aibdd-implement`  (No arguments needed)
6. Run `/aibdd-red-execute`, then `/aibdd-green-execute`, then `/aibdd-refactor-execute`
7. When reality changes, use `/aibdd-reconcile`

Stop there. You will know very quickly whether you want agents guessing, or agents executing against acceptance truth.

## See It Work

```text
You:    We need refund handling for cancelled orders, with inventory return,
        approval rules, and audit visibility.

You:    /aibdd-discovery
AIBDD:  [sources the raw idea against boundary truth]
        [asks only the missing questions]
        [writes activity artifacts and feature-rule skeletons]

You:    /aibdd-plan
AIBDD:  [locks technical boundary truth]
        [maps implementation structure and DSL truth]
        [records impacted feature scope]

You:    /aibdd-tasks
AIBDD:  [renders execution-ready tasks from accepted planning truth]

You:    /aibdd-implement
AIBDD:  [turns every checkbox into live tracked execution]

You:    /aibdd-red-execute
AIBDD:  [creates legal red from runtime-visible steps]

You:    /aibdd-green-execute
AIBDD:  [edits product code until acceptance passes]

You:    /aibdd-refactor-execute
AIBDD:  [improves structure without losing green]

You:    The requirement changed.
You:    /aibdd-reconcile
AIBDD:  [cascades from the earliest affected planner instead of patching chaos]
```

That is not a clever prompt chain.

That is a spec pipeline.

## The Pipeline

AIBDD is a process, not a bag of commands. The skills run in the order software should be made:

**Clarify -> Discover -> Plan -> Derive Acceptance -> Execute -> Evaluate -> Reconcile**

Each stage feeds the next. Discovery writes the artifacts plan consumes. Plan records the feature scope that tasks consume. Activity paths become test-plan scenarios. Tasks become live execution. Execution is evaluated through red, green, and refactor gates. When something changes upstream, reconcile and rewind exist so you do not have to fake consistency by hand.

| Skill | Your specialist | What it does |
|---|---|---|
| `/aibdd-kickoff` | **Project initializer** | Binds the project context, stack-aware config, boundary skeleton, and core AIBDD paths so the rest of the pipeline has a real starting point. |
| `/clarify-loop` | **Clarification router** | Collects missing information in a controlled, file-first way instead of letting agents improvise around ambiguity. |
| `/aibdd-discovery` | **Root planner** | Turns raw ideas into boundary-aware discovery truth, sourcing reports, activity intent, and feature-rule skeletons. |
| `/aibdd-form-activity` | **Flow formulator** | Writes `.activity` DSL from discovery output and validates the syntax so flow truth is explicit and machine-usable. |
| `/aibdd-plan` | **Technical planner** | Converts accepted discovery truth into technical boundary truth, implementation planning, and red-usable DSL mappings without creating shadow truth. |
| `/aibdd-tasks` | **Task graph builder** | Generates structured `tasks.md` from the accepted plan package, preserving implementation topology and execution order. |
| `/aibdd-implement` | **Execution driver** | Turns every checkbox into a live todo item and keeps task state synchronized with actual execution. |
| `/aibdd-red-execute` + `/aibdd-red-evaluate` | **Red gate** | Ensures your failing acceptance state is legal, visible, and grounded before code changes begin. |
| `/aibdd-green-execute` + `/aibdd-green-evaluate` | **Green gate** | Drives product code to passing acceptance without letting fake green or hollow fixes slip through. |
| `/aibdd-refactor-execute` + `/aibdd-refactor-evaluate` | **Refactor gate** | Improves internal structure while preserving strict acceptance and constitution conformance. |
| `/aibdd-reconcile` | **Change cascade manager** | Repairs upstream truth from the earliest affected planner and propagates the correction forward. |
| `/aibdd-discovery-uiux` | **Frontend intent extractor** *(In Development)* | Extracts frontend-specific intent from discovery output, emitting an FE intent bundle and brand seed for downstream UI/UX skills. |
| `/aibdd-frontend-context-analyze` | **Frontend context analyzer** *(In Development)* | Analyzes the existing frontend codebase to surface component conventions, routing shape, and integration constraints before planning begins. |
| `/aibdd-uiux-design` | **UI/UX visual planner** *(In Development)* | Derives a component inventory and frame composition map from discovery artifacts, then emits a Pencil-ready prompt and style profile for visual exploration. |
| `/aibdd-uiux-design-lite` | **UI/UX visual planner (lite)** *(Happy Path Only)* | Lightweight variant of `/aibdd-uiux-design` covering the happy-path visual flow only — suitable for early-stage exploration without full state matrix derivation. |

## Why This Workflow Wins

### 1. It reduces cognitive load

AIBDD does not dump every concern into one giant prompt. Flow truth, rule truth, plan truth, DSL truth, and acceptance truth are separated on purpose. That means less context soup, faster review, and fewer invisible contradictions.

### 2. It increases trust

The workflow is built to ask when it does not know. Clarification is a feature, not a failure. Red and green are evaluated, not declared. That makes the output easier to trust because the system is designed to expose uncertainty early.

### 3. It keeps humans in control

This is not "press one button and hope." AIBDD is human-in-the-loop, but the loop is structured. People decide the truth. The system propagates it, checks it, and executes against it.

### 4. It preserves traceability

The chain from requirement to execution stays visible:

`idea -> discovery -> activity -> test plan -> feature scope -> tasks -> red/green/refactor`

That matters when you need audits, debugging, impact analysis, or simply a clean answer to "why did we build it this way?"

### 5. It makes other agents better

AIBDD is not trying to replace every coding agent. It makes coding agents more effective by feeding them sharper specs, clearer acceptance targets, and narrower execution scopes.

In other words:

Spend effort once on precise truth, and every downstream agent gets more accurate.

## What Makes This Repo Valuable

This repository is not just a document set. It is the workflow contract for a spec-driven software factory.

It captures:

- the planning phases,
- the artifact boundaries,
- the handoff rules,
- the quality gates,
- the rollback model,
- and the execution discipline that keeps the whole thing coherent.

If you care about shipping software with AI and still being able to explain, audit, debug, and trust what happened, this is the kind of workflow that scales.

## Bottom Line

AI can already write a lot of code.

What most teams still do not have is a reliable way to turn intent into acceptance truth, and acceptance truth into shipped systems, without losing clarity in the middle.

AIBDD is built for that gap.

Build the spec.
Lock the acceptance target.
Drive execution from truth.
Ship with fewer guesses.

## License

This repository is licensed under the [Apache License 2.0](LICENSE). See [`NOTICE`](NOTICE) for attribution.
