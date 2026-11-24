# -*- coding: utf-8 -*-
"""
Human-Readable Game Data & Modifier Source Compiler for EU5 1.4.9.
Transforms raw script tokens, unscaled modifier numbers, and AST condition dumps
across all 22 structured ledgers, 72 catalogs (23,216 records), and 1,364 modifiers
into clear, idiomatic Chinese prose and structured key-value cards.
"""
import collections
import glob
import json
import os
import re

GAME_DIR = r"D:\SteamLibrary\steamapps\common\Europa Universalis V\game"
ATLAS_DIR = r"C:\Users\seepath\Documents\Codex\2026-11-02\x20\work\eu5-atlas"
PROJ_DIR = r"C:\Users\seepath\.gemini\antigravity\scratch\eu5-compendium"
DATA_DIR = os.path.join(PROJ_DIR, "data")
ASSETS_DIR = os.path.join(PROJ_DIR, "docs", "assets")

DLC_NAMES = {
    "d008_fate_of_the_phoenix": "《拜占庭：凤凰宿命》",
    "d009_across_the_pillars": "《跨越海峡》",
    "d015_ancient_monuments_pack": "《古代纪念建筑包》",
    "d001": "扩展内容包",
}

ARTIST_TYPES_ZH = {
    "painter": "画家",
    "sculptor": "雕塑家",
    "writer": "作家",
    "composer": "作曲家",
    "scientist": "科学家",
    "philosopher": "哲学家",
    "architect": "建筑师",
    "calligrapher": "书法家",
    "poet": "诗人",
    "metalworker": "金工匠师",
    "jurist": "法学家",
    "iconographer": "圣像画师",
}

WARGOAL_TYPES_ZH = {
    "superiority": "展现优势（打赢野战赚取持续战分）",
    "take_province": "夺取目标省份",
    "take_capital": "攻占敌国首都",
    "take_country": "吞并/征服目标国",
    "take_border": "夺取边境领土",
    "defend_capital": "保卫本国首都",
    "naval_superiority": "夺取制海权与封锁",
    "blockade_ports": "封锁敌方港口",
    "humiliate": "羞辱宿敌",
    "enforce_religion": "强制改宗",
    "independence": "争取独立",
}

DECISION_CAT_ZH = {
    "country_specific_decisions": "国别专属决议",
    "infrastructure_decisions": "大型基建工程决议",
    "religious_decisions": "宗教事务决议",
    "government_decisions": "政体与行政决议",
    "cultural_decisions": "文化事务决议",
    "economy_decisions": "经济金融决议",
    "military_decisions": "军事防务决议",
    "diplomatic_decisions": "外交战略决议",
}

GROUP_LABELS_ZH = {
    "societal_values": "社会价值观",
    "building_types": "建筑",
    "estate_privileges": "阶层特权",
    "government_reforms": "政府改革",
    "policy": "法律政策",
    "laws": "法律",
    "bureaucracies": "官僚机构",
    "cabinet_actions": "内阁行动",
    "town_rights": "城镇特权",
    "advances": "时代革新",
    "static_modifiers": "基础状态与环境修正",
    "auto_modifiers": "国家自动修正",
    "estates": "阶层属性",
    "pop_types": "人口阶级与识字率",
    "religions": "宗教定义",
    "religious_aspects": "宗教信条",
    "religious_schools": "宗教学派",
    "religious_focuses": "宗教改革重心",
    "religious_order_callings": "修会圣召",
    "gods": "神祇赐福",
    "parliament_issues": "议会议案",
    "parliament_types": "议会制度",
    "traits": "人物特质",
    "road_types": "道路等级",
    "industry_types": "产业扶持政策",
    "location_ranks": "城乡地点等级",
    "topography": "地形地貌",
    "climates": "气候带",
    "vegetation": "地表植被",
    "age": "时代全局规则",
    "government_types": "五大政体",
    "country_ranks": "国家等级",
    "hegemons": "世界霸权",
    "subject_types": "属国类型",
    "international_organizations": "国际组织",
    "diseases": "疫病修正",
    "regencies": "摄政状态",
    "artist_work": "艺术品类型",
}


def _parse_simple_kv_blocks(folder_path):
    """Parse top-level block = { key = val ... } across .txt files in a folder."""
    res = {}
    if not os.path.isdir(folder_path):
        return res
    for fn in sorted(os.listdir(folder_path)):
        if not fn.endswith(".txt") or fn.startswith("__") or fn == "readme.txt":
            continue
        txt = open(os.path.join(folder_path, fn), encoding="utf-8-sig", errors="ignore").read()
        txt = re.sub(r"#[^\n]*", "", txt)
        i = 0
        while i < len(txt):
            m = re.search(r"([A-Za-z0-9_]+)\s*=\s*\{", txt[i:])
            if not m:
                break
            key = m.group(1)
            b_start = i + m.end() - 1
            line_s = txt.rfind("\n", 0, i + m.start()) + 1
            if txt[line_s:i + m.start()].strip():
                i = b_start + 1
                continue
            depth = 0
            j = b_start
            while j < len(txt):
                if txt[j] == "{":
                    depth += 1
                elif txt[j] == "}":
                    depth -= 1
                    if depth == 0:
                        break
                j += 1
            res[key] = txt[b_start + 1:j]
            i = j + 1
    return res


