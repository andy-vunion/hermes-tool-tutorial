---
title: 十五五产业链投研看板
toc: false
---

<style>
.hero { padding: 40px 0; text-align: center; }
.hero h1 { font-size: 2.5em; background: linear-gradient(135deg, #58a6ff, #a371f7); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.hero p { color: #8b949e; font-size: 1.1em; }
.kpi-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; margin: 24px 0; }
.kpi-card { background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 20px; text-align: center; }
.kpi-card .value { font-size: 2em; font-weight: 700; color: #58a6ff; }
.kpi-card .label { font-size: 0.85em; color: #8b949e; margin-top: 4px; }
</style>

<div class="hero">
  <h1>🎯 十五五产业链投研看板</h1>
  <p>政策 → 赛道 → 产业链 → 标的 · 数据驱动 · 持续跟踪</p>
</div>

```js
const universe = (await FileAttachment("data/companies.json").json()).universe;
const reports = (await FileAttachment("data/companies.json").json()).reports;
const signals = await FileAttachment("data/signals.json").json();
const totalReports = reports.reduce((s, r) => s + r.cnt, 0);
```

<div class="kpi-grid">
  <div class="kpi-card"><div class="value">${universe.total.toLocaleString()}</div><div class="label">全市场A股</div></div>
  <div class="kpi-card"><div class="value">${universe.avg_pe.toFixed(1)}</div><div class="label">PE均值</div></div>
  <div class="kpi-card"><div class="value">${signals.length}</div><div class="label">T1/T2/T3信号</div></div>
  <div class="kpi-card"><div class="value">${totalReports}</div><div class="label">券商研报</div></div>
</div>

---

## 📜 数据链路

<div style="text-align:center;padding:20px;font-size:1.1em;color:#8b949e">
  📜 十五五规划 → 🏭 28赛道 → 🔗 产业链拆解 → 📦 产品/BOM → 💼 169标的 → 📡 持续跟踪
</div>

## 🏭 可投性 TOP 10

```js
const sectors = (await FileAttachment("data/sectors.json").json()).sectors;
const top10 = sectors.slice(0, 10);

display(Inputs.table(top10, {
  columns: ["sector_name", "policy_weight", "investability_score", "time_horizon", "market_size_cn_5y", "growth_cagr_pct"],
  header: {
    sector_name: "赛道", policy_weight: "政策权重", investability_score: "可投性",
    time_horizon: "时间窗口", market_size_cn_5y: "市场(亿)", growth_cagr_pct: "CAGR%"
  },
  format: {
    investability_score: (x) => x.toFixed(1),
    market_size_cn_5y: (x) => x ? (x/10000).toFixed(0) + "万" : "-",
    growth_cagr_pct: (x) => x ? x + "%" : "-"
  }
}))
```

<div class="note">
  <a href="/sectors">查看全部28赛道 →</a> &nbsp; | &nbsp;
  <a href="/chain">产业链视图 →</a> &nbsp; | &nbsp;
  <a href="/stocks">标的筛选 →</a>
</div>
