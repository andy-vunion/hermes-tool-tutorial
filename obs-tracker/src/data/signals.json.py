#!/usr/bin/env python3
import sqlite3, json, os, sys
DB = os.path.expanduser('~/.hermes/data/research.db')
db = sqlite3.connect(DB)
db.row_factory = sqlite3.Row
signals = [dict(r) for r in db.execute('SELECT * FROM trigger_signal ORDER BY signal_date DESC').fetchall()]
db.close()
json.dump(signals, sys.stdout, ensure_ascii=False, default=str)