def load_game_context(zh_kv):
    """Build lookup tables for goods demands, prices, diplomatic costs, languages, cultures, gods."""
    ctx = {
        "goods_zh": {},
        "demands": {},
        "prices": {},
        "diplo_costs": {},
        "lang_cultures": collections.defaultdict(list),
        "lang_religions": collections.defaultdict(list),
        "lang_family": {},
        "culture_info": {},
        "god_info": {},
    }

    # 0. Enrich zh_kv with clean Chinese titles from atlas catalog-data (languages, cultures, religions, io, etc.)
    cat_dir = os.path.join(ATLAS_DIR, "dist", "catalog-data")
    if os.path.isdir(cat_dir):
        for fn in ("languages.js", "cultures.js", "religions.js", "international_organizations.js", "goods.js"):
            fp = os.path.join(cat_dir, fn)
            if os.path.exists(fp):
                s_js = open(fp, encoding="utf-8").read()
                m_js = re.search(r"window\.atlasRegister\((\{.*\})\)", s_js, re.S)
                if m_js:
                    for rec in json.loads(m_js.group(1)).get("records", []):
                        if rec.get("id") and rec.get("zh"):
                            zh_kv.setdefault(rec["id"], rec["zh"])

    # 1. Goods Chinese names
    gf_path = os.path.join(ATLAS_DIR, "research", "goods-fields.json")
    if os.path.exists(gf_path):
        for g in json.load(open(gf_path, encoding="utf-8")):
            ctx["goods_zh"][g["id"]] = g["zh"]

    # 2. Goods demand bundles (construction / maintenance)
    gd_dir = os.path.join(GAME_DIR, "in_game", "common", "goods_demand")
    for fn in glob.glob(os.path.join(gd_dir, "*.txt")):
        blocks = _parse_simple_kv_blocks(os.path.dirname(fn)) if False else {}
    for k, body in _parse_simple_kv_blocks(gd_dir).items():
        parts = []
        for mk in re.finditer(r"^\s*([a-zA-Z0-9_]+)\s*=\s*([0-9.\-]+)", body, re.M):
            gk, gv = mk.group(1), mk.group(2)
            if gk in ctx["goods_zh"]:
                parts.append(f"{ctx['goods_zh'][gk]} {gv}")
        if parts:
            zh_k = zh_kv.get(k, "")
            ctx["demands"][k] = "、".join(parts)
            if zh_k:
                ctx["demands"][zh_k] = "、".join(parts)

    # 3. Prices (gold / stability / political_influence / government_power / prestige)
    cur_zh = {
        "gold": "金币",
        "scaled_gold": "×经济基础金币",
        "stability": "稳定度",
        "political_influence": "政治影响力",
        "government_power": "政府力量",
        "prestige": "威望",
        "manpower": "人力(千)",
        "sailors": "水手(千)",
        "religious_influence": "宗教影响力",
    }
    for k, body in _parse_simple_kv_blocks(os.path.join(GAME_DIR, "in_game", "common", "prices")).items():
        parts = []
        for mk in re.finditer(r"^\s*([a-zA-Z0-9_]+)\s*=\s*([0-9.\-]+)", body, re.M):
            ck, cv = mk.group(1), mk.group(2)
            if ck in cur_zh:
                parts.append(f"{cv} {cur_zh[ck]}")
        if parts:
            s_val = " + ".join(parts)
            ctx["prices"][k] = s_val
            zh_k = zh_kv.get(k, "")
            if zh_k:
                ctx["prices"][zh_k] = s_val

    # 4. Diplomatic costs (spy_network / favors)
    dc_zh = {"spy_network": "间谍网", "favors": "人情", "diplomatic_capacity": "外交容量"}
    for k, body in _parse_simple_kv_blocks(os.path.join(GAME_DIR, "in_game", "common", "diplomatic_costs")).items():
        parts = []
        for mk in re.finditer(r"^\s*([a-zA-Z0-9_]+)\s*=\s*([0-9.\-]+)", body, re.M):
            ck, cv = mk.group(1), mk.group(2)
            parts.append(f"{dc_zh.get(ck, ck)} {cv}")
        if parts:
            ctx["diplo_costs"][k] = " + ".join(parts)

    # 5. Cultures -> Languages & Culture Groups
    for k, body in _parse_simple_kv_blocks(os.path.join(GAME_DIR, "in_game", "common", "cultures")).items():
        m_lang = re.search(r"\blanguage\s*=\s*([A-Za-z0-9_]+)", body)
        groups = re.findall(r"culture_groups\s*=\s*\{([^}]*)\}", body)
        grp_list = []
        for g_str in groups:
            grp_list.extend(re.findall(r"[A-Za-z0-9_]+", g_str))
        lang_id = m_lang.group(1) if m_lang else ""
        czh = zh_kv.get(k, k)
        if lang_id:
            ctx["lang_cultures"][lang_id].append(czh)
        ctx["culture_info"][k] = {
            "lang": zh_kv.get(lang_id, lang_id) if lang_id else "",
            "groups": [zh_kv.get(g, g) for g in grp_list],
        }

    # 6. Religions -> Liturgical language
    for k, body in _parse_simple_kv_blocks(os.path.join(GAME_DIR, "in_game", "common", "religions")).items():
        m_lang = re.search(r"\blanguage\s*=\s*([A-Za-z0-9_]+)", body)
        if m_lang:
            lid = m_lang.group(1)
            ctx["lang_religions"][lid].append(zh_kv.get(k, k))

    # 7. Gods -> ability & religions
    for k, body in _parse_simple_kv_blocks(os.path.join(GAME_DIR, "in_game", "common", "gods")).items():
        m_ab = re.search(r"\bability\s*=\s*(ADM|DIP|MIL)", body, re.I)
        rels = re.findall(r"\breligion\s*=\s*([A-Za-z0-9_]+)", body)
        grps = re.findall(r"\bgroup\s*=\s*([A-Za-z0-9_]+)", body)
        ctx["god_info"][k] = {
            "ability": m_ab.group(1).upper() if m_ab else "",
            "religions": [zh_kv.get(r, r) for r in rels if r not in ("religion",)],
            "groups": [zh_kv.get(g, g) for g in grps if g not in ("group",)],
        }

    return ctx


def load_metric_sources():
    """Load metric-sources.json and build (group, id) -> formatted modifiers list."""
    ms_path = os.path.join(ATLAS_DIR, "research", "metric-sources.json")
    ms = json.load(open(ms_path, encoding="utf-8"))["modifiers"]
    mods_by_item = collections.defaultdict(list)
    for mod_key, mod_info in ms.items():
        zh_name = mod_info.get("zh", mod_key)
        for src in mod_info.get("sources", []):
            disp = src.get("display", "")
            if disp == "是":
                disp = "启用"
            elif disp == "否":
                disp = "禁用"
            mods_by_item[(src["group"], src["id"])].append({
                "mod_key": mod_key,
                "zh": zh_name,
                "display": disp,
                "scope": src.get("scope", ""),
                "condition": src.get("condition", ""),
            })
    return ms, mods_by_item


def format_item_modifiers(mods_list, max_items=12):
    """Format a list of modifier dicts into natural Chinese, deduplicating cleanly."""
    seen = []
    out = []
    for m in mods_list:
        zh = m["zh"]
        disp = m["display"]
        if zh.startswith("启用") and disp == "启用":
            piece = zh
        elif zh.startswith("本地可") and disp == "启用":
            piece = f"允许{zh[3:]}" if zh.startswith("本地可") else f"{zh}：启用"
        elif disp == "启用":
            piece = f"开启「{zh}」"
        else:
            piece = f"{zh} {disp}"
        if piece not in seen:
            seen.append(piece)
            out.append(piece)
    if not out:
        return ""
    res = "、".join(out[:max_items])
    if len(out) > max_items:
        res += f" 等 {len(out)} 项修正"
    return res


