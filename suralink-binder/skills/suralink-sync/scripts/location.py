"""Where the mirror lives — chosen by the user once, then remembered.

The skill does NOT hard-code an absolute mirror path. Instead the user picks a
root folder the first time (via Cowork's `request_cowork_directory` picker), and
the choice is saved to a tiny **pointer file** that the skill reads on every run
thereafter. The pointer survives skill updates: it lives OUTSIDE the skill
directory (the skill dir is mounted read-only at runtime and is git-managed, so
anything written inside it would be unwritable and/or clobbered on the next
sync). Git never sees the pointer, so a `git pull` of the skill can't touch it.

The pointer file
----------------
    ~/Documents/_claude-config/.suralink-sync.json   (anchor: ~/Documents)
    { "mirrorRoot": "<absolute host path the user picked>" }

The pointer is anchored at the profile ROOT (`~`, i.e. `C:\\Users\\<user>`), NOT
`~/Documents`. With OneDrive "Known Folder Move" enabled, `~/Documents`
redirects into OneDrive — which syncs the file off-machine and, more
importantly, drags the whole mirror into OneDrive when the picker defaults
there, causing the sync lag you hit when these folders are later mounted as
project folders. The profile root is never OneDrive-redirected, always exists,
and `request_cowork_directory` auto-mounts it without a picker. The pointer only
POINTS at the root — the root itself can be anywhere the user selected (another
drive, a synced projects folder, ...).

Resolution flow each run (driven from run-sync.md):
  1. Mount the anchor (`MOUNT_HINT_CONFIG_ANCHOR`) so the pointer is readable.
  2. `saved_mirror_root(anchor_mount)` ->
       - a path  -> mention it ("files saved to X -- to change the target
                   directory, just ask"), mount that path, use it. No picker.
       - None    -> first run: launch the picker (`request_cowork_directory`,
                   default `MOUNT_HINT_PICKER_DEFAULT`), let the user choose the
                   root, then `save_mirror_root(anchor_mount, chosen)`.
  3. `ensure_structure(mirror_root)`.

Each machine keeps its own pointer + its own independent mirror, catalog,
manifest and active list. Machines never share state.
"""
import json
import os
import shutil

# --- the pointer ----------------------------------------------------------
# Where the remembered-root pointer file lives, relative to the user's home.
# It is a small JSON breadcrumb, NOT the mirror itself.
CONFIG_FILENAME = ".suralink-sync.json"      # ~/Documents/_claude-config/.suralink-sync.json

# All Claude skill configs for this user live together in ONE folder so they
# survive skill updates and stay out of the way. It sits under the local
# Documents folder (which mounts), NOT the profile root (which does not -- see
# MOUNT_HINT_CONFIG_ANCHOR below).
CONFIG_SUBDIR = "_claude-config"             # ~/Documents/_claude-config

# Pass to request_cowork_directory to mount the anchor that holds the pointer.
# The profile ROOT (~) is chosen over ~/Documents on purpose: ~/Documents is
# OneDrive-redirected under Known Folder Move, the profile root is not. It
# always exists, so it auto-mounts without a picker.
# The profile ROOT (~) is NOT mountable in Cowork -- it contains Claude's own
# session storage, so request_cowork_directory refuses it. The local Documents
# folder (~/Documents) always mounts and is never OneDrive-redirected here, so
# the config anchor is Documents and the pointer lives in its _claude-config
# subfolder. On a fresh machine the subfolder may not exist yet: mount
# ~/Documents (always present) and create _claude-config under it.
MOUNT_HINT_CONFIG_ANCHOR = "~/Documents"
MOUNT_HINT_CONFIG_ANCHOR_FALLBACK = "~/Documents"

# First run: open the NATIVE folder picker by calling request_cowork_directory
# with NO path, so the user truly browses and chooses the root. This hint is
# only the REMOTE-SESSION fallback (a remote session rejects an omitted path);
# in that case we mount this default instead. It points at the LOCAL profile
# root -- never OneDrive's Documents -- so even a fallback mirror stays off
# OneDrive. There is deliberately no fixed "Suralink Mirror" folder name -- the
# root is whatever the user picks.
MOUNT_HINT_PICKER_DEFAULT = "~/Documents"

INBOX = "_inbox"   # legacy Chrome download target; current default is ~/Downloads


# --- pointer read / write -------------------------------------------------

def config_path(anchor_mount):
    """Absolute path of the pointer file, given the mounted anchor folder
    (the sandbox path returned by request_cowork_directory for ~/Documents).
    The pointer lives in the shared _claude-config subfolder so every skill's
    config sits in one place."""
    return os.path.join(os.path.abspath(anchor_mount), CONFIG_SUBDIR,
                        CONFIG_FILENAME)


