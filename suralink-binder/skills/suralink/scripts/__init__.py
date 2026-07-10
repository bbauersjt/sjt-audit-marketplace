"""suralink skill — executable operations.

Every function here returns a JavaScript string meant to run inside the
user's logged-in Suralink Chrome tab, via the session transport — bridge
chrome_eval (preferred) or linked-tab javascript_tool (fallback); see
../references/architecture.md "Transport". Suralink is cookie-authenticated;
the Python side never holds a token.
"""