def humanize_condition(text, zh_kv=None, game_ctx=None):
    """Convert Paradox script / AST expressions into idiomatic, readable Chinese."""
    if not text:
        return ""
    zh_kv = zh_kv or {}
    s = str(text).strip()

    # Strip boilerplate applicability prefixes
    s = re.sub(r"^定义未列国别或特殊获取限制；仍需满足时代、资源、选址及执行条件。\s*", "", s)
    s = re.sub(r"^资格受制度、宗教、文化、地理、组织或扩展内容条件限制。\s*", "", s)

    # Replace DLC keys
    for dk, dv in DLC_NAMES.items():
        s = re.sub(rf"\bhas_dlc\s+{dk}\b", f"需启用扩展包{dv}", s, flags=re.I)
        s = re.sub(rf"\b{dk}\b", dv, s, flags=re.I)

    # Replace artist_type & war_goal_type & decision categories & diplomatic_cost
    for ak, av in ARTIST_TYPES_ZH.items():
        s = re.sub(rf"\bartist_type\s+{ak}\b", f"艺术家职业为{av}", s)
    for wk, wv in WARGOAL_TYPES_ZH.items():
        s = re.sub(rf"\bwar_goal_type\s+{wk}\b", f"战争目标：{wv}", s)
        s = re.sub(rf"\b类型\s+{wk}\b", f"目标类型：{wv}", s)
    for dk, dv in DECISION_CAT_ZH.items():
        s = s.replace(dk, dv)
    if game_ctx:
        for dck, dcv in game_ctx["diplo_costs"].items():
            s = s.replace(f"diplomatic_cost {dck}", f"外交消耗：{dcv}")
            s = s.replace(dck, dcv)
        for pk, pv in game_ctx["prices"].items():
            s = s.replace(f"proposal_price {pk}", f"提议花费：{pv}")
            s = s.replace(f"价格 {pk}", f"执行花费：{pv}")

    # Common script phrase translations (ordered longest/most specific first)
    replacements = [
        (r"has_primary_or_accepted_culture\s+prev\.dominant_culture", "当地优势文化为本国主流或已接纳文化"),
        (r"has_primary_or_accepted_culture", "属于本国主流或已接纳文化"),
        (r"merged_culture_group_contains_culture", "已统合文化组包含该文化"),
        (r"is_member_of_international_organization\s+", "属于国际组织："),
        (r"is_leader_of_international_organization\s+", "担任国际组织领袖："),
        (r"international_organization_has_policy\s+", "国际组织已启用政策："),
        (r"international_organization_has_law\s+", "国际组织已设立法律："),
        (r"has_unlocked_government_reform_trigger\s*", "已解锁政府改革"),
        (r"has_unlocked_policy_trigger\s*", "已解锁政策"),
        (r"has_completed_religious_focus\s+", "已完成前置宗教改革："),
        (r"can_build_units_of_category\s+", "可招募兵种类别："),
        (r"game_has_missions_enabled\s+是", "开局规则已启用国家使命"),
        (r"has_enabled_mission_trigger", "已开放对应使命路线"),
        (r"has_embraced_institution\s+", "已接纳思潮："),
        (r"current_age_or_later（时代\s*([^）]+)）", r"时代达到「\1」或更晚"),
        (r"current_age_or_later\s+", "时代达到或晚于："),
        (r"current_age\s+", "当前时代为："),
        (r"has_or_had_tag\s+", "当前或曾为："),
        (r"original_capital\.region", "初始首都所在大区"),
        (r"original_capital", "初始首都"),
        (r"original_tag\s+", "初始国家为："),
        (r"has_culture_group\s+", "文化组属于："),
        (r"country_has_estate\s+", "国内存在阶层："),
        (r"has_estate_privilege\s+", "已授予特权："),
        (r"has_country_modifier\s+", "具有国家修正："),
        (r"is_situation_active\s+", "历史局势进行中："),
        (r"situation_is_active\s+是", "局势正在进行"),
        (r"is_religion_enabled\s+是", "该宗教已创立启用"),
        (r"has_town_rights\s+", "地点已设城镇特权："),
        (r"has_societal_value\s+", "社会价值观满足："),
        (r"has_reform\s+", "已采用改革："),
        (r"has_policy\s+", "已实行政策："),
        (r"has_trait\s+", "具备特质："),
        (r"has_ruler\s+是", "当前有成年在位统治者"),
        (r"has_ruler\s+否", "当前无在位统治者（摄政期）"),
        (r"has_ports\s+是", "拥有至少一座沿海港口"),
        (r"num_of_ports\s*>\s*0", "拥有沿海港口"),
        (r"num_of_non_rural\s*>\s*0", "拥有至少一座城镇或城市"),
        (r"num_locations\s*>\s*0", "拥有至少一处地点"),
        (r"is_market_center\s+是", "须为市场中心"),
        (r"is_market_center\s+否", "非市场中心"),
        (r"is_canal_open\s+否", "运河尚未凿通"),
        (r"运河通航\s+否", "运河尚未凿通"),
        (r"is_port\s+是", "位于港口地点"),
        (r"is_capital\s+是", "位于本国首都"),
        (r"首都\s+是", "须为首都"),
        (r"为属国\s+否", "须为独立主权国家"),
        (r"无法升级地点\s+否", "地点允许升级"),
        (r"papacy_active\s+是", "天主教廷机制处于启用状态"),
        (r"block_when_at_war\s+是", "交战期间不可执行"),
        (r"at_war\s+是", "处于战争状态"),
        (r"at_war\s+否", "处于和平状态"),
        (r"in_combat\s+否", "部队未在交战中"),
        (r"is_moving\s+否", "部队处于静止驻留状态"),
        (r"is_exiled\s+否", "部队未处于流亡状态"),
        (r"is_alive\s+是", "目标人物在世"),
        (r"country_exists\s+", "国家仍然存在："),
        (r"has_discovered\s+", "已探索发现："),
        (r"is_subject_type\s+", "属国类型为："),
        (r"is_emperor\s+是", "身为神圣罗马帝国皇帝"),
        (r"law_gov_group\s+", "适用政体类别："),
        (r"country_potential\s*（", "国家条件（"),
        (r"location_potential\s*（", "地点选址（"),
        (r"potential_trigger\s*（", "可见条件（"),
        (r"visible\s*（", "可见条件（"),
        (r"\bis_special\s+是[；。,\s]*", ""),
        (r"\bis_foreign\s+否[；。,\s]*", ""),
        (r"\bis_foreign\s+是", "可在外国领土建造"),
        (r"\bscope:actor\b", "发起国"),
        (r"\bscope:recipient\b", "目标国"),
        (r"\bscope:target\b", "目标对象"),
        (r"@[A-Za-z0-9_]+!", ""),
        (r"Show[A-Za-z0-9_]+\s*\(\s*'([^']+)'\s*\)", lambda m: f"「{zh_kv.get(m.group(1), m.group(1))}」"),
        (r"define:[A-Za-z0-9_]+\|LOW_CONTROL_THRESHOLD_FOR_BEST_TAX", "最佳征税控制力阈值"),
        (r"define:[A-Za-z0-9_]+\|([A-Z0-9_]+)", r"系统阈值(\1)"),
        (r"progress：selected_area（value\s+area_average_control\([^)]*\)）", "进度按所选地区平均控制力计算"),
        (r"progress：selected_province（value\s+[^）]*）", "进度按所选省份状态计算"),
        (r"COUNTRY\.GetName", "本国"),
        (r"与本国处于war状态的任何国家", "与本国交战的任意国家"),
        (r"本国的任何province", "本国任意省份"),
        (r"本国的任何core", "本国任意核心地点"),
        (r"本国现存的任何culture", "本国境内任意文化"),
        (r"任何有foreign_building且归本国owned的location", "本国拥有外国建筑的任意地点"),
        (r"\b[a-z0-9_]+_upkeep_cost\b", "持续占用外交容量维护费"),
        (r"\bscope:winner\b", "战胜方"),
        (r"\bscope:loser\b", "战败方"),
        (r"\bscope:war\b", "当前战争"),
        (r"\bactor（", "发起国（"),
        (r"\brecipient（", "目标国（"),
        (r"\bwinner（", "战胜方（"),
        (r"\bloser（", "战败方（"),
        (r"\broot\.owner\.culture\b", "部队所属国主流文化"),
        (r"\broot\.owner\.religion\b", "部队所属国国教"),
        (r"\broot\.owner\b", "所属国家"),
        (r"\bprev\.dominant_culture\b", "当地优势文化"),
        (r"\bunit_location\b", "部队所在地点"),
        (r"\bany_owned_location\b", "任意直辖地点"),
        (r"\bany_cabinet_character\b", "内阁大臣满足"),
        (r"\bany_pop\b", "当地任意人群"),
        (r"\breligion\.group\b", "宗教组"),
        (r"\bculture\.language\b", "文化所属语言"),
        (r"\bdefender_leader\b", "防御方盟主"),
        (r"\bcount\s*>=\s*", "数量 ≥ "),
        (r"\bcount\s*>\s*", "数量 > "),
        (r"\bnum_privileges\s*<\s*", "当前特权数 < "),
        (r"\bnum_possible_privileges\s*>\s*0", "仍有可授予特权"),
        (r"恒定结果\s+否", "仅由特定历史事件触发"),
        (r"恒定结果\s+是", "常规开放"),
        (r"取反（", "不满足（"),
        (r"排除（", "非（"),
        (r"均不满足（", "均非（"),
        (r"任意一项（", "满足其一（"),
        (r"任一（", "满足其一（"),
        (r"全部条件（", "同时满足（"),
        (r"government_reform:([A-Za-z0-9_]+)", lambda m: f"「{zh_kv.get(m.group(1), m.group(1))}」"),
        (r"location:([A-Za-z0-9_]+)", lambda m: zh_kv.get(m.group(1), m.group(1))),
        (r"religion:([A-Za-z0-9_]+)", lambda m: zh_kv.get(m.group(1), m.group(1))),
        (r"situation:([A-Za-z0-9_]+)", lambda m: zh_kv.get(m.group(1), m.group(1))),
        (r"international_organization:([A-Za-z0-9_]+)", lambda m: zh_kv.get(m.group(1), m.group(1))),
        (r"c:([A-Z]{2,4})\b", lambda m: zh_kv.get(m.group(1), m.group(1))),
        (r"\bhas_variable\s+([A-Za-z0-9_]+)", lambda m: f"已满足专属事件条件（{zh_kv.get(m.group(1), '剧情前置已激活')}）"),
        (r"\bowns_or_non_sovereign_subject_owns\b", "本国或非主权属国拥有"),
        (r"\bcountrytax_base\b", "国家税基"),
        (r"\bgreat_power_score\b", "列强积分"),
        (r"\bmilitary_strength\b", "军事实力"),
        (r"\bscaled_gold\b", "按经济基础缩放金币"),
        (r"\byue_language\b", "粤语"),
        (r"\bmin_language\b", "闽语"),
        (r"\bwu_language\b", "吴语"),
        (r"\bxiang_language\b", "湘语"),
        (r"\bkejia_language\b", "客家话"),
        (r"\bhuizhou_language\b", "徽语"),
        (r"\bping_language\b", "平话"),
        (r"\bswiss_confederation\b", "瑞士邦联"),
        (r"\bmiddle_kingdom\b", "中国天朝"),
        (r"\bcolonial_federation\b", "殖民联邦"),
        (r"\bprotestant_union\b", "新教联盟"),
        (r"\btreaty_of_tordesillas\b", "托尔德西里亚斯条约"),
        (r"\btreaty_location\b", "条约签署地"),
        (r"\bturkmen_culture\b", "土库曼文化"),
        (r"\bsatsana_phi\b", "萨察纳皮信仰"),
        (r"\bslaves_goods\b", "奴隶商品"),
        (r"\ballows_noble_marriage\b", "允许贵族通婚"),
        (r"\buse_regnal_number\b", "启用君主世系序数"),
        (r"\bgenerate_consorts\b", "自动生成配偶"),
        (r"\bgaituguiliu_policy\b", "改土归流政策"),
        (r"\blegal_code_law\b", "法典法律"),
        (r"\bheir_religion_law\b", "继承人宗教法"),
        (r"\bcabinet_action\b", "内阁行动"),
        (r"\bsenior_partner\b", "联统主导国"),
        (r"\bpre_selected_senior_partner\b", "预设主导国"),
        (r"\bfree_city\b", "帝国自由市"),
        (r"\baverage_free_city_antagonism\b", "自由市平均敌意"),
        (r"\bopinion_sabotage_reputation\b", "败坏声誉好感修正"),
        (r"\bitinerant_court_seat\b", "巡行宫廷驻地"),
        (r"\bupper_bergregal\b", "上矿山特权"),
        (r"\blower_bergregal\b", "下矿山特权"),
        (r"\btown_rights\b", "城镇特权"),
        (r"\bprefection_modifier\b", "地方行政区修正"),
        (r"\btarget_1\b", "目标一"),
        (r"\bsuez（", "苏伊士地峡（"),
        (r"\bpanama（", "巴拿马地峡（"),
        (r"\bkiel（", "基尔地峡（"),
        (r"\bvalue\s+recipient\.", "目标国"),
        (r"\bvalue\s+actor\.", "发起国"),
        (r"\brecipient\.", "目标国"),
        (r"\bactor\.", "发起国"),
        (r"\bmultiply\s+", "× "),
        (r"\bbase\s+([0-9.\-]+)", r"基础值 \1"),
    ]
    for pat, rep in replacements:
        s = re.sub(pat, rep, s)

    # Replace remaining snake_case tokens if they exist in zh_kv (and contain CJK); if unknown and followed by 是/否, drop both cleanly
    def _has_cjk(val):
        return bool(val and re.search(r"[\u4e00-\u9fff]", val) and "[" not in val and "$" not in val)

    def _tok_bool_sub(m):
        tok, yn = m.group(1), m.group(2)
        for cand in (tok, tok.replace("_advance", "").replace("_modifier", "").replace("_trigger", "").replace("_variable", "")):
            if _has_cjk(zh_kv.get(cand)):
                return f"「{zh_kv[cand]}」 {yn}"
        return ""

    s = re.sub(r"\b([a-z][a-z0-9]*(?:_[a-z0-9]+)+)\s+([是否])\b", _tok_bool_sub, s)

    def _tok_sub(m):
        tok = m.group(0)
        if _has_cjk(zh_kv.get(tok)):
            return f"「{zh_kv[tok]}」"
        clean = tok.replace("_advance", "").replace("_modifier", "").replace("_trigger", "").replace("_variable", "")
        if _has_cjk(zh_kv.get(clean)):
            return f"「{zh_kv[clean]}」"
        return ""

    # Clean leftover internal trigger/script identifiers & empty negation wrappers
    s = re.sub(r"\b[a-z][a-z0-9]*(?:_[a-z0-9]+)+\b", _tok_sub, s)
    for _ in range(3):
        s = re.sub(r"(?:不满足|非|均非|满足其一|同时满足)?（\s*[是否、；，\s]*\s*）", "", s)
        s = re.sub(r"(?:^|[（、；，])\s*[是否]\s*(?=[、；，）]|$)", lambda m: m.group(0)[0] if m.group(0)[0] in "（、；，" else "", s)
        s = re.sub(r"（\s*[、；，]+", "（", s)
        s = re.sub(r"[、；，]+\s*）", "）", s)
        s = re.sub(r"[、]{2,}", "、", s)
        s = re.sub(r"[；;]\s*[；;]+", "；", s)
    s = re.sub(r"\s+", " ", s).strip(" ；;。，,、")
    return s