def read_config(anchor_mount):
    """Return the parsed pointer dict, or {} if it does not exist / is junk."""
    p = config_path(anchor_mount)
    try:
        with open(p, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except (OSError, ValueError):
        return {}


def saved_mirror_root(anchor_mount):
    """The user's remembered root as a HOST absolute path, or None if unset.

    This is the value the user picked, stored verbatim. It is a host path
    (what the user sees on their computer) -- to actually read/write the mirror,
    mount it via request_cowork_directory and use the returned sandbox path."""
    root = read_config(anchor_mount).get("mirrorRoot")
    return root or None


def save_mirror_root(anchor_mount, mirror_root_host_path):
    """Persist the chosen root to the pointer file. Pass the HOST path the user
    selected (the Windows/macOS path from request_cowork_directory), not a
    sandbox `/sessions/.../mnt/...` path -- the pointer must mean something on
    the user's own machine. Idempotent; overwrites any previous choice.

    WARNING: repointing alone does NOT move the existing mirror. The catalog,
    active-client list, manifest and all downloaded files live under the OLD
    root, so a bare repoint makes the next sync re-bootstrap empty and re-pull
    everything. Call `migrate_root(old, new)` first (or warn the user) -- see
    run-sync.md "Changing the root"."""
    data = read_config(anchor_mount)
    data["mirrorRoot"] = mirror_root_host_path
    p = config_path(anchor_mount)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    return p


def has_saved_root(anchor_mount):
    """True iff a remembered root is on file for this machine."""
    return saved_mirror_root(anchor_mount) is not None


# --- mirror skeleton ------------------------------------------------------

def ensure_structure(mirror_root):
    """Create the mirror skeleton if it does not exist yet. Idempotent -- safe
    to call on every run. First run on a fresh root creates everything; later
    runs find it already there.

    `mirror_root` is the MOUNTED (sandbox) path of the folder the user chose.
    Returns the absolute mirror_root.
    """
    mirror_root = os.path.abspath(mirror_root)
    os.makedirs(mirror_root, exist_ok=True)
    os.makedirs(os.path.join(mirror_root, INBOX), exist_ok=True)
    return mirror_root


def inbox_dir(mirror_root):
    """Absolute path of the _inbox staging folder under the mirror root.
    Legacy -- current default download target is ~/Downloads."""
    return os.path.join(os.path.abspath(mirror_root), INBOX)


def is_initialized(mirror_root):
    """True if this mirror already has its skeleton (an _inbox folder)."""
    return os.path.isdir(os.path.join(mirror_root, INBOX))


# --- repointing the root --------------------------------------------------

def migrate_root(old_root, new_root, *, overwrite=False):
    """Move an existing mirror from `old_root` to `new_root` when the user
    repoints the saved root.

    WHY THIS MATTERS -- the whole mirror (catalog.json, active-clients.json, the
    `_suralink_sync.json` manifest, and every `{Client}/{Label} Suralink Files/`
    tree) lives UNDER the root. If the pointer is repointed at a fresh empty
    folder WITHOUT moving these, the skill re-bootstraps from scratch: the active
    list is empty, nothing is "known", so the next sync treats every engagement
    as a first pull and re-downloads the entire back-catalogue. Moving the
    contents over is what makes a repoint seamless instead of a full re-sync.

    Moves every top-level entry from `old_root` into `new_root`. Cross-drive
    safe (`shutil.move` copies-then-deletes when the two roots are on different
    filesystems). Both args are MOUNTED (sandbox) paths -- mount the old root and
    the new root before calling.

    A name already present in `new_root` is skipped unless `overwrite=True`
    (which replaces the existing target). Nothing is removed from `old_root`
    except entries that were successfully moved.

    Returns {"moved": [names...], "skipped": [(name, reason)...]}.
    """
    old_root = os.path.abspath(old_root)
    new_root = os.path.abspath(new_root)
    os.makedirs(new_root, exist_ok=True)
    moved, skipped = [], []
    if not os.path.isdir(old_root):
        return {"moved": moved, "skipped": skipped}
    if old_root == new_root:
        return {"moved": moved, "skipped": [("*", "old and new root are the same")]}
    for name in sorted(os.listdir(old_root)):
        src = os.path.join(old_root, name)
        dst = os.path.join(new_root, name)
        if os.path.exists(dst):
            if not overwrite:
                skipped.append((name, "already exists at destination"))
                continue
            if os.path.isdir(dst) and not os.path.islink(dst):
                shutil.rmtree(dst)
            else:
                os.remove(dst)
        shutil.move(src, dst)
        moved.append(name)
    return {"moved": moved, "skipped": skipped}
