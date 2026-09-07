# The Control Plane Engineering Bible

## Thesis

*A synthesis of OpenAI's harness engineering, Symphony, and self-improving agent practice.*


Across three case studies — a zero-manual-code product build, an open-sourced orchestration
spec, and a production tax-filing agent — the same underlying discipline repeats: an agentic
control plane is not a prompt library, it is an *information architecture*. Throughput, quality,
and autonomy all scale with how legible the repository, the task queue, and the feedback loop are
to the agent, not with how clever any single prompt is. This document distills that discipline
into a reusable engineering bible: principles, structures, and checklists for building a control
plane that lets coding agents operate with minimal human supervision while staying coherent over
months of unattended growth.

---

## Part I — Repository Legibility (Harness Engineering)

### 1.1 The core law: what the agent can't see doesn't exist

An agent's working knowledge is bounded by what is discoverable inside its context at run time.
Slack threads, meeting notes, tribal knowledge, and Google Docs are invisible to it in the same
way they'd be invisible to a new hire who never got looped in. The engineering consequence is
blunt: any decision that should shape future agent behavior must be encoded into the repository
as versioned, discoverable text — markdown, schemas, executable plans, or code — or it will be
silently forgotten on the next run. Treat "put it in the repo" as a non-negotiable step of any
architectural decision, review comment, or team convention that agents are expected to honor.

### 1.2 AGENTS.md is a table of contents, not an encyclopedia

A single monolithic instruction file fails in four predictable ways: it crowds out task-specific
context because context is scarce; it becomes non-guidance once everything is flagged
"important," causing local pattern-matching instead of intentional navigation; it rots because a
giant file is expensive to keep current and nobody owns all of it; and it resists mechanical
verification, so drift compounds silently. The fix is architectural, not disciplinary — cap the
root file at roughly 100 lines and make it point outward into a structured `docs/` tree that
functions as the actual system of record.

```text
AGENTS.md
ARCHITECTURE.md
docs/
├── design-docs/          # indexed, verification-status-tagged design decisions
├── exec-plans/           # active/, completed/, tech-debt-tracker.md
├── generated/            # machine-generated references (e.g. db-schema.md)
├── product-specs/        # indexed product specifications
├── references/           # vendored llms.txt-style library references
├── DESIGN.md
├── FRONTEND.md
├── PLANS.md
├── PRODUCT_SENSE.md
├── QUALITY_SCORE.md
├── RELIABILITY.md
└── SECURITY.md
```

This layout enables **progressive disclosure**: agents start from a small, stable entry point
and are taught where to look next rather than being handed everything up front. Enforce the
structure mechanically — dedicated linters and CI jobs validate that the knowledge base stays
up to date, cross-linked, and correctly structured, and a recurring "doc-gardening" agent scans
for documentation that no longer matches real code behavior and opens fix-up pull requests.

### 1.3 Plans are first-class, versioned artifacts

Lightweight ephemeral plans suffice for small changes. Complex work gets a full execution plan —
checked into the repository alongside a progress log and a decision log — so agents can resume or
audit work without depending on external memory. Active plans, completed plans, and known
technical debt are versioned and co-located in `docs/exec-plans/`, giving every future agent run
a durable trail of *why* the code looks the way it does, not just *what* it does.

### 1.4 Make the running application itself legible

Documentation covers static knowledge; agents also need to observe the system in motion. Two
concrete investments pay for themselves quickly:

- **Per-worktree bootability.** Make the app launchable per git worktree so an agent can boot,
  drive, and tear down its own isolated instance per change, without colliding with other agents'
  work.
- **A full local observability stack.** Wire logs, metrics, and traces into an ephemeral,
  per-worktree stack queryable by the agent itself (LogQL for logs, PromQL for metrics, TraceQL
  for traces). This turns previously vague prompts like "make service startup faster" into
  concrete, self-verifiable objectives such as a hard latency budget the agent can check against
  before opening a PR.