def _resolve_material_text(val, game_ctx):
    if not val or val == "—":
        return "无特殊建材"
    v = val.strip()
    if v in game_ctx["demands"]:
        return f"{game_ctx['demands'][v]}（{v}）" if v not in ("基础建造",) else game_ctx["demands"][v]
    for k, expanded in game_ctx["demands"].items():
        if k and k in v:
            return expanded
    return v


def _combine_cap_rules(pairs):
    """Merge fragmented [上限计算 · 若/下限] AST pairs into one clear Chinese rule."""
    base_cap = ""
    clauses = []
    other_pairs = []
    for k, v in pairs:
        if k == "等级上限":
            base_cap = v
        elif k.startswith("上限计算"):
            v2 = v
            v2 = re.sub(r"以下条件成立（([^）]+)）[；;]\s*增加（数值\s*([0-9.\-]+)）", r"若\1则 +\2 级", v2)
            v2 = re.sub(r"以下条件成立（市场接入度（0 至 1）\s*<\s*([0-9.]+)）[；;]\s*乘以（数值\s*市场接入度（0 至 1）、增加\s*([0-9.]+)）",
                        lambda m: f"市场接入度低于 {float(m.group(1))*100:g}% 时按（接入度 + {float(m.group(2))*100:g}%）折算", v2)
            if "下限" in k:
                clauses.append(f"保底 {v} 级")
            else:
                clauses.append(v2)
        elif k in ("建造基础价来源", "时代判定来源", "上限公式来源"):
            continue
        else:
            other_pairs.append([k, v])
    if base_cap:
        merged = base_cap + (f"（{'；'.join(clauses)}）" if clauses else "")
        other_pairs.insert(0, ["等级上限规则", merged])
    return other_pairs


