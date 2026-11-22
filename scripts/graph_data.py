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
        "summary": "国家从地点抽取税基、征召兵、人力与水手的核心比例闸门，缓慢趋近最大控制力。",
        "formula": "税基 = 地点财富 × 控制力；未受控财富 = 地点财富 × (1 − 控制力) → 直接流入当地阶层金库",
        "redline": "控制力 ≥ 75% 时王室才可直接拆除阶层建筑；< 75% 则是阶层狂造私产建筑的温床。",
    },
    {
        "id": "town_rights", "zh": "城镇特权与升城", "en": "Town Rights & Rank", "pillar": "territory", "x": 130, "y": 720,
        "href": "ch01-territory-core.html#urbanization",
        "summary": "乡村/城镇/城市/大都会等级决定建筑上限与市民岗位，探索时代可授城镇特权专精产业。",
        "formula": "默认特权槽位：城镇 1 个、城市 2 个、大都会 3 个；建筑上限随等级与发展度提高",
        "redline": "升城镇会大幅拉低食物效率并挤压原产粮食产能，切忌在缺粮省核心粮仓上盲目升城。",
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
        "summary": "地点 → 省份 → 市场三级流转的生存与军粮体系，新手头号破产与断粮陷阱所在。",
        "formula": "省粮仓盈余(>75%且满仓)自动卖给市场赚金币；赤字时只要未被围攻即自动耗国库钱从市场买粮",
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
        "summary": "把地方工农业利润切分成国家税基与阶层金库收入的五步经济漏斗核心。",
        "formula": "税基 = (原产利润 + 建筑利润 + 市民贸易) × 控制力；实收税款 = 阶层税基 × 税率 × 税收效率",
        "redline": "税基比率（实收税基/经济基础）<25%亮红灯，说明高富地区被低控制力黑洞吞噬。",
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
        "id": "estate_pool", "zh": "阶层金库与私建", "en": "Estate Gold & Buildings", "pillar": "state", "x": 805, "y": 220,
        "href": "ch05-estates-rebels.html#estate-wealth",
        "summary": "承接税后结余、贷款利息与低控漏水财富的阶层蓄水池，反过来建造公共建筑或恶性私产。",
        "formula": "阶层造价 = 常规 4 倍；满意度与财富影响高时造经济建筑，低落时在<75%控制地狂造阶层建筑",
        "redline": "高财富影响可用「请求紧急拨款」无息抽水市民最多 50% 金库；可用「削减阶层力量」批量拆私建。",
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
        "summary": "制海、运输与封锁工具，更是连接海外近岸省份控制力、打击私掠海盗的海权生命线。",
        "formula": "港口和平自然累积海上存在，海军传统 +50%满值加成；舰船反海盗属性按月消磨私掠耐久",
        "redline": "自动巡逻舰队把海域刷到 90% 海上存在即离开/返港！重要走廊请用 5–10 艘轻船手动驻留锁 100%。",
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
    ("control", "wealth_tax", "切分税基 vs 阶层水池"),
    ("control", "estate_pool", "未控财富喂肥阶层"),
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
    ("estate_pool", "crown_estate_power", "<75%造私产压王室"),
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
    ("navy_maritime", "proximity", "海路衰减命脉(90%陷阱)"),
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
    {"id": "military", "zh": "⑤ 军事、海权与和约", "sub": "征召耗人口 · 四阵位 · 后勤 · 90%海巡", "x": 560, "y": 365, "href": "ch08-military-combat.html"},
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
    {"pillar": "economy", "title": "国家破产百年信用黑洞", "value": "−50 信誉 (100 年恢复)", "key": "CREDITWORTHINESS_BANKRUPTCY_DRAIN = 0.5 / +0.005 yr", "desc": "破产清零债务并给 5 年 −50 稳定与 −33% 控制，同时直接扣减 50 点信誉度（每年仅回 0.5 点）；<30 分外邦拒贷。"},

    {"pillar": "state", "title": "阶层拒出征召兵与停税红线", "value": "< 25% / < 1%", "key": "ESTATE_LEVY = 0.25 / TAX = 0.01", "desc": "当某阶层满意度跌破 25% 时，立刻拒绝为国家提供陆海军征召兵；低于 1% 无法向其征税。"},
    {"pillar": "state", "title": "授予/撤销特权满意度冲击", "value": "+3×Δ / −25%−3×Δ", "key": "GRANT_IMPACT = 3 / REVOKE_BASE = -0.25", "desc": "授特权本阶层即涨 3×均衡改变量（他阶反扣一半）；撤特权直扣 −25% − 3×Δ 极易瞬间炸破 25% 征召线或引爆内战。"},
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
    {"pillar": "military", "title": "自动巡逻舰队停航阈值", "value": "90% 海上存在", "key": "NEconomy.PATROL_THE_SEAS_THRESHOLD = 90", "desc": "自动「巡逻海域」指令在海格海上存在达 90% 后就会认为达标并转场或回港，无法帮你锁死 100% 控海走廊！"},
    {"pillar": "military", "title": "未占要塞和约割地效率惩罚", "value": "−15% ~ −33%", "key": "UNOCCUPIED_FORT = -0.15 / NEVER_SIEGED = -0.18", "desc": "试图割让敌国未被占领的要塞（或ZoC内）土地，战分成本大幅暴涨（从未派兵围攻更是直接叠加至 −33% 效率）。"},

    {"pillar": "diplomacy", "title": "包围网入网与退网双重门槛", "value": "50 敌意 & −50 好感 / < 30 退", "key": "ANTAGONISM_FOR_COALITION = 50", "desc": "外国对我敌意超 50 且好感低于 −50（未交战/休战/联统）即可入网；和平状态下敌意降至 30 以下才会自动退出。"},
    {"pillar": "diplomacy", "title": "属国割地减少敌意与交界吞并控制", "value": "−50% 敌意 / ≥ 35% 控制", "key": "PEACE_SUBJECT_AE = -0.5 / BORDER_CONTROL = 0.35", "desc": "和约中将地点直接割让给自己的附属国，产生敌意直降 50%；吞并附属国需宗主交界处控制力 ≥ 35%。"},
    {"pillar": "diplomacy", "title": "间谍网解锁情报（信息迷雾）", "value": "25 点间谍网", "key": "INTEL_THRESHOLD_* = 25", "desc": "间谍网达到 25 点即可看穿目标守军、要塞等级、储备与部队构成，同时开始面临每年 25% 被发现风险。"},
    {"pillar": "diplomacy", "title": "属国集团综合实力忠诚警戒线", "value": "> 20% 总和力量", "key": "SUBJECTS_STRENGTH_THRESHOLD = 0.20", "desc": "当全部附属国的陆军/收入/人口三项综合突破宗主+属国总 bloc 的 20% 后，超出部分按 −60 倍率重扣所有属国忠诚！"},
]

