# -*- coding: utf-8 -*-
"""
Chapters 06 - 10 for EU5 Mechanics Compendium (1.4.9).
Covers Culture & Religion (incl. Religious Orders), Ages/Research/Exploration/Colony/Situations,
Military & Land Combat/Logistics, Navy/Maritime/Warscore/Peace, and Diplomacy/Subjects/PU/IOs.
"""


def T(cid, label):
    return f'<button type="button" class="term" data-concept="{cid}">{label}</button>'


CHAPTERS_6_10 = [
    {
        "id": "ch06",
        "slug": "ch06-culture-religion.html",
        "num": "06",
        "pillar": "culture",
        "title": "文化五态、四大语言、信仰与宗教修会",
        "en": "Culture, Assimilation, Languages, Faiths & Religious Orders",
        "subtitle": "只有主流与已接纳文化计入 50% 核心门槛；礼仪语言直接驱动科研引擎；而跨国宗教修会依忠诚度可赐天佑亦可成沉重重担。",
        "upstream": [
            ("DIP 内阁推广文化 / 宗教", "ch04-government-cabinet.html#cabinet-actions", "强制加快地方人口同化与皈依"),
            ("市场中心主导市民人口", "ch03-economy-market-trade.html#market-network", "决定市场语言及对市民同化的天然抗性"),
            ("威望与艺术品库存", "ch04-government-cabinet.html#characters-interactions", "威望÷100与艺术品持续积累文化影响力与传统"),
        ],
        "engine": "在文化容量约束下配置五级文化地位与三级宗教容忍，权衡同化（向 50% 核心文化冲刺）与即战征召、操控四大语言权重，并打理宗教学派、牧首区与跨国修会关系。",
        "downstream": [
            ("核心化 50% 人口闸门", "ch01-territory-core.html#integration-core", "已整合地点靠主流+接纳占比 ≥50% 自动核心化"),
            ("科研速率主驱动器", "ch07-ages-colonial.html#research-advances", "礼仪语言力量 + 教士阶层满意度直定革新进度"),
            ("阶层满意、叛乱与人物产生", "ch05-estates-rebels.html#rebellions", "阶层文化/宗教影响其满意；受歧视文化永不产将领大臣"),
        ],
        "redlines": [
            ("主流 / 接纳", "核心文化资格线", "仅「主流」和「已接纳」文化计数进 50% 核心化门槛，「相容文化」不算！"),
            ("40% / 1% 保护", "市民市场语同化锁", "讲市场语言的市民几近停止同化（最低缩减倍率 0.01×），靠接入度封锁"),
            ("Purity > 75", "神道教清净与荣辱", "清净保持 75 以上推升荣辱；战死减员扣清净；纳瓦特尔末日满即献祭王族"),
            ("热忱耗尽解散", "宗教修会存亡线", "和平时期热忱衰退，耗尽即解散；不忠修会的圣召反而转化成全境负面负担"),
        ],
        "sections": [
            {
                "id": "culture-status",
                "title": "01 · 文化五级待遇、文化容量与 50% 核心化硬门槛",
                "en": "5 Cultural Statuses & Cultural Capacity",
                "html": f"""
<p>一个国家针对境内的每一种 {T('culture','文化')} 设定五级待遇之一；文化接纳不是纯好感问题，它占用国家宝贵的 <strong>{T('cultural_capacity','文化容量')}</strong>（由人口规模对比及目标文化与主流文化的好感决定，基价：<strong>已接纳 3.0</strong>、<strong>相容 1.0</strong>，亲缘同文化组与同语族享显著折扣）。</p>
<table class="data-table">
  <thead><tr><th>文化地位</th><th>人群满意度修正</th><th>能否晋升上阶 / 征召 / 任官</th><th>是否计入 50% 核心（Core）门槛</th><th>同化速度倾向</th></tr></thead>
  <tbody>
    <tr><td><strong>1. {T('primary_culture','主流文化')}</strong></td><td class="num pos">+25%</td><td>全面开放（人物生成权 80×）</td><td class="pos"><strong>计入（core 与拓殖源）</strong></td><td>基准来源（不受他化）</td></tr>
    <tr><td><strong>2. {T('accepted_culture','已接纳文化')}</strong></td><td class="num pos">+10%</td><td>全面开放（可升阶/出兵/出将）</td><td class="pos"><strong>计入（可助他地直接变核心）</strong></td><td>极慢（−75% 同化速率）</td></tr>
    <tr><td><strong>3. {T('tolerated_culture','相容文化')}</strong></td><td class="num pos">+5%</td><td>可升级、可征召兵员（占 1/3 容量）</td><td class="neg"><strong>不计入！（卡死在已整合）</strong></td><td>略慢（−25% 同化速率）</td></tr>
    <tr><td><strong>4. {T('non_accepted_culture','受忽视文化')}</strong></td><td class="num">0%</td><td>不可主动升级与常规征召；限识字上限 −5</td><td>不计入</td><td>常规速率</td></tr>
    <tr><td><strong>5. {T('discriminated_culture','受歧视文化')}</strong></td><td class="num neg">−25%</td><td>不产任何政治力、禁止一切将领/内阁角色，识字 −15</td><td>不计入（高外迁流出）</td><td>最速同化（<strong>+50%</strong> 同化速率！）</td></tr>
  </tbody>
</table>
"""
            },
            {
                "id": "assimilation-merge",
                "title": "02 · 文化战争、同化核心修正与「统合文化组」",
                "en": "Culture War, Assimilation & Merged Culture Group",
                "html": f"""
<p>非主流文化人口每月依据 <strong>{T('culture_war_power','文化战争力量')}</strong>（我方 {T('cultural_influence','文化影响')} 对抗敌方 {T('cultural_tradition','文化传统')}）与当地同化度向主流文化缓慢转换。两项常被忽略但威力巨大的设定如下：</p>
<ul>
  <li><strong>影响同化的隐藏细节（<code>00_defines.txt</code> NCulture）</strong>：① 同语言（+50%）、共享文化组（+30%）、己方占当地优势文化（+50%）均显著提速；② 若当地「{T('market_language','市场语言')}」正是目标异族人群自己的语言，其同化直接受 −20% 拖拽——尤其是大城市的 <strong>市民人群若操市场语，几乎拒绝被他族同化</strong>（缩减至仅 <code>1 − 市场接入度</code> 或保底 <strong>0.01×</strong> 速率！）；③ 与宗教绑定的特定文化必须在人口先改信后方能同化。</li>
  <li><strong>统合文化组（{T('merged_culture_group','Merged Culture Group')}）</strong>：特定大国通过内阁行动 <code>merge_culture_group</code> 可把本国所属文化组整合并新造统一大文化（每支文化组全局限统合 1 次）。一旦完成，前主流与所有使用同语言的原接纳文化人口将迅速一并归入新统一大文化，彻底扫除容量瓶颈。</li>
</ul>
"""
            },
            {
                "id": "languages-art",
                "title": "03 · 四大语言职能、艺术品与勋贵骑士团",
                "en": "Four Languages, Works of Art & Chivalric Orders",
                "html": f"""
<p>语言切勿混为一谈，每个国家同时挂载四种语言槽位：</p>
<ul>
  <li><strong>通用语言</strong>（与主流文化一致）；</li>
  <li><strong>{T('court_language','宫廷语言')}</strong>（由 9 大来源选换：选语言力量最强的外语让 <strong>贵族满意 +</strong>；选礼仪语取悦 <strong>教士</strong>；选通用语取悦 <strong>平民</strong>；选首都市场语直接拉高<strong>贸易出售效率</strong>！）；</li>
  <li><strong>{T('liturgical_language','礼仪语言')}</strong>（如天主教固定拉丁语）：该语言全球 {T('language_power','语言力量')}（由采用国教士数与文化力决定）直接加减全国革新科研速率；</li>
  <li><strong>{T('market_language','市场语言')}</strong>（市场中心绝大多数市民使用的语言）。</li>
</ul>
<p><strong>{T('work_of_art','艺术品')}、{T('artist','艺术家')}体系与 {T('chivalric_order','勋贵骑士团')}（17 团）</strong>：按国家等级与革新解锁艺术家雇佣上限（王国 1 名 / 帝国 2 名），花费 <strong>10 威望</strong> 雇佣学者/画家/作家并拨给文化投资，即可耗资 <strong>经济基础 × 6</strong> 点名「委托创作」传世杰作（作家的职业常驻加成为全国识字 +0.05/月、思潮 +5%，科学家则直加 +5% 研究速度；战时首都/藏品地被占领有 10% 损毁、40% 遭劫走，急需现金亦可 6 折卖给阶层，名录库完整收录开局 161 件与事件 275 件艺术品）。君主国还可在特定地域成立贵族专属的 <strong>勋贵骑士团</strong>——只有当<strong>现任统治者本人加入且骑士团活跃</strong>时，才为国家提供常驻军事/外交修正（如匈牙利圣乔治骑士团加 +10% 贵族征召，成员自身另拿独立能力与威望，邀请入团冷却 10 年）。</p>
"""
            },
            {
                "id": "religion-system",
                "title": "04 · 宗教容忍度、基督教教廷/改革与特色多神教",
                "en": "Religious Tolerance, Curia, Reformation & Mechanics",
                "html": f"""
<p>国家将全境信仰分入 <strong>{T('tolerance','正统信仰容忍度')}</strong>、<strong>{T('heretic_tolerance','异端容忍度')}（同宗教组）</strong> 与 <strong>{T('heathenry_tolerance','异教容忍度')}（异宗教组）</strong>；宗教统一度与文化统一度一样按各省控制力加权（最低保底 5%）。除常驻的 DIP「推广宗教」同化转换外，五大教圈各有决定玩法风貌的机制：</p>
<ul>
  <li><strong>天主教与{T('curia','教廷')}</strong>：建造「枢机席位」获得 {T('cardinal','枢机')} 参与教廷议案投票，缴付{T('tithe','什一税')}（对教宗国负好感即拒缴）；高教宗权威可发{T('papal_bull','教宗诏书')}，遭{T('excommunication','绝罚')}者全三维月衰减（−0.1 正统、−0.2 威望、−0.1 宗教力、关系 −100 且白送宣战理由）。</li>
  <li><strong>东正教与{T('pentarchy','五大牧首区')}</strong>：加入或自建自主牧首教区并迁移圣座；每控制罗马/君堡/安条克/耶路撒冷/亚历山大一席获得固定加成，<strong>收复齐全部五大牧首席位后所有效果直接翻倍！</strong></li>
  <li><strong>新教（{T('reformation','宗教改革')}）派别</strong>：含胡斯派、路德宗、加尔文宗、圣公宗；解锁「解散修会」没收教会资产、「通过商站传播宗教改革」、「驱逐异端至殖民地」与「授权统治者离婚」。</li>
  <li><strong>东方与美洲信仰专精指标</strong>：印度教化身（Avatar）与业力（−33 至 +33 中性区间获奖）；道教调和度均衡；神道教 <strong>{T('purity','清净度')}（>75 持续推升荣辱）</strong>；纳瓦特尔 <strong>{T('doom','末日值')}</strong>（大城市持续涨末日值，靠战杀敌军、和约献祭敌国贵族及劫掠高发省压低，满额则自焚献祭君王全族）。</li>
</ul>
"""
            },
            {
                "id": "religious-orders",
                "title": "05 · 跨国宗教修会：热忱、据点与圣召双刃剑",
                "en": "Religious Orders, Holdings, Zeal & Callings",
                "html": f"""
<p>与一般国家不同，方济各会、条顿骑士团等宗教修会是跨越国境的兄弟会组织，直接在各国领土内建造诸如修道院、分会等 <strong>{T('holding','据点（Holdings）')}</strong> 并按国情形成「<strong>修会地位（Standing）</strong>」（首座之后每多 1 座据点推高，且<strong>在小国境内单座据点撬动占比更大</strong>）：</p>
<ul>
  <li><strong>{T('zeal','热忱（Zeal）')}</strong>：修会的命根子。在漫长和平中稳步流失（归零即修会解体），唯有参加宗教圣战或在异教边疆服役方能重振。</li>
  <li><strong>{T('calling','圣召（Calling）')} 的正负反转陷阱</strong>：每座修会奉行祈祷、学术、医疗或战争四类圣召之一，并对你境内的社会价值观产生每月推动（按据点数与热忱缩放）。关键机制在于：<strong>当该修会对本国统治者保持「忠诚」时，其圣召按修会地位比例赋予全境正面赐福；可一旦被敌国渗透或统治者虐待修会使其变为「不忠堕落」时，同样的圣召效果会原封不动反转成全境沉重的全国负面惩罚！</strong></li>
</ul>
"""
            },
        ],
        "discussion": {
            "title": "论坛实战讨论与排障 · 「接纳」vs「相容」与宫廷语言最优解",
            "html": """
<ul>
  <li><strong>为什么游戏玩家总建议前期先把富庶新省文化设为「接纳（Accepted）」而不是慢吞吞地全境同化？</strong><br>
  <strong>算一笔账</strong>：早期异文化省往往伴随低控制力和高宗教文化好感阻力，靠 1 名内阁用「推广文化」从 0% 把几万当地土著同化过 50% 核心线可能需要整整 25–40 年，白白卡掉殖民移民源与核心 +20% 控制力上限。而只要在文化界面消费 3 点文化容量将其提为「已接纳」，该地人口不仅<strong>立刻满足 ≥50% 核心条件直接晋升为核心（Core）</strong>，同时立即解除 +10% 满意度和完整征召兵/升阶权限！等到中后期社会价值观与同化技术飞起、容量吃紧时，再逐步降级腾出名额强推主流文化统合。</li>
</ul>
"""
        },
        "quick_links": [
            ("293 种宗教全表", "ledgers.html#religions"),
            ("17 骑士团 & 圣地/艺术品名录", "directory.html#chivalric_orders"),
            ("2,087 文化 & 528 语言全览", "directory.html#cultures"),
            ("文化与核心 50% 链路图", "map.html#culture_lang"),
        ],
    },

    {
        "id": "ch07",
        "slug": "ch07-ages-colonial.html",
        "num": "07",
        "pillar": "culture",
        "title": "时代思潮、革新研发、殖民扩张与局势自动化",
        "en": "Ages, Institutions, Advances, Colonization & Automation",
        "subtitle": "研发速度由礼仪语、识字率与教士决定；殖民必须由核心省供血人口；而开关错误的自动化常比操作失误更毁档。",
        "upstream": [
            ("礼仪语力量、平均识字率、教士满意度", "ch06-culture-religion.html#languages-art", "组成全国每月革新研究进度的三大乘区"),
            ("核心地点人口蓄水池", "ch01-territory-core.html#core-power", "唯一合法向海外特许殖民地迁出人口的源头"),
            ("经济基础与国家预算", "ch03-economy-market-trade.html#wealth-to-treasury", "承担殖民地月维护、探险出海开销与接纳思潮花费"),
        ],
        "engine": "追随六大时代聚焦、跨市贸易或内阁吸纳 18 项思潮突破 20% 人口接纳，点亮革新树解锁舰船/殖民半径，维持单省限 3 席的特许殖民地竞赛，并驾驭历史局势、灾难与半自动托管。",
        "downstream": [
            ("跨时代新兵种与内阁席位上限", "ch08-military-combat.html#force-types", "解锁地区级整合、城镇特权、高压火炮与新舰船"),
            ("跨洋热带商品贸易帝国", "ch03-economy-market-trade.html#trade-orders", "殖民领土建成种植园输送蔗糖烟草香料回本土市场"),
            ("历史大变局重塑地缘版图", "ch10-diplomacy-subjects.html#pu-and-ios", "黑死病/百年战争/宗教改革/意大利战争改写规则"),
        ],
        "redlines": [
            ("≥ 20% 总人口", "思潮接纳硬门槛", "全境处于已完全传播该思潮地点的人口之和需 ≥ 全国总人口 20%"),
            ("仅限核心(Core)", "殖民迁徙来源锁", "没有变成「核心」的新吞并行省一个殖民定居者都发不出去"),
            ("1,000 人 / 限 3", "殖民定居与竞争", "每地满 1,000 人且文化/信仰达标归属生效；每省至多 3 国同期抢殖"),
            ("365天 / 月检", "停摆自动与灾难", "部分局势与 38 项国家灾难按月结算进度，满值瞬间触发政变危机"),
        ],
        "sections": [
            {
                "id": "ages-institutions",
                "title": "01 · 六大时代更替、焦点抉择与 18 种思潮传播算法",
                "en": "6 Ages, Age Focus & 18 Institutions Spread",
                "html": f"""
<p>EU5 从 1337 年横跨至 1836 年，分为六大{T('age','时代')}：<strong>① 传统时代（1337）→ ② 文艺复兴 → ③ 探索时代 → ④ 宗教改革 → ⑤ 绝对主义 → ⑥ 革命时代</strong>。每个新时代开启时，国家必须于 <strong>ADM / DIP / MIL 三系焦点</strong> 中选一——这决定你本时代革新树中额外开放的专属强化枝干（一旦选定不可反悔）。</p>
<p>每个时代诞生 3 种、全时期共 <strong>18 种 {T('institution','思潮')}</strong>（开局时代三思潮多已就绪）：</p>
<ul>
  <li><strong>思潮三大传播渠道</strong>：① 从已彻底接纳发源地的相邻地块逐像素漫溢（受地点面积中位数 25 缩放）；② <strong>跨市场贸易传播</strong>（你所属市场只要与「已接纳该思潮的世界」建立大宗贸易流——按贸易路径半衰成本 25 与最小市场吞吐 10 结算——思潮就顺着商船跨海渗透进你的中心港口！）；③ 最稳的急救开关：派 ADM 内阁在首都等人口最密集的大省直接执行 <strong>「研究思潮（<code>study_institutions</code>）」</strong>。</li>
  <li><strong>全国接纳 20% 铁门槛（<code>INSTITUTION_MINIMUM_PERCENT = 0.2</code>）</strong>：思潮在个别小岛或港口满 100% 后还不够，必须当「所有已完全传播（100%）该思潮的自有地点人口总和 ÷ 全国总人口 ≥ <strong>20%</strong>」时，方能付钱正式点击「接纳（Embrace）」（同时让全国经济基础额外推高 <code>+6.6%</code>，守旧vs创新轴极大压低这笔账单）。</li>
</ul>
"""
            },
            {
                "id": "research-advances",
                "title": "02 · 革新研究进度公式与「储备研究力」",
                "en": "Research Progress & Stored Research",
                "html": f"""
<div class="formula-box">
<strong>每月研究进度（{T('research_progress','Research Progress')}）四大核心引擎：</strong><br>
① 本国 <strong>{T('liturgical_language','礼仪语言')}</strong> 的世界语言力量；<br>
② 全国受控地点平均 <strong>{T('literacy','识字率')}</strong>（创新价值观、图书馆与大学核心拉升项）；<br>
③ 本国 <strong>{T('clergy_estate','教士阶层')}满意度</strong>（教士一旦闹情绪直接把全国科研速率拦腰斩断！）；<br>
④ 已接纳 {T('institution','思潮')} 总数与国家/时代革新倍率。<br>
<em>小贴士：当前没有选中任何在研 {T('advance','革新')} 时，每月产生的研究点数自动存进 <strong>{T('stored_research','储备研究力')}</strong>，等你接纳新思潮后第一时间瞬间倒进新科技，绝不浪费半滴。</em>
</div>
<p>注意游戏内所有科技并非单线：革新分为通用池、时代焦点池、<strong>国家标签/文化组/宗教/政体专属革新</strong>，部分革新对先期年代落后国家会提供逐时代追赶减费（Previous Age Reduction）。</p>
"""
            },
            {
                "id": "exploration",
                "title": "03 · 未知之地（Terra Incognita）、海陆探险与双半径",
                "en": "Exploration, Naval & Colonial Range",
                "html": f"""
<p>开局世界大片大洲位于 <strong>{T('terra_incognita','未知之地')}</strong>（不可看亦不可交互）。指派带有探索特质的 <strong>{T('explorer','探险家')}</strong> 出发测绘，是按 <strong>「地区 Area」</strong> 而非单格进行的：</p>
<ul>
  <li><strong>能力职责分工</strong>：派出探险任务只看目标是否在 <strong>{T('naval_range','海军范围')}</strong>（含盟友/卖了{T('fleet_basing_rights','驻港权')}的远洋友港）之内。探险家自身 <strong>{T('mil','MIL')} 越高推进探索进度越快</strong>；而 <strong>{T('adm','ADM')} 越高则越大幅压低每月沉重的黄金维护账单</strong>！</li>
  <li><strong>水手与距离放大启动成本</strong>：出海探索不仅扣国库维持费，还实打实吃水手且起始筹备费随目标距首都的距离成正比（海军范围越高越便宜）。完成瞬间地图揭开、探险家自动返航。</li>
</ul>
"""
            },
            {
                "id": "colonial-charters",
                "title": "04 · 特许殖民地（最多 3 国竞争）、完全定居判定与征服者",
                "en": "Colonial Charters, Fully Settled Rules & Conquistadors",
                "html": f"""
<p>与过去直接派 1 个抽象殖民官不同，EU5 建立的是真实的跨海移民输血管道——<strong>{T('colonial_charter','特许殖民地')}</strong> 一次针对一整个 <strong>省份（Province）</strong> 发起（前提：目标省内任意待殖地点人口低于最大可殖上限 50k，且我方 {T('power_projection','力量投射')} 达标、处在 {T('colonial_range','殖民范围')} 内）：</p>
<ul>
  <li><strong>唯一输血源头</strong>：你必须在创建时选择本国一个<strong>非未整合、必须已核心化（<code>Core</code>）</strong> 的省份提供持续 {T('colonial_migration','殖民迁徙')}。同时配合 ADM 内阁「向特许殖民地派遣移民」可暴增增速（AI 与玩家均可在最多同时 <strong>3 个不同势力在同一省竞争</strong> <code>MAX_CHARTERS_IN_PROVINCE = 3</code>；遇疟疾等地方病省则需极高移民速度抵消死亡惩罚）。</li>
  <li><strong>完全定居（{T('fully_settled','Fully Settled')}）归属精确公式</strong>：一旦某未殖地点内居民达到 <strong>≥ 1,000 人</strong>（<code>COLONIAL_CHARTER_MIN_POPS = 1</code>）且其中信仰我方 <strong>国教</strong> 并属于我方 <strong>主流或已接纳文化</strong> 的人口占比跨过门槛（该门槛随国家 <strong>力量投射越高而越低！</strong>），该地点即宣告定居完成，直接变更为我方殖民（<code>colonized</code>）直辖地或新成立海外殖民领（随目标选择而定）。</li>
  <li><strong>征服者（{T('conquistador','Conquistadors')}）</strong>：西班牙/葡萄牙等特定剧本国家或革新允许花费金币与 90 天筹备招募一位携带独立远征部队的征服者人物，直接替宗主国跨海征讨土著政权并开疆拓土建起新属国。</li>
</ul>
"""
            },
            {
                "id": "situations-disasters",
                "title": "05 · 历史局势（24项）、国家灾难（38项）、使命与全自动化开关建议",
                "en": "Situations, Disasters, Missions & Automation Best Practices",
                "html": f"""
<p>在历史进程上，EU5 把全球风暴拆作全跨国共同介入的 <strong>24 项{T('situation','历史局势')}</strong>（百年战争、黑死病、宗教改革、西方大分裂、红巾军、意大利战争、小冰期、海盗黄金时代等）、<strong>4 类社会运动</strong>（新教与复兴浪潮等）以及仅盯着单国本月体征判定的 <strong>38 项{T('disaster','国家灾难')}</strong>（罗斯内战、宫廷与乡村、凤凰的命运、自由渴望等，另含全游戏 4,213 条国别历史事件与使命链——详见第 11 章专述）。以经典高危灾难 <strong>「帝国衰落（Decline of Empire）」</strong> 为例（1.4.9 已彻底移除了旧版维基所谓的自满条，直接硬判当前指标）：限独立<strong>帝国等级</strong>、稳定度为负且已过文艺复兴时代，当<strong>本土大区平均控制力跌破当代红线（四时代依次为 45% / 50% / 55% / 60%）</strong>，或未受容忍文化人口占比超过全国三分之一，一旦结束新升帝国保护期即按月检定爆发动荡！</p>

<table class="data-table">
  <thead><tr><th>系统自动化模块</th><th>社区公认推荐开关</th><th>原因与关键风险规避</th></tr></thead>
  <tbody>
    <tr><td><strong>税收 / 阶层自动贿赂</strong></td><td class="pos">建议开启 / 慎调（可半开）</td><td>自动税收会智能把税滑块贴在 50% 阶层满意度安全线上方避免跌破 25% 拒出征召兵线；但想囤钱发特权时注意暂关</td></tr>
    <tr><td><strong>市场贸易托管</strong></td><td><strong class="neg">关闭全自动</strong> → 改用 <strong>贸易指令（Trade Orders）</strong></td><td>全自动贸易有时会乱出口你急缺的粮食和建筑工具；利用「贸易指令」锁死关键进口与最小利润最稳妥</td></tr>
    <tr><td><strong>军队招募 / 要塞建造 / 城市升格</strong></td><td class="neg">强烈建议关闭</td><td>AI 会把核心产粮大省随便升城吃垮全境粮仓，或在低控垃圾地狂砌超上限高维护要塞</td></tr>
    <tr><td><strong>舰队自动巡逻</strong></td><td class="neg">重要走廊关闭</td><td>1.4.9 默认刷到 <strong>90%</strong> 海上存在就换海格/回港，无法帮你把核心海外领的海上存在锁死 100%</td></tr>
  </tbody>
</table>
"""
            },
        ],
        "discussion": {
            "title": "论坛实战讨论与排障 · 前期殖民卡在 900 人与思潮死活进不来怎么办？",
            "html": """
<ul>
  <li><strong>问：我的特许殖民地开在北美/西非，每月迁过去的人只有个位数还因为本地疾病越搬越少？</strong><br>
  <strong>根因与解法</strong>：殖民迁徙速率既看母省<strong>核心总人口</strong>与殖民范围/距离衰减，更强烈受当地土著规模与<strong>地方病（如疟疾）</strong>打击（游戏定义设了若月迁徙不足 0.05 即基本白烧钱的阈值）。早期务必挑离核心港近、土著少或无恶性疟疾的岛屿作第一跳板，且务必挂上 ADM 内阁「向特许殖民地派遣移民」，并在母国选用高人口<strong>核心</strong>大省供血——刚抢来还没变核心的省永远别选作移民来源地！</li>
</ul>
"""
        },
        "quick_links": [
            ("24 项局势与 38 项灾难全典", "ledgers.html#situations_disasters"),
            ("3,592 项时代革新全名录", "directory.html#advances"),
            ("第 11 章 剧本、使命与 DLC", "ch11-scenarios-missions-dlc.html"),
            ("第 12 章 自动化与 1.4.9 更新", "ch12-gameplay-automation-updates.html"),
        ],
    },

    {
        "id": "ch08",
        "slug": "ch08-military-combat.html",
        "num": "08",
        "pillar": "military",
        "title": "兵源经济学、四阵位陆战、围城与跨海后勤",
        "en": "Military Economy, 4-Section Land Combat, Sieges & Logistics",
        "subtitle": "在 EU5 打仗就是打人口与粮食：每一名征召兵战死都直接削减家乡的纳税和造厂人口，而缺粮一次就可毁灭半支远征军。",
        "upstream": [
            ("阶层满意度 ≥25% 与人力建筑", "ch05-estates-rebels.html#estate-interactions", "决定是否拉得出征召兵，以及常备人力池上限"),
            ("市场武器/马匹供给与税银预算", "ch03-economy-market-trade.html#production-buildings", "缺少装备货物会让征募停滞、低维护折损士气"),
            ("省粮仓储备与海军港口分布", "ch02-population-food.html#food-chain", "战时前线部队直接吃省粮或靠海军跨海运输食物"),
        ],
        "engine": "配置征召兵/正规军(族系上限)/雇佣兵/私人团，依中军+两翼+预备队四阵位打响炮击阶段与日/时步战斗骰，按 10:1/2:1 歼灭俘虏，并用补给站/海军运粮维持围城推进与焦土抗敌。",
        "downstream": [
            ("和平会议战争分数与厌战度", "ch09-navy-war-peace.html#warfare-peace", "死伤堆高厌战（每1点 −2.5%士气）；占领要塞锁死割地惩罚"),
            ("家乡常住人口与战后荒废", "ch02-population-food.html#prosperity-devastation", "占领瞬毁 90% 粮 + 12月劫掠修正拖垮十年经济"),
            ("战俘赎金与低价佣兵回收", "ch03-economy-market-trade.html#wealth-to-treasury", "战俘花 30% 维护供养，或 0.25× 超低价收编成己方雇佣兵"),
        ],
        "redlines": [
            ("75% / 240个月", "征召兵战力与回血", "陆战实力仅为正规军 75%（海战 5%），训练度 −20%，全灭后恢复上限需 20 年"),
            ("60% + 30% + 3%/天", "每日接敌公式", "按日步进下基础 60% + min(30%, 主动×2.5%) + 3%/天；未接敌挨打受 1.1× 兵伤"),
            ("10:1 / 2:1", "直推全歼门槛", "开战首步 10:1 兵力直接抹除敌军；敌士气崩盘后仅需 2:1 即可追击全歼"),
            ("毁 90% 粮 / 2格", "占领与补给站边界", "地点易手瞬间摧毁 90% 存粮（并可掳 15% 奴隶）；补给站仅辐射周围 2 格内友军"),
        ],
        "sections": [
            {
                "id": "force-types",
                "title": "01 · 四大兵源对比、部队族系与征召兵「人口灭绝陷阱」",
                "en": "Levies, Regulars (Unit Families), Mercenaries & Private Regiments",
                "html": f"""
<div class="callout warn"><strong>为什么老玩家称早期征召兵（Levies）为「自我人口灭绝装置」？</strong><br>
每一名 {T('army_levy','陆军征召兵')} 都是把你省里正在挖矿种地的真实 {T('pop','平民/贵族人口')} 直接掏出来拎上战场！他们享受 <strong>食物消耗 −75%（轻装觅食）</strong>，但同时承受 <strong>−20% 训练度</strong>、仅及正规军 <strong>75%</strong> 的基础实战效能（海战征召运输船更是只有 <strong>5%</strong> 效能！），并且<strong>绝不在战场上靠人力补员</strong>。一旦他们在战场上阵亡或饿死，家乡对应的真实劳动力就<strong>永久人间蒸发</strong>，重新恢复该省最大征召配额要耗费整整 <strong>240 个月（20 年）</strong>！</div>

<table class="data-table">
  <thead><tr><th>军团类别</th><th>消耗资源池与招募门槛</th><th>战力与补员机制</th><th>独特战术与经济细节</th></tr></thead>
  <tbody>
    <tr><td><strong>1. 征召兵</strong><br><code>levies</code></td><td>抽调本省真实人群；阶层满意度必须 <strong>≥ 25%</strong>；召集时间 15 天</td><td>75% 战力倍率 / 训练度 −20% / <strong>不可战地补员</strong></td><td>平时免军费（维持乘数 0.01），解散时生还者全数返乡还原劳动力</td></tr>
    <tr><td><strong>2. {T('regular_regiment','正规军')}</strong><br><code>regulars</code></td><td>消耗国家 {T('manpower','人力')} 池（上限 = 5 年月人力）与金币、武器货物；按 <strong>{T('unit_family','部队族系')}</strong> 共享上限</td><td>满额训练度、每时代性能暴涨、<strong>仅在友方领土按月 25% 补员</strong></td><td><strong>同族系老兵升级仅需原造价 10%，且永远不额外占招募上限！</strong> 可在和平期靠「操练」堆满经验（最高免伤 50%）</td></tr>
    <tr><td><strong>3. {T('mercenary','雇佣兵')}</strong><br><code>mercenaries</code></td><td>从所在地区人口池租借，另加将领能力指数定签约费与 24 个月合同（基础维护 <strong>+35%~50%</strong>）</td><td>吃雇佣兵本地食物配给（应急口粮撑 365 天）；不掉己方核心正规人力</td><td>玩家可反手点击「<strong>设为可供雇佣（<code>make_unit_available_for_hire</code>）</strong>」把闲置军团挂牌租给别国狂赚雇佣金！</td></tr>
    <tr><td><strong>4. {T('private_regiment','阶层私人团')}</strong></td><td>特权授予下由贵族/哥萨克阶层自费筹建</td><td>花极大代价靠互动 <code>press_estate_private_regiments</code> 征调参战</td><td><strong>极高风险</strong>：若在参战途中所属阶层发动内战叛乱，这些私人团会瞬间倒戈！</td></tr>
  </tbody>
</table>
"""
            },
            {
                "id": "battle-mechanics",
                "title": "02 · 四阵位部署、日步/时步交火与兵种混编规则",
                "en": "4-Section Deployment, Daily vs Hourly Combat & Combined Arms",
                "html": f"""
<p>陆军与海军交战时均各自排开四个 {T('section','阵位')}：前排由 <strong>{T('center','中军')}、{T('flank','左翼')}、{T('flank','右翼')}</strong> 构成（每个阵位受本地地形决定的 <strong>{T('frontage','战斗宽度')}</strong> 限制，山地 −4 宽、疏林 −2 宽，可最多超额叠挤 25%），后方则列驻 <strong>{T('reserves','预备队')}</strong>。</p>
<ul>
  <li><strong>兵种混编（{T('combined_arms','Combined Arms')}）红线</strong>：当一支军队或舰队内<strong>没有任何一种兵种类别占比达到或超过 50%</strong> 时，队伍里每多包含一种兵种类别就全军白拿一档战斗力加成！超过 50% 纯一色堆积（如纯重步兵海）直接作废该加成。</li>
  <li><strong>阶段与交战时间步进（1.4.9 默认按日 / 可设按小时）</strong>：
    <div class="formula-box">
      <strong>1. 开幕炮击阶段（{T('bombard_phase','Bombard Phase')}）</strong>：按日规则持续 <strong>3 天</strong>（按小时 5 拍），只有具备轰击能力的炮兵有每轮 20%+ 机会远程砸伤同阵位敌军。<br>
      <strong>2. 作战阶段（{T('combat_phase','Combat Phase')}，每 4 天轮换一次骰子）</strong>：前排未接敌军团每拍按公式投 D100 进场接战——<br>
      &nbsp;&nbsp;<code>每日接战概率 = 60%(基础) + min(30%, 有效主动性 × 2.5%) + 3% × 战斗已持续天数</code><br>
      &nbsp;&nbsp;<em>警告：卡在前排尚未投过接战骰的部队处于挨打状态，承受 <strong>1.1× 兵力伤害与 1.2× 士气伤害</strong>！高主动性骑兵与轻步兵抢先接战在早期极度致命。</em><br>
      <strong>3. 预备队填补</strong>：前排空缺时，预备队掷 <strong>D20</strong> 与自身「参战速度 × 0.1」判定冲上前线填坑。若某方全部前排阵位均无作战单位即宣告溃败撤退。
    </div>
  </li>
</ul>
"""
            },
            {
                "id": "prisoners-overrun",
                "title": "03 · 10:1/2:1 瞬间全歼与战俘（Prisoners）三大回收途径",
                "en": "Overruns & Prisoner Management",
                "html": f"""
<p>战场上并非每次都是拼到士气见底撤走：若开战首个结算步我方总兵力达敌军 <strong>10 倍</strong>（<code>INITIAL_OVERRUN_FACTOR = 10</code>），或当敌军士气崩盘低于崩溃线（0.05）时我方兵力只需达到敌军 <strong>2 倍</strong>（<code>MORALE_OVERRUN_FACTOR = 2</code>），敌方部队会直接触发 <strong>碾压全歼（Overrun）</strong> 而不战自溃。</p>
<p>歼灭或彻底打崩的敌方残部有几率被整体俘获成为 <strong>{T('prisoner','战俘')}</strong>（被俘瞬间阵亡损耗率 40%）：在俘虏被处理前，俘获国每月只付常规维护费的 <strong>30%</strong> 养着他们，随后可任选三种处理：① <strong>勒索赎金换现金</strong>（同批冷却 60 天）；② <strong>收买转化成归你效命的雇佣兵</strong>——而且这批战俘佣兵只需常规雇佣兵月维持费的 <strong>25%（0.25×）</strong>！（虽然士气上限封顶在 60%）；③ 当场斩杀或就地溶解。</p>
"""
            },
            {
                "id": "siege-forts",
                "title": "04 · 要塞上限、控制区（ZoC）、围城进程与强攻",
                "en": "Forts, Zone of Control, Sieges & Assaults",
                "html": f"""
<p>{T('fortification','要塞')} 通过 <strong>{T('zone_of_control','控制区 ZoC')}</strong> 强制锁定周围相邻地点：敌军踏入要塞控制范围后必须先攻陷该要塞方能深入腹地。全境超过 {T('fort_limit','要塞上限')}（随领土数、大都市数、防御价值观与革新扩大）后，每座超标要塞都会大幅推高全国每月要塞维护金（消耗建造与补给材料随市场价波动）。</p>
<ul>
  <li><strong>围城基本门禁</strong>：无防御工事地点需要至少 <strong>100 人</strong> 围 15 天即可占领；有城墙要塞默认每 <strong>30 天（最小加速至 7 天）</strong> 投一次阶段进度（达 <strong>20 分</strong> 即陷落），且<strong>攻城兵员人数必须始终 ≥ 城内守军人数</strong>否则围城进度完全冻结！配足炮兵（每 2 团炮兵按要塞等级给增益，最高 +8 围城加成）与海军封锁沿海港口是破城捷径。</li>
  <li><strong>强攻（{T('assault','Assault')}）代价</strong>：存在缺口（上限 3 个）时可强攻快速破城，按日重投判定（每拍进攻方扣 2.5 倍损耗与 3.0 士气），务必搭配高训练度重装正规军而非拿宝贵的征召兵往城头上送死！</li>
</ul>
"""
            },
            {
                "id": "siege-supply",
                "title": "05 · 后勤食物链、补给站（2 格）、海军送粮与焦土抗战",
                "en": "Logistics Chain, Supply Depots, Naval Food & Scorched Earth",
                "html": f"""
<p>部队断粮立刻在月底吃满 <strong>+5.0 额外损耗（每月死 5% 兵员）</strong>，远征大军往往不战而自溃。军队遵循严格的四级求粮与两项破坏规则（<code>NUnit & NCombat</code>）：</p>
<ol>
  <li><strong>三条合法食物来源</strong>：① 当前所站「拥有食物获取权（自有、盟友、已通行或已占领）」之 <strong>省份省粮仓</strong>；② 敌境内驻扎修建的友方 <strong>{T('supply_depot','补给站')}</strong>（最多存 50% 上限粮食，直接覆盖周边 <strong>距离 ≤ 2 格</strong> 友方军团，但敌方控制区会直接切断后勤路径！）；③ 停泊在紧邻海域、打开「<strong>{T('distributing_food','分发食物')}</strong>」指令的友好舰队——该舰队先利用「{T('gathering_food','收集食物')}」从邻近友港把船舱粮仓灌满，再在沿岸滩头当海上移动奶妈喂饱围城陆军！</li>
  <li><strong>单位权重与超补给耗粮惩罚</strong>：当地集结大军总权重超过地块 {T('supply_limit','补给上限')} 时，每日食物消耗最高直接飙升至正常的 <strong>4.0 倍</strong>（<code>1 + MAX_FOOD_CONSUMPTION_PENALTY 3.0</code>）瞬间掏空省储。</li>
  <li><strong>占领摧毁、劫掠与焦土（Scorched Earth）</strong>：每当一块地被夺取，其本地存粮瞬间摧毁 <strong>90%</strong> 并自动掠夺、施放 12 月 <code>looted</code> 惩罚（敌方本地获粮再 −10%、人口月损 −0.5%）。防守弱势方更可在敌军必经之省主动点下 <strong>焦土政策（<code>scorched_earth</code>）</strong>：令敌军经过耗时暴涨 <strong>+50%</strong>、极大毁坏本地粮产、虽代价是月度繁荣度跌 −5%，却能把十几万入侵大军活活饿死在半路上！</li>
</ol>
"""
            },
        ],
        "discussion": {
            "title": "论坛实战讨论与排障 · 为什么我的大军在别人家门口越站人越少、连撤都撤不走？",
            "html": """
<ul>
  <li><strong>三大低级致命错觉逐一拆解</strong>：<br>
  ① <strong>拿重骑兵纯兵种+过量征召兵在山地/密林塞满 6 万人攻城</strong>：山地大幅腰斩战斗宽度且补给上限极低，超过补给上限后你的大军食物消耗暴涨到 400%——省粮仓几周吃空后全军同时触发「无粮 +5% 月损耗」，你以为在慢慢磨城，其实你在按月活体融化自己家里几千户纳税人。<br>
  ② <strong>围海港孤岛要塞不配运输/轻船舰队</strong>：沿海要塞如未封锁港口能撑很久，而且远征陆军只要在邻近海域放几艘开启「收集/分发食物」的运输与常规舰，就可以跨省从本土大粮仓源源不断海运军粮上岸。<br>
  ③ <strong>被刚投降的占领地阻断撤退</strong>：部队撤退会瞬间丢弃携带的 <strong>50%</strong> 食物（<code>FOOD_PERCENTAGE_LOST_AT_RETREAT = 0.5</code>），务必在撤退前保证沿途身后留有我方补给站或未断连省份！</li>
</ul>
"""
        },
        "quick_links": [
            ("401 种陆海军兵种全数值表", "ledgers.html#unit_types"),
            ("18 项军队单位能力名录", "directory.html#unit_abilities"),
            ("接战概率 & 兵种混编校验器", "lab.html#calc"),
            ("军制、围城与后勤因果星图", "map.html#siege_logistics"),
        ],
    },

    {
        "id": "ch09",
        "slug": "ch09-navy-war-peace.html",
        "num": "09",
        "pillar": "military",
        "title": "海战海权、90%巡逻陷阱、私掠与战争和约",
        "en": "Navy, 90% Patrol Trap, Privateers, Warscore & Peace Treaties",
        "subtitle": "拆穿自动巡逻达 90% 即走人的底盘陷阱，用 5–10 艘轻船守住海上行政大动脉；并用未围要塞 −33% 惩罚与大帝国折扣写出性价比最高的和平条约。",
        "upstream": [
            ("沿海城镇水手建筑与船用木料/大炮", "ch03-economy-market-trade.html#production-buildings", "提供船员补充池与船体建造原料"),
            ("陆军攻占、野战分与间谍制造 CB", "ch08-military-combat.html#battle-mechanics", "贡献野战战分与 20 间谍网制造的合法宣战名分"),
            ("海格港口适宜度与海军传统", "ch01-territory-core.html#proximity", "海军传统按 (点数÷100)×50% 放大海上存在增长"),
        ],
        "engine": "调度重轻战舰打赢海战并封锁敌岸港口，平衡手动驻港 100% 海上存在与反私掠护航，按战争目标、占领价值与战斗分积累 100% 战分谈判签约。",
        "downstream": [
            ("跨海省份邻近度与控制力命脉", "ch01-territory-core.html#proximity", "海格海上存在决定所有沿海港口的近岸控制上限"),
            ("和约新割地与敌意（AE）冲击", "ch10-diplomacy-subjects.html#antagonism-coalition", "土地账单转入未整合状态，并给周边引爆敌意震荡"),
            ("战胜赔款引发通胀与5–10年休战期", "ch03-economy-market-trade.html#finance-debt", "一次性索取巨额赔款会按比例推高战胜方本国通胀"),
        ],
        "redlines": [
            ("90% 自动停巡", "巡逻海格陷阱", "自动「巡逻海域」把海格刷至 90% 就停手换区！要锁 100% 需拆轻船小队手动驻留"),
            ("1.5 士气强撤", "海战败走沉船线", "海军士气跌破半值（1.5/3.0）触发全队破碎溃撤回港；耐久 <10% 有 10% 概率沉没"),
            ("−33% 未围要塞", "和平割地重惩罚", "割让未曾被己方占领过的要塞及其土地成本暴跌 −15% 叠加 −18% = −33% 效率"),
            ("50分上限/25目标", "战分计算结构", "单靠打胜仗最多攒 50 分战分，占领跳分与目标跳分（上限 25+25）才能推进至 100"),
        ],
        "sections": [
            {
                "id": "naval-combat",
                "title": "01 · 舰船分工、海战捕获逻辑与沿海港口封锁五大惩罚",
                "en": "Naval Combat, Capture & Blockade Penalties",
                "html": f"""
<p>和陆军不同，由船厂和 {T('sailors','水手')} 招募出的 {T('regular_ship','正规舰船')}（重型战舰扛线、轻型战舰刷海权与巡护、桨帆船适应内海近岸、运输船载兵兼海上送粮）远非 {T('navy_levy','海军征召船')}（战力影响力仅有 <strong>0.05</strong>，即 5%！）所能匹敌。战损船只在非己港处无法修复（须驶回自港或租借了 {T('fleet_basing_rights','驻港权')} 的友港花水手每月修 10%，闲置可「{T('mothballed','封存')}」省一半经费）。</p>
<ul>
  <li><strong>海战沉没与俘获规则</strong>：海战中 {T('hull_size','船体尺寸')} 决定减伤，{T('cannons','火炮')} 决定杀伤；重伤（<50% 耐久）船只每轮有概率单独脱离战列。全舰队平均士气跌破 <strong>1.5（半值）</strong> 即全军狼狈退回港口，耐久不足 <strong>10%</strong> 的逃亡破船有 10% 几率当场沉入海底；被大比分碾压或重残的敌船极易遭获胜方当场俘获入编（<code>NAVY_OVERRUN_EXTRA_CAPTURE_CHANCE = 0.15</code>）。</li>
  <li><strong>{T('blockade','港口封锁')}五大精准打击</strong>：当你的海军达到目标沿海地点的 {T('blockade_capacity','封锁能力')} 要求（按港口发展度、人口、进出口吞吐量动态抬高），封锁瞬间对敌国港口施加五大持续伤害：<strong>① 压低食物产出、② 抹杀当地海上存在、③ 压低发展度、④ 压低控制力、⑤ 压低当地繁荣度</strong>，同时拉长当地围城突破速度并贡献战争参与度。</li>
</ul>
"""
            },
            {
                "id": "maritime-presence",
                "title": "02 · 构建海上行政大动脉：破解「90% 自动巡逻返港陷阱」",
                "en": "Maritime Presence & The 90% Patrol Trap",
                "html": f"""
<p>对于跨海大国（如瑞典、威尼斯、热那亚、西班牙、奥斯曼、英国、大明/日本）而言，海域上的 <strong>{T('maritime_presence','海上存在')}（0–100%）</strong> 直接决定了你的外省港口是 80% 控制力的肥美印钞机，还是 0% 控制力的阶层自留地。在 1.4.9 中请注意区分：官方已调整说明明确将海上存在主要聚焦于 <strong>减少海路邻近度衰减</strong> 以及靠沿岸海上存在产生近岸市场的 {T('merchant_maritime_power','海上贸易优势')}（和平时期本国沿海港口自身即可缓慢恢复海存，而海军传统每 100 点直接再放大 +50% 海存增值速率）。</p>
<div class="callout warn"><strong>社区实测最大坑：为什么自动巡逻总是掉海权、控制力上不去？（1.4.9 口径核对）</strong><br>
<code>00_defines.txt</code> 第 2166 行依然写着引擎定义常量：<code>PATROL_THE_SEAS_THRESHOLD = 90</code>（虽然 1.4.9 官方更新说明中将巡逻离开条件口头表述为 100%，但在脚本与本地实机巡逻验证彻底闭环前，仍强烈按 90 阈值防掉线处理）！当自动巡逻舰队到达目标门槛即启程离开或返港停靠，随后海上存在立刻下跌、海路控制随之一落千丈。<br>
<strong>正确高玩实操做法</strong>：放弃用一支庞大的混合主力跑全海自动巡逻——从船队里按每组 <strong>5–10 艘廉价轻型战舰（Light Ships）</strong> 分拆出多支纯轻船小分队，<strong>手动右键停泊并常驻在首都通往核心港口之间的每一个关键沿海海格上</strong>，就能将核心航道的海上存在永久锁死在 100%！（海战按沉没与俘获分别结算；受损返回港内时自动取港口修与海上修二者中的较高速度回血）。</div>
"""
            },
            {
                "id": "privateers",
                "title": "03 · 私掠者（Privateers）与海盗防剿",
                "en": "Privateers, Anti-Piracy & Slave Raiding",
                "html": f"""
<p>在沿海地区可通过国家行动耗费 250 名水手起步 <strong>雇佣{T('privateer','私掠者')}（<code>hire_privateer</code>）</strong> 部署至海军范围内的外国海区（每次增强 +0.20 强度）。在外人视野中私掠者与无主 {T('pirate','海盗')} 无异，能持续：<strong>每点削减受害国海上存在、按月偷取其海上收入（若单次掠得超过对方月收入 10% 将吃满对方仇恨惩罚）</strong>，并在允许奴隶制时每月有 <strong>2.5%（d1000 &lt; 25）几率直接将受害沿海 1% 人口掳掠为奴</strong>！</p>
<p><strong>反制方式</strong>：每艘战舰都标有 <strong>{T('anti_piracy_warfare','反海盗影响')}</strong> 属性。在本国海域部署含巡逻船或轻重战舰的海军，即可按月不断磨光敌方私掠者的 <strong>私掠耐久度（<code>privateer_durability</code>）</strong> 直至将其从海面彻底抹消（且一旦雇主国国内水手归零，其派出的私掠者也会每月自然崩解 5%）。</p>
"""
            },
            {
                "id": "warfare-peace",
                "title": "04 · 宣战理由、战争分数三大来源、参战度与呼吁和平",
                "en": "Casus Belli, Warscore Pillars & Call for Peace",
                "html": f"""
<p>无理由宣战（No CB）基础账单高达 <strong>−15 稳定度 + +1 厌战 + 巨额周边敌意震荡</strong>（撕毁 5–10 年停战更是重罚 <strong>−50 稳定度</strong>！除非你是力量投射占绝对碾压的高阶大国吃小国拿了宣战减免）。常规获取 {T('casus_belli','宣战理由')} 有三条：① 派间谍网攒够 <strong>20 点</strong> 后按每月 +4% 推进伪造出限期 120 个月（收复核心或议会批文单独算）的合法宣战名分；② 借议会请求表决当场白领一个省宣称；③ 宿敌羞辱或宗教圣战。</p>
<ul>
  <li><strong>总战争分数（最高 100）三大块</strong>：① <strong>{T('war_goal','战争目标')}跳分</strong>（每月 +2，最高累计到 +25 与 +50 上限，取决于先达标者）；② <strong>野战战斗得分</strong>（累计上限封顶 <strong>50 分</strong>）；③ <strong>占领敌国地点价值</strong>（按地点税基最高计6分、建筑最高10分、人口最高4分、首都 +5 分、省会 +1 分、港口 +1 分与要塞等级加总，被全面占领后缩放至 100）。</li>
  <li><strong>无条件投降与「和平呼吁」</strong>：若某方已被打到 <strong>{T('unconditional_surrender','无条件投降')}</strong>（敌全境易手战分直接跳满 100%，降军全体进入 {T('exile','流亡')} 不可作战），获胜方如果在数个月（默认仅 2 个月缓冲）后还贪心拖着不发和约，或占优方战分 ≥67% 拖战超过 60 个月，将会立刻被强施极高额的「和平呼吁（Call for Peace）」，每月暴涨自身 {T('war_exhaustion','厌战度')}（每 1 点厌战令陆海军士气 <strong>−2.5%</strong>、全国阶层满意均衡 <strong>−1%</strong>、全国防御 <strong>−2.5%</strong>）倒逼立刻签约停战！</li>
</ul>
"""
            },
            {
                "id": "peace-terms",
                "title": "05 · 和平条约战分折扣与三大隐藏成本规则",
                "en": "Peace Treaty Costs, Discounts & Inflation",
                "html": f"""
<p>打开 {T('peace_offer','和平提议')} 窗口时（最少需 ≥10 分战分方可强提要求；单边议和需等开战满 12 个月后），懂得以下精确乘数能让你每次打赢多吞 30–50% 的土地而不吃暴怒（<code>00_defines.txt NWar & NDiplomacy</code>）：</p>
<table class="data-table">
  <thead><tr><th>条约修正条款</th><th>战分花费 / 效率乘数</th><th>实战规划意义</th></tr></thead>
  <tbody>
    <tr><td><strong>割让未被占领要塞附近地</strong></td><td class="neg"><strong>−15%</strong> 效率（若整场战争从未派兵去围过再叠 <strong>−18% → −33%！</strong>）</td><td>哪怕不打算彻底拔下某座边陲高防要塞，派 1 支小队上去踩过一眼也能把 −33% 重罚缩回 −15%</td></tr>
    <tr><td><strong>强令放弃/归还核心</strong></td><td class="pos">归还核心 <strong>0.50×</strong> 倍率 / 撤销核心 <strong>0.25×</strong> 倍率</td><td>借已有核心或放死敌历史上亡国小附庸，再用低倍率「归还核心」半价吃回大片肥地</td></tr>
    <tr><td><strong>宿敌 &amp; 决定性防御方 &amp; 非联合作战</strong></td><td>宿敌割地 <strong>+33% 效率</strong> / 原防御反杀 <strong>+25% 效率</strong>；非联合作战盟友 <strong>−50%</strong></td><td>战前把必吃目标挂成宿敌能省三分之一战分；想吞对方盟友大块土地务必在开战弹窗勾选将其设为 <strong>{T('cobelligerent','联合作战国')}</strong>！</td></tr>
    <tr><td><strong>大帝国体量拆解折扣</strong></td><td class="pos">目标总战争价值 &gt; 100 起渐增，最高享 <strong>+50% 成本效率（约 −33% 战分降价）</strong></td><td>中后期殴打超级奥斯曼或大明这样的巨无霸时，割土面积会随对方总盘子变大显著变便宜</td></tr>
    <tr><td><strong>和约直接索赔巨额金币</strong></td><td>最多只占 25 战分（上限 2 年对方收入 / 5× 贷额）；另加 <strong>战争赔款 10% 月收</strong></td><td><strong>隐秘坑点</strong>：按获赔月收入基数比例，和约敲诈一大笔现钱会给你自己国库<strong>直接凭空加出通货膨胀</strong>（<code>INFLATION_FROM_PEACE_GOLD = 0.0002</code>）！</td></tr>
  </tbody>
</table>
"""
            },
        ],
        "discussion": {
            "title": "论坛实战讨论与排障 · 为什么打了 100% 全歼战果，对手国力微调却死活要不到首都周边大城？",
            "html": """
<ul>
  <li><strong>两个最常忘记勾选的细节</strong>：<br>
  ① <strong>和约条款提示“该地块所属要塞未曾被占领（Unoccupied Fort −33%）”</strong>：在 EU5 中哪怕整块省本身是平地，只要它恰好处在敌方相邻某座完好 3 级城堡的 ZoC（或同地区防御覆盖）内，且那座城堡你整场战争一兵没派去碰过，割这块平地都要被迫挨一刀狠的 −33% 战分惩罚！停火前先派炮兵顺路拔掉那颗钉子吧。<br>
  ② <strong>战时忘把敌方强力盟友标成「联合作战国」</strong>：向没挂联合作战国的参战附带国割地，成本直接翻倍（−50% 效率）外加周边仇恨怒火暴涨 +20%！</li>
</ul>
"""
        },
        "quick_links": [
            ("78 种战争目标全表", "ledgers.html#wargoals"),
            ("113 种宣战理由全表", "ledgers.html#casus_belli"),
            ("72 项和平条约名录", "directory.html#peace_treaties"),
            ("海权、封锁与和约因果星图", "map.html#navy_maritime"),
        ],
    },

    {
        "id": "ch10",
        "slug": "ch10-diplomacy-subjects.html",
        "num": "10",
        "pillar": "diplomacy",
        "title": "外交容量、联盟饱和、敌意包围网、属国连通与邦联/国际组织",
        "en": "Diplomacy, Alliance Saturation, Antagonism, Subjects, PUs & IOs",
        "subtitle": "不仅要防范同盟列强的外交容量饱和、看透 25 点间谍网与 50 敌意包围网，更要掌握用属国减半 AE、维持属国领土连通与共主邦联的议会补课艺术。",
        "upstream": [
            ("国家等级、列强点数与威望", "ch04-government-cabinet.html#government-power", "定外交官上限、宿敌资格、区域强权(20)与列强(40)席位"),
            ("战争割地账单与无名分扩张", "ch09-navy-war-peace.html#peace-terms", "每场扩土或无理由开战给邻国落下核心敌意(AE)"),
            ("中央集权 vs 地方分权轴", "ch04-government-cabinet.html#societal-values", "极端影响属国忠诚（−20 vs +30）与外交吞并速度"),
        ],
        "engine": "在联盟集团饱和度约束下挑选盟友、靠间谍掀开信息迷雾、将敌意按属国割让截流减半、治理需 0–100 领土连通与 20% 实力平衡约束的 22 种属国，并在邦联/神罗行政圈/教廷多边机制内夺取主导权。",
        "downstream": [
            ("跨国盟军火力与参战防御", "ch09-navy-war-peace.html#warfare-peace", "同盟/属国分担战场但须按参战贡献分配战果免扣信任"),
            ("免去内阁压力的无痛版图消化", "ch01-territory-core.html#integration-core", "属国替宗主同化整合，吞并瞬间全盘继承属国核心"),
            ("国际组织全球投票权与五霸权", "ch06-culture-religion.html#religion-system", "争雄神罗皇权、天朝朝贡体系或跻身五大世界霸权"),
        ],
        "redlines": [
            ("强盟 1.0 / 0.5", "联盟集团饱和度", "列强盟友计 1.0 权重、区域强权计 0.5；总权重 > 1.0 每超 1 点对每份同盟追收 +0.3 容量！"),
            ("25 点间谍网", "信息迷雾透视门", "间谍网达 25 点才掀开守军/要塞等级/兵力与补给迷雾，并开始伴随每年 25% 暴露几率"),
            ("50 敌意 & −50 好感", "包围网双条件门禁", "同时满足对我敌意 >50 且好感 <−50 方能进包围网；平和期敌意降至 <30 退出。割属国减 −50% AE"),
            ("20% 集团 / 35% 控", "属国忠诚与吞并门", "全体属国超宗属总力 20% 按 −60 倍率狂扣忠诚；吞并需好感≥190、满年限且交界控制 ≥35%"),
        ],
        "sections": [
            {
                "id": "diplo-capacity",
                "title": "01 · 外交官、好感信任人情与「联盟集团饱和度」防抱团机制",
                "en": "Relations, Diplomatic Capacity & Alliance Bloc Saturation",
                "html": f"""
<p>外交建立在三大动态关系坐标与一项防超级抱团引擎上：{T('opinion','好感')}（<code>−200 至 +200</code>，≥50 开战扣 −1 稳，≥100 扣 −2 稳，<strong>≥150 时 AI 完全禁止彼此宣战</strong>）；{T('trust','信任度')}（<code>0 至 100</code>，默认回归均衡 50）；{T('favors','人情')}（上限 100，每月自然衰退余额的 1%，低于 0.1 归零）。</p>
<div class="formula-box">
<strong>同盟占用的 {T('diplomatic_capacity','外交容量')} 精确公式（防玩家集邮式联手五个列强）：</strong><br>
<code>单份同盟占用 = 0.5(基数) + clamp(2 × 对方经济基础 ÷ max(己方经济基础, 1), 0.1, 3.0) + (0.5 − 对方对我好感 ÷ 200) + 对方强国额外项 + 强盟饱和罚项</code><br>
• <strong>对方强国额外项</strong>：对方是 <strong>{T('great_power','列强')}（≥40 点列强积分）+1.0</strong>；对方是 <strong>{T('regional_power','区域强权')}（≥20 点，享列强半数加成且限对相邻区域行使列强行动）+0.5</strong>。<br>
• <strong>{T('alliance_bloc','联盟集团')}饱和度</strong>：统计你所有现有同盟（每个列强盟友计 <strong>1.0</strong>、区域强权计 <strong>0.5</strong>）的权重总和——只要超过 <strong>1.0</strong>，超出值每多 1.0 就会给你的<strong>每一条</strong>有效同盟共同加上 <code>× 0.3</code> 容量惩戒！（超过容量立刻重挫威望与外交声誉）。
</div>
<p><em>此外注意 {T('ai_personality','国家性格')} 与 {T('ai_disposition','国家态度')}：AI 态度的警惕/恐慌切换均设防抖滞后带（0.15），且一旦好感或信任 ≥75 即倾向进入友好态。另设 <strong>{T('betrothal','订婚')}</strong> 机制：两国可为未满 16 岁的皇室子女预先订下婚约，待双方同时跨过成年岁数且配偶、宗教与特质条件符合时自动转成正式王室联姻。</em></p>
"""
            },
            {
                "id": "intelligence-fow",
                "title": "02 · 间谍网「25 点信息迷雾门」与秘密行动代价",
                "en": "Spy Networks & The 25-Intel Fog of War",
                "html": f"""
<p>其他国家的真实内政细节在 EU5 中并非免费敞开，而是默认藏在 <strong>{T('spy_network_fog','信息迷雾')}</strong> 之后：</p>
<ul>
  <li><strong>潜伏与衰减</strong>：派遣外交官对目标建立 {T('spy_network','间谍网')} 基础速度每月 <strong>+1.0 点</strong>（宿敌与特质加速）；停止指派则按每月 <strong>−1.0 点</strong> 自然衰减。</li>
  <li><strong>25 点情报分水岭与 1.4.9 开局状态说明</strong>：信息迷雾在 <code>00_defines.txt</code> 中原设 <strong>5 / 15 / 25</strong> 三档间谍网解锁门（分别看统筹能力 → 税收收入 → 全部地点守军/要塞等级/兵源），不过请注意 <strong>1.4.9 本机版本标准开局规则下默认将其开关整块注释，只保留常规战争迷雾视野规则</strong>；在开启该规则或特定模组下，25 点正式揭示军备数据并触发每年 <strong>25% 暴露风险检定</strong>（被发现即受 12 个月冷却）。至于界面残留文本中的「<strong>国家雄心（Ambitions）</strong>」，经核对 1.4.7–1.4.9 仅见界面提示文本、常规对局尚未定义可选雄心列表，实机行动统一在国家行动（Country Interactions）目录里发起。</li>
  <li><strong>三大地下开销</strong>：伪造标准宣战理由花费 <strong>20 点</strong>、资助叛乱（{T('supportrebels','支持叛军')}）花费 <strong>30 点</strong>、全境清零目标战争迷雾的「{T('infiltrate_administration','渗透行政系统')}」需要 <strong>50 点</strong>。</li>
</ul>
"""
            },
            {
                "id": "antagonism-coalition",
                "title": "03 · 敌意（Antagonism）与 50/−50 包围网入退法则",
                "en": "Antagonism & Coalitions",
                "html": f"""
<p>EU5 的 {T('antagonism','敌意（AE）')} 融合了「<strong>意识形态与文宗差异静态底噪</strong>（同文同教为负减缓，不同文化组 +4、不同宗教 +10、社会价值观背道而驰最高推高 +25）」以及「<strong>割地/无理开战等外交突发震荡</strong>」，最终对各国好感度产生高达 <strong>× −4</strong> 的致命拖拽。</p>
<ul>
  <li><strong>{T('coalition','包围网')}入网与解散双重红线</strong>：一个外国必须处在你的外交范围内、与你当前未交战/未停战/未同属共主邦联，且满足 <strong>① 对你的敌意 &gt; 50</strong> 且 <strong>② 对你的好感 &lt; −50</strong>，才能加入针对你的包围网！一旦处于和平且敌意跌破 <strong>30</strong>（或主心骨退出），该成员会自动撤出包围网。</li>
  <li><strong>三条顶级社区避网泄压招式</strong>：① <strong>给自己的附属国割地（利用战时「转移占领」）使产生敌意直接减半 −50%</strong>（<code>ANTAGONISM_ADDITIONAL_MODIFIER_PEACE_SUBJECT_REDUCTION = -0.5</code>）！② 你的直属宗主国与外交覆盖下的架构几乎不吃你对外扩地的敌意震荡（−90%）；③ 当某老牌列强的列强分数至少比你高出 <strong>2.5 倍以上</strong> 时，人家懒得把你的微末扩张放眼里（大幅豁免）；反之把敌意震荡控制在别引爆多强同时 &gt;50 即高枕无忧。</li>
</ul>
"""
            },
            {
                "id": "subjects-annex",
                "title": "04 · 22 种属国、释放省属国、0–100 连通度与 20% 实力反噬",
                "en": "22 Subject Types, Territory Connectivity & Strength Threshold",
                "html": f"""
<p>并非非要靠战后附庸他人：你随时可主动从国内调用 <strong>「建立省份属国（<code>create_province_subject</code>）」</strong> 或 <strong>「建立建筑属国」</strong> 剥离低控边省减轻内阁重担（全 22 种 {T('subject_type','属国类型')} 的贡赋倍率、同君与外交成本见速查典）。维持属国顺从与顺利吞并严厉依赖两条硬数字（<code>00_defines.txt NDiplomacy</code>）：</p>
<div class="formula-box">
<strong>① {T('subject_territory_connectivity','附属国领土连通度')}（0–100）：</strong><br>
• <strong>陆路连接</strong>：从 100 分起算，首都连通至属国之间每经过一个「地区（Area）」，依据该地区平均控制力扣分——<strong>100% 完全控制地区扣 0 分；0% 无控制地区每个狠扣 20 分！</strong><br>
• <strong>海路连接</strong>：取决于宗主目的港与属国起始港各自的「海上存在」及两港海程距离（完全失联计 0 分）。连通度越高，属国忠诚度越稳；且<strong>发起外交吞并需宗主交界处控制力至少 ≥ 35%</strong>（<code>AI_ANNEX_SUBJECT_BORDERING_CONTROL_NEEDED = 0.35</code>）。<br><br>
<strong>② 全属国集团实力惩戒线（<code>SUBJECTS_STRENGTH_THRESHOLD = 0.20</code>）：</strong><br>
别以为把附庸分开养五个小的就安全——系统将你治下<strong>所有属国算作一个整体 Bloc</strong>，与你的陆军、收入、人口三大支柱对比！一旦全部属国综合占到宗属合体的 <strong>20% 以上</strong>，超出部分直接乘以 <strong>−60 倍率</strong> 狂扣全体属国忠诚！<br>
<em>当任意属国忠诚度跌破 <strong>50</strong>，它立即变为「不忠属国」——拒绝跟打一切战争并彻底卡死吞并读条（吞并标准还需好感 ≥ 190、满立属年限，多线同吞还要吃 −0.5 倍速惩罚）。</em>
</div>
"""
            },
            {
                "id": "pu-and-ios",
                "title": "05 · 共主邦联（PU）两大坑与国际组织（神罗行政圈/天朝/教廷）",
                "en": "Personal Unions, Union Integration Catch-up & International Organizations",
                "html": f"""
<p><strong>共主邦联（{T('union','Personal Union')}）为什么常被社区评价为「比附庸难缠得多」？</strong></p>
<ol>
  <li><strong>不收日常岁贡 + 主导国反转危机</strong>：刚由王室联姻落成的共主邦联只是共戴一君的防御联盟——被联统国 <strong>不向你交一般附庸税</strong>；更可怕的是如果后续被联统国国力反超了你，他会<strong>反客为主夺走联统主导权</strong>并接管整个邦联的外交！</li>
  <li><strong>「{T('union_integration_level','共主邦联整合等级')}」与落后小弟的「议会补课机制」</strong>：主导国在邦联面板每推动一级集中化政策，当时在列成员的整合等级统一 <code>+1</code>。等到推进最后终极合邦政策时，<strong>只有整合等级与主导国平级的被联统国才会一并吞并</strong>！如果你在中途又新增了一位晚入邦联的成员，它会自动卡在较低的成员等级——此时你<strong>必须在邦联页面召开专门的「邦联议会」并通过让它逐级追赶整合进度的议案</strong>，方能最终完整合并！</li>
</ol>
<p><strong>多元 {T('international_organization','国际组织')}、地区权力斗争与五大世界霸权（{T('hegemony','Hegemons')}）</strong>：</p>
<ul>
  <li><strong>神罗 {T('imperial_circle','帝国行政圈')} 与皇帝权柄</strong>：候选地区内至少半数地点由帝国成员持有且经历 <strong>24 个月</strong> 窗口方可成圈；初始投票权 &lt;10 的小圈自动并入邻近较小行政圈，<strong>单一行政圈投票上限卡死全帝国 35%</strong>，活跃成员少于 2 国即转入休眠。神罗皇帝还可损耗成员好感强制「否决帝国议会（<code>overrule_imperial_diet</code>）」。</li>
  <li><strong>意大利战争与直布罗陀海峡主权争霸</strong>：意大利战争按参战联盟领袖动态拉锯紧张度；伊比利亚与北非的「<strong>海峡之战（Battle for the Strait）</strong>」单独跟踪「<strong>格拉纳达主权（0–100，初值 50）</strong>」，每名盟友每月贡献 <code>clamp(0.01 + 列强分数 × 0.0004, 0.01, 0.05)</code> 推力，随后接续「<strong>黄金世纪（Golden Century）</strong>」欧洲/殖民优势角逐；中华天朝体系则围绕 <strong>{T('celestial_authority_gc','天朝威仪')}</strong> 运作六部、圣旨、免贡与宝船远航（另含 1.4.9 宝船按二时代重战舰重构、巴巴里福斯塔载兵 150 人与运宝船队五年冷却实则计入区域内属国金银产出）。位列独立列强且经济/海军（至少 1 重战舰）/陆军/外交/主流文化影响单项居全球之首，即可摘得极具统治力的世界霸权冠冕。</li>
</ul>
"""
            },
        ],
        "discussion": {
            "title": "论坛实战讨论与排障 · 喂属国吃地兼顾避网 + 邦联吞并翻车救援",
            "html": """
<ul>
  <li><strong>如何一口吃下半个法德或巴尔干而让包围网凑不齐人数？</strong><br>
  <strong>社区经典解法「放小弟 + 转移占领喂食」</strong>：在交战占领地盘后、进和平谈判前，点击界面上的占领地点将该地点「<strong>转移占领（Transfer Occupation）</strong>」交给前线己方附庸或封建封邑。和约中直接勾走该地给属国时——① 你本人的敌意震荡直接暴降 <strong>−50%</strong>；② 吃下来的未整合垃圾地立刻由属国替你出钱出内阁整合消化，彻底省下你早期极度珍贵的 2–3 个内阁名额！但注意严控所有属国加起来的总人口与兵力不要冲破 20% 集团惩戒线过多。</li>
</ul>
"""
        },
        "quick_links": [
            ("194 外交行动 & 37 国际组织", "ledgers.html#diplomatic_actions"),
            ("22 种属国属性全表", "ledgers.html#subject_types"),
            ("178 决议 & 22 组织决议名录", "directory.html#decisions"),
            ("属国连通与强盟饱和演算器", "lab.html#calc"),
        ],
    },
]
