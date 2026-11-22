# -*- coding: utf-8 -*-
"""
Programmatic high-legibility inline SVG flowcharts for all 10 chapters + Home diagram.
Every box width >= max(168, max_line_chars * 14 + 32) and explicit <tspan> line spacing
so text never clips or overlaps in either desktop or mobile viewports.
"""
from html import escape


def _box(x, y, w, h, title, lines, color="#1d6b6e", jump="", badge=""):
    cx = x + w / 2
    total_lines = 1 + len(lines)
    # vertically center
    line_h = 16
    start_y = y + h / 2 - ((total_lines - 1) * line_h) / 2 + 4
    tspans = [f'<tspan x="{cx}" dy="0" font-weight="700" font-size="13" fill="var(--ink)">{escape(title)}</tspan>']
    for i, ln in enumerate(lines):
        dy = 17 if i == 0 else 15
        tspans.append(f'<tspan x="{cx}" dy="{dy}" font-size="11.5" fill="var(--ink-muted)">{escape(ln)}</tspan>')
    badge_svg = ""
    if badge:
        bw = max(44, len(badge) * 11 + 14)
        badge_svg = (
            f'<rect x="{x + w - bw - 6}" y="{y - 9}" width="{bw}" height="18" rx="9" '
            f'fill="{color}" />'
            f'<text x="{x + w - bw/2 - 6}" y="{y + 3}" text-anchor="middle" font-size="10.5" '
            f'font-weight="700" fill="#fff">{escape(badge)}</text>'
        )
    cls = "svg-node clickable" if jump else "svg-node"
    jattr = f' data-jump="{escape(jump)}"' if jump else ""
    return (
        f'<g class="{cls}"{jattr}>'
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" '
        f'fill="var(--surface)" stroke="{color}" stroke-width="2" />'
        f'<rect x="{x}" y="{y}" width="6" height="{h}" rx="3" fill="{color}" />'
        f'{badge_svg}'
        f'<text y="{start_y}" text-anchor="middle">{"".join(tspans)}</text>'
        f'</g>'
    )


def _edge_parts(x1, y1, x2, y2, label="", dashed=False, color="var(--accent-2)", curve=0, label_t=0.5, label_offset=(0, 0)):
    dash = ' stroke-dasharray="5,4"' if dashed else ""
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    t = label_t
    if curve:
        cx = mx
        cy = my + curve
        path = f'<path d="M{x1},{y1} Q{cx},{cy} {x2},{y2}" fill="none" stroke="{color}" stroke-width="1.8"{dash} marker-end="url(#arrow)" />'
        lx = (1 - t) ** 2 * x1 + 2 * (1 - t) * t * cx + t ** 2 * x2 + label_offset[0]
        ly = (1 - t) ** 2 * y1 + 2 * (1 - t) * t * cy + t ** 2 * y2 + label_offset[1]
    else:
        path = f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="1.8"{dash} marker-end="url(#arrow)" />'
        lx = x1 + (x2 - x1) * t + label_offset[0]
        ly = y1 + (y2 - y1) * t + label_offset[1]
    lbl_svg = ""
    if label:
        lw = max(56, len(label) * 11 + 16)
        lbl_svg = (
            f'<rect x="{lx - lw/2}" y="{ly - 10}" width="{lw}" height="20" rx="5" fill="var(--bg)" stroke="var(--border)" stroke-width="1" />'
            f'<text x="{lx}" y="{ly + 3.5}" text-anchor="middle" font-size="10.5" fill="var(--ink-muted)">{escape(label)}</text>'
        )
    return path, lbl_svg


def _edge(x1, y1, x2, y2, label="", dashed=False, color="var(--accent-2)", curve=0, label_t=0.5, label_offset=(0, 0)):
    path, lbl_svg = _edge_parts(x1, y1, x2, y2, label, dashed, color, curve, label_t, label_offset)
    return path + lbl_svg


def _wrap_svg(width, height, title, inner):
    return f'''<figure class="diagram-card">
  <figcaption class="diagram-head">
    <span>图解 · 点击节点可跳至对应小节</span>
    <strong>{escape(title)}</strong>
  </figcaption>
  <div class="diagram-scroll">
    <svg viewBox="0 0 {width} {height}" class="mech-svg" role="img" aria-label="{escape(title)}">
      <defs>
        <marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
          <path d="M 0 1 L 10 5 L 0 9 z" fill="var(--accent-2)" />
        </marker>
      </defs>
      {inner}
    </svg>
  </div>
</figure>'''


