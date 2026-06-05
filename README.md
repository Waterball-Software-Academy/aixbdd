# AIBDD

> Most AI coding workflows fail in the same place: the agent starts writing code before the system has a real spec.

AIBDD is built to fix that.

AIBDD turns raw product intent into boundary-aware discovery, executable acceptance criteria, implementation tasks, and disciplined `RED -> GREEN -> REFACTOR` execution. Instead of asking an agent to guess from a paragraph and good intentions, it gives the agent a chain of explicit artifacts, each with one job, one owner, and one way to prove it is correct.

This is not vibe coding with better prompts.

This is acceptance-driven software delivery with specs as truth.

This repository is the workflow SSOT for that system. It contains the AIBDD skill family that moves a project from kickoff to discovery, planning, task generation, implementation, evaluation, and reconciliation.

## Why AIBDD Hits Hard

Most teams already know AI can write code. That is not the hard part anymore.

The hard part is getting the right code, in the right boundary, with the right acceptance target, without silently dropping requirements or smearing one change across the whole system. That is where AIBDD is strong.

It gives you:

- **Specs as truth**: artifacts are not passive documentation. They are versioned, executable, and downstream-visible.
- **Specs as guard**: implementation is judged against acceptance artifacts, not against "looks done to me."
- **Separation of concerns**: activity, feature rules, technical plan, DSL, and tasks each own a precise slice of truth.
- **Traceability end to end**: intent can be followed into flow, flow into acceptance, acceptance into tasks, and tasks into execution.
- **Human control without chaos**: the workflow is human-in-the-loop, but not human-do-everything.
- **Less guessing, more asking**: when information is missing, the system is designed to clarify instead of hallucinate.
- **Reconcile instead of rot**: when upstream requirements change, AIBDD cascades the correction from the earliest affected planner instead of letting downstream artifacts silently rot.

If ordinary AI coding feels magical right up until it becomes expensive, flaky, and hard to trust, AIBDD is the counter-move.

## Who This Is For

- **Founders and product builders** who want AI to build from acceptance truth, not from ambiguous feature blur.
- **Tech leads and architects** who need boundary-aware planning, auditable handoffs, and fewer accidental cross-layer leaks.
- **PMs, BAs, and spec owners** who want a workflow where business intent survives contact with implementation.
- **Teams already using AI coding agents** but tired of reruns, shallow fixes, and "green" outputs that were never truly grounded.

## Skill Layout

The canonical skill tree lives at `.agents/skills/` (Agent Skills standard). `.claude/skills` is a symlink that points to it, so Claude Code and Codex both load the same files without duplication.

**Windows users:** Git does not create symlinks by default on Windows. Before cloning, enable symlink support so `.claude/skills` resolves correctly:

```bash
# One-time, global
git config --global core.symlinks true

# Or per-clone
git clone -c core.symlinks=true <repo-url>
```

## Quick Start

1. Run `/aibdd-kickoff` (Pick the tech-stack, full-loaded with aibdd configuration)
2. Run `/aibdd-flows-specify` (Address what you wanna build — extract the feature/flow list)
3. Run `/aibdd-rules-specify` (Enumerate atomic acceptance rules per feature)
4. Run `/aibdd-spec-by-example` (Expand each atomic rule into a runnable Cucumber Example)
5. Run `/aibdd-plan` (No arguments needed)
6. Run `/aibdd-tasks`  (No arguments needed)
7. Run `/aibdd-implement`  (No arguments needed)
8. Run `/aibdd-red-execute`, then `/aibdd-green-execute`, then `/aibdd-refactor-execute`
9. When reality changes, use `/aibdd-reconcile`

Stop there. You will know very quickly whether you want agents guessing, or agents executing against acceptance truth.

## See It Work

