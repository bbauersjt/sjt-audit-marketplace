"""Shared DB access for cch-risk-assessment scripts.

Source of truth is the editable CSV seeds in data/seed/*.csv. build_db.py
builds data/cch_ra.db IN PLACE from them. program_step.csv and
program_question_effect.csv are schema-ready but ship header-only (0 rows) --
forward scaffolding for the capture pipeline, with no query consumer yet;
program_question.csv is the only program seed read today (by program.py).
The skill folder is a FUSE mount
that rejects SQLite's default rollback -journal lock file, so the build runs
with journal_mode=OFF + locking_mode=EXCLUSIVE (no journal file is created).
Reads open the .db immutable=1 (no locks), which works even on the read-only
installed skill mount. Never build elsewhere and copy -- a copied .db carries
lock/journal state FUSE rejects.
"""
import csv, os, sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
SEED_DIR = os.path.join(DATA, "seed")
DB = os.path.join(DATA, "cch_ra.db")

# table name -> seed csv filename. Add new seeds here as the model grows.
TABLES = {
    "areas": "areas.csv",
    "form_node": "form_node.csv",
    "cascade_edge": "cascade_edge.csv",
    "area_tier": "area_tier.csv",
    "program_question": "program_question.csv",
    "program_question_effect": "program_question_effect.csv",
    "program_step": "program_step.csv",
}


def _seed_path(fname):
    return os.path.join(SEED_DIR, fname)


def build():
    """(Re)build data/cch_ra.db in place from the CSV seeds. FUSE-safe."""
    if os.path.exists(DB):
        # FUSE cowork mount forbids unlink; truncate in place instead of remove.
        try:
            os.remove(DB)
        except OSError:
            open(DB, "w").close()
    con = sqlite3.connect(DB)
    con.execute("PRAGMA journal_mode=OFF")
    con.execute("PRAGMA synchronous=OFF")
    con.execute("PRAGMA locking_mode=EXCLUSIVE")
    c = con.cursor()
    for table, fname in TABLES.items():
        with open(_seed_path(fname), newline="", encoding="utf-8") as f:
            r = csv.reader(f)
            cols = next(r)
            rows = list(r)
        c.execute(f"DROP TABLE IF EXISTS {table}")
        c.execute(f"CREATE TABLE {table} ({','.join(col + ' TEXT' for col in cols)})")
        if rows:
            c.executemany(f"INSERT INTO {table} VALUES ({','.join('?' * len(cols))})", rows)
    c.execute("CREATE INDEX IF NOT EXISTS ix_areas_type ON areas(audit_type)")
    c.execute("CREATE INDEX IF NOT EXISTS ix_edge_from ON cascade_edge(from_form, from_key)")
    c.execute("CREATE INDEX IF NOT EXISTS ix_edge_to ON cascade_edge(to_form, to_key)")
    c.execute("CREATE INDEX IF NOT EXISTS ix_tier_type ON area_tier(audit_type)")
    c.execute("CREATE INDEX IF NOT EXISTS ix_pq_area ON program_question(audit_type, area)")
    c.execute("CREATE INDEX IF NOT EXISTS ix_pqe_q ON program_question_effect(audit_type, area, q_id)")
    c.execute("CREATE INDEX IF NOT EXISTS ix_pstep_area ON program_step(audit_type, area)")
    con.commit()
    con.close()
    return DB


def get_db():
    """Return a read-only (immutable) connection, building the DB if absent."""
    if not os.path.exists(DB):
        build()
    con = sqlite3.connect(f"file:{DB}?immutable=1", uri=True)
    con.row_factory = sqlite3.Row
    return con
