#!/usr/bin/env python3
"""Data loader: export sectors + analysis as JSON"""
import sqlite3, json, os, sys
DB = os.path.expanduser('~/.hermes/data/research.db')
db = sqlite3.connect(DB)
db.row_factory = sqlite3.Row

result = {
    "sectors": [dict(r) for r in db.execute('SELECT * FROM sector_analysis ORDER BY investability_score DESC').fetchall()],
    "policy": [dict(r) for r in db.execute('SELECT * FROM policy_sectors ORDER BY id').fetchall()],
}

db.close()
json.dump(result, sys.stdout, ensure_ascii=False)
