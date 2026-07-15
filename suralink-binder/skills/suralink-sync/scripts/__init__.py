"""suralink-sync skill — orchestration layer over the `suralink` skill.

These modules run in the Cowork Python sandbox (not the browser). A "sync" is a
folder: `state.py` manages its self-describing `_suralink_sync.json` (engagement
binding + what's been pulled), `index.py` snapshots what the portal holds, and
`sync.py` diffs the two and plans where files land inside the folder. There is
no global state. The browser calls themselves are made by the `suralink` skill.
"""
