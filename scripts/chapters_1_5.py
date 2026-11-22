# -*- coding: utf-8 -*-
"""
Chapters 01 - 05 for EU5 Mechanics Compendium (1.4.9) — Overhauled Edition.
Focuses on calm, lucid explanations, exact formulas, worked in-game examples,
and complete factor breakdowns for every core metric, with 100% coverage of original handbook content.
"""


def T(cid, label):
    return f'<button type="button" class="term" data-concept="{cid}">{label}</button>'


def M(mid, label="查全部游戏修正来源 →"):
    return f'<a class="metric-jump" href="metrics.html#{mid}">{label}</a>'


CHAPTERS_1_5 = [
    # =========================================================================
    # CHAPTER 01
    # =========================================================================
    {
        "id": "ch01",
        "slug": "ch01-territory-core.html",
        "num": "01",
        "pillar": "territory",
        "title": "地理层级、整合核心、邻近度与控制力",
        "en": "Geography, Integration & Cores, Proximity & Control",
        "subtitle": "从五级地理单元出发，厘清一条道路或一座港口如何降低邻近度损耗，整合与核心如何抬高控制力上限，以及控制力如何决定地点财富归入国库还是留在地方阶层。",
        "upstream": [
            ("和约割地与殖民定居", "ch09-navy-war-peace.html#peace-terms", "新获领土以「未整合」或「殖民地」状态并入版图"),
            ("内阁整合与文化构成", "ch04-government-cabinet.html#cabinet-actions", "MIL 内阁推进整合，主流/已接纳文化达 50% 转为核心"),
            ("道路、港口与海上存在", "ch09-navy-war-peace.html#maritime-presence", "共同降低首都向各地点传递邻近度的水陆损耗"),
        ],
        "engine": "分别追踪地点的「行政身份（未整合→已整合→核心）」与「空间可达性（首都邻近度）」，合成最大控制力与当前控制力，按比例切分国家税基、兵源与地方阶层留存。",
        "downstream": [
            ("国家税基与阶层未受控收入", "ch03-economy-market-trade.html#wealth-to-treasury", "地点财富 × 控制力进入税基，余下 1 − 控制力归入地方阶层"),
            ("发展度与受支持建筑容量", "ch03-economy-market-trade.html#production-buildings", "繁荣度驱动发展度增长，每点发展度提供 +1 建筑容量与 +0.5% 邻近度效率"),
            ("殖民移民唯一人口来源", "ch07-ages-colonial.html#colonial-charters", "仅核心（Core）地点可向海外特许殖民地输出定居人口"),
        ],
        "redlines": [
            ("≥ 50% 文化占比", "核心晋升门槛", "已整合或殖民地点内，主流文化与已接纳文化人口合计 ≥50% 自动转为核心（相容文化不计）"),
            ("邻近度 × 0.75", "最大控制力主干", "每 100 点邻近度提供 +75 个百分点最大控制力；核心另加 +20 个百分点"),
            ("−0.50% / 月", "超上限控制力衰减", "当前控制力高于最大控制力时固定按 −0.50%/月回落；低于上限时按月度控制力修正爬升"),
            ("75% 控制力", "阶层建筑建造与拆除线", "阶层仅在控制力 <75% 的地点新建阶层专属建筑；国家须控制力 ≥75% 方可直接申请拆除"),
        ],
        "sections": [
            {
                "id": "hierarchy",
                "title": "01 · 五级地理单元与行政挂载层级",
                "en": "Five-Tier Geographical Hierarchy",
                "html": f"""
<p>《欧陆风云 V》的地图按包含关系分为五级：{T('location','地点（Location）')} → {T('province','省份（Province）')} → {T('area','地区（Area）')} → {T('region','区域（Region）')} → {T('sub_continent','次大陆')}/{T('continent','大陆')}。各项经济、粮食与内政机制分别挂载在固定层级上，核对数值时需先对齐作用范围：</p>
<table class="data-table">
  <thead><tr><th>地理层级</th><th>挂载在该层级的核心机制与面板操作</th><th>边界与动态切分规则</th></tr></thead>
  <tbody>
    <tr>
      <td><strong>地点（Location）</strong></td>
      <td>单一 {T('raw_materials','原材料（RGO）')}、所有 {T('building','建筑')}、{T('location_rank','城乡聚落等级')}、{T('town_rights','城镇特权')}、{T('integration_status','整合与核心状态')}、{T('proximity','邻近度')}、{T('control','控制力')}、{T('development','发展度')}、{T('prosperity','繁荣度')}、所属市场及驻军交战</td>
      <td>最小可拥有陆地单元；各地图像素面积不等（标准中位数 25），直接影响行军耗时与思潮邻格传播</td>
    </tr>
    <tr>
      <td><strong>省份（Province）</strong></td>
      <td>{T('provincial_food','省份粮仓储备')} 与市场购售粮结算、早期绝大多数 {T('cabinet_action','内阁行动')}（整合省份、提升控制力、灾后恢复、改宗同化）、陆军征召编组、{T('colonial_charter','特许殖民地')} 立项范围</td>
      <td>地图设有固定的「{T('province_definition','预设省份')}」；若同一预设省份被多国瓜分，各国对名下地点分别生成独立的本国省会（{T('province_capital','Province Capital')}，免费建筑容量 +2）与独立省粮仓</td>
    </tr>
    <tr>
      <td><strong>地区（Area）</strong></td>
      <td>中后期地区级内阁行动（整合地区、同化地区）、{T('exploration','海陆探索')} 目标单位、{T('privateer','私掠者')} 派遣范围、8 类产业促进政策、地方总督辖区及 {T('victory_card','胜利卡')} 计分范围</td>
      <td>控制一个地区 ≥ 2/3 的可拥有地点（属国地点折算计入）即构成「地区支配」，按该区潜在税基贡献 1–20 点列强积分</td>
    </tr>
    <tr>
      <td><strong>区域 / 次大陆 / 大陆</strong></td>
      <td>区域强权（≥20 分）外交干预半径（限相邻区域）、{T('overseas','海外领地')} 判定、可成立国家地理范围、动态历史事件与局势判定</td>
      <td>与本国首都无陆路相连、且位于不同且不相邻次大陆的地点判定为海外领地（影响种植园选址、执达署禁建与殖民领生成）</td>
    </tr>
  </tbody>
</table>
"""
            },
            {
                "id": "geography-climate",
                "title": "02 · 地形、植被、气候、水文与季节规则",
                "en": "Topography, Vegetation, Climate, Hydrography & Seasons",
                "html": f"""
<p>自然地理属性同时作用于人口容量、农业收成、道路与邻近度损耗、发展度增长率以及陆海军作战宽度：</p>
<ul>
  <li><strong>地形（{T('topography','Topography')}）与植被（{T('vegetation','Vegetation')}）</strong>：平原与农田利于城市化、行军与发展度积累（农田提供 +100,000 基础人口容量与 +10% 发展度增长）；丘陵、高原、湿地、山地与密林则按档位放大邻近度损耗、压低发展度增长（山地 −50%、丘陵 −25%、湿地 −30%、丛林 −30%、森林 −25%），并在交战时收缩前线可用 {T('frontage','战斗宽度')}、赋予守方地形骰点加值（如山地守方 +2、宽度 −4；疏林守方 +1、宽度 −2）。</li>
  <li><strong>河流、海岸、海峡与天然良港</strong>：沿海地点固定获得 <strong>+25% 人口容量、+10% 月发展度增长、+5% 补给上限</strong>；河流穿过的地点按河道水量档位（1–5 档）获得 <strong>+10% 至 +50% 人口容量</strong> 与 <strong>+5% 至 +25% 发展度增长</strong>，并大幅降低顺逆流的市场距离与行政邻近度损耗。跨河进攻承受骰点 −1，跨 {T('strait','海峡')} −2，海上登陆 −1。每个沿海地点的 {T('natural_harbor_suitability','天然港湾适宜度')}（0–100%）直接决定基础 {T('harbor_capacity','港口容量')}、和平期本地海上存在贡献以及水陆装卸损耗。</li>
  <li><strong>不可通行地、走廊与洋流</strong>：{T('impassable','不可通行荒地')} 无法拥有也无法穿越；特殊地形 <strong>{T('corridor','走廊（Corridor）')}</strong> 虽无人定居且不可拥有，但允许陆军穿行并传递贸易与控制路径。海域划分为沿岸海、内海、大洋与深洋，顺逆 {T('sea_current','洋流')} 改变舰队航速，带狭窄水域（Narrows）特征的海区阻挡邻格海上视野。</li>
  <li><strong>气候带、冬季等级与水面封冻（{T('frozen','Frozen')}）</strong>：{T('climate','气候')} 决定当地农业基础、人口容量倍率与可能出现的最高 {T('winter_level','冬季等级')}（无冬 / 温和冬季 / 普通冬季 / 严冬）。普通冬季使建造速度 −50%，严冬暂停工程、压低本地产粮并显著提高驻军损耗。严冬持续满一周后，符合条件的浅海与内海每周有 <strong>20%</strong> 概率结冰封冻：封冻期间港口舰队无法出航，陆军可直接踏冰通行（行政跳格基础成本 20），但春季回暖每周有 <strong>40%</strong> 概率解冻，解冻时仍停留在冰面海格上的陆军将直接覆灭。</li>
</ul>
"""
            },
            {
                "id": "integration-core",
                "title": "03 · 领土整合四态与「省份整合速度」影响因素",
                "en": "Four Integration States & Factors Affecting Integration Speed",
                "html": f"""
<p>在《欧陆风云 V》中，「<strong>已整合（Integrated）</strong>」与「<strong>核心（Core）</strong>」是前后衔接但条件完全不同的两个阶段：内阁行动只能将征服地推进至「已整合」；唯有当地人口的文化构成跨过 50% 门槛后，已整合地点才会自动晋升为「核心」。</p>
<table class="data-table">
  <thead><tr><th>领土状态</th><th>取得或晋升条件</th><th>最大控制力修正</th><th>月度控制力 / 分离主义</th><th>同化、改宗与特殊规则</th></tr></thead>
  <tbody>
    <tr>
      <td><strong>1. 未整合（已征服）</strong><br><code>conquered</code></td>
      <td>战争割让、购地等非核心方式新取得地点的初始状态</td>
      <td class="num neg">−10 个百分点</td>
      <td>分离主义 +0.50</td>
      <td>本地同化 −2%、改宗 −2%、守军增长 −0.5%、叛乱基础月进度 +1%</td>
    </tr>
    <tr>
      <td><strong>2. 殖民地</strong><br><code>colonized</code></td>
      <td>特许殖民地达到定居人数与国教/文化比例后建省</td>
      <td class="num">0</td>
      <td>无分离主义；月控制力 +0.10%</td>
      <td>免除未整合惩罚；主流或已接纳文化人口 ≥50% 时自动转为核心</td>
    </tr>
    <tr>
      <td><strong>3. 已整合</strong><br><code>integrated</code></td>
      <td>派遣 {T('mil','MIL')} 内阁执行「整合省份」或后期「整合地区」攒满 100% 进度</td>
      <td class="num pos">+5 个百分点</td>
      <td>分离主义降至 +0.10</td>
      <td>解除改宗与守军惩罚，同化惩罚缩至 −1%；尚未成为核心前仍不可向外输送殖民移民</td>
    </tr>
    <tr>
      <td><strong>4. 核心</strong><br><code>core</code></td>
      <td>处于「已整合」或「殖民地」状态，且当地<strong>主流文化 + 已接纳文化</strong>人口占比 ≥ <strong>50%</strong></td>
      <td class="num pos">+20 个百分点</td>
      <td>分离主义归零；月控制力 +0.10%</td>
      <td>比已整合净增 <strong>+15 个百分点</strong>最大控制力；本地自然新生人口 100% 归入主流文化</td>
    </tr>
  </tbody>
</table>

<div class="formula-box">
<strong>核心数值拆解：省份整合速度（Integration Speed）受哪些因素影响？</strong> {M('integration_speed')}
<ul>
  <li><strong>君主与执政大臣能力</strong>：「整合省份（<code>integrate_province</code>）」属于军事（MIL）内阁行动，其实际速率 = <code>基础进度 × (1 + 0.005 × 君主 MIL + 0.005 × 大臣 MIL + 全国内阁效率 + 大臣个人效率) × (1 + 整合速度修正)</code>。例如 1337 年莫斯科样本：君主 MIL 70（+35%）、首脑大臣 MIL 60（+30%，首脑个人效率 +25%）、全国内阁效率 +15.07%，合计增幅 +105.07%，基础速度 1 变为 <strong>2.05/月</strong>。</li>
  <li><strong>省份规模与城乡层级阻力</strong>：单个省份所含地点超过 <strong>5 个</strong> 时触发大省减速修正；城镇、城市及稠密人口地点的整合所需工作量高于乡村。</li>
  <li><strong>文化亲缘与国家力量投射</strong>：目标地为已接纳文化或本国文化影响力压制当地文化传统时整合更快；国家每拥有 1 点 {T('power_projection','力量投射')} 提供 <strong>+1% 全国整合速度</strong>。</li>
  <li><strong>制度、官僚与国际组织加成</strong>：集权行政改革、法典政策、时代革新以及国际组织领袖「行政定向投资」（+20% 整合速度）均可叠加提速。</li>
  <li><strong>进度倒退情形</strong>：爆发叛乱当即扣除 10 点整合进度；遭敌军占领每月流失 0.025；丧失所有权后每月流失 0.10。剧本初始非己方持有的历史核心默认保留 100 年。</li>
</ul>
</div>
"""
            },
            {
                "id": "core-power",
                "title": "04 · 核心（Core）地点的六项跨系统作用",
                "en": "Six Systemic Effects of Core Locations",
                "html": f"""
<p>将「已整合」地点进一步通过文化接纳或人口同化推上 50% 门槛转为 {T('core','核心')}，会同时解锁以下六项机制收益：</p>
<ol>
  <li><strong>最大控制力跃升 +15 个百分点</strong>：整合态仅给 +5%，核心态直接给 +20% 并附带 +0.10%/月控制力增长，是中远距离省份突破高税基阈值的关键垫脚石。</li>
  <li><strong>特许殖民地的唯一合法人口源头</strong>：海外特许殖民地每月抽调的本土移民，严格限定只能从本国<strong>核心地点</strong>迁出；非核心省份无法充当殖民母省。</li>
  <li><strong>自然出生人口自动同化</strong>：核心地点激活 <code>growth_is_primary_culture = yes</code>，当地每月自然净增的新生儿全部记入本国主流文化，长期自动巩固主流文化占比。</li>
  <li><strong>内阁「研究思潮」的前提条件</strong>：使用 ADM 内阁行动在指定省份定向加速思潮传播时，要求目标省份内全部地点均已成为核心。</li>
  <li><strong>战时常驻视野与收复失地折扣</strong>：自有核心被敌军占领期间依然为本国保留地图视野；若割让丢失，可对占有国制造「宣称省份」理由（割地战分 ×0.75），和约「归还核心」条款战分仅 ×0.50 且敌意降低 75%。</li>
  <li><strong>外交吞并继承与胜利卡计分</strong>：外交吞并属国完成时，属国已有的核心直接转为宗主国核心；中后期 {T('victory_card','胜利卡')} 要求本国完整拥有、控制目标地区全部地点且全部为核心，方可在 120 个月内累积满每级 1,000 分。</li>
</ol>
"""
            },
            {
                "id": "proximity",
                "title": "05 · 行政邻近度（Proximity）：路径损耗公式与全部影响因素",
                "en": "Proximity Path Cost Formula & Complete Influencing Factors",
                "html": f"""
<p>{T('proximity','邻近度（Proximity）')} 衡量行政指令从权力中心传抵各地点的通畅程度（范围 0–100 点）。系统自动在所有可用水陆连接中寻找<strong>累计损耗最低的最优路径</strong>：</p>
<div class="formula-box">
<strong>地点邻近度计算公式：</strong><br>
<code>地点最终邻近度 = max(0, 起点辐射强度 − Σ 沿途每跳实际损耗)</code><br>
<code>单跳陆地/河道实际损耗 = 路段基础损耗 ÷ [(1 + 邻近度传播效率之和) × (1 + 本地地形与植被修正)]</code>（分母保底 0.25）
</div>

<table class="data-table">
  <thead><tr><th>影响维度</th><th>具体项目与 1.4.9 核对数值</th><th>作用机制与规划要点</th></tr></thead>
  <tbody>
    <tr>
      <td><strong>1. 辐射起点强度</strong><br><code>local_proximity_source</code></td>
      <td>现首都固定 <strong>100 点</strong>；{T('historical_capital','历史首都')}（事件/决议迁都留存，最多 1 处）提供 <strong>80 点</strong>；地方总督治所 / 海军总督治所满效运转提供 <strong>80 点</strong></td>
      <td>某地点同时受首都与地方治所辐射时取到达值较高者。例如距首都三跳砾石路（原值 40）处设地方总督治所，该点邻近度直接升至 80，最大控制力净增 (80−40)×0.75 = <strong>+30 个百分点</strong></td>
    </tr>
    <tr>
      <td><strong>2. 陆路与四级道路</strong><br><a href="ledgers.html#road_types">道路数值表 →</a></td>
      <td>无路陆地每跳基础损耗 <strong>40</strong>；砂石路（Gravel）<strong>20</strong>；铺装路（Paved）<strong>15</strong>；现代公路（Modern）<strong>10</strong>；铁路（Railroad）<strong>5</strong></td>
      <td>仅在最优行政路径实际经过的节点间修路才会改善下游全部地点的邻近度；支线盲目铺路不改变主干损耗</td>
    </tr>
    <tr>
      <td><strong>3. 河流与冰面</strong></td>
      <td>顺流或逆流河段每跳基础损耗均为 <strong>12</strong>；严冬封冻水面基础损耗 <strong>20</strong></td>
      <td>大河流域在尚未铺设高级公路前，天然具备比砂石路（20）更低的行政传导损耗</td>
    </tr>
    <tr>
      <td><strong>4. 港口进出与海区存在</strong></td>
      <td>水陆转换基础损耗 <strong>35</strong>（港口容量达 1.0 时享 <strong>−50%</strong> 修正降至 <strong>17.5</strong>；《港口管理局》改革再减 −20%）；单格海域损耗在 0% {T('maritime_presence','海上存在')} 时为 <strong>30</strong>，100% 海上存在时线性降至 <strong>5</strong></td>
      <td>维持核心航道海区接近 100% 海上存在并升级枢纽良港后，海路单跳损耗（5）与铁路相当，可跨海支撑远岸高控制力</td>
    </tr>
    <tr>
      <td><strong>5. 邻近度效率与地形修正</strong><br>{M('proximity', '查全部邻近度修正 →')}</td>
      <td>• 本地发展度：每 1 点提供 <strong>+0.5%</strong> 邻近度传播效率<br>• 君主能力：每 1 点 ADM 提供 <strong>+0.1%</strong> 全国传播速度<br>• 社会价值观：「中央集权」满端 <strong>+20%</strong>；「陆权 / 海权」分别降低陆海损耗<br>• 地形惩罚：山地、丘陵、高原、密林显著放大该跳损耗（专门革新与特定文化传统可减免山地/丘陵惩罚）</td>
      <td>提高首都周边主干走廊的发展度与集权度，可同时惠及整条路线上游至下游的数十个地点</td>
    </tr>
  </tbody>
</table>
"""
            },
            {
                "id": "control",
                "title": "06 · 控制力（Control）：最大控制力与月度增速全拆解",
                "en": "Control: Max Control Cap, Monthly Drift & Fiscal Impact",
                "html": f"""
<p>每个地点的当前 {T('control','控制力')} 按月向该地点的 <strong>{T('max_control','最大控制力')}</strong> 靠拢。控制力直接决定国家能从该地点提取多少资源：<code>地点税基 = 地点月财富 × 当前控制力</code>（余下 <code>1 − 当前控制力</code> 的 {T('uncontrolled_wealth','未受控财富')} 全额归入当地各阶层金库）；常备人力与水手建筑产出乘 <code>max(10%, 当前控制力)</code>；征召兵动员额、人口同化与改宗速度以及对外国市场的保护力（<code>当前控制力 × 0.50</code>）同样随控制力成比例增减。</p>

<div class="formula-box">
<strong>最大控制力（Max Control）合成公式与影响因素：</strong> {M('max_control')}<br>
<code>最大控制力 = 邻近度 × 0.75 + 领土整合项 + 聚落与首都项 − 10% × (1 − 当地平均人口满意度) + 建筑/驻军/制度/内阁修正</code>
<ul>
  <li><strong>邻近度主干</strong>：邻近度每 1 点贡献 <strong>+0.75 个百分点</strong>（首都邻近度 100 即 +75%）。</li>
  <li><strong>领土整合项</strong>：未整合 <strong>−10%</strong>、殖民地 <strong>0%</strong>、已整合 <strong>+5%</strong>、核心 <strong>+20%</strong>。</li>
  <li><strong>聚落等级与首都地位</strong>：乡村 <strong>0%</strong>、集镇 <strong>+5%</strong>、城市 <strong>+10%</strong>、大都市 <strong>+20%</strong>；现首都另加 <strong>+20%</strong>，历史首都 <strong>+10%</strong>。</li>
  <li><strong>人口满意度与政体低端惩罚</strong>：当地人口平均满意度为 60% 时扣减 <code>10% × 0.40 = −4%</code>；君主正统性、共和传统、奉献度或游牧团结低于 50 时，按 <code>−20% × (100 − 当前值) ÷ 100</code> 扣减全国最大控制力（如正统性 40 点扣减 −12 个百分点！）。</li>
  <li><strong>建筑、内阁与战时状态</strong>：地方议会、议会大厅、乡村执达署提升本地上限；ADM 内阁「提升省份控制力」基础提供 <strong>+10% 最大控制力</strong>（经君臣能力与内阁效率放大后可达 +18% 以上）；遭敌海军封锁扣 <strong>−10%</strong>；部分贵族分权特权扣减乡村或全国最大控制力。</li>
</ul>
<strong>月度控制力变化（Monthly Control）：</strong>
<ul>
  <li><strong>高于上限时</strong>：固定每月衰减 <strong>−0.50 个百分点</strong>（破产当日还会一次性按原值削减 33% 控制力）。</li>
  <li><strong>低于上限时</strong>：基础每月恢复 +0.05%，核心/殖民地 +0.10%，有道路连通首都 +0.05%，当地贵族平均识字率最高贡献 +1.00%/月，配合 ADM 内阁「提升省份控制力」（基础 +1.00%/月）可快速拉满新整合富庶省。</li>
</ul>
</div>
<p><strong>实机复算对照（1337 年弗拉索沃）</strong>：该地为莫斯科核心乡村，到达邻近度约 65.24%（贡献 +48.93%）、核心 +20%，扣去少量人口满意度缺口后达到约 <strong>68.93% 控制力</strong>；当地月财富 0.64 金币，乘控制力后形成 <strong>0.44 金币税基</strong>，同时为莫斯科市场提供 <code>68.93 × 0.50 = 34.46</code> 点外国市场保护分。</p>
"""
            },
            {
                "id": "urbanization",
                "title": "07 · 发展度、聚落升格与 75 项城镇特权",
                "en": "Development Growth, Settlement Ranks & 75 Town Rights",
                "html": f"""
<p>{T('development','发展度（Development）')} 代表地点长期累积的开发水平（0–100）。每 <strong>1 点发展度</strong> 同时提供六项常驻收益：<strong>免费建筑容量 +1 级、人口容量修正 +2.5%、本地邻近度传播效率 +0.5%、原产（RGO）最大等级 +0.1 级、本地建造速度 +1%、市场中心吸引力 +0.2 点</strong>，并解锁纸张（需 20）、书籍（需 30）等高阶商品的人口消费门槛。</p>

<div class="formula-box">
<strong>每月发展度增长公式与影响因素：</strong> {M('development_prosperity')}<br>
<code>每月发展度净增 = (月度平值来源之和) × (1 + 本地与全国月发展增长百分比修正之和)</code>
<ul>
  <li><strong>四大平值来源（Flat Monthly Development）</strong>：普通地点无免费基础平值，必须靠以下来源提供底数：① <strong>地点繁荣度</strong>：<code>0.004 × 繁荣比例</code>（繁荣 +50% 提供 +0.002/月，荒废 −50% 则倒扣 −0.002/月）；② <strong>ADM 内阁「发展省份」</strong>：每地基础 +0.0025/月（再乘内阁行动倍率）；③ <strong>殖民迁移进行中地点</strong>：+0.0025/月；④ <strong>制度与建筑</strong>：市民特权《城市发展补助》全国每地 +0.001/月、《自由经济协会》+0.001/月、贸易公司总部所在地 +0.01/月。</li>
  <li><strong>地方百分比修正（Multiplier）</strong>：沿海 +10%、河流 1–5 档（+5%~+25%）、农田 +10%、有道路 +5%、道路连通首都另 +20%、当地市民平均识字率 ×25%（如 40% 识字给 +10%）；反之山地 −50%、丘陵 −25%、湿地/丛林 −30%、森林 −25%、沙漠 −33%、极地 −25%、围城/封锁各 −20%、被劫掠 −25%。</li>
  <li><strong>实算示例</strong>：沿海(+10%)农田(+10%)地点，繁荣度 +50%(平值 0.002)，市民识字率 40%(+10%)，开启《城市发展补助》(+0.001)，内阁发展省份倍率 1.30(平值 0.00325)：月平值合计 <code>0.00625</code>，乘地方倍率 <code>1.30</code> 得每月 <strong>+0.008125</strong> 发展度（年增约 +0.0975）。</li>
</ul>
</div>

<p><strong>城乡聚落四级升格与 {T('town_rights','城镇特权（Town Rights）')}</strong>：</p>
<ul>
  <li><strong>乡村 → 集镇（Town） → 城市（City） → 大都市（Megalopolis）</strong>：升格依次提供免费建筑容量 <strong>+25 / +100 / +200</strong>、固定人口容量 <strong>+20k / +100k / +400k</strong>（另加百分比容量 +10% / +25% / +50%）、最大控制力 <strong>+5% / +10% / +20%</strong> 及更高思潮发源权重；但升为城镇会降低本地农业产粮效率并将劳动力吸向非农岗位，<strong>高产粮食 RGO 与紧缺金银矿产地不宜盲目升城</strong>。</li>
  <li><strong>75 项城镇特权</strong>：发现时代研发《城镇特权》革新后全面开放（部分历史名城 1337 开局自带），集镇、城市、大都市默认分别拥有 <strong>1 / 2 / 3 个</strong> 特权名额（授予、撤销、升级基础花费分别为 20、10、8 政治影响力）。例如《市场特许权》提供集市系建筑上限 +3、市民贸易容量 +25% 与本地市场接入度 +10 个百分点；《工艺装备专营》使本地工具产出 +30%，但对本地其他行业施加通用生产效率 −5%，适合产业高度集中的专业化工业城。</li>
</ul>
"""
            },
        ],
        "discussion": {
            "title": "投资回报核算 · 修路、扩建矿坊与设立地方总督治所如何比选？",
            "html": """
<ul>
  <li><strong>统一用「国库月净增收 ÷ 一次性造价」比较回本周期</strong>：假设沿线地点原有总财富 30 金币/月、综合有效税率 20%，修筑一段报价 50 金币的道路使沿线控制力由 60% 升至 65%（+5 个百分点），则仅盘活存量财富即可每月增税 <code>30 × 0.05 × 0.20 = 0.30</code> 金币，扣除 0.04 维护后净增 0.26 金币/月，约 193 个满效月回本；若沿线总财富低于 10 金币/月，修路的纯财政回本将超过 40 年，此时优先扩建首都高控圈内的紧缺 RGO 更为合算。</li>
  <li><strong>偏远低控征服省的处置原则</strong>：距首都过远（邻近度接近 0）、且短期无力铺设港口海权链或总督治所的异文化新省份，直接吞并不仅税基接近零、占用稀缺的 MIL 内阁整合席位，还会抬高全国「经济基础」增加行政开支，并将 90% 以上未受控财富留给地方贵族。将其通过「建立省份属国」交由附庸就近以 100 首都邻近度治理并上缴固定比例贡赋，待中后期道路与集权成型后再行吞并，往往更为稳健。</li>
</ul>
"""
        },
        "quick_links": [
            ("邻近度与最大控制力修正反查", "metrics.html#max_control"),
            ("4 级道路数据对照表", "ledgers.html#road_types"),
            ("75 项城镇特权速查表", "ledgers.html#town_rights"),
            ("控制力与税基分流计算器", "lab.html#calc"),
        ],
    },

    # =========================================================================
    # CHAPTER 02
    # =========================================================================
    {
        "id": "ch02",
        "slug": "ch02-population-food.html",
        "num": "02",
        "pillar": "territory",
        "title": "人口容量、阶级晋升、疾病与三级粮食调配",
        "en": "Population Capacity, Promotion, Diseases & Three-Tier Food System",
        "subtitle": "解析固定底盘与百分比倍率如何合成人口容量，平民按什么速度晋升填补工坊岗位，疫病抗性如何运作，以及食物如何在地点、省份与市场三本账之间结算。",
        "upstream": [
            ("植被、气候、水文与发展度", "ch01-territory-core.html#geography-climate", "共同决定各地点的固定人口容量与百分比扩容系数"),
            ("文化地位与宗教宽容", "ch06-culture-religion.html#culture-status", "决定当地平民是否有资格晋升为市民、教士与贵族"),
            ("农业 RGO 与食物类商品", "ch03-economy-market-trade.html#production-buildings", "鱼、小麦、稻米等一面按市价创富，一面按食物值入省仓"),
        ],
        "engine": "按月结算各地点出生、死亡与市场内迁徙，将符合文化资格的平民晋升至空缺建筑岗位，并以省份粮仓为中心自动向所属市场售出余粮或购入缺口。",
        "downstream": [
            ("建筑满员率与实际产能", "ch03-economy-market-trade.html#production-buildings", "新建建筑与扩建 RGO 必须等待对应阶级工人就位才产生收益"),
            ("八大阶级消费需求矩阵", "pop-demand.html", "人口规模、识字率与财富水平生成对 75 种商品的日常购买需求"),
            ("征召兵战损与劳动力缺口", "ch08-military-combat.html#force-types", "陆军征召兵阵亡直接扣减原籍在岗人口，恢复潜力需 240 个月"),
        ],
        "redlines": [
            ("60% / 100% 占用", "人口容量拥挤阈值", "人口达容量 60% 起自然增长受阻尼衰减；达 100% 时正自然增长归零并加大外迁"),
            ("主流 / 接纳 / 相容", "阶级晋升文化门槛", "仅主流、已接纳与相容文化平民允许晋升上层阶级；受忽视与受歧视文化禁止晋升"),
            ("75% 省仓 / 25% 市仓", "粮食外调两条保护线", "省粮仓超过 75% 容量部分才向市场分享；市场总储粮低于 25% 时市民停止对外出口食物"),
            ("−5 个百分点 / 年", "省份饥荒人口惩罚", "省粮仓耗尽且市场买不到粮时触发饥荒：年增长率 −5%、补给 −25%、降级 +50%"),
        ],
        "sections": [
            {
                "id": "population-base",
                "title": "01 · 人群结构、人口容量公式与阶级晋升速度",
                "en": "Pop Groups, Population Capacity Formula & Promotion Speed",
                "html": f"""
<p>每个地点的居民按「<strong>{T('pop_type','人口类型')} × {T('culture','文化')} × {T('religion','宗教')}</strong>」划分为独立的人群（{T('pop','Pops')}），共八类人口：上层阶级包括 {T('nobles','贵族')}、{T('clergy','教士')}、{T('burghers','市民')}；下层与军事劳动人口包括 {T('peasants','农民')}、{T('rgo_pops','劳工')}、士兵、部落民与 {T('slaves','奴隶')}。</p>

<div class="formula-box">
<strong>核心数值一：地点人口容量（Population Capacity）计算公式与影响因素</strong> {M('pop_capacity')}<br>
<code>地点总人口容量 = 固定基础容量之和 × (1 + 容量百分比修正之和)</code>
<ul>
  <li><strong>固定基础容量来源（Flat Capacity）</strong>：地表植被决定底数——农田 <strong>100,000</strong>、草地/森林 <strong>50,000</strong>、疏林 <strong>35,000</strong>、丛林/高原 <strong>25,000</strong>、荒原 <strong>10,000</strong>、沙漠 <strong>5,000</strong>；聚落等级另加固定值——集镇 <strong>+20,000</strong>、城市 <strong>+100,000</strong>、大都市 <strong>+400,000</strong>；赤道邻近度与灌溉设施等建筑提供额外固定额。</li>
  <li><strong>百分比容量修正（Percentage Modifiers）</strong>：每 1 点发展度 <strong>+2.5%</strong>；每 1 级满员运作建筑 <strong>+0.1%</strong>；沿海 <strong>+25%</strong>；河流按水量 1–5 档 <strong>+10% ~ +50%</strong>；集镇/城市/大都市另加 <strong>+10% / +25% / +50%</strong>；气候带（温带、地中海、亚热带大幅加成，极地与严寒干旱扣减）。</li>
  <li><strong>拥挤度影响</strong>：当 <code>当前人口 ÷ 总人口容量</code> 超过 <strong>60%</strong> 时自然出生率开始受阻尼压缩；达到或超过 <strong>100%</strong> 时正自然增长封顶为 0，并产生强烈迁出推力。</li>
</ul>
<strong>核心数值二：人口自然增长与阶级晋升速度（Promotion Speed）</strong> {M('pop_promotion')}
<ul>
  <li><strong>自然增长率（按年率显示，按月结算）</strong>：由省粮仓盈余、当地低粮价（低于基准 0.05 金币/食物）、正繁荣度、充足生活消费品、医院/修道院建筑、医药革新及战后 DIP 内阁「专注恢复」拉升；饥荒（年率 −5 个百分点）、被劫掠（持续 12 个月，年率 −0.5 个百分点）与疫病则会造成人口净减。</li>
  <li><strong>阶级晋升（Promotion）与招工周期</strong>：新建建筑或扩建 RGO 只提供空岗位，必须等当地待业工人就位，或由农民按月「晋升」为劳工、市民、士兵、教士或贵族（预计填满月数 ≈ <code>岗位缺口人数 ÷ 当地每月可晋升人数</code>）。<strong>硬性限制</strong>：受忽视（Ignored）与受歧视（Discriminated）文化人群无法晋升上层岗位。提高晋升速度的主要手段包括：维持<strong>正稳定度</strong>（每 +1 点稳定度提供 +1% 升阶速度，+40 稳定即 +40%）、提高本地<strong>控制力</strong>与平民<strong>识字率</strong>、偏向「自由民」价值观、兴建教育建筑，以及派遣 ADM 内阁执行「鼓励城市化 / 促进人口升级」。</li>
</ul>
</div>
"""
            },
            {
                "id": "migration-disease",
                "title": "02 · 人口迁徙吸引力与疫病抗性机制",
                "en": "Migration Attraction & Disease Resistance Mechanics",
                "html": f"""
<p>除自然生老病死外，同一市场内部各地点按 <strong>{T('migration_attraction','迁徙吸引力')}</strong> 差值发生月度人口流动（前提是法律或阶层特权允许农民/劳工迁徙，如《平民迁徙权》开启自由流动，而农奴制法规锁死农民原地务农；奴隶不可自主迁徙）：</p>
<ul>
  <li><strong>迁徙吸引力来源</strong> {M('pop_growth_migration', '查全部迁徙修正 →')}：充足空缺岗位、高发展度、正繁荣度、高人口满意度、城镇与市政设施提高吸引力；人口超出容量、建筑超出免费支持上限（每超 1 级扣 −0.01 吸引力）、饥荒（−1.0）与战乱则促使人口外流。</li>
  <li><strong>征服后的双向人口流动</strong>：地点易主后，若当地原住民在新统治国处于受歧视地位，前 <strong>12 个月</strong> 内会向同文化母国加速外逃；同时新占领地对本国主流文化居民产生持续 <strong>25 年</strong> 递减的拓殖迁入拉力。</li>
  <li><strong>疫病传播与 {T('disease_resistance','疫病抗性')}</strong> {M('disease_resistance', '查全部防疫修正 →')}：黑死病（鼠疫）、伤寒、天花、流感、疟疾及美洲大瘟疫等 8 类 {T('disease','疫病')} 各有独立结算间隔（如每 10–15 天检定一次）与传播权重。商路密集的港口和高密度大都市最易率先输入疫情；本地与全国「疫病抗性」（自然内在抗性上限 60%，医院、药房、引水渠、充足药材供应与卫生革新可提高抗性）直接降低感染与死亡比例。疫情过后幸存人群获得临时群体免疫抗性，再按病种月衰减率缓慢消退。注意气候边界：例如疟疾在大陆性、副极地与极地气候区的环境感染率为 0。</li>
</ul>
"""
            },
            {
                "id": "food-chain",
                "title": "03 · 食物产出、三级粮仓调配与财政购粮账单",
                "en": "Food Production, Three-Tier Granaries & Fiscal Food Bills",
                "html": f"""
<p>在《欧陆风云 V》中，「<strong>食物类商品（如小麦、鱼、稻米、牲畜）</strong>」与「<strong>食物单位（Food）</strong>」分走两套账目：同一批渔获既作为商品在市场上按单价创造地点财富，同时按其内含食物值进入本地与省级粮仓供养居民。</p>

<div class="formula-box">
<strong>一地双账实机复算（瑞典尼雪平渔场样本）：</strong><br>
尼雪平每月产出 <code>1.18</code> 单位鱼，斯德哥尔摩市场鱼价为 <code>0.58</code> 金币/单位，当地市场接入度 <code>90%</code>，鱼的单位食物值为 <code>5</code>（小麦为 8，稻米为 10）：<br>
• <strong>商品财富账</strong>：<code>1.18 × 0.58 × 0.90 ≈ 0.62</code> 金币/月（计入尼雪平地点财富）；<br>
• <strong>省份食物账</strong>：<code>1.18 × 5 × 本地粮食生产率(1.0) = 5.90</code> 食物/月（直接汇入所在省份粮仓，不受市场接入度折减）。
</div>

<table class="data-table">
  <thead><tr><th>结算层级</th><th>收支合成规则（<code>00_defines.txt</code>）</th><th>对国库财政与人口的直接影响 {M('food_supply', '查食物修正 →')}</th></tr></thead>
  <tbody>
    <tr>
      <td><strong>第一层：地点收支</strong><br>{T('local_food','Local Food')}</td>
      <td>本地食物类 RGO 产粮 + 闲置农民自给农业 − 当地各阶级居民耗粮（每千农民基础月耗 <strong>1</strong> 食物，上层阶级与贵族高达 <strong>20</strong>！）</td>
      <td>严冬、焦土（−50% 产粮）或抽空农村劳工进城办厂会大幅压低地点净余粮</td>
    </tr>
    <tr>
      <td><strong>第二层：省份粮仓</strong><br>{T('provincial_food','Provincial Food')}</td>
      <td>将同省所有地点的食物差额合并入省粮仓（粮仓建筑提高容量，食物保存效率减少月度腐坏）</td>
      <td>• <strong>盈余分享（&gt;75% 容量）</strong>：省粮仓先留足自身容量 <strong>75%</strong> 作缓冲，超出部分卖给所属市场食物池，所得按王权分成计入财政「售粮收入」。<br>• <strong>缺口购粮</strong>：省内入不敷出且储粮不足时，自动按市场食物单价（基准 <code>0.05</code> 金币/食物）购入可分配粮食，由国库与阶层分摊记入「<strong>购粮支出</strong>」（这正是冬季或盲目升城后预算突然亏损的常见原因）。</td>
    </tr>
    <tr>
      <td><strong>第三层：市场食物池</strong><br>{T('market_food','Market Food')}</td>
      <td>汇总各盈余省分享量与跨市场运入的食物类商品（单省第二阶段单轮吸收上限为自然月缺口 3 倍）</td>
      <td>市场比较现有存粮与月耗粮（以 24 个月储粮为充裕基准）浮动食物单价；当市场总储粮低于容量 <strong>25%</strong> 时，市民商人自动暂停从该市场向外运粮；若省仓归零且市场无粮可买，全省陷入 <strong>{T('starving','饥荒')}</strong>。</td>
    </tr>
  </tbody>
</table>
"""
            },
            {
                "id": "prosperity-devastation",
                "title": "04 · 繁荣度、战时占领损失与灾后恢复",
                "en": "Prosperity, Occupation Losses & Post-War Recovery",
                "html": f"""
<p>地点 {T('prosperity','繁荣度（Prosperity）')} 的取值范围为 <strong>−100% 至 +100%</strong>，正负两端对经济与人口具有显著不对称影响：</p>
<ul>
  <li><strong>正繁荣区间（0% 至 +100%）</strong>：在和平、食物充足、高人口满意度与特定改革（如《扩张庄园农业》每月 +0.1 个百分点）下逐月积累。在 +50% 繁荣度时，每月为发展度提供 +0.002 基础平值，并提升人口自然增长与迁入吸引力。</li>
  <li><strong>负繁荣区间（荒废，−100% 至 0%）</strong>：直接按比例削减生产力——例如在 <strong>−50% 繁荣度</strong> 时，发展度每月倒扣 −0.002，且<strong>本地原材料产出与加工生产效率各扣减 −25%</strong>（满 −100% 时高达 −50% 生产效率！）。</li>
  <li><strong>占领与劫掠的定量冲击</strong>：地点被敌军攻占瞬间，直接损失当地储备粮食的 <strong>90%</strong>（仅余 10%），并在满足条件时可能触发 15% 相关人口被掳为奴隶（冷却 240 天）；同时附加持续 <strong>12 个月</strong> 的「被劫掠（<code>looted</code>）」状态：年人口增长率 −0.5 个百分点、月发展度增长 −25%、繁荣度衰减 +0.10、最大损耗 +5。</li>
  <li><strong>战后快速修复</strong>：自然恢复深度负繁荣耗时漫长；停战后指派高 DIP 大臣对受灾省份执行「<strong>专注恢复（<code>recovery_effort</code>）</strong>」，可在全省繁荣度回到 0% 前持续提供高额月度荒废修复与人口增长补偿。</li>
</ul>
"""
            },
        ],
        "discussion": {
            "title": "实务诊断 · 预算购粮赤字排查与用工缺口预判",
            "html": """
<ul>
  <li><strong>每月财政「购粮支出」居高不下时的三步定位法</strong>：① 打开粮食地图模式，找出省粮仓见底、正在向市场买粮的具体城市化省份；② 检查该省内部是否仍有农村小麦/牲畜/鱼类 RGO 尚未扩建或因缺劳工未满员——同省农村余粮优先免费供给本省城市，无需支付市场买粮费；③ 若本省无农田可用，则在所属市场设立「食物重心」贸易指令，优先进口稻米（每单位含 10 食物）或小麦（含 8 食物）压低市场食物单价。</li>
  <li><strong>为什么扩建了 RGO 或工坊却没增加收入？</strong>：核对地点面板的在岗人数与待业池。如 1337 年莫斯科扩建沃赫纳林业实测：花费 59.19 金币将林业从 1 级升至 2 级后，2,000 个岗位实际仅有 1,113 人在岗（新增 1,000 岗位仅招到 113 人），同时木材增产使市场木价从 1.15 微降至 1.01，短期月收入几乎不变。动工前务必确认当地有待业农民/劳工或足够的月晋升速度。</li>
</ul>
"""
        },
        "quick_links": [
            ("人口容量与晋升修正反查", "metrics.html#pop_capacity"),
            ("8 阶级 × 75 商品需求矩阵", "pop-demand.html"),
            ("75 种商品食物值与基础价", "ledgers.html#goods"),
            ("8 类疫病参数名录", "directory.html#diseases"),
        ],
    },

    # =========================================================================
    # CHAPTER 03
    # =========================================================================
    {
        "id": "ch03",
        "slug": "ch03-economy-market-trade.html",
        "num": "03",
        "pillar": "economy",
        "title": "商品生产、生产效率、市场定价、贸易与国家财政",
        "en": "Production Efficiency, Markets, Pricing, Trade & National Finance",
        "subtitle": "完整拆解加工生产效率与 RGO 产出的全部影响因素，追踪商品供需如何生成目标价格，跨市场商路如何结算三种效率与王室分成，以及财富、税基、经济基础与铸币信贷的精确公式。",
        "upstream": [
            ("在岗人口、发展度与控制力", "ch01-territory-core.html#control", "决定建筑运行规模、免费建筑容量以及财富转入税基的比例"),
            ("道路、河流与港口适宜度", "ch01-territory-core.html#proximity", "决定各地点对市场中心的接入度及商路跨区运输成本"),
            ("王室力量与阶层税率上限", "ch05-estates-rebels.html#power-balance", "决定国家贸易分成比例与各阶层可征收的最高税率"),
        ],
        "engine": "在各地点通过 RGO 与加工配方创造商品与财富，在市场层面按有效供需与物价稳定性计算每月 5% 追赶的市场价，经由国家/市民商路跨市场套利，最终汇入国家财政的税收、铸币与债务账户。",
        "downstream": [
            ("阶层金库与消费需求反馈", "ch05-estates-rebels.html#estate-wealth", "税后收入与未受控财富进入阶层账本，转化为下月商品采购与私建投资"),
            ("宫廷、外交与稳定度开支基数", "ch04-government-cabinet.html#government-power", "全国全额财富推高「经济基础」，同步放大三项国家预算开支"),
            ("科研思潮跨市场输入", "ch07-ages-colonial.html#ages-institutions", "市场吞吐达标后，商路可将先进市场的思潮引入国内"),
        ],
        "redlines": [
            ("只增产出不增原料", "加工生产效率核心机制", "生产效率放大成品产出而不增加原料消耗，对低毛利加工业的净利润具有高倍杠杆效应"),
            ("−5% / 超额每级", "免费建筑容量惩罚", "地点建筑总等级超出受支持上限后，每超 1 级扣减 −5% 新建筑建造效率并扣 −0.01 迁徙吸引"),
            ("5% 差额 / 月", "市场价格移动速度", "当前市价每月向目标价移动 5% 差额；目标价受时代物价稳定性 s 与时代最高倍数 m 双重约束"),
            ("税基 × 0.25 × s", "满效率铸币收入底式", "铸币比例超过免通胀阈值（平价）的部分按 ×0.005/月推高通胀；破产扣 50 点信用需百年消退"),
        ],
        "sections": [
            {
                "id": "production-buildings",
                "title": "01 · 原产（RGO）、加工建筑与「生产效率」完整影响因素",
                "en": "RGO, Production Buildings & Complete Factors Affecting Production Efficiency",
                "html": f"""
<p>地点的商品供给来自两类设施：每处地点固有一种 <strong>{T('raw_materials','原材料生产（RGO）')}</strong>（无需投入原料，每级雇用 1,000 名劳工或奴隶；扩建金币报价按 <code>100 × (0.5 + 0.25 × 商品基础价) × 木材市价修正</code> 计算，木材折扣下限 −33%），以及消耗原料产出制成品的 <strong>{T('building','生产建筑')}</strong>（分时代解锁行会、工坊与工场，基础标准造价在六时代依次为 50 / 100 / 200 / 400 / 800 / 1,200 金币，昂贵建筑为 200 至 5,000 金币）。</p>

<div class="formula-box">
<strong>加工建筑运行规模、产出与月利润公式：</strong><br>
<code>有效运行规模 = 建筑等级 × 雇员满员率 × 本地市场接入度 × 投入原料可得性</code><br>
<code>月成品产量 = 配方每级基础产出 × 有效运行规模 × (1 + 本地生产效率 + 全国生产效率)</code><br>
<code>月投入原料消耗 = 配方每级原料需求 × 有效运行规模</code><br>
<code>建筑月利润（计入地点财富） = 月成品产量 × 当地市场成品价 − Σ(月投入原料消耗 × 当地市场原料价)</code>
</div>

<p><strong>为什么「{T('production_efficiency','加工生产效率（Production Efficiency）')}」是最关键的工业数值？</strong><br>
如上式所示，市场接入度或等级提升时，产出和原料消耗同步缩放；而<strong>生产效率只放大成品产出量，不增加一分钱原料消耗</strong>。以<strong>造纸师行会（Paper Guild）</strong>的三种配方在基准价（纸 2、皮革 3、纤维 2、布 3、木 1.5 金币）下的满员单级对比为例：</p>
<ul>
  <li><strong>兽皮纸配方</strong>：月耗 0.1852 皮革 + 0.1852 木材（成本 0.8334），基础产纸 0.5（产值 1.00），月毛利仅 <strong>0.1666 金币</strong>。此时若叠出 <strong>+20% 生产效率</strong>，产纸升至 0.6（产值 1.20），成本仍为 0.8334，月毛利跃升至 <strong>0.3666 金币（净利润暴涨 +120%！）</strong>。</li>
  <li><strong>纤维纸浆 / 布料纸配方</strong>：分别耗 0.6667 纤维 + 0.2222 木材，或 0.5051 布料 + 0.1008 木材，月产纸 1.0，基准毛利约 <strong>0.3333 金币</strong>；但若市场布价涨至 4 金币，布料配方即转为亏损 −0.1716，未开启 {T('subsidy','政府补贴')} 的亏损建筑每月裁员 10% 直至停工（重新盈利后每月再雇佣 10%）。</li>
</ul>

<table class="data-table">
  <thead><tr><th>影响来源类别</th><th>提高或降低「加工生产效率」的具体因素 {M('production_efficiency')}</th><th>典型幅度与核对要点</th></tr></thead>
  <tbody>
    <tr>
      <td><strong>1. 社会价值观</strong></td>
      <td>「资本经济 ↔ 传统经济」轴偏向<strong>资本经济</strong>端</td>
      <td>满值（+100）提供 <strong>+10% 全国生产效率</strong>（传统经济端则偏向原材料 RGO 产出）</td>
    </tr>
    <tr>
      <td><strong>2. 人口识字率与阶层满意度</strong></td>
      <td>本地在岗劳工/市民识字率；全国<strong>市民阶层满意度</strong>（以 50% 为零点）</td>
      <td>劳工识字率提供最高 <strong>+2.5% 本地效率</strong>；市民满意度系数为 0.025（如 75% 满意度提供 <code>0.25 × 2.5% = +0.625%</code>，100% 提供 +1.25%）</td>
    </tr>
    <tr>
      <td><strong>3. 本地辅助建筑</strong></td>
      <td>行会大厅（Guild Hall）、工匠行会（Artisan Guild）、犹太区（Jewish Quarter）等城市设施</td>
      <td>直接提供 <strong>+0.5% 至 +5% 本地生产效率</strong>，适合建在工坊密集的核心工业大城</td>
    </tr>
    <tr>
      <td><strong>4. 城镇特权与产业政策</strong></td>
      <td>75 项城镇特权中的行业专营权；国家对地区授予的 8 项「促进产业」政策</td>
      <td>行业专营给对应单品 <strong>+15% / +30% 产出</strong>，但附带 <strong>−2.5% / −5% 本地通用生产效率</strong>（多行业混杂城慎选）；促进产业给该地区对应商品 <strong>+5% 产出</strong> 且全国人口对该商品需求 +50%</td>
    </tr>
    <tr>
      <td><strong>5. 特权、改革、法律与官僚</strong></td>
      <td>市民特权《商人的沃土》/《王室工厂》、法律政策《大行会》/《加强行会》、政府改革、官僚部门《市监》及经济霸权解锁的「精简文书」内阁行动</td>
      <td>单项通常提供 <strong>+1% 至 +2.5% 全国生产效率</strong>；官僚部门需维持高预算比例以兑现全额正向加成</td>
    </tr>
    <tr>
      <td><strong>6. 时代革新（Advances）</strong></td>
      <td>文艺复兴至革命时代共 34 项手工业、机械与工场管理革新</td>
      <td>单项提供 <strong>+1% 至 +5% 全国生产效率</strong>，并逐步解锁更高单城上限的工坊与工场</td>
    </tr>
    <tr>
      <td><strong>7. 负繁荣度与投产度规则</strong></td>
      <td>地点负繁荣度（荒废）；定义文件中的建筑投产度（{T('establishment','Establishment')}）</td>
      <td>负繁荣度按比例扣减最高 <strong>−50% 生产效率</strong>（−50% 荒废即扣 −25%）。注：1.4.9 默认安装中 <code>ESTABLISHMENT_SYSTEM_ENABLED = no</code>（新建筑直接 100% 起步）；若在规则/模组中开启，投产度超 50% 部分最高另给 +15% 效率</td>
    </tr>
  </tbody>
</table>

<div class="formula-box">
<strong>建造前的两道容量检查与「原材料产出（RGO Output）」决定因素：</strong> {M('rgo_output', '查原产修正 →')} · {M('building_cost_cap', '查建筑容量修正 →')}
<ul>
  <li><strong>地点免费建筑容量（Supported Building Levels）</strong> = <code>发展度 × 1 + 千人数 × 0.05 + 等级加成（镇 25 / 城 100 / 大都市 200）+ 身份加成（国都 +5 / 市场中心 +5 / 省会 +2 / 历史首都 +2）</code>。每超出 1 级，新建筑建造效率 <strong>−5 个百分点</strong>（例如基数 100 金币在 −15% 效率下变为 <code>100 ÷ 0.85 ≈ 117.65</code> 金币）且迁徙吸引力 −0.01。</li>
  <li><strong>单类加工建筑等级上限</strong>：行会 = <code>1 + 0.10×发展度 + 0.05×千人数 + (城5/都10)</code>；工坊 = <code>1 + 0.25×发展度 + 0.05×千人数 + (城10/都20)</code>；工场 = <code>5 + 0.50×发展度 + 0.10×千人数 + (城20/都40)</code>。若本地市场接入度低于 75%，上述上限还须乘以 <code>(市场接入度 + 0.25)</code>！</li>
  <li><strong>影响 RGO 原材料产出的核心因素</strong>：实际在岗劳工人数、社会价值观偏向「农奴制」（满端 +20% 全国原产）与「传统经济」、部落阶层满意度、改革《乡村特许寡头》(+10%)、文化专属革新（如德意志《熔析精炼法》银铅 +20%）及正繁荣度。注意查看扩建按钮的 <strong>{T('expansion_volatility','扩建波动性')}</strong> 预览与全国 <strong>{T('employment_system','雇佣制度')}</strong>（利润最高优先 / 均等 / 先到先得，切换费 10 稳定度）。</li>
</ul>
</div>
"""
            },
            {
                "id": "market-network",
                "title": "02 · 市场接入度、市场归属竞争与商品供需定价公式",
                "en": "Market Access, Market Attraction & Target Price Formula",
                "html": f"""
<p>一个 {T('market','市场（Market）')} 围绕一座 {T('market_center','市场中心')}（提供当地贸易容量 +2、贸易优势 +20、免费建筑容量 +5、储备容量 +25，且每拥有一座中心令全国市民满意度均衡 +1%）跨国界运行。每个地点先计算对各候选中心的 <strong>{T('market_access','市场接入度')}</strong>，再综合吸引力与市场保护选定归属市场：</p>

<div class="formula-box">
<strong>1. 市场接入度路径损耗（1.4.9 核对值）：</strong> {M('market_access')}<br>
<code>市场接入度（百分点） = 100 − (地图像素距离 × 0.5 × 路段因子 + 水陆转换绝对损耗) + 本地接入修正</code>
<ul>
  <li><strong>路段距离因子</strong>：普通陆路 <code>×1.00</code>；砾石/柏油/近代/铁路依次为 <code>×0.90 / 0.80 / 0.70 / 0.60</code>；顺流河段 <code>×0.50</code>、逆流 <code>×0.90</code>；近海段 <code>×0.75</code>、外海段 <code>×1.50</code>；水陆过渡段距离因子 <code>×0.50</code>，无港另扣 <strong>10 点</strong>，有港另扣 <code>2 × (1 − 港湾适宜度)</code> 点（如 75% 适宜度仅扣 0.5 点）。</li>
  <li><strong>本地接入修正与短缺分配权</strong>：集市/市集村落提供基础本地接入修正，城镇特权《大市场权》+15 点、《贸易特许权》+10 点。接入度不仅直接折算原产收入与工坊开工规模，还决定<strong>市场缺货时的拿货先后顺序</strong>——低接入度地点在原料紧张时最先断供。</li>
</ul>
<strong>2. 候选市场归属得分（为什么边境地点会被邻国市场吸走？）：</strong><br>
<code>候选市场得分 = 对该中心的接入度 + 中心实力（城+2.5/都+5 + 0.2×发展度 + 0.05×建筑级） + 所有者威望×0.05 + 语言匹配（同通用语+5/同优势语+5） + 同省(+20)/同地区(+10) − 外国市场保护（当前控制力 × 0.50 + 保护修正） + 外交条约项（特惠准入+20并解除保护 / 拒绝准入−15）</code>
</div>

<p><strong>3. 商品三套数量与「目标价格」精确公式</strong>：<br>
打开市场内任一商品面板时，须严格区分<strong>实物流量</strong>（<code>本地供给 − 本地需求 + 实际进口 − 实际出口</code>，国家与市民运量均按 100% 计）与参与定价的<strong>有效供需</strong>：</p>
<div class="formula-box">
<code>有效供给 = 本地定价供给 + 0.75 × 国家进口量 + 0.25 × 市民进口量</code><br>
<code>有效需求 = 本地定价需求 + 0.75 × 国家出口量 + 0.25 × 市民出口量</code><br>
<code>供需比 r = (有效供给 + 1) ÷ (有效需求 + 1)</code><br>
<code>候选目标价 = min(基础价 × 时代最高倍数 m, 基础价 × (1 + r × s) ÷ (r + s))</code><br>
<code>本月价格变化 = 5% × (候选目标价 − 当前市场价)</code>
</div>
<ul>
  <li><strong>六时代物价稳定性 <code>s</code> 与最高价倍数 <code>m</code></strong>：传统与文艺复兴时代 <code>s = 10%, m = 3×</code>；地理大发现 <code>s = 8%, m = 4×</code>；宗教改革 <code>s = 6%, m = 5×</code>；专制时代 <code>s = 4%, m = 5×</code>；革命时代 <code>s = 2%, m = 5×</code>（随时代演进，<code>s</code> 降低使供需失衡引起的价格涨跌幅度显著扩大）。</li>
  <li><strong>实机复算（斯德哥尔摩铜价）</strong>：铜基础价 3，有效供给 6.38，有效需求 0.90，传统时代 <code>s = 0.10</code> → <code>r = 7.38 ÷ 1.90 ≈ 3.8842</code> → 目标价 <code>3 × (1 + 0.38842) ÷ 3.9842 ≈ 1.045</code>（面板显示 1.04）；当前价 1.76，当月价格变化为 <code>0.05 × (1.04 − 1.76) = −0.036</code> 金币。</li>
  <li><strong>库存释放与高价需求弹性</strong>：商品储备占用率在 50%–75% 间按月向贸易调度释放最多 5% 库存（定价权重为 0）；当商品市价高于基础价时，人口消费需求按 <code>max(0.35, 1 − 0.40 × (当前价 ÷ 基础价 − 1))</code> 缩减（2 倍基础价保留 60% 需求，3 倍触及 35% 下限）。</li>
</ul>
"""
            },
            {
                "id": "trade-orders",
                "title": "03 · 贸易容量、贸易优势、三种效率与市民商路",
                "en": "Trade Capacity, Trade Advantage, Three Efficiencies & Burgher Trade",
                "html": f"""
<p>跨市场贸易分为玩家通过 <strong>{T('trade_orders','贸易指令')}</strong> 调度的「国家贸易」与当地市民自动经营的「{T('burgher_trade','市民贸易')}」两条轨道：</p>

<div class="formula-box">
<strong>跨市场商路运力、取货与国库分成公式：</strong> {M('trade_capacity_advantage', '查容量与优势来源 →')} · {M('trade_efficiency_maint', '查贸易效率来源 →')}<br>
<code>所需贸易容量 = 计划运量 × 商品单位运输成本（如铁 1、黏土 2、纸 0.5）× 超贸易范围距离倍率（范围内为 1）</code><br>
<code>商路月净利润 = 销售收入 − 采购支出 − 路线维护费（基础 0.25 × 已分配容量） − 海峡通行费 + (补贴收入 − 缴纳关税)</code><br>
<code>计入国库的贸易月收入 = Σ 正利润商路 × 本国贸易收入分成（基础按王室力量份额 1∶1 计）</code>（余下利润分给非王室阶层）
</div>

<table class="data-table">
  <thead><tr><th>核心贸易指标</th><th>在结算链中的具体作用</th><th>主要决定与提升因素（1.4.9 核对）</th></tr></thead>
  <tbody>
    <tr>
      <td><strong>{T('merchant_capacity','贸易容量')}<br>&amp; {T('trade_range','贸易范围')}</strong></td>
      <td>决定本国在该市场可分配多少总运力；路线成本超出贸易范围后每单位货物消耗更多容量（注意：分配 8 容量即使只买到 5 单位货，维护费仍按已分配的 8 容量计！）</td>
      <td>市场中心(+2)、集市/商埠建筑、市民力量高于 25% 的加成、城镇特权与时代革新；港口贸易装卸效率在 1.4.9 基数提升至 <strong>+200% × 港湾适宜度</strong>，顺河商路成本 −50%、海段倍率 0.30（同段路河优惠仅取其一）</td>
    </tr>
    <tr>
      <td><strong>{T('merchant_power','贸易优势')}<br>Trade Advantage</strong></td>
      <td>当出口市场的紧俏商品不够所有买方瓜分时，严格按各国在<strong>货源市场</strong>的「贸易优势」从高到低依次取货（无优势时堆再多容量也买不到现货）</td>
      <td>拥有市场中心(+20)、当地贸易建筑、市民阶层高满意度（系数 0.5）、解锁特定海上贸易优势修正后的海区存在、重商主义倾向与商栈特权</td>
    </tr>
    <tr>
      <td><strong>进口 / 出口 / 出售<br>三种效率对比</strong></td>
      <td>设买价 2、卖价 3、运量 4（基础毛利 4.00）：<br>• <strong>进口效率 +10%</strong>：买价总成本 8 减 10% → 新毛利 <strong>4.80</strong><br>• <strong>出口效率 +10%</strong>：销售额 12 增 10% → 新毛利 <strong>5.20</strong><br>• <strong>出售效率 +10%</strong>：正价差 4 增 10% → 新毛利 <strong>4.40</strong></td>
      <td>海/陆贸易效率与商人维护效率（如《公共财政簿记》改革 +40% 维护效率）；宫廷语言匹配首都市场语言提高出售效率；海关议程提供进口效率 +2% 并压低外商出口效率 −5%；《灵活出口》革新提供出口效率 +2%</td>
    </tr>
    <tr>
      <td><strong>关税、补贴与<br>市民自动商路</strong></td>
      <td>市场所有者可分商品设进出口关税或补贴（基础上限各 20%，重商主义满端各 +50%，战争经济关税上限 +15%）；1.4.8 起外国市民贸易关税与补贴按全额结算</td>
      <td><strong>贸易指令三重心</strong>：建议将「食物」与「关键军工/造纸原料短缺」指令排在名单顶部优先拿容量，「利润重心」（默认门槛 0.25 金币/容量）排在下方吃剩余容量。<strong>市民贸易容量</strong> = <code>市民千人数 × (1 + 识字项 + 集市100% + 垄断特权100%等)</code>，最大范围随六时代为 600–1,100，收益归入市民所在地点财富</td>
    </tr>
  </tbody>
</table>
"""
            },
            {
                "id": "wealth-to-treasury",
                "title": "04 · 财富、税基、经济基础与三项国家预算开支",
                "en": "Location Wealth, Tax Base, Economic Base & State Spending",
                "html": f"""
<p>阅读全国财政面板时，必须严格区分三个基础规模指标——<strong>全国财富（Wealth）</strong>、<strong>全国税基（Tax Base）</strong> 与 <strong>{T('economical_base','经济基础（Economic Base）')}</strong>：</p>

<div class="formula-box">
<strong>从地点财富到阶层税款与国家开支的四组恒等式：</strong> {M('tax_efficiency')}<br>
1. <code>地点月财富 Wᵢ = 当地 RGO 利润 + 加工建筑利润 + 归入该地的市民贸易收益</code><br>
2. <code>地点可征税基 Tᵢ = Wᵢ × 当前控制力 Cᵢ</code>（全国税基比率 = <code>ΣTᵢ ÷ ΣWᵢ</code>，波希米亚 1337 实测为 <code>200.59 ÷ 292.73 = 68.52%</code>）<br>
3. <code>单阶层月税款 = Σ(Tᵢ × 该阶层当地财富份额) × 阶层实际税率 × (1 + 全国税收效率修正)</code>（前提：阶层当前满意度 ≥ 1%）<br>
4. <code>经济基础 E = (0.50 × 全国全额财富 W + 0.015 × 全国千人数 + 0.05 × 属国财富 + 特定收入项) × (1 + 0.066 × 已接纳思潮数)</code>
</div>

<ul>
  <li><strong>为什么有些富裕大国收不上税？看阶层财富权重与最大税率上限</strong>：地点财富先按当地人口每人权重（贵族 100、市民 40、教士 25、平民 1，且平民原始份额的 <code>1 − 农民自主权</code> 部分直接转给贵族）切分；若贵族或天主教教士因特权与宗教规则使<strong>最大税率上限降至 0%</strong>（如波希米亚开局 200.59 税基中贵族占 143.80、教士占 20.38，两者最大税率均为 0%），国库便只能从市民与平民的 36.40 税基中征得 7.80 金币。提高 <strong>税收效率</strong>、提高王室力量（满幅 +20% 税率上限）、压低豪强阶层超过 25% 的力量份额，以及提高 <strong>农民自主权</strong>（自由民价值观 +33%、城镇升格、平民迁徙权 +10%）是扩大实收税款的根本手段。</li>
  <li><strong>经济基础 E 如何决定三项核心月开支（各以 <code>0.10 × E</code> 为满额基准）</strong>：<br>
    • <strong>宫廷费用</strong> = <code>0.10 × E ÷ (1 + 宫廷费用效率) × 宫廷投入比例</code><br>
    • <strong>稳定度投资</strong> = <code>0.10 × E ÷ (1 + 稳定度投资效率) × 稳定度投入比例</code><br>
    • <strong>外交投入</strong> = <code>0.10 × E × (1 + 外交开支成本修正) × 外交投入比例</code><br>
    由此可见，吞并大片低控制力省份会立即按 50% 全额财富推高 <code>E</code>（使宫廷、维稳、外交变贵），却几乎不增加税基 <code>T</code>。</li>
</ul>
"""
            },
            {
                "id": "finance-debt",
                "title": "05 · 铸币收入与通胀、阶层贷款、政府债券与信用度公式",
                "en": "Minting & Inflation, Loans, Bonds, Creditworthiness & Bankruptcy",
                "html": f"""
<div class="formula-box">
<strong>1. 铸币收入（Minting）与通胀计算公式（波希米亚 / 匈牙利实机核对）：</strong> {M('minting_inflation_credit')}<br>
• <code>满效率铸币月收入 M = 全国税基 T × 0.25 × 铸币滑块比例 s × (1 + 铸币收入修正之和 m)</code><br>
&nbsp;&nbsp;例：波希米亚 <code>T = 200.59, s = 15.3%, m = +10%(金银币政策)</code> → <code>200.59 × 0.25 × 0.153 × 1.10 = 8.44</code> 金币/月；匈牙利叠加贵金属出口禁令(+33%)得 <code>m = +43%</code>。<br>
• <code>每种启用铸币材料（金/银/铜）月需求 = T × s × 0.01</code>（首都市场缺金银时铸币效率 η 跌向 0，实际收入 ≈ <code>M × η</code>）。<br>
• <code>铸币月通胀贡献（百分点/月） = max(0, 铸币比例百分数 − 免通胀阈值百分数) × 0.005</code>（如基础阈值 5% + 金银币政策 3% = 8% 平价线；开启「自动铸币」会自动将滑块锁在零净通胀水平）。
</div>

<table class="data-table">
  <thead><tr><th>赤字融资工具</th><th>本金规模与启用条件</th><th>利息、期限与资金去向</th><th>信用度与状态后果</th></tr></thead>
  <tbody>
    <tr>
      <td><strong>{T('loan','阶层贷款')} / 外邦借款</strong></td>
      <td>单笔本金 = <code>max(2, 0.5 × 经济基础 E)</code>；受阶层存款与国家贷款容量限制</td>
      <td>期限 <strong>60 个月</strong>（到期 3 个月宽限）；月利息 = <code>本金 × 年利率 ÷ 12</code>，利息流回本国阶层金库</td>
      <td>新借一笔基础信用 <strong>−0.5</strong>；按期履约还清最多 <strong>+2.0</strong>；到期无力偿还自动展期 <strong>−3.0</strong>；向债权国宣战 <strong>−15.0</strong></td>
    </tr>
    <tr>
      <td><strong>{T('government_bond','政府债券')}</strong></td>
      <td>文艺复兴《银行业》革新解锁（基础上1笔；首都建<strong>{T('central_bank','中央银行')}</strong>另加 +10 上限、面值 +10%、利率 −1%）；面值基数 = <code>max(10, 2.0 × E)</code></td>
      <td>无固定到期日，存续期持续支付债券利息（无国内接收方），直至玩家按面值主动赎回</td>
      <td>适合为重大基建或决战筹集长期资金，免受 60 个月集中到期挤兑</td>
    </tr>
    <tr>
      <td><strong>市民紧急拨款</strong></td>
      <td>阶层互动（需市民金库 ≥10 金币，40 政治影响力，五项求助共享 5 年冷却）</td>
      <td>直接从市民金库划转 <code>min(6 × 单笔阶层贷款额, 市民金库 × 50%)</code> 入国库，<strong>不形成债务、不付利息</strong></td>
      <td>市民当前满意度 −15 个百分点（防御战价格减半），同时减少市民当期消费与自建资金</td>
    </tr>
  </tbody>
</table>

<div class="formula-box">
<strong>2. 信用度（{T('creditworthiness','Creditworthiness')}，0–100）如何决定贷款与债券利率：</strong><br>
• <code>目标信用评级 = 50 + 稳定度贡献（每 +1 稳定给 +0.1，满 +100 稳定给 +10） + 强权/官僚/改革加值</code>（基础评级每月向目标移动 10% 差额）<br>
• <code>有效信用 = clamp(基础评级 − 独立破产惩罚, 0, 100)</code>（有效信用 &lt; 30 时外国 AI 拒绝放贷）<br>
• <code>普通贷款年利率信用修正（百分点） = −5 × (有效信用 ÷ 100 − 0.5)</code>（有效信用 80 时减息 −1.5 个百分点；债券系数为 −4）<br>
• <strong>{T('bankrupt','破产（Bankruptcy）')} 三阶段代价</strong>：① <strong>当日</strong>：稳定度 −50、通胀按比例 −25%、控制力按原值 −33%、部队 25% 损失判定、建筑 10% 降级判定；② <strong>随后 60 个月</strong>：王室力量 −90%、陆海军士气/科研速度/建造速度均 −90%、贷款容量 −50%、阶层均衡满意度 −2.5%；③ <strong>长期信用扣减</strong>：新增 <strong>50 点独立破产惩罚</strong>，每年仅消退 0.5 点（完全归零需 <strong>100 年</strong>）。
</div>
"""
            },
        ],
        "discussion": {
            "title": "实算专题 · 扩张吞并一块新领土，控制力要达到多少才不亏钱？",
            "html": """
<ul>
  <li><strong>吞并财政盈亏平衡线公式</strong>：设新吞并省份每月创造财富 <code>50</code> 金币、人口 <code>200</code> 千人，本国已接纳 2 项思潮（系数 <code>1.132</code>），则新增经济基础 <code>ΔE = (0.50×50 + 0.015×200) × 1.132 = 31.70</code> 点。若本国宫廷、外交与官僚合计每点经济基础边际月支出为 <code>0.15</code> 金币，则每月固定增支 <strong>4.75 金币</strong>。</li>
  <li>设综合有效税率 <code>15%</code>、满效率铸币比例 <code>20%</code>（每点税基另增 <code>0.25×0.20 = 0.05</code> 铸币收入），则盈亏平衡控制力 = <code>4.75 ÷ [50 × (0.15 + 0.05)] ≈ 47.5%</code>！若该飞地实际控制力只有 10%，每月税铸合计仅收 1.00 金币，国库每月净倒贴 3.75 金币。反之若将其设为普通附庸（属国财富仅按 0.05 权重计入宗主经济基础，<code>ΔE</code> 仅增 2.83 点，且每月按 20% 缴贡），财政立刻由负转正。</li>
</ul>
"""
        },
        "quick_links": [
            ("生产效率 97 项来源反查", "metrics.html#production_efficiency"),
            ("501 种建筑全数值速查表", "ledgers.html#building_types"),
            ("346 项建筑生产与维护配方", "directory.html#recipes"),
            ("75 种商品图标与基础数据", "ledgers.html#goods"),
        ],
    },

    # =========================================================================
    # CHAPTER 04
    # =========================================================================
    {
        "id": "ch04",
        "slug": "ch04-government-cabinet.html",
        "num": "04",
        "pillar": "state",
        "title": "政体、社会价值观、改革法律、官僚与内阁人物",
        "en": "Government, Societal Values, Laws, Bureaucracy, Characters & Cabinet",
        "subtitle": "厘清五大政体资源高低端分段公式、稳定度与政治影响力的精确算法、官僚机构预算比例与固化度机制，以及人物能力如何放大 81 项内阁行动。",
        "upstream": [
            ("王室力量与阶层力量份额", "ch05-estates-rebels.html#power-balance", "王室份额放大内阁效率与撤特权折扣，内阁任职反向赋予阶层力量"),
            ("经济基础与国库预算", "ch03-economy-market-trade.html#wealth-to-treasury", "决定宫廷、稳定度与官僚机构的月度金币账单"),
            ("时代更替与革新解锁", "ch07-ages-colonial.html#ages-institutions", "逐步开放新价值观轴、内阁席位、改革槽与高阶内阁行动"),
        ],
        "engine": "通过政体资源、稳定度与政治影响力驱动制度演进，在 17 对社会价值观轴上定向引导改革与法律政策，配置 60 种官僚机构预算，并选派高能力人物执行内阁任务。",
        "downstream": [
            ("领土整合、提控与灾后恢复", "ch01-territory-core.html#integration-core", "内阁效率与君臣能力直接乘算省份治理速度"),
            ("国家等级升格与五大霸权", "ch10-diplomacy-subjects.html#diplo-capacity", "满足人口与威望门槛升格公国/王国/帝国，列强竞逐世界霸权"),
            ("王位继承稳定与勋贵加成", "ch06-culture-religion.html#languages-art", "继承法、角色互动与骑士团成员身份维系王朝统治"),
        ],
        "redlines": [
            ("50 点政体资源分界", "高低端修正切换点", "正统性/共和传统/奉献度/游牧团结低于 50 时触发最大控制力 −20%、满意度 −5% 缩放惩罚"),
            ("100 政治影响力", "核心制度货币上限", "君主三维×0.005 + 大臣对应能力×0.015÷总席位；空席计 0 分拉低月产出"),
            ("100 稳定度 vs 20", "换政策两条路径价差", "直接更换现行政策基础耗 100 稳定度；通过议会请求换法享 0.20 倍率仅需 20 稳定度"),
            ("+0.5% / 每点能力", "内阁行动效率系数", "君主与执政大臣每 1 点对应能力各加 +0.5% 行动效果，首脑大臣另加 +25% 个人效率"),
        ],
        "sections": [
            {
                "id": "government-power",
                "title": "01 · 国家类型、等级霸权与三大核心政治指标",
                "en": "Country Types, Ranks, Hegemons & Core Political Metrics",
                "html": f"""
<p>一国在地图上的存续方式由五种<strong>国家类型</strong>定义：{T('settled_country','定居国家')}（保有一处地点即存续）、{T('extraterritorial_country','地产/建筑国家')}（依靠境外建筑存续，如汉萨同盟、巴尔迪银行）、{T('society_of_pops','游群社会')}（依靠本国人口存续，研究农业、城市建设、冶金、税收四项革新后可执行定居）、{T('army_based','兵团国家')} 与 {T('navy_based','舰队国家')}（失去全部赖以存续的陆军或舰队即瓦解）。<strong>迁都</strong>基础金币为 <code>12 × 经济基础</code> + 50 政治影响力及石材/木材/纸/书建材，工期 <code>180 + 0.05 × 距离</code> 天。</p>

<table class="data-table">
  <thead><tr><th>晋升目标 / 国际地位</th><th>人口 / 积分与威望硬门槛</th><th>核心制度奖励与开放能力</th></tr></thead>
  <tbody>
    <tr><td><strong>公国（Duchy）</strong></td><td>总人口 &gt;20万（或正信 &gt;15万 / 接纳文化 &gt;10万），威望 &gt;25</td><td>外交容量 +1，开启胜利卡机制</td></tr>
    <tr><td><strong>王国（Kingdom）</strong></td><td>总人口 &gt;200万（或正信 &gt;150万 / 接纳文化 &gt;100万），威望 &gt;50，独立</td><td>外交容量 +2，艺术家名额 +1</td></tr>
    <tr><td><strong>帝国（Empire）</strong></td><td>总人口 &gt;1000万（或正信 &gt;750万 / 接纳文化 &gt;500万），威望 &gt;70，独立列强（天主教国另需教宗好感 &gt;100）</td><td>外交容量 +3，<strong>内阁席位 +1</strong>，艺术家名额 +2</td></tr>
    <tr><td><strong>区域强权（≥20分） / 列强（≥40分）</strong></td><td>控制地区 ≥2/3 地点获强权分 <code>潜在税基 ÷ (全球中位数÷5)</code>（每区 1–20 分；附庸转交 25%、自治领 50%、殖民国 75%）</td><td>列强获每月外交官 +0.20、力量投射 +10、月威望 +0.10、雇佣范围 +50%、债券上限 +2，开放干涉/强制和平/威胁战争</td></tr>
    <tr><td><strong>五类世界霸权（Hegemony）</strong></td><td>独立列强且单项全球第一（挑战者须超在位者 <strong>110%</strong> 触发 12 个月交替宽限；每持一霸权所受敌意 +10%）</td><td><strong>经济</strong>（税贸最高：耗粮 −10%）、<strong>海军</strong>（重舰最多：海伤 −10%）、<strong>军事</strong>（常备军最多：战分效率 +20%）、<strong>外交</strong>（声誉最高：改善关系 +30%）、<strong>文化</strong>（文化影响最高：传统 +25%）</td></tr>
  </tbody>
</table>

<div class="formula-box">
<strong>核心政治资源公式与影响因素：</strong> {M('stability_legitimacy_pi')}
<ul>
  <li><strong>五大政体专属 {T('government_power','政府力量')}（0–100，以 50 点为分界）</strong>：君主制（{T('legitimacy','正统性')}，满 100 给王室力量 +10%）、共和制（{T('republican_tradition','共和传统')}，满 100 给立法效率 +10%）、神权制（{T('devotion','奉献度')}）、游牧（{T('horde_unity','游牧团结')}，满 100 给训练度 +10%）、部落（{T('tribal_cohesion','部落凝聚力')}，满 100 给征召规模 +25%）。前四类低于 50 时，统一按 <code>(100 − 当前值) ÷ 100</code> 施加<strong>最大控制力 −20 个百分点、阶层满意度均衡 −5 个百分点</strong>的共同惩罚。</li>
  <li><strong>{T('stability','稳定度')}（−100 至 +100）</strong>：自然项按 <code>−当前稳定度 × 0.005</code> 趋近 0；满 +100 时提供<strong>人口升阶速度 +100%、信用度 +10、政治影响力月获取 +10%、阶层均衡满意度 +5%、入叛门槛 −10%</strong>；负稳定度则扣减满意度均衡（最高 −30%）与建筑设立速度。提升稳定度靠财政滑块投入（受「维稳效率」除数减费）、正教士满意度与 MIL 内阁「稳定国家」。</li>
  <li><strong>{T('political_influence','政治影响力')}（储存上限 100）精确月产出公式</strong>：<br>
    <code>每月获取 = [0.005 × (君主 ADM + DIP + MIL) + Σ(在职大臣当前行动对应能力 × 0.015 ÷ 全国总席位数) + 固定来源] × (1 + 获取百分比修正)</code><br>
    注意：大臣只计入其<strong>正在执行任务所属维度</strong>的那一项能力，且空缺席位贡献为 0！此外，每 1 点当前储备的政治影响力还会为全国阶层满意度恢复速度提供 <code>+0.003 个百分点/月</code>。</li>
</ul>
</div>
"""
            },
            {
                "id": "societal-values",
                "title": "02 · 17 对社会价值观轴线（−100 至 +100）",
                "en": "17 Societal Value Axes & Strategic Tradeoffs",
                "html": f"""
<p>{T('societal_value','社会价值观')} 由 17 条双极轴线组成（范围 −100 至 +100，按当前位置比例折算两端满额效果；法律、改革、特权、内阁行动与高权势阶层决定每月漂移方向）：</p>
<table class="data-table">
  <thead><tr><th>代表性价值观轴线（全 17 对见速查表）</th><th>解锁时期 / 资格</th><th>两端核心修正取舍（满端 ±100 基准）</th></tr></thead>
  <tbody>
    <tr><td><strong>中央集权 ↔ 地方分权</strong></td><td>开局通用</td><td><strong>中央集权</strong>：王室力量 +50%、邻近度效率 +20%、外交吞并速度 +33%、属国忠诚 −20；<strong>地方分权</strong>：属国忠诚 +30、阶层满意度均衡 +5%、吞并速度 −33%</td></tr>
    <tr><td><strong>资本经济 ↔ 传统经济</strong></td><td>开局通用</td><td><strong>资本经济</strong>：全国加工生产效率 +10%、银行利率 −3%，解锁现代财政簿记改革；<strong>传统经济</strong>：强化农矿原材料产出与传统庄园经济</td></tr>
    <tr><td><strong>农奴制 ↔ 自由民</strong></td><td>开局通用</td><td><strong>农奴制</strong>：全国原料产出 +20%、农民自主权 −33%；<strong>自由民</strong>：农民自主权 +33%、强化人口流动与平民求助稳定度收益</td></tr>
    <tr><td><strong>守旧 ↔ 创新</strong></td><td>开局通用</td><td><strong>创新</strong>：最大识字率 +10%、接纳思潮花费 −50%，解锁《思潮之路》等科研改革；<strong>守旧</strong>：强化正统稳定与首都集权改革资格</td></tr>
    <tr><td><strong>属灵 ↔ 人文</strong></td><td>开局通用</td><td><strong>属灵</strong>：强化人口改宗速度与正统容忍；<strong>人文</strong>：提升异端与异教容忍度、文化融合能力</td></tr>
    <tr><td><strong>重商主义 ↔ 自由贸易</strong></td><td>宗教改革时代</td><td><strong>重商主义</strong>：最高关税上限 +50%、最高补贴上限 +50%、强化本国市场保护；<strong>自由贸易</strong>：强化跨市场商路扩展与运力</td></tr>
    <tr><td><strong>时代与专属轴线（6 条）</strong></td><td>时代 / 宗教 / 国别</td><td>发现时代开放「注重外务 ↔ 注重内政」；专制时代开放「专制主义 ↔ 自由主义」；伊斯兰/德鲁兹等开放「隐义主义（士气/传教+10%） ↔ 教法学（科研/内阁效率+10%）」；东亚周边开放「汉化 ↔ 去汉化」；拜占庭专属「拉丁化 ↔ 罗马派」</td></tr>
  </tbody>
</table>
"""
            },
            {
                "id": "bureaucracy",
                "title": "03 · 政府改革、法律政策与官僚机构固化机制",
                "en": "Government Reforms, Laws/Policies & Bureaucracy Entrenchment",
                "html": f"""
<ul>
  <li><strong>政体转换、主要改革与普通改革（379 项）</strong>：跨政体转换（如君主制转共和制需和平、稳定 &gt;0、正统性 &gt;80、财阀方向 ≥95 且市民力量高于贵族；草原部落转君主制基础耗 50 稳定与 25 正统，历经 15 年过渡期）条件严格。既定政体下，全国限持 1 项「{T('major_reform','主要改革')}」，普通 {T('government_reform','政府改革')} 受改革槽位限制，实施期通常为 2 年（效果按完成度线性生效，如《港口管理局》给海军总督上限 +1、沿海发展增长 +10%、出入港邻近成本 −20%）。</li>
  <li><strong>法律与政策（213 部法律 / 832 项政策）</strong>：涵盖继承、宗教、军事、行政、社会经济、阶层及国际组织七大类。首次为未设政策的法律选定政策耗 <strong>20 政治影响力</strong>；直接更换已有政策基础耗 <strong>100 稳定度</strong>（部分国家另耗 10 正义值）；而在议会会期内消耗 50 个百分点支持度发起「<strong>请求议会更改法律</strong>」，可将稳定度与正义值代价乘以 <strong>0.20</strong>（即 100 稳定度折算为 20 点！）。「立法效率」修正可缩短改革与政策的实施年限。</li>
  <li><strong>60 种 {T('bureaucracy','官僚机构')} 与预算—固化双变量规则</strong>：占用官僚席位（大都市首都亦提供席位），维护费按国家经济基础缩放（如税务委员会乘数为 <code>经济基础 × 0.004</code>）。在同一 {T('entrenchment','固化度')} 下，设当前预算维护比例为 <code>f</code>（0–1）：<br>
    <code>实际生效正向效果 = 全额正向值 × f</code> &nbsp;│&nbsp; <code>实际生效负面效果 = 全额负面值 × (1 − f)</code><br>
    机构存续越久，固化度以 100 年为减半阶段周期持续上升，同步放大正负效果并抬高日常维护与裁撤费用；当固化度超过 25 时，可通过议会行动每次削减 10 点固化度。</li>
</ul>
"""
            },
            {
                "id": "characters-interactions",
                "title": "04 · 人物成长、三维能力映射与 34 项角色互动",
                "en": "Child Education, Ability Scaling & 34 Character Interactions",
                "html": f"""
<p>角色自 <strong>3 岁至 16 岁成年</strong> 共经历 156 个月受教期（每月 55% 概率判定成长，期望发生 85.8 次增长）：<strong>平衡教育</strong>使三项能力成长率各 +50%（约 1.5 倍基准）；<strong>行政/外交/军事专精教育</strong>使主项成长率 +100%（2 倍基准）、其余两项 +25%（1.25 倍基准）。统治者在位满 1、10、25 年判定获取统治者特质；内阁大臣每月约 2% 概率习得内阁特质。</p>

<table class="data-table">
  <thead><tr><th>任职身份</th><th>每 1 点行政能力 (ADM)</th><th>每 1 点外交能力 (DIP)</th><th>每 1 点军事能力 (MIL)</th></tr></thead>
  <tbody>
    <tr>
      <td><strong>在位统治者（Ruler）</strong></td>
      <td>王室力量 <strong>+0.25%</strong>、建筑建造效率 <strong>+0.2%</strong>、邻近度传播速度 +0.1%、聘顾问费 −0.5%</td>
      <td>阶层满意度均衡 <strong>+0.1 个百分点</strong>、外交声誉 <strong>+0.05</strong>、属国忠诚 +0.10、外交容量 +0.01、聘艺术家费 −0.5%</td>
      <td>陆军与海军士气各 <strong>+0.1%</strong>、招募陆海军将领费用各 −0.5%</td>
    </tr>
    <tr>
      <td><strong>陆军将军 / 海军将领</strong></td>
      <td>陆将：围城能力 +0.1%、每路宽度 +0.1%、后勤距离 +0.5%<br>海将：封锁效率 +0.5%、宽度 +0.1%、维护效率 +0.5%</td>
      <td>陆将：陆军士气 +0.2%、主动性 +1%、耗粮 −0.5%<br>海将：海军士气 +0.2%、主动性 +1%、海上存在 +0.5%</td>
      <td>陆将：训练度 <strong>+0.1%</strong>、参战速度 +0.5%、行军 +0.2%<br>海将：海战伤害 <strong>+0.2%</strong>、参战速度 +0.5%、航速 +0.2%</td>
    </tr>
  </tbody>
</table>

<p><strong>王朝继承与 34 项人物画像互动要点</strong>（完整列表见速查表）：</p>
<ul>
  <li><strong>继承顺位与退位</strong>：46 种 {T('heir_selection','继承法')} 规定顺位与摄政安排。普通退位需已有合格继承人（如君主 &gt;60 岁且总能力 &lt;100、成年继承人总能力 &gt;170），基础花费 50 威望与 40 正统性，40 岁后每多 1 岁费用乘数减 0.02（65 岁退位即半价）。</li>
  <li><strong>关键人事与继承调控</strong>：「誓发终身愿（Take the Vows）」可将非继承人宗室转入教士阶层并加入修会；匈牙利等特定君主国王权 ≥50% 时可用「赋予女性继承权（Prefection）」授予女性法定男性继承权；「封为贵族（Ennoble）」耗 10 政府力量将平民人才拔入贵族并创立新家族；「授予赐封领地（Grant Governorship）」将边区建为总督附庸（流放型同时剥夺继承权）；「接手地区防务」在战时按人物 ADM 强化地区防务 10 年。</li>
</ul>
"""
            },
            {
                "id": "cabinet-actions",
                "title": "05 · 内阁席位、内阁首脑与「内阁效率」完整公式",
                "en": "Cabinet Seats, Head of Cabinet & Complete Cabinet Efficiency Formula",
                "html": f"""
<p>国家基础拥有 <strong>2 个内阁席位</strong>（升格帝国 +1 席，特定改革与时代革新继续增加；更换大臣基础费 20 政治影响力）。全游戏 81 项内阁行动按能力划分为行政（38 项）、外交（20 项）与军事（23 项）三系。</p>

<div class="formula-box">
<strong>内阁行动最终效果公式与「内阁效率」决定因素：</strong> {M('cabinet_efficiency')}<br>
<code>单项内阁行动增幅 = 0.005 × 统治者对应能力 + 0.005 × 执政大臣对应能力 + 全国内阁效率 + 大臣个人内阁效率</code><br>
<code>行动实际效果 = 脚本基础效果 × (1 + 单项内阁行动增幅)</code>
<ul>
  <li><strong>实机核对（1337 年莫斯科样本）</strong>：执行 ADM 行动「提升控制力」（基础上限 +10%、月控制 +1%）时，君主 ADM 66（+33%）、大臣 ADM 70（+35%）、全国内阁效率 +15.07%，总增幅为 <strong>+83.07%</strong>，实际提供 <strong>+18.30% 最大控制力与 +1.83%/月增速</strong>！</li>
  <li><strong>全国内阁效率（Country Cabinet Efficiency）从哪里来？</strong>：① <strong>王室力量份额</strong>：满 100% 王室份额提供高达 <strong>+50% 全国内阁效率</strong>（例如王室占 30.14% 直接贡献 +15.07%）；② <strong>阶层与价值观</strong>：齐米阶层高满意度（系数 0.1）、教法学价值观满端（+10%）；③ <strong>特权、官僚与革新</strong>：教士特权《宗教顾问委员会》(+5%)、《讲学之誓》(+10%) 及多项行政改革与革新；④ <strong>文化超容惩罚</strong>：文化容量每超额 1 点直接扣减 <strong>−10% 全国内阁效率</strong>！</li>
  <li><strong>晋升 {T('head_of_the_cabinet','内阁首脑')}（基础费 50 政治影响力）的双向连锁效应</strong>：首脑本人获得 <strong>+25 个百分点个人内阁效率</strong>且内阁特质翻倍；同时其<strong>出身阶层获得 +25% 全国政治力量修正</strong>（若提拔王室宗亲任首脑，既强化首脑任务，又通过推高王室力量份额连带提高其余所有大臣共用的全国内阁效率；若提拔非王室首脑，则给该阶层满意度均衡 +5%）。</li>
  <li><strong>普通大臣入阁的权力代价</strong>：两席满员状态下，每名在任大臣为所属阶层提供 <code>25% ÷ 总席位数</code>（如两席各 +12.50%）的政治力量加成；研究《非世袭官僚》(−10%) 与《专制宫廷》(−50%) 可压低外姓大臣带来的阶层扩权。</li>
</ul>
</div>
"""
            },
        ],
        "discussion": {
            "title": "治理排期 · 内阁席位紧张时如何按瓶颈分配任务？",
            "html": """
<ul>
  <li><strong>战后与扩张期的席位排序原则</strong>：① 若富庶核心省在战争中陷入负繁荣度（荒废），优先派高 DIP 大臣执行「<strong>专注恢复</strong>」止住生产效率亏损与人口流失；② 对刚割让的核心邻近省份派高 MIL 大臣执行「<strong>整合省份</strong>」消除 −10% 控制上限与叛乱源；③ 对未受控财富最高的核心富裕省常驻高 ADM 大臣执行「<strong>提升控制力</strong>」即时放大税基；④ 和平发育期则转向「<strong>开发省份</strong>」「<strong>研究思潮</strong>」（选人口最多的核心省冲刺 20% 接纳线）或「<strong>推广文化 / 改宗</strong>」（冲刺 50% 核心文化线）。</li>
</ul>
"""
        },
        "quick_links": [
            ("内阁效率 301 项来源反查", "metrics.html#cabinet_efficiency"),
            ("81 项内阁行动完整筛选表", "ledgers.html#cabinet_actions"),
            ("379 项政府改革 & 213 部法律", "ledgers.html#government_reforms"),
            ("34 项角色互动 & 60 种官僚机构", "ledgers.html#character_interactions"),
        ],
    },

    # =========================================================================
    # CHAPTER 05
    # =========================================================================
    {
        "id": "ch05",
        "slug": "ch05-estates-rebels.html",
        "num": "05",
        "pillar": "state",
        "title": "王室与阶层力量、财富消费、特权议会与叛乱检定",
        "en": "Crown & Estate Power, Wealth & Consumption, Privileges, Parliament & Rebels",
        "subtitle": "从每千人政治权重推导出王室与阶层份额，完整列出力量超过 25% 与满意度偏离 50% 时的全国修正表，解析撤销特权成本、12 项阶层互动、议会支持度与要塞留忠公式。",
        "upstream": [
            ("人口阶级结构与地点控制力", "ch01-territory-core.html#control", "每千名不同阶级居民产生基础政治点数，控制力决定王室本地得分"),
            ("地点财富与农民自主权", "ch03-economy-market-trade.html#wealth-to-treasury", "决定各阶层税后存款、消费购物清单及阶层自建能力"),
            ("宗教文化待遇与稳定度", "ch06-culture-religion.html#culture-status", "共同决定底层人群满意度是否跌破 20% 加入叛乱运动"),
        ],
        "engine": "在同一全国分母下核算王室与各阶层的政治力量份额，通过满意度均衡点管理税率与征召资格，运用阶层互动与 180 天议会推进改革，并在叛乱爆发时检定要塞守军归属。",
        "downstream": [
            ("税率上限、贸易分成与内阁效率", "ch03-economy-market-trade.html#trade-orders", "王室份额按比例转化为贸易分成(+100%)、内阁效率(+50%)与撤特权折扣(−100%)"),
            ("全国科研、威望、粮产与士气修正", "ch07-ages-colonial.html#research-advances", "教士满意度驱动研究速度，贵族驱动威望正统，平民驱动粮产与维稳"),
            ("陆海军征召动员资格", "ch08-military-combat.html#force-types", "阶层当前满意度低于 25% 无法征召该阶层兵员，低于 1% 停止纳税"),
        ],
        "redlines": [
            ("25% 力量分界线", "阶层高低权势切换点", "非王室阶层份额超 25% 部分压低本阶层税率上限并扣每月政体资源；低于 25% 则提高税率上限"),
            ("50% 满意度零点", "阶层全国加成基准", "各阶层全国加成按 (当前满意度 − 50%) 线性正负缩放；<25% 禁征召，<1% 停征税"),
            ("400 × 阶层份额", "撤销特权稳定度基数", "再乘 (1 − 王室份额 + 其他折扣)；当日满意度骤降 25 + 3Δ 个百分点"),
            ("5,000 人 / >80%", "公开叛乱与要塞减忠线", "支持者 ≥5,000 人方形成公开起义；叛军进度超 80% 使起事时要塞留忠概率直接 −20 个百分点"),
        ],
        "sections": [
            {
                "id": "power-balance",
                "title": "01 · 王室力量与各阶层力量的计算公式及全国效果表",
                "en": "Crown Power vs Estate Power Formulas & National Modifier Tables",
                "html": f"""
<p>全国政治力量由<strong>王室（Crown）</strong>与各非王室阶层（贵族、教士、市民、平民，以及特定国家存在的齐米、部落、哥萨克）共同瓜分总份额 100%。底层点数从每个地点的<strong>同一批人口</strong>分两套规则算出：</p>

<div class="formula-box">
<strong>1. 每千人基础政治力量权重（<code>pop_types/00_default.txt</code>）：</strong><br>
贵族 <strong>25</strong> ｜ 教士 <strong>10</strong> ｜ 市民 <strong>4</strong> ｜ 部落民 <strong>0.25</strong> ｜ 士兵 <strong>0.0625</strong> ｜ 劳工 <strong>0.0375</strong> ｜ 农民 <strong>0.025</strong> ｜ 奴隶 <strong>0</strong>（受歧视文化人口为 0）<br>
<em>例：2,000 名贵族基础提供 50 点，相当于 12,500 名市民或 2,000,000 名农民的基础政治点数。</em><br><br>
<strong>2. 地点王室点数与全国王室份额公式：</strong> {M('crown_estate_power')}<br>
• <code>地点王室点数 = [Σ(当地各类千人数 × 基础政治权重)] × (当前控制力 + 本地王室力量修正，如会计室 Counting House +33%)</code><br>
&nbsp;&nbsp;例：某地有 20,000 市民（原始 80 点）、控制力 15%：无建筑时王室得 <code>80 × 0.15 = 12</code> 点；建满效会计室(+33%)后倍率升至 0.48，王室得 <strong>38.4 点</strong>。<br>
• 汇总各地点后，再叠加<strong>君主 ADM</strong>（每点 +0.25%）、<strong>王室成员入阁/任首脑</strong>（两席制下单席 +12.5%，王室首脑另 +25%）、<strong>中央集权价值观</strong>（满端 +50%）、高正统性（满端 +10%）等全国修正得到<code>王室最终点数</code>。<br>
• 各非王室阶层则汇总各自人口基础点数，乘以本地阶层建筑（如贵族公馆 +50%）、所授特权（每项常加 +20%~+75%）及该阶层大臣入阁加成得到<code>阶层最终点数</code>。<br>
• <code>各方全国力量份额 = 该方最终点数 ÷ (王室最终点数 + 全体非王室阶层最终点数之和)</code>
</div>

<table class="data-table">
  <thead><tr><th>权力主体</th><th>力量份额高于分界时的全国效果</th><th>力量份额低于 25% 分界时的效果</th></tr></thead>
  <tbody>
    <tr>
      <td><strong>王室（Crown）</strong><br><em>直接按自身份额 0–100% 乘满幅系数</em></td>
      <td colspan="2">• <strong>财政与行政</strong>：国家贸易收入分成 <strong>+100 个百分点</strong>、关税分成 <strong>+100 个百分点</strong>、全国内阁效率 <strong>+50%</strong>、议会基础支持度 <strong>+50 个百分点</strong>（即王室份额的一半）、全国阶层税率上限 <strong>+20 个百分点</strong>、阶层满意度均衡 +30 个百分点。<br>• <strong>改制与外交</strong>：<strong>撤销特权稳定度成本 −100%</strong>、更换政策成本 −50%、拆阶层建筑满意度损失 −50%、外交声誉 +2、力量投射 +5。</td>
    </tr>
    <tr>
      <td><strong>贵族（Nobility）</strong><br><em>以 25% 为分界</em></td>
      <td>超出部分 ×（贵族税率上限 −100%、征召战斗效率 +100%、要塞维护效率 +100%、月政体资源 −0.20）</td>
      <td>不足部分 ×（贵族税率上限 +50 个百分点）</td>
    </tr>
    <tr>
      <td><strong>教士（Clergy）</strong></td>
      <td>超出部分 ×（教士税率上限 −50%、人口改宗速度 +200%、维稳效率 +100%、月向属灵 +0.33、月政体资源 −0.20）</td>
      <td>不足部分 ×（教士税率上限 +25 个百分点）</td>
    </tr>
    <tr>
      <td><strong>市民（Burghers）</strong></td>
      <td>超出部分 ×（市民税率上限 −50%、贸易容量 +100%、海军维护效率 +50%、月政体资源 −0.20）</td>
      <td>不足部分 ×（市民税率上限 +50 个百分点）</td>
    </tr>
    <tr>
      <td><strong>平民（Commoners）</strong></td>
      <td>超出部分 ×（平民税率上限 −50%、买粮效率 +100%、全国满意度均衡 +5%、月向自由民 +0.33、月政体资源 −0.20）</td>
      <td>不足部分 ×（平民税率上限 +50 个百分点）</td>
    </tr>
  </tbody>
</table>
"""
            },
            {
                "id": "estate-wealth",
                "title": "02 · 阶层满意度全国效应、财富分账与阶层自建循环",
                "en": "Estate Satisfaction Scaling, Wealth Distribution & Autonomous Construction",
                "html": f"""
<p><strong>1. 阶层满意度（Estate Satisfaction）与均衡值收敛速度</strong> {M('estate_satisfaction')}：<br>
公共基础均衡值为 25%，叠加王权、君主 DIP（每点 +0.1%）、正稳定度（满 +5%）、地方分权（满 +5%）、所授特权加值，扣去实际税率、厌战度（每点 −1%）、负稳定度及异端/异教阶层惩罚后得到<strong>满意度均衡点</strong>。低于均衡时每月恢复 <code>0.10 + 0.003 × 当前政治影响力储备 + 恢复修正</code> 个百分点；高于均衡时每月衰减差额的 <code>5%</code>。</p>
<ul>
  <li><strong>两条硬资格线</strong>：当前满意度 <strong>&lt; 25%</strong> 无法征召该阶层陆海军；<strong>&lt; 1%</strong> 停止缴纳阶层税。</li>
  <li><strong>以 50% 为零点的连续全国修正</strong>（按 <code>(当前满意度 S − 0.50) × 系数</code> 计算，高于 50% 为正加成，低于 50% 转为负惩罚，且以 <code>2 × (S − 0.50)</code> 进入所属人口满意度）：<br>
    • <strong>贵族</strong>：月威望 ×0.2、月正统性 ×0.2 ｜ • <strong>教士</strong>：<strong>研究速度 ×0.5</strong>（75% 满意即 +12.5% 科研！）、外交声誉 ×2 ｜ • <strong>市民</strong>：贸易优势 ×0.5、加工生产效率 ×0.025 ｜ • <strong>平民</strong>：维稳效率 ×0.4、食物产出 ×0.125、征召恢复 ×0.5 ｜ • <strong>齐米</strong>：异教容忍 ×2、内阁效率 ×0.1 ｜ • <strong>部落 / 哥萨克</strong>：食物产出 ×0.05，部落另加原产 ×0.05，哥萨克另减月厌战 −0.05。</li>
</ul>

<p><strong>2. 地点财富分账、消费反馈与阶层自主建造</strong>：</p>
<ul>
  <li><strong>财富分配权重与农民自主权</strong>：地点财富按当地人数乘每人财富权重（<strong>贵族 100、市民 40、教士 25、平民 1、齐米 1、哥萨克 0.5、部落 0.01</strong>）切分原始份额；随后平民与齐米仅保留 <code>原始份额 × 当地农民自主权</code>（全国基础 25%，乡村 −20 / 镇 +10 / 城 +25 / 都 +50，农奴制 −33 / 自由民 +33，下限 10%），其余部分直接转归当地贵族。</li>
  <li><strong>财富影响（{T('wealth_impact','Wealth Impact')} = 阶层月收入 ÷ 月支出）与自主建造</strong>：阶层税后留存、控制力以外的未受控财富、贸易分红与贷款利息汇入阶层金库，首先支付当地人口对 75 种商品的采购账单与买粮分摊。当收支盈余（财富影响 &gt;100%）时，阶层会按常规造价的 <strong>4 倍系数</strong> 出资扩建有利可图的 RGO、工坊或道路；但在控制力 <strong>&lt; 75%</strong> 的地点，阶层也可建造扩大地方权势的 <strong>{T('estate_building','阶层专属建筑')}</strong>（如通行税城堡：贵族力量 +50%、市场接入 −2.5%；唯有将当地控制力提至 ≥75% 后，国家才能以 −20% 满意度代价直接申请拆除），或在拥有私军特权且存款 ≥ 维护费 2 倍时供养 <strong>{T('private_regiment','私人军团')}</strong>。</li>
</ul>
"""
            },
            {
                "id": "estate-interactions",
                "title": "03 · 12 项阶层直接互动与紧急求助规则全表",
                "en": "Complete Table of 12 Estate Interactions & Emergency Actions",
                "html": f"""
<p>在「政府 → 阶层行动」侧栏可执行 4 项常规调节互动与 8 项紧急资源转化行动。<strong>防御性战争规则</strong>：处于防御战时，「要求扩大征召」「征收特别税」及五项阶层专属求助的<strong>政治影响力与缩放金币价格全部减半</strong>，其中「扩大征召」与「特别税」的满意度扣减也同步减半（五项专属求助共享同一个 5 年冷却，满意度扣减维持原值）：</p>
<table class="data-table">
  <thead><tr><th>行动名称</th><th>适用条件</th><th>标准费用与冷却期</th><th>执行效果与满意度变动</th></tr></thead>
  <tbody>
    <tr><td><strong>贿赂阶层</strong></td><td>目标税基 &gt;0.01，国库充足</td><td>金币 = <code>目标阶层税基 × 12</code>；无独立冷却</td><td>同额金币转入该阶层金库；目标当前满意度 <strong>+10 个百分点</strong></td></tr>
    <tr><td><strong>削减阶层力量</strong></td><td>拥有阶层建筑、力量 &lt;90%、当前满意度 &gt;50%</td><td>无独立冷却</td><td>国库获 <code>税基 × 2</code> 金币；按控制力排序拆除最多 <code>min(20, 2 + 地点数÷20)</code> 座阶层建筑（大教堂除外）；满意度基础 <strong>−50 个百分点</strong>（受拆楼影响修正）</td></tr>
    <tr><td><strong>出售艺术品给阶层</strong></td><td>保有非无价、非御宝的现存艺术品</td><td>移除该作品；无独立冷却</td><td>国库获得作品估值 <strong>60%</strong> 的金币，原作品文化加成终止</td></tr>
    <tr><td><strong>征用私兵</strong></td><td>有贵族/哥萨克私军特权且有待命私兵</td><td>正统性 −10、政治影响力 −15；冷却 3 年</td><td>全部待命私人团编入国家军队（解散归还阶层；若该阶层起兵叛乱则立即召回）</td></tr>
    <tr><td><strong>要求扩大征召</strong></td><td>任意税基 &gt;0.01 的阶层</td><td>25 政治 + 系数 4 缩放金币；独立冷却 5 年</td><td>12 个月全国陆军征召规模 <strong>+15%</strong>；目标满意度 −12.5%（防御战 −6.25%）</td></tr>
    <tr><td><strong>征收特别税</strong></td><td>税基 &gt;0.01（天主教教士除外）</td><td>25 政治影响力；独立冷却 5 年</td><td>12 个月目标最高税率上限 <strong>+10 个百分点</strong>；满意度 −12.5%（防御战 −6.25%）</td></tr>
    <tr><td><strong>召开紧急议会</strong></td><td>战时、无在开议会且处 59 月冷却内</td><td>正统性 −10、政治影响力 −10；冷却 5 年</td><td>立即在首都开启选定议案的议会会期</td></tr>
    <tr><td><strong>请求神职者支持</strong></td><td>教士阶层（每位统治者限 1 次）</td><td>25 政治 + 系数 6 金币；<strong>五项共享 5 年冷却</strong></td><td>立即获得 <strong>+15 正统性</strong>；教士当前满意度 −7.5 个百分点</td></tr>
    <tr><td><strong>请求贵族使节</strong></td><td>贵族阶层</td><td>30 政治 + 系数 2 金币；共享 5 年冷却</td><td>立即获得 <strong>+5 外交官</strong>；贵族当前满意度 −10 个百分点</td></tr>
    <tr><td><strong>请求紧急拨款</strong></td><td>市民阶层（金库 ≥10 金币）</td><td>40 政治影响力；共享 5 年冷却</td><td>从市民金库划拨 <code>min(6×单笔贷款额, 市民金库×50%)</code> 入国库；市民满意度 −15%</td></tr>
    <tr><td><strong>向平民求助</strong></td><td>平民或齐米阶层</td><td>40 政治影响力；共享 5 年冷却</td><td>获得 <code>10 × (1 + 0.005 × 农奴自由轴)</code> 点<strong>稳定度</strong>（范围 5–15 点）；满意度 −15%</td></tr>
    <tr><td><strong>号召部落武装</strong></td><td>部落或哥萨克（全国月人力 &gt;0）</td><td>15 政治 + 系数 6 金币；共享 5 年冷却</td><td>立即获得相当于 <strong>12 个月全国人力收入</strong> 的人力；满意度 −20%</td></tr>
  </tbody>
</table>
"""
            },
            {
                "id": "parliament",
                "title": "04 · 阶层特权授予/撤销算式与议会 180 天表决机制",
                "en": "Privilege Grant/Revoke Math & 180-Day Parliament Bargaining",
                "html": f"""
<div class="formula-box">
<strong>1. 阶层特权（{T('estate_privilege','Estate Privileges')}，共 331 项）的授予与撤销代价公式：</strong><br>
设某项特权为该阶层提供的长期满意度均衡点加成为 <code>Δ</code>：<br>
• <strong>授予特权</strong>（基础费 20 政治影响力）：本阶层当前满意度立即 <code>+3Δ</code>，其余阶层当前满意度变化 <code>−1.5Δ</code>。<br>
• <strong>撤销特权的稳定度花费</strong> = <code>400 × 被撤阶层全国力量份额 × (1 − 王室全国份额 + 其他撤销成本修正)</code><br>
&nbsp;&nbsp;例：被撤阶层占全国力量 20%（基数 80 稳定度），王室占 30%，另通过议会《加强政府集权》获 −10% 折扣，则实付 <code>80 × (1 − 0.30 − 0.10) = 48</code> 稳定度。<br>
• <strong>撤销特权的当日满意度冲击</strong> = <code>−(25 + 3Δ)</code> 个百分点！<br>
&nbsp;&nbsp;<strong>保住征召资格的操作底线</strong>：因征召要求当前满意度 ≥25%，撤销前目标阶层当前满意度至少须达到 <code>50% + 3Δ</code>（如《贵族土地权》<code>Δ = 5%</code>，撤销前满意度至少需 <strong>65%</strong>，否则撤完跌破 25% 当即失去全部贵族征召兵）。
</div>

<p><strong>2. {T('parliament','议会（Parliament）')} 会期、议程交换与支持度请求</strong>：</p>
<ul>
  <li><strong>周期与起始支持度</strong>：常规召集间隔须满 59 个整月，会期持续 <strong>180 天</strong>，期满支持度 ≥ <strong>50%</strong> 则本届 {T('parliament_issue','议案')} 通过（1.4.9 起若阶层保存的候选诉求全部失效，会在月结自动刷新生成新议题）。开会起始支持度 = <code>王室力量份额 × 0.5 + 提案的非王室阶层力量份额</code>。</li>
  <li><strong>用议程（Agendas）与政治压力换取支持度</strong>：会期内接受某阶层议程（如调整税负、外交态度或修筑设施）立即兑现其条件并按该阶层力量、议程重要度（0.75–3.0）及满意度增加支持度（同一会期重复接受同一阶层议程每次递减 −25%）；也可花费 40 政治影响力执行「<strong>施加政治压力</strong>」直接 +25 个百分点支持度（出席四阶层各扣 −10% 满意度）。</li>
  <li><strong>消耗支持度的即时请求（基础消耗 50 个百分点支持度）</strong>：可在会期内将支持度兑现为<strong>批准省份宣称 CB</strong>（有效 10 年，割地战分 ×1.25）、<strong>请求更改法律</strong>（换政策稳定度打 2 折）、<strong>临时加税</strong>（1 年全阶层税率上限 +25%）或<strong>扩大征召</strong>（3 年征召规模 +25%）。注意：兑现请求会扣减当前议案支持度，若仍想通过本届议案（如《加强政府集权》拿 10 年撤特权 −10% 折扣与 +20% 王室力量），须预留或补足剩余 50% 支持度。</li>
</ul>
"""
            },
            {
                "id": "rebellions",
                "title": "05 · 叛乱进度、5,000 人规模门槛与要塞守军留忠公式",
                "en": "Rebel Progress, 5,000-Supporter Threshold & Rebel Fort Loyalty Formula",
                "html": f"""
<p>当人群满意度跌破加入阈值（基础 <strong>20%</strong>，退出阈值基础 <strong>35%</strong>；正稳定度每 +10 点使加入线降 1%、退出线降 0.5%，下限分别为 5% 与 10%），不满人口会按文化、宗教、奴隶身份或阶层诉求汇入对应的 <strong>{T('rebel_movement','叛乱派系')}</strong>，受低控制力缺口 <code>(1 − 控制力)</code>、未整合状态、支持人口占比、阶层力量及外国间谍资助共同推高月度进度（派遣 MIL 大臣执行「镇压叛乱」基础每月压低 −0.25 个百分点）。</p>

<div class="formula-box">
<strong>起事规模分流与「要塞守军留忠概率」精确公式（<code>00_defines.txt</code>）：</strong><br>
1. <strong>支持人数门槛（5,000 人）</strong>：当派系进度达到 100% 时，若全国支持者少于 <strong>5,000 人</strong>，仅触发地方性「小规模动乱」修正而不会建军起义；支持者 ≥ 5,000 人则爆发公开起义或 {T('civil_war','内战')}。<br>
2. <strong>起事瞬间每座要塞守军的留忠检定概率（限制在 10%–90% 之间）</strong>：<br>
<code>要塞留忠概率(%) = clamp(50 + 30 × 守军阶层满意度(0–1) − 15 × [守军与叛军同阶层] + 10 × [本地动乱 &lt; 3] + 10 × [同主流文化] + 10 × [同国教] − 20 × [叛军进度 &gt; 80%], 10, 90)</code><br>
<em>实算示例：守军阶层满意度 60%（+18）、同阶层叛乱（−15）、本地动乱低于 3（+10）、主流文化（+10）、国教（+10）、但叛军进度已过 80%（−20）→ 留忠率为 <code>50 + 18 − 15 + 10 + 10 + 10 − 20 = 63%</code>（仍有 37% 概率开城倒戈！）。</em>
</div>
<p><strong>起事前三项干预窗口</strong>：① <strong>挑起叛乱（Provoke Rebels）</strong>：进度在 <strong>70%–100%</strong> 之间时可主动增加 30% 进度提前引爆——若在进度尚未越过 <strong>80%</strong>（避免触发要塞 −20% 留忠惩罚）时预先将主力驻扎在目标险要地形主动引爆，可大幅降低要塞失守风险；② <strong>买通叛军（Buy Off）</strong>：进度 &gt;80% 时按 <code>1 + 20 × (支持人口 ÷ 全国人口)</code>（1–4 倍）付费直接削减 40 个百分点进度；③ <strong>接受诉求</strong>：按 72 类叛军诉求执行对应改制或自治代价。</p>
"""
            },
        ],
        "discussion": {
            "title": "制度博弈 · 开局收回贵族高权势特权的标准步骤",
            "html": """
<ul>
  <li><strong>以 1337 年莫斯科为例（王室 22%、博雅尔贵族 49%，当前满意度 85.10%）</strong>：若鲁莽连续撤销《进攻型军事学说》（扣 32.5% 满意）与《贵族土地权》（扣 40% 满意），贵族满意度将直接跌至 12.60%，不仅丧失全部贵族征召兵，还会使贵族要塞留忠率暴跌。</li>
  <li><strong>低成本顺序</strong>：① 先将内阁与军中可替换的贵族职位换为王室宗亲、推动《首都专政》改革（撤特权成本 −20%）或通过议会《加强政府集权》议案（10 年内撤特权成本 −10%、王室力量 +20%），压低贵族份额并放大王室折扣；② 优先撤销加权势最高但当前不急需的《贵族土地权》（+75% 贵族力量），撤后满意度 45.10% 仍高于 25% 征召线，且贵族份额下降立即抬升贵族可征税率上限；③ 派 DIP 大臣安抚恢复至 ≥57.5% 后，再择机处理下一项特权。</li>
</ul>
"""
        },
        "quick_links": [
            ("王室力量与满意度 826 项来源反查", "metrics.html#crown_estate_power"),
            ("331 项阶层特权完整数值表", "ledgers.html#estate_privileges"),
            ("12 项阶层直接互动与求助表", "ledgers.html#estate_actions"),
            ("要塞留忠与撤特权计算器", "lab.html#calc"),
        ],
    },
]
