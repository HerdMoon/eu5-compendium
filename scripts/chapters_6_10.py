# -*- coding: utf-8 -*-
"""
Chapters 06 - 10 for EU5 Mechanics Compendium (1.4.9) — Overhauled Edition.
Covers Culture/Languages/Art/Religion/Orders, Ages/Institutions/Research/Exploration/Colonies/Situations,
Military Forces/Combat/Sieges/Logistics, Navy/Maritime/Warscore/Peace, and Diplomacy/Subjects/PU/IOs.
"""


def T(cid, label):
    return f'<button type="button" class="term" data-concept="{cid}">{label}</button>'


def M(mid, label="查全部游戏修正来源 →"):
    return f'<a class="metric-jump" href="metrics.html#{mid}">{label}</a>'


CHAPTERS_6_10 = [
    # =========================================================================
    # CHAPTER 06
    # =========================================================================
    {
        "id": "ch06",
        "slug": "ch06-culture-religion.html",
        "num": "06",
        "pillar": "culture",
        "title": "文化待遇与容量、四种语言、艺术骑士团与宗教体系",
        "en": "Culture & Capacity, Four Languages, Art & Chivalry, Religion & Orders",
        "subtitle": "详解五级文化待遇与文化容量的精确算法、控制力加权的宗教与文化统一度、四种语言及语言力量对科研与商业的作用、22 类艺术品倍率，以及各宗教专属机制与跨国修会。",
        "upstream": [
            ("地点控制力与人口分布", "ch01-territory-core.html#control", "统一度按 max(控制力, 5%) 加权人口；同化与改宗速度均受本地控制力缩放"),
            ("威望、资助预算与国家等级", "ch04-government-cabinet.html#government-power", "王国/帝国开放艺术家名额，威望与作品持续累积文化影响力与传统"),
            ("DIP/MIL 内阁行动与教士阶层", "ch04-government-cabinet.html#cabinet-actions", "内阁推进同化、统合文化组与省份改宗，教士阶层放大传教与科研"),
        ],
        "engine": "在文化容量上限内权衡接纳异文化与同化人口，配置通用/宫廷/礼仪/市场四种语言，创作艺术品提升文化攻防，并通过宗教宽容、信条学派与修会管理全国信仰。",
        "downstream": [
            ("已整合省份晋升核心（Core）", "ch01-territory-core.html#integration-core", "主流文化与已接纳文化合计 ≥50% 时自动转为核心（相容文化不计）"),
            ("每月研究进度与思潮增长", "ch07-ages-colonial.html#research-advances", "礼仪语言力量最高提供 +0.20 基础月研究进度；宫廷与礼仪语一致加思潮增长"),
            ("人群满意度与阶层力量修正", "ch05-estates-rebels.html#power-balance", "文化待遇与宗教宽容按每点 5 个百分点改变人口满意度，并修正阶层权势"),
        ],
        "redlines": [
            ("3 点 / 1 点基数", "文化容量基础占用", "已接纳文化基础占 3 点容量，相容占 1 点；每超额 1 点扣内阁效率 −10%、传统与影响各 −25%"),
            ("max(0.01, 1−接入度)", "市民市场语同化阻力", "使用本市场语言的市民向异语言文化同化时乘该系数（90% 接入度仅剩 10% 速度）"),
            ("存量 × 0.95 + 新增", "文化传统与影响力月结", "两者每月自然衰减 5%，长期均衡值 = 每月固定新增点数 × 20"),
            ("每点宽容 = 5% 满意", "宗教宽容转满意度系数", "异端与异教人口另带 −5% 基础项，再叠加宗教间观感（每档 ±5%）"),
        ],
        "sections": [
            {
                "id": "culture-status",
                "title": "01 · 五级文化待遇与「文化容量」完整计算公式",
                "en": "Five Cultural Statuses & Exact Cultural Capacity Formula",
                "html": f"""
<p>国家对境内每种 {T('culture','文化')} 赋予五级待遇之一。提升待遇须满足人口门槛并支付一次性政治影响力：设为<strong>相容（Tolerated）</strong>需占全国人口 ≥1%（或达 100 万人、或为某阶层主导文化），耗 <strong>15 政治影响力</strong>；由相容升为<strong>已接纳（Accepted）</strong>需占全国人口 ≥2.5%（或达 100 万人、或为某阶层主导文化），耗 <strong>25 政治影响力</strong>。</p>

<table class="data-table">
  <thead><tr><th>文化待遇等级</th><th>人口满意度</th><th>识字率上限</th><th>上层晋升 / 征召 / 人物生成</th><th>是否计入 50% 核心门槛</th><th>作为阶层主导文化时的阶层修正</th></tr></thead>
  <tbody>
    <tr><td><strong>1. {T('primary_culture','主流文化')}</strong></td><td class="num pos">+25%</td><td>0</td><td>全面开放</td><td class="pos"><strong>计入</strong></td><td>基准（无扣减）</td></tr>
    <tr><td><strong>2. {T('accepted_culture','已接纳文化')}</strong></td><td class="num pos">+10%</td><td>0</td><td>全面开放</td><td class="pos"><strong>计入</strong></td><td>阶层满意 −5%、力量 −5%</td></tr>
    <tr><td><strong>3. {T('tolerated_culture','相容文化')}</strong></td><td class="num pos">+5%</td><td>0</td><td>允许晋升与征召</td><td class="neg"><strong>不计入</strong></td><td>阶层满意 −10%、力量 −10%</td></tr>
    <tr><td><strong>4. {T('non_accepted_culture','受忽视文化')}</strong></td><td class="num">0%</td><td class="num neg">−5%</td><td>禁止晋升上层与常规征召</td><td>不计入</td><td>阶层满意 −15%、力量 −15%</td></tr>
    <tr><td><strong>5. {T('discriminated_culture','受歧视文化')}</strong></td><td class="num neg">−25%</td><td class="num neg">−15%</td><td>政治力量为 0，禁出将领阁臣</td><td>不计入（高同化速率）</td><td>阶层满意 −20%、力量 −20%</td></tr>
  </tbody>
</table>

<div class="formula-box">
<strong>文化容量（{T('cultural_capacity','Cultural Capacity')}）基准值与计算公式</strong> {M('cultural_capacity')}<br>
<span class="base-inline">基准值</span>国家基础文化容量为 <strong>0 点</strong>（<code>country_base_values</code>），由国家等级提供主干：伯国 <strong>0</strong> → 公国 <strong>+0.5</strong> → 王国 <strong>+1.0</strong> → 帝国 <strong>+2.0</strong>；单项文化基础占用基准：<strong>相容文化 1.0 点、已接纳文化 3.0 点</strong>。<br>
<code>单项文化实际占用 = max(待遇最低占用, 基础占用[接纳 3 / 相容 1] × (1 + 观感项 + 语言项 + 共享文化组项 + 国内相对人口项 + 全球相对人口项))</code>
<ul>
  <li><strong>降低单项占用变化</strong>：双向文化观感正观感乘 −0.25（亲缘 +3 折价 <strong>−75%</strong>），负观感乘 −0.50（敌对 −3 加价 <strong>+150%</strong>）；同语言 <strong>−15%</strong> / 同语族 <strong>−5%</strong>；共享文化组最多 <strong>−30%</strong>；国内与全球相对人口各限 −35% 至 +35%。</li>
  <li><strong>提高国家容量上限与超容惩罚</strong>：人文主义价值观、多元政府改革与文化革新扩充上限；全国已用容量每超出上限 <strong>1.0 点</strong>，施加 <strong>全国内阁效率 −10%、文化影响力 −25%、文化传统 −25%</strong>。</li>
</ul>
</div>
"""
            },
            {
                "id": "assimilation-merge",
                "title": "02 · 文化影响力 vs 文化传统、人口同化与统合文化组",
                "en": "Cultural Influence vs Tradition, Assimilation & Unifying Culture Groups",
                "html": f"""
<div class="formula-box">
<strong>① {T('cultural_influence','文化影响力')}（进攻端） vs {T('cultural_tradition','文化传统')}（防御端）</strong> {M('cultural_influence', '查文化影响力 →')} · {M('cultural_tradition', '查文化传统 →')}<br>
<span class="base-inline">基准值</span>两项指标在无月度新增时均衡基准均为 <strong>0 点</strong>，且每月均按当前存量的 <strong>5%</strong> 自然衰减（<code>下月值 = 当前值 × 0.95 + 当月新增 G</code>，长期均衡值 = <strong><code>20 × G</code></strong>；艺术品基础标量均为 5.0）。
<ul>
  <li><strong>文化影响力（决定同化他族速度、文化外交与文化霸权）</strong>：由高国家威望（满 100 贡献 +1.00/月）、宫廷语与通用语一致(+10%)、高影响力倍率艺术品（交响曲 2.5×、小说 2.0×）与剧院/宫廷建筑拉升。</li>
  <li><strong>文化传统（决定本文化抵抗异族同化的防御力）</strong>：由高传统倍率艺术品（名胜建筑 2.5×、圣物 2.0×、编年史 1.8×、圣像 1.2×）、文化霸权(+25%)与古迹建筑拉升。两者在文化超容时每超 1 点均扣 −25%。</li>
</ul>
</div>

<div class="formula-box">
<strong>② 人口文化同化速度（Pop Assimilation Speed）</strong> {M('pop_assimilation')}<br>
<span class="base-inline">基准值</span>国家基础人口同化速度平值为 <strong>+1 人 / 月</strong>（<code>country_base_values</code>），全国与本地同化百分比修正初始基准均为 <strong>0%</strong>。
<ul>
  <li><strong>正向提速变化</strong>：派遣 DIP 大臣执行「推广文化 / 同化地区」提供核心转化平值，乘当地<strong>当前控制力</strong>缩放；本国文化影响力高于目标文化传统、双方同语言/同文化组、本国文化已是当地优势文化(+50%)或目标为受歧视文化(+50%)时显著加速。</li>
  <li><strong>负向减速与统合文化组</strong>：未整合(−2%)/刚整合(−1%)/已接纳文化同化极慢；将使用本市场语言的 {T('burghers','市民')} 同化为异语言文化时强制乘 <code>max(0.01, 1 − 市场接入度)</code>。文化组主导大国可派 ADM 大臣执行基础 <strong>10 年</strong> 的「<strong>{T('merged_culture_group','统合文化组')}</strong>」（每文化组限一次），完成后将组内主流与已接纳文化合并并释放文化容量。</li>
</ul>
</div>
"""
            },
            {
                "id": "languages-art",
                "title": "03 · 四种国家语言、语言力量、22 类艺术品与勋贵骑士团",
                "en": "Four Languages, Language Power, 22 Art Work Types & Chivalric Orders",
                "html": f"""
<p>每个国家同时在四个职能槽位上使用语言（主动更改宫廷语言或礼仪语言各耗 <strong>20 稳定度</strong>，冷却 10 年）：</p>
<table class="data-table">
  <thead><tr><th>语言槽位</th><th>决定方式与可选范围</th><th>核心机制作用与阶层偏好</th></tr></thead>
  <tbody>
    <tr><td><strong>通用语言（Common）</strong></td><td>由国家主流文化母语自动决定</td><td><strong>平民阶层</strong>偏好宫廷语言与通用语言一致；两者一致时提供 <strong>+10% 文化影响力</strong>；国内实际讲该语言的人口占比还影响稳定度投资效率</td></tr>
    <tr><td><strong>{T('court_language','宫廷语言')}（Court）</strong></td><td>可从通用语、礼仪语、首都市场语、已接纳文化语、统治者/宗主/组织领袖语等 9 类来源中选定</td><td><strong>贵族阶层</strong>偏好高力量宫廷语言（世界相对力量 ≥50% 时给贵族满意度均衡奖励）；与礼仪语言一致时提供 <strong>+5% 思潮增长</strong>；与首都市场语言一致时提高<strong>商品出售效率</strong></td></tr>
    <tr><td><strong>{T('liturgical_language','礼仪语言')}（Liturgical）</strong></td><td>天主教（拉丁语）、犹太教（希伯来语）等由宗教锁定；部分宗教允许切换</td><td><strong>教士阶层</strong>偏好宫廷语与礼仪语一致；<strong>礼仪语言的全球「{T('language_power','语言力量')}」（该语综合实力 ÷ 世界第一语言实力）最高直接提供 +0.20 月研究进度</strong>（如相对实力 60% 即每月 +0.12 研究进度！）</td></tr>
    <tr><td><strong>{T('market_language','市场语言')}（Market）</strong></td><td>由该市场中心多数市民使用的语言决定</td><td>与本国通用语或地点优势语言相同时，各为该市场增加 <strong>+5 点市场吸引力</strong>（同语系 +1 点）</td></tr>
  </tbody>
</table>

<p><strong>{T('artist','艺术家')}、22 类 {T('work_of_art','艺术品')} 与 17 个 {T('chivalric_order','勋贵骑士团')}</strong>：</p>
<ul>
  <li><strong>雇佣与委托创作</strong>：王国提供 1 个艺术家名额、帝国 2 个（教育法律与革新可再增）。雇佣花费 <strong>10 威望</strong>；委托创作（Commission Art）基础金币为 <strong><code>6 × 经济基础</code></strong>。在职作家常驻提供全国月识字率 +0.05、思潮增长 +5%；科学家提供<strong>研究速度 +5%</strong>。</li>
  <li><strong>艺术品倍率与战时俘获</strong>：全游戏 22 类作品按品质乘以各自的「<strong>文化传统倍率 / 文化影响力倍率</strong>」持续贡献点数——例如画作（1.0 / 1.0）、小说（0.5 / 2.0）、交响曲（0.3 / 2.5，限专制/革命时代）、编年史（1.8 / 0.6）、圣像（1.2 / 0.4，另给当地动乱 −0.2、RGO 上限 +10%）、名胜纪念建筑（2.5 / 1.0，绑定原地不可俘获）、圣物（2.0 / 1.0）。地点被攻占时，可移动作品有 <strong>10% 概率损毁、40% 概率被胜方俘获运走</strong>。</li>
  <li><strong>勋贵骑士团</strong>：区分「成员个人加成」（如圣乔治骑士团给成员 MIL +15、月威望 +0.05、外交声誉 +1）与「国家全局修正」（如贵族征召规模 +10%）。<strong>只有当本国现任统治者本人是活跃骑士团成员时，国家修正才会生效</strong>（新君继位后记得到角色菜单检查入团）。</li>
</ul>
"""
            },
            {
                "id": "religion-system",
                "title": "04 · 宗教统一度、容忍度、人口改宗与各大宗教核心机制",
                "en": "Religious Unity, Tolerance, Conversion & Major Faith Mechanics",
                "html": f"""
<div class="formula-box">
<strong>① 控制力加权的「宗教统一度」与「文化统一度」（1.4.8–1.4.9 口径）：</strong><br>
<span class="base-inline">基准值</span>取值范围 <strong>0%–100%</strong>，低控制地点最低统计权重保底为 <strong>5%</strong>（<code>POP_STATISTICS_MIN_CONTROL_WEIGHT = 0.05</code>）；满 100% 宗教统一度提供教士满意度均衡 +10 个百分点。<br>
<code>单组人口统计权重 = 人数 × max(所在地当前控制力, 5%)</code> ｜ <code>宗教统一度 = 国教人口权重之和 ÷ 全国人口权重之和</code>
</div>

<div class="formula-box">
<strong>② 正统、异端与异教容忍度（Religious Tolerance）</strong> {M('religious_tolerance')}<br>
<span class="base-inline">基准值</span>国家三项基础容忍度（<code>country_base_values</code>）：<strong>正统信仰容忍 +1.0、异端容忍（同宗教组） −2.5、异教容忍（异宗教组） −5.0</strong>；异端与异教人口另带 <strong>−5%</strong> 基础满意度偏移。<br>
• <strong>变化与效果</strong>：每 <strong>1.0 点</strong>对应容忍度改变该信仰人群满意度 <strong>±5 个百分点</strong>（再叠加宗教间观感每档 ±5%）。偏向「属灵」提升正统容忍；偏向「人文」、提高齐米满意度(×2 异教容忍)与颁布宽容法典提升异端/异教容忍。
</div>

<div class="formula-box">
<strong>③ 人口宗教改宗速度（Pop Conversion Speed）</strong> {M('pop_conversion')}<br>
<span class="base-inline">基准值</span>国家基础人口改宗速度平值为 <strong>+2 人 / 月</strong>（<code>country_base_values</code>），全国与本地改宗百分比修正基准均为 <strong>0%</strong>；最大宗教影响力基准 <strong>100</strong>（天主教为 900）；国家主动更改国教基础花费 50 稳定度（冷却 25 年）。<br>
• <strong>变化来源</strong>：正向由 MIL 内阁「改宗省份」、本地当前控制力、教士高权势（超 25% 部分按 ×200% 加成）、属灵/隐义主义价值观、宗教建筑与传教信条放大；未整合征服地(−2%)、齐米自治特权及犹太教等高抗性信仰则减速或锁定传教。
</div>

<p><strong>3. 各宗教传统专属资源与行动要点（293 种宗教详见速查表）</strong>：</p>
<ul>
  <li><strong>基督教系</strong>：<strong>天主教</strong>围绕教廷（{T('curia','Curia')}）、枢机、教宗诏书与 2% 什一税运转（宗教影响力上限 900；遭{T('excommunication','绝罚')}承受正统/威望衰减与外交孤立）；<strong>东正教</strong>设自主牧首区、圣议会、圣像与<strong>{T('pentarchy','五大牧首区')}</strong>（集齐五座圣城加成翻倍）；<strong>新教各派</strong>开放多达 3 个信条槽（新增基督信条耗 50 宗教影响力）及 20 宗教影响力行动——「<strong>解散修道院</strong>」（最多 5 地各拆 1 级修道院，每处获 0.5 倍月税贸收入）、「<strong>驱逐异端</strong>」（向殖民特许建立 60 个月异端农民迁移）与「<strong>君主离婚</strong>」。</li>
  <li><strong>伊斯兰、印度、东亚与美洲信仰</strong>：伊斯兰教结合「隐义 ↔ 教法」轴与哈乃斐等教法学派（如哈乃斐给教士识字上限 +10）；佛教与耆那教使用<strong>业力（Karma，±33 为中性区间）</strong>与跨国宗派组织（加入耗 20 稳定度）；印度教选用<strong>化身（Avatars）</strong>；三教并用仁义与调和；神道教管理<strong>{T('purity','清净度')}与荣誉</strong>；安第斯印蒂启用亚南廷；中美洲纳瓦信仰管理<strong>{T('doom','末日值')}</strong>（随拥有地点上升，靠战斗杀敌与劫掠高发展地点压低）。</li>
</ul>
"""
            },
            {
                "id": "religious-orders",
                "title": "05 · 跨国宗教修会：据点地位、热忱衰减与圣召正负反转",
                "en": "Religious Orders: Holdings, Zeal & Calling Polarity",
                "html": f"""
<p>军事修会与托钵修会可在多国领土上设立修道院或分会等 <strong>{T('holding','修会据点（Holdings）')}</strong>，按据点数量占驻在国体量的比例形成修会在该国的「<strong>地位（Standing）</strong>」（部分军事修会还可动员修会征召兵）：</p>
<ul>
  <li><strong>{T('zeal','热忱（Zeal）')} 存续机制</strong>：长期和平会使修会热忱逐月消退（耗尽即面临解散），参与宗教战争或戍守异教前线可恢复热忱。</li>
  <li><strong>{T('calling','圣召（Calling）')} 的忠诚度双刃剑</strong>：每个修会奉行祈祷、学术、医疗或征战等圣召，持续推动驻在国社会价值观并提供领袖能力与全国修正。当修会对本国保持<strong>忠诚</strong>时，其圣召按修会地位提供正面国家加成；一旦关系恶化转为<strong>不忠</strong>，同一套圣召将反转为全国负面惩罚，须及时改善关系或清理据点。</li>
</ul>
"""
            },
        ],
        "discussion": {
            "title": "策略权衡 · 新征服异族富庶省，先「接纳文化」还是慢速「同化」？",
            "html": """
<ul>
  <li><strong>算清时间账与容量账</strong>：若新整合的富庶省份占全国人口已达 ≥2.5% 且本国尚有空闲文化容量，花费 25 政治影响力将其逐步提为「<strong>已接纳文化</strong>」可在<strong>当天立即满足 ≥50% 核心条件</strong>，直接拿到核心 +20%（净增 +15%）最大控制力、+10% 人口满意度、全额上层岗位晋升与殖民移民源资格；而若依靠早期有限的内阁席位从零同化异语言人口，往往耗时二三十年。待中后期统合文化组或同化效率大幅提高后，再视容量余量决定是否调整。</li>
</ul>
"""
        },
        "quick_links": [
            ("文化容量 / 影响力 / 传统 / 同化独立反查", "metrics.html#cultural_capacity"),
            ("三类宗教容忍与改宗速度独立反查", "metrics.html#religious_tolerance"),
            ("293 种宗教完整数据表", "ledgers.html#religions"),
            ("2,087 文化 / 528 语言 / 艺术品名录", "directory.html#cultures"),
        ],
    },

    # =========================================================================
    # CHAPTER 07
    # =========================================================================
    {
        "id": "ch07",
        "slug": "ch07-ages-colonial.html",
        "num": "07",
        "pillar": "culture",
        "title": "时代焦点、思潮传播、研究速度、探险殖民与局势灾难",
        "en": "Ages, Institutions, Research Speed, Exploration, Colonization, Situations & Disasters",
        "subtitle": "完整列出六大时代参数与时代焦点锁定规则、思潮贸易传播半衰公式与 20% 接纳门槛、每月研究进度的全部来源、特许殖民地货篮与定居算式，以及 24 项局势与 38 项灾难的触发逻辑。",
        "upstream": [
            ("礼仪语言力量、识字率与教士满意度", "ch06-culture-religion.html#languages-art", "共同构成每月研究进度的核心乘区"),
            ("核心地点人口池与力量投射", "ch01-territory-core.html#core-power", "仅核心地点可输出殖民移民；力量投射决定立项门槛与定居目标人数"),
            ("跨市场贸易吞吐与国家预算", "ch03-economy-market-trade.html#trade-orders", "商路引入外部思潮；预算承担探索、殖民货篮与接纳思潮支出"),
        ],
        "engine": "随六大时代选定专精焦点，通过贸易与内阁推动 18 项思潮跨过 20% 人口暴露线，投入月度研究点解锁 3,592 项革新，向未知海域派遣探险队与特许殖民地，并应对跨国局势与国内灾难检定。",
        "downstream": [
            ("新式军舰、火炮、工场与道路", "ch08-military-combat.html#force-types", "时代革新逐步解锁高代差兵种、高上限工场、城镇特权与地区级内阁行动"),
            ("海外直辖省与殖民领附属国", "ch10-diplomacy-subjects.html#subjects-annex", "定居完成后按特许目标转为直辖领地或贡献 75% 列强分的殖民领"),
            ("政体更迭与地缘格局重组", "ch11-scenarios-missions-dlc.html#dlc-expansions", "宗教改革、百年战争、英国内战等局势灾难永久改写制度与版图"),
        ],
        "redlines": [
            ("≥ 20% 全国人口", "接纳思潮硬门槛", "思潮传播达 100% 的本国地点人口之和占全国总人口 ≥20% 方可付费接纳（每思潮 +6.6% 经济基础）"),
            ("25 × [1+0.15(A−1)]", "当代标准革新成本", "第 1 时代基准 25 点，每晚一时代 +15%；跨入新时代后补研旧时代节点基准降至 17"),
            ("50 人/月 · 限 3 张", "特许殖民基准与省上限", "满额殖民预算每张特许基础迁入 50 人/月（必须源自核心地点）；同一省份最多 3 张特许并存"),
            ("1 − (1 − p)ⁿ", "灾难与历史事件累积概率", "满足全部前置条件的合格月份按月概率 p 独立检定，消除任一前置条件即可立即阻断触发"),
        ],
        "sections": [
            {
                "id": "ages-institutions",
                "title": "01 · 六大时代全局参数、时代焦点与 18 项思潮传播",
                "en": "Six Ages Parameters, Age Focus & 18 Institutions Spread",
                "html": f"""
<p>1337–1836 年共划分为六个{T('age','时代')}：<strong>① 传统时代 → ② 文艺复兴 → ③ 地理大发现 → ④ 宗教改革 → ⑤ 专制主义 → ⑥ 革命时代</strong>。每次进入新时代会同步改变商品物价稳定性（由 10% 逐代降至 2%）、最高物价倍数（3× 升至 5×）、市民最大贸易范围（由 600 逐代升至 1,100）以及官僚维护乘数。</p>
<ul>
  <li><strong>时代焦点（Age Focus）不可逆规则</strong>：从文艺复兴时代起，每次换代时必须在<strong>行政（ADM）/ 外交（DIP）/ 军事（MIL）</strong>中三选一作为本时代焦点，解锁对应时代焦点分支革新；<strong>未选中的另外两个分支在本局永久锁定</strong>（下一时代改选其他方向，仅开放下一时代的对应分支，不会回头解锁上一时代的未选节点）。</li>
  <li><strong>{T('institution','思潮（Institutions）')} 传播三途径与 20% 接纳公式</strong> {M('institution_spread')}：
    <div class="formula-box">
      <span class="base-inline">基准值</span>无传播源地点基础月增长为 <strong>0</strong>（百分比修正仅放大已有基础传播源）；全国接纳思潮硬门槛基准为<strong>「已达 100% 传播地点人口 ÷ 全国总人口 ≥ 20%」</strong>；接纳花费修正基准为 <strong>0%</strong>。<br>
      <ul>
        <li><strong>邻格与近海自然漫溢</strong>：从已发源或已传播满的邻接地点、近海港口逐月辐射。</li>
        <li><strong>跨市场贸易输入</strong>：当本市场总吞吐量 ≥ 10 时，与已传播外部市场的进出口贸易可将思潮带入（贸易路径成本达 <strong>25</strong> 时来源贡献衰减一半；连通比例达 25% 获半幅基础值）。</li>
        <li><strong>放大传播倍率与减免接纳费</strong>：对「全核心地点」省份派 ADM 内阁执行「研究思潮」基础提供 <strong>+50% 思潮增长修正</strong>；宫廷语与礼仪语一致(+5%)、在职作家(+5%)、改革《思潮之路》(+10%)；「创新」价值观满端减免 <strong>−50% 接纳思潮花费</strong>。</li>
      </ul>
    </div>
  </li>
</ul>
"""
            },
            {
                "id": "research-advances",
                "title": "02 · 革新成本算式与「每月研究进度」完整影响因素",
                "en": "Advance Cost Formula & Complete Factors Affecting Monthly Research Speed",
                "html": f"""
<div class="formula-box">
<strong>① 人口识字率上限与月增长（{T('literacy','Literacy')}）</strong> {M('literacy')}<br>
<span class="base-inline">基准值</span>文化待遇对最大识字率的基础偏移：主流/已接纳/相容文化为 <strong>0%</strong>，受忽视文化 <strong>−5%</strong>，受歧视文化 <strong>−15%</strong>；全国与各阶级附加最大识字率修正及月增长修正初始基准均为 <strong>0%</strong>。
<ul>
  <li><strong>变化与跨系统作用</strong>：「创新」价值观满端(+10% 上限)、《文字系统》革新(+5%)、新教《虔敬主义》(+5%)、哈乃斐学派(教士 +10%)、教育政策与大学/图书馆/修道院建筑抬高上限，作家艺术家(+0.05/月)与纸书供应加快月增长。识字率除提供基础科研点外，还分别加成劳工生产效率(最高 +2.5%)、市民发展增长(×25%)与贵族控制力增速(最高 +1.0%/月)。</li>
</ul>
</div>

<div class="formula-box">
<strong>② 革新成本算式与「每月研究进度 / 研究速度」</strong> {M('research_speed')}<br>
<span class="base-inline">基准值</span>当代标准革新研究点成本基准 = <strong><code>25 × [1 + 0.15 × (时代序号 − 1)]</code></strong>（第 1 时代 25 点；跨入后续时代补研旧节点基数由 25 降至 <strong>17</strong>）；全国研究速度百分比修正初始基准为 <strong>0%</strong>。
<ul>
  <li><strong>月进度平值来源（<code>research_speed</code>）</strong>：礼仪语言的全球相对实力最高直接提供 <strong>+0.20 点/月</strong>（60% 实力即 +0.12/月），叠加全国国民识字率基础贡献（未选在研项目时自动存入{T('stored_research','储备研究力')}池）。</li>
  <li><strong>研究速度百分比变化（<code>research_speed_modifier</code>）</strong>：<strong>教士阶层当前满意度</strong>以 50% 为零点按 <strong>×0.5 系数</strong> 正负缩放（80% 满意给 +15%，30% 满意扣 −10%！）；在职<strong>科学家艺术家(+5%)</strong>、改革《思潮之路》(+5%)、「教法学」满端(+10%)及学术革新放大倍率；破产期间承受 −90% 惩罚。</li>
</ul>
</div>
"""
            },
            {
                "id": "exploration",
                "title": "03 · 未知之地探索与专项远征队（Expeditions）",
                "en": "Terra Incognita Exploration & Special Expeditions",
                "html": f"""
<p>揭示 <strong>{T('terra_incognita','未知之地')}</strong> 以「地区（Area）」为单位，目标须位于本国 {T('naval_range','海军范围')}（含盟友与取得驻港权的港口）之内：</p>
<ul>
  <li><strong>常规海陆探索成本与领队分工</strong>：陆地探索启动费为 <strong>100 金币 + 250 人力</strong>，海域探索为 <strong>100 金币 + 250 水手</strong>；基础准备期 <strong>270 天</strong>，出发后基础月维持费 <strong>10 金币</strong>。领队人物的 <strong>MIL（军事能力）</strong> 加快探索月进度，<strong>ADM（行政能力）</strong> 压低每月维持费；提高海军范围可降低远距离目标所需的总进度。</li>
  <li><strong>专项探险（Expeditions，共 8 类）</strong>：设有独立路线与途经点事件。例如「海图勘测」需和平、非乡村港口与对应革新，单次限派 1 支且冷却 5 年；「环球航行」依次经过 13 个指定海路途经点（单国成功完成后不可重复）；圣物搜寻、朝圣、大游历、大使团及西葡运宝船队（需海军将领领队，5 年冷却）等返程型探险即使在出发后发生迁都，返航时仍正常结算。</li>
</ul>
"""
            },
            {
                "id": "colonial-charters",
                "title": "04 · 特许殖民地：货篮成本、月迁入算式、定居门槛与征服者",
                "en": "Colonial Charters, Goods Basket, Migration Math & Conquistadors",
                "html": f"""
<p>海外拓殖通过向目标省份颁发 <strong>{T('colonial_charter','特许殖民地（Colonial Charter）')}</strong> 推进（同一省份最多容许 <strong>3 张</strong> 特许并存竞争；设立基础金币为 <code>min(250, 2 × 经济基础)</code>，要求本国 {T('power_projection','力量投射')} 达标且目标在 {T('colonial_range','殖民范围')} 内）：</p>

<div class="formula-box">
<strong>特许殖民地基准值与三项核心计算（1.4.7–1.4.9 口径）：</strong> {M('colonial_migration')}<br>
<span class="base-inline">基准值</span>国家基础殖民范围与海军范围均为 <strong>1,000</strong>（<code>country_base_values</code>）；启动特许最低力量投射基准为 <strong>25 点</strong>；满额殖民预算下单张特许状基础迁入基准为 <strong>50 人 / 月</strong>（单省最多 3 张特许并存；探索每月基础进度为 +0.05）。
<ol>
  <li><strong>每月维持用货篮</strong>：每张特许基础月耗 <strong>布匹 0.2 + 盐 0.2 + 药材 0.1 + 武器 0.05 + 工具 0.05</strong>，按所属市场当前单价折算金币，再乘距离、当地土著人口与地理折扣（与既有据点同地区 <strong>−50%</strong>、同区域 <strong>−33%</strong>）及殖民维护效率。</li>
  <li><strong>单张特许每月移民人数</strong> = <code>50 人/月（满额殖民预算基准） × (1 + 全国殖民迁移百分比修正之和)</code> + 内阁定向移民分项。<br>
    <em>例：满预算下叠加《殖民特许状》革新(+25%)与《哥萨克拓殖权》(+10%)，单张月送达 <code>50 × 1.35 = 67.5</code> 人。<strong>硬性规则</strong>：迁出人口只能来自本国<strong>核心（Core）</strong>地点，来源地农民耗尽时自动重选其他核心地点。</em></li>
  <li><strong>{T('fully_settled','完全定居（Fully Settled）')} 人口门槛</strong>：按地点逐一完成，最低 <strong>1,000 人</strong>、最高参数 <strong>15,000 人</strong>，须拥有足够比例信奉本国<strong>国教</strong>且属<strong>主流或已接纳文化</strong>的居民（本国力量投射越高，所需合格人口目标越低，例如在 20,000 人土著地每多 1 点投射约减 8 人目标；「安置边疆」内阁行动完成定居时同步升级当地 RGO）。</li>
</ol>
</div>

<p><strong>定居完成后的三种归属目标与「{T('conquistador','征服者')}」</strong>：</p>
<ul>
  <li><strong>殖民特许目标（3 选 1）</strong>：① <strong>保留为直属领地</strong>（默认陆连/近海）；② <strong>建立殖民附属国</strong>（海外省份建成新殖民领，当其月收入 &gt; 月支出 105% 时达成财政自给）；③ <strong>扩张现有附属国</strong>（并入同地区/相邻地区/同区域既有的本国殖民领）。</li>
  <li><strong>委派征服者</strong>：针对已发现的美洲目标地区（须可从首都所在地区/区域港口在海军范围内抵达），招募基础价 <strong>250 金币 + 4,000 人力</strong>，准备期 90 天；领队须具备探索资格、未婚、信奉天主教且非王室阶层（科尔特斯、皮萨罗等历史事件亦可直接生成征服者远征登陆）。</li>
</ul>
"""
            },
            {
                "id": "situations-disasters",
                "title": "05 · 24 项历史局势与 38 项国内灾难的触发与终局",
                "en": "24 Historical Situations & 38 National Disasters",
                "html": f"""
<p>动态历史事件（DHE）、跨国 <strong>{T('situation','历史局势')}</strong> 与单国 <strong>{T('disaster','国内灾难')}</strong> 均采用「<strong>先核对全部强制资格条件，再在合格月份按月概率 <code>p</code> 独立抽取</strong>」的两步机制：连续 <code>n</code> 个合格月内至少触发一次的概率为 <code>1 − (1 − p)ⁿ</code>（如月概率 2% 持续合格 12 个月，年内触发率约 <code>1 − 0.98¹² = 21.5%</code>；只要提前消除任一前置条件，当月触发率即降为 0）。</p>
<ul>
  <li><strong>跨国局势时序链（本体 22 项 + 扩展包 2 项）</strong>：早期涵盖日本南北朝、德里衰亡、归尔甫与吉伯林派、土耳其人崛起（最强贝伊拥有 ≥500 地点即达成规模终局）、海峡之战、<strong>百年战争</strong>（英方可通过法兰西区域 ≥161 地点归英系或宣称法兰西王位保持联统主导获胜）、<strong>黑死病</strong>（1346 起检定）与<strong>红巾军起义</strong>（&gt;1350 年）；中期串联西方教会大分裂、胡斯战争、意大利战争、托尔德西里亚斯条约、美洲大瘟疫，以及<strong>宗教改革（1510 起）→ 特利腾大公会议（1530 起，改革渴望 ≥25% 或处于 1545–1563 窗口）→ 宗教战争（1590 起，需会议已结束）</strong>三连环；晚期进入哥伦布大交换、海盗黄金时代、小冰期（1645–1715+）、殖民地独立革命与人民起义。</li>
  <li><strong>代表性国内灾难门槛拆解（全 38 项见速查表）</strong>：<br>
    • <strong>继承危机</strong>：一般君主国无继承人、摄政或继承人总能力 &lt;150 时，稳定度 &lt;10 且正统性 &lt;50 即进入合格月（普通分支为稳定 &lt;0 且正统 &lt;40）。<br>
    • <strong>英国内战</strong>：专制时代起，王室份额 &gt;40% 或专制—自由轴 &lt;+25 时每月 2% 检定（有克伦威尔标记升至 3%）；议会派胜则建共和国并解锁护国公改革，保王派胜则大幅转向专制。<br>
    • <strong>莫斯科继承战争</strong>：和平期有其他成年同王朝男性、正统性 &lt;75 且觊觎者叛乱进度 ≥25% 时每月 5% 检定。<br>
    • <strong>帝国衰落 &amp; 自由渴望</strong>：帝国衰落检查独立帝国负稳定度下本土大区平均控制力低于时代红线（45%/50%/55%/60%）或未容忍文化超 1/3；自由渴望在持续满 20 年或恢复议会/稳定达标后结束，从而为后续大革命灾难让出判定空间。</li>
</ul>
"""
            },
        ],
        "discussion": {
            "title": "科研与拓殖常见卡点 · 思潮迟迟达不到 20% 与殖民地人口倒退排查",
            "html": """
<ul>
  <li><strong>偏远大国如何快速接纳文艺复兴或印刷机等欧洲思潮？</strong>：① 先派商队与已普及该思潮的高吞吐市场建立稳定进出口路线（市场总吞吐 ≥10 开启贸易传播）；② 一旦首都所在核心大省出现微量传播进度，立即挂上高 ADM 大臣执行「<strong>研究思潮</strong>」（+50% 基础乘内阁倍率）并叠满宫廷—礼仪同语(+5%)、作家艺术家(+5%)与图书馆建筑；首都核心城市圈人口密集，填满一省往往就能直接跨过全国 20% 暴露线。</li>
  <li><strong>热带西非或美洲丛林殖民为何进度停滞？</strong>：疟疾等风土病每 10–15 天结算人口损耗，若仅靠单张特许状基础 50 人/月迁入而母省人口不足，净增可能趋近零。优先抢占无恶性地方病的海岛或温带良港作为第一级核心跳板，再集中多张特许或配合内阁定向移民推进。</li>
</ul>
"""
        },
        "quick_links": [
            ("识字率 / 思潮传播 / 研究速度独立反查", "metrics.html#research_speed"),
            ("24 项局势与 38 项灾难全表", "ledgers.html#situations_disasters"),
            ("3,592 项时代革新全名录", "directory.html#advances"),
            ("8 类探险与殖民目标名录", "directory.html#expedition_types"),
        ],
    },

    # =========================================================================
    # CHAPTER 08
    # =========================================================================
    {
        "id": "ch08",
        "slug": "ch08-military-combat.html",
        "num": "08",
        "pillar": "military",
        "title": "四大兵源、人力池、野战阵线与伤害算式、围城与后勤",
        "en": "Force Sources, Manpower, Combat Math, Sieges & Supply Lines",
        "subtitle": "对照征召兵人口账与常备军人力池公式，完整拆解训练度、军事战术、主动性、经验与陆军传统在按日/按小时战斗中的数学作用，以及围城 D14 检定表与三级前线粮道。",
        "upstream": [
            ("阶层满意度与受控军事建筑", "ch05-estates-rebels.html#power-balance", "满意度 ≥25% 开放征召；军械库至征兵中心按控制力产出月度人力"),
            ("武器、战马、火炮市价与预算", "ch03-economy-market-trade.html#production-buildings", "决定常备军招募与日常军饷物资成本（战马涨价显著推高骑兵维护）"),
            ("省份粮仓、要塞与沿海舰队", "ch02-population-food.html#food-chain", "支撑远征军取粮、补给站存粮与海岸分发补给"),
        ],
        "engine": "编组步、骑、炮与辅助兵团（保持单类 <50% 触发混编加成），在左/中/右三路宽度与预备队体系下结算接敌、兵力伤害与士气伤害，并通过围城阶段检定与粮道维护夺取敌方据点。",
        "downstream": [
            ("战俘收容、赎金与低价佣兵", "ch03-economy-market-trade.html#wealth-to-treasury", "10:1 或溃败后 2:1 触发覆灭俘获，可赎回或以 0.25× 维护费改编佣兵"),
            ("战争分数与厌战度累积", "ch09-navy-war-peace.html#warfare-peace", "野战最多提供 50 战分；攻陷关联要塞消除和约割地 −33% 效率惩罚"),
            ("原籍劳动力缺口与人口恢复期", "ch02-population-food.html#population-base", "征召兵战死直接扣减原籍人口，小规模矿镇可能需数十年自然恢复"),
        ],
        "redlines": [
            ("0.75 战力 / −20% 训", "陆军征召兵基础折算", "征召兵对正规军战力 0.75（承伤约 1.333×），不可补员，潜力恢复周期 240 个月"),
            ("月产量 × 60 个月", "人力与水手上限公式", "全国基础最大人力与水手储量均等于 5 年月度产量；建筑产出乘 max(10%, 控制力)"),
            ("60% + 2.5%×主动", "按日模式每拍接敌率", "主动性封顶 +30%，每战一日另 +3%；未接敌前排单位承伤 ×1.10（兵力）/ ×1.20（士气）"),
            ("≥ 守军人数 · 30天", "要塞围城推进硬门槛", "围城兵力低于守军时进度冻结；D14 总点 ≥20 或守军跌至 5% 投降，缺口最多 3 处"),
        ],
        "sections": [
            {
                "id": "force-types",
                "title": "01 · 四种兵源对比、人力/水手建筑产出与部队族系",
                "en": "Levies, Regulars, Mercenaries, Private Regiments & Manpower Math",
                "html": f"""
<table class="data-table">
  <thead><tr><th>兵源类型</th><th>征募条件与资源池</th><th>战斗属性与补员规则</th><th>人口与财政长期影响</th></tr></thead>
  <tbody>
    <tr>
      <td><strong>1. {T('army_levy','陆军征召兵')}</strong></td>
      <td>所属阶层当前满意度 <strong>≥ 25%</strong>；直接从各地点合格人口中调出</td>
      <td>基础征召作战效率 <strong>0.75</strong>（常备军打征召兵倒数约 <code>1.333×</code>），自带<strong>训练度 −20%、耗粮 −75%</strong>；服役期<strong>无法补员</strong></td>
      <td>解散时幸存者返乡，<strong>阵亡者直接从原籍人口永久扣除</strong>（在 10,000 人矿镇死 2,000 劳工按 0.25% 年增长需约 90 年自然恢复！）；再次征召潜力恢复期基础 <strong>240 个月</strong></td>
    </tr>
    <tr>
      <td><strong>2. {T('regular_regiment','常备正规军')}</strong></td>
      <td>消耗全国<strong>{T('manpower','人力池')}</strong>、金币与军需商品；受 <strong>{T('unit_family','部队族系')}</strong> 名额限制</td>
      <td>享 100% 满额属性，可在友方地点按月消耗人力补员；和平期驻止有将领时可「<strong>操练（Drill）</strong>」累积经验（最高减伤 50%）</td>
      <td>同族系跨时代升级沿用原名额，且升级成本系数仅为 <strong>0.10（10%）</strong>；实际常备规模还会与「阶层预期陆军规模」对比</td>
    </tr>
    <tr>
      <td><strong>3. {T('mercenary','雇佣兵')}</strong></td>
      <td>支付签约费与领袖费，默认合同 <strong>24 个月</strong>（最长 120 个月）</td>
      <td>常规佣兵月维护费倍率为 <strong>1.35×</strong>；兵员与补充来自雇佣兵池，不消耗本国人力池</td>
      <td>劳动力紧缺而国库充裕时，用佣兵承担攻城与血战可保护本国高价值 RGO 工人；本国空闲部队亦可挂牌出租赚取雇佣兵收入</td>
    </tr>
    <tr>
      <td><strong>4. {T('private_regiment','阶层私人团')}</strong></td>
      <td>授予贵族/哥萨克私军特权，且阶层存款 ≥ 招募后待命月维护费的 <strong>2 倍</strong></td>
      <td>耗 10 正统性与 15 政治影响力执行「征用私兵」（冷却 3 年）调入国家军队</td>
      <td>待命维护费超阶层存款 50% 时触发裁撤；若所属阶层发动叛乱，已借出的私人团立即召回倒戈</td>
    </tr>
  </tbody>
</table>

<div class="formula-box">
<strong>① 月度人力与最大人力池（Manpower）</strong> {M('manpower', '查人力来源 →')} · {M('levy_efficiency', '查征召兵修正 →')}<br>
<span class="base-inline">基准值</span>无军事兵源建筑时，国家基础月度常备人力为 <strong>0 人 / 月</strong>；全国最大人力储量上限基准固定为 <strong>60 个月（5 年）</strong>的月产量；每地点同时招募队列基准为 <strong>1</strong>。<br>
<code>全国月人力 = Σ[各地点陆军建筑满员产出 × (1 + 本地修正) × max(10%, 本地当前控制力)] × (1 + 全国人力百分比修正)</code><br>
• <strong>五级陆军建筑每级满员基础月产</strong>：军械库 / 训练场 <strong>+10 人/月</strong>（+600 上限） → 军营 <strong>+15</strong> → 军团营地 <strong>+20</strong> → 征兵中心 <strong>+25 人/月</strong>（中国早期「戍营」+2.5/月），再由数量价值观、征兵法律与军事革新放大。
</div>

<div class="formula-box">
<strong>② 月度水手与最大水手池（Sailors · 与人力相互独立）</strong> {M('sailors')}<br>
<span class="base-inline">基准值</span>无港口海事建筑时，国家基础月度水手为 <strong>0 人 / 月</strong>；全国最大水手储量上限基准同样为 <strong>60 个月（5 年）</strong>的月产量。<br>
• <strong>五级沿海港口建筑每级满员基础月产</strong>：码头 <strong>+16 水手/月</strong>（+960 上限） → 干船坞 <strong>+32</strong> → 船厂 <strong>+64</strong> → 大船厂 <strong>+125</strong> → 海军基地 <strong>+200 水手/月</strong>。<br>
• <strong>编组维护与混编基准</strong>：骑兵等精锐物资维护随战马/武器市价浮动；当全军<strong>没有任何单一兵种团数占比 ≥ 50%</strong> 时，每类占比 ≥10% 的兵种基准提供 <strong>+2.5% {T('combined_arms','兵种混编')}</strong> 加成。
</div>
"""
            },
            {
                "id": "battle-mechanics",
                "title": "02 · 四阵位宽度、接敌公式与训练度/战术/经验伤害算式",
                "en": "Frontage, Engagement Math & Discipline/Tactics/Experience Damage Formulas",
                "html": f"""
<p>战场划分为<strong>{T('flank','左翼')}、{T('center','中路')}、{T('flank','右翼')}</strong>三个前线区段与一个后方<strong>{T('reserves','预备队')}</strong>（可切换「平衡阵型」或把骑兵放两翼的「骑兵侧翼阵型」，辅助团优先留预备队）。每路最大可用 {T('frontage','战斗宽度')} 受地形与植被缩减（如山地 −4、疏林 −2，地形结算后每路保底宽度为 2；部署时每路最多容纳宽度的 125%，超宽单位等空位补入；击溃正对面敌军后按侧击能力跨路侧击）。</p>

<table class="data-table">
  <thead><tr><th>战斗时间步进规则</th><th>初始炮击 / 常规阶段</th><th>每步基础接敌率</th><th>主动性贡献（上限）</th><th>时间递增接敌</th><th>陆/海最短持续</th><th>总伤害倍率</th></tr></thead>
  <tbody>
    <tr><td><strong>按日（Daily，默认）</strong></td><td><strong>3 天</strong> / 每 <strong>4 天</strong> 重掷 D10</td><td><strong>60%</strong></td><td>每点 <strong>+2.5%</strong>（封顶 +30%）</td><td>每天 <strong>+3%</strong></td><td>5 天 / 5 天</td><td>0.12</td></tr>
    <tr><td><strong>按小时（Hourly，规则可选）</strong></td><td>5 步 / 每 5 步重掷 D10</td><td>10%</td><td>每点 +1.0%（封顶 +15%）</td><td>每步 +1%</td><td>24 步 / 72 步</td><td>0.01</td></tr>
  </tbody>
</table>

<div class="formula-box">
<strong>单次交火伤害组成总式：</strong><br>
<code>单日兵力伤害 ∝ 当日有效骰点项(D10换0~9 + 基数5 ± 将领/地形，封顶15) × 攻击方有效火力 × 基础刻度（陆兵0.04/陆士0.25；海船0.0625/海士0.05） × (1 + 攻方训练度) ÷ [(1 + 守方训练度) × 守方军事战术] × (1 − 0.5 × 守方经验比例) × 未接敌惩罚</code>
</div>

<table class="data-table">
  <thead><tr><th>独立野战数值</th><th>官方基准值与范围</th><th>结算作用与全部正负变化来源</th></tr></thead>
  <tbody>
    <tr>
      <td><strong>① {T('discipline','训练度')}</strong><br>Discipline<br>{M('discipline', '查训练度来源 →')}</td>
      <td>常备军初始修正基准 <strong>0%</strong>（乘除基数 <strong>1.00×</strong>）；陆军征召兵自带 <strong>−20%</strong></td>
      <td>同时放大本方输出并作为除数降低承伤。由将领 MIL(每点 +0.1%)、满游牧团结(+10%)、质量/进攻价值观、贵族与骑士团特权、军事改革与革新提升</td>
    </tr>
    <tr>
      <td><strong>② {T('military_tactics','军事战术')}</strong><br>Military Tactics<br>{M('military_tactics', '查战术来源 →')}</td>
      <td>国家基础军事战术基准 <strong>1.00</strong>（兵种混编单类 &lt;50% 时每类基准 <strong>+2.5%</strong>）</td>
      <td>直接做除数减免承伤（升至 2.00 时承伤减半！）；主要由各时代核心火器与阵型革新拉开代差。部队满 100% 经验另减 50% 承伤（月自然衰减基准 5%，正规军 −1%）</td>
    </tr>
    <tr>
      <td><strong>③ 陆海军士气</strong><br>Morale<br>{M('morale', '查士气来源 →')}</td>
      <td>传统时代陆军基准约 <strong>3.0</strong>（崩溃线 0.05）；月恢复基准 <strong>5%</strong>（友境另 +25%）</td>
      <td>君主每点 MIL +0.1%，将领每点 DIP +0.2%，满陆/海军传统各 +20%。无将领部队直接 <strong>−20%</strong>，每 1 点厌战度扣 <strong>−2.5% 陆海军士气</strong>，破产 60 个月内 −90%</td>
    </tr>
    <tr>
      <td><strong>④ 接战主动性与宽度</strong><br>Initiative &amp; Frontage<br>{M('initiative', '查主动性来源 →')}</td>
      <td>按日模式基础接敌率 <strong>60%</strong>（主动性加成基准 0%，封顶 +30%）；地点基础宽度 <strong>10</strong></td>
      <td>未接敌前排单位挨打额外承伤 <strong>×1.10（兵力）/ ×1.20（士气）</strong>；将领每点 DIP +1% 主动性，每点 MIL +0.5% 参战速度，每点 ADM +0.1% 宽度（山地宽度 −4、疏林 −2）</td>
    </tr>
  </tbody>
</table>
"""
            },
            {
                "id": "prisoners-overrun",
                "title": "03 · 10∶1 与 2∶1 压倒性溃灭及战俘（Prisoners）处置",
                "en": "Overrun Ratios & Post-Battle Prisoner Mechanics",
                "html": f"""
<ul>
  <li><strong>两类整军溃灭（Overrun）门槛</strong>：① 战斗首个结算步本方兵力达到敌军 <strong>10∶1</strong> 时直接溃灭敌军；② 敌军士气崩溃后，本方兵力达到敌军 <strong>2∶1</strong> 即触发追击溃灭。</li>
  <li><strong>{T('prisoner','战俘（Prisoners）')} 收容与转化</strong>：溃败被俘过程中有 40% 基础折损率；收容在押战俘占用常规维护费的 <strong>30%</strong>。此后有三种处理方式：① <strong>赎回（Ransom）</strong>换取金币（再次赎回冷却 60 天）；② <strong>招为战俘雇佣兵</strong>——月维护费仅需常规标准的 <strong>25%（0.25×）</strong>，但士气上限锁定为 <strong>0.60</strong>；③ 处决或遣散。</li>
</ul>
"""
            },
            {
                "id": "siege-forts",
                "title": "04 · 要塞控制区（ZoC）、围城 D14 阶段检定表与强攻核算",
                "en": "Fort Zone of Control, D14 Siege Table & Assault Calculation",
                "html": f"""
<p>{T('fortification','要塞')} 对周边邻接格投射 <strong>{T('zone_of_control','要塞控制区（ZoC）')}</strong>：敌军踏入邻接敌堡的地点后，必须先攻克该要塞才能继续穿行至同一要塞控制的其他敌方地点；而己方（含直属宗主与直属属国）受控要塞的 ZoC 则保护友军免受包括严冬在内的一般本地损耗（黑死病等不可避免损耗除外）。注意行军进度达 <strong>50%</strong> 时锁定移动去向。</p>

<div class="formula-box">
<strong>① 围城能力与炮兵围攻加值（攻方指标）</strong> {M('siege_ability')}<br>
<span class="base-inline">基准值</span>全国围城能力修正初始基准为 <strong>0%</strong>；无工事阶段基准 <strong>15 天</strong>，有要塞阶段基准 <strong>30 天</strong>（最短下限 7 天）；炮兵对要塞检定加值上限基准为 <strong>+5</strong>（最多 3 处缺口）。<br>
• 攻城将领每点 ADM +0.1% 围城能力，满陆军传统 +10% 围城能力；<strong>围城兵力必须 ≥ 当前守军人数</strong>否则进度冻结。<br>
• <code>阶段检定总点 = 原始骰点(1–14) + 累积围城进度 + 炮兵加值(基准上限 +5) + 城墙缺口数(×2) − 要塞等级 − 未封锁沿海港口罚点(−1)</code>
</div>

<div class="formula-box">
<strong>② 要塞防御、要塞上限与驻军规模（守方指标 · 与围城能力独立）</strong> {M('fort_defensive')}<br>
<span class="base-inline">基准值</span>全国与本地要塞防御（<code>global/local_defensive</code>）修正基准均为 <strong>0%</strong>；国家免超额要塞上限基准为 <strong>1 座</strong>（王国 +1、帝国 +2）；本地驻军补充速度基准为 <strong>+1% / 月</strong>。<br>
• <code>单阶段实际天数 = 30 × (1 + 守方要塞防御 − 攻方围城能力)</code>（每 +10% 要塞防御拖慢敌方每轮 3 天；每 1 点厌战度反扣 −2.5% 全国要塞防御）。
</div>

<table class="data-table">
  <thead><tr><th>检定点数或独立事件</th><th>阶段结果</th><th>守军损耗与后续围城进度变化</th></tr></thead>
  <tbody>
    <tr><td><strong>原始骰点掷出 1（或总点 &lt; 1）</strong></td><td><strong>围攻方疫病暴发</strong></td><td>围攻方损失上限兵力的 <strong>5%</strong>，进度不变</td></tr>
    <tr><td><strong>总点 ≤ 4（且非自然 1）</strong></td><td>保持现状</td><td>守军与进度均不变</td></tr>
    <tr><td><strong>总点 5 – 11</strong></td><td>物资短缺</td><td>守军损失 2%，累积围城进度 <strong>+1</strong></td></tr>
    <tr><td><strong>总点 12 – 13</strong></td><td>食物短缺</td><td>守军损失 3%，累积围城进度 <strong>+2</strong></td></tr>
    <tr><td><strong>总点 14 – 15</strong></td><td>水源短缺</td><td>守军损失 5%，累积围城进度 <strong>+3</strong></td></tr>
    <tr><td><strong>总点 16 – 19</strong></td><td>守军逃亡</td><td>守军损失 10%，累积围城进度 <strong>+2</strong></td></tr>
    <tr><td><strong>总点 ≥ 20（或守军剩 ≤ 5%）</strong></td><td><strong>要塞投降</strong></td><td>围城结束，地点控制权易手</td></tr>
    <tr><td><strong>每阶段独立判定：城墙缺口</strong></td><td>轰出缺口（最多 3 处）</td><td>当次守军损失 5%、进度 +2，此后每处缺口常驻提供 +2 检定点并开放<strong>{T('assault','强攻')}</strong></td></tr>
  </tbody>
</table>
"""
            },
            {
                "id": "siege-supply",
                "title": "05 · 补给上限、超载耗粮、补给站与海陆粮道",
                "en": "Supply Limit, Overstacking Food Penalty, Supply Depots & Naval Food",
                "html": f"""
<div class="formula-box">
<strong>补给上限、后勤距离与损耗（Supply Limit &amp; Attrition）</strong> {M('supply_attrition')}<br>
<span class="base-inline">基准值</span>地点基础补给上限为 <strong>15</strong>（<code>location_base_values</code>，本国领地另享 +25% 关系加成）；地点最大损耗上限基准为 <strong>10%</strong>；国家陆军后勤距离基准为 <strong>30</strong>；补给站容量基准为 <strong>1,000</strong>。
</div>
<p>部队将麾下各兵团重量加总与所在地点的 <strong>{T('supply_limit','补给上限')}</strong> 比较：</p>
<ul>
  <li><strong>超载最多 4 倍耗粮与撤退丢粮</strong>：超出当地补给上限不会立即直接死人，而是按超载比例增加部队军粮消耗，额外耗粮封顶 <strong>+300%（即总耗粮变为正常值的 4 倍）</strong>，迅速抽干随军携带军粮（辅助团每千人携粮系数高达 3,000、耗粮仅 0.2，是远征军的核心粮车）。一旦随军军粮耗尽断粮，即刻触发高额缺粮月度损耗；且陆军战败撤退时会直接损失随身携带军粮的 <strong>50%</strong>。</li>
  <li><strong>前线三条合法补粮渠道</strong>（受后勤距离限制，敌军与敌方要塞 ZoC 会截断后勤线）：<br>
    ① <strong>有取粮权的省份（Food Access）</strong>：在本国或签有取粮条款的盟友/通行国直接调用省粮仓；<br>
    ② <strong>敌境建立 {T('supply_depot','补给站（Supply Depot）')}</strong>：解锁对应革新后，在己方已控制的敌境地点耗 100 人力建立，每次可将军队所携粮食的 25% 存入（冷却 30 天），为周围 <strong>≤ 2 个地点距离</strong> 内的友军供粮；<br>
    ③ <strong>海军跨海送粮</strong>：邻近海域舰队先对有取粮权的沿岸地点开启「{T('gathering_food','收集食物')}」装船，再开启「{T('distributing_food','分发食物')}」为相邻 <strong>1 格距离</strong> 内无法就地取粮的友方陆军供粮。</li>
  <li><strong>焦土战术（Scorched Earth）</strong>：在己方控制地点发动后，使敌军移动成本 <strong>+50%</strong>、本地产粮 <strong>−50%</strong>（代价为本地月繁荣度 −5 个百分点），专用于拖垮深入腹地的大规模敌军粮道。</li>
</ul>
"""
            },
        ],
        "discussion": {
            "title": "战术算账 · 围城「继续等待」与「缺口强攻」如何权衡减员？",
            "html": """
<ul>
  <li><strong>用期望损耗对比强攻伤亡</strong>：设 4,000 人围攻 600 守军的要塞，阶段 30 天，当前每阶段投降概率约 25%（期望还需 4 阶段 = 120 天），而严冬山地每月损耗 3%，等待 4 个月将非战斗减员约 <strong>459 人</strong>。若此时城墙已轰开缺口，估算用常备步兵（切勿用征召兵）发起一次必胜强攻仅阵亡约 300 人，则果断强攻反而比苦等少死 159 人，且提前 4 个月解放主力并避免敌方援军合围。</li>
</ul>
"""
        },
        "quick_links": [
            ("训练度 / 军事战术 / 士气独立反查", "metrics.html#discipline"),
            ("围城能力 / 要塞防御 / 补给独立反查", "metrics.html#fort_defensive"),
            ("401 种陆海军单位完整数值表", "ledgers.html#unit_types"),
            ("接敌概率与兵种混编计算器", "lab.html#calc"),
        ],
    },

    # =========================================================================
    # CHAPTER 09
    # =========================================================================
    {
        "id": "ch09",
        "slug": "ch09-navy-war-peace.html",
        "num": "09",
        "pillar": "military",
        "title": "舰种海域换算、海上存在、私掠封锁、宣战理由与和约",
        "en": "Naval Terrain Math, Maritime Presence, Privateers, Casus Belli & Peace Terms",
        "subtitle": "通过同宽度桨帆船与重型舰的四海域火力算例掌握海军配船，解析港口与舰队如何维持海上存在，对比宣战理由的割地倍率，并算清未占要塞 −33% 与大国和约折扣。",
        "upstream": [
            ("沿海港口水手、木材与船具供给", "ch08-military-combat.html#force-types", "码头至海军基地产出水手，船厂按时代模板建造四大舰种"),
            ("间谍网 20 点或议会 50% 支持度", "ch05-estates-rebels.html#parliament", "分别提供常规伪造宣战理由与议会批准省份宣称两条开战路径"),
            ("野战胜利与要塞占领", "ch08-military-combat.html#siege-forts", "累积战争分数并解除敌方关联要塞对割地条款的封锁与加价"),
        ],
        "engine": "按作战海区宽度配比桨帆、轻舰与重舰争夺制海权与封锁港口，日常用港口与巡逻舰队维持海区海上存在，战时围绕战争目标积累战分并按和约成本效率拟定条款。",
        "downstream": [
            ("跨海行政邻近度损耗骤降", "ch01-territory-core.html#proximity", "100% 海上存在将单格海域邻近度损耗由 30 压至 5"),
            ("扩张敌意（AE）与赔款通胀", "ch10-diplomacy-subjects.html#antagonism-coalition", "割地触发周边敌意检定（割给属国 −50%）；索取大额赔款推高本国通胀"),
            ("厌战度与和平呼声反噬", "ch05-estates-rebels.html#power-balance", "高厌战同步削减陆海士气、阶层满意度均衡与要塞防御"),
        ],
        "redlines": [
            ("1.69× vs 0.34×", "同宽桨帆对重舰火力比", "同占 1.5 宽度下，3 艘桨帆在狭窄水域火力为 1 艘重舰的 1.69 倍，大洋则跌至 0.34 倍"),
            ("×0.75 vs ×1.25 vs ×10", "三种宣战理由割地倍率", "核心省宣称割地战分 ×0.75，议会批准宣称 ×1.25，羞辱宿敌高达 ×10"),
            ("−15% 叠 −18% = −33%", "未占且未围要塞和约惩罚", "索取关联要塞未占领的地点扣 −15% 和约效率，整场战争从未围攻过该要塞再扣 −18%"),
            ("战斗 50 / 目标 25", "战争分数分项上限", "总战分上限 100；单靠战斗最高 50 分，持续控制战争目标最高跳满 25 分"),
        ],
        "sections": [
            {
                "id": "naval-combat",
                "title": "01 · 四大舰种、海域地形倍率与同宽度火力复算",
                "en": "Ship Classes, Sea Zone Modifiers & Equal-Frontage Firepower Math",
                "html": f"""
<p>常备海军分为<strong>桨帆战舰（Galley，默认占宽 0.5）</strong>、<strong>轻型战舰（Light Ship）</strong>、<strong>重型战舰（Heavy Ship，默认占宽 1.5）</strong>与<strong>运输船（Transport）</strong>四类（海军征召船战力极弱且仅在有港口的沿海地点可征召）。舰船返港维修时，实际每期修理速度取 <code>max(港口修理速度, 舰队自身海上修理速度)</code>；海战结束后严格区分<strong>沉没</strong>与<strong>俘获</strong>（俘获敌舰直接编入胜方舰队）。</p>

<table class="data-table">
  <thead><tr><th>作战海域类型</th><th>3 艘文艺复兴桨帆船（共占 1.5 宽，27 炮）</th><th>1 艘早期卡拉克重舰（占 1.5 宽，40 炮）</th><th>同战线宽度火力比（桨帆 ÷ 重舰）</th></tr></thead>
  <tbody>
    <tr><td><strong>狭窄水域（Narrows：海峡/海湾）</strong></td><td><code>27 × 1.50(+50%) = 40.50</code></td><td><code>40 × 0.60(−40%) = 24.00</code></td><td class="num pos"><strong>1.69 倍</strong>（桨帆显著占优）</td></tr>
    <tr><td><strong>内海（Inland Sea：地中海/红海等）</strong></td><td><code>27 × 1.25(+25%) = 33.75</code></td><td><code>40 × 0.75(−25%) = 30.00</code></td><td class="num pos"><strong>1.13 倍</strong>（桨帆略优且造价低）</td></tr>
    <tr><td><strong>普通大洋（Ocean）</strong></td><td><code>27 × 0.50(−50%) = 13.50</code></td><td><code>40 × 1.00(无减值) = 40.00</code></td><td class="num neg"><strong>0.34 倍</strong>（重舰绝对碾压）</td></tr>
    <tr><td><strong>深洋（Deep Ocean）</strong></td><td><code>0</code>（无法作战并受高损耗）</td><td><code>40 × 1.00 = 40.00</code></td><td class="num neg">重舰独占远洋</td></tr>
  </tbody>
</table>
<p><strong>港口封锁（{T('blockade','Blockade')}）</strong>：敌对舰队驻留港外海区并满足港口封锁负担（随港口人口与发展度提高）时，同时削减该港口的<strong>粮食产出、本地海上存在（−2.0）、月发展度增长（−20%）、最大控制力（−10%）与繁荣度</strong>，并消除沿海要塞围城的 −1 未封锁罚点。</p>
"""
            },
            {
                "id": "maritime-presence",
                "title": "02 · 海上存在（Maritime Presence）：月度收支公式与巡逻机制",
                "en": "Monthly Maritime Presence Formula & Fleet Patrol",
                "html": f"""
<p>{T('maritime_presence','海上存在（0–100 点）')} 按国家、按海区独立结算，是沿海与岛屿帝国降低行政邻近度海路损耗（0 点时每海格耗 30，100 点时降至 5）的核心支柱（注：1.4.9 已移除基础海上存在的无条件贸易说明，海上贸易优势由专门修正项转化）：</p>

<div class="formula-box">
<strong>海区每月海上存在变化公式：</strong> {M('maritime_presence')}<br>
<span class="base-inline">基准值</span>按国家、按海格独立取值 <strong>0–100 点</strong>，无相邻本国港口且无驻舰时基准为 <strong>0 点</strong>；每月自然衰减基准为存量的 <strong>0.5%</strong>（<code>global_maritime_presence_decay</code>）；单港原始月贡献基准 = <code>0.10 + 0.30 × 天然港湾适宜度</code>。<br>
<code>下月存在度 = clamp(本月存在度 + 相邻本国港口汇总贡献 + 驻海区舰队贡献 − 私掠扣项 − 本月存在度 × 0.5% 自然衰减, 0, 100)</code>
<ul>
  <li><strong>单座港口本地基础项</strong> = <code>0.10 + 0.30 × 天然港湾适宜度 + 建筑加成（海岸要塞每级 +0.15、海军炮台每级 +0.30） − 敌军封锁(2.0) − 冰封(2.0) − 风暴潮(0.50)</code>（例如 80% 适宜度良港无额外建筑时提供 <code>0.34</code> 点/月原始贡献，再按海区港口除数汇总）。</li>
  <li><strong>舰队驻守与全国放大修正</strong>：轻型战舰等船型按各自等级贡献月点数（如 5 艘各给 0.20 的轻舰常驻一海区原始贡献 +1.00 点/月）；海军将领每点 DIP 提供 +0.5% 海上存在，满 100 <strong>海军传统</strong>提供高达 <strong>+50% 海上存在相对修正</strong>（另给海军士气 +20%）。</li>
  <li><strong>巡逻海域（Patrol the Seas）核对说明</strong>：1.4.9 更新日志说明每支巡逻舰队一次驻守一个海域至存在度满值再轮换下一海域（本机 <code>00_defines.txt</code> 常量 <code>PATROL_THE_SEAS_THRESHOLD</code> 仍记为 90；对咽喉海区直接分派数艘轻型舰常驻即可稳定维持接近 100 点）。</li>
</ul>
</div>
"""
            },
            {
                "id": "privateers",
                "title": "03 · 私掠者（Privateers）雇佣、收益与反海盗克制",
                "en": "Hiring Privateers, Plunder Math & Anti-Piracy",
                "html": f"""
<p>解锁私掠许可后，可在海军范围内的沿岸海域执行「雇佣{T('privateer','私掠者')}」：基础启动费 <strong>250 水手</strong>，日常基础维护 <strong>10 水手/月</strong>（本国断水手时私掠力量每月衰减 0.05）。私掠者在目标海域削减他国海上存在、按系数截取私掠金币收入（单次掠夺额达受害国月收入 10%［分母保底 5 金币］时触发满额好感惩罚），并在满足条件时每月有 <strong>2.5%</strong> 概率掳掠沿岸 1% 合格人口。受害国可派遣高<strong>{T('anti_piracy_warfare','反海盗能力')}</strong>的轻型舰巡弋清剿，也可以免间谍网、每月 +15% 的高速制造「反海盗战争」宣战理由（约 7 个月成型）。</p>
"""
            },
            {
                "id": "warfare-peace",
                "title": "04 · 宣战理由选型、两条制造途径与战争分数上限",
                "en": "Choosing Casus Belli, Two Fabrication Paths & Warscore Caps",
                "html": f"""
<p>开战前必须先对齐<strong>战争目的</strong>与<strong>{T('casus_belli','宣战理由（CB）')}</strong>——选错理由会使同一块土地在和谈时贵出数倍甚至超过 100 分上限（无理由强宣基础代价为 <strong>15 稳定度 + 1 厌战度</strong>，再乘力量投射差倍率 <code>1 − 0.01 × (攻方投射 − 守方投射)</code>）：</p>

<table class="data-table">
  <thead><tr><th>常见宣战理由</th><th>取得途径与制造耗时</th><th>有效期</th><th>关联战争目标与和约割地战分系数</th></tr></thead>
  <tbody>
    <tr><td><strong>宣称省份（核心收复）</strong></td><td>目标省含我方核心地点；耗 <strong>20 间谍网</strong>，基础每月 +4%（25个月；《伪造宣称》+25% 缩至 20个月）</td><td>15 年</td><td>夺取目标省；<strong>割地战分 ×0.75</strong>（20 分地仅收 15 分）</td></tr>
    <tr><td><strong>议会批准省份宣称</strong></td><td>对手无需有我方核心；在议会会期内消耗 <strong>50 个百分点支持度</strong> 直接绑定目标国一省</td><td>10 年</td><td>夺取目标省；割地战分与攻方敌意均为 <strong>×1.25</strong>（20 分地收 25 分）</td></tr>
    <tr><td><strong>羞辱宿敌</strong></td><td>目标为正式宿敌且无停战</td><td>宿敌存续期</td><td>展现优势；<strong>割地与附庸系数高达 ×10</strong>（20 分地变 200 分，专用于刷威望与赔款，切忌用来割地！）</td></tr>
    <tr><td><strong>关税争端 / 帝国主义</strong></td><td>上月向目标市场实缴关税 &gt;0 / 革命时代独立王国或帝国</td><td>10 年 / 25 年</td><td>要求强制进口关税豁免（20分） / 夺取首都大规模扩张</td></tr>
  </tbody>
</table>

<ul>
  <li><strong>战争分数（总上限 100）结构</strong>：战斗得分上限 <strong>50 分</strong>；持续控制战争目标累计跳分上限 <strong>25 分</strong>；其余来自地点占领与港口封锁（单地点战争价值基数 <code>2 + min(6, 地点税基 × 0.13) + 建筑/人口/首都/要塞加值</code>）。征服战争若连续 <strong>3 年</strong> 无任何战斗或围城将自动白和。</li>
  <li><strong>厌战度（War Exhaustion，上限 20）与和平呼声（Call for Peace）</strong>：每 <strong>1 点厌战度</strong> 施加<strong>陆海军士气各 −2.5%、阶层满意度均衡 −1 个百分点、全国防御 −2.5%</strong>（和平期每月消退 −0.125）。当战争持续满 60 个月且胜方战分 ≥67%，或败方执行<strong>无条件投降</strong>（开战满 12 个月可用）满 2 个月后胜方仍拖延不签和约，胜方将承受递增的「和平呼声」月厌战惩罚。</li>
</ul>
"""
            },
            {
                "id": "peace-terms",
                "title": "05 · 和平条约战分公式、要塞惩罚与大国规模折扣",
                "en": "Peace Treaty Cost Formula, Unoccupied Fort Penalty & Size Discounts",
                "html": f"""
<div class="formula-box">
<strong>和约索取地点的战分报价公式（最低需 10 战分方可提条件）：</strong><br>
<code>地点最终战分报价 = (地点基础战分 × 战争目标系数) ÷ (1 + 适用和约成本效率之和)</code>
<ul>
  <li><strong>未占领要塞重罚（−15% 至 −33%）</strong>：若拟索取地点受敌方尚未陷落的要塞保护，和约成本效率扣减 <strong>−0.15</strong>；若该要塞在整场战争中<strong>从未被围攻过</strong>，额外再扣 <strong>−0.18</strong>，合计 <strong>−0.33</strong>（使 20 分基准地涨价至 <code>20 ÷ 0.67 ≈ 29.85</code> 分，甚至直接锁死不可勾选）。</li>
  <li><strong>三大正向降价效率</strong>：① <strong>大国规模折扣</strong>：<code>min(0.50, max(0, 原属国总战争价值 − 100) × 0.001)</code>（总价值 600 的大国给满 +50% 效率，20 分地降至 13.33 分）；② <strong>对宿敌效率 +0.33</strong>；③ <strong>力量投射差</strong>：每高出对方 1 点给 +0.1% 效率（军事霸权另给 +20%）。</li>
  <li><strong>特殊条款参数</strong>：<strong>归还核心</strong>战分 ×0.50 且敌意 −75%；<strong>放弃核心</strong>战分 ×0.25；<strong>羞辱</strong>战分 <code>5 + 0.5×败方威望</code>（获 <code>max(5, 0.2×败方威望)</code>）；<strong>索取金币</strong>最多占 25 战分，但每索取相当于 1 个月收入的赔款会产生 <strong>+0.02 个百分点通货膨胀</strong>（12 个月收入即 +0.24% 通胀）；<strong>将占领地直接授予己方属国</strong>享受 <strong>−0.50 敌意附加修正</strong>。</li>
</ul>
</div>
"""
            },
        ],
        "discussion": {
            "title": "和谈检查单 · 签约前省下几十点战分与一半敌意的三步操作",
            "html": """
<ul>
  <li><strong>停火签约前三查</strong>：① 检查拟割省份旁是否有从未派兵接触过的敌方要塞——哪怕派一队轻骑踏上该要塞触发一次围城记录，也能先去掉 −18% 的「从未围攻」罚项，攻克后更是彻底消除 −33% 除数惩罚；② 若无需直辖边地，先在地图面板把占领权移交给参战附庸，和约直接割给属国以触发 −50% 敌意减免；③ 索取现金赔款时对照当前通胀水平，避免在铸币已达上限时叠加高额输入性通胀。</li>
</ul>
"""
        },
        "quick_links": [
            ("海上存在 / 水手 / 人力独立反查", "metrics.html#maritime_presence"),
            ("113 种宣战理由全表", "ledgers.html#casus_belli"),
            ("78 种战争目标全表", "ledgers.html#wargoals"),
            ("72 项和平条约条款名录", "directory.html#peace_treaties"),
        ],
    },

    # =========================================================================
    # CHAPTER 10
    # =========================================================================
    {
        "id": "ch10",
        "slug": "ch10-diplomacy-subjects.html",
        "num": "10",
        "pillar": "diplomacy",
        "title": "外交容量与接受度、间谍情报、敌意包围网、属国吞并与国际组织",
        "en": "Diplomatic Capacity, Covert Actions, Antagonism, Subjects & International Organizations",
        "subtitle": "汇集同盟/继承契约/防御联盟三大外交容量公式、12 项间谍行动、地点敌意对数生成与包围网门槛、22 类属国忠诚与连通度算式，以及共主邦联、神罗帝国权威与天朝天命机制。",
        "upstream": [
            ("国家等级、君主 DIP 与外交投入", "ch04-government-cabinet.html#government-power", "决定外交容量上限、外交声誉、每月外交官与吞并基础进度"),
            ("和约割地与力量投射", "ch09-navy-war-peace.html#peace-terms", "割地发展度生成原始敌意；力量投射折算宣战与和约成本"),
            ("途经地区控制力与海上存在", "ch01-territory-core.html#control", "决定宗主国对属国的领土连通度（0–100 分）及属国忠诚"),
        ],
        "engine": "在外交容量约束下缔结同盟、王室联姻或继承契约，积累间谍网执行秘密行动，管控扩张敌意防止触发包围网，维持属国忠诚推进外交吞并，并在国际组织内竞逐领导权与共同立法。",
        "downstream": [
            ("盟军协同作战与通行补给", "ch08-military-combat.html#siege-supply", "同盟自动开放陆地通行与舰队停泊权；属国按六种军事姿态协同作战"),
            ("版图无痛扩张与核心继承", "ch01-territory-core.html#core-power", "完成属国或共主邦联成员吞并后，直接并入其领土与既有核心"),
            ("共同国库投资与帝国统一", "ch11-scenarios-missions-dlc.html#formables-events", "神罗皇帝与天朝天子运用权威/天命推行组织改革与成员投资"),
        ],
        "redlines": [
            ("强盟权重 > 1.0", "联盟集团附加容量", "列强计 1.0、区域强权计 0.5；总和超 1 后每份同盟均加收 0.3 × (总权重 − 1) 外交容量"),
            ("敌意 >50 且好感 <−50", "加入包围网双门槛", "敌意对好感乘 −4；同时越过两线且无停战方可入网，改善好感至 ≥−50 即可阻断"),
            ("属国实力 > 20%", "集团实力忠诚惩罚", "全体属国综合实力占宗属总和超 20% 部分乘 −60 扣忠诚；忠诚 <50 停吞并且拒参战"),
            ("每跨无控区 −20 分", "属国陆路连通度", "连通度 = 100 − Σ 20 × (1 − 途经地区平均控制力)；同时吞并多国每多 1 国速度 −50%"),
        ],
        "sections": [
            {
                "id": "diplo-capacity",
                "title": "01 · 双边关系、三种「外交容量」占用算式与力量投射",
                "en": "Relations, Three Diplomatic Capacity Formulas & Power Projection",
                "html": f"""
<p>双边往来由三项有向指标记录：<strong>{T('opinion','好感')}</strong>（−200 至 +200）、<strong>{T('trust','信任')}</strong>（0–100，均衡 50；好感或信任任一 ≥75 即可使中立国家转为友好态度，状态退出带回差防抖）与<strong>{T('favors','人情')}</strong>（上限 100，每月自然衰减余额的 1%；「赠礼」按 <code>受赠国月收入×2 + 赠送国月收入</code>［保底 25 金币］支付并获 +5 人情；请求军事通行耗 5 人情）。16 岁以下皇室子女可先订立<strong>{T('betrothal','婚约（Betrothal）')}</strong>，成年达标后自动转为正式王室联姻。</p>

<div class="formula-box">
<strong>① 外交容量、外交范围与外交官（{T('diplomatic_capacity','Diplomatic Capacity')}）</strong> {M('diplo_capacity')}<br>
<span class="base-inline">基准值</span>国家基础外交容量为 <strong>2.0 点</strong>（<code>country_base_values</code>，另加公国 +1 / 王国 +2 / 帝国 +3）；基础外交范围为 <strong>1,000</strong>（公国 +200 / 王国 +500 / 帝国 +1,000）；最大外交官基准为 <strong>3 名</strong>（月恢复 +0.10 名/月，列强另 +0.20/月）。
<ol>
  <li><strong>双边同盟占用容量</strong> = <code>0.5 + clamp(2 × 对方经济基础 ÷ max(1, 本国经济基础), 0.1, 3.0) + (0.5 − 对方对我好感 ÷ 200) + 对方强权身份（列强 +1.0 / 区域强权 +0.5） + max(0, 0.3 × [本国列强盟友数 + 0.5 × 区域强权盟友数 − 1])</code></li>
  <li><strong>继承契约买方占用容量</strong> = <code>1 + clamp(2 × 买方经济基础 ÷ max(1, 授予方经济基础), 0.5, 3.0)</code>。</li>
  <li><strong>防御联盟成员占用容量</strong> = <code>0.33 × 联盟成员总数 + 0.0005 × 其他成员经济基础之和</code>（包围网固定每成员占 1 点容量）。</li>
</ol>
</div>

<div class="formula-box">
<strong>② 外交声誉与 {T('power_projection','力量投射')}（相互独立指标）</strong> {M('diplo_reputation')}<br>
<span class="base-inline">基准值</span>国家基础外交声誉为 <strong>+1.0</strong>（<code>country_base_values</code>）；力量投射初始无强权无革新时基准为 <strong>0 点</strong>。
<ul>
  <li><strong>外交声誉变化与作用</strong>：君主每点 DIP(+0.05)、教士高满意度(×2)、王室力量(满 +2)、文化影响力(+2)、改革《传统外交伦理》(+3)提升（违约扣 −1）；提高外交接受度，且<strong>每 1 点声誉降低新产生敌意 −4%</strong>。</li>
  <li><strong>力量投射变化与作用</strong>：列强(+10)/区域强权(+5)、每项已研革新(+0.05)、强权野心革新(+5~+10)、王室力量(满 +5)、外向价值观(满 +5)提升；<strong>每 1 点提供全国整合速度 +1%、政治影响力月获取 +1%</strong>，并降低宣战与殖民门槛。</li>
</ul>
</div>
"""
            },
            {
                "id": "intelligence-fow",
                "title": "02 · 战争迷雾、情报门槛与 12 项间谍网秘密行动",
                "en": "Fog of War, Intelligence & 12 Spy Network Covert Actions",
                "html": f"""
<p>地图视野（{T('fow','战争迷雾')}）对己方控制地、盟友/宗主/属国共享，且<strong>本国核心地点被敌军占领时仍保留视野</strong>（注：<code>00_defines.txt</code> 中按 5/15/25 间谍网揭示外国面板数据的信息迷雾开关在 1.4.9 默认规则中处于注释关闭状态；「国家雄心」仅保留界面文本而无常规可选条目）。派遣外交官建立 {T('spy_network','间谍网')} 基础每月 +1 点（停派每月 −1 点，满 25 点后存在暴露风险）：</p>
<table class="data-table">
  <thead><tr><th>间谍网消耗</th><th>可执行秘密行动及核心效果</th></tr></thead>
  <tbody>
    <tr><td><strong>5 点 / 20 点</strong></td><td><strong>破坏声誉（5点）</strong>：降低第三国对目标好感 ｜ <strong>制造宣战理由（20点）</strong>、<strong>腐化官员（20点，削弱内阁效率）</strong>、<strong>散布不满（20点，削弱维稳投入）</strong></td></tr>
    <tr><td><strong>30 点 / 40 点</strong></td><td><strong>支持叛军（30点）</strong>、<strong>煽动属国独立（30点）</strong> ｜ <strong>窃取地图（40点，揭示已知地区）</strong>、<strong>无效化宣战理由（40点，移除对方对我的 CB）</strong></td></tr>
    <tr><td><strong>50 点 / 75 点 / 刺杀</strong></td><td><strong>渗透政府（50点，获取行政军事情报）</strong>、日本氏族侦察/破坏（50/70点） ｜ <strong>窃取技术（75点：己方 +20% 目标在研进度，目标损失 10%）</strong> ｜ <strong>刺杀人物（25–100点）</strong></td></tr>
  </tbody>
</table>
"""
            },
            {
                "id": "antagonism-coalition",
                "title": "03 · 敌意（Antagonism）生成公式、消退规则与包围网门槛",
                "en": "Antagonism Generation Math, Decay & Coalition Rules",
                "html": f"""
<div class="formula-box">
<strong>和约索取单处地点产生的「{T('antagonism','敌意（AE）')}」计算链：</strong> {M('antagonism_ae')}<br>
<span class="base-inline">基准值</span>初始敌意为 <strong>0 点</strong>；敌意产生修正与衰减修正基准均为 <strong>0%</strong>；和平期基础年度消退：割地敌意 <strong>2.0 点 / 年</strong>、和约其他条款 <strong>3.0 点 / 年</strong>；包围网入网双硬线：<strong>敌意 &gt; 50 且好感 &lt; −50</strong>。<br>
<code>单地点原始敌意 = 0.4 + 0.04 × 发展度 + 0.4 × log₂(发展度)</code>（例如发展度 20 的地点原始贡献约 <strong>2.93</strong> 点）
<ul>
  <li><strong>交战方与条款层修正</strong>：进攻国每点列强积分 +1%（封顶 +25%），防守国每点 −1%（最多 −50%）；索取非主战目标领土 +15%；每点外交声誉 <strong>−4%</strong>；<strong>将地点直接授予己方属国 −50%</strong>；建筑型国家基础层 −85%、宗主国观察自己属国扩张 −90%。</li>
  <li><strong>观察国距离与文教亲缘缩放</strong>：距离每 100 单位按 0.75 衰减；观察国与被割地点同文化 <strong>+40%</strong>（同文化组 +20%）、同宗教 <strong>+35%</strong>（异宗教 <strong>−35%</strong>）、同方言 +25% / 同语言 +20% / 同语族 +5%（若观察国列强分达侵略者 2.5 倍以上还会触发“不太在意”减免）。</li>
  <li><strong>好感拖拽、年度消退与 {T('coalition','包围网')} 入退条件</strong>：每 1 点敌意对好感乘 <strong>−4</strong>；割地敌意基础每年消退 2 点、和约其他要求每年消退 3 点（满威望加速 +25%，DIP 内阁「缓解忧虑」+10%；<strong>注意：身处进攻战并担任进攻方期间，自然消退暂停！</strong>）。外国须同时满足<strong>对我敌意 &gt; 50、对我好感 &lt; −50</strong> 且无停战/非从属，方可加入包围网。</li>
</ul>
</div>
"""
            },
            {
                "id": "subjects-annex",
                "title": "04 · 22 类属国义务、忠诚度与连通度算式、外交吞并速度",
                "en": "22 Subject Types, Loyalty & Connectivity Math & Diplomatic Annexation",
                "html": f"""
<p>除战争臣服与外交附庸外，可随时对本国非殖民中省份执行「<strong>建立省份属国</strong>」或对境外建筑区执行「建立建筑属国」（参战后可逐国设定常规、侵略、<strong>支援［优先协同友军野战与围城］</strong>、被动、防御、袭扰六种军事姿态）。常见属国缴费与吞并参数对比如下（完整 22 类见速查表）：</p>
<ul>
  <li><strong>可外交吞并类</strong>：普通<strong>附庸（Vassal）</strong>与共戴一君的<strong>采邑（Fiefdom）</strong>均缴 <code>20% × 属国经济基础</code> 金币，维持满 <strong>10 年</strong>、启动好感 <strong>+150</strong>（维持 ≥+125）可吞并；<strong>封邑（Appanage）</strong>需 15 年与 +190 好感；拜占庭<strong>普罗尼亚</strong>另缴 10% 人力与水手（20 年 / +190 好感）；<strong>自治领（Dominion）</strong>需 50 年。</li>
  <li><strong>类型禁止直接外交吞并类</strong>：<strong>卫戍国（March，缴 10% 金币）</strong>、<strong>殖民领（缴 2.5% 金币 + 10% 人力水手）</strong>、<strong>贸易公司（缴 50% 金币）</strong>、<strong>朝贡国</strong>、<strong>土司</strong>与帝国自由市等。</li>
</ul>

<div class="formula-box">
<strong>① 附属国忠诚度与连通度（Subject Loyalty &amp; Connectivity）</strong> {M('subject_loyalty')}<br>
<span class="base-inline">基准值</span>属国忠诚度范围 <strong>0–100 点</strong>，顺从合格门槛基准为 <strong>50 点</strong>；全体属国综合实力免罚阈值基准为宗属总和的 <strong>20%</strong>；陆路领土连通度满分基准为 <strong>100 分</strong>。
<ul>
  <li><strong>正向与负向变化</strong>：好感每点 <strong>+0.15</strong>、信任每点 <strong>+0.10</strong>、君主每点 DIP <strong>+0.10</strong>、地方分权满端 <strong>+30</strong>（中央集权满端 −20）；<strong>集团实力超标惩罚</strong> = <code>−60 × max(0, 全体属国综合份额 − 0.20)</code>；<strong>{T('subject_territory_connectivity','领土连通度')}</strong> = <code>max(0, 100 − Σ[20 × (1 − 途经地区平均控制力)])</code>。</li>
</ul>
</div>

<div class="formula-box">
<strong>② 外交吞并总成本与每月吞并进度（Diplomatic Annexation Speed）</strong> {M('annexation_speed')}<br>
<span class="base-inline">基准值</span>吞并固定起底成本基准为 <strong>50 点</strong> + 每处属国地点 <strong>10 点</strong>；国家基础吞并速度为 <strong>+0.50 点 / 月</strong>（满外交预算另供 +0.50 点/月，合计 1.0 点/月基数）；交界控制力门槛 <strong>≥ 35%</strong>。<br>
• <code>每月吞并进度 = (全国基础 0.5 + 外交预算投入 0~0.5) × 类型速度系数 × (1 + 中央集权[+33%] + 属国忠诚×0.2%[满+20%] + 同主流文化/文化影响差加成 − 50% × 额外同时吞并国数)</code>。<br>
<em>注意：每多同时吞并 1 个属国，所有在吞目标的速度修正均扣减 <strong>−50 个百分点</strong>，宜逐个单线吞并。</em>
</div>
"""
            },
            {
                "id": "pu-and-ios",
                "title": "05 · 共主邦联一体化、神罗帝国权威与中华天朝天命",
                "en": "Personal Unions, HRE Imperial Authority & Middle Kingdom Mandate",
                "html": f"""
<p><strong>1. {T('union','共主邦联（Personal Union）')} 的整合等级与议会追赶机制</strong>：<br>
共享君主的国家组成共主邦联，默认由经济基础最高者出任<strong>资深伙伴（Senior Partner）</strong>。邦联吞并须先通过组织立法提升「<strong>{T('union_integration_level','邦联整合等级')}</strong>」：基础成立满 <strong>50 年</strong> 并通过《王冠统一》开放成员吞并（后续《迅速统一》年限 −10 年、速度 1.5；《快速统一》年限 −20 年、速度 2.0）。<strong>关键规则</strong>：每次修法仅提升当时参与实施成员的个人等级；中途新加入邦联的次级伙伴若个人等级落后于组织等级，资深伙伴须在入会满 5 年后召开邦联议会通过「<strong>执行法律实施（Enforce Law Implementation）</strong>」将其个人等级补齐至组织等级，方可启动外交吞并。</p>

<p><strong>2. 37 类 {T('international_organization','国际组织')} 共同金库与两大帝国体系公式</strong>：</p>
<ul>
  <li><strong>共同国库与领袖定向投资</strong>：启用组织金库后，独立领袖可对成员发起三类 10 年衰减投资（成员直接收到支出金额 <strong>75%</strong> 的现金并获强力修正：<strong>经济投资</strong>给建造效率 +100%、RGO 工期 −50%；<strong>行政投资</strong>给稳定投入 +0.10、整合速度 +20%；<strong>军事投资</strong>给陆海维护效率各 +50%）。</li>
  <li><strong>神圣罗马帝国 · 帝国权威（Imperial Authority，0–100）月度收支</strong>：初始设 4 世俗 + 3 教会共 7 席选帝侯。每月变化 = 内部和平 <strong>+0.05</strong>（皇帝主动攻打成员扣 −0.50）+ 每个自由市 <strong>+0.003</strong> + 诸侯数项 <code>(成员数 − 125) × 0.001</code>（意大利脱离后基准 75）− 每个缺额选帝席 <strong>−0.10</strong> − 异端/异教诸侯扣分 − 外国占有帝国地点（德意志区每处 −0.003、其余 −0.001）+ 皇帝总能力超出 150 部分 ×0.001。累积权威用于推进金玺诏书、永久和平、帝国行政圈与皇权改革（满 50 权威可执行「推翻帝国议会」）。</li>
  <li><strong>中华天朝（Middle Kingdom）· 天命（{T('celestial_authority_gc','Celestial Authority')}，初始 70，范围 0–100）</strong>：每月基础自然变化 <strong>−0.10</strong>，成员间交战每国 −0.01/月，每道维持敕令 −0.10/月；普通成员按 <code>0.005 × (对皇帝好感 ÷ 200) × (成员经济基础 ÷ 1,000)</code> 正负贡献；皇帝<strong>对外赐赉滑块</strong>在 0% / 50% / 100% 时分别提供 <strong>−0.20 / 0 / +0.20</strong> 月天命。保持天命严格高于 20 方可推行户籍登记等天朝律令。</li>
</ul>
"""
            },
        ],
        "discussion": {
            "title": "外交控盘 · 如何拆解潜在包围网并平稳消化大片附庸？",
            "html": """
<ul>
  <li><strong>双线阻断包围网</strong>：由于加入包围网必须<strong>同时满足「敌意 &gt; 50」与「好感 &lt; −50」</strong>，在签下割地和约前展开敌意预览名单，对敌意即将突破 50–65 区间的邻近强国提前派遣外交官拉满「改善关系」与赠礼——只要将其总好感维持在 −49 以上（或通过错峰宣战保持双边停战期），即便敌意过 50 对方也无法入网。</li>
  <li><strong>多附庸集团防背叛</strong>：当属国集团综合实力逼近 20% 阈值时，一方面扩充宗主本国常备军与核心税基做大分母，另一方面打通途经地区的控制力（或港口海上存在）将属国领土连通度维持在 80–100 分，并在单次只专注吞并 1 个文化相近、满 190 好感的核心附庸，避免触发多线吞并 −50% 减速惩罚。</li>
</ul>
"""
        },
        "quick_links": [
            ("外交容量 / 外交声誉 / 力量投射独立反查", "metrics.html#diplo_capacity"),
            ("属国忠诚度 / 外交吞并速度独立反查", "metrics.html#subject_loyalty"),
            ("194 项外交行动 & 37 类国际组织", "ledgers.html#diplomatic_actions"),
            ("22 种属国类型完整数据表", "ledgers.html#subject_types"),
        ],
    },
]
