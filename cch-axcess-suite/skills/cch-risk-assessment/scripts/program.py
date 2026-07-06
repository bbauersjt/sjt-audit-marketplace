#!/usr/bin/env python3
"""Pull the yes/no questions a significant area's audit program needs answered.

The judgment layer calls this ONCE per significant area (determined via the tier
system + user agreement) to get the exact set of program tailoring questions that
must be answered to run the audit -- no MD reading. Answer each from your sources
(TB, prior year, client profile) or flag for the user, write to a payload, drop
from context. cch-axcess applies the resulting step selection; this skill only
supplies the questions + the firm's default/look-for guidance.

Columns:
  q_id          CCH object key -> the write target for the answer (YES/NO valueKey)
  question_text the yes/no question
  default_answer firm default (blank until authored)
  autonomy      'auto' = safe to keep default unattended | 'review' = judgment-layer must decide | blank = unauthored
  look_for      the signal to evaluate when autonomy='review' (blank until authored)

Usage:
  python3 program.py --area CASH [--type NPO] [--json]
  python3 program.py --list            # areas + question counts
"""
import argparse, json, sys
from _db import get_db

def questions(area, at="NPO"):
    con=get_db()
    rows=con.execute(
        "SELECT q_id,seq,qtype,question_text,default_answer,autonomy,look_for,notes "
        "FROM program_question WHERE audit_type=? AND area=? ORDER BY CAST(seq AS INTEGER)",
        (at, area)).fetchall()
    con.close()
    return [dict(r) for r in rows]

def list_areas(at="NPO"):
    con=get_db()
    rows=con.execute(
        "SELECT area, program, COUNT(*) n FROM program_question WHERE audit_type=? "
        "GROUP BY area, program ORDER BY program", (at,)).fetchall()
    con.close()
    return [dict(r) for r in rows]

def main():
    p=argparse.ArgumentParser(description="pull a program's yes/no tailoring questions")
    p.add_argument("--area"); p.add_argument("--type", dest="at", default="NPO")
    p.add_argument("--list", action="store_true"); p.add_argument("--json", action="store_true")
    a=p.parse_args()
    if a.list:
        rows=list_areas(a.at)
        if a.json: print(json.dumps(rows, indent=2)); return
        for r in rows: print(f"{r['program']}  {r['area']:20} {r['n']} questions")
        print(f"\n{len(rows)} programs with tailoring questions (areas with 0 are omitted: JE2, ESTIMATES)")
        return
    if not a.area: sys.exit("need --area AREA  (or --list)")
    qs=questions(a.area, a.at)
    if a.json: print(json.dumps(qs, indent=2)); return
    if not qs: print(f"{a.area}: no tailoring questions (program has no Y/N gating)"); return
    print(f"{a.area} ({a.at}) - {len(qs)} yes/no questions to answer:\n")
    for q in qs:
        d=f" [default={q['default_answer']}]" if q['default_answer'] else ""
        lf=f"\n      look-for: {q['look_for']}" if q['look_for'] else ""
        print(f"  {q['seq']:>2}. {q['question_text']}{d}\n      q_id: {q['q_id']}{lf}")

if __name__=="__main__":
    main()