TROUBLESHOOT = [
    {"symptom": "打下来的省内阁终于整合完了，为什么还是不能喂殖民移民，最大控制力只有 +5% 而不是 +20%？", "pillar": "territory", "cause": "整合（Integrated）≠ 核心（Core）。内阁仅把「未整合」变为「已整合」；核心化要求当地本国主流文化或「已接纳文化」人口占比达到 ≥ 50%（CORE_THRESHOLD=0.5）。注意：相容文化不触发核心化！", "fix": "在「文化」面板把当地优势文化设为【已接纳】，或指派 DIP 内阁执行【推广文化 / 同化地区】把主流文化推过 50%。", "href": "ch01-territory-core.html#integration-core"},
    {"symptom": "国库明明显示税收和贸易正增长，为什么月底突然暴跌甚至每月倒亏大几十杜卡特？", "pillar": "economy", "cause": "省份自动买粮黑洞！若某个刚被劫掠、过度升城或遇到严冬寒潮的省份月结缺粮且省粮仓见底，只要未被围攻，它会按所属市场当期最高市价疯狂「购买食物」并把整张账单扣在国家预算支出里！", "fix": "切到食物地图模式找出红字缺粮省：停止在该省盲目升城镇、扩建当地小麦/鱼类 RGO，用贸易指令优先从邻市进口便宜粮食压低市价。", "href": "ch02-population-food.html#food-chain"},
    {"symptom": "明明盖了十几座高利润手工坊和市集，国库月收入却纹丝不动，甚至税基比率亮起橙红灯？", "pillar": "economy", "cause": "控制力黑洞 + 阶层漏斗：地点财富必须先乘以「控制力」才成为可征税税基。低控制区利润绝大部分没消失，而是成了「未受控财富」流进了地方阶层金库；而且贸易利润也只有「王室力量份额」的那一部分进国库！", "fix": "别在 10% 控制力的远方造厂：用「未受控财富」排序派 ADM 内阁提控、修连接首都的道路/港口、或利用 5–10 艘轻船锁住海上存在。", "href": "ch03-economy-market-trade.html#wealth-to-treasury"},
    {"symptom": "打了一场不大不小的仗，战后发现家里好多矿山和建筑突然空掉没人上班了？", "pillar": "military", "cause": "征召兵（Levies）不是虚空变出来的！每一名拉出的陆军征召兵都是从真实平民/贵族人口里暂时抽调的。征召兵战力只有正规军 75%、不能补员，一旦在战场战死或饿死，家乡对应劳动力永久减员且恢复需 20 年（240 月）。", "fix": "高价值地区慎拉征召兵做消耗战炮灰；尽早造军械建筑扩充正规军和人力池，或战前注意保持前线有省粮仓/补给站防饿死。", "href": "ch08-military-combat.html#force-types"},
    {"symptom": "开战时点「动员征召兵」，为什么某个阶层的人明明都在国内却一个兵都征不出来？", "pillar": "state", "cause": "触发了 25% 征召兵满意度硬红线（ESTATE_LEVY_SATISFACTION_THRESHOLD=0.25）：任意阶层满意度低于 25% 时直接拒交全部陆海军征召兵。多半是刚强撤了一项特权（直扣 -25% - 3×Δ）或把税拉爆所致。", "fix": "降税滑块、点击阶层互动【贿赂阶层】（花 12 倍阶层税基立刻拉回满意度），或在议会优先解决该阶层的议程。", "href": "ch05-estates-rebels.html#estate-interactions"},
    {"symptom": "阶层钱多得流油，我快打输或破产了却不想背 60 个月的高息贷款还要怕信用崩盘？", "pillar": "state", "cause": "忽视了市民阶层的专属绝境互动「请求紧急拨款」（英文 ID 虽叫 ask_burghers_for_loan，但在 1.4.9 机制中其实已重做为无债务无偿划拨！）。", "fix": "在阶层互动中对市民阶层使用【请求紧急拨款】：直接划走最多 50% 市民存款且不加任何负债和利息，代价仅为 -15% 市民满意度（防御战花费还减半！）。", "href": "ch05-estates-rebels.html#estate-interactions"},
    {"symptom": "贵族/教士/市民在乡下疯狂造各种「阶层建筑」拉高力量，右键却提示无法拆除？", "pillar": "state", "cause": "王室手动拆除阶层建筑有硬控制力门槛 ≥ 75%（DESTROY_ESTATE_BUILD_MIN_CONTROL_THRESHOLD=0.75）；而阶层恰好专门挑选控制力 <75% 的边远省乱盖（满意度越低越爱盖）。", "fix": "① 用 ADM 内阁先把省控冲过 75% 再拆；② 利用议会议程请求；③ 直接在阶层面板点【削减阶层力量】，按控制力从低到高一次性强拆最多 20 座阶层建筑还能反薅 2 倍税基金币！", "href": "ch05-estates-rebels.html#estate-wealth"},
    {"symptom": "我给舰队设置了「自动巡逻海域」指令，为什么过了一段时间跨海控制力和海上贸易力量全掉回去了？", "pillar": "military", "cause": "1.4.9 巡逻 AI 的停航设定是 PATROL_THE_SEAS_THRESHOLD = 90！只要一片海格刷到 90% 海上存在，自动巡逻舰队就会离开去别处或返港摸鱼，一旦受天气/海盗或衰减立刻滑落。", "fix": "不要把全部轻船交给自动巡逻：拆成几支 5–10 艘轻型战舰的小分队，手动停泊/驻守在首都通往核心港口的关键沿海海格上永久锁死 100%。", "href": "ch09-navy-war-peace.html#maritime-presence"},
    {"symptom": "新占领了一片好大的地盘，内阁一共就 2~3 个席位，算了一下全部整合完要 40 年，该怎么扩张？", "pillar": "state", "cause": "内阁席位瓶颈（Cabinet Bottleneck）：单省超 5 地点大幅减速，且早期只有单省级整合。硬吃大量未整合土地会长期被 -10% 控制、+0.5 分离主义与高叛乱率反噬。", "fix": "学会「释放省份属国（Create Province Subject）」或战时先把占领权「转移占领」给属国！既免除内阁整合压力、让属国代为消化核心化，还能在和约里直接砍半（-50%）包围网敌意！", "href": "ch10-diplomacy-subjects.html#subjects-annex"},
    {"symptom": "为什么辛辛苦苦搞了一个共主邦联（PU），推进到最后一步想一并整合吞并时，新联统的小国却没有一起吞掉？", "pillar": "diplomacy", "cause": "「共主邦联整合等级（union_integration_level）」单独结算规则：每通过一次邦联集中化法律，当时在列成员整合等级 +1；晚于前面法律进度才新加入邦联的成员停留在低等级，不与主导国平级绝不随终局吞并。", "fix": "在邦联窗口召开【邦联议会】，选择专门让落后成员「追赶整合进度」的议案拉平等级，再最终合众吞并。", "href": "ch10-diplomacy-subjects.html#pu-and-ios"},
    {"symptom": "我是 4 级大国，仅仅又跟隔壁另一位列强结了个同盟，为什么外交容量瞬间爆表、外交声誉暴跌？", "pillar": "diplomacy", "cause": "联盟集团饱和度（Alliance Bloc Saturation）：每位列强盟友算 1.0 强盟权重，区域强权算 0.5。当总强盟权重超过 1.0，多出的每一份权重都会给你的所有同盟每条追加 +0.3 外交容量惩罚，此外同盟占容还按对方/我方经济比放大。", "fix": "避免同时拉拢多个列强/区域强权大国结盟；改用 1–2 个强力盟友 + 多个低成本附庸/封地组成属国阵线。", "href": "ch10-diplomacy-subjects.html#diplo-capacity"},
    {"symptom": "本来只想等叛乱出来平推省事，为什么叛军一刷出来把我半边要塞全一起接管了？", "pillar": "state", "cause": "叛军爆发瞬间会对区内每座要塞掷「要塞守军忠诚检定（REBEL_FORT_LOYALTY）」：若当地文化/宗教不合、叛军隶属守军同一阶层、该阶层满意度又极低且拖到 80% 进度后才镇压，要塞保底仅 10% 几率守住！", "fix": "利用军事行动【激起反叛（Provoke Rebels）】在叛军进度达到 80%（跨过扣 20 分门槛）之前主动引爆提前围杀；或预先把部队停在要塞内与安抚核心阶层。", "href": "ch05-estates-rebels.html#rebellions"},
    {"symptom": "刚花钱升级了三五座同一个行业的高级工厂，结果一开业全都亏钱停工甚至把原料市价拉爆？", "pillar": "economy", "cause": "忽略了「扩建波动性（Expansion Volatility）」与「市场接入度供料排序」：同一市场内集中暴建多级同类工厂会同时推高原料目标价、砸穿成品目标价；若市场缺原料，接入度低的偏远厂先断供停工并掉失「投产度」。", "fix": "分散在多个不同市场或先扩建上游 RGO 原料产能；留意升级面板自带的未来 6 个月波动性盈利预报，并善用国家贸易指令专程进口卡脖子原料。", "href": "ch03-economy-market-trade.html#production-buildings"},
    {"symptom": "为什么新建了工厂或升级了城镇，半年过去了雇工槽位还是空着大量「有厂无工」？", "pillar": "economy", "cause": "社会阶级升级（Promotion）存在严格门槛与月度配额：当地必须有未就业的「平民（Peasants）」且文化至少是「相容文化（Tolerated）」，受歧视或受忽视文化无法晋升；同时城市正稳定度、识字率与控制力都会缩放升阶速率。", "fix": "在「文化」界面把当地人口文化至少设为【相容文化】，派 ADM 内阁在该省执行【促进人口升级（pop_promote_action）】，并通过贸易保供满足需求防满意度滑坡。", "href": "ch02-population-food.html#population-base"},
    {"symptom": "和平时期我已经很有钱了，但破过一次产之后哪怕过了几十年，为什么外国依然拒绝借钱给我、利息高得离谱？", "pillar": "economy", "cause": "触发了 100 年期的「破产信用黑洞」：破产瞬间直扣 50 点信誉度（Creditworthiness，0–100，中性基准 50），而破产惩罚排水恢复速率仅为每年 0.5 点！当信誉度低于 30 时外国 AI 被引擎禁止向你贷款。", "fix": "靠借小额本国阶层贷款并在 60 个月内按时偿还每笔刷 +2.0 点信誉度回血，绝不让贷款到期强制展期（每次倒扣 -3.0 点）。", "href": "ch03-economy-market-trade.html#finance-debt"},
    {"symptom": "为什么在神圣罗马帝国或其他国家境内，某块地看地图有港口也紧邻海上，我陆军站在冰上打仗却突然全军蒸发了？", "pillar": "territory", "cause": "「封冻（Frozen）」海域的双刃剑机制：严冬连续寒潮有 20% 概率将浅海封冻成冰面，允许陆军不靠船直接横跨行军（甚至强化海上控制）；但一旦入春回暖触发 40% 解冻概率，正在冰格上的陆军会遭毁灭性冰沉损失！", "fix": "北欧、波罗的海、黑海北部冬季行军务必紧盯海格【封冻】状态标签与月份，临近开春切勿把主力长时间滞留于冰冻海域之上。", "href": "ch01-territory-core.html#geography-climate"},
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
