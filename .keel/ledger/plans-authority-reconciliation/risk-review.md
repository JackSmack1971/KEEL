# Risk review

This is a control-plane documentation change because planning authority and
active-plan discovery are affected. The mutation is repository-local and
reversible. The main risk is losing provenance or leaving ambiguous authority;
archiving complete file contents, explicit supersession headers, and negative
searches contain that risk. No runtime, test, hook, configuration, benchmark,
or P0/P4/D1 implementation surface is in scope.
