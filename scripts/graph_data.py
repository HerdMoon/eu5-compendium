# -*- coding: utf-8 -*-
"""
Core dependency graph (36 hub concepts across 6 pillars), 36 game-changing redline thresholds,
and 16 player troubleshooting diagnostics for EU5 1.4.9.
"""
import json
import os

PROJ_DIR = r"C:\Users\seepath\.gemini\antigravity\scratch\eu5-compendium"
DATA_DIR = os.path.join(PROJ_DIR, "data")

PILLARS = [
    {"id": "territory", "zh": "疆域与控制", "en": "Territory & Control", "color": "#1d6b6e", "bg": "rgba(29,107,110,0.12)"},
    {"id": "economy", "zh": "人口、市场与财政", "en": "Population, Market & Finance", "color": "#b06c1d", "bg": "rgba(176,108,29,0.12)"},
    {"id": "state", "zh": "政府、内阁与阶层", "en": "State, Cabinet & Estates", "color": "#9b2c3d", "bg": "rgba(155,44,61,0.12)"},
    {"id": "culture", "zh": "文化、信仰与科技", "en": "Culture, Faith & Tech", "color": "#5c4687", "bg": "rgba(92,70,135,0.12)"},
    {"id": "military", "zh": "军事、海权与和约", "en": "Military, Navy & War", "color": "#3d5467", "bg": "rgba(61,84,103,0.12)"},
    {"id": "diplomacy", "zh": "外交、属国与秩序", "en": "Diplomacy, Subjects & IOs", "color": "#1f4e8c", "bg": "rgba(31,78,140,0.12)"},
]