def diagram_ch01():
    # Territory -> Integration & Core + Proximity -> Max Control -> Tax Base vs Uncontrolled Wealth
    c1, c2, c3, c4 = "#1d6b6e", "#b06c1d", "#9b2c3d", "#5c4687"
    parts = [
        _box(20, 35, 190, 68, "新占非核心地点", ["未整合 Conquered", "最大控制 −10% | 分离 +0.5"], c3, "#integration-core", "起点"),
        _box(280, 35, 195, 68, "MIL 内阁整合行动", ["整合省份 / 整合地区", ">5地点减速 · 叛乱 −10"], c3, "#integration-core"),
        _box(565, 35, 190, 68, "已整合 Integrated", ["最大控制 +5%", "分离降至 +0.1 | 同化 −1%"], c1, "#integration-core"),
        _box(870, 25, 230, 86, "核心 Core (≥50%核心文化)", ["最大控制 +20% · 月控 +0.1%", "出生100%主流文化 · 殖民移民源", "被占保视野 · 收复CB"], c4, "#core-power", "终态"),

        _box(20, 175, 190, 72, "三大邻近度来源", ["首都(100) · 历史首都(+50)", "地方总督 · 陆海衰减"], c1, "#proximity"),
        _box(280, 175, 195, 72, "到达邻近度 (0–100%)", ["地形/植被/道路/河港损耗", "海军海上存在防海运衰减"], c1, "#proximity"),
        _box(565, 175, 190, 72, "最大控制力上限", ["邻近%×0.75 + 整合状态", "+ 城镇等级 + 满意度"], c1, "#control"),
        _box(870, 175, 230, 72, "实际控制力 → 资金分流", ["× 控制力 → 国库税基", "× (1−控) → 阶层金库(<75%造私产)"], c2, "#control"),

        _edge(210, 69, 280, 69, "派内阁"),
        _edge(475, 69, 565, 69, "100%完成"),
        _edge(755, 69, 870, 69, "≥50%核心文化"),
        _edge(210, 211, 280, 211, "逐格扣除"),
        _edge(475, 211, 565, 211, "×0.75"),
        _edge(660, 103, 660, 175, "+5%/+20% / −10%", color=c4),
        _edge(985, 111, 985, 175, "+20%上限 / +0.1%/月", color=c4),
        _edge(755, 211, 870, 211, "缓慢趋近"),
    ]
    return _wrap_svg(1120, 280, "疆域整合四态、邻近度网络与控制力分流链", "".join(parts))


def diagram_ch02():
    c1, c2, c3 = "#b06c1d", "#1d6b6e", "#9b2c3d"
    parts = [
        _box(30, 40, 190, 72, "本地人口与产能", ["农民/劳工自给或RGO", "城市效率低且耗口粮多"], c2, "#population-base"),
        _box(280, 40, 205, 72, "本地食物 (Local Food)", ["每地月产减去本地口粮消耗", "盈余或赤字汇入省粮仓"], c1, "#food-chain"),
        _box(545, 40, 220, 72, "省食物储备 (Provincial)", ["保留75%缓冲防严冬断粮", "军粮优先直接取自所在省粮仓"], c1, "#food-chain", "核心闸门"),
        _box(825, 40, 205, 72, "市场粮食贸易 (Market)", ["满溢(>75%)自动卖出赚国库", "不足且未被围攻→自动花钱买！"], c3, "#food-chain", "破产预警"),

        _box(280, 180, 205, 72, "人口升级/迁移/疫病", ["需≥相容文化+岗位方能晋升", "战后12月逃亡潮/25年3×拉力"], c2, "#migration-disease"),
        _box(545, 180, 220, 72, "饥荒惩戒 vs 繁荣/荒废", ["粮仓归零：人口−5%/月", "正繁荣靠和平；负荒废靠DIP恢复"], c3, "#prosperity-devastation"),
        _box(825, 180, 205, 72, "发展度与长期税基", ["正繁荣自动推高发展度", "发展度再抬高RGO/建筑上限"], c2, "#prosperity-devastation"),

        _edge(220, 76, 280, 76, "生产/消耗"),
        _edge(485, 76, 545, 76, "净结余"),
        _edge(765, 76, 825, 76, "自动买卖"),
        _edge(655, 112, 655, 180, "归零即饥荒", color=c3),
        _edge(485, 216, 545, 216, "人口留存"),
        _edge(765, 216, 825, 216, "正向滚雪球"),
    ]
    return _wrap_svg(1060, 285, "三级粮仓自动买卖机制、人口流动与繁荣-荒废循环", "".join(parts))


