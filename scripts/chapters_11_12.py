# -*- coding: utf-8 -*-
"""
Chapters 11 - 12 for EU5 Mechanics Compendium (1.4.9) — Overhauled Edition.
Covers 1337 Scenarios, Regional Country Lists, Formables (Tiers 1-4), Dynastic Tags & Events,
National Missions, DLC Expansion Mechanics, Game Rules/Achievements, UI Reading & Automation,
EU4/Vic3 Accounting Bridge, and the Verified 1.4.8-1.4.9 Changelog.
"""
from html import escape
import json
import os

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")


def T(cid, label):
    return f'<button type="button" class="term" data-concept="{cid}">{label}</button>'


def _build_ch12_patch_html():
    vu_path = os.path.join(DATA_DIR, "version_update.json")
    if not os.path.exists(vu_path):
        return "<p>1.4.8–1.4.9 更新档案尚未生成，请先运行 <code>extract_game_data.py</code>。</p>"
    with open(vu_path, encoding="utf-8") as f:
        vu = json.load(f)

    checks_rows = "".join(
        f'<tr><td><code>{escape(str(c.get("version", "")))}</code></td>'
        f'<td><strong>{escape(str(c.get("topic", "")))}</strong><br><small style="color:var(--ink-muted)">{escape(str(c.get("confidence", "")))}</small></td>'
        f'<td>{escape(str(c.get("summary", "")))}</td></tr>'
        for c in vu.get("checks", [])
    )

    tc_items = "".join(
        f'<li><strong>{escape(str(tc.get("zh", tc.get("id", ""))))}</strong>（<code>{escape(str(tc.get("id", "")))}</code>）：总计 <strong>{tc.get("total", 0)}</strong> 条，本轮更新 <strong>{tc.get("changed_count", 0)}</strong> 条</li>'
        for tc in vu.get("tableChanges", [])
    )

    unres_items = "".join(f"<li>{escape(u)}</li>" for u in vu.get("unresolved", []))

    return f"""
<p>当前手册对照基准版本：<strong>EU5 {escape(str(vu.get("version", "1.4.9")))}</strong>（官方校验码 <code>{escape(str(vu.get("officialChecksum", "3ed0")))}</code> · Steam Build <code>{escape(str(vu.get("steamBuild", "26655995")))}</code> · 对比基线 {escape(str(vu.get("previous", "1.4.7")))} · 核对日期 {escape(str(vu.get("date", "")))}）。下表完整收录全部 <strong>{len(vu.get("checks", []))} 项</strong> 官方 1.4.8–1.4.9 机制修订与源码核对结果：</p>
<table class="data-table">
  <thead><tr><th>版本</th><th>核对主题 / 置信度</th><th>机制更新与代码依据说明</th></tr></thead>
  <tbody>{checks_rows}</tbody>
</table>
<h3>本轮数据名录更新统计（10 类核心表变化）</h3>
<ul>{tc_items}</ul>
<div class="callout warn"><strong>源码与实机核对边界说明（Verification Limits）</strong>：<ul>{unres_items}</ul></div>
"""


