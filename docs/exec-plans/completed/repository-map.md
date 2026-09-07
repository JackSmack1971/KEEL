# Repository map

## Objective

Create a compact derived view of repository structure with evidence provenance.

## Facts emitted

The map records repository-relative paths, categories, and classifier rules for topology directories, likely modules, entrypoints, tests, command/config files, and dependency manifests. It records source file count and ignored-directory rules, but does not claim semantic imports, ownership, or architecture boundaries.

## Safety

Mapping reads names and bounded manifest text only. It does not execute commands, load project code, activate capability policy, or replace authoritative architecture documents. `keel map --stdout` is read-only; `keel map` writes only the derived map artifact.

## Verification

Focused mapper tests, the existing KEEL verification graph, strict control-plane validation, and KEELBench are required.
