#!/usr/bin/env python3
import sqlite3, json, os, sys
DB = os.path.expanduser('~/.hermes/data/research.db')
db = sqlite3.connect(DB)
db.row_factory = sqlite3.Row

# Companies with sector names
companies = []
for c in db.execute('SELECT * FROM sector_companies').fetchall():
    d = dict(c)
    # Find sector name
    sector = db.execute('SELECT sector_name FROM sector_analysis WHERE id=?', (c['sector_analysis_id'],)).fetchone()
    d['sector_name'] = sector['sector_name'] if sector else ''
    companies.append(d)

# Financials
financials = [dict(r) for r in db.execute('SELECT * FROM stock_financials').fetchall()]

# Universe
u = db.execute('''SELECT COUNT(*) as total, COUNT(CASE WHEN pe_ttm>0 THEN 1 END) as with_pe,
    AVG(CASE WHEN pe_ttm>0 AND pe_ttm<1000 THEN pe_ttm END) as avg_pe,
    COUNT(CASE WHEN pe_ttm>0 AND pe_ttm<15 THEN 1 END) as pe_lt15
FROM universe_snapshot''').fetchone()
universe = dict(u)

# PE percentiles
pe_pct = {}
for f in financials:
    if f['pe_ttm'] and f['pe_ttm'] > 0:
        rank = db.execute('SELECT COUNT(*) FROM universe_snapshot WHERE pe_ttm>0 AND pe_ttm<?', (f['pe_ttm'],)).fetchone()[0]
        pe_pct[f['ts_code']] = round(rank / u['with_pe'] * 100, 1)

# Reports summary
reports = [dict(r) for r in db.execute('SELECT sector_name, COUNT(*) as cnt FROM sector_reports GROUP BY sector_name ORDER BY cnt DESC').fetchall()]

db.close()
json.dump({"companies": companies, "financials": financials, "universe": universe, "pe_pct": pe_pct, "reports": reports}, sys.stdout, ensure_ascii=False, default=str)
