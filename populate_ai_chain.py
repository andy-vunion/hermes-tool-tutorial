#!/usr/bin/env python3
"""
产业链拆解体系 —— AI算力赛道填充脚本
将 methodology.md 中的方法论 + schema.sql 中的表结构，
用实际数据填充 research.db

运行方式: python3 populate_ai_chain.py
依赖: python3 标准库 (sqlite3, csv, json, datetime)
"""

import sqlite3
import csv
import json
import os
from datetime import datetime

DB_PATH = os.path.expanduser("~/.hermes/data/research.db")
CSV_PATH = os.path.dirname(os.path.abspath(__file__)) + "/us_benchmarks.csv"
SCHEMA_PATH = os.path.dirname(os.path.abspath(__file__)) + "/industry-chain-schema.sql"

def run_schema(conn):
    """执行建表 SQL"""
    with open(SCHEMA_PATH) as f:
        sql = f.read()
    conn.executescript(sql)
    conn.commit()
    print("[1/5] Schema 表结构已创建 ✅")

def populate_track_heat(conn):
    """填充赛道热度表 —— AI算力赛道"""
    rows = [
        ("AI算力", "2026-06-13", 45.0, 8.0, 12.0,
         35.0, 2.0, 14.0, 2.5,
         5.2, 15.0, 1.5,
         12, "national", 344.0,
         25.0, 1800, 85.0,
         68.0, 42.0,
         78.5, "hotspot", "medium"),
    ]
    conn.executemany("""
        INSERT OR REPLACE INTO track_heat_index (
            chain_name, snap_date,
            etf_flow_monthly, inst_holding_change_qoq, northbound_flow_monthly,
            rev_growth_median, gross_margin_trend, roe_median,
            turnover_rate_avg, earnings_revision_ratio,
            analyst_coverage_change, short_interest_ratio,
            policy_mention_count, policy_level, fiscal_support_billion,
            vc_pe_financing_monthly, new_company_registrations, patent_growth_yoy,
            sector_index_return_12m, alpha_vs_benchmark_12m,
            heat_composite_score, heat_tier, data_confidence
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, rows)
    conn.commit()
    print(f"[2/5] track_heat_index: {len(rows)} 条 ✅")

def populate_track_lifecycle(conn):
    """填充产业生命周期"""
    rows = [
        ("AI算力", "2026-06-13", "growth", "high",
         "accelerating", 15.0, 45, "increasing", "expanding", "high",
         "strong", "2024-03-05", "政府工作报告首提'人工智能+'；大基金三期3440亿落地",
         15, 35.0, "fast_rising", "moderate",
         "capacity_expansion", 85.0,
         "台积电CoWoS扩产50%; 国内中芯/华虹加码成熟制程; CSP自研芯片分流",
         0, None, 8.5),
    ]
    conn.executemany("""
        INSERT OR REPLACE INTO track_lifecycle (
            chain_name, snap_date, lifecycle_stage, stage_confidence,
            rev_growth_trajectory, industry_penetration_pct, competitor_count,
            competitor_count_trend, gross_margin_trend_direction, capex_intensity,
            policy_signal_strength, latest_policy_date, latest_policy_summary,
            policy_to_revenue_lag_months, localization_rate, localization_rate_trend,
            import_dependency_level,
            capacity_cycle, utilization_rate_est, expansion_plans_summary,
            is_policy_driven_pseudo_demand, pseudo_demand_evidence,
            growth_sustainability_score
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, rows)
    conn.commit()
    print(f"[2/5] track_lifecycle: {len(rows)} 条 ✅")

def populate_chain_composition(conn):
    """填充产业链拆解明细 —— AI算力15个独立节点 + 6个聚合节点"""
    # 15个满足三条件的独立节点
    independent = [
        # (chain_name, node_name, depth, parent, parent_id, listed, tam, comp_ident, meet, leader, leader_share, cr3, cr5, moat, tech_gen, tech_gap, gap_trend, loc_rate, val_pct, val_trend, margin_prof, bottleneck, substitute_mo, risks, sources, conf)
        ("AI算力", "AI训练芯片", 2, "GPU芯片", None, 4, 800.0, 1, 1,
         "海光信息(688041)", 45.0, 75, 90, "tech",
         "7nm DCU", "落后2代(4nm)", "narrowing", 5.0, 25.0, "increasing", "50-65%",
         "critical", 36,
         json.dumps(["x86授权被限", "华为昇腾竞争", "先进制程代工受限"]),
         json.dumps(["海光年报", "TrendForce", "IDC"]),
         "medium"),

        ("AI算力", "AI推理芯片", 2, "GPU芯片", None, 5, 500.0, 1, 1,
         "寒武纪(688256)", 30.0, 65, 85, "tech",
         "思元590", "落后1.5代", "narrowing", 15.0, 18.0, "increasing", "60-75%",
         "high", 24,
         json.dumps(["客户集中80%+", "训练侧差距大", "流片受阻风险"]),
         json.dumps(["寒武纪年报", "IDC"]),
         "medium"),

        ("AI算力", "GPU模组制造", 2, "GPU芯片", None, 3, 300.0, 1, 1,
         "工业富联(601138)", 50.0, 80, 95, "scale+customer",
         "N/A(组装)", "同步", "same", 100.0, 8.0, "stable", "8-12%",
         "low", 0,
         json.dumps(["低附加值环节", "客户过于集中"]),
         json.dumps(["工业富联年报"]),
         "high"),

        ("AI算力", "800G光模块", 2, "光模块", None, 5, 350.0, 1, 1,
         "中际旭创(300308)", 50.0, 80, 90, "tech+scale",
         "800G OSFP", "领先1代", "advantage", 100.0, 12.0, "increasing", "30-40%",
         "low", 0,
         json.dumps(["AI Capex周期", "1.6T替代800G"]),
         json.dumps(["LightCounting", "公司年报"]),
         "high"),

        ("AI算力", "1.6T光模块", 2, "光模块", None, 3, 200.0, 1, 1,
         "中际旭创(300308)", 40.0, 75, 90, "tech",
         "1.6T DR8", "领先1-2代", "advantage", 100.0, 10.0, "increasing", "35-45%",
         "low", 0,
         json.dumps(["量产良率", "北美Capex节奏"]),
         json.dumps(["LightCounting"]),
         "medium"),

        ("AI算力", "EML激光器(50G/100G)", 2, "光芯片", None, 3, 120.0, 1, 1,
         "源杰科技(688498)", 35.0, 65, 80, "tech",
         "100G EML", "落后2-3年", "narrowing", 35.0, 6.0, "increasing", "45-60%",
         "high", 36,
         json.dumps(["良率爬坡", "Lumentum/Coherent降价打压"]),
         json.dumps(["源杰招股书", "行业报告"]),
         "medium"),

        ("AI算力", "冷板式液冷", 2, "液冷散热", None, 5, 150.0, 1, 1,
         "英维克(002837)", 25.0, 50, 70, "customer+tech",
         "CDU+冷板", "同步", "same", 90.0, 5.0, "increasing", "25-35%",
         "moderate", 12,
         json.dumps(["竞争加剧", "技术路径向浸没式切换"]),
         json.dumps(["CCID", "公司年报"]),
         "high"),

        ("AI算力", "AI服务器主板(30+层)", 2, "高端PCB", None, 3, 150.0, 1, 1,
         "沪电股份(002463)", 40.0, 75, 90, "tech+scale",
         "30-40层 HDI", "领先", "advantage", 100.0, 4.0, "stable", "25-35%",
         "low", 0,
         json.dumps(["PCB层数天花板", "IC载板替代"]),
         json.dumps(["Prismark", "公司年报"]),
         "high"),

        ("AI算力", "IC载板(FCBGA)", 2, "高端PCB", None, 4, 100.0, 1, 1,
         "深南电路(002916)", 30.0, 65, 80, "tech+scale",
         "FCBGA 16层", "落后1-2代", "narrowing", 20.0, 3.0, "increasing", "20-30%",
         "high", 24,
         json.dumps(["台/日/韩主导", "投资门槛极高"]),
         json.dumps(["Prismark"]),
         "medium"),

        ("AI算力", "白盒交换机整机", 2, "交换机", None, 4, 120.0, 1, 1,
         "锐捷网络(301165)", 30.0, 60, 80, "scale+channel",
         "800G交换机", "同步", "same", 80.0, 4.0, "stable", "15-25%",
         "moderate", 12,
         json.dumps(["交换芯片依赖进口", "白盒化压低利润"]),
         json.dumps(["IDC", "公司年报"]),
         "medium"),

        ("AI算力", "企业级SSD", 2, "存储", None, 4, 180.0, 1, 1,
         "江波龙(301308)", 25.0, 55, 75, "tech+channel",
         "PCIe 5.0 NVMe", "落后1代", "narrowing", 35.0, 3.0, "stable", "15-25%",
         "moderate", 18,
         json.dumps(["NAND周期", "三星/海力士竞争"]),
         json.dumps(["TrendForce", "公司年报"]),
         "medium"),

        ("AI算力", "刻蚀设备", 2, "半导体设备", None, 3, 250.0, 1, 1,
         "中微公司(688012)", 40.0, 75, 90, "tech",
         "5nm CCP/ICP", "落后1-2代", "narrowing", 15.0, 7.0, "increasing", "35-45%",
         "critical", 24,
         json.dumps(["EUV配套刻蚀仍是空白", "出口管制升级"]),
         json.dumps(["SEMI", "公司年报"]),
         "medium"),

        ("AI算力", "薄膜沉积设备", 2, "半导体设备", None, 3, 200.0, 1, 1,
         "拓荆科技(688072)", 35.0, 70, 85, "tech",
         "28nm+ ALD/CVD", "落后2-3代", "narrowing", 12.0, 6.0, "increasing", "35-45%",
         "critical", 36,
         json.dumps(["先进制程突破", "AMAT/TEL垄断"]),
         json.dumps(["SEMI", "公司年报"]),
         "medium"),

        ("AI算力", "量测/检测设备", 2, "半导体设备", None, 3, 110.0, 1, 1,
         "中科飞测(688361)", 25.0, 60, 75, "tech",
         "14nm+光学检测", "落后3代", "narrowing", 5.0, 4.0, "increasing", "40-55%",
         "critical", 48,
         json.dumps(["KLA绝对垄断", "0.1nm精度差距"]),
         json.dumps(["SEMI"]),
         "low"),

        ("AI算力", "DAC铜缆", 2, "高速铜连接", None, 3, 100.0, 1, 1,
         "兆龙互连(300913)", 35.0, 70, 85, "tech+customer",
         "800G DAC", "同步", "same", 90.0, 3.0, "stable", "20-30%",
         "low", 0,
         json.dumps(["AEC/AOC替代DAC", "料号生命周期短"]),
         json.dumps(["LightCounting"]),
         "medium"),
    ]

    conn.executemany("""
        INSERT OR REPLACE INTO chain_composition_detail (
            chain_name, node_name, depth_level, parent_node_name, parent_node_id,
            listed_company_count, tam_est_billion_cny, competitive_landscape_identifiable,
            meet_decomposition_threshold,
            market_leader, market_leader_share, cr3_concentration, cr5_concentration,
            competitive_moat_type,
            tech_generation, tech_gap_vs_global_leader, tech_gap_trend,
            localization_rate, value_pct_in_chain, value_trend, margin_profile,
            bottleneck_severity, substitute_timeline_months,
            key_risk_factors, data_sources, confidence_level
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, independent)

    # 6个不满足条件的聚合节点（不满足三条件，标记为需要聚合）
    aggregated = [
        ("AI算力", "硅光模块", 2, "光模块", None, 2, 80.0, 0, 0,
         "中际旭创", None, None, None, "tech",
         "1.6T硅光", "同步", "same", 80.0, 3.0, "increasing", "35-45%",
         "low", 0,
         json.dumps(["TAM<100亿"]),
         json.dumps(["LightCounting"]),
         "low",
         "TAM<100亿: 归入1.6T光模块"),

        ("AI算力", "DFB激光器(25G及以下)", 2, "光芯片", None, 3, 60.0, 1, 0,
         "源杰科技", 40.0, 65, 80, "tech",
         "25G DFB", "同步", "same", 60.0, 2.0, "stable", "25-35%",
         "low", 0,
         json.dumps(["TAM<100亿"]),
         json.dumps(["源杰招股书"]),
         "medium",
         "TAM<100亿: 归入光芯片"),

        ("AI算力", "CW激光器(硅光)", 2, "光芯片", None, 2, 40.0, 0, 0,
         "源杰科技", 50.0, 80, 95, "tech",
         "70mW CW", "同步", "advantage", 80.0, 1.5, "increasing", "45-60%",
         "low", 0,
         json.dumps(["TAM<100亿"]),
         json.dumps(["行业报告"]),
         "low",
         "TAM<100亿: 归入光芯片"),

        ("AI算力", "浸没式液冷", 2, "液冷散热", None, 2, 50.0, 1, 0,
         "高澜股份", 35.0, 70, 85, "tech",
         "浸没式Tank", "同步", "same", 40.0, 1.5, "increasing", "30-40%",
         "low", 0,
         json.dumps(["TAM<100亿"]),
         json.dumps(["CCID"]),
         "low",
         "TAM<100亿: 归入液冷散热"),

        ("AI算力", "交换芯片", 2, "交换机", None, 1, 50.0, 1, 0,
         "盛科通信(688702)", 10.0, 50, 50, "tech",
         "2.4T", "落后4代", "narrowing", 3.0, 2.0, "increasing", "45-60%",
         "critical", 60,
         json.dumps(["上市<3家"]),
         json.dumps(["公司年报"]),
         "low",
         "上市仅1家: 归入交换机"),

        ("AI算力", "HBM封装", 2, "存储", None, 2, 60.0, 1, 0,
         "长电科技", 60.0, 90, 95, "tech",
         "HBM2E封装", "落后1-2代", "narrowing", 5.0, 2.0, "increasing", "20-30%",
         "high", 24,
         json.dumps(["上市<3家"]),
         json.dumps(["TrendForce"]),
         "low",
         "上市仅2家: 归入HBM先进封装"),
    ]

    conn.executemany("""
        INSERT OR REPLACE INTO chain_composition_detail (
            chain_name, node_name, depth_level, parent_node_name, parent_node_id,
            listed_company_count, tam_est_billion_cny, competitive_landscape_identifiable,
            meet_decomposition_threshold,
            market_leader, market_leader_share, cr3_concentration, cr5_concentration,
            competitive_moat_type,
            tech_generation, tech_gap_vs_global_leader, tech_gap_trend,
            localization_rate, value_pct_in_chain, value_trend, margin_profile,
            bottleneck_severity, substitute_timeline_months,
            key_risk_factors, data_sources, confidence_level, notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, aggregated)

    conn.commit()
    print(f"[3/5] chain_composition_detail: {len(independent)} 独立节点 + {len(aggregated)} 聚合节点 ✅")

def populate_us_benchmarks(conn):
    """从 CSV 导入美股对标映射"""
    with open(CSV_PATH) as f:
        reader = csv.DictReader(f)
        rows = []
        for row in reader:
            rows.append((
                row["chain_name"], row["node_name"], row.get("composition_node_name", ""),
                row["us_ticker"], row["us_company_name"],
                float(row["us_market_cap_billion_usd"]),
                float(row["us_ps_ratio"]), float(row["us_pe_ratio"]),
                float(row["us_gross_margin_pct"]), float(row["us_rev_growth_3y_cagr"]),
                row["comparison_dimension"],
                float(row["ceiling_market_cap_multiple"]),
                float(row["tech_gap_years"]), row["tech_gap_trend"],
                row["tech_gap_metrics"], row["valuation_premium_discount"],
                row["valuation_rationale"],
                float(row["liquidity_discount_pct"]), float(row["geopolitical_discount_pct"]),
                row["data_as_of_date"], row["data_source"], row["notes"],
            ))
    conn.executemany("""
        INSERT OR REPLACE INTO us_benchmark_mapping (
            chain_name, node_name, composition_node_name,
            us_ticker, us_company_name,
            us_market_cap_billion_usd, us_ps_ratio, us_pe_ratio,
            us_gross_margin_pct, us_rev_growth_3y_cagr,
            comparison_dimension,
            ceiling_market_cap_multiple,
            tech_gap_years, tech_gap_trend, tech_gap_metrics,
            valuation_premium_discount, valuation_rationale,
            liquidity_discount_pct, geopolitical_discount_pct,
            data_as_of_date, data_source, notes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, rows)
    conn.commit()
    print(f"[4/5] us_benchmark_mapping: {len(rows)} 条 ✅")

def populate_capital_flows(conn):
    """填充资金流向追踪 —— AI算力赛道"""
    rows = [
        ("AI算力", "2025-Q4", "government",
         344.0, None, None,
         json.dumps(["中芯国际","华虹半导体","长电科技"]),
         "increasing", 18, 7.0,
         "工信部公告", "high"),

        ("AI算力", "2026-04", "vc_pe",
         25.0, None, None,
         json.dumps(["寒武纪","地平线","壁仞科技","燧原科技"]),
         "increasing", 30, 8.0,
         "IT桔子/CVSource(估计)", "medium"),

        ("AI算力", "2026-Q1", "industrial_capex",
         250.0, 38.0, None,
         json.dumps(["中际旭创","沪电股份","工业富联"]),
         "increasing", 9, 7.5,
         "北美CSP财报(Capex指引)", "high"),

        ("AI算力", "2026-Q1", "mutual_fund",
         None, None, None,
         json.dumps(["中际旭创","海光信息","寒武纪","沪电股份","中微公司"]),
         "increasing", 0, 3.5,
         "公募季报(Wind)", "high"),

        ("AI算力", "2026-05", "etf",
         45.0, None, None,
         json.dumps(["科创50ETF","芯片ETF","人工智能ETF"]),
         "increasing", 0, 4.0,
         "Wind ETF资金流", "high"),

        ("AI算力", "2026-Q1", "northbound",
         12.0, None, None,
         json.dumps(["中际旭创","工业富联","沪电股份"]),
         "stable", 0, 2.0,
         "沪深港通", "low"),
    ]

    conn.executemany("""
        INSERT OR REPLACE INTO capital_flow_tracker (
            chain_name, snap_date, flow_type,
            flow_amount_billion, flow_change_yoy, flow_change_qoq,
            top_recipients,
            flow_direction,
            lead_time_vs_stock_performance_months, predictive_power_score,
            data_source, confidence
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, rows)
    conn.commit()
    print(f"[5/5] capital_flow_tracker: {len(rows)} 条 ✅")

def verify(conn):
    """验证数据完整性"""
    tables = [
        ("track_heat_index", "赛道热度"),
        ("track_lifecycle", "产业生命周期"),
        ("chain_composition_detail", "产业链拆解"),
        ("us_benchmark_mapping", "美股对标"),
        ("capital_flow_tracker", "资金流向"),
    ]
    print("\n=== 数据完整性验证 ===")
    for table, label in tables:
        cnt = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        print(f"  {label:12s} ({table:30s}): {cnt} 条")
    
    # 关键验证
    independent = conn.execute(
        "SELECT COUNT(*) FROM chain_composition_detail WHERE meet_decomposition_threshold=1"
    ).fetchone()[0]
    aggregated = conn.execute(
        "SELECT COUNT(*) FROM chain_composition_detail WHERE meet_decomposition_threshold=0"
    ).fetchone()[0]
    print(f"\n  独立可分析节点: {independent} · 需聚合节点: {aggregated}")
    print(f"  美股对标覆盖: {conn.execute('SELECT COUNT(DISTINCT node_name) FROM us_benchmark_mapping').fetchone()[0]} 个节点")

if __name__ == "__main__":
    conn = sqlite3.connect(DB_PATH)
    try:
        run_schema(conn)
        populate_track_heat(conn)
        populate_track_lifecycle(conn)
        populate_chain_composition(conn)
        populate_us_benchmarks(conn)
        populate_capital_flows(conn)
        verify(conn)
        print("\n🎉 AI算力赛道产业链拆解数据填充完成！")
    finally:
        conn.close()