def humanize_rich_table_row(cid, item, mods_by_item, game_ctx, zh_kv):
    """Clean both summary columns and detail_pairs of a rich ledger row, and build a readable summary."""
    rid = item["id"]
    item_mods = mods_by_item.get((cid, rid), [])
    clean_mods_str = format_item_modifiers(item_mods, max_items=15)

    # Clean detail_pairs
    raw_pairs = _combine_cap_rules(item.get("detail_pairs", []))
    new_pairs = []
    recipes_list = []
    cond_list = []
    mat_str = ""

    has_explicit_cond = any(k in ("国家资格", "选址条件", "启用条件", "可见条件", "执行条件") for k, _ in raw_pairs)

    for k, v in raw_pairs:
        if k.startswith("适用范围"):
            if not has_explicit_cond:
                vc = humanize_condition(v, zh_kv, game_ctx)
                if vc:
                    cond_list.append(vc)
            continue
        if k in ("国家资格", "选址条件", "启用条件", "可见条件", "执行条件"):
            vc = humanize_condition(v, zh_kv, game_ctx)
            if vc:
                cond_list.append(f"{k}：{vc}")
                new_pairs.append([k, vc])
            continue
        if k == "建造材料":
            mat_str = _resolve_material_text(v, game_ctx)
            new_pairs.append(["建造所需材料", mat_str])
            continue
        if k.startswith("生产方式"):
            pm_name = k.split("·", 1)[1].strip() if "·" in k else k
            v_clean = v.replace("每级基础产出", " → 产出")
            recipes_list.append(f"【{pm_name}】{v_clean}")
            new_pairs.append([k, v_clean])
            continue
        if k in ("修正", "全国效果", "效果") and clean_mods_str:
            new_pairs.append([k, clean_mods_str])
            continue
        if "游戏文件" in k or "核对来源" in k or "Source" in k:
            new_pairs.append(["游戏文件位置", v])
            continue
        k_label = {"diplo_chance": "外交接受倾向"}.get(k, k)
        needs_clean = k.startswith("政策 · ") or any(x in v for x in ("_", "scope:", "actor", "recipient", "has_", "base ", "multiply", "@", "Show", "COUNTRY.Get", "define:"))
        new_pairs.append([k_label, humanize_condition(v, zh_kv, game_ctx) if needs_clean else v])

    # Fix unscaled summary effects column when clean_mods_str is available
    if cid in ("estate_privileges", "government_reforms", "religions") and clean_mods_str:
        item["effects"] = clean_mods_str
    if cid == "diplomatic_actions":
        for f_col in ("cost", "acceptance", "effect"):
            if item.get(f_col):
                item[f_col] = humanize_condition(item[f_col], zh_kv, game_ctx) or item[f_col]

    item["scopeConditions"] = humanize_condition(item.get("scopeConditions", ""), zh_kv, game_ctx)
    item["detail_pairs"] = new_pairs

    # Synthesize crystal-clear natural Chinese `detail` string for directory & search
    if cid == "building_types":
        segs = [f"{item['group']}（可建于：{item['ranks']}）"]
        cost_part = f"基础造价 {item['price']} 金币" if item["price"] != "—" else "特殊事件/不可直接建造"
        if mat_str:
            cost_part += f"（建材：{mat_str}）"
        if item["time"] != "—":
            cost_part += f"，工期 {item['time']} 天"
        if item["jobs"] != "—":
            cost_part += f"，每级雇佣 {item['jobs']} 名{item['employees']}"
        segs.append(cost_part)
        if recipes_list:
            segs.append("运转配方：" + "；".join(recipes_list[:3]))
        if clean_mods_str:
            segs.append("提供效果：" + clean_mods_str)
        if cond_list:
            segs.append("限制条件：" + "；".join(cond_list[:2]))
        item["detail"] = " ｜ ".join(segs)
    elif cid == "unit_types":
        segs = [f"{item['category']} · 时代：{item['age']}（{item['unit_type']}）"]
        stats = []
        if item["troops"] != "—": stats.append(f"满编 {item['troops']} 人")
        if item["combat_power"] != "—": stats.append(f"陆战战力 {item['combat_power']}")
        if item["cannons"] != "—": stats.append(f"舰炮 {item['cannons']} 门")
        if item["hull"] != "—": stats.append(f"船体 {item['hull']}")
        if item["build_time"] != "—": stats.append(f"组建工期 {item['build_time']} 天")
        if stats:
            segs.append("、".join(stats))
        for k, v in new_pairs:
            if any(w in k for w in ("机动", "攻防", "特性")):
                segs.append(f"{k.split('·')[0].strip()}：{v}")
        item["detail"] = " ｜ ".join(segs[:5])
    elif cid == "estate_privileges":
        segs = [f"适用阶层：{item['estate']}阶层"]
        if item["power_mod"] != "—":
            segs.append(f"该阶层力量 {int(float(item['power_mod'])):+d}%" if item["power_mod"].lstrip("-").isdigit() else f"阶层力量修正 {item['power_mod']}%")
        if item["sat_eq"] != "—":
            segs.append(f"满意度均衡点 {float(item['sat_eq']):+g}%")
        if clean_mods_str:
            segs.append(f"全国效果：{clean_mods_str}")
        item["detail"] = " ｜ ".join(segs)
    elif cid == "laws":
        pols = [f"{k.replace('政策 · ', '【')}】{v}" for k, v in new_pairs if k.startswith("政策 · ")]
        segs = [f"法律分类：{item['category']}（适用：{item['groups']} · 共 {item['policies_count']} 项可选政策，实施期 {item['impl_times']}）"]
        if pols:
            segs.append("下属政策：" + "；".join(pols[:4]))
        item["detail"] = " ｜ ".join(segs)
    elif cid == "government_reforms":
        segs = [f"解锁时代：{item['age']} ｜ 政体要求：{item['government']}"]
        if item["societal_req"] != "—":
            segs.append(f"价值观要求：{item['societal_req']}")
        if item["impl_years"] != "—":
            segs.append(f"实施周期：{item['impl_years']} 年")
        segs.append(f"改革效果：{clean_mods_str or item['effects']}")
        item["detail"] = " ｜ ".join(segs)
    elif cid == "government_types":
        segs = [
            f"政府力量：{item['gov_power']} ｜ 默认统治阶层：{item['default_estate']} ｜ 继承人槽位：{item['heir_count']}",
            f"允许贵族通婚：{item['noble_marriage']} · 自动生成配偶：{item['gen_consorts']}",
        ]
        if clean_mods_str:
            segs.append(f"政体基础修正：{clean_mods_str}")
        item["detail"] = " ｜ ".join(segs)
    elif cid == "road_types":
        segs = [
            f"第 {item['level']} 级道路 ｜ 每单位距离造价 {item['cost']} 金币、工期 {item['time']} 天",
            f"行军移动耗时 {item['move_cost']}%、市场距离损耗 {item['market_cost']}%" + (f"、邻近度损耗每格额外减免 {item['prox_red']} 点" if item["prox_red"] != "—" else ""),
        ]
        item["detail"] = " ｜ ".join(segs)
    elif cid == "industry_types":
        item["detail"] = f"涵盖商品：{item['goods']} ｜ 扶持后本地区产出 +{item['area_out']}%、全国人口需求 +{item['pop_demand']}% ｜ 基础授予消耗：{item['grant_cost']} 政治影响力"
    elif cid == "diplomatic_actions":
        item["detail"] = f"行动类型：{item['kind']} ｜ 消耗：{item['cost']} ｜ 接受规则：{item['acceptance']} ｜ 效果：{item['effect']}"
    elif cid == "international_organizations":
        item["detail"] = f"组织形式：{item['group']}（领袖：{item['leadership']}）｜ 成员资格：{item['membership']} ｜ 军事规则：{item['war']} ｜ 核心效果：{clean_mods_str or item['effects']}"
    elif cid == "religions":
        segs = [f"宗教组：{item['group']}"]
        if item["liturgical"] != "—":
            segs.append(f"固定礼仪语言：{item['liturgical']}")
        if item["aspect_slots"] != "—":
            segs.append(f"信条槽位：{item['aspect_slots']} 个")
        if item["mechanics"] != "—":
            segs.append(f"核心机制：{item['mechanics']}")
        if clean_mods_str or item["effects"] != "—":
            segs.append(f"宗教修正：{clean_mods_str or item['effects']}")
        item["detail"] = " ｜ ".join(segs)
    elif cid == "wargoals":
        segs = [f"目标判定：{item['goal_type']}"]
        if item["ticking"] != "—": segs.append(f"持续跳分参数：{item['ticking']}")
        if item["conquest_fac"] != "—": segs.append(f"割地战分花费 ×{item['conquest_fac']}")
        if item["subjugation_fac"] != "—": segs.append(f"附庸战分花费 ×{item['subjugation_fac']}")
        if item["antagonism_fac"] != "—": segs.append(f"产生敌意倍率 ×{item['antagonism_fac']}")
        item["detail"] = " ｜ ".join(segs)
    return item


