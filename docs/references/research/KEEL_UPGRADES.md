KEEL v2 — Competitive Architecture Audit and Upgrade Strategy
=============================================================

Executive conclusion
--------------------

KEEL should **not** try to become a larger Spec Kit, BMAD, or Superpowers.

Its strongest opportunity is to become something those systems mostly are not:

> **A repository-native engineering control plane that converts intent into governed autonomous work, proves what actually happened, and continuously improves the engineering environment itself.**

That distinction matters.

Most competing frameworks optimize some variant of:
    intent
      ↓
    specification
      ↓
    plan
      ↓
    tasks
      ↓
    implementation
      ↓
    review

KEEL's strongest existing mechanics instead approximate:
    intent
      ↓
    governed change contract
      ↓
    bounded execution
      ↓
    evidence-bound verification
      ↓
    sealed Git candidate
      ↓
    controlled integration
      ↓
    landed-tree re-verification
      ↓
    durable provenance anchor

That is a substantially stronger integrity model than simply asking an agent to follow a plan.

The problem is that KEEL currently excels most strongly at **governing a known change**.

The next-generation system must excel at:
    given an ambiguous engineering objective,
    discover the necessary work,
    understand the repository,
    choose the right workflow,
    decompose it,
    route agents intelligently,
    execute parallel-safe portions,
    continuously verify,
    recover from failures,
    integrate safely,
    measure the result,
    and improve the harness.

KEEL has pieces of that architecture already, but many remain advisory, skeletal, or deferred.

My overall assessment:

| Dimension                        | KEEL v2 | Competitive position                             |
| -------------------------------- | ------- | ------------------------------------------------ |
| Intent preservation              | 9/10    | Excellent                                        |
| Scope containment                | 9.5/10  | Likely differentiator                            |
| Git-verification integrity       | 9.5/10  | Likely best-in-class concept                     |
| Effect/authorization governance  | 9/10    | Major differentiator                             |
| Auditability/provenance          | 9/10    | Excellent                                        |
| Stack neutrality                 | 8/10    | Architecturally strong, operationally incomplete |
| Verification architecture        | 8.5/10  | Strong                                           |
| Repository legibility            | 7/10    | Good doctrine, shallow intelligence              |
| Context engineering              | 6.5/10  | Functional but primitive                         |
| Spec ergonomics                  | 6/10    | Behind BMAD/Kiro/Spec Kit                        |
| Adaptive workflow depth          | 5.5/10  | Behind BMAD                                      |
| Task/work decomposition          | 5.5/10  | Behind GSD/Spec Kitty                            |
| Multi-agent orchestration        | 4/10    | Major gap                                        |
| Codebase intelligence            | 4.5/10  | Major gap                                        |
| Developer UX                     | 4.5/10  | Major gap                                        |
| Model/agent routing              | 4/10    | Early                                            |
| Installation/upgrade portability | 3.5/10  | Serious weakness                                 |
| Self-improvement                 | 4/10    | Architecture exists; loop incomplete             |
| Empirical performance evidence   | 2/10    | Largest strategic weakness                       |

The important conclusion is therefore:

> **KEEL has a stronger trust substrate than its current end-to-end development experience.**

That is a good problem to have.

* * *

1. What KEEL already gets unusually right
   =========================================

1.1 The ledger decomposes engineering truth correctly
-----------------------------------------------------

Your change ledger separates:

* proposal;

* behavioral delta;

* scope;

* requirements;

* acceptance criteria;

* risk;

* effects;

* authorization;

* verification;

* candidate sealing;

* landing provenance.

This is considerably better than a monolithic `SPEC.md`.

Those artifacts answer different questions:
    proposal.md
        Why are we changing this?

    delta.md
        What behavior changes?

    scope.txt
        What may implementation touch?

    requirements.json
        What must remain/become true?

    acceptance.json
        How can success be disproved?

    risk.json
        How dangerous is the change?

    effects.json
        What consequential external actions may occur?

    authorization.json
        Which effects have actually been authorized?

    verification.json
        What evidence was observed?

That separation enables mechanical invariants that prose-heavy frameworks struggle to enforce.

* * *

2. KEEL's strongest technical differentiator: verified candidates
   =================================================================

The strongest part of the framework is the:
    VERIFY
      ↓
    commit
      ↓
    SEAL
      ↓
    refs/keel/candidates/<change>
      ↓
    integration
      ↓
    ANCHOR

model.

The important property is not merely that tests ran.

KEEL attempts to prove that the exact committed material corresponds to the verified material, and later that the landed material still corresponds to the sealed candidate.

That addresses an overlooked agentic-development failure mode:
    agent verifies tree A
            ↓
    tree changes
            ↓
    commit/merge tree B
            ↓
    everyone assumes B was verified

KEEL explicitly tries to close that gap.

This is directionally aligned with OpenAI's harness-engineering philosophy: repository constraints should become mechanically enforceable rather than remaining prose instructions, and agents should be given observable feedback surfaces that can falsify their assumptions.

I would preserve this system almost at all costs.

It is part of KEEL's potential moat.

* * *

3. Scope governance is another major advantage
   ==============================================

The combination of:
    change ID
    + declared scope
    + isolated worktree
    + pre/post tool enforcement
    + verified changed paths

is excellent architecture.

Spec Kitty and Conductor both correctly recognize worktree isolation as foundational for parallel agents. Spec Kitty explicitly gives agents isolated Git worktrees as part of its governed `spec → plan → tasks → next → review → accept → merge` runtime.

Conductor similarly treats a worktree as the container for an agent's branch, environment, terminal, conversation, and review flow.

KEEL already has the conceptual substrate for this.

The missing layer is **automatic orchestration of those worktrees**.

* * *

4. Authorization and effects are unusually sophisticated
   ========================================================

`.keel/contracts.json` defines explicit effect capabilities such as:
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

This is the beginning of something extremely valuable:

> **Capability-based engineering authorization.**

Most coding frameworks reason primarily about files.

KEEL is starting to reason about **effects**.

That distinction matters enormously for autonomous engineering.

Changing:
    deployment.yaml

is not equivalent to:
    deploying production

Likewise:
    editing migration code

is not equivalent to:
    running the migration

KEEL's architecture recognizes this separation.

I would expand it substantially rather than simplify it.

* * *

5. The largest architectural gap: KEEL does not yet execute Missions
   ====================================================================

You have already introduced `.keel/lib/mission_graph.py`.

That is the correct abstraction.

But currently `dispatch_plan()` literally emits:
    "execution": "DEFERRED"

Mission support therefore remains primarily an advisory DAG.

This is the single most important subsystem to build next.

OpenAI's Symphony architecture exists specifically because context switching and unattended orchestration became bottlenecks after individual Codex agents became capable enough. Symphony turns tracker work into isolated executable agent work, coordinating dependencies, workspaces, retries, and integration.

Current Codex itself is explicitly designed for multi-agent workflows and built-in isolated worktree execution.

KEEL should therefore evolve from:
    MISSION
      ↓
    calculate runnable nodes
      ↓
    tell operator what could run

