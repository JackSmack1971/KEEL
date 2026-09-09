# NS1 traceability remediation

Status: active
Related capability: NS1; remediation of the traceability audit for PR #12
Baseline: `8b995eb15d89862f847e9aa62f8485553b07e40f` (`8b995eb`)

## Objective

Close the three NS1 evidence gaps without changing preflight decision
semantics, RuntimeProfile integration, or the confirmed public CLI contract.

## Scope and non-goals

In scope:

- `.keel/tests/test_codex_cost_preflight.py`: named hostile scenarios,
  per-operation forbidden-call assertions, and one exception-path case.
- `.keel/tests/test_public_cli_contract.py`: preserved as the CLI regression
  boundary; no behavior change is intended.
- This record of the cp1252 baseline reproduction.

Out of scope: preflight/runtime/CLI implementation files; the attestation test
files and attestation implementation files; repairing or working around the
cp1252 failures; merging to `main`.

## Verification plan

1. Run the focused preflight and public CLI scripts and inspect that all nine
   scenario identifiers and four forbidden-operation assertions produce
   independent results, including a passing exception-path test.
2. Rerun the exact baseline reproduction commands below against this commit
   before and after the test-only change. The attestation failures must remain
   classified as pre-existing and unchanged.
3. Review `git diff --name-only` and implementation-file diffs to confirm the
   decision logic, RuntimeProfile integration, and CLI surface are untouched.
4. Run `python .keel/bin/keel.py verify`, commit the candidate, seal it, then
   run landing preparation and `python .keel/bin/keel.py land verify` against
   the resulting landing candidate. Do not integrate to `main` without
   separate authorization.

## cp1252 baseline reproduction record

This section is the durable reproduction record for the two failures that
predate this remediation. It must be updated with the observed exit status and
output after each independent rerun; no source fix is permitted here.

Environment used for the reproduction:

- OS: Windows (PowerShell)
- Python: `C:\Users\click\.local\bin\python.exe` (Python 3.14 Windows x86-64)
- Working tree: clean checkout of revision `8b995eb15d89862f847e9aa62f8485553b07e40f`
- Locale/encoding failure: Python `Path.read_text()` defaults to cp1252 in this
  environment and cannot decode byte `0x9d` in `ARCHITECTURE.md`.

Exact commands:

```powershell
git switch --detach 8b995eb15d89862f847e9aa62f8485553b07e40f
python -B .keel/tests/test_candidate_attestation.py
python -B .keel/tests/test_git_attestation_lifecycle.py
```

Observed baseline result (independently rerun on 2026-09-09):

- `test_candidate_attestation.py`: exit `1`; `UnicodeDecodeError` from
  `Path.read_text()` using `encodings.cp1252`, at `ARCHITECTURE.md` position
  `10575`, caused by byte `0x9d`.
- `test_git_attestation_lifecycle.py`: exit `1`; `Git proof tests PASS`, then
  the same child `test_candidate_attestation.py` cp1252 `UnicodeDecodeError`
  and a `subprocess.CalledProcessError`.

These are two separately invoked failing commands, with the second failure
also proving the lifecycle wrapper cannot complete because its child has the
same pre-existing decode failure. They are not acceptance failures for the
traceability test edits and must remain visible in the final handoff.
