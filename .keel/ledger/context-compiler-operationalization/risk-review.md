# Risk review

This is a control-plane change because it changes derived context packet metadata and fallback behavior used by KEEL hooks and agents. The change is local, reversible, and does not grant authorization, activate capabilities, or mutate external systems. Risk is bounded by focused deterministic tests, the existing character budget, repository-relative file selection, and strict control-plane validation. Malformed discovery is treated as untrusted derived input and falls back to resolver output.