```text
You:    We need refund handling for cancelled orders, with inventory return,
        approval rules, and audit visibility.

You:    /aibdd-flows-specify
AIBDD:  [sources the raw idea against boundary truth]
        [asks only the missing questions]
        [writes the rule-less feature-file list]

You:    /aibdd-rules-specify
AIBDD:  [enumerates atomic acceptance rules into each feature]

You:    /aibdd-spec-by-example
AIBDD:  [expands each atomic rule into a runnable Cucumber Example]

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

**Clarify -> Specify Flows -> Specify Rules -> Specify Examples -> Plan -> Derive Acceptance -> Execute -> Evaluate -> Reconcile**

Each stage feeds the next. Flows, rules, and examples specification writes the artifacts plan consumes. Plan records the DSL and feature scope that tasks and the red gate consume. Tasks become live execution. Execution is evaluated through red, green, and refactor gates. When something changes upstream, reconcile cascades the correction from the earliest affected planner so you do not have to fake consistency by hand.

| Skill | Your specialist | What it does |
|---|---|---|
| `/aibdd-kickoff` | **Project initializer** | Binds the project context, stack-aware config, boundary skeleton, and core AIBDD paths so the rest of the pipeline has a real starting point. |
| `/clarify-loop` | **Clarification router** | Collects missing information in a controlled, file-first way instead of letting agents improvise around ambiguity. |
| `/aibdd-flows-specify` | **Root planner** | Turns raw ideas into boundary-aware sourcing truth, impact matrix, function-package charters, the UAT-flow activity diagrams (`.activity`), and the rule-less feature-file list bound to them. |
| `/aibdd-rules-specify` | **Rule specifier** | Enumerates atomic acceptance rules into each feature skeleton, then fixes or clarifies findings. |
| `/aibdd-spec-by-example` | **Example author** | Expands every atomic rule into a runnable Cucumber Example via the 4-pattern templates, in business language, before planning begins. |
| `/aibdd-form-activity` | **Flow formulator** | Writes `.activity` DSL from flows-specify output and validates the syntax so flow truth is explicit and machine-usable. |
| `/aibdd-plan` | **Technical planner** | Converts accepted flows/rules truth into technical boundary truth, implementation planning, and red-usable DSL mappings without creating shadow truth. |
| `/aibdd-form-api-spec`, `/aibdd-form-entity-spec`, `/aibdd-form-story-spec` | **Contract formulators** | Translate the planner's reasoning package into the boundary's declared contract format — OpenAPI, DBML, or Storybook CSF3 + component. Delegated by plan; they format truth, they do not decide scope. |
| `/aibdd-tasks` | **Task graph builder** | Generates structured `tasks.md` from the accepted plan package, preserving implementation topology and execution order. |
| `/aibdd-implement` | **Execution driver** | Turns every checkbox into a live todo item and keeps task state synchronized with actual execution. |
| `/aibdd-spec-by-example-analyze` | **Example & step mapper** | Turns feature rules into concrete Examples and maps every Scenario step to legal DSL, so the red gate can render runtime-visible steps with no guessing. |
| `/aibdd-red-execute` + `/aibdd-red-evaluate` | **Red gate** | Ensures your failing acceptance state is legal, visible, and grounded before code changes begin. |
| `/aibdd-green-execute` + `/aibdd-green-evaluate` | **Green gate** | Drives product code to passing acceptance without letting fake green or hollow fixes slip through. |
| `/aibdd-refactor-execute` + `/aibdd-refactor-evaluate` | **Refactor gate** | Improves internal structure while preserving strict acceptance and constitution conformance. |
| `/aibdd-reconcile` | **Change cascade manager** | Repairs upstream truth from the earliest affected planner and propagates the correction forward. |

## Why This Workflow Wins

### 1. It reduces cognitive load

AIBDD does not dump every concern into one giant prompt. Flow truth, rule truth, plan truth, DSL truth, and acceptance truth are separated on purpose. That means less context soup, faster review, and fewer invisible contradictions.

### 2. It increases trust

The workflow is built to ask when it does not know. Clarification is a feature, not a failure. Red and green are evaluated, not declared. That makes the output easier to trust because the system is designed to expose uncertainty early.

### 3. It keeps humans in control

This is not "press one button and hope." AIBDD is human-in-the-loop, but the loop is structured. People decide the truth. The system propagates it, checks it, and executes against it.

### 4. It preserves traceability

The chain from requirement to execution stays visible:

`idea -> flows-specify (activity + feature list) -> rules-specify (feature rules) -> spec-by-example (rule examples) -> plan (DSL + feature scope) -> tasks -> red/green/refactor`

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
