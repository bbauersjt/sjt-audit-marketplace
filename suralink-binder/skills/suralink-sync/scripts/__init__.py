"""suralink-sync skill — orchestration layer over the `suralink` skill.

These modules run in the Cowork Python sandbox (not the browser). They manage
the manifest, diff portal state against it, and plan where files land in the
mirror. The browser calls themselves are made by the `suralink` skill.
"""
