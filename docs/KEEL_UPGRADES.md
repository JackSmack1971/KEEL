After inspecting the current KEEL package and comparing it against current Codex engineering guidance and the strongest ideas in GSD, BMad, Spec Kit, Spec Kitty, OpenSpec, Tessl, Kiro, Superpowers, Conductor, and Zencoder/Zenflow, I think the project has a credible path to becoming something meaningfully better.

But the path is not “add more process.” KEEL is already stronger than most of these systems in governance. The next leap is turning it from a governed change protocol into an adaptive engineering operating system.

Executive assessment

My current read:

DimensionKEEL todayCompetitive position





Intent preservation

9/10

Excellent

Scope governance

9.5/10

Probably best-in-class

Verification integrity

9.5/10

Distinctive advantage

Authorization/effects control

9.5/10

Distinctive advantage

Git-native auditability

9/10

Strong differentiator

Stack agnosticism

8.5/10

Strong architecture, incomplete adapters

Agent context engineering

7/10

Good foundation

Spec/requirements ergonomics

6.5/10

Behind Spec Kit/Kiro/BMad

Task decomposition

5/10

Behind GSD/Spec Kitty

Parallel execution

4.5/10

Policy exists; runtime weak

Autonomous orchestration

3/10

Major gap

Codebase intelligence

4/10

Major gap

Developer experience

5/10

Major gap

Self-improvement/evals

3/10

Designed, not operational

Installation/upgrades

3/10

Major productization gap

Empirical evidence KEEL helps

2/10

Biggest strategic weakness

So the paradox is:

KEEL may already have the strongest safety/integrity substrate of the group, while being substantially behind several competitors as an end-to-end development experience.

That is fixable.

1. What KEEL actually is

Most competitors you named are principally some mixture of:

intent → specification → plan → tasks → implementation

KEEL instead has something closer to:

intent → governed change contract → bounded execution → independently evidenced state → sealed Git object → controlled integration

That is much more interesting.

Your current lifecycle:

DISCUSS
   ↓
PLAN
   ↓
EXECUTE
   ↓
VERIFY
   ↓
SHIP
   ↓
SEAL
   ↓
INTEGRATE
   ↓
ANCHOR

has several unusually strong properties.

proposal.md, delta.md, scope.txt, risk.json, effects.json, and authorization.json separate different kinds of truth instead of mixing everything into a giant specification.

Then KEEL binds verification to:

base commit
+
material changed paths
+
stable intent artifacts
+
content digest

and later verifies the committed tree before producing:

refs/keel/candidates/<change-id>

and verifies the landed tree before anchoring.

That is far beyond the typical:

“Agent says tests passed.”

or even:

“CI says this PR passed.”

The sealed-candidate → landed-tree verification model is probably KEEL's clearest technical differentiator.

The prior hardening work also materially strengthened this foundation: the static control-plane validation covered all 38 mandatory domains and specifically exercised sealed candidates, landed-tree digests, phase permissions, effects-bound authorization, Windows hooks, emergency debt, and cache hygiene. Actual Codex runtime hook behavior remained the major unverified runtime surface.

The archive you gave me doesn't contain .git, so keel.py doctor correctly refuses to certify this extracted copy. That's a good failure mode rather than a defect.

2. KEEL is solving a deeper problem than Spec Kit/OpenSpec

Spec Kit currently describes its core default workflow as:

Spec → Plan → Tasks → Implement → Converge

and emphasizes structured cross-artifact reasoning. (GitHub Pages)

OpenSpec emphasizes a lighter artifact-guided system and explicitly optimizes for being fluid, iterative, brownfield-friendly, and relatively easy to adopt. (GitHub)

Tessl ties requirements to specs and tests, with approval before implementation. (Tessl Documentation)

All are useful.

KEEL asks a different question:

How do we know that the thing an agent is about to land is exactly the thing that was authorized, scoped, implemented, and verified?

That question becomes increasingly important as coding agents become more autonomous.

OpenAI's own harness engineering experience strongly reinforces this philosophy: make the environment legible to agents, enforce invariants mechanically instead of relying exclusively on documentation, and give agents direct access to validation surfaces such as tests, browsers, logs, metrics, and traces. (OpenAI)

KEEL is unusually aligned with that direction.