to:
    MISSION CONTROLLER
            │
            ├── dependency resolver
            ├── worktree allocator
            ├── capability resolver
            ├── context compiler
            ├── topology router
            ├── agent launcher
            ├── verifier
            ├── reviewer
            ├── retry controller
            ├── integration controller
            └── mission verifier

Each mission child should remain an ordinary KEEL change.

That preserves your trust model:

> **Mission orchestrates. Change governs.**

Do not create a parallel mission execution model that bypasses the ledger.

* * *

6. Mission graphs need far richer semantics
   ===========================================

The present work graph supports essentially:
    {
      "risk": "...",
      "depends_on": [...]
    }

That will not be enough.

A serious engineering DAG needs at least:
    id:
    objective:
    depends_on:
    blocks:
    scope_hint:
    capabilities_required:
    environment:
    risk:
    estimated_complexity:
    acceptance_refs:
    resources:
    exclusive_resources:
    parallel_safe:
    review_policy:
    verification_policy:
    retry_policy:
    integration_policy:
    effects:
    authorization_class:
    model_profile:
    context_profile:
    state:

It should also distinguish dependency types:
    HARD
    SOFT
    DATA
    INTERFACE
    ENVIRONMENT
    REVIEW
    AUTHORIZATION

Otherwise the graph cannot intelligently schedule work.

* * *

7. Build dynamic mission decomposition, not just mission validation
   ===================================================================

The next missing primitive is:
    objective
        ↓
    repository understanding
        ↓
    solution architecture
        ↓
    change decomposition
        ↓
    dependency graph

GSD's major advantage is context and work decomposition. Its current design explicitly uses fresh-context research/planning/execution agents to combat context degradation.

BMAD similarly advertises scale-adaptive planning that changes according to problem complexity and offers specialized planning, architecture, product, UX, testing, and implementation workflows.

KEEL currently has the infrastructure to govern work once the decomposition exists.

It needs a **Mission Planner** capable of producing the decomposition.

* * *

8. Repository intelligence is currently far too shallow
   =======================================================

This is probably the second most important technical weakness.

