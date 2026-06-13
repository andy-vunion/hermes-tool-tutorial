-- ============================================================
-- 产业链拆解体系 - 新增表结构设计
-- 用于 research.db，与现有 industry_chain/bom_analysis 等表协同
-- ============================================================

-- ----------------------------------------------------------
-- 1. 赛道热度追踪表 (Track Heat Index)
-- 每个赛道每个时间快照一条记录，支持时间序列回看
-- ----------------------------------------------------------
CREATE TABLE IF NOT EXISTS track_heat_index (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chain_name TEXT NOT NULL,               -- 赛道名称，如 'AI算力'、'人形机器人'
    snap_date TEXT NOT NULL,                -- 快照日期 YYYY-MM-DD
    -- 资金面指标
    etf_flow_monthly REAL,                  -- 板块ETF月度净流入(亿元)，数据源: Wind/东方财富
    inst_holding_change_qoq REAL,           -- 机构重仓股数季度环比变化(家数), 数据源: 公募季报
    northbound_flow_monthly REAL,           -- 北向资金月度净流入(亿元)，数据源: 沪深港通
    -- 基本面指标
    rev_growth_median REAL,                 -- 板块营收增速中位数(%), 数据源: 财报
    gross_margin_trend REAL,                -- 板块毛利率加权均值(%), 数据源: 财报
    roe_median REAL,                        -- 板块ROE中位数(%), 数据源: 财报
    earnings_revision_ratio REAL,           -- 盈利上调/下调比例, 数据源: 分析师一致预期
    -- 情绪面/交易面
    turnover_rate_avg REAL,                 -- 板块日均换手率(%), 数据源: 交易所
    analyst_coverage_change REAL,           -- 分析师覆盖数量季度变化, 数据源: 券商报告
    short_interest_ratio REAL,              -- 融券余额占比(%), 数据源: 交易所 (A股此项可能低)
    -- 政策面
    policy_mention_count INTEGER,           -- 国务院/部委文件中提及次数(季度), 数据源: 爬虫+关键词
    policy_level TEXT,                      -- 最高政策层级: national/ministry/provincial/none
    fiscal_support_billion REAL,            -- 财政/补贴投入规模(亿元), 数据源: 政府公告
    -- 产业面
    vc_pe_financing_monthly REAL,           -- VC/PE月度融资额(亿元), 数据源: IT桔子/CVSource
    new_company_registrations INTEGER,      -- 新增企业注册数(季度), 数据源: 企查查/天眼查
    patent_growth_yoy REAL,                 -- 专利申报同比增速(%), 数据源: 国家知识产权局
    -- 价格面
    sector_index_return_12m REAL,           -- 板块指数12个月收益率
    alpha_vs_benchmark_12m REAL,            -- 相对沪深300的12个月Alpha
    -- 综合评分
    heat_composite_score REAL,              -- 赛道综合热度评分(0-100), 加权合成
    heat_tier TEXT,                         -- 热度等级: hotspot/warm/neutral/cold
    data_confidence TEXT,                   -- 数据可信度: high/medium/low
    created_at TEXT DEFAULT (datetime('now')),
    UNIQUE(chain_name, snap_date)
);

-- ----------------------------------------------------------
-- 2. 赛道生命周期表 (Track Lifecycle)
-- 每个赛道每年一条记录（或里程碑事件触发更新）
-- ----------------------------------------------------------
CREATE TABLE IF NOT EXISTS track_lifecycle (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chain_name TEXT NOT NULL,
    snap_date TEXT NOT NULL,                -- 评估日期
    lifecycle_stage TEXT NOT NULL,          -- concept/import/growth/maturity/decline
    stage_confidence TEXT,                  -- 阶段判断置信度: high/medium/low
    -- 生命周期判断依据
    rev_growth_trajectory TEXT,             -- 营收增速轨迹描述: accelerating/decelerating/stable
    industry_penetration_pct REAL,          -- 行业渗透率(%)
    competitor_count INTEGER,              -- 竞争格局: 主要玩家数量
    competitor_count_trend TEXT,            -- 玩家数量趋势: increasing/stable/consolidating
    gross_margin_trend_direction TEXT,      -- 毛利率趋势: expanding/stable/compressing
    capex_intensity TEXT,                   -- 资本开支强度判断: high/moderate/low
    -- 政策信号追踪
    policy_signal_strength TEXT,            -- 政策信号强度: strong/moderate/weak/none
    latest_policy_date TEXT,                -- 最近一次重大政策日期
    latest_policy_summary TEXT,             -- 政策摘要
    policy_to_revenue_lag_months INTEGER,   -- 政策→营收兑现的估计时滞(月)
    -- 国产替代指标
    localization_rate REAL,                 -- 国产化率(%)
    localization_rate_trend TEXT,           -- 趋势: rising/fast_rising/stable/declining
    import_dependency_level TEXT,           -- 进口依赖度: critical/high/moderate/low
    -- 产能周期
    capacity_cycle TEXT,                    -- capacity_expansion/stabilization/oversupply/digestion
    utilization_rate_est REAL,              -- 估计产能利用率(%)
    expansion_plans_summary TEXT,           -- 扩产计划摘要
    -- 综合判断
    is_policy_driven_pseudo_demand INTEGER, -- 是否为政策催化的伪需求 0/1 (assumption flag)
    pseudo_demand_evidence TEXT,            -- 伪需求判断依据
    growth_sustainability_score REAL,       -- 成长可持续性评分(0-10)
    created_at TEXT DEFAULT (datetime('now')),
    UNIQUE(chain_name, snap_date)
);