def diagram_ch03():
    c1, c2, c3 = "#b06c1d", "#1d6b6e", "#9b2c3d"
    parts = [
        _box(25, 40, 185, 72, "RGO原产 + 工坊建筑", ["扩建波动性(预判6月冲击)", "投产度>50%享最高+15%PE"], c1, "#production-buildings"),
        _box(265, 40, 195, 72, "市场接入度 (Access)", ["受距市中心距离/道/港(1.4.9)缩放", "折算工坊吞吐与RGO售价"], c1, "#market-network"),
        _box(515, 40, 195, 72, "地点月财富 (Wealth)", ["原产利润 + 建筑利润", "+ 本地市民贸易贡献"], c1, "#wealth-to-treasury"),
        _box(765, 40, 235, 72, "控制力分流：国库 vs 阶层", ["受控：财富×控制 → 阶层税基→征税入库", "未控：直接进阶层金库"], c3, "#wealth-to-treasury", "主权闸门"),

        _box(25, 180, 185, 72, "供需、目标价与市价", ["市价每月仅追赶5%差额", "上下限受物价稳定性锁定"], c2, "#market-network"),
        _box(265, 180, 195, 72, "贸易指令 & 关税补贴", ["贸易优势定出口抢货顺序", "贸易指令自动寻优 · 10/25/50%关税"], c2, "#trade-orders"),
        _box(515, 180, 195, 72, "贸易利润王室分成", ["按「王室力量份额」进国库", "其余贸易润直接归入各阶层"], c3, "#trade-orders"),
        _box(765, 180, 235, 72, "债务、债券与信誉度(0–100)", ["5年阶层贷(利息归内) vs 中央债券(永息)", "破产扣50信誉，每年仅回0.5(100年!)"], c3, "#finance-debt"),

        _edge(210, 76, 265, 76, "×接入比"),
        _edge(460, 76, 515, 76, "加总"),
        _edge(710, 76, 765, 76, "×控制力"),
        _edge(210, 216, 265, 216, "价差驱商"),
        _edge(460, 216, 515, 216, "净利润"),
        _edge(612, 180, 612, 112, "市民贸易部分", color=c2, dashed=True),
        _edge(882, 112, 882, 180, "净结余定借贷", color=c1),
    ]
    return _wrap_svg(1030, 285, "从商品价格与市场接入到国库税收及主权信用五步漏斗", "".join(parts))


def diagram_ch04():
    c1, c2, c3 = "#9b2c3d", "#5c4687", "#1d6b6e"
    parts = [
        _box(30, 35, 195, 72, "5大政体 & 政府力量", ["正统性 / 共和传统 / 奉献度", "游牧团结 / 部落凝聚力"], c1, "#government-power"),
        _box(285, 35, 200, 72, "17对社会价值观轴", ["−100至+100 · 受惯性(100)牵制", "集权+50%王室 / 改革解锁门槛"], c2, "#societal-values"),
        _box(545, 35, 210, 72, "官僚部门与百年固化", ["满经费生效正面；缺钱只剩负面", "每100年深化固化与裁撤重价"], c1, "#bureaucracy"),
        _box(815, 35, 200, 72, "法律政策与改革槽", ["政体/时代解锁法律选项", "实施期渐变加成 · 换法耗稳定"], c1, "#bureaucracy"),

        _box(30, 175, 195, 72, "儿童教育与34项角色互动", ["3岁启蒙/16成年 · 娶贵族防绝嗣", "赐法定男性/出家/指派总督"], c3, "#characters-interactions"),
        _box(285, 175, 200, 72, "政治影响力与内阁效率", ["君主+内阁均能月产(上限100)", "首相满10年翻倍但终身锁定"], c1, "#cabinet-actions"),
        _box(545, 175, 470, 72, "81项内阁行动三系调度（稀缺席位瓶颈）", ["ADM：提控(+10%上限)/促升/降通胀/思潮 | DIP：灾后恢复/安抚/同化 | MIL：整合/维稳/镇叛"], c1, "#cabinet-actions", "核心抓手"),

        _edge(225, 71, 285, 71, "互相塑造"),
        _edge(485, 71, 545, 71, "制度支撑"),
        _edge(755, 71, 815, 71, "法理协同"),
        _edge(127, 107, 127, 175, "君主/继承人"),
        _edge(225, 211, 285, 211, "人才供给"),
        _edge(485, 211, 545, 211, "执行速率"),
    ]
    return _wrap_svg(1045, 280, "政体底座、官僚固化、人物养成与内阁行动调度体系", "".join(parts))