CHAPTERS_11_12 = [
    # =========================================================================
    # CHAPTER 11
    # =========================================================================
    {
        "id": "ch11",
        "slug": "ch11-scenarios-missions-dlc.html",
        "num": "11",
        "pillar": "diplomacy",
        "title": "开局剧本、成立国家层级、国别事件、使命包与扩展包机制",
        "en": "Scenarios, Formable Tiers, Country Events, Mission Packs & Expansion Mechanics",
        "subtitle": "梳理 1337 剧本 13 大地理分区国家档案、成立层级（Tier 1–4）与王朝显示国号辨析、国别事件等待时间公式、使命接取快照规则，以及《凤凰宿命》与《跨越海峡》专属机制。",
        "upstream": [
            ("1337.4.1 剧本设定与国家定义", "directory.html#starting-scenarios", "载入 2,354 个国家标签的初始领土、政体、文化宗教与开局战争"),
            ("版图扩张与文化/宗教资格", "ch06-culture-religion.html#culture-status", "决定可成立国家的可见条件（Potential）与执行条件（Allow）"),
            ("历史局势与灾难触发", "ch07-ages-colonial.html#situations-disasters", "驱动拜占庭凤凰宿命、土耳其崛起与直布罗陀海峡之战进程"),
        ],
        "engine": "区分「国家基础标签」「显示国号」「成立层级」与「国际组织身份」，按月概率判定 4,213 条国别事件，按接取时快照推进可选使命链，并结算扩展包专属行动。",
        "downstream": [
            ("新标签专属革新与历史事件", "ch07-ages-colonial.html#research-advances", "注意区分按文化开放的革新与直接绑定国家标签（如 POR/CHI）的事件"),
            ("复兴罗马或黄金世纪奖励", "ch10-diplomacy-subjects.html#pu-and-ios", "完成灾难或局势终局永久保留特殊内阁行动、宣战理由与官僚槽"),
            ("本局铁人成就资格校验", "ch12-gameplay-automation-updates.html#rules-achievements", "启用通用使命包会关闭本局成就资格，成就档须在开局规则保持关闭"),
        ],
        "redlines": [
            ("目标层级 > 当前层级", "成立国家层级递进规则", "成立新国家要求目标成立层级（1–4）严格高于当前成立层级（与伯/公/王/帝行政等级分开计算）"),
            ("期望等待 = 1 ÷ p", "动态历史事件触发估算", "合格窗口期内月概率为 p 时，n 个合格月内触发率为 1 − (1 − p)ⁿ，平均等待月数为 1 ÷ p"),
            ("弃 10 年 / 完 20 年", "使命链重选冷却期", "部分使命按接取当日数值设定目标（如海军占比 +5%）；放弃后冷却 10 年，完成后冷却 20 年"),
            ("≥146 地 vs ≤100 地", "凤凰宿命复兴结算线", "土耳其崛起已结束、安纳托利亚对手均 ≤100 地且拜占庭系 ≥146/150 地可进入《凤凰复兴》"),
        ],
        "sections": [
            {
                "id": "scenarios-countries",
                "title": "01 · 1337 剧本结构与 13 大地理分区国家名录",
                "en": "1337 Scenario Structure & 13 Regional Country Directories",
                "html": f"""
<p>标准剧本始于 <strong>1337 年 4 月 1 日</strong>，止于 <strong>1836 年 12 月 31 日</strong>。选国界面同时标注三种独立信息：<strong>推荐玩法方向</strong>（经济 Economy / 政治 Politics / 扩张 Expansion）、<strong>推荐玩家熟练度</strong>（新手至专家，决定提示详略）以及<strong>国家开局处境难度</strong>（极易至极难）。</p>
<ul>
  <li><strong>2,354 个国家定义与 13 大分区目录</strong>：名录库按开局首都所在地理范围划分为非洲、中北亚、东亚、东欧、德意志、日本、中东、北美、大洋洲、南美、南亚、东南亚与西欧 13 个区域名录（含开局在场国家及后续由事件/叛乱登场的标签），并分开记录各地点的所有权、当前占领控制与历史核心，以及 1337 开局既有的对外战争与苏格兰王位内战等初始战事。</li>
</ul>
"""
            },
            {
                "id": "formables-events",
                "title": "02 · 163 个可成立国家、成立层级与「国号 / 标签 / 组织」辨析",
                "en": "163 Formable Countries, Formation Tiers & Tag vs Name vs IO",
                "html": f"""
<p>成立新国家（{T('formable_country','Formable Countries')}）由<strong>可见条件（Potential）</strong>与<strong>执行条件（Allow）</strong>共同控制：未单独写明区域占比时默认要求拥有指定范围 <strong>100%</strong> 地点；同时<strong>目标国家的「成立层级（1–4 级）」必须严格高于本国现有成立层级</strong>（该层级与伯国/公国/王国/帝国行政等级相互独立）：</p>

<table class="data-table">
  <thead><tr><th>可成立国家示例</th><th>成立层级</th><th>地理范围控制比例要求</th><th>文化、宗教或局势附加条件</th></tr></thead>
  <tbody>
    <tr><td><strong>诺森伯兰（NOL）</strong></td><td>第 1 级</td><td>苏格兰低地 + 诺森布里亚地区合计 50%</td><td>英语文化语言；启用合理成立规则</td></tr>
    <tr><td><strong>尼德兰 / 瑞典</strong></td><td>第 2 级</td><td>低地五地区 30% / 瑞典及芬兰四地区 75%</td><td>尼德兰文化组 / 瑞典文化</td></tr>
    <tr><td><strong>斯堪的纳维亚 / 大不列颠 / 埃及</strong></td><td>第 3 级</td><td>各自指定区域 <strong>75%</strong>（蒙古 MGO 为蒙古区 85%）</td><td>瑞典（层级2）可升格斯堪的纳维亚（层级3）；大不列颠需百年战争已结束；埃及排除开局马穆鲁克</td></tr>
    <tr><td><strong>西班牙（SPA） / 重建蒙古帝国（MGE）</strong></td><td>第 4 级</td><td>伊比利亚区域 75% / 横跨多区域版图 85%</td><td>西班牙需伊比利亚文化组、基督教且半岛无独立异教政权</td></tr>
  </tbody>
</table>

<p><strong>标签、显示国号与国际组织的三重区分（以「中国」相关概念为例）</strong>：</p>
<ul>
  <li><strong>国家标签与王朝显示国号</strong>：1337 开局统治中原的元朝使用基础标签 <code>CHI</code>（另有历史标签 <code>YUA</code>，明朝标签为 <code>MNG</code>）；可成立的「中华（China）」检查华北、华南、华东、华西四区域拥有 <strong>70%</strong> 地点、主流文化属中华文化组、天朝组织已不存在且红巾军未在活跃；而满洲（<code>MCH</code>）触发《肇清告谕》事件时，则是先成立 <code>CHI</code> 再将画面显示国号改写为「清（Qīng）」。同理，成立罗姆（Rûm）显示名用 <code>RUM</code> 而底层标签转为 <code>TUR</code>。</li>
  <li><strong>天朝（Middle Kingdom）国际组织</strong>：独立于单一国家标签之外的跨国组织，控制成员贡礼、天命与防御义务。查阅专属革新与 <strong>4,213 条国别事件</strong> 时，需看清脚本检查的是<strong>文化</strong>（如葡萄牙海军革新按文化开放）还是<strong>特定国家标签</strong>（如哥伦布事件 <code>flavor_por.1</code> 在 1485–1520 年窗口按月概率 5% 直接检查 <code>POR</code> 标签，12 个合格月内触发率约 <code>1 − 0.95¹² ≈ 46.0%</code>）。</li>
</ul>
"""
            },
            {
                "id": "missions-system",
                "title": "03 · 11 组国家使命包与 178 项决议：快照目标与冷却规则",
                "en": "11 National Mission Packs & 178 Decisions",
                "html": f"""
<ul>
  <li><strong>使命包开关与成就资格</strong>：默认标准开局规则下<strong>任务包（Mission Packs）处于关闭状态</strong>以保留铁人成就资格；若在开局规则开启任务包（用于引导学习经济、政治与扩张流程，同时关闭本局成就），国家可从候选池中选用通用或专项{T('mission','使命')}链。</li>
  <li><strong>接取快照定标与冷却期</strong>：许多{T('mission_task','使命任务')}在点击接取瞬间读取当前国家数值并生成动态达标线（例如贸易使命要求将海军市场份额提升至 <code>接取时比例 + 5 个百分点</code>，上限 100%）。主动中止使命后需冷却 <strong>10 年</strong> 方可重选同一使命链，完整完成后冷却 <strong>20 年</strong>。<strong>178 项国家决议</strong>（含开凿苏伊士/巴拿马/基尔运河等大型工程与政教改革）则在常规成就局全程开放，满足可见与执行条件即可付费发动。</li>
</ul>
"""
            },
            {
                "id": "dlc-expansions",
                "title": "04 · 扩展包机制拆解：《凤凰宿命》《跨越海峡》与古迹包",
                "en": "Expansion Mechanics: Fate of the Phoenix, Across the Pillars & Monuments",
                "html": f"""
<ul>
  <li><strong>《拜占庭：凤凰宿命（Fate of the Phoenix）》</strong>：<br>
    • <strong>凤凰宿命灾难与双结局</strong>：1337 传统时代拜占庭开局触发，期间雇佣兵签约溢价 +50%、官僚维护效率 +20%、造 CB 速度 +20%，伴随行省抗命与逃兵事件。结束需安纳托利亚所有贝伊政体或突厥/土库曼文化国家（含属国）均 <strong>≤ 100 地点</strong>，并满足发展路线（土耳其崛起已结束且拜占庭系 <strong>≥ 150 地点</strong>）或 1401 年后时间路线；结算时若土耳其崛起已结束且拜占庭系 <strong>≥ 146 地点</strong>，进入<strong>《凤凰复兴》</strong>（解锁恢复罗马疆界 CB、永久保留亲希腊与拉丁军国主义两项内阁行动及20年军队复兴加成），否则进入《衰败时代仍将继续》（失去两行动且稳定正统各 −20）。<br>
    • <strong>东部教会与复兴希腊古典信仰（Reestablish Hellenism）</strong>：开放借出圣像、弥合东西教会分裂，以及高难度的复兴希腊多神教行动——需当前或曾为 <code>BYZ</code>、拉丁化—罗马派价值轴严格越过 <strong>±90</strong>、本国或属国完整拥有跨越希腊至埃及黎凡特的全部 <strong>22 处古典圣地</strong>，支付 100 宗教影响力与 50 稳定度改宗，并在首都生成 10% 人口的初始宗教运动。</li>
  <li><strong>《跨越海峡（Across the Pillars）》</strong>：<br>
    • <strong>海峡之战与黄金世纪</strong>：卡斯蒂利亚、格拉纳达、摩洛哥围绕直布罗陀海峡角逐主权与影响力，胜者可在发现时代开启持续 100 年的「黄金世纪」局势（满期保持 ≥75 殖民优势可永久保留达瓦殖民行政额外官僚槽；另有召引安达卢西亚工匠每月每地 +0.02 发展度、征募加齐在 6 个月内从友好穆斯林省份迁入 25% 士兵与 15% 劳工至首都省）。<br>
    • <strong>运宝船队与探险</strong>：新西班牙船队与大陆加利恩船队各自按 <strong>5 年冷却</strong> 装载美洲对应区域属国生产的金银返航；另含黄金城（El Dorado）与青春泉远征。</li>
  <li><strong>古代纪念建筑与圣地外观包</strong>：外观包文件登记地图 3D 模型与地点插画；实际机制加成请分别在名录库的「<strong>圣地（Holy Sites）</strong>」（如麦加克尔白重要性 5）或「<strong>开局艺术品</strong>」（如纪念建筑传统倍率 2.5 / 影响倍率 1.0）条目核对。</li>
</ul>
"""
            },
        ],
        "discussion": {
            "title": "查阅指引 · 为什么满足了领土比例仍点不了「成立国家」？",
            "html": """
<ul>
  <li><strong>按顺序核对四项隐藏约束</strong>：① 本国当前「成立层级」是否已大于或等于目标国家层级（同级或降级成立被规则禁止）；② 开局规则中的「可成立国家限制」是否排除了非历史项；③ 目标定义是否排除了你的开局标签（如马穆鲁克不可点普通成立埃及）或要求特定局势已结束（如成立大不列颠需百年战争已结算，成立中华需天朝与红巾军已结束）；④ 指定核心地标是否由本国<strong>直接拥有</strong>而非交在属国名下。</li>
</ul>
"""
        },
        "quick_links": [
            ("163 个可成立国家完整条件", "directory.html#formable-countries"),
            ("4,213 条国别历史事件名录", "directory.html#country-events"),
            ("178 项决议 & 11 组使命包", "directory.html#decisions"),
            ("2,354 国家定义与地区开局表", "directory.html#country-definitions"),
        ],
    },

    # =========================================================================
    # CHAPTER 12
    # =========================================================================
    {
        "id": "ch12",
        "slug": "ch12-gameplay-automation-updates.html",
        "num": "12",
        "pillar": "territory",
        "title": "开局规则、界面读数通则、自动化托管矩阵与 1.4.9 更新核对",
        "en": "Game Rules, UI Reading Conventions, Automation Settings & 1.4.9 Changelog",
        "subtitle": "归纳全书存量/流量与百分点/百分比读数通则、31 项开局规则与成就勘误、七大系统自动化委托细节、EU4/Vic3 玩家转场四笔对账，以及 42 项 1.4.8–1.4.9 版本修订清单。",
        "upstream": [
            ("前 11 章全部经济、内政与军事公式", "metrics.html", "理解每个数值的底层决定因素后，方能判断哪些环节适合交给自动化"),
            ("1.4.8–1.4.9 官方补丁与本机脚本文件", "glossary.html", "对齐最新实装参数与界面提示拆项顺序"),
        ],
        "engine": "以「地图模式定位异常地点 → 地点/国家面板悬停核对分项 → 统计账本同口径横向比较 → 分层设置自动化与储金底线」构成日常运营闭环。",
        "downstream": [
            ("31 项核心数值修正来源反查器", "metrics.html", "随时检索任一核心指标或全部 1,364 项修正的具体建筑、特权、改革与革新来源"),
            ("22 大速查表与 72 全量名录库", "ledgers.html#building_types", "按清晰中文词条快速核查 501 种建筑、401 种兵种与全部制度条目"),
        ],
        "redlines": [
            ("普通+铁人+关任务包", "获取成就三项前提", "简单/极简单难度、允许切换国家或开启任务包均会关闭本局成就资格"),
            ("百分点 vs 相对百分比", "全书公式读数铁律", "60% 提高 5 个百分点为 65%；在 60% 原值上提高 5% 相对修正则为 63%"),
            ("税基 × 12 金币", "自动贿赂阶层单次扣款", "开启阶层自动化后每 6 个月检查贿赂，预算紧张时需留足现金或手动控管"),
            ("Build 26655995 / 3ed0", "本手册核对基准版本", "覆盖至 EU5 1.4.9 全部 42 项机制核对与 10 张核心表差异刷新"),
        ],
        "sections": [
            {
                "id": "rules-achievements",
                "title": "01 · 开局规则、成就勘误与顶栏「存量 vs 流量」读数通则",
                "en": "Game Rules, Achievement Errata & Topbar Stock vs Flow Conventions",
                "html": f"""
<p><strong>1. 开局规则（31 项）与成就核对要点（87 项成就见名录库）</strong>：</p>
<ul>
  <li><strong>成就启用条件</strong>：须启用铁人模式、玩家难度至少为普通、关闭允许切换国家，且<strong>关闭任务包（Mission Packs）</strong>。时间步进可在开局规则选择按日（默认）或按小时。</li>
  <li><strong>重要成就脚本核对勘误</strong>：成就《众城之城（City of Cities）》英文界面虽写作 <code>core province</code>，底层脚本实际检查的是<strong>任一单个核心地点（Core Location）的发展度达到 100</strong>（同省两处 60 与 40 不可相加）；《坚守阿特拉斯》要求摩洛哥统合苏斯与摩洛哥两地区后完成集权（≥25 且王权 &gt;45%）或分权（≥50 且部落满意 &gt;65%）路线；《海峡事务》要求卡斯蒂利亚在直布罗陀南北两岸指定核心城市均建有海岸要塞或海军炮台。</li>
</ul>

<p><strong>2. 全游戏界面读数与单位通则</strong>：</p>
<ul>
  <li><strong>存量（Stock）与流量（Flow）分离</strong>：顶栏「国库」为当前持有的金币存量，「月结余」为当月经常性收入减支出的流量（金币/月）；「政治影响力（上限 100）」「人力」「水手」均同时显示当前存量与每月净流入；「稳定度（−100~+100）」「政府力量（0–100）」「威望（0–100）」为按月趋近均衡或衰减的状态值。</li>
  <li><strong>地点口径 vs 全国口径</strong>：点开单个 {T('location','地点')} 看到的人口占比以该地总人口为分母，点开国家文化/宗教面板则以全国（或控制力加权后）人口为分母；跨国横向对比请使用<strong>统计账本（Ledger）</strong>并受探索视野与账本可见性规则约束。</li>
</ul>
"""
            },
            {
                "id": "automation-matrix",
                "title": "02 · 七大系统自动化委托与单项策略设置详解",
                "en": "Seven Automation Systems & Granular Budget Controls",
                "html": f"""
<p>自动化面板允许按系统总开关、市场/阶层子开关及「<strong>最低保留储金（Gold to Save）</strong>」分层委托：</p>
<table class="data-table">
  <thead><tr><th>托管系统 / 专项设置</th><th>可执行的具体操作范围</th><th>底层判断逻辑与使用建议</th></tr></thead>
  <tbody>
    <tr><td><strong>阶层税率自动调节</strong><br>Tax Automation</td><td>关闭全权收支托管后，可逐个阶层开启自动税率并设定<strong>目标满意度（默认 50%）</strong></td><td>按住 Ctrl(±5%)/Alt(±10%) 微调目标线，系统在征税上下限内自动贴线收税，既防跌破 25% 拒出征召兵又免去频繁手调，<strong>推荐日常开启</strong></td></tr>
    <tr><td><strong>自动铸币 &amp; 信用管理</strong></td><td>自动铸币以<strong>每月零净通胀</strong>为目标动态调滑块；信用管理在盈余时还债、赤字时借贷或发债</td><td>自动铸币省心稳健；准备手动积攒大额现金或精细控制阶层贷/央行债券结构时可关闭信用托管</td></tr>
    <tr><td><strong>市场贸易 vs 贸易指令</strong></td><td>可全权托管某市场贸易，或手动设立按优先级排序的<strong>贸易指令（利润 / 短缺 / 食物重心）</strong></td><td>建议核心市场<strong>优先使用贸易指令</strong>锁死粮食与关键工业原料保供，将剩余闲置容量再交自动贸易赚取差价；自动关税分重商、均衡、自由贸易三档</td></tr>
    <tr><td><strong>生产与建造托管</strong></td><td>新建/关停/补贴建筑、自动扩建标记的盈利满员建筑与未满级 RGO、自动拆楼</td><td>务必设定合理的「<strong>保留储金（Gold to Save）</strong>」底线；核心产粮省升城、关键要塞选址与高波动新工坊建议保留手动决策</td></tr>
    <tr><td><strong>政府、阶层与外交托管</strong></td><td>内阁人选/行动、阶层贿赂（每 6 个月检查，单次耗 <code>12 × 阶层税基</code> 金币）、自动改善关系/王室联姻</td><td><strong>自动改善关系</strong>（可预留外交官与外交容量，并指定目标名单）能有效缓解扩张敌意好感压力；资金紧张时留意关闭自动贿赂阶层以防大额扣款</td></tr>
  </tbody>
</table>
"""
            },
            {
                "id": "eu4-vic3-bridge",
                "title": "03 · 从 EU4 与 Victoria 3 到 EU5：四笔关键对账算例",
                "en": "Four Core Accounting Examples Bridging EU4 & Vic3 to EU5",
                "html": f"""
<ol>
  <li><strong>工坊利润如何一步步折算成国库税金？</strong><br>
    在 EU5 中，工坊必须先招满对应阶级工人、买足原料并按 <code>市场接入度</code> 售出成品形成<strong>地点财富</strong>，再乘 <code>当前控制力</code> 变为<strong>税基</strong>，最后乘 <code>有效阶层税率</code> 进入国库。例如一座造纸行会每月新增财富 <strong>2.00 金币</strong>，当地控制力 <strong>60%</strong>，综合有效税率 <strong>15%</strong> → 国库每月实增税款为 <code>2.00 × 0.60 × 0.15 = 0.18</code> 金币（若政府每月为它支付 0.25 金币亏损补贴，国库反而每月净亏 −0.07 金币）。</li>
  <li><strong>金银矿产量与国库铸币收入如何区分？</strong><br>
    金矿（基础价 8）与银矿（基础价 6）首先作为普通商品在市场上出售创造地点财富；另一方面为首都市场提供铸币原料，使国库得以按 <code>全国税基 × 0.25 × 铸币比例 × (1 + 铸币修正)</code> 满效率印钞（无独立固定金矿直接进国库项，将铸币滑块归零则铸币收入为 0）。</li>
  <li><strong>开战前为何必须先核对宣战理由与敌方要塞？</strong><br>
    同一处基准 20 战分的省份，用「核心省份宣称」只需 15 分，用「议会宣称」需 25 分，用「羞辱宿敌」高达 200 分；且若关联要塞未占领且从未围攻过，还会额外承受 −33% 和约效率惩罚。</li>
  <li><strong>为什么打赢一场硬仗后国内矿山与农田产值下滑？</strong><br>
    常备正规军伤亡消耗全国「人力池」而不动在岗工人；陆军征召兵伤亡则直接扣减原籍地点的真实农民与劳工人口，战后需同时核对原籍人口缺口与 240 个月征召恢复期。</li>
</ol>
"""
            },
            {
                "id": "changelog-149",
                "title": "04 · 1.4.8 – 1.4.9 版本机制修订与数据表刷新记录",
                "en": "Verified 1.4.8 - 1.4.9 Patch Changelog & Table Updates",
                "html": _build_ch12_patch_html()
            },
        ],
        "discussion": {
            "title": "全书速查导航 · 遇到具体问题时去哪里找精确答案？",
            "html": """
<ul>
  <li><strong>想查某项核心数值（如生产效率、最大控制力、训练度、研究速度）有哪些建筑、特权、改革和科技能加它？</strong> → 直接前往 <a href="metrics.html"><strong>核心数值与 1,364 项修正反查器（metrics.html）</strong></a>。</li>
  <li><strong>想查具体某座建筑的造价、建材、雇员、运转配方与限制条件，或某支部队、法律、特权、宗教的完整参数？</strong> → 前往 <a href="ledgers.html#building_types"><strong>22 大核心速查表（ledgers.html）</strong></a> 或 <a href="directory.html#building_types"><strong>72 类游戏名录库（directory.html）</strong></a>，也可随时按 <code>Ctrl+K</code> 全局秒搜。</li>
</ul>
"""
        },
        "quick_links": [
            ("核心数值与 1,364 修正反查器", "metrics.html"),
            ("501 种建筑全表 · 22 数据典", "ledgers.html#building_types"),
            ("31 项规则 & 87 项成就名录", "directory.html#game_rules"),
            ("交互式实算器与排障工作台", "lab.html#calc"),
        ],
    },
]
