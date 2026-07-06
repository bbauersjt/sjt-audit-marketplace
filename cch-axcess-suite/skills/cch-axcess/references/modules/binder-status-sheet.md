---
summary: Build the binder status / sign-off sheet to Excel — every file with index, name, type, sign-off status, status, last-modified, and a clickable deep link
leg: wpm
triggers:
  - "build the binder status sheet"
  - "binder status sheet"
  - "binder index"
  - "sign-off map"
  - "sign-off tracker"
  - "workpaper status sheet"
  - "what's signed off in this binder"
  - "export the binder to Excel with links"
  - "clickable binder index"
inputs:
  - "Engagement URL (clientId + engagementId)"
  - "Output folder (user-visible working folder)"
calls:
  - scripts.wpm.folder_tree
  - scripts.binder_status.rows_from_folders
  - scripts.binder_status.build_status_workbook
status: validated (bridge, 2026-06-23)
---
# Module — Binder Status / Sign-off Sheet

Produces an Excel of every binder file: Folder, Index, Type, Name, **Sign-off Status**, Form/File Status,
Last Modified, and a clickable **Open** deep link (KC forms -> Knowledge Coach; reports/leadsheets ->
engagement app). Bridge-first; no clicks.

## Procedure
1. **Transport** is decided at SKILL.md Step 0.0 (`chrome_bridge_status`). `leg: wpm`.
2. **Auth.** Capture the WPM bearer + `IDToken` via `chrome_network_recent(host_filter="cchaxcess")`
   (bridge), or the monkeypatch capture on the linked-tab fallback. User-scoped; reuse across the walk.
3. **Folder tree.** `chrome_api_call GET /v1/NewEngagementView/folders/{clientId}` (bridge) — or
   `scripts.wpm.folder_tree` on the fallback. Collect every folder `locationId` + 4-digit `index` + name,
   including the pseudo-folders -1/-2/-3/-4 (Unfiled WP/Reports/Leadsheets/KC Forms).
4. **Walk contents.** For EACH folder: `chrome_api_call GET /v1/NewEngagementView/{clientId}/{locationId}/{engagementId}`
   with the captured headers (`Authorization` + all-caps `IDToken` + `USERLocale`/`CountryCode`; locale headers
   REQUIRED or you get 200 + empty arrays). Each row carries `type, name, index, signOffs[], documentUrl,
   formStatus, statusCode, lastModifiedOn`. Linked-tab fallback: `scripts.wpm.folder_get`. Assemble a list of
   `{fIdx, fName, items:[rows]}` per folder.
   - If you batch the walk as one in-page eval (engagement origin), use **async** XHR only — a synchronous
     XHR loop freezes the tab.
5. **Build the sheet** (exec cache; openpyxl):
   ```python
   from scripts import binder_status
   rows = binder_status.rows_from_folders(folder_blocks)
   binder_status.build_status_workbook(rows, r"<output folder>\binder-status.xlsx")
   ```
6. Present the file to the user.

## Sign-off column
Sign-off status comes from the WPM row's **`signOffs[]`** — NOT `documentStatus`/`formStatus` (those are
lifecycle state: "Active"/blank). Empty `signOffs` -> "Not signed off". The populated key names in
`binder_status._signoff` are best-effort (the validation binder had nothing signed); confirm against one
signed form and adjust the display mapping if needed (display-only, low risk).

<!-- END -->
