# KEEL runtime

Repository-local deterministic change ledger and phase/scope/verification guardrails for Codex. Runtime scripts use Python 3 standard library plus Git.

Primary commands:
```sh
python3 .keel/bin/keel.py doctor
python3 .keel/bin/keel.py status
python3 .keel/bin/keel.py start <change-id>
python3 .keel/bin/keel.py gate discuss
python3 .keel/bin/keel.py gate plan
python3 .keel/bin/keel.py verify
python3 .keel/bin/keel.py replan
python3 .keel/bin/keel.py reopen
python3 .keel/bin/keel.py record-authorization --authority <who> --scope <approved-action> --evidence-reference <chat/ticket/change-record>
python3 .keel/bin/keel.py seal --change <id> --commit HEAD
python3 .keel/bin/keel.py candidate-status --change <id>
python3 .keel/bin/keel.py landing prepare --change <id> --target-ref <ref>
python3 .keel/bin/keel.py landing integrate --change <id>
```

`authorization.json` is script-owned. The Plan gate derives its required/not-required shape from `effects.json`; `record-authorization` records permission already obtained and binds it to those effects. It does not create authorization. Re-plan invalidates prior authorization. Within Codex, agent-initiated recording is blocked unless the operator has explicitly enabled the exact change in the parent environment.

`seal` is required before landing. It proves the committed candidate tree still matches the verification digest and creates `refs/keel/candidates/<id>`. `landing prepare` independently builds and verifies the target-plus-candidate integration tree; `landing integrate` protects the target with compare-and-swap and checks the actual landed tree before recording the final ref/note. `anchor` remains the compatibility path for candidate-equivalent historical landings.

Do not hand-edit `gate-log.jsonl`, `state.json`, or `verification.json` in normal operation. If KEEL itself must change, use a standard control-plane KEEL change and independent review.