- **Browser-level legibility.** Wiring a devtools protocol into the agent runtime — with skills
  for DOM snapshots, screenshots, and navigation — lets the agent reproduce UI bugs, validate
  fixes, and reason about front-end behavior directly instead of guessing from static code
  reading. This is what enables single unattended agent runs lasting many hours.

### 1.5 Enforce invariants, not implementations

Agents are most effective inside strict boundaries with predictable structure. Rather than
prescribing exactly how a task should be solved, define the shape the solution must fit and
enforce that shape mechanically:

| Enforcement Target | Mechanism | Effect |
|---|---|---|
| Parse-don't-validate at data boundaries | Custom lint rule | Prevents ad-hoc, unchecked shape assumptions downstream |
| Layered dependency direction (e.g. Types → Config → Repo → Service → Runtime → UI) | Structural lint / architecture test | Blocks illegal cross-layer imports; cross-cutting concerns enter only through a single explicit interface |
| Structured logging, naming conventions, file size limits | Custom lints | Encodes "taste" as a mechanical, always-applied rule instead of a review comment |
| Lint error messages | Written to include remediation instructions | Agent-actionable feedback loop instead of a human-only warning |

Constraints this strict would usually be postponed until an organization has hundreds of
engineers; with agents, they are an early prerequisite, because they are what allows sustained
speed without architectural drift. Within the boundaries, leave agents significant freedom in
implementation style — correctness, maintainability, and legibility to future agent runs are the
bar, not human stylistic preference.

### 1.6 Human taste re-enters the system as code, not commentary

Review comments, refactor PRs, and user-facing bug reports are the raw material of taste. The
discipline is to promote recurring taste judgments into either updated documentation or, when
documentation repeatedly fails to prevent the same mistake, directly into a lint rule or
structural test. A one-off review comment is cheap and gets forgotten; a lint rule is expensive
to write once and then applies to every future line of agent-generated code.

### 1.7 Merge philosophy changes at agent throughput

Conventional low-throughput norms — long-lived branches, blocking on every flaky test, exhaustive
human review — become net-negative once agent output volume rises. Prefer short-lived pull
requests, non-blocking retries on flaky checks, and minimal blocking gates. Corrections are cheap
and fast at this throughput; waiting is the expensive resource. This tradeoff is only sound
because Part I's other investments (observability, structural enforcement, self-review loops)
keep quality high without gate-based enforcement.

### 1.8 Entropy management is a recurring background process, not a cleanup sprint

Agents faithfully replicate whatever patterns already exist in the repository — including
suboptimal ones — so drift is structurally inevitable, not a discipline failure. Manual "AI slop"
cleanup days do not scale. The durable fix is to encode a small number of opinionated, mechanical
"golden principles" (e.g., prefer shared utility packages over hand-rolled helpers; never probe
data shapes ad hoc — validate at the boundary or use typed SDKs) and run a recurring background
agent task that scans for deviations from them, updates quality grades per domain, and opens
small, easily reviewable, often auto-mergeable refactor pull requests. Treat this the way you'd
treat a high-interest loan: pay down drift continuously in small increments rather than letting
it compound into a periodic, painful cleanup.

---

## Part II — Orchestration (Symphony)

### 2.1 The next bottleneck after harness engineering is human attention

Once individual agent sessions are reliable, the limiting resource shifts from "can the agent do
the work" to "how many sessions can one human supervise." In practice, three to five concurrent
interactive sessions is the point past which context-switching costs outweigh added throughput.
Solving this requires decoupling agent execution from live human supervision — moving from a
model where humans drive sessions to one where humans steer a system that drives sessions itself.

### 2.2 The control-plane inversion: the issue tracker becomes the scheduler

The core reframe: individual coding sessions and pull requests are a means to an end, and the
actual unit of work software teams already organize around is the ticket. Rather than a human
opening a session per task, an orchestrator continuously polls the issue tracker and guarantees
that every eligible open ticket has an agent actively working it, restarting on crash or stall
and picking up new work automatically. The team's task board is repurposed as an explicit state
machine, and tickets can represent much larger units of work than a single PR — some issues span
multiple PRs across repositories, others are pure investigation that never touches code.