3. The biggest architectural weakness: KEEL governs work but does not yet manage work

This is the main distinction I would address.

The existing implementation is excellent at:

given change C,
control C correctly

It is much weaker at:

given objective O,
discover the optimal set of changes C1...Cn
order them
parallelize safe subsets
manage dependencies
recover failures
coordinate reviews
land them
learn from the result

GSD is considerably more mature here.

It now has specialized research, mapping, planning, checking, execution, debugging, verification, UI, security, framework-selection, and synthesis agents. It also performs model-tier routing according to workload. (GitHub)

Spec Kitty explicitly models:

spec
  ↓
plan
  ↓
tasks
  ↓
next
  ↓
review
  ↓
accept
  ↓
merge

and allocates isolated worktrees to agents. (GitHub)

Symphony goes further:

task tracker
      ↓
dependency DAG
      ↓
eligible tasks
      ↓
isolated agent workspaces
      ↓
continuous execution
      ↓
CI / review / rebase / retry
      ↓
land

OpenAI reports that this style of orchestration produced as much as a 500% increase in landed PRs in some teams. (OpenAI)

KEEL currently documents orchestration as DEFERRED.

That is architecturally reasonable for bootstrap.

Competitively, it is now the largest missing subsystem.

4. Build KEEL Missions

I would introduce a level above a KEEL change.

Not:

User objective
     ↓
KEEL change

but:

                    MISSION
                       │
          ┌────────────┴────────────┐
          │                         │
      OBJECTIVES                 CONSTRAINTS
          │                         │
          └────────────┬────────────┘
                       ↓
                DISCOVERY / RESEARCH
                       ↓
                 WORK GRAPH
                 ┌─────┴─────┐
                 │           │
              Change A    Change B
                 │           │
                 └────┬──────┘
                      ↓
                   Change C
                      ↓
               Mission Verify
                      ↓
                 Mission Close

Each leaf remains a normal KEEL change.

This is important.

Do not weaken KEEL by allowing a giant autonomous mission to bypass the per-change ledger.

Instead:

KEEL Mission orchestrates; KEEL Change governs.

That gives you Symphony/GSD/Spec Kitty scale without surrendering KEEL's strongest property.

A mission artifact could eventually contain roughly:

mission_id: auth-redesign

objective: >
  Replace legacy session authentication with OIDC.

success_criteria:
  - existing accounts remain usable
  - token refresh survives restart
  - old auth endpoints removed
  - rollback tested

constraints:
  - no database downtime
  - backward-compatible migration
  - preserve mobile clients

work:
  auth-contract:
    risk: high
    depends_on: []

  migration:
    risk: high
    depends_on:
      - auth-contract

  backend:
    depends_on:
      - auth-contract

  frontend:
    depends_on:
      - auth-contract

  cutover:
    depends_on:
      - backend
      - frontend
      - migration

KEEL can then compute the runnable frontier.

5. Your specification model is durable but too weakly typed

delta.md is elegant:

ADDED
MODIFIED
REMOVED

But prose deltas alone cannot carry everything a serious autonomous engineering system eventually needs.

You need machine-readable connections between:

requirement
→ acceptance criterion
→ implementation surface
→ verification evidence

Today KEEL's scope.txt gives excellent file-level traceability.

It does not yet give equally strong behavioral traceability.

I would therefore extend rather than replace the delta model.

For example:

proposal.md
delta.md
requirements.json
acceptance.json
scope.txt
risk.json
effects.json

An acceptance object might be:

{
  "id": "AC-004",
  "requirement": "Expired refresh tokens are rejected",
  "evidence_type": "automated-test",
  "required": true,
  "evidence": [
    "tests/auth/refresh_expiration_test.py"
  ]
}

Then verification isn't merely:

all configured commands passed

but can become:

AC-001 PASS
AC-002 PASS
AC-003 PASS
AC-004 PASS

This is one place where Tessl's explicit test/spec relationship contains a useful idea. (Tessl Documentation)

6. Introduce an Evidence Graph

This could become a major KEEL differentiator.

Instead of treating verification as a flat list of commands:

check A passed
check B passed
check C passed

model the evidence relationship:

Requirement
     │
     ▼
Acceptance Criterion
     │
     ├── Unit test
     ├── Integration test
     ├── Architecture invariant
     ├── Browser evidence
     ├── Security scan
     └── Runtime observation