def diagram_ch05():
    c1, c2, c3 = "#9b2c3d", "#b06c1d", "#1d6b6e"
    parts = [
        _box(25, 35, 195, 72, "王室 vs 阶层政治力量", ["同批人口两头计算(王室乘控制力)", "入阁/带兵为所属阶层+25%基础"], c1, "#power-balance"),
        _box(280, 35, 210, 72, "11项阶层互动与绝境求助", ["贿赂/削减拆私建/售艺术品/征私兵", "防御战绝境行动耗费与扣满减半！"], c1, "#estate-interactions", "新增重点"),
        _box(550, 35, 210, 72, "市民金库抽水与私建攻防", ["控制<75%阶层狂建阶层私产/私军", "「紧急拨款」无息划走市民最多50%"], c2, "#estate-wealth"),
        _box(820, 35, 200, 72, "议会与59月博弈", ["基础支持 = 王室份额×0.5", "过50%胜出；撤特权暴跌−25%−3Δ"], c1, "#parliament"),

        _box(160, 175, 230, 72, "阶层满意度与人群满意度", ["<25% 拒出征召兵 | <1% 停税", "人群 = 20%基 + 阶层 + 文宗物价"], c3, "#rebellions"),
        _box(460, 175, 230, 72, "叛乱运动阈值(5,000人分水岭)", ["<5,000支持→原地小规模 −0.5%月控", "≥5,000支持→爆发内战/分离起义"], c1, "#rebellions"),
        _box(760, 175, 260, 72, "要塞守军倒戈检定(10–90%)", ["基50 + 30×满意 ± 文化宗教动乱", "进度>80%−20！善用「激起反叛」抢先动手"], c1, "#rebellions", "防丢要塞"),

        _edge(220, 71, 280, 71, "筹码博弈"),
        _edge(490, 71, 550, 71, "金库吞吐"),
        _edge(760, 71, 820, 71, "份额定话语"),
        _edge(385, 107, 290, 175, "扣满震荡", color=c2),
        _edge(390, 211, 460, 211, "降破阈值"),
        _edge(690, 211, 760, 211, "触发起义检定"),
    ]
    return _wrap_svg(1050, 280, "王室与阶层权力金库攻防、11项阶层互动与叛乱要塞检定", "".join(parts))


def diagram_ch06():
    c1, c2, c3 = "#5c4687", "#1d6b6e", "#9b2c3d"
    parts = [
        _box(30, 35, 195, 72, "五级文化地位 & 容量", ["主流 / 已接纳 / 相容 / 忽视 / 歧视", "相容可升阶征兵但不能核心化！"], c1, "#culture-status"),
        _box(290, 35, 215, 72, "文化战争与同化速度", ["进攻文化影响力 vs 防御文化传统", "同语族/统合文化组/非市语民加速"], c1, "#assimilation-merge"),
        _box(570, 35, 200, 72, "50% 人口跨过核心门槛", ["主流 + 已接纳占比 ≥ 50%", "触发已整合地自动升级为核心"], c2, "#culture-status", "领土联动"),
        _box(830, 35, 195, 72, "四大语言与艺术骑士团", ["礼仪语定科研 · 宫廷语定贵族", "艺术品蓄文化力 · 骑士团赠强修正"], c1, "#languages-art"),

        _box(160, 175, 225, 72, "三级宗教容忍 & 改信", ["正统 / 异端 / 异教容忍度", "绑定信仰的文化需先改信方能同化"], c1, "#religion-system"),
        _box(465, 175, 235, 72, "教宗、五大牧首区与多信仰", ["教廷诏书/绝罚 · 集齐5席位翻倍", "清净度>75涨荣辱 · 末日值献祭"], c2, "#religion-system"),
        _box(780, 175, 245, 72, "宗教修会：热忱与圣召双刃", ["和退战进之热忱 · 按国体量缩放地位", "忠诚赐圣召祝福；不忠变负面重担"], c3, "#religious-orders", "跨国影响"),

        _edge(225, 71, 290, 71, "推动转变"),
        _edge(505, 71, 570, 71, "推高占比"),
        _edge(770, 71, 830, 71, "文化地位反馈"),
        _edge(385, 211, 465, 211, "教派行动"),
        _edge(700, 211, 780, 211, "据点网络"),
        _edge(272, 175, 360, 107, "先皈依后同化", color=c2, dashed=True),
    ]
    return _wrap_svg(1055, 280, "文化核心化50%链路、四大语言与多宗教/修会生态", "".join(parts))


