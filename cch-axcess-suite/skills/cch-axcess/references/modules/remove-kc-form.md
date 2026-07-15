---
summary: Remove / delete a KC form (always soft-delete — no hard delete in this skill)
leg: kc
triggers:
  - "delete this form"
  - "remove KC form"
  - "drop the form we just added"
  - "clean up unfiled forms"
  - "scrub the binder of unwanted forms"
inputs:
  - "Form IDs to soft-delete"
calls:
  - scripts.wpm.folder_get
  - scripts.wpm.ensure_user_delete_folder
  - scripts.wpm.soft_delete_form
  - scripts.wpm.set_index
status: validated
---
# Module — Soft-Delete KC Form from Binder

> **wpId lookup — GetBinder FIRST.** See `architecture.md` → "WPM surface — confirmed facts".

**Triggers:** "delete this form from the binder", "remove [form] from this engagement", "drop the form we just added", "clean up unfiled forms", "remove KC form", "scrub the binder of unwanted forms".

## What this does

- Moves unwanted KC forms (KBA/AUD/AID/COR/RPT/KCO) into a "User to delete" folder (index `9999`). The user reviews the folder in the UI and deletes from there when confident.
- **This skill does NOT hard-delete KC forms.** See `scripts/wpm.py` header and "Why no hard delete" below.

## Prerequisites

- Leg: `kc` warm (Step 0) — GetBinder lookup is KC API; WPM soft-delete rides `ls:wpm` from the same tab. Rules 0–3 apply (SKILL.md).
- The binder wrapper folder's `locationId` (parent of the section folders; visible in the root WPM response).

## Procedure

### 1. Ensure the "User to delete" folder exists

```python
from scripts import wpm
# Get the wrapper listing
js = wpm.folder_get(client_id, eng_id, wrapper_folder_id, wpm_headers)
# Run via chrome_api_call (bridge, KC origin) or the linked-tab Chrome JS tool, then:
folders = parsed_response  # list of folder/workpaper rows under wrapper
create_js = wpm.ensure_user_delete_folder(client_id, wrapper_folder_id, folders, wpm_headers)
if create_js is None:
    # Existing folder — scan listing for its locationId
    user_del_loc = next(f["locationId"] for f in folders
                        if f["name"].strip().lower() == "user to delete" and f["type"] == "Folder")
else:
    # Run create_js via chrome_api_call (bridge, KC origin) or the linked-tab Chrome JS tool; response IS the new locationId as plain text
    user_del_loc = int(chrome_response_text)
```

### 2. Look up documentId + current locationId for each form

```python
js = wpm.folder_get(client_id, eng_id, folder_id, wpm_headers)
# Match by name (regex on form ID); pull `locationId` and `documentId`.
```

### 3. Soft-delete (move into "User to delete")

```python
for form in forms_to_remove:
    js = wpm.soft_delete_form(
        client_id=client_id,
        parent_folder_location_id=form["locationId"],
        user_delete_folder_id=user_del_loc,
        document_id=form["documentId"],
        headers=wpm_headers,
    )
    # Run via chrome_api_call (bridge, KC origin) or the linked-tab Chrome JS tool; status 200 expected.
```

### 4. Set sub-indexes so they sort together under 9999

```python
items = [
    {"index": f"9999.{i+1}", "name": form["name"],
     "object_id": form["documentId"], "object_type": "KCForms"}
    for i, form in enumerate(forms_to_remove)
]
js = wpm.set_index(client_id, items, wpm_headers)
```

### 5. Verify

```python
# Re-GET the "User to delete" folder; confirm all moved forms appear.
js = wpm.folder_get(client_id, eng_id, user_del_loc, wpm_headers)
```

Tell the user the forms are staged in `9999 User to delete` for them to review and remove from the UI.

## Known failure modes

- Forms that were never indexed (fresh adds still in `-4 Unfiled KC Forms`) move fine but the Set-Index step is required to make them sort under `9999.N`. Without it the moved forms show no index column entry.
- `wpm.set_index` is sequential — don't try to parallelize.
- Wrapper folder doesn't exist yet? Run `setup-binder-from-index.md` first; "User to delete" needs a parent.

## Why no hard delete

- Hard-deleting a KC form corrupts the binder and is unrecoverable — this skill does not implement it. Soft-delete is the only path.
- See `architecture.md` → KC-form hard delete, and the policy block atop `scripts/wpm.py`.

<!-- END -->
