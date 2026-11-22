# -*- coding: utf-8 -*-
"""
Chapters 01 - 05 for EU5 Mechanics Compendium (1.4.9).
Each chapter adheres to a unified 6-part structure:
  1. System Context Card (Upstream -> Core Engine -> Downstream)
  2. Interactive Inline SVG Causal Diagram
  3. Numbered Deep-Dive Mechanics Sections (with T(cid, label) interactive tooltips, formula boxes, data tables)
  4. Quick Redline Threshold Strip
  5. Community Pitfalls & Field Diagnostics (Discussion)
  6. Ledger / Simulator Cross-Links
"""


def T(cid, label):
    return f'<button type="button" class="term" data-concept="{cid}">{label}</button>'


CHAPTERS_1_5 = [
    {
        "id": "ch01",
        "slug": "ch01-territory-core.html",
        "num": "01",
        "pillar": "territory",
        "title": "疆域结构、整合四态、核心与控制力",
        "en": "Geography, Integration States, Cores & Control",
        "subtitle": "土地本身不产金币也不出兵——只有走完「未整合→已整合→核心」与「邻近度→控制力」两条轨道，疆域才会变成国家实力。",
        "upstream": [
            ("和约割地 / 殖民定居", "ch09-navy-war-peace.html#peace-terms", "输入新获「未整合」或「殖民地」地点"),
            ("MIL 内阁整合 / 同化", "ch04-government-cabinet.html#cabinet-actions", "推动未整合升为已整合、主流文化占比过 50%"),
            ("海上存在 / 道路 / 总督", "ch09-navy-war-peace.html#maritime-presence", "削减邻近度在海洋与山林间的逐格损耗"),
        ],
        "engine": "决定每个地点处于哪种行政状态（征服/殖民/已整合/核心）、与首都的行政可达性（邻近度），并据此结算实际「控制力」——切分财富归国库还是归阶层。",
        "downstream": [
            ("地点税基与未受控财富", "ch03-economy-market-trade.html#wealth-to-treasury", "控制力决定税基占比，余下全部喂给阶层金库"),
            ("殖民移民独家来源", "ch07-ages-colonial.html#colonial-charters", "只有核心地点能向特许殖民地迁出人口"),
            ("阶层私人建筑攻防", "ch05-estates-rebels.html#estate-wealth", "<75%控制地沦为阶层建楼扩张势力基地"),
        ],
        "redlines": [
            ("≥ 50%", "核心化文化门槛", "已整合地点须主流或已接纳文化占比 ≥50%（相容文化不算）方成核心"),
            ("> 5 地点", "单省整合减速线", "省份含超过 5 个地点时，内阁整合省份速度受惩戒放慢"),
            ("75% 控制力", "阶层私建强拆红线", "阶层专在 <75% 控制地盖阶层建筑；王室需 ≥75% 才可直接拆除"),
            ("× 0.75", "邻近度转上限系数", "每 100 点邻近度仅贡献 +75% 最大控制上限，剩余靠核心与城乡级补齐"),
        ],
        "sections": [
            {
                "id": "hierarchy",
                "title": "01 · 地理五级嵌套与预设省份动态切分",
                "en": "Geographical Hierarchy & Dynamic Provinces",
                "html": f"""
<p>《欧陆风云 V》的地图由严格嵌套的五级地理单元构成：最小单元为 {T('location','地点')}，向上依次聚合成 {T('province','省份')}、{T('area','地区')}、{T('region','区域')} 与 {T('sub_continent','次大陆')}/{T('continent','大陆')}。玩家必须分清不同系统分别挂载在哪一层级——操作层错位是新手最常卡壳的原因。</p>
<table class="data-table">
  <thead><tr><th>地理层级</th><th>决定机制与关键操作</th><th>特殊规则与边界</th></tr></thead>
  <tbody>
    <tr><td><strong>地点（Location）</strong></td><td>{T('raw_materials','原产 RGO')}、{T('building','建筑')}、{T('location_rank','城乡等级与城镇特权')}、{T('integration_status','整合/核心状态')}、{T('control','控制力')}、市场归属、人口与驻军作战</td><td>面积大小并不均等（中位数约 25），直接影响思潮传播速率与行军天数</td></tr>
    <tr><td><strong>省份（Province）</strong></td><td>{T('provincial_food','省食物储备')}、征召兵动员、绝大多数 {T('cabinet_action','内阁行动')}（如整合/提控/传教/同化）、{T('colonial_charter','特许殖民地')} 发起对象</td><td>若多个国家瓜分同一「{T('province_definition','预设省份')}」，各国会各自独立生成一名「{T('province_capital','省会')}」和独立省粮仓</td></tr>
    <tr><td><strong>地区（Area）</strong></td><td>后期地区级内阁行动（整合地区、同化地区、提控地区）、{T('privateer','私掠部署')}、{T('exploration','海陆探险')}、接管地区防务、地方总督管辖与 {T('victory_card','胜利卡')}</td><td>控制一个地区 ≥2/3 可拥有地点即可赚取该区的「列强点数」（1–20 分）</td></tr>
    <tr><td><strong>区域 / 次大陆（Region / Subcontinent）</strong></td><td>区域强权跨界干预半径（仅限相邻区域）、{T('overseas','海外飞地')} 判定、动态历史事件及霸权地缘范围</td><td>首都与某地无陆连且跨入非相邻次大陆时触发海外飞地机制</td></tr>
  </tbody>
</table>
"""
            },
            {
                "id": "geography-climate",
                "title": "02 · 地形、气候、走廊、洋流与海格「封冻」双刃剑",
                "en": "Terrain, Climate, Corridors, Currents & Sea Freezing",
                "html": f"""
<p>自然条件并非静态背景：每个地点的 {T('topography','地形')}、{T('vegetation','植被')} 与 {T('climate','气候')} 同时决定人口容量、粮食产能、邻近度衰减、战斗宽度及补给上限；跨过 {T('river','河流')}、{T('strait','海峡')} 或海上登陆作战更会给进攻方施加骰点惩罚（跨河 −1、渡海峡 −2、海上登陆 −1）。</p>
<ul>
  <li><strong>不可通行地、荒地与「走廊（Corridor）」</strong>：普通 {T('impassable','荒地')} 既不能拥有也不能通行，但特殊地貌 <strong>{T('corridor','走廊')}</strong> 虽然同样无人居住、不可宣称所有权，却允许 {T('army','陆军')} 直接穿越调动。</li>
  <li><strong>海洋、洋流与航运加速</strong>：{T('sea_current','洋流')} 会令顺流舰队加速、逆流减速；带狭窄（Narrows）地形的海格还会阻隔海格间的 {T('fow','战争迷雾视野')}。</li>
  <li><strong>冬季等级与「{T('frozen','封冻')}」冰封机制</strong>：根据南北半球（北半球约一月、南半球约六月），气候限制当地可达到的最大 {T('winter_level','冬季等级')}（无冬/轻冬/常冬/严冬）。严重寒冬会让建造停工，连续严冬更有 <strong>20%</strong> 概率将浅海封冻成冰面——此时陆军可直接踏冰行军并传递更高控制力，但港口内的舰队将被彻底搁浅。入春解冻概率高达 <strong>40%</strong>，若解冻瞬间大军仍在冰格行军，将遭遇毁灭性冰沉减员！</li>
</ul>
"""
            },
            {
                "id": "integration-core",
                "title": "03 · 核心补全专题：整合四态（征服→殖民→已整合→核心）全流程",
                "en": "The 4 Integration States & Coring Pipeline",
                "html": f"""
<div class="callout warn"><strong>新手第一大误区：把「整合（Integrated）」当成「核心（Core）」！</strong><br>
在 EU4 中吞并完点一次造核即大功告成，而在 EU5 中这是<strong>两段完全独立的门槛</strong>：内阁大臣只能把新打下来的地从「未整合」推进到「已整合」；要升级为「核心」，必须靠当地<strong>主流文化或已接纳文化人口比例 ≥ 50%</strong>（<code>CORE_THRESHOLD = 0.5</code>，相容文化不计入）。</div>

<table class="data-table">
  <thead>
    <tr><th>整合阶段</th><th>进入条件 / 转化手段</th><th>最大控制力修正</th><th>分离主义 / 控制恢复</th><th>同化、皈依与特殊效果</th></tr>
  </thead>
  <tbody>
    <tr>
      <td><strong>1. 未整合（征服）</strong><br><code>conquered</code></td>
      <td>战争割让、外交通商购地等非核心夺取地点的默认起始态</td>
      <td class="num neg">−10%</td>
      <td>本地分离主义 <strong>+0.50</strong></td>
      <td>同化速度 −2%、皈依速度 −2%、守军增长 −0.5%、叛乱基础进度 +1%</td>
    </tr>
    <tr>
      <td><strong>2. 殖民地</strong><br><code>colonized</code></td>
      <td>特许殖民地达标（≥1,000 人且文化宗教过线）完成定居</td>
      <td class="num">0%</td>
      <td>无分离主义；月控 <strong>+0.10%</strong></td>
      <td>直接豁免未整合惩罚，待文化占比达 50% 后晋级核心</td>
    </tr>
    <tr>
      <td><strong>3. 已整合</strong><br><code>integrated</code></td>
      <td>指派 {T('mil','MIL')} 内阁执行「<strong>整合省份</strong>」或后期「<strong>整合地区</strong>」至 100%</td>
      <td class="num pos">+5%</td>
      <td>残余分离主义降至 <strong>+0.10</strong></td>
      <td>解除皈依与守军惩罚，同化惩罚减轻至 −1%，但仍无法输送殖民人口</td>
    </tr>
    <tr>
      <td><strong>4. 核心</strong><br><code>core</code></td>
      <td>在已整合（或殖民）地点内，拥有者的<strong>主流文化或已接纳文化</strong>占比达到 <strong>≥ 50%</strong> 时自动转化</td>
      <td class="num pos">+20%</td>
      <td>分离主义<strong>彻底清零</strong>；月控 <strong>+0.10%</strong></td>
      <td>同化惩罚清零；<strong>自然出生人口 100% 属主流文化</strong>；被敌军占领时始终保留视野</td>
    </tr>
  </tbody>
</table>

<div class="formula-box">
<strong>内阁整合与进度衰退底层公式（<code>00_defines.txt</code>）：</strong><br>
• <strong>整合行动速率</strong>：执行 MIL 行动 <code>integrate_province</code>（省份整合速度 +100%），受执行者军事能力与全国内阁效率放大。<br>
• <strong>三大拖慢因素</strong>：① 单省地点数超过 <code>5</code> 个触发地点数惩罚；② 城镇/城市等级与庞大总人口；③ 我方文化战争力弱于当地文化。若文化为已接纳文化则整合权重显著提高。<br>
• <strong>进度倒扣与保留</strong>：爆发叛乱立刻倒扣 <code>−10</code> 进度；被敌军占领每月掉 <code>0.025</code>；丧失所有权每月掉 <code>0.10</code>。非己方持有的剧本历史核心默认保留 <code>100 年</code>（和约归还核心仅需 0.5× 战分，强迫撤销核心需 0.25× 战分）。
</div>
"""
            },
            {
                "id": "core-power",
                "title": "04 · 为什么「核心（Core）」决定全局战局与殖民命脉？",
                "en": "Seven Strategic Effects of Cores",
                "html": f"""
<p>除了最大控制力比「已整合」整整高出 <strong>15 个百分点</strong>（+20% vs +5%）之外，{T('core','核心')} 还是七项跨系统机制的共同前置阀门：</p>
<ol>
  <li><strong>殖民迁徙唯一人口蓄水池</strong>：游戏明确规定，仅有处于 <strong>核心状态</strong> 的地点能够向海外 {T('colonial_charter','特许殖民地')} 输出 {T('colonial_migration','殖民移民')}。早期把周边新征服省份升为核心能显著加快殖民速度。</li>
  <li><strong>自然增长自动同化引擎</strong>：核心地点生效 <code>growth_is_primary_culture = yes</code>，无论当地还残留多少异文化少数群体，<strong>每月新出生的全部人口直接归入国家主流文化</strong>，滚雪球式锁死文化优势。</li>
  <li><strong>战时永不丢失的战略视野</strong>：只要一处地点是你本国的核心，即使在战争中被敌军 {T('occupation','占领')}，你依然穿透战争迷雾永久掌握该地及周边动向（<code>owner_gets_vision_when_occupied = yes</code>）。</li>
  <li><strong>收复失地宣战理由与 AI 征服优先级</strong>：丧失核心地对占领国可低成本制造收复宣战理由（且和约归还仅花 50% 战分效率加成），同时核心令外交卖地惩罚飙升至每块地 <strong>−20 稳定度</strong> 与 10 年叛乱增长。</li>
  <li><strong>外交吞并与胜利卡终极计分</strong>：{T('annexation','吞并属国')} 时宗主会全盘继承属国的所有现有核心；后期大国角逐 {T('victory_card','胜利卡')} 必须将目标地区全部地点拿下、控制且<strong>全部转为核心</strong>方能每十年吃满 1,000 分。</li>
</ol>
"""
            },
            {
                "id": "proximity",
                "title": "05 · 邻近度辐射网与 1.4.9 水陆衰减规则",
                "en": "Proximity Radiation & 1.4.9 Pathfinding",
                "html": f"""
<p>{T('proximity','邻近度')} 衡量行政命令从 {T('capital','首都')} 辐射至全国每个地点的衰减程度。{T('capital','首都')} 恒为 <strong>100%</strong>，部分曾任国都的 {T('historical_capital','历史首都')} 自带 <strong>+50</strong> 基础邻近度（若当前首都辐射更高则取大者），特殊事件或地方总督亦可作为二级辐射源。</p>
<div class="formula-box">
地点到达邻近度 = max(0, 来源强度 − 沿最佳路径各格地理成本之和)<br>
最大控制力来自邻近度分项（百分点） = 地点邻近度百分数 × 0.75
</div>
<p>在 <strong>1.4.9 版本</strong> 中，行政邻近度与市场接入度分别走独立路径账本：</p>
<ul>
  <li><strong>陆路降损</strong>：平原顺畅、山地/崎岖/密林惩罚极重（地形减速保底系数 0.25）；修建更高等级 {T('road','道路')}、提升本地 {T('development','发展度')}，以及把社会价值观推向<strong>中央集权</strong>（满极点 +20% 邻近传播）或<strong>陆权倾向</strong>均可大幅压低每步扣分。</li>
  <li><strong>海路降损（海洋高速走廊）</strong>：跨海传播仰仗沿岸海域的 <strong>{T('maritime_presence','海上存在')}</strong>、节点 {T('harbor_capacity','港口容量')}（基于天然港口区位度叠加码头建筑，在 1.4.9 中港口对行政邻近度的装卸扣费修正为 <strong>−50%</strong>，而贸易路径港口效率基数上调至 +200%）以及社会价值观<strong>海权倾向</strong>。没有港口的海岸上岸会承受巨额损耗。</li>
</ul>
"""
            },
            {
                "id": "control",
                "title": "06 · 控制力：国库与阶层金库的权力分水岭",
                "en": "Control: Where Uncontrolled Wealth Goes",
                "html": f"""
<p>每个地点的当前 {T('control','控制力')} 并不固定，而是每月按差额缓慢趋向 <strong>{T('max_control','最大控制力')}</strong>（邻近度 × 0.75 + 整合状态 [征服 −10 / 整合 +5 / 核心 +20] + 人群满意度 + 建筑与驻军/内阁提控）。</p>
<p>控制力是全游戏最关键的「利益分流闸门」：它同时成比例决定一个地点能向国家贡献多少 <strong>{T('tax_base','税基')}</strong>、<strong>{T('army_levy','陆海军征召兵')}</strong>、<strong>月度人力</strong>、<strong>水手</strong> 与 <strong>人口升阶/同化/皈依速率</strong>。</p>
<div class="callout warn"><strong>新手必知常识：被低控制力「扣掉」的钱并没有凭空消失！</strong><br>
某地产出 1.00 杜卡特财富而控制力只有 20% 时，国库可征税基只有 0.20 杜卡特；其余 <strong>0.80 杜卡特「未受控财富」直接按当地阶级比例落入贵族、市民与教士的私有金库</strong>！你放任边疆保持低控制力，实际上是在拿自己的国土养肥国内对抗王室的阶层势力。</div>
"""
            },
            {
                "id": "urbanization",
                "title": "07 · 地点等级、城镇升格与 75 项城镇特权",
                "en": "Location Ranks & Town Rights",
                "html": f"""
<p>地点按行政建制划分为四级：<strong>{T('rural_location','乡村')}（Rural Settlement）</strong> 与三类城市化聚落——<strong>{T('town_and_city','城镇')}（Town）</strong>、<strong>城市（City）</strong> 与 <strong>大都会（Megalopolis）</strong>。各地点存在由地点等级与发展度决定的「{T('supported_building_levels','建筑等级上限')}」（含建造中与缺工建筑；1.4.8 修复了升级替换期间双倍占槽问题；超限虽可强建但造价递增）。</p>
<p><strong>城镇特权（{T('town_rights','Town Rights')}）</strong> 机制随第 3 时代（探索时代）研究对应革新对所有国家解锁（少数历史重镇开局自带）：</p>
<ul>
  <li><strong>配额限制</strong>：默认每个城镇拥有 <strong>1 个</strong> 特权槽、城市 <strong>2 个</strong>、大都会 <strong>3 个</strong>（具体效果见「数据速查典 → 城镇特权」75 项完整列表，例如大特贸港、专精纺织或学术都市权，且部分排他互斥）。</li>
  <li><strong>城市化代价警钟</strong>：将乡村升格为城镇后，本地建筑上限、市民人口容量、最大控制力与市场吸引力虽大幅跃升，但会永久压低本地 {T('food_productivity','食物生产效率')} 并将部分农村人群转入消费口粮而不产粮的城市阶级！</li>
</ul>
"""
            },
        ],
        "discussion": {
            "title": "论坛实战讨论与排障 · Reddit & Paradox 社区高频问题",
            "html": """
<ul>
  <li><strong>问：刚打下来的边疆省既离首都十万八千里（邻近度 0%），人口又是异文化（升不了核心），怎么办？</strong><br>
  <strong>解法</strong>：在欧盟 5 前期硬吞低控制异文化远疆属于双输——既占宝贵 MIL 内阁席位、给国库加零税收，还全把钱喂给当地贵族建私产。社区公认最优解是利用「<strong>释放省份属国（Create Province Subject）</strong>」切分给忠诚附庸或总督治理：属国会在自己首都附近产生 100 邻近度帮你建好建筑、同化并吃掉核心化成本，且你每月照收属国贡赋（日后吞并直接白捡核心）。</li>
  <li><strong>问：什么地方最值得花大价钱升为城镇/城市？哪些地绝对别升？</strong><br>
  <strong>三条铁律</strong>：① <strong>核心高控制产粮区绝不升城</strong>（特别是高产量小麦/牲畜/鱼类省会，留着当全市场廉价粮仓养大都市）；② <strong>金银铜铁等天价稀缺 RGO 产区慎升城</strong>，确保劳工优先填满 RGO；③ <strong>优先升级高控制低价值 RGO 的沿海天然良港与关键河口枢纽</strong>，既能建码头放大水手与市场辐射，又能给市民/工匠工坊腾出海量建筑上限。</li>
</ul>
"""
        },
        "quick_links": [
            ("城镇特权 75 项速查", "ledgers.html#town_rights"),
            ("控制力与税基分流模拟", "lab.html#calc"),
            ("36 节点因果星图", "map.html#control"),
        ],
    },

    {
        "id": "ch02",
        "slug": "ch02-population-food.html",
        "num": "02",
        "pillar": "economy",
        "title": "人口生态、迁移潮、疫病与三级粮食安全",
        "en": "Population, Migration Dynamics, Diseases & Food Chain",
        "subtitle": "人口是一切RGO产出、城市工匠、税收份额与征召兵的母池；粮食危机不仅饿死人口，更会瞬间抽干国家财政。",
        "upstream": [
            ("地点等级、气候与河流", "ch01-territory-core.html#geography-climate", "决定地点人口容量与食物基础产量"),
            ("文化地位与宗教容忍", "ch06-culture-religion.html#culture-status", "锁定哪些人群允许晋升及是否遭战后驱逐"),
            ("阶层满意度与物价", "ch05-estates-rebels.html#power-balance", "影响人群满意度及是否外迁"),
        ],
        "engine": "动态计算各地点人口在自然出生/瘟疫死亡/征召阵亡/跨地迁移中的净增减，推动平民向高阶阶级升级，并在「地点→省份→市场」三层粮仓之间自动买卖粮食。",
        "downstream": [
            ("RGO与建筑就业填槽", "ch03-economy-market-trade.html#production-buildings", "没劳动力、或无相容文化可晋升会导致有厂无工"),
            ("征召兵永久人口代价", "ch08-military-combat.html#force-types", "征召兵阵亡从对应人口群里永久扣除"),
            ("核心文化占比与科研识字", "ch07-ages-colonial.html#research-advances", "平均识字率直驱研发速度，核心出生100%归主流"),
        ],
        "redlines": [
            ("75% 省粮储线", "向外售粮门槛", "省粮仓先留存 ≥75% 容量且满溢才向市场卖粮；缺口自动用国库买！"),
            ("25% 市场粮库", "市民禁出口红线", "市场总粮储跌破 25% 上限时，市民商人自动禁止向境外倒卖粮食"),
            ("−5% / 月", "省饥荒致命跌幅", "省粮仓归零触发饥荒，每月饿死 -5% 人口且市场食需激增 1.5 倍"),
            ("12月 / 25年", "征服迁徙双周期", "受歧视征服地前 12 月加速逃亡；同时激发长达 25 年 3× 拓殖拉力"),
        ],
        "sections": [
            {
                "id": "population-base",
                "title": "01 · 人群构成、人口容量、升阶机制与雇佣制度",
                "en": "Pop Structure, Capacity, Promotion & Employment",
                "html": f"""
<p>在 EU5 中，每个地点的居民并非单一数字，而是被拆分为<strong>「{T('pop_type','社会阶级')} × {T('culture','文化')} × {T('religion','宗教')}」</strong>的独立 {T('pop','人群（Pops）')} 单元。总人口受制于当地 {T('population_capacity','人口容量')}（气候、植被、河流、发展度与建筑决定），接近或超出上限时人口自然增长停滞甚至衰减。</p>
<ul>
  <li><strong>六大社会阶级与政治分层</strong>：上层阶级（{T('nobles','贵族')}、{T('clergy','教士')}、{T('burghers','市民')}）与下层阶级（{T('peasants','平民')}、{T('slaves','奴隶')}），外加在 RGO 中劳动的 {T('rgo_pops','劳工与奴隶')} 与士兵池。城镇规模越大、<strong>{T('peasant_enfranchisement','自主权 / 平民赋权')}</strong> 越高，平民从地点财富中留给自己的份额就越多（自主权越低，越多的平民份额会被贵族抽走）。</li>
  <li><strong>晋升（Promotion）与「有厂无工」铁律</strong>：当新建工坊、兵营或教堂提供空缺岗位时，只能由当地的 <strong>平民</strong> 逐月向上晋升填补，且<strong>必须至少属于「相容文化（Tolerated Culture）」</strong>（受忽视文化与受歧视文化人群严禁晋升为教士、市民或贵族！）。可用正 {T('stability','稳定度')}（+稳定%/100 加速）、高 {T('control','控制力')} 及 ADM 内阁行动「<strong>促进人口升级（<code>pop_promote_action</code>）</strong>」加快补员。</li>
  <li><strong>雇佣制度（Employment System）</strong>：国家可在制度行动中切换地点填补空缺工人的优先级（优先高盈利建筑、平均分配或先保特定战略设施），应对人口紧张期的用工荒。</li>
  <li><strong>识字率（{T('literacy','Literacy')}）双刃剑</strong>：全国人口平均识字率越高，{T('research_progress','研究进度')} 越快；但高识字人口对生活必需品匮乏与高市价极其敏感，商品缺货涨价时会更剧烈地压低其 {T('pop_satisfaction','人群满意度')}。</li>
</ul>
"""
            },
            {
                "id": "migration-disease",
                "title": "02 · 征服后人口迁移潮、殖民输出与疫病结算",
                "en": "Post-Conquest Migration, Colonies & Diseases",
                "html": f"""
<p>人口是流动的资产。通常和平时期，平民只在<strong>同一市场内部</strong>从负 {T('migration_attraction','迁徙吸引力')} 地点流向正吸引力中心（需阶层特权未禁止自由迁徙；奴隶则被永久锁死原地）。而在扩张与天灾中存在三套高频机制：</p>
<ol>
  <li><strong>征服后 12 个月逃亡潮 & 25 年拓殖拉力（1.4.9 精确参数）</strong>：当一块地刚被征服易主，原住民若在新宗主国沦为受歧视文化/宗教，最初 <strong>12 个月</strong>（<code>POST_CONQUEST_EMIGRATION_MONTHS = 12</code>）会按 <strong>2.0 倍外逃速率</strong> 向未被歧视的原母国逃亡；与此同时，新占领地会立刻对拥有者产生高达 <strong>3.0 倍</strong>（<code>1 + SETTLER_PULL_BASE 2.0</code>）的本土人口移民吸引力，在随后 <strong>25 年</strong>（<code>SETTLER_PULL_RAMP_YEARS = 25</code>）内线性衰减至正常值。</li>
  <li><strong>特许殖民地跨市迁徙</strong>：打破同市场限制，但<strong>严格限定只能从本国「核心（Core）」地点向海外特许殖民地输送人群</strong>。</li>
  <li><strong>{T('disease','疫病')} 爆发与 {T('disease_resistance','防疫能力')}</strong>：黑死病、天花等疫病先通过商路、边境与军队驻扎传播覆盖地点，再在各自结算周期按当前传播比例与死亡率消减人群及宫廷角色。防疫抗性上限为 60%（<code>MAX_INTRINSIC_DISEASE_RESISTANCE = 0.6</code>），高人口密度大都市在黑死病阶段死伤最为惨重（亦可用内阁/局势行动「躲避黑死病」止损）。</li>
</ol>
"""
            },
            {
                "id": "food-chain",
                "title": "03 · 三级粮仓流转架构与新手破产陷阱「自动买粮」",
                "en": "3-Tier Food Chain & Auto-Import Bankruptcy Trap",
                "html": f"""
<div class="callout warn"><strong>社区新手第一大经济黑洞：不明原因月度赤字暴涨！</strong><br>
许多玩家发现前一天还在正收益，入冬或连升几座城镇后突然每月支出暴增几十杜卡特。罪魁祸首几乎总是——<strong>缺粮省份正在自动按当前高企的市场价为你疯狂「购买食物」</strong>！</div>

<table class="data-table">
  <thead><tr><th>粮仓层级</th><th>来源与消耗口径</th><th>流转门槛与财政结算后果</th></tr></thead>
  <tbody>
    <tr><td><strong>L1 · {T('local_food','本地食物')}</strong></td><td>粮食 RGO 产出 + 闲置人口{T('subsistence_agriculture','自给农业')}（基数 0.8 效率远低于 RGO） − 当地人群月消耗</td><td><strong>正结余自动上缴省粮仓</strong>；城市/矿区等负产出地直接免费从同省其他产粮地抽调弥补</td></tr>
    <tr><td><strong>L2 · {T('provincial_food','省份食物')}</strong></td><td>汇总同省各地点净结余；供养所有本省居民与当前驻扎/过境本省的陆军部队</td><td>• 省储满仓（先留足 <strong>75%</strong> 本地缓冲区）且未受围攻：溢出部分自动<strong>向市场卖粮 → 变现入国库收入</strong>。<br>• 省储亏空且未受围攻：自动在省会所属市场<strong>花国库真金白银买粮（<code>buying_food</code>） → 直接记入国库支出</strong>！单月买/卖额度封顶为省粮仓总容量。</td></tr>
    <tr><td><strong>L3 · {T('market_food','市场食物')}</strong></td><td>汇集同市场所有盈余省与跨市场食物商品贸易的买进供给</td><td>仅当<strong>省储归零且市场亦买不到粮</strong>时触发 {T('starving','饥荒')}；当市场总储粮低于 <strong>25%</strong> 时，市民自动禁止往外市场倒卖粮食。</td></tr>
  </tbody>
</table>

<p>当一个省份进入 <strong>饥荒（<code>province_starving</code>）</strong> 时，全省略地点同步吃下毁灭性惩罚：本地人口增长 <strong>−5.0%/月</strong>、补给上限 <strong>−25%</strong>、移民吸引力 <strong>−1.0</strong>、降级速率 <strong>+50%</strong>、上层阶级容量 <strong>−50%</strong>，且该省在市场上生成的食物抢购需求权重大幅跃升至 <strong>1.5 倍</strong>。</p>
"""
            },
            {
                "id": "prosperity-devastation",
                "title": "04 · 繁荣度（Prosperity）与荒废度的不对称恢复",
                "en": "Prosperity, Devastation & Recovery Effort",
                "html": f"""
<p>每个地点的 {T('prosperity','繁荣度')} 在 <strong>−100% 到 +100%</strong>（<code>PROSPERITY_MIN=-1, PROSPERITY_MAX=1</code>）之间浮动：</p>
<ul>
  <li><strong>正值区间（繁荣 +0.1% ~ +100%）</strong>：在和平、高 {T('pop_satisfaction','人群满意度')}、{T('food_stockpile','粮食充裕')} 时缓慢自然增长。正繁荣持续推动本地 {T('development','发展度')} 上涨，并明显抬升移民吸引力吸引高产劳动力。</li>
  <li><strong>负值区间（荒废 −100% ~ −0.1%）</strong>：源于长期 {T('siege','围城')}、海军 {T('blockade','封锁')}、满意度崩盘、疫病或敌军 {T('loot','劫掠')}（<code>looted</code> 持续 <strong>12 个月</strong>，强施 −0.5%/月人口凋零、+0.10 繁荣衰减、−25% 发展增长、+5 最大损耗）。</li>
  <li><strong>战后恢复密钥</strong>：深度荒废依靠自然恢复极其缓慢，极度拖累战后十年税收。务必在停战第一时间指派一名高外交能力（DIP）内阁对重灾省执行 <strong>灾后恢复工作（<code>recovery_effort</code>）</strong>：直接赋予全省略地点 <strong>荒废恢复 +5.0%/月 + 人口增长 +0.10%/月</strong>，直到全省繁荣度全部回到 ≥0% 后自动结束！</li>
</ul>
"""
            },
        ],
        "discussion": {
            "title": "论坛实战讨论与排障 · 粮食破产自救与用工荒",
            "html": """
<ul>
  <li><strong>问：我的国家明明很多粮食省份，为什么还是月月有自动买粮账单？</strong><br>
  <strong>根因排查</strong>：EU5 的「省份（Province）」是独立买粮核对单位，且不同市场之间不能跨省调拨免费食物！如果市场总价被大城市群推高，哪怕你是全球产粮第一大国，你治下只要有一个驻满重矿产或城市的独立省份月度食物略亏，那个省就得按高昂的市场单价向市场掏钱买粮。<strong>对策</strong>：先扩建缺粮省内部自带的农村粮食 RGO（最省钱），再用贸易指令从周边便宜市场向本国主市场猛灌小麦/鱼/牲畜砸低市场粮食参考价，或开启财政界面的粮食调控考量。</li>
  <li><strong>问：打仗征兵和城市工厂哪边该让步？</strong><br>
  <strong>原则</strong>：千万不要拿人口稀少但高价值的矿区/都会去拉征召兵做无谓攻城损耗，每损耗 1,000 征召兵就等于永久抹掉了一座 1 级 RGO 的满编工人，在城市化极慢的内陆会直接卡死二十年发展！</li>
</ul>
"""
        },
        "quick_links": [
            ("75 种商品食物值全表", "ledgers.html#goods"),
            ("粮食与人口因果网络", "map.html#food_system"),
            ("省买粮与用工荒排障", "lab.html#troubleshoot"),
        ],
    },

    {
        "id": "ch03",
        "slug": "ch03-economy-market-trade.html",
        "num": "03",
        "pillar": "economy",
        "title": "生产工坊、市场贸易、关税与国家金融债务",
        "en": "Production, Markets, Trade Orders, Tariffs & Debt",
        "subtitle": "从第一单位商品价格波动、市场接入度切分到税基入库，看懂为什么高利润建筑却未充实国库，以及为何破产会留下百年信用黑洞。",
        "upstream": [
            ("地点人口与控制力", "ch01-territory-core.html#control", "定 RGO/工坊可用劳工，控制力定谁拿走利润"),
            ("王室力量份额", "ch05-estates-rebels.html#power-balance", "决定跨市场贸易利润中王室能分走多少成"),
            ("市场中心、港口与道路", "ch01-territory-core.html#urbanization", "塑造市场接入度及海陆物流折扣"),
        ],
        "engine": "计算 RGO/建筑产能与扩张波动，由市场接入度与贸易优势裁定供需分配及 5%/月调价，经由财富→税基→税率入国库，并在财政赤字时切换铸币、阶层贷、中央债券或破产清算。",
        "downstream": [
            ("阶层金库与私有投资", "ch05-estates-rebels.html#estate-wealth", "低控漏水财富与贷款利息喂肥阶层，引发私产建楼"),
            ("思潮随商路跨海扩散", "ch07-ages-colonial.html#ages-institutions", "从拥抱思潮市场进货顺带加快国内思潮传播"),
            ("国家信用与外交借贷资格", "ch10-diplomacy-subjects.html#diplo-capacity", "信誉度<30 遭列强拒贷；赔款过度制造通胀"),
        ],
        "redlines": [
            ("5% 趋近 / 月", "市价调整速率", "市场价每月向目标价靠近 5% 差额，无极端修正下限约 0.33×、上限 3×"),
            ("10/25/50%", "关税三档税率", "市场所有者可设三档进口/出口关税或 −10/−20/−35% 补贴操控流向"),
            ("50% 投产度", "工厂起飞分界", "新建建筑投产度超 50% 即获全产能及最高 +15% 额外生产效率加成"),
            ("−50 / 100年", "破产信用黑洞", "破产直扣 50 点信誉度（每年仅回 0.5 点），需整整百年方彻底抹平"),
        ],
        "sections": [
            {
                "id": "production-buildings",
                "title": "01 · 原产 RGO、建筑吞吐、「扩建波动性」与投产度",
                "en": "RGO, Buildings, Expansion Volatility & Establishment",
                "html": f"""
<p>任何地点的物质生产由两大引擎组成：每地自带一项先天 {T('raw_materials','原材料 RGO')}（每级雇佣 1,000 名 {T('rgo_pops','劳工或奴隶')}，开采零原料投入，受地貌/发展度及时代限制最高等级；少数普遍商品如黏土/石料/砂砾可不靠 RGO 靠建筑产出），以及玩家或阶层建造的各类 {T('building','建筑')}（通过切换 {T('production_method','生产方式 PM')} 调整原料配比与产率）。</p>
<ul>
  <li><strong>建筑盈利、停工与补贴机制</strong>：生产类建筑月利润 =（产出市价总值 − 原料市价成本）× {T('market_access','市场接入度')} × 雇佣比例 × (1 + {T('production_efficiency','生产效率')})。若亏损且未由政府开启 <strong>{T('subsidy','建筑补贴')}</strong>，建筑每月解雇 <strong>10%</strong> 工人直至自动停工；非生产类基础设施（如要塞、医院、大学、码头）则每月消耗市场商品并扣取政府 <strong>建筑维护费</strong>（受投入物价与王室力量影响）。</li>
  <li><strong>扩建波动性（{T('expansion_volatility','Expansion Volatility')}）防破产预览</strong>：扩建新一级工坊会同时抬高本地市场对投入原料的采购需求、压低对产成品的售价。UI 在扩建悬停时提前测算未来 6 个月价格滑落曲线——这是社区防踩坑「IKEA-maxxing（同一城市连点十级家具厂直接亏穿停产）」的关键仪表盘。</li>
  <li><strong>建筑投产度（{T('establishment','Establishment')}）机制</strong>：在投产爬坡规则启用时，新建筑须先积累超过 <strong>50%</strong> 投产度才能摆脱产能折扣并享满额运转（随后投产度越满越额外馈赠最高 <strong>+15%</strong> 生产效率，即超出部分 × 30%）；停工建筑每月倒扣投产度。</li>
</ul>
"""
            },
            {
                "id": "market-network",
                "title": "02 · 市场划分、接入度（1.4.9）与供需定价模型",
                "en": "Markets, 1.4.9 Market Access & Pricing Model",
                "html": f"""
<p>地点按距离、地形、道路、河流、同语言吸引力及拥有者控制力的 {T('protectionism','市场保护')} 自动划归最吸引它的 {T('market','市场中心')}。市场与你的外交从属分为四级：<strong>国内市场 / 交易市场（有外国商馆） / 国外市场 / 遥远市场（超贸易范围）</strong>。</p>
<div class="formula-box">
<strong>市场价格追赶方程：</strong> <code>本月价格变化 ΔP = 5% × (当前目标价 − 当前市场价)</code><br>
其中<strong>目标价</strong>由市场内 <code>有效供给</code> 与 <code>有效需求</code> 比率及当前时代的 {T('price_stability','物价稳定性')}（决定极度过剩与极度短缺时的价格上下限乘数，默认波动界限约 0.33× 至 3.0×）共同计算。<br>
<strong>1.4.9 市场接入度（Market Access）双重威力：</strong><br>
1. 接入度从 100% 起扣（普通地图距离每像素损失 0.5 百分点；1.4.9 将港口装卸效率基数上调至 <strong>+200%</strong>，且道路/河流运输加成在同路段分别选用各自最优值）；<br>
2. <strong>产出缩放与短缺优先权</strong>：原产出售价格与加工建筑吞吐量直接乘以接入度比例；更致命的是，当市场商品短缺时，<strong>高接入度地点优先购得库存</strong>，低接入度偏远厂直接断料停产！
</div>
"""
            },
            {
                "id": "trade-orders",
                "title": "03 · 贸易优势 vs 容量、贸易指令、关税与补贴",
                "en": "Merchant Power, Trade Orders, Tariffs & Subventions",
                "html": f"""
<p>建立跨市场商路时必须严密区分两个截然不同的数值：<strong>{T('merchant_capacity','贸易容量')}</strong> 决定你一次能搬多少吨货（随目标市场超出 {T('trade_range','贸易范围')} 的距离而加倍消耗容量并推高路费）；而同市场多国商人同时抢出口紧俏货时，严格按照各国在该市场的 <strong>{T('merchant_power','贸易优势')}</strong> 排名依次优先交割！（1.4.8 明确外国市民贸易在市场边境的关税与补贴按全额独立结算）。</p>
<ul>
  <li><strong>贸易指令（{T('trade_orders','Trade Orders')}）半自动托管利器</strong>：相比彻底交出大权给全自动贸易、或手动累死点几十条路线，更推荐玩家在市场面板为单一紧缺商品、食物模式或人群需求设置 <strong>贸易指令</strong>：划拨一块贸易容量并指定最低利润底线（默认 0.25 杜卡特），AI 每天自动跨市场重新分配容量锁定最优路线。</li>
  <li><strong>市场所有者的政策武器：关税（Tariffs）与补贴（Subventions）</strong>：只要你拥有市场中心，就可以在贸易政策面板<strong>按单种商品</strong>调整税率（轻 10%、中 25%、重 50%），或设置负关税 <strong>补贴（轻 −10%、中 −20%、重 −35%）</strong> 倒贴钱吸引外国商人把本国急缺的木材、铁、铁工具和粮食塞进本市场！交战期 AI 默认开启 −25% 粮食进口补贴与 +40% 粮食出口关税锁死粮荒。配合外交 <strong>{T('tariff_exemption','关税豁免')}</strong> 与属国 <strong>商人转移</strong>，可把贸易帝国利益最大化。</li>
  <li><strong>谁拿走贸易利润？</strong>：所有国家贸易净利润并不全归国库！按「<strong>王室力量份额</strong>」归王室直接进账，剩余份额全部按比例分发给贵族/教士/市民/平民等阶层金库（另附 {T('sound_toll','海峡通行费')} 10% 抽成直入海峡控制者高控地点）。{T('burgher_trade','市民贸易')} 则主要满足当地城市缺失货物与吃掉富余货，不占用你的国家商人。</li>
</ul>
"""
            },
            {
                "id": "wealth-to-treasury",
                "title": "04 · 从地点财富到国库的「五步漏斗」与税基比率体检",
                "en": "The 5-Step Wealth Funnel & Tax Base Ratio",
                "html": f"""
<div class="formula-box">
<strong>① 地点月财富</strong> = 当地 RGO 利润 + 建筑利润 + 归入该地的市民贸易贡献<br>
<strong>② 地点可税基（Tax Base）</strong> = 地点月财富 × 当前控制力 &nbsp;│&nbsp; <em>未受控财富 = 财富 × (1 − 控制力) → 直接进阶层口袋！</em><br>
<strong>③ 各阶层切分份额</strong> = 地点税基 × 各阶层在该地的财富份额（受自主权比例调节平民→贵族转移）<br>
<strong>④ 单阶层税款入库</strong> = 全国该阶层税基之和 × 阶层税率滑块 × 国家税收效率（前提：阶层满意度 ≥ 1%）<br>
<strong>⑤ 月度国库总平衡</strong> = 税款总和 + 贸易王室分成 + 铸币 + 属国贡赋/卖粮收入 − 各项维护 − 买粮账单 − 利息支出
</div>
<p>如何快速检查自己的经济是否患有「虚胖绝症」？查看经济总览的 <strong>{T('tax_base_ratio','税基比率')}（实收总税基 ÷ 全国{T('economical_base','经济基础')}）</strong>——记住：全国总财富、人口和属国规模都会把分母「经济基础」抬得很高（这决定你的科研开销基准、事件花费缩放和宫廷支出账单！），如果税基比率处于<strong>橙色（25%–50%）或红色（&lt;25%）</strong>，说明你看似 GDP 惊人、所有行政开支暴贵，实际却收不到多少真税钱！此时扩厂远不如先把高富区控制力救上来。</p>
"""
            },
            {
                "id": "finance-debt",
                "title": "05 · 铸币通胀、阶层贷款、中央政府债券与百年信誉度",
                "en": "Minting, Estate Loans, Government Bonds & Creditworthiness",
                "html": f"""
<p>面对国库赤字与应急建造需求，欧盟 5 提供截然不同的四类融资杠杆，切忌像前作一样无脑借贷破产：</p>
<table class="data-table">
  <thead><tr><th>融资渠道</th><th>获取方式与单笔规模</th><th>偿还方式与利息流向</th><th>核心风险与社区建议</th></tr></thead>
  <tbody>
    <tr><td><strong>市民紧急拨款</strong><br><code>ask_burghers_for_loan</code></td><td>阶层互动（市民金库 ≥10），最多无偿划拨其<strong>总存款 50%</strong>（上限 6×阶层贷额）</td><td><strong>无债务、零利息、不占贷款容量！</strong>仅降市民 15% 满意度（防御战减半）</td><td><strong>应急第一顺位</strong>！市民钱多时相当于王室白嫖无息救命款</td></tr>
    <tr><td><strong>{T('loan','阶层贷款')} / 外邦贷款</strong></td><td>本国单笔 = <code>0.5 × 经济基础</code>（最低 2），固定期限 <strong>60 个月</strong>，受国家 {T('loan_capacity','贷款容量')} 约束</td><td>每月付息直接进本国阶层金库（或外邦债主国）；到期享 <strong>3 月宽限期</strong>，缺钱被迫自动展期</td><td>按期还清加 <code>+2.0</code> 信誉；借新贷扣 <code>−0.5</code>；被迫展期每笔重扣 <code>−3.0</code>；向债主国宣战重罚 <code>−15.0</code></td></tr>
    <tr><td><strong>{T('government_bond','政府债券')}（央行）</strong></td><td>在首都建成<strong>{T('central_bank','中央银行')}</strong>后解锁发债；单笔 = <code>2.0 × 经济基础</code>（最低 10）</td><td><strong>无固定到期日、永不强制自动还款或展期</strong>；无限期支付 {T('bond_interest','债券利息')}（利息资金<strong>直接蒸发不进阶层腰包</strong>），直至你手动按面值回购</td><td>中后期发长期战争债券的神器，前提是确保税基增长速度压过永续付息</td></tr>
    <tr><td><strong>{T('minting','铸币')} 增印</strong></td><td>在财政面板拉动铸币滑块（滑块收益叠加黄金/白银 RGO 产量影响）</td><td>不产生利息债务，但持续推高全国 <strong>{T('inflation','通货膨胀')}</strong>（推高一切物价与建筑成本；不铸币时通胀自然缓慢消退，亦可用 ADM 内阁减通胀）</td><td>一般维持零净通胀（约轻微铸币与减免抵消），应急可短拉 2–3 年，防通胀突破 5% 以上滚雪球</td></tr>
  </tbody>
</table>
<p><strong>{T('creditworthiness','国家信誉度')}（0–100，中性均衡 50）与 {T('bankrupt','破产')} 代价</strong>：主权信用低于 <strong>30</strong> 时，外国银行和友好列强会拒绝向你借出任何新贷款。一旦现金枯竭无法续贷而被迫破产，除长达 <strong>5 年（60 个月）</strong> 的严重军事与经济衰弱期（<strong>稳定度 −50、控制力 −33%、通胀 −25%、25% 几率损毁现役部队、10% 几率建筑物降级</strong>）外，更会一次性重创 <strong>−50 点信誉度</strong>——而这个破产污点每年仅以 <code>+0.5 点/年</code> 速度清洗，换言之<strong>破产一次需要整整 100 年才可彻底恢复如初！</strong></p>
"""
            },
        ],
        "discussion": {
            "title": "论坛实战讨论与排障 · 为什么我的经济体越扩大越穷？",
            "html": """
<ul>
  <li><strong>陷阱一：经济基础（Economical Base）膨胀诅咒</strong><br>
  许多扩张狂魔吞下一大片 5% 控制力的穷乡僻壤或海量不值钱属国、甚至无节制接纳毫无用处的外国思潮（每接纳 1 个思潮推高 +6.6% 经济基础！），结果「经济基础」账面虚胖翻倍，导致宫廷支出、稳定度投入、事件索要金币、甚至连内阁/建筑基准价全水涨船高——实际手里可征税基根本没涨！应对原则：没钱养或控制力拉不上去的边缘低价省，果断建属国或精简发展核心高控省。</li>
  <li><strong>陷阱二：把工坊全塞进 40% 市场接入度的偏远镇</strong><br>
  在同一个市场下，40% 接入度的工厂不仅产出打四折，更会在铁、煤炭、羊毛一缺货的瞬间最先遭市场断供停工并掉光投产度。要重资产堆工厂，先围绕着市场中心附近高接入地点（或者先在重要节点另起一个新市场中心）集聚建造。</li>
</ul>
"""
        },
        "quick_links": [
            ("75 种商品图标与数值全典", "ledgers.html#goods"),
            ("地点财富→税基实时模拟器", "lab.html#calc"),
            ("税基与信誉因果星图", "map.html#wealth_tax"),
        ],
    },

    {
        "id": "ch04",
        "slug": "ch04-government-cabinet.html",
        "num": "04",
        "pillar": "state",
        "title": "政府、官僚固化、人物互动与内阁 81 行动全景",
        "en": "Government, Bureaucracy, 34 Character Actions & 81 Cabinet Actions",
        "subtitle": "内阁席位是治国最稀缺的生产力工具，官僚机构隐藏百年固化代价，而 34 项人物互动决定你是稳固继承还是陷入摄政危局。",
        "upstream": [
            ("王室力量与各阶层力量", "ch05-estates-rebels.html#power-balance", "王室份额增减内阁效率，任命阶层人物增加其+25%政治力量"),
            ("国家经济基础", "ch03-economy-market-trade.html#wealth-to-treasury", "直接缩放官僚机构每月的金币维护账单"),
            ("时代与革新研发", "ch07-ages-colonial.html#ages-institutions", "逐步解锁额外内阁席位、改革槽位与地区级内阁行动"),
        ],
        "engine": "以政体专属政府力量与 17 对价值观塑造顶层方向，权衡官僚部门经费与固化风险，调度宫廷儿童培育与 34 项角色互动，并将稀缺内阁大臣委派到最迫切的 81 项行动上。",
        "downstream": [
            ("疆域整合与高控提速", "ch01-territory-core.html#integration-core", "MIL 内阁消化征服地；ADM 内阁救低控制富省"),
            ("灾后恢复与同化转正", "ch02-population-food.html#prosperity-devastation", "DIP 内阁清理荒废度并加快 50% 核心文化转换"),
            ("外交与内战局势压制", "ch05-estates-rebels.html#rebellions", "镇压叛乱运动、降厌战、压通胀并塑造外交声誉"),
        ],
        "redlines": [
            ("100 储存上限", "政治影响力上限", "由君主与内阁平均能力产出（空席按 0 计），超过 100 溢出作废"),
            ("10 年固化期", "内阁首脑锁定", "大臣在阁满 10 年方能晋升首相（效率 +25% / 特质翻倍），晋升后不可免职"),
            ("3岁启蒙/16成年", "角色教育时间窗", "3 岁设教育焦点（55%/月判定成长），16 岁成年方能领兵、入阁或结婚"),
            ("每 100 年一阶", "官僚固化陷阱", "官僚部门经费不足时正面消失仅剩负面；每百年加深固化并抬高裁撤重价"),
        ],
        "sections": [
            {
                "id": "government-power",
                "title": "01 · 五类国家形态、五大政体与核心政治指标",
                "en": "Country Types, Government Types & Core Political Metrics",
                "html": f"""
<p>在 EU5 中，“国家怎么存在”与“国家怎么统治”是两个正交维度：</p>
<ul>
  <li><strong>五类国家存在形态</strong>：① <strong>{T('settled_country','定居国家')}</strong>（依地点存续）；② <strong>{T('extraterritorial_country','地产/建筑国家')}</strong>（靠跨国建筑存续，如银行家族、修会、汉萨商业行会）；③ <strong>{T('society_of_pops','游群社会')}</strong>（靠游牧或部落人群存续）；④ <strong>{T('army_based','兵团国家')}</strong> 与 ⑤ <strong>{T('navy_based','舰队国家')}</strong>（可拥有领土，但赖以维系的陆军或舰队覆灭即告灭亡）。</li>
  <li><strong>五大政体与专属 {T('government_power','政府影响力')}（0–100）</strong>：君主制 → <strong>{T('legitimacy','正统性')}</strong>；共和国 → <strong>{T('republican_tradition','共和传统')}</strong>（连任消耗传统，跌破危险线可能变独裁）；神权制 → <strong>{T('devotion','奉献度')}</strong>；草原游牧 → <strong>{T('horde_unity','游牧团结')}</strong>（靠劫掠省份维持）；部落 → <strong>{T('tribal_cohesion','部落凝聚力')}</strong>。</li>
  <li><strong>切忌混淆三大政治数值</strong>：<strong>政府影响力（0–100）</strong> 衡量统治合法性；<strong>{T('political_influence','政治影响力')}（0–100 上限）</strong> 是执行改革/设法律/换内阁/授特权的月度行动点数（统治者能力 + 内阁平均能力月产，且存量每 1 点微弱加快全国阶层满意度回升）；<strong>{T('stability','稳定度')}（−100 至 +100）</strong> 向 0 衰减，负责承担宣战、撤特权与换法律代价。</li>
</ul>
"""
            },
            {
                "id": "societal-values",
                "title": "02 · 17 对社会价值观轴线（−100 至 +100）与惯性平衡",
                "en": "17 Societal Values & Inertia",
                "html": f"""
<p>{T('societal_value','社会价值观')} 共有 17 对双极轴线，构成一个国家从政治集权到经贸军事路线的底层指纹。每一对都在 <code>−100</code>（左端）至 <code>+100</code>（右端）之间缓慢滑动——受法律、政策、阶层特权、事件与外交内阁行动的月度推动力牵引，同时受<strong>系统惯性阻力（100）</strong>限制：推得越靠近极点，维持或再进所需的月度推动力呈指数级增大。高级 {T('government_reform','政府改革')} 与政体转换常严格要求特定轴线跨过 <strong>±50</strong>（或君主转共和需财阀 ≥95）门槛。</p>
<p>核心实战举例：<strong>中央集权 vs 地方分权</strong>（集权极点给 +50% 王室力量、+20% 邻近传播、+33% 吞并速度，但给所有属国 −20 忠诚；分权极点反给属国 +30 忠诚、+5% 阶层满意度均衡）；<strong>守旧 vs 创新</strong>（创新极大降低 −50% 接纳思潮花费并 +10% 最大识字率）；<strong>陆权 vs 海权</strong>（直接重塑水陆邻近度衰减方向）。（全 17 对数值详见「数据速查典 → 社会价值观」）。</p>
"""
            },
            {
                "id": "bureaucracy",
                "title": "03 · 法律、政府改革与「官僚部门固化（Entrenchment）」双刃剑",
                "en": "Laws, Reforms & Bureaucracy Entrenchment",
                "html": f"""
<p>一国通常初始仅有 <strong>1 个</strong>普通 {T('government_reform','政府改革')} 槽位（只能持有 1 项决定核心特征的「{T('major_reform','主要改革')}」）；改革、{T('law','法律')} 下的 {T('policy','政策')} 若带有实施期，效果会随实施进度渐进生效，切记更换政策基准代价通常消耗高达 100 稳定度（除非走议会途径免稳换法）。</p>
<p><strong>极易踩坑的新增系统：60 种{T('bureaucracy','官僚部门')}与{T('entrenchment','固化度')}</strong>：</p>
<ul>
  <li>政府可通过行动（<code>add_bureaucracy_action</code>）建立如「税务委员会」、「法典院」等行政分支部门，它们均包含<strong>常驻修正、正面修正、负面修正</strong>三组效果。</li>
  <li><strong>经费切换正负</strong>：你在财政「官僚部门维护花费」上投入百分比 <code>m</code>（0–100%）时，<strong>正面修正按 <code>m</code> 比例生效，而负面修正按 <code>1 − m</code> 比例生效！</strong>一旦缺钱砍预算，好效果消失、腐败官僚的纯负面 Debuff 立刻全面爆发。</li>
  <li><strong>百年固化代价</strong>：官僚部门存活得越久，其<strong>固化度</strong>随每 <strong>100 年一阶（<code>BUREAUCRACY_ENTRENCHMENT_YEARS_PER_PHASE = 100</code>）</strong> 稳步爬坡，同时按经济基础膨胀每月维护账单、激怒不同阶层，并让你日后调用「移除官僚部门」废除该冗余机构的政治和金币成本呈倍数飙升！</li>
</ul>
"""
            },
            {
                "id": "characters-interactions",
                "title": "04 · 统治者能力、儿童培育与 34 项角色互动全景",
                "en": "Character Abilities, Education & 34 Character Interactions",
                "html": f"""
<p>统治者个人三维能力直接为全国家带来可观全局光环：<strong>每 1 点 ADM</strong> = <code>+0.25%</code> 王室力量 + <code>+0.2%</code> 建造效率；<strong>每 1 点 DIP</strong> = <code>+0.05</code> 外交声誉 + <code>+0.1%</code> 阶层满意度均衡；<strong>每 1 点 MIL</strong> = <code>+0.1%</code> 陆海军士气。所有皇室后代自 <strong>3 岁</strong> 开启教育（平衡教育全能力 +0.50；偏科教育通用 +0.25 + 指定科 +0.75；每月有 55% 几率随天赋提升点数），<strong>16 岁</strong> 成年正式可任职。</p>

<table class="data-table">
  <thead><tr><th>互动领域</th><th>关键角色互动（共 34 项，详见速查典）</th><th>核心底层机制与社区实战避坑</th></tr></thead>
  <tbody>
    <tr><td><strong>王位与继承控制</strong></td><td><strong>指定为继承人</strong> / <strong>赋予女性继承权（完人）</strong> / <strong>誓发终身愿（出家）</strong> / <strong>退位</strong> / <strong>罢免王公</strong> / <strong>切腹自尽</strong></td><td>• 生了高能女儿却受限传男法？用「赋予女性继承权（<code>prefection</code>）」授她<strong>法定男性（<code>legal_male</code>）</strong>身份直接继承！<br>• 废柴继承人逼他 <code>take_the_vows</code> 强制进教士阶层即可剥夺继承资格；退位基础需继承人存在且 40 岁后每岁降 0.02 花费倍率；共和国负稳定度时「罢免王公」免扣共和传统。</td></tr>
    <tr><td><strong>婚姻与宗族维持</strong></td><td><strong>与贵族结婚（<code>marry_noble</code>）</strong> / <strong>与出身卑微者结婚</strong> / <strong>封为贵族（<code>ennoble</code>）</strong> / <strong>将外廷儿童接回本宫廷</strong></td><td>AI 对年轻未婚君主留了直到 <strong>30 岁</strong> 的外交联姻宽限期——不想拖到断代摄政，及早手点「与贵族结婚」配对本国贵族防外国篡统；「封为贵族」可把低出身神童在指定地点建起全新忠诚贵族宗族！</td></tr>
    <tr><td><strong>军政与地方总督</strong></td><td><strong>晋升内阁首脑</strong> / <strong>授予内阁权利</strong> / <strong>接手地区防务（<code>assume_fort_command</code>）</strong> / <strong>任命地方/家族总督</strong> / <strong>大翻译官</strong></td><td>「<strong>接手地区防务</strong>」令目标角色在 10 年内按 ADM 加强目标地区防务并兼领军衔与入阁权；「授予赐封总督」可把远疆省交王室成员治领（分死后归还、流放剥夺继承权、历练 10 年涨属性三种路线）。</td></tr>
    <tr><td><strong>惩戒与宫廷创作</strong></td><td><strong>驱逐（<code>banish_character</code>）</strong> / <strong>处决（<code>execute_character</code>）</strong> / <strong>赦免</strong> / <strong>委托艺术品</strong> / <strong>遣散艺术家</strong> / <strong>邀请骑士团</strong></td><td>连续使用驱逐或处决会在 <strong>2 年内叠加 +2.50 / +5.00 政府力量递增惩戒</strong>；若处决外国人物会立即承受对方 <strong>−200 外交好感</strong>。</td></tr>
  </tbody>
</table>
"""
            },
            {
                "id": "cabinet-actions",
                "title": "05 · 内阁席位、内阁首脑与 81 项内阁行动三系总表",
                "en": "Cabinet Seats, Head of Cabinet & 81 Cabinet Actions",
                "html": f"""
<p>国家开局通常仅拥有 <strong>2 个内阁席位</strong>（帝国等级 +1 席，后期革新与国家修正扩容），每次换人消耗 20 政治影响力。把 1 名在阁任职满 <strong>10 年</strong> 的大臣提拔为 <strong>{T('head_of_the_cabinet','内阁首脑')}</strong>，会令其获得 <strong>+25% 内阁效率</strong> 且其<strong>内阁特质效果翻倍（+100%）</strong>，还会依照他的出身阶层激活全国修正（代价是此后该大臣终身不可从内阁踢出或领兵打仗）。</p>
<table class="data-table">
  <thead><tr><th>能力系别</th><th>最常用通用核心内阁行动（完整 81 项见速查典）</th><th>底层关键数值与最佳实践顺序</th></tr></thead>
  <tbody>
    <tr><td><strong>行政系 (ADM)</strong></td><td><strong>提升省份/地区控制力</strong>、<strong>发展省份</strong>、<strong>促进人口升级（<code>pop_promote_action</code>）</strong>、<strong>降低通胀</strong>、<strong>研究思潮（<code>study_institutions</code>）</strong>、<strong>鼓励迁移 / 拓殖边疆</strong></td><td>• <code>increase_control_province</code>：直接给予省内地点 <strong>最大控制 +10%</strong>、<strong>月控 +1.0%</strong>，UI 默认贴心按「未受控财富」从高到低排好最值钱的省份！<br>• <code>reduce_inflation</code>：每月稳定削减 −0.025% 通胀（乘以效率与 ADM）；<code>study_institutions</code> 定向把思潮拉进人口最密的中心省突破 20% 门槛。</td></tr>
    <tr><td><strong>外交系 (DIP)</strong></td><td><strong>灾后恢复工作（<code>recovery_effort</code>）</strong>、<strong>安抚阶层</strong>、<strong>推广文化 / 同化地区</strong>、<strong>推广宗教</strong>、<strong>统合文化组</strong>、<strong>降低厌战度</strong>、<strong>改变社会价值观</strong>、<strong>反间谍 / 挑拨属国</strong></td><td>• <code>recovery_effort</code>（可多名并派）：对带负繁荣（荒废）省份加 <strong>+5% 荒废恢复</strong> 与 <strong>+0.1% 人口增长</strong>，直至全省略地点恢复至 ≥0% 自动收工。<br>• <code>promote_culture</code> / <code>assimilate_area</code>：专门强推主流文化迈过 50% 核心门槛。</td></tr>
    <tr><td><strong>军事系 (MIL)</strong></td><td><strong>整合省份（<code>integrate_province</code>） / 整合地区（<code>integrate_area</code>）</strong>、<strong>稳定国家（<code>stabilize_country</code>）</strong>、<strong>强化政府</strong>、<strong>弹压叛乱（<code>rebel_crackdown</code>）</strong>、<strong>绥靖民众</strong></td><td>• <code>integrate_province</code>（可多人并行）：唯一能把 <code>conquered</code> 变成 <code>integrated</code> 的行动（+100% 整合速率），中期革新升级为一次性整合全「地区 Area」。<br>• <code>stabilize_country</code>：零金币开支拉高正稳定度，极适合缺钱大国省下财政稳定投入滑块。</td></tr>
  </tbody>
</table>
"""
            },
        ],
        "discussion": {
            "title": "论坛实战讨论与排障 · 如何解决「内阁席位严重不够用」？",
            "html": """
<ul>
  <li><strong>打完一场大胜后，2–3 个内阁席位该怎么排优先级？</strong><br>
  <strong>社区通用黄金顺序</strong>：① <strong>极度高价值核心省被战火打成荒废（负数）→ 先丢 1 名高 DIP 大臣去「灾后恢复」</strong>，只要几月即可清掉荒废让税基与人口止血恢复；② <strong>核心高产低控制直辖省 → 挂 1 名高 ADM「提升控制力」</strong>（常驻直接额外加 +10% 最大控制上限非常恐怖）；③ <strong>高人口、同文化或高价值的新占边省 → 排高 MIL 「整合省份」</strong>；④ <strong>烂尾穷省与小碎地 → 直接释放给省份属国，别拿金贵的内阁席位陪葬</strong>（连 AI 自己都在代码里写死了「每名内阁最多同时消化 4 个未整合省，超出即自动切分属国」）。</li>
</ul>
"""
        },
        "quick_links": [
            ("81 项内阁行动三系筛选", "ledgers.html#cabinet_actions"),
            ("34 项角色互动全列表", "ledgers.html#character_interactions"),
            ("17 对社会价值观与 60 官僚部门", "ledgers.html#societal_values"),
        ],
    },

    {
        "id": "ch05",
        "slug": "ch05-estates-rebels.html",
        "num": "05",
        "pillar": "state",
        "title": "阶层博弈、12 项直接互动、议会与叛乱检定",
        "en": "Estates, 12 Direct Interactions, Parliament & Rebellions",
        "subtitle": "不仅要拆解「王室力量」的算法、特权的满意度公式与阶层私建偷钱，更要掌握 12 项主动互动键以及叛乱爆发瞬间的要塞守军倒戈检定。",
        "upstream": [
            ("低控制未受控财富与人口", "ch01-territory-core.html#control", "地点控制越低，越把地方财富与政治点让给阶层"),
            ("统治者 ADM 与集权价值观", "ch04-government-cabinet.html#societal-values", "直接缩放王室力量占比"),
            ("宗教容忍、文化与消费物价", "ch02-population-food.html#population-base", "联合阶层满意度共同决定底层人群是否逼破造反线"),
        ],
        "engine": "在同一批人口上对比王室与五大阶层的政治力量，使用 12 项直接互动与 180 天议会收割税、兵与紧急资金，同时严防特权撤销或满意度崩溃引发叛军夺城与私兵倒戈。",
        "downstream": [
            ("国家实收税率与贸易分成", "ch03-economy-market-trade.html#trade-orders", "王室份额吃满贸易大头；<1% 满意直接拒绝交税"),
            ("陆海军征召兵供给闸门", "ch08-military-combat.html#force-types", "任一阶层满意度 <25% 直接关停征召动员"),
            ("内阁效率与议会基础支持", "ch04-government-cabinet.html#cabinet-actions", "王室份额一半直算议会底票，且显著加速内阁行事"),
        ],
        "redlines": [
            ("< 25% 满意度", "拒出征召兵红线", "阶层满意度低于 25% 立刻拒绝交出征召兵；低于 1% 拒绝交税"),
            ("75% 控制力", "私建拆建攻防线", "阶层只在 <75% 控制地造私产；王室需 ≥75% 才可直接手拆（或用削减行动）"),
            ("防御战减半", "绝境互动超级杠杆", "防御性战争中所有阶层绝境求助的政治花销与满意度下跌全部折半（×0.5）"),
            ("5,000 人 / 80%", "叛乱两重关键界碑", "<5,000 人只刷小规模地方惩罚；进度超 80% 未处置使要塞守军忠诚大跌 −20"),
        ],
        "sections": [
            {
                "id": "power-balance",
                "title": "01 · 王室力量与阶层力量的「双轨制」精密算法",
                "en": "How Crown Power vs Estate Power Works",
                "html": f"""
<p>许多新手困惑：「为什么游戏里有王室力量，却没有王室人口？」答案在于底层采取<strong>同源双算机制</strong>——国家每一组实际人口 <code>P</code>（贵族、教士、市民、平民等）：</p>
<div class="formula-box">
<strong>① 为所属阶层贡献点数：</strong> <code>(该人口 ÷ 1,000) × 所属阶级每千人政治权数</code>（如贵族每千人权数远高平民百倍；受歧视文化人口不贡献任何力量）× 本地/特权/任职修正。<br>
&nbsp;&nbsp;&nbsp;&nbsp;<em>特别警告：把某一阶层出身的大臣塞入内阁，或指派其担任将领指挥军团，直接为该阶层提供 <code>+25%</code> 基础力量加成！</em><br>
<strong>② 为王室贡献点数：</strong> <strong>同一批居民</strong>同时以 <code>(该人口 ÷ 1,000) × 该地控制力 × 王室明细基数</code> 为王室计数，再叠加王室宗室成员亲自入阁/领兵以及中央集权、统治者 ADM（每点 +0.25%）等全国修正。<br>
<strong>③ 最终王室力量份额：</strong> <code>王室份额 = 王室最终点数 ÷ (王室最终点数 + 所有阶层最终点数之和) × 100%</code>
</div>
<p>这个「王室份额」就是全内政的总阀门：它的<strong>一半（<code>×0.5</code>）直接充当议会基础支持度</strong>；贸易利润中王室能进国库的份额也以它衡量；并且大幅拔高全局 <strong>内阁效率</strong> 与税收潜力。</p>
"""
            },
            {
                "id": "estate-wealth",
                "title": "02 · 阶层金库、4 倍造价私有建筑与「阶层建筑」清除术",
                "en": "Estate Gold Pools, Private Buildings & Regiments",
                "html": f"""
<p>各阶层并非纸面符号，每个阶层都有自己的独立真金白银账户（{T('estate_tax_base','阶层税基')} 免税余款 + 低控制地点偷走的 {T('uncontrolled_wealth','未受控财富')} + 阶层贷款收回的利息 + 玩家贿赂款）。阶层用这些资金满足消费后，若月度 <strong>{T('wealth_impact','财富影响（收入÷支出）')}</strong> 高于 100% 且心情好，会<strong>花 4 倍价格（<code>ESTATE_MAX_PRICE_MULTIPLIER = 4</code>）帮你修建赚钱 RGO、道路与公共建筑</strong>；</p>
<p>但一旦阶层陷入高消费危机或低满意度，他们会<strong>停止造公共经济楼，转向专挑控制力低于 75% 的边地狂造「{T('estate_building','阶层建筑')}」</strong>——不产任何国家税收，专门给你扣各种全国 Debuff 并疯狂膨胀他们的阶层政治力量！</p>
<ul>
  <li><strong>阶层私人团（{T('private_regiment','Private Regiments')}）</strong>：一旦拥有《贵族私军》等特权且阶层金库大于维护费 2 倍，阶层会自掏腰包招私人部队，王室战时可调用「征用私兵」借来用（不掉你的人力池！），但若该阶层触发内战，<strong>这些借来的私人团会立刻在战场上就地倒戈</strong>。</li>
  <li><strong>铲除阶层建筑的三把手术刀</strong>：① 把当地控制力推到 <strong>≥ 75%</strong> 手动强拆（每拆扣目标 −20% 满意度）；② 通过议会特殊议程拆除；③ 最干脆的直接互动——点开阶层菜单里的 <strong>「削减阶层力量（<code>perform_reduction</code>）」</strong>！</li>
</ul>
"""
            },
            {
                "id": "estate-interactions",
                "title": "03 · 核心补全：12 项阶层直接互动与绝境求助全览",
                "en": "Complete Guide to Estate Actions & Emergency Actions",
                "html": f"""
<div class="callout"><strong>机制补白声明</strong>：阶层除了发特权、调税率与开议会外，玩家还能在阶层侧边面板随时点击<strong>常规主动互动</strong>与战时危急 <strong>绝境行动（Emergency Actions）</strong>——其中「防御战全部开销与满意度惩罚减半」以及「向市民无息借钱实为无债直接抽水」是破局神技。</div>

<table class="data-table">
  <thead><tr><th>类别 / 行动名</th><th>前置与目标条件</th><th>金币 / 政治消耗与惩罚</th><th>实际收益与冷却期</th></tr></thead>
  <tbody>
    <tr><td><strong>贿赂阶层</strong><br><code>bribe_estate</code></td><td>阶层税基 <code>&gt; 0.01</code> 且国库足够</td><td>国库扣除 <strong>目标税基 × 12</strong> 金币（全额转入该阶层金库）</td><td>目标满意度立即 <strong>+10%</strong>（无冷却，极速救急 25% 征召/1% 征税线！）</td></tr>
    <tr><td><strong>削减阶层力量</strong><br><code>perform_reduction</code></td><td>目标拥有阶层建筑、力量 <code>&lt; 90%</code> 且当前满意度 <code>&gt; 50%</code></td><td>该阶层满意暴扣（受拆楼惩罚倍率）；同时没收其 <strong>税基 × 2</strong> 金币进国库</td><td>按控制从低到高批量摧毁最多 <code>min(20, 2 + 地点数÷20)</code> 座阶层私产建筑（大教堂除外），无冷却</td></tr>
    <tr><td><strong>向阶层出售艺术品</strong><br><code>sell_work_of_art_to_estates</code></td><td>保有非无价之宝、非帝国御宝的闲置艺术品</td><td>永久移除/销毁该艺术品</td><td>国库立即进账该艺术品估值 <strong>60%</strong> 现金</td></tr>
    <tr><td><strong>征用私兵</strong><br><code>press_estate_private_regiments</code></td><td>授有私军特权且目标阶层存有私人团</td><td>正统性 <strong>−10</strong>、极高政治影响力（<strong>−15</strong>）</td><td>强征阶层私人团并入国家陆军参战（独立 <strong>3 年</strong> 冷却）</td></tr>
    <tr><td><strong>要求扩大征召</strong><br><code>ask_for_extra_levies</code></td><td>任一税基 <code>&gt; 0.01</code> 之阶层</td><td>25 政治 + 缩放金币；满意度 <strong>−12.5%</strong>（<strong>防御战耗费与扣满减半 → −6.25%</strong>）</td><td>12 个月全军 <strong>征召兵规模 +15%</strong>（独立 5 年冷却）</td></tr>
    <tr><td><strong>征收特别税</strong><br><code>extraordinary_taxes</code></td><td>税基 <code>&gt; 0.01</code>（<strong>天主教教士因教规免税禁用</strong>）</td><td>25 政治影响力；满意度 <strong>−12.5%</strong>（<strong>防御战耗费与扣满减半 → −6.25%</strong>）</td><td>12 个月该阶层 <strong>最高税率上限 +10%</strong>（独立 5 年冷却）</td></tr>
    <tr><td><strong>召开紧急议会</strong><br><code>call_emergency_parliament</code></td><td>交战中且常规议会处在 59 个月冷却期</td><td>正统性 −10、政治影响力 −10</td><td>无视冷却立即重开议会选定议案（独立 5 年冷却）</td></tr>
    <tr><td><strong>绝境 · 请求神职者支持</strong><br><code>ask_clergy_for_legitimacy</code></td><td><strong>教士阶层</strong>（每位君主限用 <strong>1 次</strong>）</td><td>25 政治 + 金币（防御战减半）；教士满意 <strong>−7.5%</strong></td><td>立即获 <strong>+15 正统性</strong>（五大专属求助共享 5 年冷却）</td></tr>
    <tr><td><strong>绝境 · 请求贵族使节</strong><br><code>ask_nobility_for_diplomats</code></td><td><strong>贵族阶层</strong></td><td>30 政治 + 金币（防御战减半）；贵族满意 <strong>−10%</strong></td><td>立即获 <strong>+5 名外交官</strong>（共享 5 年冷却）</td></tr>
    <tr><td><strong>绝境 · 请求紧急拨款</strong><br><code>ask_burghers_for_loan</code></td><td><strong>市民阶层</strong>（市民金库存款 <code>≥ 10</code> 金币）</td><td>40 政治（防御战减半）；市民满意 <strong>−15%</strong></td><td>从市民金库直接划转最多 <strong>市民金库 50%</strong>（上限 6×阶层贷额）进国库——<strong>不记债务、无利息！</strong></td></tr>
    <tr><td><strong>绝境 · 向平民求助</strong><br><code>ask_commoners_for_stability</code></td><td><strong>平民或齐米（Dhimmi）</strong></td><td>40 政治（防御战减半）；目标满意 <strong>−15%</strong></td><td>立即获 <code>10 × (1 + 0.005 × 农奴自由轴)</code> 稳定度（<strong>5 ~ 15 点</strong>）</td></tr>
    <tr><td><strong>绝境 · 号召部落武装</strong><br><code>ask_tribes_for_manpower</code></td><td><strong>部落或哥萨克</strong>（且国家月人力 <code>&gt; 0</code>）</td><td>15 政治 + 金币（防御战减半）；目标满意 <strong>−20%</strong></td><td>立即获相当于 <strong>12 个月全国月人力</strong> 的现役人力</td></tr>
  </tbody>
</table>
"""
            },
            {
                "id": "parliament",
                "title": "04 · 特权冲击公式与议会 180 天博弈规则",
                "en": "Privileges Formula & Parliament Mechanics",
                "html": f"""
<p>阶层 {T('estate_privilege','特权')} 不是简单的“加减属性列表”，它同时深刻改变该阶层力量、满意度均衡点（25% 基础起点）与社会价值观导向。</p>
<div class="formula-box">
<strong>特权授予与撤销的满意度骤变公式（<code>00_defines.txt</code>）：</strong><br>
设一项特权给予目标阶层的长期满意度均衡点加成为 <code>Δ</code>：<br>
• <strong>授予时</strong>（基价 20 政治）：目标阶层当前满意度立刻增加 <code>+3 × Δ</code>；而其余阶层受嫉妒反噬变化 <code>−0.5 × (3 × Δ)</code>。<br>
• <strong>撤销时（极度危险！）</strong>：目标阶层立刻重摔 <code>−25% − 3 × Δ</code>，外加消耗按其阶层权势缩放的大笔稳定度！<br>
&nbsp;&nbsp;<em>算例：撤掉一项 +10% 均衡的特权，该阶层瞬间狂掉 25 + 30 = <strong>55%</strong> 满意度——几乎必然将其从 70% 一脚踹进 15%，同时触发「<25% 拒出征召」与「内战急行军」！</em>
</div>
<p><strong>{T('parliament','议会')}周期与过关算法</strong>：常规国家两次议会间隔须超过 <strong>59 整月</strong>，会期 <strong>180 天</strong>（议会地点如被占领直接流产），表决门槛为 <strong>50% 支持度</strong>。开会起始支持度 = <strong>王室力量份额 × 0.5 + 提案阶层力量份额（若非常忠诚）</strong>。除了通过核心议案（如大笔税收、扩大征兵、低代价修法/拿 CB）外，议会还可用支持度花销去强行换法律避开 −100 稳定度重罚。</p>
"""
            },
            {
                "id": "rebellions",
                "title": "05 · 叛乱进度、5,000 人分水岭、要塞守军倒戈与三项干预按钮",
                "en": "Rebellion Thresholds, Rebel Fort Loyalty & Interventions",
                "html": f"""
<p>底层人群的 {T('pop_satisfaction','人群满意度')} 从 <strong>20% 基数</strong> 起算，叠加所属阶层贡献 + 文化地位与好感 + 宗教容忍 + 消费品涨价/缺货 − 动乱度与分离主义。当某群人口满意度过低（默认 &lt;20% 加入、&gt;35% 退出），就会按非整合度、低控制力与阶层力量共同推高全国或地方 {T('rebel_movement','叛乱运动')} 月度进度。</p>
<ul>
  <li><strong>进度满 100% 的两极分支（<code>MIN_REBEL_POP_SIZE_THRESHOLD = 5</code>）</strong>：若起事时支持该运动的真实人口<strong>不足 5,000 人</strong>，则不会拉起叛军建国交战，只会变成 <strong>小规模叛乱（<code>minor_revolt</code>）</strong>（施加当地繁荣与控制力各 −0.5%/月的衰减修正并安抚人群 +10%）；只有满 <strong>≥ 5,000 人</strong> 时才爆发真正的独立起义或全国内战！</li>
  <li><strong>叛军爆发瞬间「要塞守军忠诚检定」公式</strong>：内战或叛乱起事时，范围内每一座建有要塞的地点都会投一次 D100 决定守军忠于朝廷还是叛变开门（保底 <strong>10%</strong>、封顶 <strong>90%</strong>）：
    <div class="formula-box">
      <code>要塞留存朝廷忠诚概率(%) = 50(基础) + 30 × 阶层满意度 + 10(本地叛乱度&lt;3) + 10(为主流文化) + 10(为国教) − 15(守军阶层与叛军同类) − 20(叛乱进度已超过 80%!)</code>
    </div>
  </li>
  <li><strong>三项叛乱干预按键</strong>：① <strong>收买叛军（<code>negotiate_rebels_buy_off</code>）</strong> 花钱压下进度；② <strong>同意要求（<code>negotiate_rebels_accept_demands</code>）</strong> 妥协换停战；③ <strong>激起反叛（<code>provoke_rebels</code>）</strong>——社区高玩最常用的神技：在进度跨过 <strong>80% 要塞减分线之前</strong> 提前把军阵摆在关键要塞与山头主动点引爆，全歼反贼后直接彻底消弭隐患！</li>
</ul>
"""
            },
        ],
        "discussion": {
            "title": "论坛实战讨论与排障 · 如何安全拆除开局贵族恶性特权？",
            "html": """
<ul>
  <li><strong>如何避免刚撤一个特权就被贵族拉起全国大内战？</strong><br>
  <strong>三步排雷顺序</strong>：① <strong>先把目标阶层满意度喂到接近 90–100%</strong>（提前先给一个便宜不占力量的小特权过渡，或连续执行两次「安抚阶层 + 贿赂阶层」拉满缓冲）；② <strong>用正统性/集中化先压低贵族力量份额</strong>——记得：把贵族大臣踢出内阁与战将岗瞬间就能削掉其 25% 基础权数，减少撤特权的稳定度账单；③ <strong>绝对不要卡在 80% 以上叛乱进度撤楼！</strong>宁可利用「激起反叛」把早已部署好大军压顶的叛军提前一战清干净，也别拖到全国要塞守军吃 −20 叛变减值同时丢掉十几座要塞。</li>
</ul>
"""
        },
        "quick_links": [
            ("12 项阶层互动完整数值表", "ledgers.html#estate_actions"),
            ("叛军爆发要塞倒戈检定实算器", "lab.html#calc"),
            ("阶层力量与金库因果网络", "map.html#estate_pool"),
        ],
    },
]
