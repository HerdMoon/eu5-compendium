# -*- coding: utf-8 -*-
"""
Chapters 11 - 12 for EU5 Mechanics Compendium (1.4.9).
Covers all remaining narrative/operational sections from the original handbook:
  - CH 11: 1337 Scenarios, Starting/Formable Countries (163), 4,213 Events,
           11 National Mission Packs & DLC Expansion Mechanics (Phoenix / Strait / Monuments).
  - CH 12: Game Rules (31), Achievements (87), Map Modes/Ledger Navigation,
           Automation Delegation Matrix, EU4/Vic3 Accounting Bridge & 1.4.8-1.4.9 Changelog.
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
<p>当前手册底层对照基准：<strong>EU5 {escape(str(vu.get("version", "1.4.9")))}</strong>（官方校验码 <code>{escape(str(vu.get("officialChecksum", "3ed0")))}</code> · Steam Build <code>{escape(str(vu.get("steamBuild", "26655995")))}</code> · 对比基线 {escape(str(vu.get("previous", "1.4.7")))} · 发布日 {escape(str(vu.get("date", "")))}）。下表收录全部 <strong>{len(vu.get("checks", []))} 项</strong> 官方 1.4.8–1.4.9 机制修订与源码核对口径：</p>
<table class="data-table">
  <thead><tr><th>版本</th><th>核对主题 / 置信度</th><th>机制更新与代码依据摘要</th></tr></thead>
  <tbody>{checks_rows}</tbody>
</table>
<h3>本轮数据名录刷新汇总（10 类核心表变化）</h3>
<ul>{tc_items}</ul>
<div class="callout warn"><strong>源码与实机核对边界（Verification Limits）</strong>：<ul>{unres_items}</ul></div>
"""


