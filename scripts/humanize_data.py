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


# 30 Individual Flagship Core Metrics curated for metrics.html + embedded chapter breakdowns
FLAGSHIP_METRICS = [
    # --- Pillar 1: Territory (疆域与控制) ---
    {
        "id": "proximity",
        "pillar": "territory",
        "zh": "行政邻近度",
        "en": "Proximity to Capital",
        "mod_keys": ["local_proximity_source", "road_proximity", "terrain_proximity", "mountains_proximity_impact", "hills_proximity_impact", "sea_cost_on_distance_from_capital_when_maritime"],
        "formula_role": "从首都（100 点）、历史首都（80 点）或地方/海军总督驻地（80 点）出发，沿耗散最低的水陆路径向各地点递减，再以 ×0.75 的权重进入本地「最大控制力」公式。",
        "core_drivers": [
            "基础跳格损耗：无路陆地 40、砂石路 20、铺装路 15、现代公路 10、铁路 5；顺逆流河道 12；封冻水面 20",
            "港口与海域传导：水陆进出港基础损耗 35（天然港湾容量达 1.0 时提供 −50% 修正，压至 17.5）；单格海域损耗随当地「海上存在」从 30（0% 存在）线性降至 5（100% 存在）",
            "邻近度效率与地形除数：单跳实际损耗 = 基础损耗 ÷ [(1 + 邻近度效率) × (1 + 地形植被修正)]（除数下限 0.25）；每 1 点发展度提供 +0.5% 本地邻近度效率，山地/丘陵/密林则放大损耗",
            "次级源头建筑：历史首都、地方总督治所、海军总督府可在远离现首都的边疆直接生成 80 点本地邻近度源头",
        ],
        "chapter_href": "ch01-territory-core.html#proximity",
    },
    {
        "id": "max_control",
        "pillar": "territory",
        "zh": "最大控制力与月度控制力",
        "en": "Max Control & Monthly Control",
        "mod_keys": ["local_max_control", "global_max_control", "global_max_rural_control", "local_monthly_control", "global_monthly_control"],
        "formula_role": "当前控制力按月向「最大控制力」靠拢（低于上限时按月度增长率爬升，高于上限时每月固定衰减 −0.50%）。当前控制力直接乘算：地点财富转化为国家税基的比例、征召兵出兵率、月度人力/水手产出，以及文化同化与宗教改信速度。",
        "core_drivers": [
            "邻近度主干：邻近度 × 0.75（如邻近度 60 提供 +45% 最大控制力）",
            "整合四态加成：已征服 −10%、殖民地 0%、已整合 +5%、核心（Core）+20%（从已整合升为核心净增 +15% 最大控制力）",
            "聚落层级与首都地位：乡村 0%、集镇 +5%、城市 +10%、大都市 +20%；现首都额外 +20%，历史首都 +10%",
            "满意度与驻军状态：当地平均满意度低于 100% 时扣减 10% × (1 − 满意度)；本国陆军驻扎提供临时控制加成，遭敌海军封锁扣 −10%",
            "建筑、特权与内阁：议会大厅/地方议会/执达署提升上限；贵族分权特权扣减乡村或全国上限；ADM 内阁「提升省份控制力」提供 +10% 上限与 +1.00%/月增速；本地贵族识字率最高提供 +1.00%/月增速",
        ],
        "chapter_href": "ch01-territory-core.html#control",
    },
    {
        "id": "integration_speed",
        "pillar": "territory",
        "zh": "省份整合速度与核心晋升",
        "en": "Integration Speed & Core Threshold",
        "mod_keys": ["global_integration_speed_modifier", "local_integration_speed_modifier", "province_integration_speed"],
        "formula_role": "新征服地点处于「已征服」态（−10% 最大控制力、高分离主义），必须派遣内阁执行「整合省份」累积满 100% 进度转为「已整合」；此后若当地本国主流或已接纳文化人口占比达 ≥50%，自动免费晋升为「核心（Core）」。",
        "core_drivers": [
            "执政大臣能力与内阁效率：负责整合的内阁大臣 ADM（行政能力）越高、全国内阁效率越高，月度基础进度越快",
            "文化与宗教亲缘：目标地点优势文化与本国主流文化同语系/同文化组、同宗教时整合更快；异教异族省份耗时显著增加",
            "聚落规模阻力：城市与大都市因人口稠密、制度复杂，整合所需总点数高于乡村聚落",
            "制度与革新修正：集权倾向、行政官僚机构、法典类法律政策与时代革新提供 +10% ~ +25% 整合速度",
        ],
        "chapter_href": "ch01-territory-core.html#integration-core",
    },
    {
        "id": "development_prosperity",
        "pillar": "territory",
        "zh": "发展度与繁荣度",
        "en": "Development & Prosperity",
        "mod_keys": ["global_monthly_development", "local_monthly_development_modifier", "local_monthly_development", "global_monthly_prosperity", "local_monthly_prosperity"],
        "formula_role": "每 1 点发展度提供：+1 受支持建筑等级、+2.5% 人口容量、+0.5% 本地邻近度效率、+0.1 RGO 最大等级、+1% 建造速度与 +0.2% 市场中心吸引力。繁荣度（−100% 至 +100%）在正值时加速发展与人口增长，负值（荒废）时按比例扣减最高 −50% 生产效率与 −100% 生命力。",
        "core_drivers": [
            "长期和平与高满意度：无战火劫掠、无围城占领且省内食物充足时，繁荣度按月向正均衡点回升，并带动发展度自然累积",
            "地形气候阻力：干旱、极寒、高山与密林大幅提高发展度增长门槛；温带平原与河谷农田增长最快",
            "主动建设手段：ADM 内阁「发展省份」、道路与市政水利建筑、工匠与市民特权、时代农业与城市革新",
            "战乱与疫病冲击：敌军劫掠、围城、饥荒与重大瘟疫会令繁荣度断崖式跌入负值，战后可用 DIP 内阁「灾后恢复」快速拉回",
        ],
        "chapter_href": "ch01-territory-core.html#urbanization",
    },

    # --- Pillar 2: Population & Food (人口与民生) ---
    {
        "id": "pop_capacity",
        "pillar": "territory",
        "zh": "人口容量与拥挤度",
        "en": "Population Capacity & Crowding",
        "mod_keys": ["local_population_capacity", "local_population_capacity_modifier"],
        "formula_role": "地点总人口容量 = 固定基础容量 × (1 + 容量百分比修正总和)。当实际人口占容量比例超过 60%（GROWTH_DAMPING_START）时，自然增长开始受阻尼衰减并推高外迁压力；达到或超过 100% 时正自然增长归零。",
        "core_drivers": [
            "地表植被固定底盘：农田 +100k、草地/森林 +50k、林地 +35k、丛林/高原 +25k、荒地 +10k、沙漠 +5k",
            "聚落层级固定与百分比双加成：集镇 (+20k 且 +10%)、城市 (+100k 且 +25%)、大都市 (+400k 且 +50%)",
            "发展度与在岗建筑：每 1 点发展度 +2.5% 容量；每 1 级满员运作建筑 +0.1% 容量",
            "水文与气候倍率：沿海 +25%，河流按规模 +10% ~ +50%；温带/热带/亚热带提供大幅正修正，极地与严寒干旱大幅扣减",
        ],
        "chapter_href": "ch02-population-food.html#population-base",
    },
    {
        "id": "pop_growth_migration",
        "pillar": "territory",
        "zh": "人口自然增长与迁徙吸引力",
        "en": "Population Growth & Migration Attraction",
        "mod_keys": ["global_population_growth", "local_migration_attraction", "non_rural_migration_attraction", "global_migration_speed_modifier"],
        "formula_role": "每月人口变动 = 自然增长（出生减死亡）+ 同一市场内部从低吸引力地点向高吸引力地点的净迁徙 + 跨海殖民迁移。",
        "core_drivers": [
            "食物储备与繁荣度：省粮仓充盈度、正繁荣度与免费土地（低拥挤度）是自然出生率的第一驱动力；省粮仓见底触发饥荒直接施加 −5%/月死亡惩罚",
            "消费品满足与医疗：人口买齐生命需求商品（谷物/鱼/盐/药材等）、医药与公共卫生革新、医院/修道院建筑显著压低死亡率",
            "迁徙吸引力差值：空缺高薪岗位、高市场接入度、高满意度、城镇聚落特权拉高迁入吸引；超额拥挤、超建建筑（每超 1 级 −0.01 吸引）、战火劫掠与宗教迫害迫使人口外逃（注意：农奴制特权可禁止农民自由迁徙）",
        ],
        "chapter_href": "ch02-population-food.html#population-base",
    },
    {
        "id": "pop_promotion",
        "pillar": "territory",
        "zh": "阶级晋升与降级速度",
        "en": "Pop Promotion & Demotion Speed",
        "mod_keys": ["global_pop_promotion_speed_modifier", "local_pop_promotion_speed_modifier", "local_pop_promotion_speed", "local_tribal_promotion"],
        "formula_role": "新建工坊、军营、集市或教堂只创造岗位空缺，不会凭空变出工人；必须由当地农民/劳工按月「晋升（Promotion）」为市民、工匠、士兵、教士或贵族后，建筑才能排满运转。",
        "core_drivers": [
            "文化准入硬门槛：只有属于本国「主流文化」或「已接纳文化」的人群才被允许晋升为上层阶级（受容忍/受歧视文化人群无法晋升填补高级岗位）",
            "本地控制力与识字率：高控制力、高平民识字率、学校/图书馆/大学建筑显著加快晋升转化率",
            "国家稳定与内阁催化：正稳定度、自由民价值观倾向、ADM 内阁「促进人口升级」及部落定居化政策大幅提速；当建筑停工裁员时，失业上层人口按月缓慢降级回流平民",
        ],
        "chapter_href": "ch02-population-food.html#population-base",
    },
    {
        "id": "food_supply",
        "pillar": "territory",
        "zh": "食物产出、消耗与省粮仓",
        "en": "Food Production, Consumption & Provincial Granary",
        "mod_keys": ["global_monthly_food_modifier", "local_monthly_food_modifier", "global_pop_food_consumption", "local_food_capacity", "food_consumption_modifier"],
        "formula_role": "食物以「省份（Province）」为单位统筹：省内所有农村食物型 RGO（谷物、牲畜、鱼、果蔬等）产出减去全城邦各阶级人口消耗，盈余存入省粮仓，赤字先吃省粮仓储备，耗尽后向所属市场高价购粮，再断粮即爆发饥荒。",
        "core_drivers": [
            "农村农业 RGO 与劳工在岗率：过度把农村升级为城市或抽空农民去城里进厂，会直接砍断本省原粮底座",
            "季节与气候波动：严冬（轻微/正常/严酷冬季）期间本地农业食物产出大幅滑坡，必须靠秋收积累的「本地食物容量（粮仓建筑）」平抑过冬",
            "上层人口高消耗系数：贵族、市民、教士与常备驻军的人均食物消耗远高于普通农民；大都市必须配套灌溉、农庄与省粮仓扩建",
        ],
        "chapter_href": "ch02-population-food.html#food-chain",
    },
    {
        "id": "disease_resistance",
        "pillar": "territory",
        "zh": "疫病抗性与瘟疫传播",
        "en": "Disease Resistance",
        "mod_keys": ["global_disease_resistance", "local_disease_resistance"],
        "formula_role": "黑死病、伤寒、天花、疟疾等疫病沿商路、港口、行军路线与高密度城市扩散；本地与全国「疫病抗性」直接减免每次结算周期的感染率与人口病死率，疫后幸存人群会获得随月份缓慢衰减的群体免疫抗性。",
        "core_drivers": [
            "医疗与市政设施：医院、药房、引水渠、检疫港建筑直接提供高额本地疫病抗性",
            "商路与港口敞口：贸易量越大、人口越拥挤的大都市越容易成为首波输入震中；疫期可通过决议/行动实施港口隔离检疫（牺牲短期贸易换取抗性）",
            "药材商品供应与革新：市场药材（Medicaments）充足及文艺复兴后医学革新提供永久抗性底座",
        ],
        "chapter_href": "ch02-population-food.html#migration-disease",
    },

    # --- Pillar 3: Economy, Market & Trade (经济与财政) ---
    {
        "id": "production_efficiency",
        "pillar": "economy",
        "zh": "加工生产效率",
        "en": "Production Efficiency",
        "mod_keys": ["local_production_efficiency", "global_production_efficiency"],
        "formula_role": "建筑月度产出 = 配方每级基础产出 × 运行规模（等级 × 满员率 × 市场接入度 × 原料可得性）× (1 + 本地生产效率 + 全国生产效率)。核心价值：生产效率只放大成品产出，不增加原料消耗量！在原料成本占大头的加工业中，+10% 生产效率往往令单级净利润提升 25%–40%。",
        "core_drivers": [
            "建筑成熟度（Establishment）：启用成熟度规则时，建筑满员运转后成熟度逐月爬升；超过 50% 后超出部分按 ×0.3 折算，满 100% 时提供最高 +15% 生产效率",
            "社会价值观：「资本经济 vs 传统经济」推向资本经济极点提供最高 +10% 全国生产效率",
            "人口与阶层素质：本地劳工平均识字率提供最高 +2.5% 本地效率；市民阶层提供最高 +2.5% 全国效率",
            "城市基建与城镇特权取舍：犹太区(+5%)、行会大厅(+1%/级)、工匠行会(+0.5%/级)；31 项城镇行业专营特权大幅拉高对应产业产出，但代价是对本地通用加工施加 −5% 生产效率",
            "制度、官僚与科技：市民特权《商人的沃土》/《王室工厂》(+1%)、法律《大行会》/《加强行会》(+2.5%)、改革《工会弹压体制》(+2.5%)、官僚《市监》(+2.5%)、内阁《精简文书工作》(+1%) 及 34 项时代革新(+1%~+5%)；负繁荣度（荒废）最高扣减 −50%",
        ],
        "chapter_href": "ch03-economy-market-trade.html#production-buildings",
    },
    {
        "id": "rgo_output",
        "pillar": "economy",
        "zh": "原材料产出与 RGO 等级上限",
        "en": "Raw Materials Output & Max RGO Size",
        "mod_keys": ["global_raw_material_output", "local_raw_material_output", "local_max_rgo_size", "global_max_rgo_size_modifier"],
        "formula_role": "地点 RGO 月度实物产量 = 在岗劳工/奴隶满员等级 × 商品基础产量 × (1 + 本地原产修正 + 全国原产修正)；实物进入市场后按「本地市场接入度 × 当前市场价格」转化为地点财富。",
        "core_drivers": [
            "在岗劳工人数与扩建上限：每级 RGO 需 1,000 名劳工或奴隶；最大可扩建等级由本地基础储量、发展度（每点 +0.1 级）与采矿/农垦建筑决定",
            "社会价值观取舍：「农奴制」极点提供 +20% 全国原料产出，「传统经济」同样强化农矿原产（与偏向城市工业的自由民/资本经济形成路线分野）",
            "专项基建与时代革新：矿井、林场、农庄、水利设施及《生产定额管理》(+10%)、《工场生产》(最大 RGO 规模 +10%) 等革新；严冬与宗教斋戒/安息日特权可能阶段性扣减 −5%",
        ],
        "chapter_href": "ch03-economy-market-trade.html#production-buildings",
    },
    {
        "id": "building_cost_cap",
        "pillar": "economy",
        "zh": "建筑建造效率与受支持建筑容量",
        "en": "Build Efficiency & Supported Building Levels",
        "mod_keys": ["global_build_buildings_efficiency", "global_urban_build_buildings_efficiency", "free_building_levels", "global_construction_speed", "local_construction_speed"],
        "formula_role": "每个地点拥有「受支持建筑等级上限」= 发展度 + 0.05 × 本地千人数 + 聚落等级基数 + 免费建筑等级修正。每超出上限 1 级，本地新建建筑效率扣减 −5%（变相涨价）且迁徙吸引力 −0.01。",
        "core_drivers": [
            "拉高本地建筑容量：提升发展度（每点 +1 级）、做大本地人口规模、将集镇升格为城市/大都市、解锁提供「建筑等级上限」的市政建筑与革新",
            "压低造价的双杠杆：一是堆叠「建筑建造效率」修正（直接降低金币与建材消耗）；二是在本市场预先扩产木材、砖块、石料、铁、工具等建材商品，压低建材市价",
            "建造队列与工期：高发展度（每点 +1% 建造速度）、本地建造速度修正与增加并行建造队列的革新可加快大基建成型",
        ],
        "chapter_href": "ch03-economy-market-trade.html#production-buildings",
    },
    {
        "id": "market_access",
        "pillar": "economy",
        "zh": "市场接入度与市场吸引力",
        "en": "Market Access & Market Center Power",
        "mod_keys": ["local_market_access", "road_market_access", "global_trade_center_power"],
        "formula_role": "从所属市场中心（100%）沿水陆交通网向成员地点衰减。市场接入度同时决定三件事：① 建筑运行规模上限与 RGO 变现率；② 边缘地点被哪个邻近市场吸走（市场吸引力 × 接入度）；③ 市场原料供不应求时的拿货先后顺序（高接入度先吃饱，低接入度直接断料停工）！",
        "core_drivers": [
            "道路与河海走廊：高等级道路（砂石路 −10% / 铺装路 −20% / 铁路大幅降低市场距离损耗）与内河航道显著延展高接入半径",
            "港口装卸与港湾适宜度（1.4.9）：进出港装卸效率基数提升至 +200%（按天然港湾适宜度缩放），水陆转换附加距离为 0.02 × (1 − 港湾适宜度)",
            "市场中心实力与新建市场：发展度、集市/商埠建筑、重商主义倾向提升本国市场吸引力；若远端富庶省接入度长期低于 55%，直接花费金币新建本土市场中心即可就地拉回 100%",
        ],
        "chapter_href": "ch03-economy-market-trade.html#market-network",
    },
    {
        "id": "trade_capacity_advantage",
        "pillar": "economy",
        "zh": "贸易容量、贸易范围与贸易优势",
        "en": "Trade Capacity, Range & Advantage",
        "mod_keys": ["global_merchant_capacity_modifier", "local_merchant_capacity", "trade_range_modifier", "global_merchant_power", "local_merchant_power", "merchant_power_from_maritime_modifier"],
        "formula_role": "跨市场贸易先比「贸易优势（Advantage）」再算「贸易容量（Capacity）」：当紧俏高利商品在出口市场供不应求时，按各国在该市场的贸易优势从高到低依次扫货；贸易容量则决定每条商路能装载多少单位货物（大宗重货与超远航线消耗更多容量）。",
        "core_drivers": [
            "贸易容量来源：市场中心、集市/商埠/海关建筑、商船队、城镇商业特权与自由贸易价值观（注意部分市民垄断特权会把国家容量转移给市民私营贸易）",
            "贸易优势来源：在该市场控制的核心港口与商馆等级、已解锁海上贸易优势修正时的周边「海上存在」、宫廷语言匹配首都市场语言、商业共和国/汉萨同盟专属机制",
            "贸易范围扩展：海军港口网络、海外贸易站、航海时代革新与外交贸易通行权决定商人能否触达亚洲香料与美洲白银源头市场",
        ],
        "chapter_href": "ch03-economy-market-trade.html#trade-orders",
    },
    {
        "id": "trade_efficiency_maint",
        "pillar": "economy",
        "zh": "海陆贸易效率与商人维护费",
        "en": "Sea/Land Trade Efficiency & Merchant Maintenance",
        "mod_keys": ["trade_sea_efficiency", "trade_land_efficiency", "trade_income", "merchant_maintenance_efficiency"],
        "formula_role": "单条商路毛利 = (进口市场售价 − 出口市场买价) × 成交量 × (1 + 海/陆贸易效率 + 进出口专项效率) − 商人维护成本 − 过境关税；最终结算的贸易净利润按「王室力量份额」划归国库，其余归入市民阶层。",
        "core_drivers": [
            "海陆路线分化：海运单次运量大且受「海上贸易效率」与护航舰队加成；内陆丝路/商队受「陆上贸易效率」与驿站建筑加成",
            "商人维护效率：直接压低维持庞大商队所需的固定日常开销，使中等价差的大宗商品路线也能扭亏为盈",
            "王室分成比例：即便全国贸易总额极高，若王室力量仅有 15%，国库也只能拿到 15% 的贸易利润——提升王室力量是放大贸易财政收入的隐藏乘区",
        ],
        "chapter_href": "ch03-economy-market-trade.html#trade-orders",
    },
    {
        "id": "tax_efficiency",
        "pillar": "economy",
        "zh": "税收效率、税基与经济基础",
        "en": "Tax Efficiency, Tax Base & Economical Base",
        "mod_keys": ["tax_income_efficiency", "global_estate_max_tax", "peasants_estate_max_tax", "burghers_estate_max_tax", "nobles_estate_max_tax"],
        "formula_role": "国库实收某阶层税金 = Σ(各地点财富 × 本地控制力 × 该阶层财富占比) × 阶层当前税率 × (1 + 税收效率)。与此同时，全国无论控制高低的全部财富、人口、属国与已接纳思潮共同构成「经济基础（Economical Base）」，作为宫廷、官僚、维稳与事件花费的放大倍率。",
        "core_drivers": [
            "税收效率（无副作用净增）：由税务官僚机构、集权财政改革、税法政策与时代革新提供，在不扣减阶层满意度的前提下直接放大入库税金",
            "阶层征税上限（Max Tax）：决定税率滑块最高能拉到多少；免税特权（如贵族免税、教士什一税豁免）会锁死对应富裕阶层的征税上限",
            "税基含金量管理：盲目吞并大片 0% 控制力的远端穷省，不会增加分子「可控税基」，却会推高分母「经济基础」，导致维稳与行政账单倒挂暴涨",
        ],
        "chapter_href": "ch03-economy-market-trade.html#wealth-to-treasury",
    },
    {
        "id": "minting_inflation_credit",
        "pillar": "economy",
        "zh": "铸币平价、通货膨胀与信誉利率",
        "en": "Minting Threshold, Inflation & Bank/Bond Interest",
        "mod_keys": ["minting_income_factor", "minting_inflation_threshold", "monthly_inflation", "bank_interest", "bond_interest"],
        "formula_role": "拉高铸币滑块可直接印钞救急，但一旦超过「铸币平价（免通胀阈值）」就会按月累积通货膨胀，全盘推高全国建筑造价、军费与商品采购价。财政赤字借债则优先向本国富余阶层池借款，不足时转向国际金融家或发行政府债券，利息由基础利率与国家信誉度决定。",
        "core_drivers": [
            "金银铜矿与皇家铸币厂：本土出产黄金、白银、铜并建造铸币厂（如塞哥维亚铸币厂 +10% 铸币收入、+2% 铸币平价）可显著抬高无通胀安全印钞上限",
            "通货膨胀消减：下调铸币滑块、启用稳健货币政策、派遣 ADM 内阁执行反通胀行动；切忌在和约中一次性索取远超经济体量的赔款引发输入性通胀",
            "压低借贷利息：保持高国家信誉度（不违约破产）、偏向「资本经济」价值观（最高 −3% 银行利率）、建立中央银行与金融改革",
        ],
        "chapter_href": "ch03-economy-market-trade.html#wealth-to-treasury",
    },

    # --- Pillar 4: State, Estates & Culture (国家、阶层与文教) ---
    {
        "id": "crown_estate_power",
        "pillar": "state",
        "zh": "王室力量与各阶层力量权重",
        "en": "Crown Power & Estate Power Share",
        "mod_keys": ["global_crown_estate_power", "local_crown_estate_power", "global_nobles_estate_power", "global_burghers_estate_power", "crown_power_from_population"],
        "formula_role": "王室力量占比 = 王室点数 ÷ (王室点数 + 贵族/教士/市民/农民等各阶层点数之和)。它直接决定：① 国家截留的贸易利润比例；② 议会开幕时的基础支持度（王室占比 × 0.5）；③ 全国内阁效率与集权改革推进能力。",
        "core_drivers": [
            "人口控制力双轨制：各地点人口按「当前控制力」向王室贡献点数，同时按各自阶级人口基数、财富留存与特权乘数向阶层贡献点数——拉高核心富庶省控制力是最治本的强干弱枝手段",
            "内阁与统帅人事权：每任命 1 名某阶层出身的大臣或将领，该阶层力量 +25%！优先任用王室宗亲（Crown）掌管要职可直接为王室加分",
            "价值观与统治者能力：「中央集权」极点提供 +50% 王室力量；君主每点 ADM 提供 +0.25% 王室力量",
            "警惕阶层私产与强权特权：每项大特权往往赋予该阶层 +20% ~ +50% 力量；低控制省份（<75%）由阶层自建的私产建筑会持续膨胀地方豪强实力",
        ],
        "chapter_href": "ch05-estates-rebels.html#power-balance",
    },
    {
        "id": "estate_satisfaction",
        "pillar": "state",
        "zh": "阶层满意度均衡点",
        "en": "Estate Satisfaction Equilibrium",
        "mod_keys": ["global_estate_target_satisfaction", "nobles_estate_target_satisfaction", "clergy_estate_target_satisfaction", "burghers_estate_target_satisfaction", "peasants_estate_target_satisfaction"],
        "formula_role": "各阶层当前满意度每月向「满意度均衡点」缓慢收敛。关键红线：满意度低于 50% 产生负面修正；低于 25% 拒绝提供该阶层征召兵并酝酿叛乱运动；低于 1% 彻底抗税停摆；而赎回（剥夺）已授予特权必须支付高额稳定度与满意度代价。",
        "core_drivers": [
            "税率与特权平衡：拉高阶层税率滑块按比例压低均衡点，授予阶层特权（每项 +5% ~ +15%）与顺应其议会议程则抬高均衡点",
            "统治者外交魅力与价值观：君主每点 DIP 提供 +0.1% 全阶层均衡点；「地方分权」倾向提供 +5% 均衡点",
            "厌战度、稳定与宗教文化：每点厌战度扣 −1% 均衡点；低正统性/低稳定度及迫害异教/异族人群会严重拉低对应阶层（如齐米或农民）的满意度",
        ],
        "chapter_href": "ch05-estates-rebels.html#power-balance",
    },
    {
        "id": "cabinet_efficiency",
        "pillar": "state",
        "zh": "内阁效率与立法效率",
        "en": "Cabinet Efficiency & Legislative Efficiency",
        "mod_keys": ["country_cabinet_efficiency", "legislative_efficiency"],
        "formula_role": "「内阁效率」直接乘算所有在任内阁大臣执行省份整合、提升控制、文化同化、宗教改信、灾后恢复等行动的月度速度与加成幅度；「立法效率」则缩短改革与法律变更漫长的实施爬坡年限。",
        "core_drivers": [
            "王室力量红利：王室力量占比越高，提供的全国内阁效率基础加成越高",
            "内阁首脑（Head of Cabinet）：提拔在阁资历满 10 年的资深重臣出任首脑，直接提供 +25% 内阁效率并令其内阁特质效果翻倍",
            "大臣个人专业能力：ADM/DIP/MIL 行动分别吃负责大臣对应维度的能力值；搭配宫廷官僚机构、大学人才库与集权行政革新可叠至极高倍率",
        ],
        "chapter_href": "ch04-government-cabinet.html#cabinet-actions",
    },
    {
        "id": "stability_legitimacy_pi",
        "pillar": "state",
        "zh": "稳定度、正统性与政治影响力",
        "en": "Stability, Government Power & Political Influence",
        "mod_keys": ["stability_cost_efficiency", "stability_investment", "monthly_legitimacy", "monthly_republican_tradition", "monthly_devotion", "monthly_political_influence"],
        "formula_role": "稳定度（−100 至 +100）决定全国叛乱压制、人口晋升与财政秩序；政府力量（正统性/共和传统/奉献度/部落凝聚力，0–100）支撑统治合法性；政治影响力则是推行改革、修法、撤换阁臣与外交干预计划的核心月度点数。",
        "core_drivers": [
            "维稳预算与维稳效率：稳定度靠财政预算中的「稳定度投资」按月拉升，但偏离 0 越远自然衰减越快；堆叠「维稳效率」能大幅节省维持高稳定所需的金币（注意经济基础越大，维稳基数越贵）",
            "政府力量维护：王室联姻、高威望、胜仗、宫廷排场预算（宫廷支出效率）及特定宗教信条持续产出正统性/共和传统/奉献度",
            "政治影响力产出：由君主三维能力与全体在任内阁大臣平均能力共同决定——切勿让内阁席位空缺（空席按 0 分拉低内阁均值！）",
        ],
        "chapter_href": "ch04-government-cabinet.html#government-power",
    },
    {
        "id": "research_literacy",
        "pillar": "culture",
        "zh": "识字率、思潮传播与研究速度",
        "en": "Literacy, Institution Spread & Research Speed",
        "mod_keys": ["research_speed_modifier", "global_max_literacy", "global_monthly_literacy", "global_institution_growth_modifier", "local_institution_growth_modifier"],
        "formula_role": "各大时代的新「思潮（Institutions）」经港口贸易与邻格辐射扩散，当已传播地点人口占全国达 ≥20% 时即可接纳并解锁对应革新树；每月研究进度由国家基础科研点 × (1 + 研究速度修正) 注入当前在研革新。",
        "core_drivers": [
            "礼仪语言力量（Liturgical Language Power）：本国宗教采用的礼仪语言在世界范围内的综合文化与学术实力，直接大幅加减全国研究速度",
            "全国识字率底座：学校、图书馆、修道院、大学建筑与「创新」价值观（+10% 最大识字率、−50% 接纳思潮花费）抬高各阶级识字率上限，不仅加速科研，还同步加成劳工生产效率与贵族控制力增速",
            "教士满意度与学者赞助：保持教士阶层高满意、雇佣「科学家」与「作家」类艺术家创作、派遣内阁在首都大都市定向「研究思潮」并连入先进贸易圈",
        ],
        "chapter_href": "ch07-ages-colonial.html#ages-institutions",
    },
    {
        "id": "culture_capacity_assimilation",
        "pillar": "culture",
        "zh": "文化容量、文化影响力与同化速度",
        "en": "Cultural Capacity, Influence/Tradition & Assimilation",
        "mod_keys": ["cultures_capacity", "cultures_capacity_modifier", "cultural_influence_modifier", "cultural_tradition_modifier", "global_pop_assimilation_speed_modifier", "local_pop_assimilation_speed_modifier"],
        "formula_role": "接纳异文化需占用「文化容量」（超上限严重惩罚稳定与内政）；已接纳文化立刻消除异族控制/满意度惩罚并使已整合省份达 ≥50% 相容人口时直接升为核心。未接纳文化则需靠「文化同化」按月改写为主流文化（同化攻防受本国「文化影响力」对目标「文化传统」的比值修正）。",
        "core_drivers": [
            "文化容量扩展：升格王国/帝国等级、人文主义价值观、多元帝国政府改革与特定外交/行政革新",
            "文化影响力 vs 文化传统：资助艺术家创作伟大艺术品（按倍率放大传统与影响力）、兴建剧院/歌剧院/宫廷建筑、推广本国宫廷语言与市场语言，压制被征服民族的同化抗性",
            "同化速度乘区：本地当前控制力（0% 控制力几乎无法同化！）、DIP 内阁「推广主流文化」、同语系亲缘加成与学校建筑",
        ],
        "chapter_href": "ch06-culture-religion.html#culture-status",
    },
    {
        "id": "religious_tolerance_conversion",
        "pillar": "culture",
        "zh": "正统/异端/异教容忍度与改信速度",
        "en": "Religious Tolerance & Conversion Speed",
        "mod_keys": ["tolerance_own", "tolerance_heretic", "tolerance_heathen", "global_pop_conversion_speed_modifier", "local_pop_conversion_speed_modifier"],
        "formula_role": "三种容忍度直接作用于对应信仰人群的「本地满意度」：正容忍度转化为安定与高生产力，负容忍度引发持续不满、低控制上限与宗教叛军。若走宗教统一路线，则通过「人口皈依速度」将异端/异教人口按月转化为国教信徒。",
        "core_drivers": [
            "路线二选一（灵性主义 vs 人文主义）：偏向「灵性主义」大幅强化传教改信速度与正统容忍；偏向「人文主义」则拉高异端/异教容忍度，免去漫长传教直接安定多宗教帝国",
            "改信速度核心杠杆：本地控制力、大教堂/修道院/清真寺等宗教建筑、宗教法庭与传教法典、教士阶层特权及内阁「改宗省份」行动（注意：授予齐米自治等宽容特权虽稳住异教徒，但往往禁止或大幅减速当地传教）",
        ],
        "chapter_href": "ch06-culture-religion.html#religion-system",
    },

    # --- Pillar 5: Military & Naval (军事与海权) ---
    {
        "id": "discipline_tactics",
        "pillar": "military",
        "zh": "训练度、军事战术与兵种协同",
        "en": "Discipline, Military Tactics & Combined Arms",
        "mod_keys": ["discipline", "military_tactics", "levy_combat_efficiency_modifier", "commander_combat_bonus"],
        "formula_role": "野战与海战交锋中，「训练度（Discipline）」同时放大本方造成的杀伤与士气打击，「军事战术（Military Tactics）」按比例减免本方承受的伤亡。此外，当全军单一兵种占比低于 50% 时，按步、骑、炮混编丰富度触发额外的「协同作战」加成。",
        "core_drivers": [
            "常备正规军 vs 征召兵代差：陆军征召兵天生背负 −20% 训练度与 75% 战力折算，且阵亡直接死伤本国在岗青壮年劳工；常备军享满额训练，和平期「操练（Drill）」可叠满最高 50% 部队经验减伤",
            "训练度与战术来源：「质量（Quality）」与「进攻」社会价值观、高陆军传统、军事改革（如职业军官团/军事学院）、贵族与骑士团特权(+2.5% ~ +5%)、时代核心军事革新（解锁高战术代差的新式火器与线列步兵）",
        ],
        "chapter_href": "ch08-military-combat.html#battle-mechanics",
    },
    {
        "id": "morale_initiative",
        "pillar": "military",
        "zh": "陆海军士气与接战主动性",
        "en": "Land/Naval Morale & Initiative",
        "mod_keys": ["land_morale_modifier", "naval_morale_modifier", "army_initiative", "navy_initiative", "combat_speed_modifier"],
        "formula_role": "进入战场前排的部队不会瞬间全部开火，而是每拍（每日 3 拍）按「基础 60% + min(30%, 主动性 × 2.5%) + 3% × 交战天数」掷 D100 判定接战！「主动性」高的精锐骑兵与轻快舰船能抢先完成集火包抄；「士气」则决定部队崩溃败退前的持续作战韧性。",
        "core_drivers": [
            "将领统帅与君主能力：高 MIL 统帅显著拉升队列部署、主动性与战斗骰点修正；君主每点 MIL 提供 +0.1% 全国士气；将领阵亡或溃逃会造成灾难性士气雪崩",
            "士气放大器：高陆/海军传统、高威望、正统信仰狂热/神恩、防御本土核心领土加成及满额军饷维护滑块",
            "致命扣减项：厌战度（每 1 点扣 −2.5% 士气！）、部队缺粮断补、国家破产（直接腰斩士气与战斗力）",
        ],
        "chapter_href": "ch08-military-combat.html#battle-mechanics",
    },
    {
        "id": "siege_fort_supply",
        "pillar": "military",
        "zh": "围城能力、要塞防御与补给损耗",
        "en": "Siege Ability, Fort Defense & Supply/Attrition",
        "mod_keys": ["siege_ability", "fort_defense", "local_supply_limit_modifier", "global_supply_limit_modifier", "land_unit_attrition", "global_hostile_attrition"],
        "formula_role": "要塞投射「控制区（ZoC）」锁死敌军深入路径。每次围城结算周期时长 = 基础天数 × (1 + 守方要塞防御 − 攻方围城能力)；攻城骰点加总破城状态、炮兵加值、封锁加值与地形修正，出缺口并攻破后方可夺占省份行政中心。",
        "core_drivers": [
            "攻城提速三件套：配齐足额攻城炮兵团（提供最高 +8 检定加值并概率轰出城墙缺口）、派遣海军彻底封锁沿海要塞港口（消除守军补给加值）、堆叠攻城专家将领与工兵革新",
            "要塞防御构筑：利用山地/丘陵/河口岛屿地形建城，升级星形棱堡（每时代要塞等级必须跟上，否则被新式重炮迅速轰穿），搭配防御价值观与戍卫特权",
            "后勤补给生命线：大军团切忌在严冬山地超补给上限抱团驻留；推进时保持与本土补给站（Supply Depot）或受控港口的补给线畅通，防止非战斗损耗抽干人力池",
        ],
        "chapter_href": "ch08-military-combat.html#siege-forts",
    },
    {
        "id": "manpower_sailors_maritime",
        "pillar": "military",
        "zh": "月度人力、水手与海上存在",
        "en": "Manpower, Sailors & Maritime Presence",
        "mod_keys": ["global_manpower_modifier", "local_manpower", "global_sailors_modifier", "local_sailors", "global_maritime_presence_modifier", "local_maritime_presence"],
        "formula_role": "常备陆海军的招募与战损补充完全依赖全国「人力池」与「水手池」（最大储量上限等于 60 个月的月度恢复量）。「海上存在（0%–100%）」则是海权帝国的行政生命线：100% 海上存在可将单格海域的首都邻近度损耗从 30 压至极低的 5（1.4.9 起基础海上存在不再直接附加贸易加成，需特定修正转化）！",
        "core_drivers": [
            "兵源建筑与控制力乘积：军械库(+10 人/月)、训练场(+10)、军营(+15)、军团营地(+20)、征兵中心(+25) 及沿海码头/船坞（水手），其实际产出均需乘以「本地满员率 × 本地控制力」（在 0% 控制力飞地建军营几乎不产人力！）",
            "数量价值观与兵役法：「数量（Quantity）」社会价值观、征兵制法律政策、军事官僚机构大幅扩充全国人力修正",
            "刷满海上存在的两大抓手：一是在关键航道沿岸兴建海军基地、灯塔与港务建筑（提供被动本地海上存在）；二是派遣轻型护卫舰/巡航分舰队在战略海区常态化执行「海盗巡逻 / 投射海权」任务",
        ],
        "chapter_href": "ch09-navy-war-peace.html#maritime-presence",
    },

    # --- Pillar 6: Diplomacy, Subjects & IO (外交与国际体系) ---
    {
        "id": "diplo_capacity_reputation",
        "pillar": "diplomacy",
        "zh": "外交容量与外交声誉",
        "en": "Diplomatic Capacity & Diplomatic Reputation",
        "mod_keys": ["diplomatic_capacity", "diplomatic_capacity_modifier", "diplomatic_reputation", "diplomatic_range_modifier"],
        "formula_role": "每缔结一项正式同盟、王室联姻保证或维持一个属国，都会按对方体量占用「外交容量」（同时结盟多个列强还会触发强盟饱和额外占用），超上限扣减政治影响力与外交效率。「外交声誉」则直接加分于结盟、附庸、和平谈判、帝国选举与属国服从判定。",
        "core_drivers": [
            "扩充外交容量：提升国家等级（公国→王国→帝国）、外向/分权价值观、设立外交部官僚机构、在首都兴建外国使馆区及研发外交革新",
            "积累外交声誉：君主每点 DIP (+0.05 声誉)、重信守诺（不撕毁盟约、不无故背刺停战期）、贵族外交家特质与国际组织领袖威望；外交吞并属国完成瞬间或败坏声誉间谍行动会造成阶段性声誉扣减",
        ],
        "chapter_href": "ch10-diplomacy-subjects.html#diplo-capacity",
    },
    {
        "id": "antagonism_ae",
        "pillar": "diplomacy",
        "zh": "扩张敌意 (AE) 与反法同盟包围网",
        "en": "Antagonism & Coalition Threshold",
        "mod_keys": ["antagonism_received_modifier", "antagonism_monthly_change_modifier", "antagonism_religion_influence", "antagonism_culture_influence"],
        "formula_role": "强宣、撕毁停战或和约割地会产生「敌意（Antagonism）」，按距离、同宗教、同文化组与同国际组织（尤其神圣罗马帝国境内加倍）向周边国家辐射，并以 ×(−4) 倍率恶化对方对你的好感。当至少数个国家对你的敌意 >50 且当前好感 <−50、无停战协议时，即可组建针对你的包围网联盟。",
        "core_drivers": [
            "源头减免手段：务必使用高折扣宣战理由（如收复核心、圣战、帝国敕令而非无理由强宣）；和约中将占领地直接割让给己方属国可大幅减免产生的敌意；堆叠「敌意产生修正」",
            "加快年度衰减：高威望、高外交声誉、安抚性外交立场与人文主义革新加速每年年初的敌意自然消退",
            "拆解包围网技巧：派遣外交官对敌意刚过 50 的摇摆强国全力「改善关系 / 赠礼」，只要把总好感拉回 >−50（或维持交叉停战期），对方即无法入网",
        ],
        "chapter_href": "ch10-diplomacy-subjects.html#antagonism-coalition",
    },
    {
        "id": "subject_loyalty_annexation",
        "pillar": "diplomacy",
        "zh": "属国忠诚度、殖民迁移与外交吞并",
        "en": "Subject Loyalty, Colonial Migration & Annexation",
        "mod_keys": ["subject_loyalty", "subject_income_modifier", "diplomatic_annexation_efficiency", "annexation_speed_modifier", "colonial_migration_size_modifier", "colonial_range_modifier"],
        "formula_role": "属国忠诚度（0–100）必须保持在 ≥50 以上才会正常上缴贡赋、出兵助战并允许推进「外交吞并」（低于 50 停止进贡并可寻求你宿敌的独立支持）。海外「特许殖民地」则靠殖民范围触达后，每月从母国港口抽调人口迁入直至建省。",
        "core_drivers": [
            "宗属总体实力比红线：系统合并计算「全体属国军经实力占宗主+属国总和的比例」，一旦超过 20% 基准线便按高额斜率全体扣减忠诚度——宗主国自身常备军与核心税基必须始终压过众藩属之和",
            "集权 vs 分权路线取舍：「地方分权」最高提供 +30 属国忠诚（适合神罗诸侯群/多附庸体系）；「中央集权」虽扣 −20 属国忠诚，但提供高达 +33% 外交吞并速度（适合快速削藩并入直辖）",
            "领土连通与吞并效率：属国与宗主首都之间若被多块 0% 控制力的无序海域或荒地隔断会扣减忠诚；堆叠「外交吞并效率」、高外交声誉、同宗教同文化亲缘可大幅加快吞并读条",
        ],
        "chapter_href": "ch10-diplomacy-subjects.html#subjects-annex",
    },
]


