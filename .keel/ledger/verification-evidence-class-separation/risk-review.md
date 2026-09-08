# Risk review

This changes the framework’s authority boundary: an incorrect result could either block legitimate work or authorize unimplemented work. The implementation is confined to the generic evidence graph and lifecycle consumers, is covered by focused regressions plus the existing control-plane suite, and is developed in an isolated worktree. No external or irreversible effect is declared. Seal and anchor remain script-owned and will independently re-read the verified committed tree.