# 36 Hub Concept Nodes laid out in a clean 6-column x 6-row grid (viewBox 1380 x 840)
# X columns: 130, 355, 580, 805, 1030, 1255  (spacing 225px, box width ~168px)
# Y rows: 95, 220, 345, 470, 595, 720       (spacing 125px, box height ~58px)
NODES = [
    # Column 1: Territory & Control (x=130)
    {
        "id": "location", "zh": "地点基础", "en": "Location", "pillar": "territory", "x": 130, "y": 95,
        "href": "ch01-territory-core.html#hierarchy",
        "summary": "地图最小行政单元：承载地貌、植被、气候、原产(RGO)、人口与所有建筑。",
        "formula": "五级嵌套：地点 Location → 省份 Province → 地区 Area → 区域 Region → 次大陆/大陆",
        "redline": "同一预设省份被多国瓜分时，各国在当地独立生成自己的省会与省粮仓。",
    },
    {
        "id": "proximity", "zh": "邻近度", "en": "Proximity", "pillar": "territory", "x": 130, "y": 220,
        "href": "ch01-territory-core.html#proximity",
        "summary": "衡量首都/历史首都/地方总督治所沿陆海路线辐射到地点的行政可达性（0–100%）。",
        "formula": "到达值 = 来源强度 − 各段地理/地形成本；陆路依赖道路/发展度，海路依赖港口容量与海上存在",
        "redline": "邻近度百分数 × 0.75 直接构成最大控制力的主干部分（100 邻近度贡献 +75% 上限）。",
    },
    {
        "id": "integration", "zh": "整合四态", "en": "Integration Status", "pillar": "territory", "x": 130, "y": 345,
        "href": "ch01-territory-core.html#integration-core",
        "summary": "所有领土必居四态之一：未整合（征服）→ 殖民地 → 已整合 → 核心。",
        "formula": "未整合(max ctrl −10%) —[MIL内阁整合]→ 已整合(+5%) —[主流/接纳文化≥50%]→ 核心(+20%)",
        "redline": "单省超过 5 个地点会拖慢整合速度；爆发叛乱立刻倒扣 10 点整合进度。",
    },
    {
        "id": "core", "zh": "核心领土", "en": "Core", "pillar": "territory", "x": 130, "y": 470,
        "href": "ch01-territory-core.html#core-power",
        "summary": "国家不可分割的根基领土：提供 +20% 最大控制并决定殖民移民来源与自然人口同化。",
        "formula": "前置：已整合(Integrated) 且 主流/已接纳文化人口占比 ≥ 50%（CORE_THRESHOLD=0.5）",
        "redline": "唯有核心地点能向特许殖民地输送移民；核心自然出生人口 100% 属主流文化；被占领仍保视野。",
    },
    {
        "id": "control", "zh": "控制力", "en": "Control", "pillar": "territory", "x": 130, "y": 595,
        "href": "ch01-territory-core.html#control",
        "summary": "国家从地点抽取税基、征召兵、人力与水手的核心比例系数，按月趋近最大控制力。",
        "formula": "税基 = 地点财富 × 控制力；未受控财富 = 地点财富 × (1 − 控制力) → 直接流入当地阶层金库",
        "redline": "控制力 ≥ 75% 时王室可直接拆除阶层建筑；控制力 < 75% 时不满阶层会自行建造阶层建筑。",
    },
    {
        "id": "town_rights", "zh": "城镇特权与升城", "en": "Town Rights & Rank", "pillar": "territory", "x": 130, "y": 720,
        "href": "ch01-territory-core.html#urbanization",
        "summary": "乡村/城镇/城市/大都会等级决定建筑上限与市民岗位，探索时代可授城镇特权专精产业。",
        "formula": "默认特权槽位：城镇 1 个、城市 2 个、大都会 3 个；建筑上限随等级与发展度提高",
        "redline": "升格城镇会降低食物产出加成并减少农业用地，粮食主产区升城前需核算省粮平衡。",
    },

    # Column 2: Population, Food, Economy & Market (x=355)
    {
        "id": "pop_cap", "zh": "人口与阶级", "en": "Pops & Classes", "pillar": "economy", "x": 355, "y": 95,
        "href": "ch02-population-food.html#population-base",
        "summary": "由社会阶级、文化、宗教三维切分的人群集合，决定劳动产出、士兵池与政治力量。",
        "formula": "人群需至少属「相容文化」且地点有空缺岗位方能由平民向上级阶级（市民/教士/贵族/士兵）升级",
        "redline": "人口超过人口容量停涨或负增长；每千人征召兵阵亡永久扣减当地对应真实人群。",
    },
    {
        "id": "food_system", "zh": "三级粮食链", "en": "Food Stockpile", "pillar": "economy", "x": 355, "y": 220,
        "href": "ch02-population-food.html#food-chain",
        "summary": "地点 → 省份 → 市场三级流转的民生口粮与军需补给体系，直接联动财政收支。",
        "formula": "省粮仓盈余(>75%且满仓)自动卖给市场换取收入；赤字且未被围攻时自动由国库按市价买粮",
        "redline": "省粮仓归零触发饥荒：人口 -5%/月、补给上限 -25%、移民吸引 -1.0、上层阶级 -50%。",
    },
    {
        "id": "prosperity", "zh": "繁荣与荒废", "en": "Prosperity", "pillar": "economy", "x": 355, "y": 345,
        "href": "ch02-population-food.html#prosperity-devastation",
        "summary": "介于 −100% 与 +100% 的地方景气指数：正值催生发展度与移民，负值即荒废重创产出。",
        "formula": "正繁荣靠和平与高人群满意度自然缓慢增长；战乱荒废需 DIP 内阁「灾后恢复」(+5%/月)挽救",
        "redline": "被敌军劫掠施加 12 月 looted 修正：人口 -0.5%/月、繁荣衰减 +0.1、月发展 -25%。",
    },
    {
        "id": "production", "zh": "原产与工坊", "en": "RGO & Buildings", "pillar": "economy", "x": 355, "y": 470,
        "href": "ch03-economy-market-trade.html#production-buildings",
        "summary": "RGO 采集原材料（1,000劳工/奴隶/级），建筑加工制成品或提供国家机制设施。",
        "formula": "加工产出 = 满接入产出 × 市场接入度 × 就业比例 × (1 + 生产效率 + 投产度加成)",
        "redline": "扩建需看「扩建波动性」预判 6 个月价格冲击；亏损且无补贴建筑每月裁员 10% 并流失投产度。",
    },
    {
        "id": "market_access", "zh": "市场接入度", "en": "Market Access", "pillar": "economy", "x": 355, "y": 595,
        "href": "ch03-economy-market-trade.html#market-network",
        "summary": "地点到所属市场中心的物流畅通度，直接按比例缩放本地售价与工坊吞吐量。",
        "formula": "普通传输基础损失(百分点) = 像素距离 × 0.5（经道路/河流/海运/1.4.9港口+200%效率修正）",
        "redline": "低市场接入度不但打折当地利润，还会让本地建筑在市场缺货时抢不到原料而被迫停工。",
    },
    {
        "id": "trade_system", "zh": "贸易与关税", "en": "Trade & Tariffs", "pillar": "economy", "x": 355, "y": 720,
        "href": "ch03-economy-market-trade.html#trade-orders",
        "summary": "按贸易优势排序出口抢货、按贸易容量运送商品跨市套利，并受关税与补贴调控。",
        "formula": "每份贸易利润 = 售价 − 买价 − 维护 − 关税/海峡税；王室按「王室力量份额」分成，余下归阶层",
        "redline": "利用「贸易指令 (Trade Orders)」设最低利润门槛自动寻优；市场所有者可设 10/25/50% 关税锁货。",
    },

    # Column 3: Finance, State & Cabinet (x=580)
    {
        "id": "wealth_tax", "zh": "财富与税基", "en": "Wealth & Tax Base", "pillar": "economy", "x": 580, "y": 95,
        "href": "ch03-economy-market-trade.html#wealth-to-treasury",
        "summary": "将地方工农业利润按控制力切分为国家税基与阶层金库收入的财政核算核心。",
        "formula": "税基 = (原产利润 + 建筑利润 + 市民贸易) × 控制力；实收税款 = 阶层税基 × 税率 × 税收效率",
        "redline": "税基比率（实收税基 ÷ 经济基础）< 25% 显示红标，提示高产区控制力偏低。",
    },
    {
        "id": "debt_credit", "zh": "借贷、债券与信誉", "en": "Loans, Bonds & Credit", "pillar": "economy", "x": 580, "y": 220,
        "href": "ch03-economy-market-trade.html#finance-debt",
        "summary": "涵盖 5 年期阶层贷款、中央银行无到期日政府债券与 0–100 国家信誉度体系。",
        "formula": "破产 → 稳定度 −50、控制力 −33%、信誉度直降 50 点；按年仅恢复 0.5 点（需 100 年抹平）",
        "redline": "信誉度跌破 30 后外国 AI 拒绝放贷；短期缺钱优先用向市民无息紧急拨款（不占贷额）。",
    },
    {
        "id": "gov_power", "zh": "政体与政府力量", "en": "Government Power", "pillar": "state", "x": 580, "y": 345,
        "href": "ch04-government-cabinet.html#government-power",
        "summary": "君主正统性、共和传统、神权奉献度、游牧团结与部落凝聚力决定治国稳定底座。",
        "formula": "随不同政体升降，用于维持修正、任免人物、应对事件与防止体制崩溃",
        "redline": "共和传统过低有沦为独裁风险；驱逐或处决角色会在 2 年内叠加政府力量成本。",
    },
    {
        "id": "societal_values", "zh": "社会价值观", "en": "Societal Values", "pillar": "state", "x": 580, "y": 470,
        "href": "ch04-government-cabinet.html#societal-values",
        "summary": "17 对 −100 至 +100 双向意识形态轴线，深层改写王室力量、控制衰减、军事与贸易倾向。",
        "formula": "向极点推进受惯性阻力(100)限制，位置越高需越强推动力才能维持或继续偏移",
        "redline": "集权极点赋予 +50% 王室力量与 +20% 邻近传播但 −20 属国忠诚；重质量/海军直接重塑国策。",
    },
    {
        "id": "bureaucracy", "zh": "官僚部门与固化", "en": "Bureaucracy & Entrench", "pillar": "state", "x": 580, "y": 595,
        "href": "ch04-government-cabinet.html#bureaucracy",
        "summary": "需按月付费维护的行政分支机构，存在正负双面修正与随百年积累的固化成本。",
        "formula": "维护率 m → 正向修正生效 m，负向修正生效 (1−m)；固化度每 100 年进阶并抬升维护与撤销价",
        "redline": "经费不足的官僚机构只触发负面修正；固化太高后强行裁撤代价极其高昂。",
    },
    {
        "id": "cabinet", "zh": "内阁与角色互动", "en": "Cabinet & Characters", "pillar": "state", "x": 580, "y": 720,
        "href": "ch04-government-cabinet.html#cabinet-actions",
        "summary": "稀缺的内阁席位统筹省份整合、灾后恢复、提控与同化；34 项角色互动掌控继承与总督。",
        "formula": "政治影响力由统治者+内阁平均能力月产（上限100）；内阁效率受王室力量、首相与价值观加成",
        "redline": "提拔内阁首脑需任职满 10 年，效果翻倍（+25%效率、特质×2）但此后不可踢出内阁。",
    },

    # Column 4: Estates, Rebels, Culture & Tech (x=805)
    {
        "id": "crown_estate_power", "zh": "王室 vs 阶层力量", "en": "Crown vs Estate Power", "pillar": "state", "x": 805, "y": 95,
        "href": "ch05-estates-rebels.html#power-balance",
        "summary": "同一批居民同时算阶层力量与(控制力加权后)王室力量，王室份额决定税贸与内阁大权。",
        "formula": "王室份额 = 王室最终点数 ÷ (王室最终点数 + 各阶层点数总和)；议会基础支持 = 王室份额 × 0.5",
        "redline": "委任某阶层人物入阁或带兵立刻增加该阶层 +25% 基础力量；特权给得越多王室越贫弱。",
    },
    {
        "id": "estate_pool", "zh": "阶层金库与建筑", "en": "Estate Gold & Buildings", "pillar": "state", "x": 805, "y": 220,
        "href": "ch05-estates-rebels.html#estate-wealth",
        "summary": "承接税后结余、贷款利息与未受控财富的阶层资金池，用于建造公共经济建筑或阶层专属建筑。",
        "formula": "阶层造价 = 常规 4 倍；满意度与财富影响高时造经济建筑，偏低时在 <75% 控制地造阶层建筑",
        "redline": "高财富影响可用「请求紧急拨款」无息提取市民最多 50% 金库；可用「削减阶层力量」批量拆除阶层建筑。",
    },
    {
        "id": "estate_actions", "zh": "阶层满意度与互动", "en": "Estate Satisfaction", "pillar": "state", "x": 805, "y": 345,
        "href": "ch05-estates-rebels.html#estate-interactions",
        "summary": "阶层对统治的满意指数，决定征税上限、是否交征召兵，也是 12 项直接互动与绝境求助筹码。",
        "formula": "授特权即时 +3×Δ 满意度(他阶 −1.5×Δ)；撤特权暴跌 −25%−3×Δ；防御战绝境行动耗费与扣满减半",
        "redline": "满意度 < 25% 该阶层直接拒绝提供陆海军征召兵；< 1% 无法收税。",
    },
    {
        "id": "rebels", "zh": "人口满意与叛乱", "en": "Pop Satisfaction & Rebels", "pillar": "state", "x": 805, "y": 470,
        "href": "ch05-estates-rebels.html#rebellions",
        "summary": "个人群体的满意度（受阶层、文化、宗教、物价、分离主义影响）是叛乱运动的燃料。",
        "formula": "群体满意度 = 20% + 阶层贡献 + 文化地位/好感 + 宗教容忍 + 物价供需 − 动乱/分离主义",
        "redline": "叛乱满100%若支持人口<5,000只触发小规模叛乱；≥5,000爆发起义并掷要塞守军忠诚检定(10–90%)。",
    },
    {
        "id": "culture_lang", "zh": "文化、同化与语言", "en": "Culture & Language", "pillar": "culture", "x": 805, "y": 595,
        "href": "ch06-culture-religion.html#culture-status",
        "summary": "主流/已接纳/相容/受忽视/受歧视五级待遇决定人口满意度、升级资格与核心化门槛。",
        "formula": "文化战争强度取决于 我方文化影响力 vs 敌方文化传统；礼仪语言力量主导研究速度",
        "redline": "仅有「主流」与「已接纳」文化计入 50% 核心门槛，「相容文化」可征召与升阶但无法核心化！",
    },
    {
        "id": "religion_orders", "zh": "宗教、容忍与修会", "en": "Religion & Orders", "pillar": "culture", "x": 805, "y": 720,
        "href": "ch06-culture-religion.html#religion-system",
        "summary": "正统/异端/异教三级容忍度影响人口与外交；宗教修会凭热忱与据点赋予圣召正负全局修正。",
        "formula": "宗教统一度按地点控制力加权（最低 5%）；皈依与同化互相促进（特定宗教绑定文化须先改信）",
        "redline": "跨国修会忠诚时赐福国家，不忠堕落时同样圣召会变成按国家体量缩放的沉重负面负担。",
    },

    # Column 5: Research, Colonization, Military & Combat (x=1030)
    {
        "id": "ages_research", "zh": "时代、思潮与革新", "en": "Ages & Research", "pillar": "culture", "x": 1030, "y": 95,
        "href": "ch07-ages-colonial.html#ages-institutions",
        "summary": "六大时代限制革新池：须思潮发源、经贸易或内阁研究传播并被 20% 人口接纳方能解锁。",
        "formula": "研发进度取决于 礼仪语言力量 + 国家平均识字率 + 教士满意度 + 已接纳思潮数量",
        "redline": "接纳思潮硬门槛为「思潮完全传播地点的总人口占比 ≥ 20%」；未选革新时会储备研究力。",
    },
    {
        "id": "colonization", "zh": "探险与特许殖民", "en": "Exploration & Colony", "pillar": "culture", "x": 1030, "y": 220,
        "href": "ch07-ages-colonial.html#colonial-charters",
        "summary": "以海军范围探索未知，借特许殖民地持续从核心地点迁出人口完成海外领土定居。",
        "formula": "完全定居条件：本地人口 ≥ 1,000 且 国教与主流/接纳文化占比跨过随力量投射降低的门槛",
        "redline": "每省最多 3 个特许殖民地同时竞争；非核心地点绝对无法作为殖民移民源！",
    },
    {
        "id": "army_composition", "zh": "征召、正规与佣兵", "en": "Levies, Regulars & Mercs", "pillar": "military", "x": 1030, "y": 345,
        "href": "ch08-military-combat.html#force-types",
        "summary": "四类兵源的战力、成本与人口代价博弈：征召兵省钱伤本，正规军昂贵而强韧可补员。",
        "formula": "征召兵战力=正规 75%（海战仅 5%）、训练度 −20%、无补员、解散或覆灭需 240 个月恢复",
        "redline": "同一「部队族系」共享招募上限（跨代升级不占新名额）；战俘可按 0.25x 低价收编为佣兵。",
    },
    {
        "id": "land_combat", "zh": "阵位战斗与歼灭", "en": "Land Combat", "pillar": "military", "x": 1030, "y": 470,
        "href": "ch08-military-combat.html#battle-mechanics",
        "summary": "中军/左翼/右翼/预备队四阵位战斗：经过开幕炮击后，每轮判定主动性接战与预备队填补。",
        "formula": "每日接敌率 = 60% + min(30%, 有效主动性 × 2.5%) + 3% × 战斗天数；每多 1 个混编兵种获加成",
        "redline": "开战首拍 10:1 兵力直接全歼；士气崩盘时只需 2:1 兵力即可触发追击全歼（Overrun）。",
    },
    {
        "id": "siege_logistics", "zh": "围城、后勤与焦土", "en": "Siege & Logistics", "pillar": "military", "x": 1030, "y": 595,
        "href": "ch08-military-combat.html#siege-supply",
        "summary": "要塞控制区（ZoC）阻断通行；军队依赖省粮、2格补给站或舰队跨海分发食物避免损耗。",
        "formula": "围城兵至少 ≥ 守军（无城防最少 100 人），30天一跳达 20 分攻克；占领瞬间摧毁 90% 本地存粮",
        "redline": "焦土政策使敌军移动耗时 +50% 并断粮；无粮部队每月承受 5% 额外饿死损耗。",
    },
    {
        "id": "navy_maritime", "zh": "海军、存在与私掠", "en": "Navy & Maritime", "pillar": "military", "x": 1030, "y": 720,
        "href": "ch09-navy-war-peace.html#maritime-presence",
        "summary": "承担制海、运输与封锁职能，同时通过海上存在降低近岸海格的邻近度传播损耗并压制私掠。",
        "formula": "港口和平自然累积海上存在，海军传统满值 +50% 加成；舰船反海盗属性按月消磨私掠耐久",
        "redline": "常量定义 PATROL_THE_SEAS_THRESHOLD = 90（1.4.9 补丁说明称巡逻至 100%）；关键航道建议驻舰维持满值。",
    },

    # Column 6: War, Peace, Diplomacy & IOs (x=1255)
    {
        "id": "war_peace", "zh": "战分、CB与和约", "en": "Warscore & Peace", "pillar": "military", "x": 1255, "y": 95,
        "href": "ch09-navy-war-peace.html#warfare-peace",
        "summary": "宣战理由设定战分账单与目标，战斗（上限 50）、占领与目标跳分（上限 25）汇总 100 分。",
        "formula": "未占领要塞令当地割地效率 −15%（从未围攻再减 −18% 合计 −33%）；归还核心仅 0.5x 花费",
        "redline": "无理由开战暴扣 15 稳定与敌意；战争索取巨额赔款会按月收入比例给本国带来通胀！",
    },
    {
        "id": "diplo_bloc", "zh": "外交容量与盟友团", "en": "Diplomacy & Alliance Bloc", "pillar": "diplomacy", "x": 1255, "y": 220,
        "href": "ch10-diplomacy-subjects.html#diplo-capacity",
        "summary": "好感/信任/人情搭建双边关系，列强同盟受联盟集团饱和度递增惩罚防超级抱团。",
        "formula": "强盟权重：列强盟友计 1.0、区域强权计 0.5；超 1.0 权重每多 1 点为全同盟增 +0.3 容量消耗",
        "redline": "超越外交容量将持续惩罚外交声誉与威望；好感 ≥150 时 AI 禁止彼此宣战。",
    },
    {
        "id": "spy_intel", "zh": "间谍网与信息迷雾", "en": "Spy Network & FoW", "pillar": "diplomacy", "x": 1255, "y": 345,
        "href": "ch10-diplomacy-subjects.html#intelligence-fow",
        "summary": "每月 +1 点渗透敌国，既是制造 CB、支持叛军的资源，更是掀开信息迷雾的唯一钥匙。",
        "formula": "20 点造普通 CB、30 点支持叛军、50 点渗透行政移除战争迷雾；停建则每月 −1 衰减",
        "redline": "间谍网达到 25 点方能看清敌国守军、要塞等级、兵力上限与传统，但同时触发每年 25% 暴露检定。",
    },
    {
        "id": "antagonism", "zh": "敌意与包围网", "en": "Antagonism & Coalition", "pillar": "diplomacy", "x": 1255, "y": 470,
        "href": "ch10-diplomacy-subjects.html#antagonism-coalition",
        "summary": "替代旧作 AE 的动态仇恨与意识形态差异体系（对好感乘数 −4），触发多国联合防御圈。",
        "formula": "入网门禁：对我敌意 > 50 且 好感 < −50（未处于战争/休战/联统）；降至 < 30 方可平和退网",
        "redline": "和约把土地直接割给己方附属国可减少 50% 敌意震荡！列强比你强 2.5 倍以上时不太在乎。",
    },
    {
        "id": "subjects_connectivity", "zh": "属国连通与实力", "en": "Subjects & Connectivity", "pillar": "diplomacy", "x": 1255, "y": 595,
        "href": "ch10-diplomacy-subjects.html#subjects-annex",
        "summary": "22 种附属国分摊内阁整合压力并缴贡赋，受领土连通度（0–100）与实力集团平衡双约束。",
        "formula": "陆路连通从 100 起算，每经过 1 个 0% 控制地区扣 20 分；全属国在军力/收入/人口超总和 20% 触发惩罚",
        "redline": "忠诚度 < 50 变为不忠属国：拒绝参战且冻结吞并；外交吞并需交界控制力 ≥ 35% 且耗费好感 190。",
    },
    {
        "id": "unions_ios", "zh": "共主邦联与国际组织", "en": "Unions & IOs", "pillar": "diplomacy", "x": 1255, "y": 720,
        "href": "ch10-diplomacy-subjects.html#pu-and-ios",
        "summary": "共享君主但不直接交税的共主邦联，以及神罗（含帝国行政圈）、教廷、中华天朝多边舞台。",
        "formula": "邦联通过集中化法律推进整合等级，晚入邦联的落后成员必须通过邦联议会逐级议案追赶",
        "redline": "小心联统反转：被联统国若国力反超你会自动篡夺联统主导权！神罗单一行政圈投票权封顶 35%。",
    },
]