Then:

KEEL VERIFY

calculates coverage of the acceptance graph.

Example:

REQ-7
└── AC-7.1: unauthorized request returns 403
    ├── unit:test_policy_denial                PASS
    ├── integration:test_api_policy            PASS
    └── security-review:auth-boundary           PASS

This is much more rigorous than conventional test orchestration.

It also prepares KEEL for nontraditional engineering:

ML
firmware
data pipelines
infrastructure
games
frontend
distributed systems
security
scientific software

where "tests passed" can mean radically different things.

7. KEEL needs a Capability Resolver

Your capability registry is conceptually excellent.

The 38-domain model is one of the strongest things in the package.

But right now it is mostly:

human/agent discovers project
→ edits registry
→ activates domains

The next version should mechanically infer evidence.

For example:

package.json
     ↓
Node ecosystem

Cargo.toml
     ↓
Rust ecosystem

pyproject.toml
     ↓
Python ecosystem

Dockerfile
     ↓
container build

terraform/
     ↓
IaC

playwright.config.*
     ↓
browser verification

.github/workflows/
     ↓
CI

prisma/schema.prisma
     ↓
persistent datastore / migrations

src/**/*.tsx
     ↓
frontend / browser / a11y considerations

But this must remain evidence based, not assumption based.

So the resolver returns:

DETECTED
LIKELY
UNKNOWN
CONFLICT

rather than silently changing policy.

Then:

keel doctor

could say:

Detected:
  Node 24
  TypeScript
  React
  Vite
  Vitest
  Playwright
  GitHub Actions

Suggested domain activations:
  build-toolchain
  testing-evals
  quality-static-analysis
  ui-browser-a11y-i18n
  ci-cd

Potential missing controls:
  dependency supply-chain
  frontend runtime evidence

This would greatly improve the "drop KEEL into anything" story.

8. KEEL does not yet have real codebase intelligence

GSD has explicit parallel codebase mapping. Its mapper produces structured durable codebase context instead of repeatedly forcing agents to rediscover the repository. (GitHub)

Zencoder emphasizes repository intelligence and cross-repository integration. (Zencoder Docs)

KEEL currently provides:

ARCHITECTURE.md
docs/
capability registry
AGENTS.md

but no active system for creating trustworthy architecture knowledge.

That is insufficient for very large repositories.

I would add:

keel map

with outputs like:

.keel/knowledge/
    topology.json
    modules.json
    boundaries.json
    commands.json
    tests.json
    ownership.json
    dependencies.json
    entrypoints.json

The important difference from generic RAG:

These should be extracted facts with provenance.

Example:

{
  "module": "payments",
  "path": "src/payments",
  "depends_on": [
    {
      "module": "ledger",
      "evidence": "import graph"
    }
  ]
}

Agents can query that compact representation instead of rereading 400 files.

9. Make repository context compiled, not accumulated

This is an especially important frontier-model insight.

Current OpenAI model guidance warns that large or conflicting instruction surfaces can cause unnecessary pauses or divergence, while explicitly recommending clear delegation and verification guidance. (OpenAI Developers)

KEEL should therefore avoid becoming:

AGENTS.md
+ 38 domain docs
+ skills
+ plans
+ ledgers
+ architecture
+ generated knowledge
+ historical decisions

all loaded at once.

Instead create a:

KEEL Context Compiler

Input:

task
+
active change
+
scope
+
risk
+
capabilities
+
affected architecture

Output:

minimal task context

For example:

