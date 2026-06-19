---
title: 标的筛选
---

```js
const {companies, financials, universe, pe_pct} = await FileAttachment("data/companies.json").json();
const {sectors} = await FileAttachment("data/sectors.json").json();
const signals = await FileAttachment("data/signals.json").json();

// Merge company data with financials
const finMap = {};
financials.forEach(f => { finMap[f.ts_code] = f; });

const rows = companies.map(c => {
  const fin = finMap[c.ticker] || {};
  const pct = pe_pct[c.ticker] || "-";
  return {
    name: c.name, ticker: c.ticker, sector: c.sector_name, role: c.role,
    pe: fin.pe_ttm || c.pe_ttm || 0,
    pct: pct, gm: fin.gm_ttm || 0,
    rev_yoy: fin.rev_ttm_yoy || 0, roe: fin.roe_est || 0
  };
});

const selSector = view(Inputs.select([...new Set(rows.map(r => r.sector))].sort(), {label: "赛道筛选", value: ""}));

const filtered = selSector ? rows.filter(r => r.sector === selSector) : rows;
```

<div class="kpi-grid" style="grid-template-columns:repeat(4,1fr);margin-bottom:20px">
  <div class="kpi-card"><div class="value">${companies.length}</div><div class="label">标的</div></div>
  <div class="kpi-card"><div class="value">${filtered.length}</div><div class="label">当前筛选</div></div>
  <div class="kpi-card"><div class="value">${universe.avg_pe.toFixed(1)}</div><div class="label">全市场PE均值</div></div>
  <div class="kpi-card"><div class="value">${universe.pe_lt15}</div><div class="label">PE&lt;15标的</div></div>
</div>

```js
display(Inputs.table(filtered, {
  columns: ["name", "ticker", "sector", "pe", "pct", "gm", "rev_yoy", "roe", "role"],
  header: {
    name: "标的", ticker: "代码", sector: "赛道", pe: "PE_TTM",
    pct: "分位%", gm: "毛利率", rev_yoy: "营收YoY", roe: "ROE≈", role: "产业链角色"
  },
  format: {
    pe: (x) => x.toFixed(1),
    pct: (x) => typeof x === "number" ? x + "%" : "-",
    gm: (x) => x ? x.toFixed(1) + "%" : "-",
    rev_yoy: (x) => x ? x.toFixed(1) + "%" : "-",
    roe: (x) => x ? x.toFixed(1) + "%" : "-"
  },
  sort: "pe",
  reverse: false,
  rows: 22
}))
```

## 📡 最新信号

```js
const nameMap = {};
companies.forEach(c => { if (c.ticker) nameMap[c.ticker] = c.name; });
const sigRows = signals.slice(0, 20).map(s => ({
  date: s.signal_date, name: nameMap[s.ts_code] || s.ts_code, code: s.ts_code,
  t1: s.t1_pass ? "✓" : "", t2: s.t2_pass ? "✓" : "", t3: s.t3_pass ? "✓" : "",
  close: s.close?.toFixed(2), dist: s.dist_52w_high?.toFixed(1) + "%", vol: s.vol_ratio?.toFixed(1)
}));

display(Inputs.table(sigRows, {
  columns: ["date", "name", "code", "t1", "t2", "t3", "close", "dist", "vol"],
  header: { date: "日期", name: "标的", code: "代码", t1: "T1", t2: "T2", t3: "T3", close: "收盘", dist: "距52W高", vol: "量比" },
  rows: 15
}))
```
