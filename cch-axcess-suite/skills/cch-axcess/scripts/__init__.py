"""cch-axcess scripts package.

All deterministic CCH Axcess operations live here. Modules describe WHAT and WHEN;
these scripts handle HOW. Import what you need:

    from scripts import kc, wpm, auth, catalog, xref

Every API function takes a `headers` dict captured live from the user's browser
(see auth_capture.py). No tokens are persisted in this repo.
"""
# <!-- END -->