def humanize_catalog_record(cid, r, rich_lookup, mods_by_item, game_ctx, zh_kv):
    """Transform any of the 72 catalog records into clean, natural, idiomatic Chinese."""
    rid = r["id"]
    out = dict(r)
    cond_clean = humanize_condition(r.get("scopeConditions", ""), zh_kv, game_ctx)
    out["scopeConditions"] = cond_clean

    # 1. If this catalog has a rich structured version, reuse its crystal-clear summary & pairs!
    if cid in rich_lookup and rid in rich_lookup[cid]:
        rich = rich_lookup[cid][rid]
        out["detail"] = rich["detail"]
        out["detail_pairs"] = rich.get("detail_pairs", [])
        out["scopeConditions"] = rich.get("scopeConditions", cond_clean)
        return out

    # Lookup exact scaled modifiers for this item
    mod_group = "policy" if cid == "law-options" else cid
    item_mods = mods_by_item.get((mod_group, rid), [])
    mods_str = format_item_modifiers(item_mods, max_items=15)
    raw = (r.get("detail") or "").strip()

    # 2. Dedicated humanizers per catalog family
    if cid == "recipes":
        m_b = re.search(r"建筑\s+([^。]+)", raw)
        m_in = re.search(r"投入\s+([^。]+)", raw)
        m_out = re.search(r"产出\s+([^。]+)", raw)
        segs = []
        if m_b: segs.append(f"适用建筑：{m_b.group(1).strip()}")
        if m_in: segs.append(f"每级投入原料：{m_in.group(1).strip()}")
        if m_out: segs.append(f"每级产出商品：{m_out.group(1).strip()}")
        else: segs.append("职能：日常运转维护配方（无直接商品产出）")
        out["detail"] = " ｜ ".join(segs)

    elif cid == "colonial_charter_goals":
        goal_desc = {
            "keep_as_territory": "省份完成殖民定居后，直接归入宗主国直辖版图（默认适用于陆路相连的非海外殖民省）。",
            "form_colonial_nation": "海外省份完成殖民定居且邻近尚无本国殖民领时，自动在当地建立新的「殖民领」附属国并择优定都。",
            "expand_subject": "海外省份完成殖民定居后，直接划归同区域或相邻地区现有的本国「殖民领」附属国管辖。",
        }
        out["detail"] = goal_desc.get(rid, humanize_condition(raw, zh_kv, game_ctx))

    elif cid == "languages":
        cults = game_ctx["lang_cultures"].get(rid, [])
        rels = game_ctx["lang_religions"].get(rid, [])
        m_fam = re.search(r"语系\s+([^。]+)", raw)
        segs = []
        if m_fam:
            segs.append(f"所属语系：{m_fam.group(1).strip()}")
        if cults:
            sample_c = "、".join(cults[:6]) + (f" 等 {len(cults)} 支文化" if len(cults) > 6 else "")
            segs.append(f"使用该语言的文化：{sample_c}")
        if rels:
            segs.append(f"作为固定礼仪语言的宗教：{'、'.join(rels[:5])}")
        if not segs:
            segs.append("地区历史语言（可用于宫廷、市场与文化同化亲缘判定）")
        out["detail"] = " ｜ ".join(segs)

    elif cid == "cultures":
        cinfo = game_ctx["culture_info"].get(rid, {})
        segs = []
        if cinfo.get("groups"):
            segs.append(f"所属文化组：{'、'.join(cinfo['groups'])}")
        if cinfo.get("lang"):
            segs.append(f"母语：{cinfo['lang']}")
        elif raw:
            segs.append(raw.replace("语言 ", "母语："))
        out["detail"] = " ｜ ".join(segs) if segs else "地方文化条目"

    elif cid == "gods":
        ginfo = game_ctx["god_info"].get(rid, {})
        segs = []
        rels = ginfo.get("religions") or ginfo.get("groups") or []
        if rels:
            segs.append(f"崇拜信仰：{'、'.join(rels[:5])}")
        else:
            m_rel = re.search(r"宗教\s+([^。]+)", raw)
            if m_rel: segs.append(f"崇拜信仰：{m_rel.group(1)}")
        if ginfo.get("ability"):
            ab_zh = {"ADM": "行政 (ADM)", "DIP": "外交 (DIP)", "MIL": "军事 (MIL)"}.get(ginfo["ability"], ginfo["ability"])
            segs.append(f"神职偏重：{ab_zh}")
        if mods_str:
            segs.append(f"神祇与神谕修正：{mods_str}")
        elif not segs:
            segs.append("一神教通用至高神祇条目")
        out["detail"] = " ｜ ".join(segs)

    elif cid == "religious_focuses":
        segs = ["信仰专属改革重心（通过积累月度改革进度解锁）"]
        if mods_str:
            segs.append(f"改革效果：{mods_str}")
        if cond_clean:
            segs.append(f"前置要求：{cond_clean}")
        out["detail"] = " ｜ ".join(segs)

    elif cid == "law-options":
        m_law = re.search(r"所属法律\s+([^。]+)", raw)
        m_yr = re.search(r"年数\s+([0-9.]+)", raw)
        m_est = re.search(r"支持阶层（([^）]+)）", raw)
        segs = []
        if m_law: segs.append(f"所属法律：【{m_law.group(1)}】")
        if m_yr: segs.append(f"实施爬坡期：{m_yr.group(1)} 年")
        if mods_str: segs.append(f"政策效果：{mods_str}")
        if m_est: segs.append(f"拥护阶层：{m_est.group(1)}")
        out["detail"] = " ｜ ".join(segs) if segs else (mods_str or humanize_condition(raw, zh_kv, game_ctx))

    elif cid == "advances":
        m_age = re.search(r"时代\s+([^。]+)", raw)
        unlocks = re.findall(r"(解锁[^\s。]+\s+[^。]+)", raw)
        unlocks += [f"解锁兵种：{u}" for u in re.findall(r"unlock_unit\s+([^。]+)", raw)]
        unlocks += [f"解锁建筑：{u}" for u in re.findall(r"unlock_building\s+([^。]+)", raw)]
        unlocks += [f"解锁征召兵：{u}" for u in re.findall(r"unlock_levy\s+([^。]+)", raw)]
        segs = []
        if m_age: segs.append(f"所属时代：{m_age.group(1)}")
        if unlocks: segs.append("解锁内容：" + "、".join(unlocks[:4]))
        if mods_str: segs.append(f"研发加成：{mods_str}")
        if cond_clean: segs.append(f"研发前提：{cond_clean}")
        out["detail"] = " ｜ ".join(segs) if segs else humanize_condition(raw, zh_kv, game_ctx)

    elif cid == "heir_selections":
        rules = []
        if "through_female 是" in raw: rules.append("允许经母系血统追溯")
        if "allow_female 是" in raw: rules.append("允许女性继承王位")
        elif "allow_female 否" in raw: rules.append("仅限男性继位")
        if "allow_children 是" in raw: rules.append("允许未成年幼主继位")
        if "include_ruler_siblings 是" in raw: rules.append("纳入君主兄弟姐妹顺位")
        if "depth_first 是" in raw: rules.append("按长系子嗣深度优先递补")
        segs = []
        if rules: segs.append("继承顺位规则：" + "、".join(rules))
        if mods_str: segs.append(f"制度修正：{mods_str}")
        if cond_clean: segs.append(f"可用条件：{cond_clean}")
        out["detail"] = " ｜ ".join(segs) if segs else "特殊政体/宗教专属继承制度"

    elif cid == "age":
        m_yr = re.search(r"起始年份\s+([0-9]+)", raw)
        m_ps = re.search(r"物价稳定性\s+([0-9.]+)", raw)
        m_ef = re.search(r"效率\s+([0-9.]+)", raw)
        m_br = re.search(r"burgher_max_trade_range\s+([0-9.]+)", raw)
        m_bm = re.search(r"bureaucracy_maintenance_multiplier\s+([0-9.]+)", raw)
        segs = []
        if m_yr: segs.append(f"开启年份：{m_yr.group(1)} 年")
        if m_ef: segs.append(f"时代行政效率基准：{m_ef.group(1)}")
        if m_ps: segs.append(f"基础物价稳定性：{float(m_ps.group(1))*100:g}%")
        if m_br: segs.append(f"市民最大贸易范围：{m_br.group(1)}")
        if m_bm: segs.append(f"官僚维护费乘数：×{m_bm.group(1)}")
        if mods_str: segs.append(f"全局修正：{mods_str}")
        out["detail"] = " ｜ ".join(segs)

    elif cid == "institution":
        m_age = re.search(r"时代\s+([^。]+)", raw)
        channels = []
        if "coast_border" in raw or "neighbor" in raw: channels.append("邻近接壤或近海港口自然辐射")
        if "import" in raw: channels.append("从已传播市场进口商品输入")
        if "export" in raw: channels.append("向已传播市场出口贸易回流")
        segs = [f"诞生时代：{m_age.group(1)}" if m_age else "历史核心思潮"]
        if channels: segs.append("主要传播途径：" + "、".join(channels))
        if cond_clean: segs.append(f"发源/传播条件：{cond_clean}")
        out["detail"] = " ｜ ".join(segs)

    elif cid == "expedition_types":
        mode = "海上远航探险" if "海洋" in raw else "内陆远征探险"
        m_spd = re.search(r"travel_speed\s+([0-9.]+)", raw)
        uniq = "单局唯一史诗远征" if "unique 是" in raw else "常规可重复探险"
        segs = [f"{mode}（{uniq}）"]
        if m_spd: segs.append(f"行进速度倍率：×{m_spd.group(1)}")
        if "closest_non_rural_port" in raw: segs.append("出发点：最近非乡村沿海港口")
        if cond_clean: segs.append(f"发起条件：{cond_clean}")
        out["detail"] = " ｜ ".join(segs)

    elif cid == "artist_work":
        m_val = re.search(r"基础估值\s+([0-9.]+)", raw)
        m_inc = re.search(r"每年增值\s+([0-9.]+)", raw)
        m_tr = re.search(r"woa_tradition_multiplier\s+([0-9.]+)", raw)
        m_inf = re.search(r"woa_influence_multiplier\s+([0-9.]+)", raw)
        cap = "城破可被敌军掠夺" if "captured 是" in raw else "绑定原地不可搬迁"
        segs = []
        if m_val: segs.append(f"基础估值 {m_val.group(1)} 金币" + (f"（每年增值 +{m_inc.group(1)}）" if m_inc else ""))
        if m_tr or m_inf:
            segs.append(f"文化传统倍率 ×{m_tr.group(1) if m_tr else '1.0'}、文化影响力倍率 ×{m_inf.group(1) if m_inf else '1.0'}")
        segs.append(cap)
        if cond_clean: segs.append(f"创作要求：{cond_clean}")
        out["detail"] = " ｜ ".join(segs)

    elif cid in ("diseases", "climates", "topography", "vegetation", "location_ranks"):
        segs = []
        if cid == "diseases":
            m_int = re.search(r"calc_interval_days\s+([0-9]+)", raw)
            m_dec = re.search(r"每月抗性衰减\s+([0-9.]+)", raw)
            if m_int: segs.append(f"结算周期：每 {m_int.group(1)} 天判定一次")
            if m_dec: segs.append(f"疫后群体抗性月衰减：{float(m_dec.group(1))*100:g}%")
        elif cid == "climates":
            m_win = re.search(r"冬季\s+([^\s。]+)", raw)
            m_col = re.search(r"每月殖民迁移\s+([0-9.\-%]+)", raw)
            if m_win: segs.append(f"常规冬季强度：{m_win.group(1)}")
            if m_col: segs.append(f"殖民迁入修正：{m_col.group(1)}")
        elif cid == "topography":
            m_mv = re.search(r"移动成本参数\s+([0-9.%]+)", raw)
            m_df = re.search(r"防守方加值\s+([0-9.\-]+)", raw)
            m_vd = re.search(r"vegetation_density\s+([0-9.]+)", raw)
            if m_mv: segs.append(f"部队行军移动成本：{m_mv.group(1)}")
            if m_df: segs.append(f"防守方地形骰点：+{m_df.group(1)}")
            if "blocked_in_winter 是" in raw: segs.append("严冬封山阻断通行")
            if m_vd: segs.append(f"植被密度基准：{m_vd.group(1)}")
        elif cid == "vegetation":
            m_mv = re.search(r"移动成本参数\s+([0-9.%]+)", raw)
            m_pr = re.search(r"邻近度\s+([0-9.\-]+)", raw)
            if m_mv: segs.append(f"部队移动成本：{m_mv.group(1)}")
            if m_pr: segs.append(f"邻近度额外修正：{m_pr.group(1)}")
        elif cid == "location_ranks":
            m_lv = re.search(r"层级\s+([0-9]+)", raw)
            m_tm = re.search(r"工期参数\s+([0-9]+)", raw)
            m_up = re.search(r"upgrade_from\s+([^\s。]+)", raw)
            m_ins = re.search(r"institution_spawn_chance_factor\s+([0-9.]+)", raw)
            if m_lv: segs.append(f"聚落等级：第 {m_lv.group(1)} 级" + (f"（由「{m_up.group(1)}」升格，工期 {m_tm.group(1)} 天）" if m_up and m_tm else ""))
            if m_ins: segs.append(f"思潮发源权重：×{m_ins.group(1)}")
        if mods_str:
            segs.append(f"环境/地点修正：{mods_str}")
        if cond_clean:
            segs.append(f"升级/触发条件：{cond_clean}")
        out["detail"] = " ｜ ".join(segs) if segs else humanize_condition(raw, zh_kv, game_ctx)

    elif cid in ("religious_order_types", "religious_order_callings"):
        segs = []
        if cid == "religious_order_types":
            lev = "可动员军事征召兵" if "can_field_levies 是" in raw else "非军事修会（不出征召兵）"
            m_dc = re.search(r"default_calling\s+([^\s。]+)", raw)
            m_fc = re.search(r"founding_cost_gold\s+([0-9.]+)", raw)
            segs.append(lev)
            if m_dc: segs.append(f"默认圣召：{m_dc.group(1)}")
            if m_fc: segs.append(f"创立基础花费：{m_fc.group(1)} 金币")
        else:
            m_adm = re.search(r"leader_adm\s+([0-9.\-]+)", raw)
            m_dip = re.search(r"leader_dip\s+([0-9.\-]+)", raw)
            m_mil = re.search(r"leader_mil\s+([0-9.\-]+)", raw)
            if m_adm or m_dip or m_mil:
                segs.append(f"修会领袖能力加成：ADM {m_adm.group(1) if m_adm else 0} / DIP {m_dip.group(1) if m_dip else 0} / MIL {m_mil.group(1) if m_mil else 0}")
            if mods_str:
                segs.append(f"据点与国家赐福：{mods_str}")
        out["detail"] = " ｜ ".join(segs)

    elif cid in ("traits", "religious_aspects", "religious_schools", "parliament_types", "bureaucracies", "town_rights"):
        segs = []
        m_cat = re.search(r"^(?:类别|类型|宗教)\s+([^\s。]+)", raw)
        if m_cat:
            segs.append(f"归属类别：{m_cat.group(1)}")
        if mods_str:
            segs.append(f"提供修正：{mods_str}")
        else:
            cleaned = humanize_condition(raw, zh_kv, game_ctx)
            if cleaned:
                segs.append(cleaned)
        if cond_clean:
            segs.append(f"获取条件：{cond_clean}")
        out["detail"] = " ｜ ".join(segs)

    elif cid in ("situations", "disasters", "decisions", "missions", "peace_treaties", "casus_belli", "holy_sites", "chivalric_orders", "unit_abilities", "country_interactions", "resolutions", "parliament_agendas", "parliament_issues", "rebel_demands", "achievements", "movements"):
        # Clean noisy engine properties first
        s = raw
        s = re.sub(r"content_priority\s+[0-9.\-]+。?\s*", "", s)
        s = re.sub(r"is_content_highlighted\s+[是否]。?\s*", "", s)
        s = re.sub(r"hide_repeatable_tag\s+[是否]。?\s*", "", s)
        s = re.sub(r"show_target_in_tooltip\s+[是否]。?\s*", "", s)
        s = re.sub(r"show_start_message\s+[是否]。?\s*", "", s)
        s = re.sub(r"toggle\s+[是否]。?\s*", "", s)
        s = re.sub(r"map\s+[是否]。?\s*", "", s)
        s = re.sub(r"confirm\s+[是否]。?\s*", "", s)
        s = re.sub(r"army_only\s+是。?\s*", "仅限陆军部队使用。", s)
        s = re.sub(r"navy_only\s+是。?\s*", "仅限海军舰队使用。", s)
        s = re.sub(r"图像\s+[^\s。]+。?\s*", "", s)
        s = re.sub(r"monthly_spawn_chance\s+([0-9.]+)", r"每月触发检定权重 \1", s)
        s = re.sub(r"base_antagonism\s+([0-9.]+)", r"基础敌意系数 \1", s)
        s = re.sub(r"antagonism_type\s+", "敌意事由：", s)
        s = re.sub(r"importance\s+([0-9.]+)", r"重要度 \1", s)
        s = re.sub(r"chance\s+([0-9.]+)", r"出现权重 \1", s)
        s = re.sub(r"months\s+([0-9]+)", r"表决持续 \1 个月", s)
        s = re.sub(r"repeatable\s+是", "可重复接取", s)
        s = re.sub(r"repeatable\s+否", "不可重复", s)
        s = re.sub(r"player_playstyle\s+diplomatic", "推荐方向：外交与贸易", s)
        s = re.sub(r"player_playstyle\s+administrative", "推荐方向：内政与建设", s)
        s = re.sub(r"player_playstyle\s+military", "推荐方向：军事与扩张", s)
        s = re.sub(r"player_playstyle\s+", "推荐方向：", s)
        s = re.sub(r"no_cb\s+是", "无宣战理由强宣（高稳定与敌意惩罚）", s)
        s = humanize_condition(s, zh_kv, game_ctx)
        segs = [x for x in [s, f"修正效果：{mods_str}" if mods_str else ""] if x]
        out["detail"] = " ｜ ".join(segs) if segs else (cond_clean or "详见触发条件")

    else:
        out["detail"] = humanize_condition(raw, zh_kv, game_ctx) or raw

    return out