-- ----------------------------------------------------------
-- 3. 产业链拆解明细表 (Chain Decomposition Detail)
-- 对 industry_chain 的补充——层次化拆解 + 子节点关系
-- ----------------------------------------------------------
CREATE TABLE IF NOT EXISTS chain_composition_detail (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chain_name TEXT NOT NULL,
    node_name TEXT NOT NULL,                -- 细分节点名称, 如 '光芯片→EML激光器→100G EML'
    depth_level INTEGER NOT NULL,           -- 拆解层级: 1=一级(光芯片), 2=二级(激光器芯片), 3=三级(100G EML)
    parent_node_name TEXT,                  -- 父节点名称 (关联 industry_chain.node_name)
    parent_node_id INTEGER,                -- 父节点ID (关联 industry_chain.id)
    -- 拆解粒度判断三要素
    listed_company_count INTEGER,           -- 上市公司数量(含拟IPO)
    tam_est_billion_cny REAL,              -- TAM估算(亿元人民币)
    competitive_landscape_identifiable INTEGER, -- 竞争格局是否可辨识 0/1
    meet_decomposition_threshold INTEGER,   -- 是否满足拆解三条件 0/1
    -- 竞争格局
    market_leader TEXT,                     -- 市场龙头(公司名/代码)
    market_leader_share REAL,              -- 龙头市占率(%)
    cr3_concentration REAL,                -- CR3集中度(%)
    cr5_concentration REAL,                -- CR5集中度(%)
    competitive_moat_type TEXT,            -- 护城河类型: tech/scale/customer/channel/policy
    -- 技术指标
    tech_generation TEXT,                   -- 当前技术代际, 如 '100G','5nm'
    tech_gap_vs_global_leader TEXT,         -- 与全球领先的差距, 如 '落后2代'
    tech_gap_trend TEXT,                    -- 差距趋势: narrowing/stable/widening
    localization_rate REAL,                 -- 该细分国产化率(%)
    -- 价值量
    value_pct_in_chain REAL,               -- 在产业链总价值中的占比(%)
    value_trend TEXT,                       -- 价值占比趋势: increasing/stable/decreasing
    margin_profile TEXT,                    -- 毛利率概况, 如 '35-45%'
    -- 关键风险
    bottleneck_severity TEXT,              -- 卡脖子程度: critical/high/moderate/low
    substitute_timeline_months INTEGER,     -- 国产替代估计时间(月)
    key_risk_factors TEXT,                  -- JSON array of risk factors
    -- 数据追溯
    data_sources TEXT,                      -- 数据来源, JSON array
    confidence_level TEXT,                  -- 数据置信度: high/medium/low
    notes TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

-- ----------------------------------------------------------
-- 4. 美股对标映射表 (US Benchmark Mapping)
-- 每个产业链节点 → 对标美股 + 关键指标
-- ----------------------------------------------------------
CREATE TABLE IF NOT EXISTS us_benchmark_mapping (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chain_name TEXT NOT NULL,
    node_name TEXT NOT NULL,                -- 关联 industry_chain.node_name
    composition_node_name TEXT,             -- 关联 chain_composition_detail.node_name (可选, 更细粒度)
    -- 美股对标
    us_ticker TEXT NOT NULL,               -- 美股代码, 如 'NVDA'
    us_company_name TEXT NOT NULL,         -- 美股公司名称
    us_market_cap_billion_usd REAL,        -- 美股市值(十亿美元)
    us_ps_ratio REAL,                      -- 美股PS倍数
    us_pe_ratio REAL,                      -- 美股PE倍数
    us_gross_margin_pct REAL,              -- 美股毛利率(%)
    us_rev_growth_3y_cagr REAL,           -- 美股3年营收CAGR(%)
    -- 对标维度
    comparison_dimension TEXT,             -- 对标类型: ceiling/target/tech_gap/valuation_anchor
    -- 天花板参照
    ceiling_market_cap_multiple REAL,      -- 美股市值 / A股对标市值天花板倍数
                                            -- e.g. 5x 表示A股市值天花板约为美股的1/5
    -- 技术代差
    tech_gap_years REAL,                   -- 技术代差(年)
    tech_gap_trend TEXT,                   -- 代差趋势: narrowing/stable/widening
    tech_gap_metrics TEXT,                 -- 技术代差量化指标, JSON: {"先进制程":"4nm vs 7nm", ...}
    -- 估值锚
    valuation_premium_discount TEXT,       -- premium/fair/discount 相对美股
    valuation_rationale TEXT,              -- 估值差异原因
    -- 流动性/地缘折价
    liquidity_discount_pct REAL,           -- 流动性折价(%)
    geopolitical_discount_pct REAL,        -- 地缘政治折价(%)
    data_as_of_date TEXT,                  -- 数据截止日期
    data_source TEXT,                      -- 数据源
    notes TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);

-- ----------------------------------------------------------
-- 5. 未上市公司追踪表 (Pre-IPO & Private Company Tracking)
-- ----------------------------------------------------------
CREATE TABLE IF NOT EXISTS private_company_tracker (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chain_name TEXT NOT NULL,
    node_name TEXT NOT NULL,                -- 所属产业链节点
    company_name TEXT NOT NULL,
    -- 上市进程状态
    ipo_status TEXT NOT NULL,               -- pre_ipo/guidance_filing/listing_hearing/registered/long_shot
    ipo_exchange TEXT,                      -- 目标交易所: STAR/ChiNext/BSE/HK/US
    ipo_expected_date TEXT,                 -- 预计上市日期
    ipo_filing_date TEXT,                   -- 受理/辅导备案日期
    ipo_progress_detail TEXT,              -- 进展细节
    -- 公司基本信息
    founded_year INTEGER,
    headquarters TEXT,
    employee_count INTEGER,
    -- 融资信息
    latest_financing_round TEXT,            -- 最新融资轮次: A/B/C/D/Pre-IPO
    latest_financing_amount_billion REAL,   -- 最新融资额(亿元)
    total_financing_billion REAL,           -- 累计融资额(亿元)
    post_money_valuation_billion REAL,      -- 投后估值(亿元)
    key_investors TEXT,                     -- 主要投资方, JSON array
    -- 业务规模估算
    estimated_revenue_billion REAL,         -- 估计营收(亿元)
    estimated_revenue_growth_pct REAL,      -- 估计营收增速(%)
    estimated_gross_margin_pct REAL,        -- 估计毛利率(%)
    customer_count INTEGER,                 -- 客户数/付费用户数
    key_customers TEXT,                     -- 主要客户, JSON array
    capacity_plan TEXT,                     -- 产能规划描述
    -- 技术评估
    tech_description TEXT,                  -- 核心技术描述
    tech_maturity TEXT,                     -- 技术成熟度: lab/pilot/mass_production
    tech_position TEXT,                     -- 技术地位: leader/challenger/niche
    patent_count INTEGER,                  -- 专利数
    -- 对标
    peer_listed_company TEXT,               -- 对标已上市公司, 如 '中际旭创(300308)'
    valuation_discount_vs_listed_pct REAL, -- 估值折扣 vs 已上市对标(%)
    -- 跟踪
    data_source TEXT,                       -- 数据源: 证监会官网/IT桔子/企查查/36氪
    data_confidence TEXT,                   -- high/medium/low
    last_updated TEXT,
    notes TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    UNIQUE(chain_name, company_name)
);

-- ----------------------------------------------------------
-- 6. 资金流向追踪表 (Capital Flow Tracking)
-- 多层级资金流向：政府/VC/二级/产业
-- ----------------------------------------------------------
CREATE TABLE IF NOT EXISTS capital_flow_tracker (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chain_name TEXT NOT NULL,
    snap_date TEXT NOT NULL,                -- 快照周期: YYYY-MM (月度) 或 YYYY-QN (季度)
    flow_type TEXT NOT NULL,                -- government/vc_pe/mutual_fund/etf/industrial_capex/northbound
    flow_amount_billion REAL,              -- 资金量(亿元)
    flow_change_yoy REAL,                  -- 同比变化(%)
    flow_change_qoq REAL,                  -- 环比变化(%)
    -- 详情
    top_recipients TEXT,                    -- 最大受益标的, JSON array
    flow_direction TEXT,                    -- increasing/stable/decreasing
    -- 预测力评估
    lead_time_vs_stock_performance_months INTEGER, -- 领先股价表现的月数(回测结果)
    predictive_power_score REAL,            -- 预测力评分(0-10), 基于回测IC
    data_source TEXT,
    confidence TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    UNIQUE(chain_name, snap_date, flow_type)
);

-- ----------------------------------------------------------
-- 7. 赛道Gate筛选结果表 (Track Gate Result)
-- M0→M1之间的赛道前置筛选输出
-- ----------------------------------------------------------
CREATE TABLE IF NOT EXISTS track_gate_result (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    snap_date TEXT NOT NULL,                -- 筛选日期
    chain_name TEXT NOT NULL,              -- 赛道名称
    -- 赛道硬门槛 (一票否决项)
    tg1_listed_company_count_pass INTEGER,  -- ≥3家上市公司?
    tg2_tam_threshold_pass INTEGER,        -- TAM ≥ 100亿?
    tg3_competition_identifiable_pass INTEGER, -- 竞争格局可辨识?
    hard_gate_passed INTEGER,              -- 硬门槛全部通过? 0/1
    -- 赛道热度评分 (0-100)
    heat_score REAL,                       -- 综合热度评分
    heat_fundamental REAL,                 -- 基本面得分
    heat_capital REAL,                     -- 资金面得分
    heat_policy REAL,                      -- 政策面得分
    heat_industry REAL,                    -- 产业面得分
    heat_price REAL,                       -- 价格面得分
    -- 生命周期判断
    lifecycle_stage TEXT,                  -- 当前生命周期阶段
    lifecycle_investable INTEGER,          -- 是否处于可投资阶段(concept期可能过早) 0/1
    -- 美股对标天花板
    ceiling_market_cap_total_billion_cny REAL, -- 美股对标总市值天花板(亿人民币)
    avg_tech_gap_years REAL,               -- 平均技术代差(年)
    -- 综合
    track_tier TEXT,                        -- 赛道分级: S/A/B/C/D
    pass_for_stock_gate INTEGER,           -- 是否通过赛道Gate, 进入个股M0→M1流程 0/1
    rejection_reason TEXT,                  -- 未通过原因
    -- 权重分配 (用于后续个股Gate评分)
    node_weight_overrides TEXT,             -- JSON: {"光模块": 0.15, "GPU芯片": 0.20, ...}
    benchmark_gross_margin REAL,            -- 赛道毛利率benchmark(用于个股硬门槛HG3)
    benchmark_rev_growth REAL,              -- 赛道营收增速benchmark(用于个股硬门槛HG1)
    benchmark_pe_ceiling REAL,              -- 赛道PE合理天花板(用于估值参考)
    created_at TEXT DEFAULT (datetime('now')),
    UNIQUE(snap_date, chain_name)
);

-- ----------------------------------------------------------
-- 8. 政策信号追踪表 (Policy Signal Tracking)
-- ----------------------------------------------------------
CREATE TABLE IF NOT EXISTS policy_signal_tracker (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chain_name TEXT NOT NULL,
    signal_date TEXT NOT NULL,              -- 政策发布日期
    signal_source TEXT NOT NULL,            -- 来源: 总书记讲话/国常会/政治局/部委/地方
    signal_level TEXT NOT NULL,             -- national/ministry/provincial/municipal
    signal_document TEXT,                   -- 文件名/讲话标题
    signal_summary TEXT,                    -- 核心内容摘要
    signal_keywords TEXT,                   -- 关键词, JSON array
    signal_strength TEXT,                   -- strong/moderate/weak (根据措辞强度)
    -- 涉及金额 (若有)
    fiscal_amount_billion REAL,            -- 涉及财政金额(亿元)
    fiscal_type TEXT,                       -- 补贴/税收优惠/直接投资/政府采购
    -- 影响评估
    estimated_revenue_impact_billion REAL,  -- 估计对产业营收影响(亿元)
    implementation_progress TEXT,           -- 落实情况: proposed/approved/implementing/completed
    impact_lag_months_est INTEGER,         -- 估计政策→业绩传导月数
    data_source TEXT,
    confidence TEXT,
    created_at TEXT DEFAULT (datetime('now'))
);

-- ----------------------------------------------------------
-- 索引
-- ----------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_thi_chain_date ON track_heat_index(chain_name, snap_date);
CREATE INDEX IF NOT EXISTS idx_tlc_chain_date ON track_lifecycle(chain_name, snap_date);
CREATE INDEX IF NOT EXISTS idx_ccd_chain_node ON chain_composition_detail(chain_name, node_name);
CREATE INDEX IF NOT EXISTS idx_ccd_parent ON chain_composition_detail(parent_node_id);
CREATE INDEX IF NOT EXISTS idx_ubm_chain_node ON us_benchmark_mapping(chain_name, node_name);
CREATE INDEX IF NOT EXISTS idx_pct_chain_status ON private_company_tracker(chain_name, ipo_status);
CREATE INDEX IF NOT EXISTS idx_cft_chain_date ON capital_flow_tracker(chain_name, snap_date);
CREATE INDEX IF NOT EXISTS idx_tgr_chain_date ON track_gate_result(chain_name, snap_date);
CREATE INDEX IF NOT EXISTS idx_pst_chain_date ON policy_signal_tracker(chain_name, signal_date);