### 2.3 Minimal reference architecture

A ticket-driven orchestrator is composed of five layers, each independently portable:

| Layer | Responsibility |
|---|---|
| Policy layer (repo-owned) | A `WORKFLOW.md` contract: prompt template, runtime settings, hooks, tracker config — version-controlled with the code it governs |
| Configuration layer | Typed parsing of front matter into runtime settings, with environment-variable indirection and defaults |
| Coordination layer (orchestrator) | Polling loop, per-issue eligibility, concurrency limits, retries, reconciliation |
| Execution layer | Per-issue workspace lifecycle plus the coding-agent subprocess protocol |
| Integration layer | Tracker adapter (issue fetch, state fetch, normalization) |
| Observability layer | Structured logs and an optional human-facing status surface |

The reference implementation intentionally avoids depending on any single repository or specific
tracker plumbing; the durable idea is the guarantee, not the code: **for every open task, an
agent is running in its own workspace.**

### 2.4 Dispatch mechanics worth copying directly

- **Per-issue, persistent workspaces.** Workspaces are keyed off a sanitized issue identifier and
  reused across runs and retries; they are never deleted on success, only on terminal-state
  cleanup, so partial context and build caches survive between turns.
- **Blocker-aware dispatch.** A ticket with unresolved blockers does not get dispatched, so
  dependent chains of work (e.g., "upgrade React" blocked on "migrate to Vite") execute in the
  correct order automatically without a human sequencing them.
- **Priority-then-age-then-id sorting.** Deterministic dispatch order avoids starvation and makes
  scheduling behavior debuggable.
- **Continuation turns, not fresh sessions.** After a successful turn, if the ticket is still
  active, the same live agent thread continues rather than restarting — only the first turn sends
  the full task prompt; later turns send lightweight continuation guidance.
- **Stall and failure are different retry paths.** A stalled session (no observed activity past a
  timeout) is killed and retried; a hard failure gets exponential backoff capped at a maximum
  delay. Both preserve the workspace.
- **Tracker writes stay with the agent, not the orchestrator.** The orchestrator is a scheduler
  and a tracker *reader*; state transitions, PR links, and comments are written by the agent
  itself using tools defined in the workflow prompt. This keeps the orchestrator simple and keeps
  the actual working process — check out, mark in-progress, open a PR, move to review, attach
  proof of work — documented once in `WORKFLOW.md` instead of living only as unwritten team habit.

### 2.5 Safety invariants for any agent-workspace scheduler

1. The agent subprocess must only ever run with its current working directory equal to its
   assigned per-issue workspace path.
2. Every workspace path must resolve, after normalization, to a strict subdirectory of the
   configured workspace root — never outside it.
3. Workspace directory names are sanitized to a restricted character set, replacing anything else,
   to prevent path-traversal or collision from untrusted ticket identifiers.

### 2.6 Behavioral shift, not just a throughput shift

The most significant effect of ticket-driven orchestration is economic: once an engineer no
longer personally supervises implementation, the perceived cost of trying an idea collapses.
Speculative refactors, hypothesis tests, and exploratory prototypes become nearly free to attempt
and to discard. This also broadens who can originate work — product managers and designers can
file tickets directly without touching a repository or a coding session, and receive back a
reviewable result (including a recorded proof-of-work walkthrough). Agents themselves begin
filing follow-up tickets for improvements noticed mid-task, which humans triage and schedule
later. The net effect is that engineers spend a much larger share of time on the genuinely
ambiguous, judgment-heavy problems, while routine implementation work is absorbed by the
orchestrated layer.

### 2.7 Give agents objectives, not just state-machine transitions