def build_metrics_bundle(ms, zh_kv, game_ctx):
    """Build docs/assets/metrics-data.js for metrics.html (42 flagship metrics + searchable 1,364 modifiers)."""
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
        for s in raw_sources:
            g_zh = GROUP_LABELS_ZH.get(s["group"], s["group"])
            disp = "启用" if s["display"] == "是" else ("禁用" if s["display"] == "否" else s["display"])
            cond = humanize_condition(s.get("condition", ""), zh_kv, game_ctx)
            # Strip redundant default condition phrases to keep cards super clean
            for boring in ("持有这项阶层特权时", "采用这项政府改革时", "研发这项革新后", "建筑在当地运作，按建筑等级和商品供应缩放"):
                if cond == boring:
                    cond = ""
            grouped[g_zh].append({
                "zh": s["zh"],
                "val": disp,
                "scope": s.get("scope", ""),
                "cond": cond[:90],
            })
        item = {
            "id": mk,
            "zh": minfo.get("zh", mk),
            "en": minfo.get("en", mk),
            "cat": CAT_ZH.get(minfo.get("category", "all"), "其他修正"),
            "total": len(raw_sources),
            "groups": [[gname, items[:24], len(items)] for gname, items in grouped.items()],
        }
        modifiers_list.append(item)
        mod_lookup[mk] = item

    modifiers_list.sort(key=lambda x: (-x["total"], x["zh"]))

    # Attach live grouped sources preview onto each flagship metric
    enriched_flagships = []
    for fm in FLAGSHIP_METRICS:
        fm_copy = dict(fm)
        merged_groups = collections.defaultdict(list)
        total_src = 0
        for mk in fm["mod_keys"]:
            m_obj = mod_lookup.get(mk)
            if not m_obj:
                continue
            total_src += m_obj["total"]
            for gname, items, _cnt in m_obj["groups"]:
                existing_names = {x["zh"] for x in merged_groups[gname]}
                for it in items:
                    if it["zh"] not in existing_names:
                        merged_groups[gname].append(it)
                        existing_names.add(it["zh"])
        fm_copy["total_sources"] = total_src
        fm_copy["source_groups"] = [[g, lst[:16], len(lst)] for g, lst in merged_groups.items()]
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
    print(f"Exported metrics-data.js: {len(enriched_flagships)} flagship metrics, {len(modifiers_list)} modifiers with sources.")