# Directed edges (from, to, label)
EDGES = [
    ("location", "proximity", "地形/道路成本"),
    ("proximity", "control", "×0.75 定上限基数"),
    ("integration", "core", "≥50%核心文化"),
    ("core", "control", "+20%上限/+0.1月控"),
    ("town_rights", "production", "特权专精加成"),
    ("core", "colonization", "独家移民源"),
    ("control", "wealth_tax", "切分税基 vs 阶层金库"),
    ("control", "estate_pool", "未控财富流入阶层"),
    ("pop_cap", "production", "填满RGO/工坊岗位"),
    ("pop_cap", "food_system", "口粮消耗"),
    ("food_system", "prosperity", "盈余促长/饥荒重创"),
    ("food_system", "wealth_tax", "满仓卖/缺粮国库买"),
    ("production", "market_access", "受市中心距离缩放"),
    ("market_access", "wealth_tax", "按接入度折算利润"),
    ("trade_system", "wealth_tax", "市民与王室分润"),
    ("wealth_tax", "debt_credit", "结余决定还贷或举债"),
    ("debt_credit", "control", "破产-33%控制/百年信用"),
    ("gov_power", "bureaucracy", "解锁与政体基石"),
    ("societal_values", "crown_estate_power", "集权+50%王室力量"),
    ("societal_values", "proximity", "集权+20%/陆海偏好"),
    ("bureaucracy", "gov_power", "正负修正随维护切换"),
    ("cabinet", "integration", "MIL行动整合省份"),
    ("cabinet", "control", "ADM行动提控+10%上限"),
    ("cabinet", "prosperity", "DIP灾后恢复除荒废"),
    ("cabinet", "culture_lang", "同化/推广加速核心化"),
    ("crown_estate_power", "trade_system", "王室份额分贸易利"),
    ("crown_estate_power", "cabinet", "提升内阁效率"),
    ("estate_pool", "crown_estate_power", "<75%造阶层建筑增权重"),
    ("estate_actions", "rebels", "阶层不满拉低群体"),
    ("estate_actions", "army_composition", "<25%拒出征召兵"),
    ("rebels", "integration", "起义倒扣-10整合"),
    ("culture_lang", "core", "主流/接纳决定50%核心"),
    ("culture_lang", "ages_research", "礼仪语言加速科研"),
    ("religion_orders", "rebels", "容忍/改信定宗教动荡"),
    ("ages_research", "production", "革新解锁与效率"),
    ("ages_research", "integration", "解锁地区级整合"),
    ("colonization", "trade_system", "殖民货跨市套利"),
    ("army_composition", "land_combat", "75%战力/族系上限"),
    ("army_composition", "pop_cap", "征召阵亡永久扣人口"),
    ("land_combat", "war_peace", "战分(上限50)+战俘"),
    ("siege_logistics", "war_peace", "占领战分+未围要塞-33%"),
    ("food_system", "siege_logistics", "军粮与省粮仓直连"),
    ("navy_maritime", "proximity", "海路衰减与海上存在"),
    ("navy_maritime", "war_peace", "封锁重创敌港口/战分"),
    ("war_peace", "antagonism", "割地产生敌意震荡"),
    ("war_peace", "integration", "新割地进入未整合"),
    ("diplo_bloc", "war_peace", "召唤盟友/强盟饱和"),
    ("spy_intel", "war_peace", "造CB(20)/揭25迷雾"),
    ("antagonism", "diplo_bloc", "50敌意/-50好感触发包围网"),
    ("subjects_connectivity", "antagonism", "割地给属国减半AE"),
    ("subjects_connectivity", "cabinet", "代为消化/需连通度≥35%控制吞并"),
    ("unions_ios", "subjects_connectivity", "PU整合需议会补课"),
]