CHAPTERS_11_12 = [
    {
        "id": "ch11",
        "slug": "ch11-scenarios-missions-dlc.html",
        "num": "11",
        "pillar": "diplomacy",
        "title": "开局剧本、成立国家、国别事件、使命链与扩展包机制",
        "en": "Scenarios, Formables, 4,213 Events, Missions & Expansion Mechanics",
        "subtitle": "从 1337 选国标签与 163 个可成立国家门槛，到开局默认关闭但带「快照定标」的国家使命，再到《凤凰宿命》《直布罗陀海峡》与古迹包实机拆解。",
        "upstream": [
            ("开局设定与 87 地区地理框定", "directory.html#starting-scenarios", "1337.4.1–1836.12.31 剧本注入初始首都、政体、疆域与外交"),
            ("文化/宗教与国家经济基准", "ch06-culture-religion.html#culture-status", "锁定成立国家 Potential/Allow 与接取使命瞬间指标"),
            ("历史局势与国家灾难进程", "ch07-ages-colonial.html#situations-disasters", "推动如土耳其崛起、凤凰宿命与海峡之战阶段开关"),
        ],
        "engine": "按「可见(Potential)→执行(Allow)」双重闸门筛选成立与国别事件，用动态接取快照推进 11 条使命链，并在启用的扩展包中调度跨国生死危机与远征竞赛。",
        "downstream": [
            ("成立国家重塑国号、旗帜与革新", "ch04-government-cabinet.html#government-power", "切入更高成立层级、更换显示国号并开放新政体/事件组"),
            ("国别事件永久改写人口与特权", "ch05-estates-rebels.html#estate-interactions", "4,213 项史实分支直接发人物、降稳或授予特殊设施"),
            ("成就解锁资格校验", "ch12-gameplay-automation-updates.html#rules-achievements", "启用通用「使命包」规则会锁定本局常规成就获取"),
        ],
        "redlines": [
            ("1337.4.1 启幕", "标准剧本时间跨度", "起于 1337 年 4 月 1 日，终止于 1836 年 12 月 31 日（含 11 组新手/进阶推荐开局）"),
            ("默认 100% 领土", "成立国家隐含比例", "163 个可成立国家未额外写明比例时默认需占满指定区域 100%（例如埃及需 75%、蒙古需 85%）"),
            ("停10年 / 完20年", "使命链再接冷却与候补", "通用候选池上限 10 项；接取使命时冻结当下比例定标（如海军占幅 +5%）；弃做 10 年 / 完成后 20 年再选"),
            ("≤100 vs ≥150", "凤凰宿命安纳托利亚线", "拜占庭需己方+属国 ≥150 地点，且土库曼/贝伊政体诸侯各自+属国均 ≤100 地点方走出发展线"),
        ],
        "sections": [
            {
                "id": "scenarios-countries",
                "title": "01 · 1337 开局剧本、87 地区名录与 2,354 国家定义体系",
                "en": "1337 Bookmarks, Regions & 2,354 Country Definitions",
                "html": f"""
<p>《欧陆风云 V》的标准 1337 书签从 <strong>1337 年 4 月 1 日</strong> 开始、于 <strong>1836 年 12 月 31 日</strong> 结束（名录库另完整收录 11 组开局推荐场景与 87 个分区国家目录）。在剧本载入时，每个参战主体由两部分文件联合生成：</p>
<ul>
  <li><strong>静态国家定义（2,354 个标签）</strong>：规定主流文化、国教、颜色及可释放或 {T('formable_country','可成立国家')} 后备设定（仅出现在地图上有领土、{T('pop','人口')}、海外建筑或游牧军团的实体，例如汉萨同盟虽以共和政体居吕贝克，却属靠商站存续的「建筑国家」）。</li>
  <li><strong>1337 剧本动态覆写（ownership / control / core）</strong>：同一 {T('location','地点')} 字段严格区分「实际所有权、当前占领控制与历史核心主张」；未逐条写明参数的国家直接承继政体模板初值。</li>
</ul>
"""
            },
            {
                "id": "formables-events",
                "title": "02 · 163 个可成立国家（Potential/Allow）与 4,213 国别事件读法",
                "en": "163 Formable Countries & Reading Country-Specific Events",
                "html": f"""
<p>成立新国家（163 条完整条件见名录库）并不是简单的“换皮按钮”，而要严格过三道引擎审查：</p>
<ul>
  <li><strong>潜在可见（Potential） vs 即时执行（Allow）</strong>：前者决定你的决定栏里能不能看见该按钮（通常检查主流文化、宗教、历史规则开关[史实/合理/幻想]及是否排除现存继承国如马穆鲁克不可点普通成立埃及），后者审查现实占比——如未在脚本指定具体百分比，则默认必须 100% 全控目标地区或集齐首都与核心地标（例如埃及需埃及区域 75%，蒙古与重建蒙古帝国分别要求在对应蒙古区域/帝国版图内控制 85%）。</li>
  <li><strong>国号、标签与成立层级（Rank Tier）</strong>：多条历史路径可以指向同一目标标签却各自写入不同显示国号（如华夏正统王朝国号与天朝体系联动）。</li>
  <li><strong>如何正确读取 4,213 条国别历史事件</strong>：所有动态历史事件均附带触发窗口期与月度基础权重，但是否真弹出还会受到前置事件标记（flag）、统治者/人物存活、具体地点归属以及选项附加触发条件的制约——名录库已逐一整理出日期窗口、月概率与各选项具体数值增减（例如葡萄牙哥伦布事件 1485–1520 年窗口内 5% 月概率检定，拒聘 −5 威望，聘用则注入人物作用域）。</li>
</ul>
"""
            },
            {
                "id": "missions-system",
                "title": "03 · 11 组国家使命包：动态接取快照定标、冷却与成就开关",
                "en": "National Mission Packs, Dynamic Snapshots & Cooldowns",
                "html": f"""
<div class="callout warn"><strong>开局最重要的法则提示：默认「使命包」关闭才是标准成就规则！</strong><br>
与 EU4 固定国树不同，EU5 默认开局规则下 <strong>通用{T('mission','使命')}系统处于关闭状态</strong>（以此保留完整成就资格）；只有玩家主动在开局规则开启「使命包（Mission Packs）」（会立即<strong>锁定成就</strong>），才可从最多 10 个候选名额里按前序挑选 11 组通用或专项使命链。</div>
<ul>
  <li><strong>接取即冻结（Snapshot Benchmark）机制</strong>：大量发展贸易、高效内阁或提升识字率等 {T('mission_task','使命任务')} 会读取你<strong>点击接取当天的账面读数</strong>并写死终点目标！例如通用贸易线的海军份额目标 = <code>接取时比例 + 5 个百分点</code>（封顶 100%，接时 72% 则要求追到 77%）。</li>
  <li><strong>三大通用链与退出冷却</strong>：「羞辱宿敌」「区域扩张」「探索未知」均可绕开卡死的前置（如无自控市场中心时可通过跳过条件转入下一步），但在终止使命后需冷却 <strong>10 年</strong> 方可重选同一使命，完整走完终点任务后则冷却 <strong>20 年</strong>。</li>
</ul>
"""
            },
            {
                "id": "dlc-expansions",
                "title": "04 · 扩展包机制精讲：《凤凰宿命》《直布罗陀海峡》与纪念建筑包",
                "en": "DLC Mechanics: Fate of the Phoenix, Battle for the Strait & Monuments",
                "html": f"""
<ul>
  <li><strong>《凤凰宿命（Fate of the Phoenix）》· 拜占庭生死线</strong>：开局若为拜占庭（<code>BYZ</code>）、处于传统时代且开启该内容包，即激活高危灾难——承受<strong>雇佣兵签约费 +50%、官僚维护成本 +20%、造 CB +20%</strong>与远省抗命/常备军逃兵风险。欲摆脱阴影，必须在安纳托利亚所有土耳其文化/贝伊政体对手及其各级属国合计均 <strong>≤ 100 地点</strong>、土耳其崛起{T('situation','局势')}已止，且拜占庭自身与各级属国合计扩张至 <strong>≥ 150 地点</strong> 后跨入复兴/西部路线。</li>
  <li><strong>《Across the Pillars》· 直布罗陀海峡之战与黄金世纪</strong>：紧盯「格拉纳达主权（0–100，初 50）」，参战三方（卡斯蒂利亚/格拉纳达/摩洛哥）外加各自盟友（每人每月贡献 <code>clamp(0.01 + 列强分×0.0004, 0.01, 0.05)</code>）共同拉锯；此外复兴安达卢斯、雇佣希内特骑兵与信仰志愿军均有严格地理及合约约束，后接「黄金世纪」欧美优势争夺以及「黄金城/青春泉」条件远征。</li>
  <li><strong>古代纪念建筑与圣地外观包辨认原则</strong>：<code>dlc/D015_ancient_monuments_pack</code> 等美术扩展仅负责注册地图 3D 模型与地点插画；该地点的真实属性收益<strong>务必回查圣地记录、艺术品类型或本地独特建筑定义</strong>（如麦加天房的实际效果由圣地条目、重要性 5 及伊斯兰圣地类型三者联合给出）。</li>
</ul>
"""
            },
        ],
        "discussion": {
            "title": "论坛实战讨论与排障 · 成立新国家没改名、使命卡住与拜占庭防爆兵",
            "html": """
<ul>
  <li><strong>为什么按规则吞够了地块却一直看不到「成立国家」按钮？</strong><br>
  逐一核对名录库里的两个分离字段：① 先看「潜在条件（Potential）」是否限定了特定文化组、宗教（或禁用了现有同源继承标签），以及本局开局规则「历史成立国家允许度」有没有把合理/幻想类成立关掉；② 再看「执行条件（Allow）」里的占比是否默认为全控 100%，以及有没有漏掉某个小岛/附庸暂占而非直辖的关键首都点！</li>
</ul>
"""
        },
        "quick_links": [
            ("163 可成立国家全条件名录", "directory.html#formable-countries"),
            ("4,213 国别历史事件名录", "directory.html#country-events"),
            ("11 组使命链 & 87 地区开局", "directory.html#missions"),
            ("2,354 国家资料 & 圣地列表", "directory.html#country-definitions"),
        ],
    },
    {
        "id": "ch12",
        "slug": "ch12-gameplay-automation-updates.html",
        "num": "12",
        "pillar": "territory",
        "title": "开局规则、成就、自动化委任矩阵与 1.4.8–1.4.9 更新总览",
        "en": "Game Rules, Achievements, Automation Matrix, EU4/Vic3 Bridge & 1.4.9 Changelog",
        "subtitle": "把前面 11 章的力学原理真正落地到每局对局：梳理 31 项开局规则与 87 项成就边界、掌握自动化委任开关、跑通 EU4/Vic3 转场对账，并逐条核对 1.4.8–1.4.9 补丁变动。",
        "upstream": [
            ("前 11 章全部核心财务、控制与军政机制", "map.html", "决定你在界面面板上看到每一个红字异常到底对应哪条公式"),
            ("1.4.8–1.4.9 Steam 官方公告与本地 00_defines", "glossary.html", "决定哪些计算已实装修复、哪些文案尚存旧版差异"),
        ],
        "engine": "以「地图模式找异象 → 面板钻取构成 → 账本横向对账 → 自动化托管零碎操作」形成闭环指挥流，并逐条追踪补丁变化。",
        "downstream": [
            ("无错失全自动化运营收益", "ch03-economy-market-trade.html#trade-orders", "在锁定粮食防线与不乱拆核心产粮省的前提下大幅降低后期操作量"),
            ("全游戏 22 表与 72 名录精确反查", "ledgers.html#building_types", "任何具体建筑、兵种、法律、特权、需求权重 3 秒定位源码"),
        ],
        "redlines": [
            ("31 规则 / 87 成就", "铁人成就准入门槛", "开启通用「使命包」或修改关键难度/沙盒开关会直接剥夺本局成就资格；部分特殊成就在 1.4.9 放宽了兼容条件"),
            ("先控 60% × 税 15%", "工坊真进国库汇率", "一座月利 2 杜卡特的造纸行会在 60% 控制 × 15% 有效税率下仅进国库 0.18 杜卡特（补贴 0.25 反而净亏 −0.07！）"),
            ("+200% 港口贸易效率", "1.4.9 重大路径分家", "1.4.9 贸易港口效率翻倍至 +200% 且道路/河运各自取优，行政邻近度港口扣费维持 −50%，两账本彻底独立"),
            ("PATROL 90 vs 100", "唯一未对齐待核边界", "1.4.9 公告将海巡停航形容为 100% 海存，但本机 00_defines.txt 仍为 PATROL_THE_SEAS_THRESHOLD = 90"),
        ],
        "sections": [
            {
                "id": "rules-achievements",
                "title": "01 · 31 项开局规则、87 项成就边界与「地图模式→面板→账本」排障工作流",
                "en": "31 Game Rules, 87 Achievements & UI Diagnostic Workflow",
                "html": f"""
<ul>
  <li><strong>开局规则（31 项）与成就验证</strong>：在选国确认界面，如随意调改战斗时间步进以外的沙盒项或激活了「使命包」，右上角奖杯即标灰；注意区分「本局是否拥有成就资格（Eligibility）」与「局内具体触发达标（Completion）」（如 1.4.8/1.4.9 调整了阿特拉斯成就的政体阈值以及《Getting Things Strait》对海军炮台的兼容判定）。</li>
  <li><strong>高手标准界面诊断三步曲</strong>：① 先开 <strong>地图模式</strong>（经济/税基比率/食物/控制力/市场边界）找出飘红的异常地块；② 点开目标 {T('location','地点')} 与国家侧边栏拆解底层权重构成（分清「当地未受控财富」与「省买粮账单」）；③ 切进统计账本横向对比同名指标，切勿把 A 市场的价格直接套进 B 市场比较。</li>
</ul>
"""
            },
            {
                "id": "automation-matrix",
                "title": "02 · 全系统「自动化委任与预算门禁」逐项策略清单",
                "en": "Complete Automation Delegation & Budget Gates",
                "html": f"""
<p>EU5 的自动化面板并非非黑即白的总开关，绝大多数项支持<strong>「总开关 + 分市场/分省份局部开关 + 预算保留底线」</strong>三层控制。建议按下方实操分级托管：</p>
<table class="data-table">
  <thead><tr><th>系统门类</th><th>可委任子功能项</th><th>底层判断逻辑与预算副作用</th><th>推荐策略</th></tr></thead>
  <tbody>
    <tr><td><strong>经济与金融</strong><br>Economy</td><td>收支平衡 (Balance)、信用管理 (Credit)、市场贸易 (Trade)、关税 (Tariffs)</td><td>信用管理会在国库充裕时还旧债、赤字时自动借阶层贷或发政府债券；市场拥有者才可自动调关税（易错杀关键输入关税）</td><td>信用管理/收支可局部开；<strong>关税关闭</strong></td></tr>
    <tr><td><strong>生产与建造</strong><br>Production</td><td>新建建筑、关停补贴切换、自动扩建建筑/RGO、升级道路/城镇</td><td>AI 易按即期虚高利润狂扩同城同类厂触犯扩建波动性，或误把产粮村升城毁粮仓</td><td>仅对熟稳高控省 RGO 开；<strong>严禁AI自动升城</strong></td></tr>
    <tr><td><strong>阶层与税率</strong><br>Estates</td><td>税收滑块自动化、议会提议响应、阶层贿赂</td><td>自动税收贴紧 50% 满意均衡线防跌破 25% 拒出征召兵，平时最省心；要攒整笔钱冲特权/拆特权时需暂关</td><td class="pos">推荐默认常开</td></tr>
    <tr><td><strong>军事与海巡</strong><br>Military</td><td>征召集结、围城托管、海巡 (Patrol the Seas)</td><td>海巡按 90 存在阈值跑圈即跳走（重要水道请拆 5–10 轻船死蹲 100%）；围城托管易把征召炮灰堆上山地吃高耗粮</td><td>局部平叛可开；<strong>大决战与关键海格手操</strong></td></tr>
    <tr><td><strong>文化宗教外务</strong><br>Diplomatic</td><td>自动改善关系、自动同化/传教选择、殖民迁移补位</td><td>自动改善关系极擅长压制边缘潜在包围网成员好感拉回正区间，减轻手操疲劳</td><td class="pos">关系改善强烈推荐常开</td></tr>
  </tbody>
</table>
"""
            },
            {
                "id": "eu4-vic3-bridge",
                "title": "03 · 从 EU4 与 Victoria 3 转场 EU5 的「四件套对账脑图」",
                "en": "Accounting Bridge from EU4 & Victoria 3 to EU5",
                "html": f"""
<p>如果你带着《欧陆风云 4》的涂色直觉或《维多利亚 3》的供需思维进游戏，下面四个具体算例能立刻打通底层逻辑阻塞：</p>
<ol>
  <li><strong>建一座新工坊能给你进账多少真实金币？</strong><br>
  在 Vic3 视角你看「利润 +2.00 杜卡特」就以为发财了；但在 EU5，必须走完：<code>利润 × {T('market_access','市场接入度')} → 地点财富 × {T('control','控制力')} → 税基 × 有效阶层税率 → 国库税金</code>！假设接满接入度后月赚 <strong>2.00</strong>，省控 <strong>60%</strong>，综合税率 <strong>15%</strong>：实际入库月税仅为 <code>2.00 × 0.60 × 0.15 = 0.18</code> 杜卡特（如果还开着每月 <strong>0.25</strong> 补贴，国库反而净亏 <strong>−0.07/月</strong>！）。</li>
  <li><strong>开采银矿 / 金矿与{T('minting','铸币')}怎样变现？</strong><br>
  贵金属先入市场定价变现成地点财富，同时抬高王室铸币效率上限与拉高基础 {T('inflation','通货膨胀')}压力；过度拉满铸币虽暂充国库却会让全部建筑和维护账单一起涨价。</li>
  <li><strong>打赢战争赔款 + 割地怎么不炸裂经济？</strong><br>
  割入的新地是「征服未整合（最大控制 −10%）」：立刻吃进 {T('economical_base','经济基础')} 抬高全国稳定/外交花费，却几乎产不出税基！大笔现金赔款甚至直加微量通胀；优先抢对方核心高控城市或喂给属国消化。</li>
  <li><strong>为什么打了一场仗国内矿山突然集体缺工停产？</strong><br>
  因为每拉出 1,000 陆军征召兵就是直接把 RGO/工厂里的 1,000 真工人拉上阵死掉了（恢复上限需整整 20 年），在核心人力极贵时宁可花钱雇正规军或战俘佣兵。</li>
</ol>
"""
            },
            {
                "id": "changelog-149",
                "title": "04 · 1.4.8–1.4.9 机制修订清单、名录刷新统计与源码核对边界",
                "en": "1.4.8 - 1.4.9 Patch Changelog & Verification Limits",
                "html": _build_ch12_patch_html()
            },
        ],
        "discussion": {
            "title": "论坛实战讨论与排障 · 后期几百个省卡手了怎么只留关键微操？",
            "html": """
<ul>
  <li><strong>三层混合驾驶模式（最推荐高玩后期配置）</strong>：<br>
  ① 把 <strong>日常阶层税收、自动外交改善关系、非核心殖民/市场微调指令</strong> 安心托管给自动化；② <strong>核心城市升格、关键商品进出口关税与 RGO 定向扩建、主力港口 5 艘一组的海上存在护航船队</strong> 全部死守手动；③ 在每次打开大型扩张战争和约前，习惯性检查右侧省买粮账单与经济比率颜色灯——两分钟就能查清全国哪根血管在漏水。</li>
</ul>
"""
        },
        "quick_links": [
            ("501 建筑全表 · 22 数据典", "ledgers.html#building_types"),
            ("31 开局规则与 87 成就名录", "directory.html#game_rules"),
            ("8 阶级×75 商品需求矩阵", "pop-demand.html"),
            ("37 红线常量 & 4合1模拟器", "lab.html#redlines"),
        ],
    },
]