from flagship_metrics_defs import FLAGSHIP_METRICS

SOURCE_GROUP_ROUTE = {
    "building_types": ("ledgers.html#building_types", "id"),
    "goods": ("ledgers.html#goods", "id"),
    "unit_types": ("units.html", "unit"),
    "estate_privileges": ("ledgers.html#estate_privileges", "id"),
    "government_reforms": ("ledgers.html#government_reforms", "id"),
    "laws": ("ledgers.html#laws", "id"),
    "policy": ("directory.html#law-options", "id"),
    "bureaucracies": ("ledgers.html#bureaucracies", "id"),
    "cabinet_actions": ("ledgers.html#cabinet_actions", "id"),
    "town_rights": ("ledgers.html#town_rights", "id"),
    "advances": ("directory.html#advances", "id"),
    "societal_values": ("ledgers.html#societal_values", "id"),
    "religions": ("ledgers.html#religions", "id"),
    "religious_aspects": ("directory.html#religious_aspects", "id"),
    "religious_schools": ("directory.html#religious_schools", "id"),
    "religious_focuses": ("directory.html#religious_focuses", "id"),
    "religious_order_callings": ("directory.html#religious_order_callings", "id"),
    "gods": ("directory.html#gods", "id"),
    "parliament_issues": ("directory.html#parliament_issues", "id"),
    "parliament_types": ("directory.html#parliament_types", "id"),
    "traits": ("directory.html#traits", "id"),
    "road_types": ("ledgers.html#road_types", "id"),
    "industry_types": ("ledgers.html#industry_types", "id"),
    "location_ranks": ("directory.html#location_ranks", "id"),
    "topography": ("directory.html#topography", "id"),
    "climates": ("directory.html#climates", "id"),
    "vegetation": ("directory.html#vegetation", "id"),
    "age": ("directory.html#age", "id"),
    "government_types": ("ledgers.html#government_types", "id"),
    "subject_types": ("ledgers.html#subject_types", "id"),
    "international_organizations": ("ledgers.html#international_organizations", "id"),
    "diseases": ("directory.html#diseases", "id"),
    "artist_work": ("directory.html#artist_work", "id"),
    "estate_actions": ("ledgers.html#estate_actions", "id"),
    "character_interactions": ("ledgers.html#character_interactions", "id"),
    "diplomatic_actions": ("ledgers.html#diplomatic_actions", "id"),
    "casus_belli": ("ledgers.html#casus_belli", "id"),
    "wargoals": ("ledgers.html#wargoals", "id"),
}


