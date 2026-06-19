---
title: 赛道全景
---

```js
const {sectors, policy} = await FileAttachment("data/sectors.json").json();
```

<div class="grid grid-cols-3" style="gap: 16px">
  ${sectors.map(s => {
    const col = s.investability_score >= 8.5 ? "#3fb950" : s.investability_score >= 7.5 ? "#58a6ff" : "#d29922";
    const tb = s.time_horizon === "near" ? "🟢 近期" : s.time_horizon === "mid" ? "🟡 中期" : "⚪ 远期";
    const mkt = s.market_size_cn_5y ? (s.market_size_cn_5y/10000).toFixed(0) + "万亿" : "-";
    return `
    <div class="card" style="background:#161b22;border:1px solid #30363d;border-radius:8px;padding:16px;cursor:pointer"
         onclick="window.location.href='/chain'">
      <h3 style="color:#c9d1d9;margin-bottom:8px">${s.sector_name}</h3>
      <div style="font-size:2em;font-weight:700;color:${col};margin:8px 0">${s.investability_score.toFixed(1)}</div>
      <div style="font-size:12px;color:#8b949e;line-height:1.7">
        ${tb} · 权重${s.policy_weight.toFixed(1)} · ${mkt}<br>
        CAGR ${s.growth_cagr_pct || "-"}%<br>
        <span style="font-size:10px">${(s.catalyst_2026 || "").substring(0, 40)}</span>
      </div>
    </div>`;
  }).join("")}
</div>

---

## 📋 政策原文映射

```js
display(Inputs.table(policy, {
  columns: ["sector_name", "category", "plan_section", "priority", "quant_target"],
  header: { sector_name: "赛道", category: "类别", plan_section: "章节", priority: "优先级", quant_target: "量化目标" },
  rows: 28
}))
```