def diagram_ch07():
    c1, c2, c3 = "#5c4687", "#1d6b6e", "#b06c1d"
    parts = [
        _box(25, 35, 190, 72, "六大时代与焦点选择", ["传统/复兴/探索/改革/绝对/革命", "ADM/DIP/MIL焦点定制革新池"], c1, "#ages-institutions"),
        _box(275, 35, 215, 72, "18种思潮诞生与传播", ["经跨市贸易与ADM「研究思潮」扩散", "满传播地点占全国总人口≥20%接纳"], c1, "#ages-institutions"),
        _box(550, 35, 215, 72, "革新研发与储备研究力", ["礼仪语+均识字率+教士满意+思潮数", "未选项目自动积攒研究储量"], c3, "#research-advances"),
        _box(825, 35, 200, 72, "局势、灾难、使命与自动化", ["24历史局势 · 38国家灾难月检定", "合理开关内政/贸易自动化"], c1, "#situations-disasters"),

        _box(160, 175, 235, 72, "海陆探险与海军/殖民范围", ["ADM减探险月耗 · MIL加推进速度", "发现未知之地解锁互动"], c2, "#exploration"),
        _box(470, 175, 255, 72, "特许殖民地(省限3个并行)", ["仅限「核心」地点输出殖民迁徙人口！", "满1,000人且文化/宗教达标即定居归属"], c2, "#colonial-charters", "核心硬要求"),
        _box(795, 175, 230, 72, "新定居领土与殖民领/征服者", ["定居地直接跳过未整合(colonized)", "跨海输入热带香料奴隶返哺母国"], c3, "#colonial-charters"),

        _edge(215, 71, 275, 71, "开放思潮"),
        _edge(490, 71, 550, 71, "≥20%人口"),
        _edge(765, 71, 825, 71, "时代推进"),
        _edge(395, 211, 470, 211, "揭开地图"),
        _edge(725, 211, 795, 211, "完成定居"),
        _edge(650, 107, 600, 175, "革新技术解锁殖民/范围", color=c2, dashed=True),
    ]
    return _wrap_svg(1055, 280, "时代思潮20%门槛、革新科研公式与核心供血殖民体系", "".join(parts))


def diagram_ch08():
    c1, c2, c3 = "#3d5467", "#9b2c3d", "#b06c1d"
    parts = [
        _box(25, 35, 205, 72, "征召兵 vs 正规军 vs 佣兵", ["征召=75%战力/死扣真实人口/240月恢复", "正规=部队族系共享上限(10%升级费)"], c1, "#force-types"),
        _box(290, 35, 205, 72, "四阵位部署与开幕炮击", ["中军+左右翼+预备队 · 混编(<50%)", "默认按日: 3天轰击阶段 / 4天轮换"], c1, "#battle-mechanics"),
        _box(555, 35, 220, 72, "D100 主动接敌与 D20 增援", ["接敌基60%+min(30%,主动×2.5%)+3%/天", "未接敌挨打：兵伤×1.1、士伤×1.2"], c2, "#battle-mechanics"),
        _box(835, 35, 195, 72, "10:1/2:1歼灭与战俘", ["10:1首日/2:1溃灭 · 40%俘获死亡", "赎金(60天)或0.25×价收编佣兵"], c2, "#prisoners-overrun"),

        _box(160, 175, 240, 72, "三级后勤与跨海海军供粮", ["驻扎吃省粮 · 前线靠2格补给站", "海军收集/分发食物跨海补给孤军"], c3, "#siege-supply"),
        _box(470, 175, 235, 72, "要塞控制区(ZoC)与围城", ["30天/跳，兵数≥守军(无防100)", "缺水−5%守军/+3进度 · 强攻代价大"], c1, "#siege-forts"),
        _box(775, 175, 255, 72, "占领毁粮、劫掠与焦土", ["占领瞬毁90%存粮 + 12月looted修正", "焦土令敌移动+50%耗并月损−5%繁荣"], c2, "#siege-supply"),

        _edge(230, 71, 290, 71, "编组入阵"),
        _edge(495, 71, 555, 71, "D10交火"),
        _edge(775, 71, 835, 71, "胜负结算"),
        _edge(400, 211, 470, 211, "无粮+5%损耗"),
        _edge(705, 211, 775, 211, "攻克或防御"),
    ]
    return _wrap_svg(1060, 280, "兵源代价对比、四阵位日步战斗判定与跨海后勤/焦土机制", "".join(parts))