def resolve_source_href(group_key, item_id):
    if not item_id or group_key not in SOURCE_GROUP_ROUTE:
        return ""
    base, mode = SOURCE_GROUP_ROUTE[group_key]
    if mode == "unit":
        return f"units.html#{item_id}"
    return f"{base}?id={item_id}"


def clean_source_zh(zh_str):
    s = re.sub(r"\s*AUTO_MODIFIER_NAME_[A-Za-z0-9_]+:.*$", "", str(zh_str or "")).strip()
    return s.replace("\xa0", " ")


def build_metrics_bundle(ms, zh_kv, game_ctx):
    """Build docs/assets/metrics-data.js for metrics.html (66 separated single-concept metrics + searchable 1,364 modifiers)."""
    CAT_ZH = {
        "country": "国家全局修正",
        "location": "地点修正",
        "province": "省份修正",
        "unit": "陆海军单位修正",
        "character": "人物角色修正",
        "religion": "宗教修正",
        "internationalorganization": "国际组织修正",
        "internationalorganizatiuon": "国际组织修正",
        "mercenary": "雇佣兵修正",
        "rebel": "叛军修正",
        "dynasty": "王朝修正",
        "all": "通用修正",
    }

    modifiers_list = []
    mod_lookup = {}
    for mk, minfo in ms.items():
        raw_sources = minfo.get("sources", [])
        if not raw_sources:
            continue
        grouped = collections.defaultdict(list)
        seen_per_group = collections.defaultdict(set)
        for s in raw_sources:
            g_zh = GROUP_LABELS_ZH.get(s["group"], s["group"])
            disp = "启用" if s["display"] == "是" else ("禁用" if s["display"] == "否" else s["display"])
            cond = humanize_condition(s.get("condition", ""), zh_kv, game_ctx)
            for boring in ("持有这项阶层特权时", "采用这项政府改革时", "研发这项革新后", "建筑在当地运作，按建筑等级和商品供应缩放"):
                if cond == boring:
                    cond = ""
            cond_s = cond[:90]
            szh = clean_source_zh(s["zh"])
            sig = (szh, disp, cond_s)
            if sig in seen_per_group[g_zh]:
                continue
            seen_per_group[g_zh].add(sig)
            src_entry = {
                "zh": szh,
                "val": disp,
                "scope": s.get("scope", ""),
                "cond": cond_s,
            }
            href = resolve_source_href(s["group"], s.get("id", ""))
            if href:
                src_entry["href"] = href
            grouped[g_zh].append(src_entry)
        item = {
            "id": mk,
            "zh": minfo.get("zh", mk),
            "en": minfo.get("en", mk),
            "cat": CAT_ZH.get(minfo.get("category", "all"), "其他修正"),
            "total": len(raw_sources),
            "groups": [[gname, items[:28], len(items)] for gname, items in grouped.items()],
        }
        modifiers_list.append(item)
        mod_lookup[mk] = item

    modifiers_list.sort(key=lambda x: (-x["total"], x["zh"]))

    # Attach exact per-modifier sub_modifiers onto each separated flagship metric (NO cross-modifier merging!)
    enriched_flagships = []
    for fm in FLAGSHIP_METRICS:
        if not fm.get("base_value"):
            raise ValueError(f"Flagship metric {fm['id']} missing mandatory base_value!")
        fm_copy = dict(fm)
        sub_mods = []
        total_src = 0
        for mk in fm["mod_keys"]:
            m_obj = mod_lookup.get(mk)
            if not m_obj:
                raise KeyError(f"Unknown or empty mod_key {mk!r} in flagship {fm['id']!r}")
            total_src += m_obj["total"]
            sub_mods.append({
                "id": m_obj["id"],
                "zh": m_obj["zh"],
                "en": m_obj["en"],
                "cat": m_obj["cat"],
                "total": m_obj["total"],
                "groups": m_obj["groups"],
            })
        fm_copy["total_sources"] = total_src
        fm_copy["sub_modifiers"] = sub_mods
        enriched_flagships.append(fm_copy)

    bundle = {
        "flagships": enriched_flagships,
        "modifiers": modifiers_list,
    }
    with open(os.path.join(ASSETS_DIR, "metrics-data.js"), "w", encoding="utf-8") as f:
        f.write("window.__EU5_METRICS__ = " + json.dumps(bundle, ensure_ascii=False) + ";\n")
    with open(os.path.join(DATA_DIR, "metrics_summary.json"), "w", encoding="utf-8") as f:
        json.dump(
            {
                "flagships": [
                    {
                        "id": fm["id"],
                        "zh": fm["zh"],
                        "en": fm["en"],
                        "pillar": fm["pillar"],
                        "base_value": fm["base_value"],
                        "chapter_href": fm["chapter_href"],
                        "total_sources": fm["total_sources"],
                    }
                    for fm in enriched_flagships
                ],
                "modifiers": [
                    {"id": m["id"], "zh": m["zh"], "en": m["en"], "cat": m["cat"], "total": m["total"]}
                    for m in modifiers_list[:500]
                ],
            },
            f,
            ensure_ascii=False,
        )
    print(f"Exported metrics-data.js: {len(enriched_flagships)} separated flagship metrics, {len(modifiers_list)} modifiers with sources.")