An early design mistake was treating the orchestrator's states as rigid boxes the agent could
only step through one edge at a time (e.g., "implement," full stop). Model capability outgrows a
box that narrow quickly. The corrected design gives the agent a broader toolset (issue and PR
CLI, log access, reporting tools) and an *objective* for the ticket, similar to how a manager
assigns a goal rather than a literal step list to a direct report — then lets the agent reason
about how to get there, including creating and closing related tickets as it goes.

---

## Part III — Closing the Loop in Production (Self-Improving Agents)

### 3.1 The pattern generalizes beyond coding

The same legibility-plus-orchestration discipline from Parts I and II applies directly to
non-coding production agents. The tax-filing case study demonstrates a three-pillar loop that
turns real-world usage into a structured, agent-actionable improvement backlog instead of a
one-off support queue.

### 3.2 Pillar 1 — Domain-expert correction is the signal source

The people actually doing the work — accountants, in this case — are the ones positioned to tell
a true model failure apart from an expected preference, a carried-forward prior value, or normal
workflow noise. Treat every expert correction event as structured data from the start: capture
exactly what the system proposed, what the expert changed, and what was ultimately used, rather
than only logging a final accept/reject.

### 3.3 Pillar 2 — Production must generate traceable evidence, not just outputs

A system that only logs inputs and final outputs cannot support this loop; it must preserve the
full path from source material through every intermediate transformation to the final result,
with provenance at each step (e.g., which source document a specific extracted field cites back
to). Turning raw corrections into usable evaluation targets happens in three steps:

1. **Capture the difference.** Compare system output against the ground-truth outcome to produce
   field-level review rows with expected value, predicted value, and an actionability flag.
2. **Group related failures.** Cluster similar review rows to separate a recurring systemic
   failure from one-off expected noise (a single misclassified property is noise; the same field
   type being missed across dozens of cases is a pattern).
3. **Promote repeated patterns to eval targets.** Only a reviewed, clustered, repeated pattern
   becomes a concrete evaluation target — a single correction is evidence, not yet a task.

### 3.4 Pillar 3 — A bounded, evidence-carrying task environment for the agent

A validated finding becomes a scoped engineering task, not a vague alert. The task environment
separates a writable worktree from read-only production context, so the agent can investigate
freely without being able to mutate the evidence it's reasoning from:

```text
/candidates/<finding-id>/
├── repo/                        # writable — a dedicated branch
│   ├── AGENTS.md
│   ├── tasks/<finding-id>/      # task.yaml, EXEC_PLAN.md, RESULTS.md
│   ├── app/<scoped-feature>/    # the specific product surface in scope
│   ├── evals/                   # targeted dataset + suite + regression suite + grader
│   ├── skills/                  # reusable domain skills (e.g., eval-runner)
│   └── docs/                    # architecture and task-environment docs
└── scoped-tools/                # read-only
    ├── production-trace
    ├── source-artifacts
    └── domain-reference-docs
```

Within this environment the agent works through a fixed loop: investigate the pipeline (is this
an unsupported field, a missed extraction pattern, a source-selection issue, a mapping gap, or a
grader defect?); implement a targeted fix scoped to the identified cause; validate against the
targeted eval and a broader regression suite; and surface a candidate pull request for human
engineering review. Critically, if the evidence is ambiguous or the fix is not safely
automatable, the finding routes back to a human rather than being forced through — the loop is
designed to fail safely toward human judgment, not to force closure.

### 3.5 The organizational division of labor stays explicit

Automation is applied to a bounded layer — extraction and mapping, in the tax example — while
engineers retain architecture and product decisions and shipping authority, and domain experts
steer the loop through the corrections they were already making as part of their normal job.
Nobody's role is replaced by the loop; the loop exists to compress the distance between "an
expert noticed something wrong" and "the system stopped doing that."

### 3.6 Compounding reusable infrastructure

The first domain built this way is the expensive one — the case study cites roughly six weeks and
substantial engineering oversight to reach high precision and recall on the first schedule type.
That investment produces reusable abstractions, review conventions, and eval-construction
patterns that make each subsequent domain (additional tax schedules, then entirely different
business lines) measurably faster to bring into the same loop.

