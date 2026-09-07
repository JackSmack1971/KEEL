# Risk review

This is a high-scrutiny control-plane planning change. It creates execution authority but does not alter `.keel/lib/`, runtime behavior, hooks, implementation tests, P1–P7 behavior, P4 authorization, or D1 artifacts. The only material repository content authorized in this turn is the single active P0 ExecPlan; KEEL lifecycle metadata is written only by repository-native commands.

The future P0 implementation is explicitly bounded to portable verification resolution, bootstrap/non-Git classification, framework/consumer artifact boundaries, and compatibility foundations. It must not guess command success, silently consume creator-machine paths, treat missing Git as generic failure for Git-independent operations, leak consumer state into packages, or claim runtime/provider evidence that is unavailable. Rollback is a normal Git revert of the implementation change; no external or irreversible effect is declared.
