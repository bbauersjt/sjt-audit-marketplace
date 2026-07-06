#!/usr/bin/env python3
"""Cascade tree expander for cch-risk-assessment.

Given one upstream selection (e.g. an AUD-100 / KBA-200 pick), walk the
cascade_edge table and print every downstream node it forces -- the full
decision tree for the judgment layer. Edges are populated from live capture
(snapshot + diff); with no edges yet this prints just the root.

Usage:
    python tree.py --from AUD-100:KEY [--type NPO] [--json] [--depth N]
    python tree.py --roots [--type NPO]      # list nodes with no precedent (tree starts)

A node id is "FORM:KEY" (e.g. "KBA-400:CASH.SigClassTans").
"""
import argparse, json, sys
from _db import get_db


def label_for(con, form, key, at):
    # try form_node first, then fall back to the areas table by binding key
    r = con.execute(
        "SELECT label FROM form_node WHERE form=? AND node_key=? AND (audit_type=? OR audit_type='ALL') LIMIT 1",
        (form, key, at or ""),
    ).fetchone()
    if r and r["label"]:
        return r["label"]
    r = con.execute(
        "SELECT plain_name FROM areas WHERE binding_key=? AND (audit_type=? OR ?='') LIMIT 1",
        (key, at or "", at or ""),
    ).fetchone()
    return r["plain_name"] if r else ""


def children(con, form, key, at):
    sql = "SELECT to_form,to_key,relation,trigger_value FROM cascade_edge WHERE from_form=? AND from_key=?"
    args = [form, key]
    if at:
        sql += " AND (audit_type=? OR audit_type='ALL')"; args.append(at)
    return con.execute(sql, args).fetchall()


def walk(con, form, key, at, depth, maxd, seen, acc):
    nid = f"{form}:{key}"
    node = {"id": nid, "form": form, "key": key, "label": label_for(con, form, key, at), "children": []}
    acc.append((depth, node))
    if nid in seen or (maxd is not None and depth >= maxd):
        return node
    seen.add(nid)
    for e in children(con, form, key, at):
        child = walk(con, e["to_form"], e["to_key"], at, depth + 1, maxd, seen, acc)
        if e["relation"]:
            child["relation"] = e["relation"]
        node["children"].append(child)
    return node


def main():
    p = argparse.ArgumentParser(description="cch-risk-assessment cascade tree")
    p.add_argument("--from", dest="frm", help="start node FORM:KEY")
    p.add_argument("--type", dest="at", help="audit type (ASB HOA CNS EBP ALG NPO)")
    p.add_argument("--depth", type=int, default=None)
    p.add_argument("--roots", action="store_true", help="list nodes that have no precedent")
    p.add_argument("--json", action="store_true")
    a = p.parse_args()
    con = get_db()

    if a.roots:
        sql = ("SELECT DISTINCT from_form,from_key FROM cascade_edge e "
               "WHERE NOT EXISTS (SELECT 1 FROM cascade_edge p WHERE p.to_form=e.from_form AND p.to_key=e.from_key)")
        args = []
        if a.at:
            sql = sql.replace("WHERE NOT EXISTS", "WHERE (audit_type=? OR audit_type='ALL') AND NOT EXISTS"); args = [a.at]
        rows = con.execute(sql, args).fetchall()
        for r in rows:
            print(f"{r['from_form']}:{r['from_key']}")
        if not rows:
            print("(no edges captured yet)")
        return

    if not a.frm or ":" not in a.frm:
        sys.exit("need --from FORM:KEY  (e.g. --from AUD-100:OVERALL_TQ_TAILORING_AuditAreas)")
    form, key = a.frm.split(":", 1)
    acc = []
    root = walk(con, form, key, a.at, 0, a.depth, set(), acc)
    con.close()

    if a.json:
        print(json.dumps(root, indent=2)); return
    for depth, node in acc:
        lbl = f"  {node['label']}" if node["label"] else ""
        rel = f"  <{node.get('relation')}>" if node.get("relation") else ""
        print(f"{'  ' * depth}- {node['id']}{lbl}{rel}")
    if len(acc) == 1:
        print("  (no downstream edges captured yet)")


if __name__ == "__main__":
    main()
