# Empty add-row grid spawn — SOLVED

Status: **SOLVED.** End-to-end recipe is codified — `scripts.kc.build_spawn_payload()` creates the row, `scripts.kc.build_write_payload()` fills it.

## Recipe
1. `kc.addable_empty_grids(form)` → list empty grid collection paths.
2. For each target value, POST `kc.update_property(kc.build_spawn_payload(path, first_cell_value))` — empty `collectionKey`/`objectKey`/`propertyKey`, collection path in `dataEntryExpression`; the server creates a GUID row and lands `value` in its first writable cell.
3. Re-read the form → fill remaining columns via `kc.build_write_payload`, keyed by the new GUID.

## Caveats
- **One spawn = one row.** Loop a known count; never loop "until no add-row remains" — the trailing UI add-box has no backing collection object and never disappears.
- **Double occurrence.** A spawned row appears in TWO collection paths: the semantic data row (`…UserEntry`, writes accepted) and a generic display row in the parent (writes 200 but no-op). De-dup by GUID; write only to the data row.

<!-- END -->