`capability_resolver.py` largely detects capabilities using path globs:
    package.json
    pyproject.toml
    Cargo.toml
    tests/**
    *.tf
    playwright.config.*

That is a useful bootstrap heuristic.

It is not codebase understanding.

Likewise, the Context Compiler operates largely through explicitly mapped documents and bounded character extraction.

This will become inadequate on large repositories.

Zenflow/Zencoder already emphasizes multi-repository indexing and context engines, while its agents execute inside isolated worktrees.

Kiro generates persistent product, technology, and structural steering from repository analysis and supports codebase indexing across its surfaces.

KEEL needs a **Repository Intelligence Graph**.

At minimum:
    FILES
      ↓
    SYMBOLS
      ↓
    IMPORTS / CALLS
      ↓
    MODULES
      ↓
    COMPONENTS
      ↓
    OWNERSHIP
      ↓
    RUNTIME PATHS
      ↓
    TESTS
      ↓
    CONFIGURATION
      ↓
    DEPLOYMENT SURFACES

Useful node types might include:
    file
    module
    symbol
    service
    package
    endpoint
    database
    table
    queue
    job
    test
    schema
    config
    deployment
    workflow
    generated-artifact
    owner

Useful edges:
    imports
    calls
    implements
    tests
    generates
    deploys
    reads
    writes
    owns
    depends_on
    configured_by
    exposes
    consumes

This graph should be a **derived cache**, never policy.

That fits your existing doctrine perfectly.

* * *

9. Context compilation must become query-driven
   ===============================================

Current context compilation has a hard bound of:
    "max_chars": 12000

Hard bounds are good.

The selection method is the problem.

The next compiler should behave more like:
    task
     +
    mission node
     +
    changed scope
     +
    repository graph
     +
    git history
     +
    capability evidence
     +
    acceptance obligations
           ↓
    relevance planner
           ↓
    bounded context packet

Rather than:
    known capability
        ↓
    predefined documents

Each context fragment should carry provenance:
    source:
    digest:
    reason_selected:
    relevance:
    freshness:
    authority:
    token_cost:

Then context selection can itself be benchmarked.

* * *

10. Avoid excessive repeated prompt injection
    =============================================

Your hooks inject KEEL context on both:
    SessionStart
    UserPromptSubmit

This is understandable, but it deserves scrutiny.

The OpenAI Codex repository's own AGENTS guidance explicitly warns against frequent context changes that harm caching and requires injected context to remain bounded.

KEEL should evolve toward **delta context injection**:
    previous state digest
            ↓
    current state digest
            ↓
    unchanged?
       YES → no injection
       NO  → inject only changed decision state

Or:
    ACTIVE CHANGE: xyz
    PHASE: EXECUTE → VERIFY
    NEW REQUIREMENT: R-07
    SCOPE CHANGE: none
    NEW BLOCKER: CI failure

This is much more token-efficient than continuously restating the whole state.

* * *

11. KEEL needs a first-class adaptive workflow engine
    =====================================================

BMAD is currently stronger here.

Its philosophy is explicitly scale-adaptive: small fixes can skip deep planning while larger efforts can invoke richer product, architecture, UX, and testing processes.

Kiro likewise supports everything from conversational fixes to quick specs to full specification-driven workflows.

KEEL currently has:
    read-only
    trivial
    standard
    emergency

Good foundation.

But those are principally governance modes.

You also need **execution archetypes**.

For example:
    BUGFIX
    FEATURE
    REFACTOR
    MIGRATION
    SECURITY
    PERFORMANCE
    DEPENDENCY
    RELEASE
    INCIDENT
    RESEARCH
    UI
    DATA
    INFRA
    API_CONTRACT
    GENERATED_CODE
    DOCUMENTATION

Each archetype should produce different obligations.

Example:
    BUGFIX

    required:
      reproduction
      root-cause evidence
      regression test
      affected path trace
      baseline comparison

while:
    DATABASE_MIGRATION

    required:
      schema diff
      forward migration
      rollback strategy
      data-loss analysis
      production-volume estimate
      compatibility window
      backup evidence

This is how KEEL becomes stack-agnostic without becoming task-agnostic.

* * *

12. Domain intelligence should be activated dynamically
    =======================================================

Stack agnosticism should **not** mean one generic process.

It should mean:

> No technology assumptions until repository evidence establishes them.

Then activate specialized contracts.

Example:
    repo discovery
       │
       ├─ detects React
       ├─ detects Playwright
       ├─ detects PostgreSQL
       ├─ detects Terraform
       └─ detects GitHub Actions
              ↓
    capability profile
              ↓
    domain contracts activated

Possible modules:
    frontend
    backend
    database
    security
    distributed systems
    mobile
    embedded
    ML
    data engineering
    IaC
    CI/CD
    release engineering
    game development
    browser automation
    accessibility
    performance

The current resolver points toward this architecture but stops at detection.

The missing layer is:
    DETECTION
       ↓
    CONTRACT SELECTION
       ↓
    WORKFLOW AUGMENTATION
       ↓
    VERIFICATION AUGMENTATION

without silently changing security policy.

* * *

13. Codebase discovery should produce executable commands
    =========================================================

Another missing surface is reliable command discovery.

An agent needs to know:
    How do I build this?
    How do I test the affected subsystem?
    How do I lint it?
    How do I run it?
    How do I launch the browser?
    How do I reproduce CI?

Static manifest detection should evolve into **Command Intelligence**.

Sources can include:
    package scripts
    Make targets
    justfiles
    taskfiles
    CI definitions
    Docker Compose
    Cargo metadata
    Gradle tasks
    dotnet solutions
    tox/nox
    pytest config
    README examples
    historical successful KEEL runs

Then KEEL can maintain:
    commands:
      test.unit:
      test.integration:
      test.browser:
      lint:
      typecheck:
      build:
      run:
      package:

with evidence and confidence.

* * *

14. Your current verification configuration is not portable
    ===========================================================

This is a concrete defect in the uploaded archive.

`.keel/config.json` contains required commands referencing:
    C:/Users/click/.agents/skills/codex-control-plane-bootstrapper/...

and:
    C:/Users/click/.codex/skills/.system/skill-creator/...

Those paths also appear repeatedly inside historical ledger verification artifacts.

That means the current package cannot be copied to another developer machine and retain its canonical verification contract.

For a framework whose goal is:

> completely stack-agnostic and ready for any engineering task

this is a P0 productization issue.

The correct model is one of:
    repository-owned validator

or:
    resolved capability:
      executable:
      discovery:
      version constraint:

Never:
    absolute creator-machine path

Canonical verification must be hermetic enough to reproduce.

* * *

15. Extracted-package behavior exposes another portability issue
    ================================================================

I executed all repository-local deterministic test scripts against the archive.

Most passed.

Two failed:
    test_developer_ux.py
    test_upgrade_kernel.py

because the extracted archive lacks `.git`.

The second failure specifically reaches:
    git status --short

with `check=True`, causing an exception.

`keel.py doctor`, `keel.py init --check`, and `keel.py version` likewise refuse operation because the extracted directory is not a Git repository.

Some commands absolutely should require Git.

But bootstrap/introspection commands need clearer separation between:
    UNINITIALIZED
    NOT_A_GIT_REPOSITORY
    BOOTSTRAPPABLE
    ACTIVE
    BROKEN

rather than treating all of those as fatal runtime states.

The installer should be able to inspect and bootstrap a directory before a valid repository lifecycle exists.

* * *

16. Build a real installation and upgrade system
    ================================================

Competitors are substantially ahead here.

BMAD provides:
    npx bmad-method install

with stable/next/pinned channels, non-interactive CI installation, tool integrations, configuration overrides, and upgrade behavior.

OpenSpec exposes straightforward installation and project updates.

Spec Kitty provides explicit installation and upgrade documentation and a user-facing CLI.

KEEL needs something equivalent to:
    keel init
    keel install
    keel doctor
    keel adopt
    keel upgrade
    keel migrate
    keel uninstall
    keel repair

with:
    dry-run
    diff preview
    backup
    rollback
    version pinning
    compatibility matrix
    schema migration
    Codex capability detection

The current migration engine is a good seed, but it is not yet a framework distribution system.

* * *

17. Upgrade compatibility needs a broader contract
    ==================================================

The current migration implementation principally recognizes a config schema migration:
    config 1 → 2

A mature KEEL will need versioned contracts for:
    framework
    ledger
    mission
    requirements
    acceptance
    effects
    authorization
    verification
    repository-map
    capability registry
    context packet
    telemetry
    hook definitions
    agent definitions
    skills
    benchmark corpus

Each should have:
    schema_version
    minimum_reader_version
    migration path
    forward compatibility behavior
    unknown-field policy

This becomes critical once KEEL is installed across real repositories.

* * *

18. Runtime capability detection must replace static Codex assumptions
    ======================================================================

Your documentation correctly says generated `.codex/` files do not prove runtime activation.

Excellent.

Preserve that principle.

But take it further.

Codex is evolving quickly: multi-agent support, worktrees, skills, automation, model routing, and other surfaces change frequently. Current OpenAI materials explicitly emphasize shared repository guidance, approvals, sandboxing, MCP/tool connections, skills, automations, and worktrees as team-level Codex primitives.

Therefore KEEL should establish:
    Codex Capability Handshake

at runtime.

Example:
    {
      "codex": {
        "version": "...",
        "features": {
          "subagents": true,
          "worktrees": true,
          "skills": true,
          "hooks": true,
          "mcp": true
        }
      }
    }

Any unavailable feature should degrade gracefully.

Never infer support merely from config files.

* * *

19. Your topology router is too primitive
    =========================================

Current routing approximately maps:
    risk + dependency count

to:
    roles + effort + verification breadth

That is a reasonable v0.

But it ignores:
    task type
    codebase familiarity
    blast radius
    test coverage
    architecture depth
    uncertainty
    security exposure
    novelty
    history of failures
    token budget
    latency constraints
    model strengths
    parallelizability

Zenflow already exposes phase-specific model/agent assignment and cross-model review, including isolated subagents and parallel reviewers.

KEEL should eventually route on a richer feature vector:
    work profile
          ↓
    complexity classifier
          ↓
    capability requirements
          ↓
    agent topology
          ↓
    model profile
          ↓
    verification depth

For example:
    simple localized edit
        → single executor + deterministic verify

    uncertain bug
        → explorer → executor → verifier

    cross-cutting refactor
        → architecture explorer
          + dependency explorer
          → planner
          → isolated implementers
          → reviewer
          → verifier

    security-sensitive migration
        → threat reviewer
          + migration specialist
          → executor
          → independent adversarial reviewer
          → full verifier

* * *

20. Cross-model review should become optional policy
    ====================================================

Zenflow makes a compelling point: independent reviewers using different models may catch different error classes than the implementation model.

KEEL's conceptual separation of:
    executor
    verifier
    reviewer
    risk-reviewer

is already ideal for this.

Add policy such as:
    review:
      independence: required
      model_diversity: preferred

for high-risk changes.

Do not hard-code vendor/model names into the core framework.

Define capabilities instead:
    FAST_EXECUTOR
    DEEP_REASONER
    SECURITY_REVIEWER
    VISUAL_REVIEWER
    LOW_COST_EXPLORER

Adapters resolve those capabilities.

* * *

21. Make the Context Compiler topology-aware
    ============================================

Different agents should receive different context.

Currently the system is moving toward one bounded context compiler.

It should become role-sensitive:
    Explorer Context
        architecture + relevant code + history

    Planner Context
        intent + exploration findings + constraints

    Executor Context
        exact scope + contracts + implementation references

    Verifier Context
        acceptance contract + diff + test surfaces

    Risk Reviewer Context
        effects + trust boundaries + threat surfaces

That prevents context overload.

GSD's fresh-context approach exists precisely to resist accumulated context degradation.

* * *

22. KEEL's Evidence Graph is promising but needs typed assertions
    =================================================================

The current provider vocabulary is a good starting point:
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
    changed_path

But eventually the graph needs assertions stronger than:
    check exited zero

Examples:
    provider: browser
    assert:
      selector_visible: "#dashboard"

    provider: metric_query
    assert:
      p95_latency_ms:
        lt: 200

    provider: schema
    assert:
      backward_compatible: true

    provider: benchmark
    assert:
      regression_percent:
        lt: 3

    provider: security
    assert:
      critical_findings: 0

Then acceptance criteria become executable contracts rather than aliases for commands.

* * *

23. Verification should become change-aware
    ===========================================

Running every canonical check every time will eventually become expensive.

KEEL already knows:
    changed paths
    repository graph
    capabilities
    requirements
    risk

Therefore it can construct:
    minimum sufficient verification set

Example:
    changed authentication service
           ↓
    dependent modules
           ↓
    related integration tests
           ↓
    security checks
           ↓
    API contract checks

For high risk, expand outward.

For trivial changes, narrow inward.

This produces something much better than blindly running a fixed verification list.

* * *

24. Verification commands need discovery + provenance
    =====================================================

Each verification command should eventually have:
    id:
    argv:
    source:
    version:
    applies_when:
    scope:
    required:
    timeout:
    environment:
    provenance:

Example:
    id: frontend-playwright
    source: package.json/scripts
    applies_when:
      capability: ui-browser
      paths:
        - src/ui/**

This would make KEEL genuinely stack-neutral.

* * *

25. Developer UX is currently far behind the architecture
    =========================================================

This may become KEEL's adoption bottleneck.

Today the conceptual user experience includes commands like:
    keel start
    keel gate discuss
    keel gate plan
    keel verify
    keel seal
    keel candidate-status
    keel anchor

Technically sound.

But users should rarely need to understand all of that.

BMAD's `bmad-help` explicitly recommends what the user should do next.

Spec Kitty exposes a visible workflow.

Kiro presents specs, tasks, hooks, agents, and project context as integrated product surfaces.

KEEL needs a first-class:
    keel

command that answers:
    What am I doing?
    What state am I in?
    What blocks me?
    What happens next?
    What requires my approval?
    What is running?
    What failed?
    What can run concurrently?

For example:
    KEEL · auth-redesign

    MISSION
    3 / 7 changes landed

    RUNNING
    △ refresh-token-storage    VERIFY

    READY
    ○ login-ui                  STANDARD
    ○ logout-api                TRIVIAL

    BLOCKED
    × mobile-auth               waits: refresh-token-storage

    AUTHORIZATION
    ! production migration      REQUIRED

    NEXT
    keel run

That experience would radically improve adoption.

* * *

26. Build `keel run`
    ====================

The framework currently exposes many primitives.

What it needs is orchestration over them.

Conceptually:
    keel run <objective>

should:

1. inspect repository;

2. determine whether read-only/trivial/change/mission is appropriate;

3. construct or update the work contract;

4. gather missing decisions;

5. build the work graph;

6. schedule safe work;

7. create worktrees;

8. launch appropriate agents;

9. verify outputs;

10. request authorization only where required;

11. seal candidates;

12. integrate according to configured policy;

13. verify the mission;

14. present final evidence.

Advanced users keep direct commands.

Ordinary users get a coherent front door.

* * *

27. Do not require ceremony for obvious changes
    ===============================================

OpenSpec's explicit philosophy is:
    fluid not rigid
    iterative not waterfall
    easy not complex
    brownfield-friendly

and it positions reduced ceremony as a design advantage.

That criticism could eventually be aimed directly at KEEL.

Your trivial mode helps.

But adaptive ceremony must go further.

The system should infer:
    1-file docs typo
       → micro path

    simple tested bug
       → compact change

    cross-service feature
       → full change

    multi-system migration
       → mission

The user should experience **proportional governance**.

* * *

28. The framework must distinguish invariants from bureaucracy
    ==============================================================

OpenAI's own Codex Security repository has an instructive principle:

> keep protections for real risks, but do not add arbitrary checks merely because checks are possible.

That principle should become foundational to KEEL.

A mechanism deserves mandatory status only when it protects a demonstrated invariant.

Otherwise it should be:
    advisory
    conditional
    optional

This protects KEEL from becoming enterprise theater.

* * *

29. Documentation has become too large relative to the runtime
    ==============================================================

The extracted package contains roughly:
    732 files
    3.7 MB
    ~3,763 Python LOC under .keel
    41 historical ledger changes
    ~2.7 MB of ledger data

The ratio is revealing.

There is a substantial governance/documentation surface around a relatively compact runtime.

That is not intrinsically bad, but it creates entropy risk.

KEEL should eventually compile much of its human documentation from machine-readable contracts.

For example:
    contracts
       ↓
    generated docs
       ↓
    CLI help
       ↓
    agent context

instead of maintaining all of them separately.

* * *

30. Separate framework history from consumer-repository state
    =============================================================

Shipping 41 internal KEEL development ledgers inside a reusable project control plane is useful as provenance for KEEL itself.

It is less desirable for a consumer project.

A distributed KEEL package should distinguish:
    KEEL framework source/history

from:
    project-local KEEL state

Otherwise every new adopter inherits KEEL's own construction history.

A clean bootstrap should probably contain:
    .keel/
      runtime/
      schemas/
      config/
      templates/
      state/

with no framework-development ledger unless explicitly installed as examples.

* * *

31. KEELBench is strategically vital
    ====================================

The strongest architectural feature you can build after orchestration may actually be the evaluation system.

You already have a 12-scenario corpus:
    bugfix
    feature
    refactor
    dependency
    migration
    security
    frontend
    performance
    brownfield
    multiservice
    release
    recovery

and paired baseline-vs-KEEL trial semantics.

Excellent.

But currently it is mostly an evaluation contract, not evidence of advantage.

This is the biggest credibility gap.

You cannot meaningfully say:

> KEEL is better than BMAD/GSD/Spec Kit/etc.

until you run reproducible evaluations.

* * *

32. Build KEELBench into a serious benchmark
    ============================================

Measure at least:

### Correctness

    acceptance pass rate
    regression rate
    hidden-test pass rate
    requirement coverage

### Efficiency

    tokens
    wall-clock time
    tool calls
    iterations
    agent runs

### Human burden

    clarifications
    approvals
    interventions
    manual corrections

### Process quality

    scope violations
    unauthorized effects
    merge conflicts
    failed integrations
    rework

### Engineering quality

    maintainability
    architecture compliance
    security findings
    test quality

### Recovery

    time to recover
    number of failed attempts
    rollback success

Then compare:
    bare Codex
    Codex + AGENTS
    GSD
    BMAD
    Spec Kit
    OpenSpec
    Superpowers
    KEEL

where licenses/tooling permit meaningful controlled trials.

Without this, "superior" remains branding.

With it, superiority becomes measurable.

* * *

33. Make evaluations adversarial
    ================================

Ordinary feature tasks are not enough.

KEEL's governance advantages should appear most clearly in difficult cases:
    ambiguous requirements
    dirty working tree
    pre-existing test failure
    malicious repository instructions
    hidden dependency
    generated file
    out-of-scope tempting fix
    failing flaky test
    migration requiring rollback
    secret accidentally exposed
    deployment command
    scope expansion halfway through work
    conflicting documentation
    parallel agents touching same subsystem
    post-verification modification

These cases test exactly what KEEL claims to improve.

* * *

34. Add mutation tests for the control plane itself
    ===================================================

KEEL is sufficiently safety/integrity-oriented that normal unit tests are not enough.

Mutate:
    gate predicates
    scope checks
    digest comparisons
    authorization binding
    Git ancestry logic
    effect matching
    acceptance evaluation

If mutants survive, you have blind spots in the governance layer.

Given KEEL's positioning, this should become mandatory for security-critical invariants.

* * *

35. Build property-based tests around lifecycle invariants
    ==========================================================

Useful invariants include:
    A sealed candidate can never reference an unverified material state.

    Replanning invalidates incompatible authorization.

    A scope-restricted change cannot verify with undeclared changed paths.

    Anchoring cannot succeed when candidate material changed.

    A landed state cannot precede a sealed candidate.

    Mission nodes cannot execute before hard dependencies land.

    No migration can silently discard unknown schema fields unless policy permits.

Property testing these state machines would substantially increase confidence.

* * *

36. Treat the lifecycle as a formal state machine
    =================================================

Instead of distributing state transitions across command implementations, define:
    DISCUSS
    PLAN
    EXECUTE
    VERIFY
    SHIP
    SEALED
    LANDED
    CLOSED

and transition guards centrally.

Then test the transition table exhaustively.

This could later enable model checking.

KEEL's value proposition warrants that rigor.

* * *

37. Effects need a richer ontology
    ==================================

The current effect list is good but too coarse.

Expand toward:
    git.remote.push
    git.remote.force_push
    vcs.pr.create
    vcs.pr.merge
    vcs.branch.delete

    database.schema.migrate
    database.data.mutate
    database.drop

    cloud.deploy.staging
    cloud.deploy.production
    cloud.resource.create
    cloud.resource.delete

    infra.plan
    infra.apply
    infra.destroy

    secret.read
    secret.write
    secret.rotate

    package.publish
    package.yank

    issue.create
    issue.modify
    issue.close

    messaging.send
    email.send

Capability hierarchy enables policies like:
    cloud.deploy.*

without enumerating every provider.

* * *

38. Effect inference must operate on tool semantics, not just argv
    ==================================================================

Current `effect_inference.py` recognizes commands such as:
    git push
    git merge
    terraform apply
    kubectl apply
    alembic upgrade

Useful.

But modern agents invoke MCP tools, APIs, GitHub integrations, cloud connectors, database tools, and browser actions.

Kiro's current hook model explicitly exposes hooks around both built-in tools and MCP tool names.

KEEL needs:
    Effect Adapter Registry

for:
    shell
    GitHub
    GitLab
    AWS
    Azure
    GCP
    Kubernetes
    database
    MCP
    email
    issue trackers
    package registries

Each adapter maps provider actions into KEEL's provider-neutral effect ontology.

* * *

39. Build environment reproducibility into the candidate
    ========================================================

Verification currently binds code/intention.

Eventually it should also capture a reproducibility envelope:
    OS
    architecture
    runtime versions
    dependency lock digests
    tool versions
    container image
    environment fingerprint

Not necessarily for every trivial change.

But for consequential builds/releases this becomes important.

Otherwise:
    same commit
    ≠
    same verified environment

* * *

40. Supply-chain attestation is a natural extension
    ===================================================

The seal mechanism could eventually create an attestation roughly equivalent to:
    candidate SHA
    intent digest
    verification digest
    environment digest
    dependency digest
    toolchain digest

That could map naturally into signed provenance systems later.

This would make KEEL relevant not merely to agent workflow but software supply-chain integrity.

* * *

41. Brownfield adoption needs explicit intelligence
    ===================================================

OpenSpec deliberately emphasizes brownfield usability.

KEEL's clean-room architecture is strong.

But real adoption means entering repositories containing:
    undocumented commands
    weak tests
    architecture drift
    dirty state
    legacy scripts
    conflicting docs
    generated artifacts
    partial CI
    multiple languages

A first-run:
    keel adopt

should produce:
    repository profile
    architecture map
    command registry
    capability profile
    test profile
    risk surfaces
    documentation gaps
    generated-artifact registry
    recommended KEEL configuration

without initially modifying anything.

Then:
    keel adopt --apply

creates only accepted scaffolding.

That would be a major competitive feature.

* * *

42. Project context should be continuously refreshed
    ====================================================

Kiro explicitly treats persistent project knowledge as a reusable steering surface.

KEEL should go further:
    repository changes
          ↓
    knowledge diff
          ↓
    derived repository map
          ↓
    staleness detection

If a new runtime, database, or package manager appears, KEEL should notice.

But the result remains advisory until policy/config explicitly adopts it.

That preserves the no-silent-policy principle.

* * *

43. Self-improvement is architecturally present but functionally deferred
    =========================================================================

`feedback_entropy.py` currently emits target plans whose execution is:
    DEFERRED

Yet this area could become another differentiator.

The full loop should be:
    agent failure
    human correction
    production incident
    review comment
    CI regression
          ↓
    normalize observation
          ↓
    cluster repeated pattern
          ↓
    determine root class
          ↓
    create regression eval
          ↓
    prove failure
          ↓
    propose harness improvement
          ↓
    run baseline vs candidate
          ↓
    adopt only if statistically/materially better

This is exactly the direction implied by OpenAI's harness-engineering approach: recurring failures should become improvements to the environment and mechanical feedback loops rather than repeated human reminders.

* * *

44. Do not automatically convert every mistake into policy
    ==========================================================

This is critical.

An autonomous self-improvement system can ossify quickly.

Require repeated evidence.

For example:
    ONE failure
        → observation

    REPEATED related failures
        → candidate pattern

    REPRODUCIBLE eval
        → candidate intervention

    MEASURED improvement
        → promoted invariant

That prevents rule explosion.

* * *

45. Introduce a Policy Compiler
    ===============================

Today policy exists across:
    AGENTS.md
    WORKFLOW.md
    .keel/config.json
    contracts.json
    hooks
    templates
    docs

Long term, many rules should derive from a smaller declarative policy source.

For example:
    risk:
      high:
        require:
          - independent_review
          - full_verification

    effects:
      cloud.deploy.production:
        authorization: explicit

    parallelism:
      same_paths: forbidden

Then compile that into:
    hook logic
    CLI checks
    agent guidance
    documentation

This greatly reduces drift.

* * *

46. Introduce invariant ownership
    =================================

Every enforced rule should answer:
    What failure does this prevent?
    Who owns it?
    How is it tested?
    What evidence justified it?
    Can it be removed?

Example:
    invariant: sealed-candidate-digest
    reason: prevent post-verification material drift
    owner: keel-core
    tests:
      - ...
    introduced_by:
      - incident/eval reference

This turns governance into maintainable engineering.

* * *

47. Architecture enforcement needs executable dependency rules
    ==============================================================

You already document architecture enforcement.

The next step is auto-discovery + mechanical checking.

Examples:
    domain cannot import infrastructure
    UI cannot access database
    core cannot depend on web framework
    generated files cannot be manually edited

Adapters could produce:
    dependency-cruiser
    ArchUnit
    NetArchTest
    cargo-deny/custom lint
    go list analysis
    Python import graph
    Bazel queries

Again:
    stack detection
        ↓
    appropriate invariant adapter

* * *

48. Build "change impact analysis"
    ==================================

Before execution, KEEL should be able to answer:
    You plan to modify X.

    Likely impacted:
      Y
      Z

    Tests:
      A
      B

    Interfaces:
      C

    Owners:
      team-D

    Deployment:
      service-E

This is one of the highest-leverage functions possible for autonomous coding.

It combines repository graph + Git history + test mapping.

* * *

49. Learn from Git history
    ==========================

The repository itself contains valuable implicit engineering knowledge.

Mine:
    files commonly changed together
    tests commonly changed with implementation
    modules causing regressions
    revert frequency
    review hotspots
    ownership
    historical migration patterns

This should inform:
    scope suggestions
    risk classification
    context compilation
    verification selection

Never turn history directly into mandatory policy without validation.

* * *

50. Risk should become evidence-derived
    =======================================

Currently risk is largely declared.

Long term:
    risk = f(
      effect severity,
      dependency fanout,
      data sensitivity,
      changed criticality,
      coverage,
      architecture centrality,
      migration presence,
      external interfaces,
      historical failure rate
    )

The agent can propose the risk level.

Policy sets the minimum.

The user can raise it.

The system should make lowering it require justification.

* * *

51. Add uncertainty explicitly
    ==============================

Engineering tasks differ not just in risk but epistemic uncertainty.

Introduce something like:
    LOW
    MEDIUM
    HIGH
    UNKNOWN

High uncertainty should trigger:
    more exploration
    more evidence
    smaller execution slices

rather than simply stronger verification after implementation.

This would distinguish KEEL from risk-only workflow engines.

* * *

52. Build reversible execution into planning
    ============================================

One useful planner question should be:

> What is the smallest reversible step that increases knowledge?

For uncertain engineering:
    investigate
    → reproduce
    → instrument
    → write characterization test
    → implement

is often superior to:
    plan entire solution
    → execute

KEEL's delta architecture supports this naturally.

* * *

53. Add experiment changes
    ==========================

Not every change should be treated as production intent.

Introduce:
    EXPERIMENT

where:
    learning objective
    hypothesis
    measurement
    cleanup policy

matter more than permanent requirements.

This would broaden KEEL beyond standard feature engineering.

* * *

54. Verification should include semantic diff review
    ====================================================

Textual changed paths are necessary but insufficient.

A verification layer could classify:
    public API changes
    schema changes
    permission changes
    dependency changes
    configuration changes
    test removal
    generated artifacts
    security controls

A change touching:
    authentication permissions

deserves stronger review even if it is only three lines.

* * *

55. Protect verification quality itself
    =======================================

Agents can game weak tests unintentionally.

Examples:
    delete failing assertion
    mock away behavior
    relax threshold
    skip test
    weaken type

KEEL should detect suspicious verification-surface changes.

For important changes:
    test changed?
        ↓
    independent review required

Especially when acceptance evidence depends on that test.

* * *

56. Require independent verification where the executor controls the oracle
    ===========================================================================

General rule:
    If the implementation agent also changes the mechanism used to prove success,
    increase verification independence.

That is a powerful generic invariant.

* * *

57. Detect scope laundering
    ===========================

Agentic systems sometimes discover an undeclared requirement and silently expand the implementation.

KEEL already requires replan.

Strengthen this by measuring:
    scope expansion
    requirement expansion
    effect expansion

after Plan.

Unexpected expansion should become telemetry.

That metric can reveal poorly specified planning.

* * *

58. The main CLI needs structured output everywhere
    ===================================================

Every command should support:
    --json

with stable schemas.

That makes KEEL usable by:
    Codex
    CI
    Symphony-like orchestrators
    IDE integrations
    web dashboards
    third-party agents

Human-readable CLI output should be a rendering layer over the API.

* * *

59. Treat the CLI as an API
    ===========================

Long-term layering:
    KEEL DOMAIN LIBRARY
            ↑
        JSON API
            ↑
          CLI
            ↑
    ┌───────┼────────┐
    Codex   IDE      CI

Avoid encoding important behavior inside command-printing paths.

* * *

60. Build event sourcing around important lifecycle transitions
    ===============================================================

You already have JSONL audit artifacts.

Expand this into an append-only lifecycle event stream:
    {
      "event": "PLAN_PASSED",
      "change": "...",
      "timestamp": "...",
      "intent_digest": "...",
      "actor": "...",
      "evidence": [...]
    }

Derived state can then be reconstructed.

Benefits:
    audit
    debugging
    telemetry
    replay
    forensics

* * *

61. Add correlation IDs across agents and tools
    ===============================================

Mission:
    mission_id

Change:
    change_id

Agent run:
    run_id

Tool invocation:
    operation_id

Evidence:
    evidence_id

These should propagate throughout the system.

Then KEEL can answer:
    Which agent created this?
    Which requirement caused the edit?
    Which verification covered it?
    Which mission required it?

* * *

62. Build a local dashboard eventually — but not yet
    ====================================================

Spec Kitty's visible dashboard is valuable.

Kiro's integrated environment is valuable.

Conductor's workspace model is valuable.

KEEL will eventually benefit from a visual surface.

But do **not** build it before the orchestration API.

Correct order:
    domain/runtime
        ↓
    stable event/state API
        ↓
    CLI
        ↓
    dashboard

Otherwise the UI will fossilize premature concepts.

* * *

63. Product positioning should change
    =====================================

Avoid:

> better Spec Kit.

Prefer:

> **KEEL is a stack-agnostic engineering control plane for autonomous coding agents.**

Or more specifically:

> **KEEL turns engineering intent into isolated, governed, verifiable work and proves exactly what was authorized, implemented, tested, and landed.**

That communicates the actual differentiator.

* * *

64. Competitive comparison
    ==========================

GSD
---

Strong at:
    context isolation
    decomposition
    fresh-agent execution
    planning loops

KEEL advantage:
    governance
    effects
    verification provenance
    sealed candidates

KEEL must steal:
    context lifecycle
    decomposition ergonomics
    fresh execution agents

GSD's explicit focus on context rot is worth taking seriously.

* * *

BMAD
----

Strong at:
    product thinking
    planning ergonomics
    specialized personas
    scale adaptation
    workflow catalog
    developer onboarding

KEEL advantage:
    mechanical integrity
    Git provenance
    effect controls
    candidate verification

KEEL must steal:
    adaptive workflow selection
    user guidance
    domain workflow libraries
    product/design reasoning

BMAD's current ecosystem includes 34+ workflows and specialist modules, which highlights how far KEEL still has to go in workflow breadth.

* * *

Spec Kit
--------

Strong at:
    specification discipline
    artifact workflow
    cross-artifact reasoning
    tool portability

Its documented default workflow is explicitly structured around Spec → Plan → Tasks → Implement.

KEEL advantage:
    post-plan governance
    execution integrity
    effects
    Git sealing

Steal:
    spec ergonomics
    artifact analysis
    onboarding simplicity

* * *

Spec Kitty
----------

Strong at:
    mission/work-package execution
    worktrees
    next/review/accept/merge loop
    multi-agent factory model
    dashboard

KEEL advantage:
    verification integrity
    effects authorization
    stronger candidate provenance

Steal aggressively:
    mission UX
    work-package scheduling
    parallel execution
    operator visibility

This is probably KEEL's closest architectural competitor.

* * *

OpenSpec
--------

Strong at:
    low ceremony
    brownfield usability
    fluid artifact editing
    multi-agent compatibility

KEEL advantage:
    mechanical enforcement
    traceability
    verification

Steal:
    simplicity
    fast-path ergonomics
    brownfield adoption

OpenSpec's philosophy should serve as a constant warning against over-governing KEEL.

* * *

Tessl
-----

Strong at:
    specification-to-test relationship
    intent preservation
    requirements before implementation

Its core argument is closing the "intent-to-code chasm" through reviewed specifications.

KEEL already goes further downstream.

Steal:
    spec/test synchronization

* * *

Kiro
----

Strong at:
    integrated UX
    repository indexing
    steering
    specs
    hooks
    custom agents
    skills
    subagents
    cross-surface continuity

Kiro now presents a unified harness across IDE, CLI, Web, and Mobile with specs, steering, hooks, permissions, skills, subagents, checkpoints, and compaction.

This is the clearest reminder that KEEL cannot compete purely as Markdown + Python scripts.

Steal:
    context UX
    hooks model
    continuous project understanding
    operator experience

* * *

Superpowers
-----------

Strong at:
    brainstorming
    design-first development
    TDD
    subagent execution
    focused composable skills

Its methodology explicitly forces design clarification before planning and uses subagent-driven implementation afterward.

KEEL advantage:
    formal governance
    verification provenance
    effect boundaries

Steal:
    skill simplicity
    TDD discipline
    focused agent transitions

* * *

Traycer
-------

Strong at:
    file-level plans
    phase mode
    agent handoff
    implementation verification

Traycer specifically frames plans as executable guides for other agents and provides verification against those plans.

Steal:
    plan visualization
    verification feedback ergonomics

* * *

Conductor
---------

Strong at:
    parallel workspace UX
    worktree isolation
    agent-session ownership
    review flow

KEEL has the invariant.

Conductor has the product experience.

Steal the experience, not necessarily the implementation.

* * *

Zencoder / Zenflow
------------------

Strong at:
    multi-repository context
    workflow definitions
    model routing
    cross-model verification
    subagent orchestration

Zenflow's explicit ability to assign different agents/models to planning, implementation, and review is particularly relevant to KEEL's topology router.

Steal:
    capability-based model routing
    cross-model review
    multi-repo intelligence

* * *

65. The architecture I would target
    ===================================
    
                             USER OBJECTIVE
                                    │
                                    ▼
                         ┌────────────────────┐
                         │ Intent Interpreter │
                         └─────────┬──────────┘
                                   │
                                   ▼
                      ┌──────────────────────────┐
                      │ Repository Intelligence  │
                      │ Graph + Capability State │
                      └────────────┬─────────────┘
                                   │
                                   ▼
                          ┌────────────────┐
                          │ Workflow Router│
                          └────────┬───────┘
                                   │
                      ┌────────────┴────────────┐
                      │                         │
                SINGLE CHANGE                MISSION
                      │                         │
                      │                  ┌──────▼──────┐
                      │                  │ Work Graph  │
                      │                  └──────┬──────┘
                      │                         │
                      └──────────────┬──────────┘
                                     ▼
                        ┌────────────────────────┐
                        │ Context Compiler       │
                        │ + Impact Analysis      │
                        └────────────┬───────────┘
                                     │
                                     ▼
                          ┌────────────────────┐
                          │ Topology / Model   │
                          │ Capability Router  │
                          └─────────┬──────────┘
                                    │
                        ┌───────────┴─────────────┐
                        ▼                         ▼
                   EXPLORERS                 REVIEWERS
                        │                         │
                        └───────────┬─────────────┘
                                    ▼
                             EXECUTION AGENTS
                                    │
                                    ▼
                          ┌────────────────────┐
                          │ KEEL Change Ledger │
                          └─────────┬──────────┘
                                    │
                                    ▼
                         Scope / Effect Guards
                                    │
                                    ▼
                           Verification Graph
                                    │
                                    ▼
                            Candidate Seal
                                    │
                                    ▼
                             Integration
                                    │
                                    ▼
                           Landed Verification
                                    │
                                    ▼
                              Mission Verify
                                    │
                                    ▼
                             Telemetry / Eval
                                    │
                                    ▼
                        Feedback / Entropy Loop
                                    │
                                    └───────► Harness improvement

That would be a formidable architecture.

* * *

66. Proposed KEEL architectural layers
    ======================================

I would formalize six major subsystems.
KEEL Core
---------

Immutable concepts:
    changes
    states
    requirements
    acceptance
    effects
    authorization
    verification
    sealing
    anchoring

This should remain small and extremely well tested.

* * *

KEEL Intelligence
-----------------

Derived understanding:
    repository graph
    capability detection
    impact analysis
    command discovery
    test mapping
    context compilation
    risk inference

No permission authority.

* * *

KEEL Planner
------------

Transforms objectives into executable contracts:
    workflow selection
    requirements
    architecture decisions
    change decomposition
    mission graph

* * *

KEEL Runtime
------------

Executes work:
    worktrees
    subagents
    agent topology
    retries
    scheduling
    integration

* * *

KEEL Adapters
-------------

Provider/stack-specific behavior:
    Codex
    GitHub
    GitLab
    Node
    Python
    Rust
    .NET
    Java
    Docker
    Kubernetes
    AWS
    databases
    browser

Core remains provider-neutral.

* * *

KEEL Learning
-------------

Measures whether the framework works:
    telemetry
    benchmarks
    feedback
    failure clustering
    eval generation
    harness promotion

* * *

67. Recommended priority order
    ==============================

Do **not** implement everything simultaneously.
P0 — Portability and runtime correctness
----------------------------------------

Fix immediately:
    absolute local paths
    non-Git bootstrap behavior
    hermetic self-validation
    runtime capability handshake
    version compatibility

Because every later benchmark becomes questionable if the framework itself cannot reproduce cleanly elsewhere.

* * *

P1 — Repository Intelligence Graph
----------------------------------

Build:
    symbol/module graph
    dependency graph
    test mapping
    command discovery
    impact analysis
    ownership/provenance

This improves almost every downstream decision.

* * *

P2 — Mission Runtime
--------------------

Convert:
    mission_graph execution = DEFERRED

into an actual scheduler:
    frontier
    → worktrees
    → agents
    → verify
    → review
    → seal
    → integrate
    → next frontier

This is the most important competitive feature.

* * *

P3 — Adaptive Workflow Engine
-----------------------------

Add:
    bugfix
    feature
    refactor
    migration
    security
    release
    performance
    incident

with domain-specific obligations.

* * *

P4 — Topology and Model Capability Router
-----------------------------------------

Route:
    task
    → roles
    → context
    → model capability
    → verification policy

Avoid hard-coding model brands.

* * *

P5 — Developer UX
-----------------

Create:
    keel
    keel run
    keel status
    keel adopt

with a clean dashboard-like terminal experience.

* * *

P6 — Verification intelligence
------------------------------

Build:
    typed assertions
    change-aware checks
    impact-derived verification
    oracle independence checks
    semantic diff classification

* * *

P7 — Self-improvement loop
--------------------------

Operationalize:
    observation
    → failure cluster
    → eval
    → intervention
    → benchmark
    → promotion

* * *

P8 — Productization
-------------------

Add:
    installer
    version pinning
    upgrade channels
    migration system
    plugin/adapter packaging
    team distribution

* * *

68. One rule I would impose now
    ===============================

Every future KEEL feature should have to answer:

> **Does this measurably improve correctness, autonomous capability, engineering efficiency, or human oversight?**

If not, don't add it.

KEEL's biggest strategic danger is not missing sophistication.

It is **process accretion**.

Because your framework already contains unusually strong governance primitives, it would be very easy to confuse additional mechanisms with additional capability.

The next phase should optimize:
    less human work
    more agent autonomy
    better decisions
    stronger evidence
    fewer failures

not:
    more files
    more gates
    more templates

* * *

69. The metric that should define KEEL
    ======================================

I would eventually define a composite metric such as:
    Verified Engineering Yield

Conceptually:
    VEY =
    verified accepted changes
    ──────────────────────────
    human effort × compute cost × elapsed time

subject to hard penalties for:
    regressions
    scope violations
    unauthorized effects
    security failures
    rework

That would give KEEL a measurable optimization objective.

You do not want:

> maximum agent activity.

You want:

> **maximum trustworthy engineering output per unit of supervision and compute.**

That is a much stronger thesis.

* * *

70. Final assessment
    ====================

KEEL v2 is not yet superior to all of the systems you named.

But it **does possess a core idea that could make it superior in an important way**.

GSD is currently stronger at context-driven execution.

BMAD is stronger at lifecycle breadth and planning experience.

Spec Kit is stronger at specification UX.

Spec Kitty is stronger at mission orchestration.

OpenSpec is stronger at low-friction adoption.

Kiro is vastly stronger as an integrated product.

Conductor is stronger at parallel-agent workspace UX.

Zenflow is stronger at agent/model orchestration.

Superpowers is stronger at focused skill methodology.

Yet none of those advantages invalidate KEEL.

KEEL's distinctive foundation is:
    INTENT
      +
    SCOPE
      +
    RISK
      +
    EFFECTS
      +
    AUTHORIZATION
      +
    EVIDENCE
      +
    EXACT GIT STATE

bound into one verifiable lifecycle.

That is exactly the kind of control plane that becomes more valuable as coding agents become **more autonomous**, not less.

The strategic path therefore is not to imitate every competitor.

It is to combine:
    GSD's context discipline

    + BMAD's adaptive planning

    + Spec Kit's intent ergonomics

    + Spec Kitty's mission runtime

    + OpenSpec's low ceremony

    + Kiro's repository intelligence and UX

    + Superpowers' composable execution skills

    + Conductor's isolated parallelism

    + Zenflow's model/agent routing

    + KEEL's own verification and authorization substrate

into one coherent system.

If executed correctly, KEEL stops being a "Codex project setup."

It becomes:

> **a stack-independent operating system for trustworthy autonomous software engineering.**

That is ambitious enough to justify the architecture you have already built.

The first implementation wave I would pursue is **P0 portability → Repository Intelligence Graph → executable Mission Runtime**. Those three changes would eliminate the clearest weaknesses I found and move KEEL from an unusually rigorous governance framework toward a genuinely autonomous engineering system.

71. Supplied competitive-audit reconciliation
   =============================================

The supplied competitive architecture audit confirms the direction above and adds four immediate trust-boundary findings that must remain explicit in the roadmap:

* Canonical verification must be portable. Required validators may not depend on creator-machine absolute paths; they must resolve to repository-owned or discoverable, version-constrained capabilities.
* Effect enforcement must cover the complete tool surface. Shell/apply-patch matching is not sufficient when MCP and function tools can perform consequential work. A Tool Capability Registry should classify structured invocations, fail closed for unknown mutating tools during protected work, and keep Codex rules as a complementary shell-enforcement lane.
* Framework distribution must be separated from framework-development history. Consumer installs should not inherit the framework repository's historical ledger archaeology.
* Hook configuration is not runtime proof. Installation, project trust, hook activation, compatibility, and failure behavior require an observable capability/guardrail handshake; configuration presence alone must never be reported as active enforcement.

The audit also makes the execution gap concrete. Mission planning currently remains advisory where `dispatch_plan()` reports deferred execution. The target runtime is a bounded controller that uses native runtime subagents and worktrees where available, while KEEL remains responsible for intent, scope, effects, authorization, evidence, and lifecycle state:

    mission objective
        → repository intelligence and decomposition
        → dependency waves and isolated child changes
        → execute
        → deterministic verify
        → acceptance coverage and independent review
        → bounded repair/reverify
        → seal and authorized integration

The governing boundary remains:

> **KEEL decides what, why, allowed effects, and proof; the execution runtime decides how agents run; KEEL observes and validates the result.**

The intelligence layer should evolve in parallel with that runtime, but must remain advisory. Its next contracts are:

* a typed, provenance-bearing repository graph for symbols, modules, dependencies, runtime surfaces, tests, ownership, generated artifacts, and deployment/data boundaries;
* query-driven, role-specific context compilation with priority/token allocation instead of raw character truncation, preserving objective, acceptance, scope, forbidden effects, authorization, and lifecycle state as non-droppable material;
* capability-based routing using task/repository features, uncertainty, fan-out, test surface, historical outcomes, runtime capability, and cost/latency budgets—not only risk and dependency count;
* a bounded convergence loop that classifies missing, partial, contradictory, and unrequested work before creating repair work;
* domain-aware workflow obligations activated only from repository evidence, including bugfix, feature, migration, security, performance, dependency, API, UI/accessibility, infrastructure, and release work.

Finally, KEELBench must decide whether these additions help. Future evaluation should compare vanilla Codex and KEEL across representative task classes and repeated runs, measuring correctness, intent fidelity, safety, quality, autonomy, efficiency, parallelism, resilience, context quality, proof quality, adaptability, and learning value. Component ablations should identify which controls produce the uplift; architectural complexity without measurable trustworthy-engineering yield should not be promoted.

The consolidated strategic sequence is therefore:

    portable trust boundary
        → executable mission scheduler
        → bounded convergence
        → semantic repository/context engine
        → empirical adaptive routing and learning

This reconciliation updates the roadmap; it does not claim that any of these target capabilities are already implemented.