# Home page 6-pillar condensed graph (viewBox 1120 x 470, cols 155/560/965, rows 145/365)
HOME_NODES = [
    {"id": "territory", "zh": "① 疆域与控制", "sub": "地点 · 邻近度 · 核心化 · 控制力", "x": 155, "y": 145, "href": "ch01-territory-core.html"},
    {"id": "economy", "zh": "② 人口、市场与财政", "sub": "三级粮仓 · RGO工坊 · 税基 · 债券", "x": 560, "y": 145, "href": "ch02-population-food.html"},
    {"id": "state", "zh": "③ 政府、内阁与阶层", "sub": "内阁瓶颈 · 王室vs阶层 · 12阶层互动", "x": 965, "y": 145, "href": "ch04-government-cabinet.html"},
    {"id": "culture", "zh": "④ 文化、信仰与科技", "sub": "50%核心门槛 · 修会 · 思潮 · 殖民", "x": 155, "y": 365, "href": "ch06-culture-religion.html"},
    {"id": "military", "zh": "⑤ 军事、海权与和约", "sub": "征召耗人口 · 四阵位 · 后勤 · 海上存在", "x": 560, "y": 365, "href": "ch08-military-combat.html"},
    {"id": "diplomacy", "zh": "⑥ 外交、属国与秩序", "sub": "强盟饱和 · 属国连通 · 50AE网 · PU神罗", "x": 965, "y": 365, "href": "ch10-diplomacy-subjects.html"},
]