def diagram_ch09():
    c1, c2, c3 = "#3d5467", "#1f4e8c", "#9b2c3d"
    parts = [
        _box(30, 35, 195, 72, "正规海军与海战退败", ["船体减伤 · 火炮加伤 · 征召船仅5%影响", "士气<1.5(半值)强撤；<10%耐久沉没判定"], c1, "#naval-combat"),
        _box(285, 35, 215, 72, "港口封锁五大惨痛重创", ["按人口/发展/贸易核定封锁需求船数", "封锁扣粮食、海存、发展、控制、繁荣"], c3, "#naval-combat"),
        _box(560, 35, 225, 72, "海上存在与 90% 巡逻陷阱", ["海军传统+50%相对海存", "自动巡逻达90即走！5–10轻船驻停锁100"], c2, "#maritime-presence", "实战核心"),
        _box(845, 35, 185, 72, "私掠者 vs 反海盗作战", ["偷月入/降海存/2.5%月掳沿海奴", "反海盗舰船持续耗空私掠耐久"], c3, "#privateers"),

        _box(160, 175, 235, 72, "113种CB与战分三支柱", ["20间谍网造CB(或议会/事件)", "总分100 = 占领 + 战斗(≤50) + 目标(≤25)"], c2, "#warfare-peace"),
        _box(465, 175, 240, 72, "和约修正：要塞、宿敌与核心", ["未围要塞割地−33%效率(先围减至−15%)", "宿敌+33% · 大国减耗−33% · 还核0.5×"], c1, "#peace-terms"),
        _box(775, 175, 255, 72, "投降呼吁、赔款与停战期", ["无条件投降数月不和反涨我厌战度", "和平夺金加通胀 · 战败国入5–10年休战"], c3, "#peace-terms"),

        _edge(225, 71, 285, 71, "夺取制海"),
        _edge(500, 71, 560, 71, "控海线"),
        _edge(785, 71, 845, 71, "攻防对抗"),
        _edge(395, 211, 465, 211, "结算筹码"),
        _edge(705, 211, 775, 211, "敲定条款"),
        _edge(392, 107, 290, 175, "封锁贡献战分", color=c2, dashed=True),
    ]
    return _wrap_svg(1055, 280, "制海封锁、90%海巡陷阱与战争分数/和约折扣全览", "".join(parts))