---

## Part IV — The Unified Control Plane Blueprint

### 4.1 Layer map

The three case studies compose into one stack. Each layer below depends on the legibility
guarantees of the layer beneath it — orchestration cannot work reliably without a legible
repository, and a self-improvement loop cannot work reliably without both.

| Layer | Governing Question | Primary Artifact |
|---|---|---|
| Repository legibility | Can an agent discover everything it needs from the repo alone? | Structured `docs/` tree + thin `AGENTS.md` |
| Architectural enforcement | Are the rules we care about mechanically checked, not just written down? | Custom linters + structural tests with remediation-aware error text |
| Capability extension | How does an agent acquire a new, reliable, repeatable skill? | `SKILL.md` packages with progressive disclosure |
| Orchestration | How does work reach an agent without a human manually starting a session? | `WORKFLOW.md` + a ticket-polling scheduler |
| Production feedback | How does real-world usage turn into a concrete, bounded engineering task? | Traced corrections → clustered findings → scoped task environments |
| Entropy control | How does the system stay coherent as volume grows? | Golden principles + recurring background cleanup agent |

### 4.2 Skills as the connective tissue

Skills (Part I's structural discipline plus the dedicated skills mechanism) are what let both the
orchestration layer and the production-feedback layer hand an agent a *reliable, named
capability* instead of re-deriving a workflow from scratch every run. A skill packages
instructions, optional scripts, and reference material behind a `SKILL.md` with a `name` and
`description`; the agent sees only lightweight metadata for all installed skills until it selects
one, at which point the full instructions load. This progressive-disclosure design is what keeps
a large skill library (skills for observability querying, for browser-driven QA, for tracker
GraphQL access, for domain-specific eval running) from crowding out task context — but it means
skill descriptions must front-load their trigger words and scope boundaries, since a large
library gets its descriptions shortened automatically under context pressure.

### 4.3 A build-order checklist

1. Stand up the structured `docs/` tree and shrink any existing monolithic instructions file down
   to a table-of-contents scope.
2. Add mechanical enforcement for the three or four architectural rules that matter most today;
   write their lint error text as remediation instructions, not just violation names.
3. Make the running system observable and drivable by the agent itself (logs, metrics, traces,
   and — for anything with a UI — devtools-level control).
4. Package the first few recurring workflows as skills with tightly scoped, trigger-word-rich
   descriptions.
5. Write a `WORKFLOW.md` that documents the *actual* process a ticket goes through today, even if
   that process currently only lives in people's heads.
6. Stand up a minimal ticket-polling orchestrator against that `WORKFLOW.md`, enforcing the three
   safety invariants (workspace-scoped execution, workspace-root containment, sanitized workspace
   keys) from day one.
7. Instrument production usage to capture full traces with provenance, not just final outputs, in
   any agent-touched workflow you intend to self-improve.
8. Build the correction → clustering → scoped-task pipeline only after you have enough real
   corrections to make clustering meaningful — this is a v2 investment, not a launch requirement.
9. Schedule a recurring background cleanup agent against a short list of golden principles before
   drift becomes a scheduled human chore.

### 4.4 Failure modes to design against

| Failure Mode | Root Cause | Mitigation |
|---|---|---|
| Agent misses institutional knowledge | Decision lived in chat/docs outside the repo | Encode every durable decision into the repo as text |
| Agent output drifts stylistically over time | No mechanical enforcement, only human review comments | Convert repeated review feedback into lint rules |
| Orchestrator double-dispatches or leaks workspaces | Missing claim/running-state checks or path containment | Enforce the three safety invariants unconditionally |
| Self-improvement loop chases noise | Corrections used individually instead of clustered | Require clustering and repetition before promoting to an eval target |
| Automation forced past its safe boundary | No explicit "route back to human" exit | Always define an ambiguous-case escape hatch to human review |
| Skill library crowds out task context | Too many skills with unfocused descriptions | Keep descriptions tight, trigger-word-first, and scoped |