HOME_EDGES = [
    ("territory", "economy", "控制力分流税基/阶层"),
    ("economy", "state", "税基与阶层金库博弈"),
    ("state", "territory", "内阁整合省份与直接提控"),
    ("culture", "territory", "≥50%核心文化"),
    ("state", "culture", "同化/传教/礼仪科研"),
    ("economy", "military", "粮仓供军 · 税贸养兵"),
    ("military", "territory", "制海保控 · 征服新地"),
    ("military", "diplomacy", "战分和约与敌意震荡"),
    ("diplomacy", "state", "属国分担内阁/官僚"),
]

# 36 Game-Changing Redlines (all exact 1.4.9 values)
REDLINES = [
    {"pillar": "territory", "title": "核心化文化门槛", "value": "≥ 50%", "key": "NCulture.CORE_THRESHOLD = 0.5", "desc": "已整合（Integrated）地点必须由本国「主流文化」或「已接纳文化」人口占 50% 以上才会自动变为核心（Core）。相容文化不计入！"},
    {"pillar": "territory", "title": "省整合减速地点阈值", "value": "> 5 个地点", "key": "NLocation.MAX_NUM_LOCATIONS_FOR_INTEGRATE_SLOWDOWN = 5", "desc": "单个省份包含超过 5 个地点时，内阁执行「整合省份」速度受到显著惩罚。"},
    {"pillar": "territory", "title": "阶层私人建筑攻防红线", "value": "75% 控制力", "key": "ESTATE_BUILD_MAX / DESTROY_ESTATE_BUILD_MIN = 0.75", "desc": "阶层只在控制力 <75% 的地点建造阶层建筑；王室也必须把控制力提到 ≥75% 才能手动拆掉阶层建筑（或使用削减阶层力量行动）。"},
    {"pillar": "territory", "title": "邻近度转最大控制力系数", "value": "× 0.75", "key": "PROXIMITY_CONTRIBUTION = 0.75", "desc": "100% 邻近度基础提供 +75% 最大控制力，剩余空间由核心（+20%）、城镇等级与人群满意度补足。"},
    {"pillar": "territory", "title": "海外飞地判定距离", "value": "150", "key": "NLocation.OVERSEAS_DISTANCE = 150", "desc": "与首都距离超过 150 且满足跨大洲/无陆连条件的领土触发海外管理属性。"},
    {"pillar": "territory", "title": "叛乱/被占整合倒退", "value": "−10 / −0.025月", "key": "REBELLION_HIT = -10 / OCCUPIED_DECAY = -0.025", "desc": "未整合地点爆发叛乱立刻损失 10 点整合进度；被敌军占领每月掉 0.025 进度，易主则每月掉 0.1。"},

    {"pillar": "economy", "title": "省粮仓自动向外出售阈值", "value": "> 75% 储量且满溢", "key": "NMarket.FOOD_PROVINCE_LOCAL_RESERVE_RATIO = 0.75", "desc": "省粮仓保留 75% 本地缓冲后才将富余分享到市场；缺粮且未被围攻的省份会每月自动用国库金币买粮直至购空市场。"},
    {"pillar": "economy", "title": "市民出口粮食安全底线", "value": "≥ 25% 市场粮库", "key": "MARKET_MIN_FOOD_STOCKPILE_RATIO_FOR_BURGHER_TRADE = 0.25", "desc": "当所属市场粮食储备跌破 25% 上限时，市民商人自动停止将粮食出口倒卖到外部市场。"},
    {"pillar": "economy", "title": "饥荒爆发惩罚", "value": "−5% 人口 / 月", "key": "province_starving: -0.05", "desc": "省粮仓归零触发饥荒：人口增长 −5%/月、补给上限 −25%、移民吸引 −1.0、上层阶级容量 −50%、市场食需激增 1.5 倍。"},
    {"pillar": "economy", "title": "被劫掠地点惩罚期", "value": "12 个月", "key": "NLocation.LOOT_MONTHS = 12", "desc": "敌军占领并劫掠后施加 12 月修正：人口 −0.5%/月、发展度 −25%、繁荣衰减 +0.1、敌军获粮 −10%。"},
    {"pillar": "economy", "title": "税基比率预警颜色线", "value": "75% / 50% / 25%", "key": "TAX_BASE_RATIO_THRESHOLDS", "desc": "实收税基 / 地点财富 ≥75% 显绿、≥50% 显黄、≥25% 显橙、<25% 显红（提示高产区控制力流失极严重）。"},
    {"pillar": "economy", "title": "市场月度调价速率与极限", "value": "5% 趋近 / 0.33~3x", "key": "MONTHLY_PRICE_CHANGE = 0.05", "desc": "市场价每月仅向目标价移动 5% 差额；无额外修正时价格波动下限约 −33%，上限 3 倍。"},
    {"pillar": "economy", "title": "阶层造价倍率与投产阈值", "value": "4 倍造价 / 50%投产", "key": "ESTATE_MAX_PRICE_MULTIPLIER = 4 / THRESHOLD = 0.5", "desc": "阶层自行建楼支付常规 4 倍造价；新建建筑投产度超 50% 后享最高 +15%（0.5×0.3）生产效率加成。"},
    {"pillar": "economy", "title": "贸易关税与补贴三档税率", "value": "±10% / ±25% / ±50%", "key": "TARIFF: 0.10/0.25/0.50 | SUBVENTION: -0.10/-0.20/-0.35", "desc": "市场所有者可在贸易政策页面按商品设定三档关税或三档倒贴补贴（轻−10%、中−20%、重−35%）。"},
    {"pillar": "economy", "title": "国家破产信誉度惩罚", "value": "−50 信誉 (0.5/年恢复)", "key": "CREDITWORTHINESS_BANKRUPTCY_DRAIN = 0.5 / +0.005 yr", "desc": "破产清零债务并施加 5 年 −50 稳定与 −33% 控制，同时直接扣减 50 点信誉度（每年自然恢复 0.5 点）；信誉度 < 30 时外国 AI 拒绝放贷。"},

    {"pillar": "state", "title": "阶层拒出征召兵与停税阈值", "value": "< 25% / < 1%", "key": "ESTATE_LEVY = 0.25 / TAX = 0.01", "desc": "当某阶层满意度跌破 25% 时，立即停止为国家提供陆海军征召兵；低于 1% 时无法向其征税。"},
    {"pillar": "state", "title": "授予/撤销特权满意度变动", "value": "+3×Δ / −25%−3×Δ", "key": "GRANT_IMPACT = 3 / REVOKE_BASE = -0.25", "desc": "授予特权本阶层即时上升 3×均衡改变量（他阶反扣一半）；撤销特权直接扣减 −25% − 3×Δ，撤销前需核算满意度余量。"},
    {"pillar": "state", "title": "向市民无息紧急拨款上限", "value": "市民金库 ≥10 / 最多 50%", "key": "BURGHER_GRANT_MIN = 5.0 / MAX_FRACTION = 0.5", "desc": "「请求紧急拨款」一次抽走最多市民金库 50%（上限 6 倍阶层贷款），无债务无利息不占贷款容量，防御战成本与扣满减半！"},
    {"pillar": "state", "title": "议会冷却与通过门槛", "value": "59 个月 / 180 天 / 50%", "key": "PARLIAMENT_COOLDOWN = 59 / THRESHOLD = 0.5", "desc": "常规议会每 59 整月后才能重开（战时可耗正统性开紧急议会），会期 180 天，过半（50%）支持度通过议案。"},
    {"pillar": "state", "title": "内阁首脑任职门槛与锁定", "value": "任职 10 年 / 不可移除", "key": "promote_to_head_of_cabinet_timer = 10y", "desc": "大臣在内阁服务满 10 年可升为内阁首脑（效率 +25%、特质翻倍），但任职期间无法被免职或派往带兵。"},
    {"pillar": "state", "title": "小规模叛乱 vs 公开起义门槛", "value": "5,000 支持人口", "key": "NPop.MIN_REBEL_POP_SIZE_THRESHOLD = 5 (k)", "desc": "叛乱进度满 100% 时若支持人口不足 5,000，不会独立造反，而是原地变成 -0.5% 月控制/繁荣的衰减惩戒。"},
    {"pillar": "state", "title": "要塞守军倒戈保底上下限", "value": "10% ~ 90%", "key": "REBEL_FORT_LOYALTY_BASE=50, MIN=10, MAX=90", "desc": "基础 50 + 30×阶层满意 ± 文化宗教动乱修正 − 进度>80%扣20 − 同类守军扣15，决定起义时要塞直接叛变还是坚守。"},
    {"pillar": "state", "title": "官僚固化百年阶段", "value": "每 100 年一阶", "key": "BUREAUCRACY_ENTRENCHMENT_YEARS_PER_PHASE = 100", "desc": "官僚部门随时间深化固化，不断抬高正负修正幅度与每月的维护金账单，并让后续废除难度倍增。"},

    {"pillar": "culture", "title": "思潮全国接纳人口门槛", "value": "≥ 20% 人口", "key": "NCountry.INSTITUTION_MINIMUM_PERCENT = 0.2", "desc": "思潮必须在己方已拥有且完全传播该思潮的地点的总人口累计占全国总人口 20% 以上，才能点击接纳。"},
    {"pillar": "culture", "title": "征服后人口逃亡与拓殖拉力", "value": "12 个月 / 25 年 (3×)", "key": "POST_CONQUEST_MONTHS=12 / SETTLER_RAMP=25", "desc": "异国割让地受歧视人群头 12 个月加速外逃；同时当地对主流文化产生高达 3 倍移民吸引力并持续衰减 25 年。"},
    {"pillar": "culture", "title": "单省特许殖民地竞争上限", "value": "最多 3 个", "key": "NColony.MAX_CHARTERS_IN_PROVINCE = 3", "desc": "同一省份内最多允许 3 支不同特许殖民地并行迁入竞争定居权；每地至少满 1,000 人完成定居。"},
    {"pillar": "culture", "title": "神道教清净度涨荣辱阈值", "value": "Purity > 75", "key": "game_concept_honor_desc", "desc": "清净度保持 75 以上会稳定推高国家荣辱；交战死伤或瘟疫减员则会扣减清净度。"},

    {"pillar": "military", "title": "征召兵战力折算与恢复期", "value": "75% 战力 / 240 个月", "key": "LAND_LEVY_IMPACT = 0.75 / RECOVERY = 240", "desc": "陆军征召兵基础战力仅及正规军 75%、训练度 −20%，不可战地补员，损失后恢复上限需整整 20 年（240 月）。"},
    {"pillar": "military", "title": "战场兵力碾压全歼（Overrun）", "value": "10:1 首日 / 2:1 溃退", "key": "INITIAL_OVERRUN = 10 / MORALE_OVERRUN = 2", "desc": "开战首个结算步我方达敌军 10 倍兵力直接全歼；敌军士气崩溃时 2 倍兵力即可追击彻底抹除。"},
    {"pillar": "military", "title": "兵种混编禁止占比线", "value": "单一类别 < 50%", "key": "game_concept_combined_arms_desc", "desc": "一支军队或舰队中，单一兵种类别占比达到或超过 50% 时会失去「兵种混编」的战斗力协同加成。"},
    {"pillar": "military", "title": "占领瞬间摧毁存粮与掳奴", "value": "毁 90% 粮 / 掳 15% 人口", "key": "FOOD_LOST = 0.9 / ENSLAVE = 0.15", "desc": "敌军夺取地点瞬间摧毁 90% 当地储备食物；在允许奴隶制时立即将 15% 本地人口掳走为奴（240 天冷却）。"},
    {"pillar": "military", "title": "自动巡逻舰队阈值常量", "value": "90% 常量 / 补丁称 100%", "key": "NEconomy.PATROL_THE_SEAS_THRESHOLD = 90", "desc": "00_defines.txt 中 PATROL_THE_SEAS_THRESHOLD 仍为 90，而 1.4.9 补丁说明称舰队会巡逻至 100% 再换区；关键航道建议驻舰实测确认。"},
    {"pillar": "military", "title": "未占要塞和约割地效率惩罚", "value": "−15% ~ −33%", "key": "UNOCCUPIED_FORT = -0.15 / NEVER_SIEGED = -0.18", "desc": "试图割让敌国未被占领的要塞（或ZoC内）土地，战分成本大幅暴涨（从未派兵围攻更是直接叠加至 −33% 效率）。"},

    {"pillar": "diplomacy", "title": "包围网入网与退网双重门槛", "value": "50 敌意 & −50 好感 / < 30 退", "key": "ANTAGONISM_FOR_COALITION = 50", "desc": "外国对我敌意超 50 且好感低于 −50（未交战/休战/联统）即可入网；和平状态下敌意降至 30 以下才会自动退出。"},
    {"pillar": "diplomacy", "title": "属国割地减少敌意与交界吞并控制", "value": "−50% 敌意 / ≥ 35% 控制", "key": "PEACE_SUBJECT_AE = -0.5 / BORDER_CONTROL = 0.35", "desc": "和约中将地点直接割让给自己的附属国，产生敌意直降 50%；吞并附属国需宗主交界处控制力 ≥ 35%。"},
    {"pillar": "diplomacy", "title": "间谍网解锁情报（信息迷雾）", "value": "25 点间谍网", "key": "INTEL_THRESHOLD_* = 25", "desc": "间谍网达到 25 点即可看穿目标守军、要塞等级、储备与部队构成，同时开始面临每年 25% 被发现风险。"},
    {"pillar": "diplomacy", "title": "属国集团综合实力忠诚警戒线", "value": "> 20% 总和力量", "key": "SUBJECTS_STRENGTH_THRESHOLD = 0.20", "desc": "当全部附属国的陆军/收入/人口三项综合突破宗主+属国总 bloc 的 20% 后，超出部分按 −60 倍率重扣所有属国忠诚！"},
]