def diagram_ch10():
    c1, c2, c3 = "#1f4e8c", "#9b2c3d", "#1d6b6e"
    parts = [
        _box(25, 35, 200, 72, "外交容量与强盟饱和度", ["同盟费随对方经济&好感浮动", "列强盟友1.0 / 区域强权0.5超额+0.3/盟"], c1, "#diplo-capacity"),
        _box(285, 35, 205, 72, "间谍网 & 25点信息迷雾", ["20造CB · 25透视军备要塞+暴露风险", "30扶叛 · 50全破战争迷雾"], c1, "#intelligence-fow"),
        _box(550, 35, 225, 72, "敌意(AE)与50/−50包围网", ["差异+扩张震荡(对好感×−4)", ">50敌意且<−50好感入网；<30方退出"], c2, "#antagonism-coalition", "防爆指南"),
        _box(835, 35, 195, 72, "属国代消与割地减半AE", ["和约直接割给属国减 −50% AE", "释放省份/建筑属国避内阁瓶颈"], c3, "#subjects-annex"),

        _box(160, 175, 245, 72, "属国连通度与20%集团警戒", ["陆连每跨1个0控地区扣20分(满100)", "众属国超总和20%按−60倍率重扣忠诚"], c2, "#subjects-annex"),
        _box(475, 175, 250, 72, "22种属国与共主邦联(PU)", ["吞并需好感≥190 & 交界控制≥35%", "PU晚入成员须开邦联议会逐级追赶"], c1, "#pu-and-ios"),
        _box(795, 175, 235, 72, "神罗行政圈、天朝与教廷", ["多国决议投票 · 单一行政圈投票上限35%", "天朝威仪/朝贡与罗马教廷枢机表决"], c1, "#pu-and-ios"),

        _edge(225, 71, 285, 71, "博弈工具"),
        _edge(490, 71, 550, 71, "扩张后果"),
        _edge(775, 71, 835, 71, "泄压分流"),
        _edge(932, 107, 900, 175, "管理属国", color=c3),
        _edge(405, 211, 475, 211, "忠诚>50方吞并"),
        _edge(725, 211, 795, 211, "多边体制"),
    ]
    return _wrap_svg(1055, 280, "强盟饱和惩罚、属国连通/实力双线与国际组织机制图", "".join(parts))


CHAPTER_DIAGRAMS = {
    "ch01": diagram_ch01,
    "ch02": diagram_ch02,
    "ch03": diagram_ch03,
    "ch04": diagram_ch04,
    "ch05": diagram_ch05,
    "ch06": diagram_ch06,
    "ch07": diagram_ch07,
    "ch08": diagram_ch08,
    "ch09": diagram_ch09,
    "ch10": diagram_ch10,
}


def build_home_svg(home_nodes, home_edges):
    colors = {
        "territory": "#1d6b6e",
        "economy": "#b06c1d",
        "state": "#9b2c3d",
        "culture": "#5c4687",
        "military": "#3d5467",
        "diplomacy": "#1f4e8c",
    }
    pos = {n["id"]: (n["x"], n["y"]) for n in home_nodes}
    w, h = 240, 82
    edge_paths, edge_labels = [], []
    # Wide 1120x470 grid: centers x=155,560,965 (165px horiz gap); y=145,365 (138px vert gap)
    custom_lines = [
        ("territory", "economy", (275, 145), (440, 145), 0, 0.5, (0, 0)),
        ("economy", "state", (680, 145), (845, 145), 0, 0.5, (0, 0)),
        ("state", "territory", (965, 104), (155, 104), -72, 0.5, (0, 0)),
        ("culture", "territory", (155, 324), (155, 186), 0, 0.5, (0, 0)),
        ("state", "culture", (845, 182), (275, 338), 42, 0.22, (0, 0)),
        ("economy", "military", (560, 186), (560, 324), 0, 0.5, (0, 0)),
        ("military", "territory", (465, 324), (245, 186), 0, 0.52, (0, 0)),
        ("military", "diplomacy", (680, 365), (845, 365), 0, 0.5, (0, 0)),
        ("diplomacy", "state", (965, 324), (965, 186), 0, 0.5, (0, 0)),
    ]
    lbl_map = {(a, b): lbl for a, b, lbl in home_edges}
    for a, b, p1, p2, cv, lt, lo in custom_lines:
        lbl = lbl_map.get((a, b), "")
        ep, el = _edge_parts(p1[0], p1[1], p2[0], p2[1], lbl, color=colors[a], curve=cv, label_t=lt, label_offset=lo)
        edge_paths.append(ep)
        if el:
            edge_labels.append(el)

    node_parts = []
    for n in home_nodes:
        col = colors[n["id"]]
        nx, ny = n["x"] - w / 2, n["y"] - h / 2
        node_parts.append(
            f'<a href="{escape(n["href"])}" class="home-pillar-link" data-pillar="{n["id"]}">'
            + _box(nx, ny, w, h, n["zh"], [n["sub"]], color=col)
            + '</a>'
        )
    return (
        '<svg viewBox="0 0 1120 470" class="home-svg" role="img" aria-label="EU5六大支柱总联结图">'
        '<defs><marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
        '<path d="M 0 1 L 10 5 L 0 9 z" fill="var(--accent-2)" /></marker></defs>'
        + "".join(edge_paths) + "".join(node_parts) + "".join(edge_labels) + '</svg>'
    )
