---
title: 产业链拆解
---

```js
const chains = await FileAttachment("data/chains.json").json();
const sectors = (await FileAttachment("data/sectors.json").json()).sectors;
const chainNames = Object.keys(chains);
const selChain = view(Inputs.select(chainNames, {label: "选择赛道", value: chainNames[0]}));
```

```js
const chain = chains[selChain];
const groups = {};
chain.nodes.forEach(n => {
  if (!groups[n.pos]) groups[n.pos] = [];
  groups[n.pos].push(n);
});
```

```js
const icons = {"上游": "⬆️", "中游": "🔄", "下游": "⬇️"};
const columns = ["上游", "中游", "下游"].map(pos => {
  if (!groups[pos]) return null;
  return html`<div class="card" style="background:#161b22;border:1px solid #30363d;border-radius:8px;padding:16px">
    <h3 style="color:#58a6ff;margin-bottom:12px;text-align:center">${icons[pos]} ${pos}</h3>
    ${groups[pos].map(n => html`
      <div style="background:#1c2333;border:1px solid #2a3345;border-radius:6px;padding:12px;margin-bottom:8px">
        <div style="font-weight:600;color:#c9d1d9;margin-bottom:4px">${n.name}</div>
        <div style="font-size:12px;color:#8b949e;line-height:1.6">
          毛利率 <span style="color:#3fb950">${n.gm}</span> · 国产化率 <span style="color:#d29922">${n.local}</span><br>
          壁垒: ${n.barrier}<br>
          ${n.desc}
        </div>
      </div>
    `)}
  </div>`;
});
display(html`<div class="grid grid-cols-3" style="gap: 20px">${columns}</div>`);
```

---

## 📊 价值分布

```js
// Calculate value distribution
const valueDist = chain.nodes.map(n => ({
  name: n.name,
  pos: n.pos,
  gm: n.gm
}));

display(Plot.plot({
  marks: [
    Plot.barX(valueDist, {x: "name", y: "gm", fill: "pos", sort: {x: "y", reverse: true}})
  ],
  x: {label: "毛利率区间"},
  y: {label: "环节"},
  color: {legend: true, domain: ["上游","中游","下游"], range: ["#3fb950","#58a6ff","#d29922"]},
  height: 300,
  marginLeft: 120,
  style: {background: "#0d1117", color: "#c9d1d9"}
}))
```

## 🏭 赛道可投性

```js
display(Inputs.table(sectors, {
  columns: ["sector_name", "investability_score", "time_horizon", "growth_cagr_pct", "catalyst_2026"],
  header: { sector_name: "赛道", investability_score: "可投性", time_horizon: "窗口", growth_cagr_pct: "CAGR%", catalyst_2026: "催化剂" },
  rows: 15
}))
```
