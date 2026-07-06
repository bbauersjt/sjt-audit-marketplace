"""suralink skill — executable operations.

Every function here returns a JavaScript string meant to be passed to
mcp__Claude_in_Chrome__javascript_tool and run inside the user's logged-in
Suralink Chrome tab. Suralink is cookie-authenticated; the Python side never
holds a token. See ../references/architecture.md.
"""
