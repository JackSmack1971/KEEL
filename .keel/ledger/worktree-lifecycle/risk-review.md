# Risk review

This control-plane change exposes local Git worktree mutation. Creation is reversible; retirement can remove a worktree, so the command requires an exact registered path, refuses the primary worktree, refuses dirty removal by default, and requires an explicit force flag to discard changes. No remote or external effects are introduced.
