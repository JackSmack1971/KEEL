# Risk review

This control-plane change adds declarative environment metadata and a read-only inspector. It never executes setup/start/stop commands, allocates resources, or contacts external systems. Invalid configuration is reported explicitly; no defaults are inferred.