TROUBLESHOOT = [
    {"symptom": "新征服省份已由内阁整合完毕，为何仍无法提供殖民移民，且最大控制力仅 +5% 而非 +20%？", "pillar": "territory", "cause": "整合（Integrated）不等于核心（Core）。内阁仅将「未整合」转为「已整合」；转为核心要求当地本国主流文化或「已接纳文化」人口占比达到 ≥ 50%（CORE_THRESHOLD=0.5），相容文化不计入。", "fix": "在「文化」面板将当地优势文化设为【已接纳】，或指派外交内阁执行【推广文化 / 同化地区】使主流文化占比跨过 50%。", "href": "ch01-territory-core.html#integration-core"},
    {"symptom": "税收与贸易收入正常，为何月度财政结余突然大幅转负？", "pillar": "economy", "cause": "省份自动购粮支出增加。当遭遇劫掠、严冬寒潮或农业用地不足的省份出现月度粮食赤字且省粮仓耗尽时，只要未被围攻，系统会按所属市场当期粮价自动购粮，并计入国家财政「购买食物」支出项。", "fix": "切换到食物地图模式定位赤字省份：暂缓在该省升格城镇、扩建当地粮食类 RGO，并通过贸易指令从邻近市场进口低价粮食。", "href": "ch02-population-food.html#food-chain"},
    {"symptom": "新建了多座高利润工坊与市集，为何国库月度税收增长缓慢、税基比率偏低？", "pillar": "economy", "cause": "地点财富需先乘以「控制力」才计入国家可征税税基。低控制力地区的未受控财富（财富 × (1 − 控制力)）直接流入地方阶层金库；此外国家贸易收入仅按「王室力量份额」分成。", "fix": "优先在高控制力地区投资建厂；按「未受控财富」排序指派行政内阁提升控制力、铺设连接首都的道路与港口，并在沿海航道维持海上存在。", "href": "ch03-economy-market-trade.html#wealth-to-treasury"},
    {"symptom": "战争结束后，为何国内部分矿山与工坊出现岗位空缺？", "pillar": "military", "cause": "陆军征召兵（Levies）直接抽调自真实平民与贵族人口。征召兵基础战力为正规军的 75% 且无法战地补员，一旦阵亡或因断粮损耗，原籍对应劳动力人口会永久扣减，征召上限需 240 个月恢复。", "fix": "核心经济区减少消耗性征召动员；逐步建设军械库等军事建筑扩充人力池与正规军，并在战前保障前线省粮仓与补给站。", "href": "ch08-military-combat.html#force-types"},
    {"symptom": "战时点击「动员征召兵」，为何某一阶层不提供任何兵员？", "pillar": "state", "cause": "触发了 25% 征召兵满意度阈值（ESTATE_LEVY_SATISFACTION_THRESHOLD=0.25）：任意阶层满意度低于 25% 时停止提供陆海军征召兵，常见于刚撤销特权（扣减 −25% − 3×Δ）或税率过高。", "fix": "下调该阶层税率、使用阶层互动【贿赂阶层】（消耗 12 倍阶层税基即时提升满意度），或在议会中完成该阶层议程。", "href": "ch05-estates-rebels.html#estate-interactions"},
    {"symptom": "国库资金紧张但不想承担 60 个月贷款利息与信誉度风险，有哪些替代筹款渠道？", "pillar": "state", "cause": "市民阶层拥有专属互动「请求紧急拨款」（脚本 ID 为 ask_burghers_for_loan，1.4.9 实际效果为一次性无息拨款，不产生债务）。", "fix": "当市民金库 ≥ 10 金币且财富影响达标时，对市民阶层执行【请求紧急拨款】：可提取最多 50% 市民存款（上限 6 倍贷款额），代价为 −15% 市民满意度（防御战期间扣减减半）。", "href": "ch05-estates-rebels.html#estate-interactions"},
    {"symptom": "阶层在地方自行建造了阶层建筑，为何右键无法手动拆除？", "pillar": "state", "cause": "王室手动拆除阶层建筑要求当地控制力 ≥ 75%（DESTROY_ESTATE_BUILD_MIN_CONTROL_THRESHOLD=0.75），而阶层恰在控制力 < 75% 且满意度偏低的地点建造此类建筑。", "fix": "① 用行政内阁将省控制力提升至 75% 以上后手动拆除；② 通过议会议程处理；③ 在阶层面板执行【削减阶层力量】，按控制力从低到高批量移除最多 20 座阶层建筑并获得 2 倍税基金币。", "href": "ch05-estates-rebels.html#estate-wealth"},
    {"symptom": "对舰队下达「自动巡逻海域」后，跨海邻近度为何偶尔出现波动？", "pillar": "military", "cause": "00_defines.txt 中 PATROL_THE_SEAS_THRESHOLD 常量为 90（1.4.9 补丁说明称舰队会巡逻至 100% 再换区）；当舰队轮换海区或返港修理时，海格海上存在会因月度自然衰减与风暴下滑。", "fix": "对连接首都与核心海外港口的少数关键海格，可拆分 5–10 艘轻型战舰定点驻留，以稳定维持 100% 海上存在。", "href": "ch09-navy-war-peace.html#maritime-presence"},
    {"symptom": "扩张后未整合省份过多，内阁席位不足导致长期承受未整合惩罚，应如何分流？", "pillar": "state", "cause": "单省超过 5 个地点会放缓整合速度，且早期仅能按省逐一整合。长期持有大量未整合土地会承受 −10% 最大控制力与 +0.5 分离主义。", "fix": "使用「释放省份属国」或在战时「转移占领」后再由和约割让给附属国：由属国的内阁代为整合，同时和约割地给属国可减少 50% 敌意。", "href": "ch10-diplomacy-subjects.html#subjects-annex"},
    {"symptom": "共主邦联（PU）推进到最终统一法律时，为何较晚加入的成员国未被一并吞并？", "pillar": "diplomacy", "cause": "共主邦联按成员各自记录整合等级（union_integration_level）：每次通过集中化法律仅使当时在列成员等级 +1；后加入成员等级滞后时不会随终局议案一并吞并。", "fix": "在邦联界面召开【邦联议会】，先通过追赶整合进度的专门议案将后加入成员拉平至同一整合等级，再执行最终合并。", "href": "ch10-diplomacy-subjects.html#pu-and-ios"},
    {"symptom": "作为大国仅新增一个列强盟友，为何外交容量立刻超限？", "pillar": "diplomacy", "cause": "联盟集团饱和度机制：每位列强盟友计 1.0 强盟权重，区域强权计 0.5。总权重超过 1.0 后，超出的每 1.0 权重会为本国所有同盟关系每条追加 +0.3 外交容量消耗。", "fix": "控制列强/区域强权同盟数量（通常保留 1 个强盟），其余战略方向改用附庸或封地体系。", "href": "ch10-diplomacy-subjects.html#diplo-capacity"},
    {"symptom": "叛军起义爆发时，为何省内要塞直接转为叛军控制？", "pillar": "state", "cause": "叛军起义时每座要塞按 REBEL_FORT_LOYALTY 公式检定守军忠诚（上下限 10%–90%）：阶层满意度低、叛军与守军同阶层（−15）、镇压前进度已超 80%（−20）都会大幅提高倒戈概率。", "fix": "在叛乱进度升至 80% 之前使用军事行动【激起反叛】主动引爆并清剿，或提前改善对应阶层满意度。", "href": "ch05-estates-rebels.html#rebellions"},
    {"symptom": "在同一市场连续扩建多级同类加工建筑后，为何利润下降甚至停工？", "pillar": "economy", "cause": "集中扩建会同时推高上游原料目标价并压低成品目标价（即界面提示的 6 个月扩建波动性）；若市场原料短缺，市场接入度较低的地点会优先断供停工并损失投产度。", "fix": "扩建前参考 6 个月价格冲击预估，同步扩建上游 RGO 或通过贸易指令进口紧缺原料，并将产线分散至高接入度城市。", "href": "ch03-economy-market-trade.html#production-buildings"},
    {"symptom": "新建工坊或升格城镇数月后，为何市民/劳工岗位仍未招满？", "pillar": "economy", "cause": "人口阶级晋升受月度晋升速度与文化资格双重限制：当地须有富余平民，且人群文化至少为「相容文化」（受忽视/受歧视文化无法晋升），识字率、稳定度与控制力也会缩放晋升速率。", "fix": "将当地主要文化至少设为【相容文化】，并指派行政内阁执行【促进人口升级】。", "href": "ch02-population-food.html#population-base"},
    {"symptom": "破产数十年后财政早已宽裕，为何外国仍拒绝放贷且利率偏高？", "pillar": "economy", "cause": "破产直接扣减 50 点国家信誉度（Creditworthiness，0–100，基准 50），而破产惩罚的自然恢复速率为每年 0.5 点；信誉度低于 30 时外国 AI 不会放贷。", "fix": "借入小额本国阶层贷款并在 60 个月到期前按时偿还（每笔按时还款 +2.0 信誉度），避免到期强制展期（−3.0 信誉度）。", "href": "ch03-economy-market-trade.html#finance-debt"},
    {"symptom": "冬季陆军跨过结冰海域行军，为何开春后部队突然损失？", "pillar": "territory", "cause": "严冬连续寒潮有 20% 概率使浅海进入「封冻（Frozen）」状态供陆军通行；气温回升后触发 40% 解冻判定时，仍停留在海格冰面上的陆军会遭受解冻覆没。", "fix": "在波罗的海、北海及黑海北部冬季作战时留意海格【封冻】状态与季节更替，入春前将陆军撤回陆地或改由运输舰接运。", "href": "ch01-territory-core.html#geography-climate"},
]


def export_graph_bundle():
    with open(os.path.join(DATA_DIR, "graph_bundle.json"), "w", encoding="utf-8") as f:
        json.dump({
            "pillars": PILLARS,
            "nodes": NODES,
            "edges": EDGES,
            "home_nodes": HOME_NODES,
            "home_edges": HOME_EDGES,
            "redlines": REDLINES,
            "troubleshoot": TROUBLESHOOT,
        }, f, ensure_ascii=False, indent=2)
    print(f"Exported graph bundle: {len(NODES)} nodes, {len(EDGES)} edges, {len(REDLINES)} redlines, {len(TROUBLESHOOT)} troubleshooting cases.")


if __name__ == "__main__":
    export_graph_bundle()