Task touches:
  src/auth/**
  migrations/**
  tests/auth/**

Relevant context:
  auth architecture invariant
  migration rules
  DB commands
  security contract
  acceptance criteria
  active delta

Excluded:
  frontend guidance
  mobile docs
  ML guidance
  unrelated historical plans

This attacks context rot much more elegantly than simply creating fresh sessions.

10. Superpowers has something KEEL currently lacks: behavioral methodology

Superpowers strongly dictates how engineering reasoning itself should occur:

brainstorm
→ design
→ implementation plan
→ TDD
→ subagent implementation
→ review

and reinforces true red/green workflows. (GitHub)

KEEL deliberately leaves more room for model judgment.

I agree with that choice.

However, KEEL currently has only two meaningful reusable skills:

keel-change-lifecycle
control-plane-maintenance

That is too thin.

Don't turn KEEL into BMad's huge role catalog.

Instead add a small collection of engineering protocols:

debugging
root-cause-analysis
architecture-investigation
dependency-upgrade
migration
security-review
performance-investigation
frontend-runtime-verification
test-remediation
incident-response
release

These should be skills, not mandatory phases.

So KEEL becomes:

stable governance kernel
+
dynamically activated engineering protocols

That is the right architecture.

11. Do not copy BMad's giant agent organization

BMad's advantage is breadth. It offers extensive agents, workflows, modules, customization, and scale-adaptive development guidance. (GitHub)

The downside is conceptual surface area.

KEEL shouldn't compete by saying:

We have 45 agents instead of 34.

I'd instead target:

few persistent roles
+
many composable skills
+
dynamic topology

For example:

Coordinator
Explorer
Planner
Executor
Verifier
Reviewer
Risk Reviewer

Then allow the coordinator to instantiate combinations.

That is closer to the trajectory OpenAI describes for capable models: give agents objectives, sufficient tools and context, and avoid reducing them to unnecessarily rigid state-machine nodes. (OpenAI)

12. Add a Subagent Topology Resolver

Your current fixed agents are useful:

explorer
keel-discuss
keel-plan
keel-verify
keel-ship
reviewer
risk-reviewer

But KEEL should eventually compute delegation.

Example:

change scope:
  backend
  frontend
  migration

risk:
  high

resolver:
  explorer[backend]
  explorer[frontend]
  migration-reviewer
  security-reviewer
  verifier

For a tiny fix:

executor
verifier

For investigation:

3 explorers
synthesizer

This also aligns with current OpenAI model guidance that subagent delegation can materially improve both quality and latency when parallelizable work exists. (OpenAI Developers)

13. Parallelism should become a first-class execution primitive

Your current rule is correct:

one change-id = one worktree = one primary writer.

Keep it.

Conductor and Zenflow both use isolated worktrees to make parallel sessions practical. (Conductor)

KEEL should automate the lifecycle:

keel worktree create C-102
keel worktree status C-102
keel worktree retire C-102

Then:

keel mission run

could safely spawn:

C-102 ─ worktree A
C-103 ─ worktree B
C-104 ─ blocked on A+B

This would turn the existing parallelism policy into a parallelism capability.

Big difference.

14. You need environment isolation, not merely Git isolation

OpenAI's harness-engineering article makes another critical point: their agents can run independent application instances, browser sessions, logs, traces, and metrics per worktree. (OpenAI)

KEEL currently governs the source tree extremely well.

It does not govern:

ports
databases
containers
temporary directories
service names
browser profiles
runtime logs
test fixtures
cloud sandboxes

Yet those frequently cause parallel-agent interference.

Add:

Environment Contract

perhaps:

environment:
  setup: scripts/dev-setup
  start: scripts/dev-start
  stop: scripts/dev-stop

isolation:
  ports: dynamic
  temp: per-change
  database: per-change
  browser_profile: per-change

This should activate only when relevant.

15. Verification needs to become multimodal

Currently the deterministic command runner is good, but largely subprocess-oriented.

For modern software, verification often requires:

DOM
screenshots
browser console
network requests
logs
metrics
traces
performance profiles
database state
mobile simulators
hardware

OpenAI explicitly describes making browser behavior and observability available to Codex because this dramatically increases autonomous engineering capability. (OpenAI)

Kiro similarly exposes specs, hooks, MCP, permissions, subagents, checkpoints, and other runtime capabilities through one harness. (Kiro)

KEEL should therefore define evidence providers.

For example:

command
unit_test
browser
visual
log_query
metric_query
trace_query
schema
security
benchmark
hardware
human_review
external_ci

Then the core doesn't care which stack produced the evidence.

That's genuine stack agnosticism.

16. One implementation detail that weakens stack-agnostic claims

.keel/config.json determines "source" using a list of extensions:

.c
.cpp
.cs
.go
.java
.js
.py
.rs
.ts
...

That's practical, but it isn't truly stack agnostic.

It can misclassify things such as:

.vue
.svelte
astro
proto
graphql
cue
nix
hcl
Rmd
notebooks
shader files
generated DSLs
Makefiles
Dockerfiles
Bazel/Starlark

More importantly, whether a file is substantive source is project-dependent.

Replace extension heuristics with something layered:

explicit project classification
        ↓
detected ecosystem classifiers
        ↓
generic source heuristic
        ↓
unknown = conservative

The kernel shouldn't hard-code the universe of programming languages.

17. Effects enforcement is excellent conceptually, but command detection is necessarily incomplete

The hook currently recognizes known integration command patterns.

That works for:

git push
git merge
gh pr ...

But arbitrary effects can happen through:

curl
terraform
kubectl
aws
gcloud
az
database clients
custom deploy scripts
npm publish
docker push
MCP
application-specific CLIs

There is no universal reliable way to infer effect semantics from shell strings.

So don't keep expanding giant command blacklists.

Introduce an:

Effect Capability Model

Commands/tools declare capabilities such as:

filesystem.write
git.local.commit
git.remote.push
vcs.merge
package.publish
database.migrate
cloud.deploy
infra.apply
issue.modify
email.send
secret.read

Then authorization is against effects, not command spelling.

That's dramatically more scalable.

18. KEEL needs a first-class reconciliation engine

Long-running agents fail.

Machines reboot.

Processes crash.

Branches move.

Review comments arrive.

CI flakes.

Dependencies get merged underneath you.

Symphony's strength is not merely agent dispatch; it also reconciles continuously, restarts agents, reacts to state changes, rebases, retries checks, and shepherds work into landing. (OpenAI)

KEEL should introduce:

keel reconcile

which asks:

What does the ledger claim?
What does Git say?
What does the workspace say?
What does CI say?
What does the issue tracker say?
What external effects occurred?
What state transition is legal now?

Then repair the process state, not blindly modify code.

This will matter enormously for unattended runs.

19. Implement next-action computation

BMad has bmad-help, which tells users what logically comes next. (GitHub)

Spec Kitty has next. (GitHub)

KEEL should have:

keel next

Examples:

$ keel next

C-184 is in PLAN.

Blocking:
  effects.json requires authorization
  risk-review.md incomplete

Next legal actions:
  1. complete risk review
  2. obtain authorization
  3. record authorization
  4. run `keel gate plan`

Or:

$ keel next

No active change.

Mission checkout-v2 has:
  C-201 READY
  C-202 READY
  C-203 BLOCKED by C-201,C-202

Recommended:
  start C-201 and C-202 in separate worktrees

This looks simple but would radically improve usability.

20. KEEL currently over-indexes on correctness and under-indexes on economics

A superior agent framework has to optimize:

quality
latency
token usage
model cost
human attention
failure recovery

GSD already has model tiers. (GitHub)

KEEL currently has no meaningful compute-routing layer.

Add a work complexity estimator:

trivial
standard
complex
critical

and use it to select:

reasoning effort
model
number of agents
review depth
verification breadth
context budget

Not hard-coded model names.

Instead express capabilities:

fast
balanced
deep
max

Then map them at runtime.

This keeps KEEL model-independent.

21. The most important missing subsystem is KEEL Evals

This is where I would be toughest on the project.

You want to say:

KEEL outperforms GSD, BMad, Spec Kit, Kiro, etc.

Right now that statement would be impossible to substantiate.

The framework needs its own benchmark.

Create something like:

KEELBench

with representative repositories/tasks:

bugfix
feature
refactor
dependency upgrade
migration
security remediation
frontend change
performance regression
brownfield investigation
multi-service change
release

Measure:

task success
acceptance coverage
introduced regressions
scope violations
architectural violations
unauthorized effects
human interventions
tokens
wall time
retries
merge conflicts
CI failures
review findings
post-merge defects

Then compare:

Codex vanilla
Codex + KEEL
Codex + GSD
Codex + Spec Kit
Codex + OpenSpec
...

Ideally repeated trials.

Until this exists:

KEEL superiority is an architectural hypothesis.

Once it exists:

KEEL superiority can become an engineering result.

This is the single most important strategic change I would make.

22. KEEL should learn from failures mechanically

You already have the right doctrine:

repeated mistakes should become mechanical invariants.

Now operationalize it.

Imagine:

production incident
       ↓
reviewed evidence
       ↓
finding
       ↓
failure class
       ↓
regression eval
       ↓
candidate invariant
       ↓
test / lint / hook / architecture rule

That produces:

KEEL Learning Loop

EXECUTE
   ↓
VERIFY
   ↓
SHIP
   ↓
OPERATE
   ↓
OBSERVE
   ↓
LEARN
   ↓
HARDEN
   ↺

Kiro already advertises learning from developer review feedback as a persistent steering mechanism. (Kiro)

KEEL's version should be more conservative:

never automatically convert arbitrary feedback into permanent instruction.

Instead:

observation
→ proposal
→ evaluation
→ promotion

That's much safer.

23. Turn entropy control into an actual service

Your ENTROPY.md direction is good but largely aspirational.

Eventually KEEL should periodically detect:

stale architecture docs
obsolete commands
dead capabilities
unused skills
broken links
drifting generated artifacts
unreferenced decisions
TODO debt
orphaned plans
stale dependencies
duplicated instructions
oversized AGENTS cascades
repeated review findings

Then generate small KEEL-governed maintenance changes.

That produces a repository that actively resists agent-created decay.

This aligns extremely closely with OpenAI's observation that agent-first development shifts the human role toward building scaffolding and mechanically preventing recurring failures rather than repeatedly correcting individual outputs. (OpenAI)

24. Developer experience is currently KEEL's weakest visible surface

Competitors are polished.

Kiro offers one harness across IDE, CLI, web, and mobile, with specs, hooks, subagents, permissions, MCP, memory and isolated execution. (Kiro)

Zenflow provides worktrees, workflow cards, integrations, agent presets, review surfaces, and cross-service orchestration. (Zencoder Docs)

KEEL currently feels like:

excellent research prototype
+
excellent control plane
+
manual CLI plumbing

To win adoption, commands should eventually feel more like:

keel init
keel discover
keel start
keel status
keel next
keel run
keel verify
keel review
keel ship
keel mission
keel doctor

rather than requiring users to understand the internal state machine before becoming productive.

The sophisticated internals should remain available.

They shouldn't be required knowledge for ordinary usage.

25. Installation, upgrades and schema migration are missing product primitives

A real framework needs:

version
installer
upgrade
migration
compatibility check
rollback

Today you have:

schema_version: 1

but not a mature lifecycle surrounding it.

Eventually:

keel version
keel init
keel upgrade
keel migrate
keel doctor --compat

must understand:

Codex version
hook schema
KEEL schema
skill version
configuration version
ledger version

This becomes especially important because Codex itself evolves.

Your current documentation is appropriately cautious about trusting project .codex/ configuration and hook definitions. Preserve that philosophy.

26. What I would steal from each competitor

There are good ideas worth incorporating, without copying their architectures.

SystemSteal thisDo not copy





GSD

codebase mapping, context engineering, model routing, fresh specialist agents

command/workflow proliferation

BMad

scale-adaptive workflow selection, discoverable “what next?” UX

huge persona organization

Spec Kit

requirements → plan → tasks traceability and convergence

dependence on an essentially linear SDD lifecycle

Spec Kitty

governed work packages, next, worktree execution

UI/process becoming the core abstraction

OpenSpec

lightweight delta/change philosophy, brownfield friendliness

mostly prose-level enforcement

Tessl

requirement ↔ test relationships, current library knowledge

ecosystem coupling

Kiro

unified harness, hooks, specs, permissions, subagents, runtime surfaces

IDE/platform dependence

Superpowers

reusable behavioral engineering skills, rigorous debugging/TDD protocols

overly prescriptive workflow for every task

Conductor

excellent workspace/worktree ergonomics

dependency on a GUI orchestrator

Zencoder/Zenflow

workflow templates, integration graph, worktree automation

product-service dependency

Symphony

objective/task orchestration, reconciliation, unattended agents

tying KEEL itself to one tracker

That combination starts becoming genuinely unusual.

27. The architecture I would target

I would evolve KEEL toward this:

                         USER OBJECTIVE
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Mission Contract    │
                    │ intent + success    │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Capability Resolver │
                    │ project discovery   │
                    └──────────┬──────────┘
                               │
               ┌───────────────┴───────────────┐
               ▼                               ▼
      Repository Knowledge             Research Providers
      / Context Compiler
               │                               │
               └───────────────┬───────────────┘
                               ▼
                    ┌─────────────────────┐
                    │ Work Graph Planner  │
                    │ DAG + dependencies  │
                    └──────────┬──────────┘
                               │
                               ▼
                 ┌──────────────────────────┐
                 │ Subagent Topology        │
                 │ + Compute Router         │
                 └────────────┬─────────────┘
                              │
            ┌─────────────────┼──────────────────┐
            ▼                 ▼                  ▼
       WORKTREE A        WORKTREE B         WORKTREE C
       KEEL C-01         KEEL C-02          KEEL C-03
            │                 │                  │
      DISCUSS/PLAN       DISCUSS/PLAN       DISCUSS/PLAN
            │                 │                  │
         EXECUTE            EXECUTE             ...
            │                 │
            ▼                 ▼
      EVIDENCE GRAPH    EVIDENCE GRAPH
            │                 │
          VERIFY            VERIFY
            │                 │
           SEAL             SEAL
            └──────────┬──────┘
                       ▼
               Integration Manager
                       │
                 CI / Review Loop
                       │
                    LAND
                       │
                    ANCHOR
                       │
                       ▼
                Mission Verification
                       │
                       ▼
                  Feedback/Evals
                       │
                       ▼
                 Invariant Promotion

And across everything:

Authorization
Risk
Effects
Observability
Provenance
Recovery
Audit

That is a much stronger thesis than merely "Spec Kit, but better."

28. Recommended next-generation KEEL roadmap

I would prioritize the next work in this order:

KEELBench + telemetry schema — establish measurable baseline against vanilla Codex first. Without this, you cannot determine whether future sophistication actually helps.

Capability Resolver / project discovery — make stack agnosticism operational instead of documentary.

Context Compiler + repository knowledge graph — drastically improve large-repo performance and token economics.

Requirements/acceptance/evidence graph — upgrade verification from command passing to behavioral traceability.

keel next + workflow recommender — dramatically improve user experience with relatively little architectural risk.

Worktree manager + environment contracts — convert safe parallelism from policy into capability.

Mission/work-DAG layer — move KEEL from single-change governance into end-to-end objective execution.

Dynamic subagent topology + compute routing — let problem structure determine agents/model effort.

Reconciliation engine — make unattended and long-horizon execution resilient.

Feedback/eval/invariant promotion loop — give KEEL controlled self-improvement.

Provider-neutral effect capabilities — move authorization away from shell-command pattern recognition.

Installer/version/upgrader/schema migration system — productize the framework.

Runtime proof providers — browser, logs, traces, metrics, benchmarks, devices, external CI.

Issue/PR orchestration adapters — GitHub, Linear, Jira, etc., with Symphony-like scheduling sitting above KEEL rather than inside its kernel.

That sequence matters.

I would not build the autonomous scheduler first.

A scheduler amplifies whatever system is beneath it. Build the intelligence, evidence, context, and evaluation layers first; then unleash parallel autonomous execution.

Where I think KEEL can actually win

The winning positioning is not:

“The most comprehensive spec-driven development framework.”

Too many systems already compete there.

Nor:

“The most agents.”

Meaningless arms race.

Nor:

“The most autonomous coding framework.”

Autonomy is rapidly becoming commodity functionality.

The compelling thesis is:

KEEL is a stack-agnostic engineering control plane that converts high-level objectives into bounded, parallelizable, evidence-backed changes and can prove that what landed is what was intended, authorized, and verified.

And eventually:

It continuously learns which capabilities, context, agents, checks, and invariants produce the best engineering outcomes.

That second sentence is where it goes from an unusually strong harness to something potentially category-defining.

The current system already possesses the hardest-to-retrofit part: a serious execution-integrity kernel. Most competing systems could add more agents tomorrow. Retrofitting effects-bound authorization, verification-bound Git objects, landed-tree validation, scope confinement, controlled replanning, emergency process debt, and a domain activation model into a loose workflow framework is considerably harder.

The next milestone, therefore, should not be “KEEL v2 with more documentation.” It should be a focused architectural release centered on Capability Resolution + Context Compilation + Acceptance/Evidence Graph + KEELBench. Those four primitives would attack the largest weaknesses while strengthening the design you already have rather than diluting it. (OpenAI)