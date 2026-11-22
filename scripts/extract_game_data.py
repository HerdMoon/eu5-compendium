# -*- coding: utf-8 -*-
"""
Extract clean, verified game data for EU5 Mechanics Compendium (1.4.9).
- Strictly reads from EU5 game installation directory and read-only reference files in eu5-atlas.
- Never modifies anything outside C:/Users/seepath/.gemini/antigravity/scratch/eu5-compendium.
"""
import glob
from html.parser import HTMLParser
import json
import os
import re
import shutil

GAME_DIR = r"D:\SteamLibrary\steamapps\common\Europa Universalis V\game"
ATLAS_DIR = r"C:\Users\seepath\Documents\Codex\2026-11-02\x20\work\eu5-atlas"
PROJ_DIR = r"C:\Users\seepath\.gemini\antigravity\scratch\eu5-compendium"
DATA_DIR = os.path.join(PROJ_DIR, "data")
ICONS_DST = os.path.join(PROJ_DIR, "docs", "assets", "goods-icons")
LEDGERS_JS_DIR = os.path.join(PROJ_DIR, "docs", "assets", "ledgers")
CATALOGS_JS_DIR = os.path.join(PROJ_DIR, "docs", "assets", "catalogs")
ASSETS_DIR = os.path.join(PROJ_DIR, "docs", "assets")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(ICONS_DST, exist_ok=True)
os.makedirs(LEDGERS_JS_DIR, exist_ok=True)
os.makedirs(CATALOGS_JS_DIR, exist_ok=True)


def parse_defines():
    path = os.path.join(GAME_DIR, "loading_screen", "common", "defines", "00_defines.txt")
    with open(path, encoding="utf-8-sig") as f:
        lines = f.readlines()
    defines = {}
    cur_sec = None
    depth = 0
    for raw in lines:
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        if depth == 0:
            m = re.match(r"^([A-Za-z0-9_]+)\s*=\s*\{$", line)
            if m:
                cur_sec = m.group(1)
                defines.setdefault(cur_sec, {})
                depth = 1
                continue
        if cur_sec:
            if line == "}":
                depth -= 1
                if depth == 0:
                    cur_sec = None
                continue
            if "{" in line and "}" not in line:
                depth += line.count("{") - line.count("}")
                continue
            if "}" in line and "{" not in line:
                depth -= line.count("}")
                continue
            m = re.match(r"^([A-Za-z0-9_]+)\s*=\s*(.+)$", line)
            if m:
                k, v = m.group(1), m.group(2).strip().strip('"')
                if not v.startswith("@"):
                    try:
                        v_num = float(v) if "." in v else int(v)
                        defines[cur_sec][k] = v_num
                    except ValueError:
                        defines[cur_sec][k] = v
    with open(os.path.join(DATA_DIR, "defines.json"), "w", encoding="utf-8") as f:
        json.dump(defines, f, ensure_ascii=False, indent=2)
    print(f"Extracted defines: {sum(len(v) for v in defines.values())} keys across {len(defines)} sections.")
    return defines


def load_yml_kv(lang="simp_chinese"):
    loc_dir = os.path.join(GAME_DIR, "main_menu", "localization", lang)
    kv = {}
    yml_files = sorted(glob.glob(os.path.join(loc_dir, "*.yml")))
    for extra_sub in ["dlc", "modifiers"]:
        subp = os.path.join(loc_dir, extra_sub)
        if os.path.exists(subp):
            yml_files.extend(sorted(glob.glob(os.path.join(subp, "**", "*.yml"), recursive=True)))
    line_re = re.compile(r'^\s*([A-Za-z0-9_.\-]+):\d*\s+"(.*)"\s*$')
    for p in yml_files:
        try:
            with open(p, encoding="utf-8-sig", errors="ignore") as f:
                for line in f:
                    m = line_re.match(line)
                    if m:
                        kv[m.group(1)] = m.group(2)
        except OSError:
            pass
    return kv


def clean_paradox_text(text, loc_kv, defines, concepts_name_map, lang="zh"):
    if not text:
        return ""
    # Replace both double-escaped \\n and literal \n
    s = text.replace("\\\\n", "\n").replace("\\n", "\n")

    # 1. Resolve $key$ substitutions up to 5 passes
    for _ in range(5):
        def repl_dollar(m):
            k = m.group(1)
            if k in ("BULLET", "BULLET_WITH_TAB"):
                return "• "
            if k in loc_kv:
                return loc_kv[k]
            return k
        new_s = re.sub(r"\$([A-Za-z0-9_.\-]+)\$", repl_dollar, s)
        if new_s == s:
            break
        s = new_s

    # 2. Resolve GetDefine('Sec','Key')
    legacy_define_aliases = {
        ("NCombat", "BOMBARD_HOURS"): {
            "zh": f"{defines.get('NCombat', {}).get('BOMBARD_DURATION_DAILY', 3)}天（日步）/ {defines.get('NCombat', {}).get('BOMBARD_DURATION_HOURLY', 5)}",
            "en": f"{defines.get('NCombat', {}).get('BOMBARD_DURATION_DAILY', 3)} days (daily) / {defines.get('NCombat', {}).get('BOMBARD_DURATION_HOURLY', 5)}",
        },
        ("NCombat", "INITIATIVE_CHANCE_EACH"): {
            "zh": f"{float(defines.get('NCombat', {}).get('INITIATIVE_CHANCE_EACH_DAILY', 0.025))*100:g}%（日步）/ {float(defines.get('NCombat', {}).get('INITIATIVE_CHANCE_EACH_HOURLY', 0.01))*100:g}%（时步）",
            "en": f"{float(defines.get('NCombat', {}).get('INITIATIVE_CHANCE_EACH_DAILY', 0.025))*100:g}% (daily) / {float(defines.get('NCombat', {}).get('INITIATIVE_CHANCE_EACH_HOURLY', 0.01))*100:g}% (hourly)",
        },
    }

    def repl_define(m):
        sec, key, fmt = m.group(1), m.group(2), m.group(3) or ""
        if (sec, key) in legacy_define_aliases:
            return legacy_define_aliases[(sec, key)][lang]
        val = defines.get(sec, {}).get(key)
        if val is None:
            return key
        if isinstance(val, (int, float)):
            if "%" in fmt:
                pct = val * 100
                if "+" in fmt and pct >= 0:
                    return f"+{pct:.0f}%" if abs(pct - round(pct)) < 1e-6 else f"+{pct:.1f}%"
                return f"{pct:.0f}%" if abs(pct - round(pct)) < 1e-6 else f"{pct:.1f}%"
            return f"{val:g}"
        return str(val)

    s = re.sub(
        r"\[GetDefine\(\s*'([^']+)'\s*,\s*'([^']+)'\s*\)(?:\|([^\]]*))?\]",
        repl_define,
        s,
    )

    if lang == "zh":
        special_calls = {
            "GetAutoModifier('balanced_harmony').GetNameWithTooltip": "调和平衡",
            "GetAutoModifier('negative_harmony').GetNameWithTooltip": "阴面失衡（负调和）",
            "GetAutoModifier('positive_harmony').GetNameWithTooltip": "阳面失衡（正调和）",
            "GetCountry('DLH').GetName": "德里苏丹国",
            "GetCountry('DLH').GetNameWithNoTooltip": "德里苏丹国",
            "GetInternationalOrganizationType('catholic_church').GetName": "天主教会",
            "GetInternationalOrganizationType('sect').GetName": "宗派",
            "GetUniqueInternationalOrganization('hre').GetLeaderTitle": "神圣罗马皇帝",
            "GetUniqueInternationalOrganization('hre').GetName": "神圣罗马帝国",
            "GetUniqueInternationalOrganization('hre').GetNameWithNoTooltip": "神圣罗马帝国",
            "GetUniqueInternationalOrganization('middle_kingdom').GetName": "中华天朝",
            "ShowModifierEffect('excommunicated')": "每月宗教影响力 -0.1、威望 -0.2、政府力量 -0.1、对教宗关系 -100",
            "ShowModifierEffect('head_of_the_cabinet_modifier')": "内阁效率 +25%、内阁特质效果翻倍（+100%）、任职期间不可免职或兼任统帅",
            "ShowModifierEffect('integration_integrated')": "本地最大控制力 +5%、本地分离主义 +0.10、同化速度 -1%",
            "ShowModifierEffect('is_army_levy')": "训练度 -20%、经验衰减 +2%、食物消耗 -75%（轻装觅食）",
            "ShowModifierEffect('is_navy_levy')": "经验衰减 +2%",
            "ShowModifierEffect('minor_rebel_uprising')": "本地月度繁荣度 -0.5%、本地月度控制力 -0.5%",
            "ShowModifierEffect('province_starving')": "人口增长 -5%/月、补给上限 -25%、移民吸引力 -1.0、上层阶级容量 -50%、降级速度 +50%",
            "ShowAutoModifierEffect('war_exhaustion_impact')": "陆海军士气 -2.5%、全局阶层满意度目标 -1%、全局防御 -2.5%（每 1 点厌战）",
            "ShowBiasValue('opinion_excommunicated')": "-50",
            "ShowBiasValue('opinion_excommunicated')|+=0": "-50",
            "ShowParliamentTypes": "包括议会制、贵族议会、三级会议等政体专属议会形式",
            "ShowAdultAge": str(defines.get("NCharacter", {}).get("ADULT_AGE", 16)),
            "ShowMaxInfantAge": str(defines.get("NCharacter", {}).get("MAX_INFANT_AGE", 2)),
            "ShowMinChildAge": "3",
            "ShowMaxChildAge": str(defines.get("NCharacter", {}).get("MAX_CHILD_AGE", 10)),
            "ShowMinAdolescentAge": "11",
            "ShowMaxAdolescentAge": str(defines.get("NCharacter", {}).get("MAX_ADOLESCENT_AGE", 15)),
            "ShowCabinetTypeDatabase('adm')": "（行政 ADM 类内阁行动：如提升控制力、发展省份、降通胀、研究思潮）",
            "ShowCabinetTypeDatabase('dip')": "（外交 DIP 类内阁行动：如灾后恢复、安抚阶层、推广文化/宗教、降厌战）",
            "ShowCabinetTypeDatabase('mil')": "（军事 MIL 类内阁行动：如整合省份/地区、稳定国家、镇压叛乱）",
        }
    else:
        special_calls = {
            "GetAutoModifier('balanced_harmony').GetNameWithTooltip": "Balanced Harmony",
            "GetAutoModifier('negative_harmony').GetNameWithTooltip": "Negative Harmony",
            "GetAutoModifier('positive_harmony').GetNameWithTooltip": "Positive Harmony",
            "GetCountry('DLH').GetName": "Delhi Sultanate",
            "GetCountry('DLH').GetNameWithNoTooltip": "Delhi Sultanate",
            "GetInternationalOrganizationType('catholic_church').GetName": "Catholic Church",
            "GetInternationalOrganizationType('sect').GetName": "Sect",
            "GetUniqueInternationalOrganization('hre').GetLeaderTitle": "Emperor",
            "GetUniqueInternationalOrganization('hre').GetName": "Holy Roman Empire",
            "GetUniqueInternationalOrganization('hre').GetNameWithNoTooltip": "Holy Roman Empire",
            "GetUniqueInternationalOrganization('middle_kingdom').GetName": "Middle Kingdom",
            "ShowModifierEffect('excommunicated')": "Monthly Religious Influence -0.1, Prestige -0.2, Gov Power -0.1, Papal Relations -100",
            "ShowModifierEffect('head_of_the_cabinet_modifier')": "Cabinet Efficiency +25%, Cabinet Trait Impact +100%, cannot be removed",
            "ShowModifierEffect('integration_integrated')": "Local Max Control +5%, Separatism +0.10, Assimilation -1%",
            "ShowModifierEffect('is_army_levy')": "Discipline -20%, Experience Decay +2%, Food Consumption -75%",
            "ShowModifierEffect('is_navy_levy')": "Experience Decay +2%",
            "ShowModifierEffect('minor_rebel_uprising')": "Local Monthly Prosperity -0.5%, Local Monthly Control -0.5%",
            "ShowModifierEffect('province_starving')": "Pop Growth -5%/mo, Supply Limit -25%, Migration -1.0, Upper Class Cap -50%",
            "ShowAutoModifierEffect('war_exhaustion_impact')": "Land/Naval Morale -2.5%, Estate Target Satisfaction -1%, Global Defensive -2.5% per point",
            "ShowBiasValue('opinion_excommunicated')": "-50",
            "ShowBiasValue('opinion_excommunicated')|+=0": "-50",
            "ShowParliamentTypes": "Monarchy / Estate / Noble Parliament types",
            "ShowAdultAge": str(defines.get("NCharacter", {}).get("ADULT_AGE", 16)),
            "ShowMaxInfantAge": str(defines.get("NCharacter", {}).get("MAX_INFANT_AGE", 2)),
            "ShowMinChildAge": "3",
            "ShowMaxChildAge": str(defines.get("NCharacter", {}).get("MAX_CHILD_AGE", 10)),
            "ShowMinAdolescentAge": "11",
            "ShowMaxAdolescentAge": str(defines.get("NCharacter", {}).get("MAX_ADOLESCENT_AGE", 15)),
            "ShowCabinetTypeDatabase('adm')": "Administrative cabinet actions",
            "ShowCabinetTypeDatabase('dip')": "Diplomatic cabinet actions",
            "ShowCabinetTypeDatabase('mil')": "Military cabinet actions",
        }

    manual_lookup_zh = {
        "town_rights_enable": "城镇特权（探索时代革新）",
        "war_exhaustion_impact": "厌战度影响",
        "opinion_excommunicated": "-50",
        "catholic": "天主教", "christian": "基督教", "muslim": "伊斯兰教",
        "hellenistic": "希腊多神教", "hellenism_religion": "希腊多神教",
        "mayan": "玛雅", "nahuatl": "纳瓦特尔", "hussite": "胡斯派",
        "lutheran": "路德宗", "calvinist": "加尔文宗", "anglican": "圣公宗",
        "orthodox": "东正教", "shinto": "神道教", "hindu": "印度教",
        "andean_group": "安第斯文化组", "western_europe": "西欧",
        "scandinavian_region": "斯堪的纳维亚区域", "italy_region": "意大利区域",
        "france_region": "法兰西区域", "iberia_region": "伊比利亚区域",
        "great_britain_region": "大不列颠区域", "balkan_region": "巴尔干区域",
        "anatolia_region": "安纳托利亚区域", "crescent_region": "新月沃土区域",
        "egypt_region": "埃及区域", "maghreb_region": "马格里布区域",
        "north_german_region": "北德意志区域", "south_german_region": "南德意志区域",
        "age_1_traditions": "传统时代（I）", "age_2_renaissance": "文艺复兴时代（II）",
        "age_3_discovery": "探索时代（III）", "age_4_reformation": "宗教改革时代（IV）",
        "age_5_absolutism": "绝对主义时代（V）", "age_6_revolutions": "革命时代（VI）",
        "monarchy": "君主制", "republic": "共和国", "theocracy": "神权制",
        "steppe_horde": "草原游牧", "tribe": "部落制",
        "nobles_estate": "贵族阶层", "clergy_estate": "教士阶层",
        "burghers_estate": "市民阶层", "peasants_estate": "平民阶层", "crown_estate": "王室",
        "nobles": "贵族", "clergy": "教士", "burghers": "市民",
        "peasants": "平民", "laborers": "劳工", "slaves": "奴隶",
        "oresund": "厄勒海峡", "gulf_izmit": "伊兹密特湾",
        "free_subjects": "自由民", "defensive": "防御倾向", "land": "陆权倾向", "naval": "海权倾向",
        "elector": "选帝侯", "free_city": "帝国自由市",
        "junior_partner": "被联统国", "senior_partner": "联统主导国",
        "army_artillery": "炮兵", "army_heavy_cavalry": "重骑兵", "army_light_infantry": "轻步兵",
        "navy_heavy_ship": "重型战舰", "navy_light_ship": "轻型战舰",
        "a_arquebusiers": "火绳枪兵", "a_cavaliers": "骑士骑兵",
        "n_cog": "柯克帆船", "n_twodecker": "双层战列舰", "n_xebec": "三桅帆船",
        "global_estate_target_satisfaction": "全局阶层满意度均衡点",
        "local_peasant_enfranchisment": "本地平民自主权",
        "mercenary_range": "雇佣兵招募范围", "stability_decay": "稳定度衰减", "subject_loyalty": "属国忠诚度",
        "military_access": "军事通行权", "fleet_basing_rights": "驻港权", "food_access": "食物获取权",
        "embargo_nation": "禁运", "sound_toll_exemption": "海峡通行费豁免", "scutage": "兵役免除税",
        "alliance": "同盟", "guarantee": "保障独立",
        "katun_celebration": "廿纪年大捷庆典", "katun_celebration_bad": "廿纪年厄运惩罚",
        "looted": "被劫掠", "minor_rebel_uprising": "小规模叛乱修正",
        "winter_none": "无冬", "winter_mild": "轻冬", "winter_normal": "常冬", "winter_severe": "严冬",
    }

    def repl_bracket(m):
        inner = m.group(1).strip()
        if inner in special_calls:
            return special_calls[inner]
        mc = re.match(r"Concept\(\s*'([^']+)'\s*,\s*'([^']+)'\s*\)", inner)
        if mc:
            return f"【{mc.group(2)}】" if lang == "zh" else mc.group(2)
        mdb = re.match(r"Show(?:Database|DatabaseWithIcon|Values)\(\s*'([^']+)'\s*\)", inner)
        if mdb:
            return f"（详见速查典：{mdb.group(1)}）" if lang == "zh" else f"(See ledger: {mdb.group(1)})"
        ms = re.match(r"[A-Za-z0-9_]+\(\s*'([^']+)'\s*\)", inner)
        if ms:
            arg = ms.group(1)
            if lang == "zh":
                if arg in manual_lookup_zh:
                    return manual_lookup_zh[arg]
                for cand in [arg, f"MODIFIER_TYPE_NAME_{arg}", f"goods_{arg}", f"building_{arg}", f"{arg}_name"]:
                    if cand in loc_kv and "[" not in loc_kv[cand]:
                        return loc_kv[cand]
            return concepts_name_map.get(arg, arg.replace("_", " "))
        base = inner.split("|")[0].strip()
        if base in concepts_name_map:
            return f"【{concepts_name_map[base]}】" if lang == "zh" else concepts_name_map[base]
        if base in loc_kv and "[" not in loc_kv[base]:
            return loc_kv[base]
        return base.replace("_", " ")

    for _ in range(3):
        new_s = re.sub(r"\[([^\[\]]+)\]", repl_bracket, s)
        if new_s == s:
            break
        s = new_s

    s = re.sub(r"@[A-Za-z0-9_]+!", "", s)
    s = re.sub(r"#(?:[A-Za-z0-9_+=.%]+)\s*", "", s).replace("#!", "")
    s = re.sub(r"\n{3,}", "\n\n", s).strip()
    return s


def categorize_concept(cid, zh, desc):
    if any(k in cid for k in ["location", "province", "area", "region", "continent", "climate", "topography", "vegetation", "winter", "hemisphere", "river", "lake", "seazone", "sea_current", "frozen", "strait", "corridor", "road", "harbor", "port", "coastal", "inland", "core", "integrat", "conquer", "coloni", "separat", "proximity", "control", "prosperity", "development", "urban", "rural", "town", "impassable", "wasteland", "weather"]):
        return "territory"
    if any(k in cid for k in ["pop", "food", "starv", "agricult", "good", "raw_material", "produced_good", "rgo", "building", "employ", "market", "trade", "import", "export", "tariff", "subvent", "merchant", "price", "supply", "demand", "stockpile", "tax", "wealth", "gold", "treasury", "income", "expense", "loan", "bond", "bank", "interest", "debt", "credit", "inflation", "mint", "budget", "subsid", "sound_toll", "econom", "gdp", "disease", "migrat", "literacy", "establish", "volatility", "plantation", "slaver"]):
        return "economy"
    if any(k in cid for k in ["country", "rank", "government", "reform", "law", "policy", "cabinet", "estate", "parliament", "privilege", "crown", "legitimacy", "republican", "devotion", "horde", "tribal", "bureaucracy", "entrench", "rebel", "revolt", "civil_war", "unrest", "stability", "character", "ruler", "heir", "consort", "dynast", "regent", "courtier", "adult", "child", "infant", "adolescent", "marry", "marriage", "betrothal", "divorce", "societal", "mission", "action", "decision", "political_influence", "political_power", "private_regiment", "legal_male", "trait", "ability", "adm", "dip", "mil", "immortality"]):
        return "state"
    if any(k in cid for k in ["cultur", "language", "dialect", "relig", "faith", "heretic", "heathen", "toleran", "convert", "conversion", "assimilat", "art", "saint", "canoniz", "clergy", "pope", "curia", "cardinal", "patriarch", "pentarchy", "tithe", "excommunicat", "age", "institution", "advance", "research", "embrace", "explor", "expedition", "conquistador", "terra_incognita", "discover", "chivalr", "holy_site", "omen", "karma", "purity", "honor", "yanantin", "righteousness", "harmony", "self_control", "doom", "katun", "reformation", "guru", "avatar", "god", "sect", "movement", "order", "zeal", "calling", "holding"]):
        return "culture"
    if any(k in cid for k in ["army", "navy", "unit", "regiment", "ship", "combat", "battle", "siege", "fort", "garrison", "zone_of_control", "morale", "discipline", "tactics", "frontage", "flank", "center", "reserve", "broken", "initiative", "bombard", "phase", "engage", "d10", "d20", "d100", "dice", "strength", "attrition", "loot", "reinforce", "repair", "levy", "levies", "regular", "manpower", "sailor", "mercenar", "prisoner", "privateer", "pirate", "blockade", "maritime", "war", "peace", "casus_belli", "truce", "occup", "retreat", "exile", "crossing", "disembark", "embark", "assault", "artillery", "hull", "cannon", "experience", "tradition", "combined_arms", "defender", "attacker", "enemy"]):
        return "military"
    if any(k in cid for k in ["diplom", "ally", "alliance", "subject", "overlord", "vassal", "union", "junior_partner", "senior_partner", "annex", "liberty_desire", "antagonism", "coalition", "opinion", "trust", "favor", "rival", "spy", "fow", "fog_of_war", "hidden", "international", "hre", "imperial", "elector", "emperor", "free_cit", "great_power", "regional_power", "hegemon", "power_projection", "treaty", "guarantee", "military_access", "fleet_basing", "embargo", "isolate", "score", "victory_card", "situation", "disaster", "event", "revolution"]):
        return "diplomacy"
    return "state"


def extract_glossary(defines):
    zh_kv = load_yml_kv("simp_chinese")
    en_kv = load_yml_kv("english")

    zh_gc_path = os.path.join(GAME_DIR, "main_menu", "localization", "simp_chinese", "game_concepts_l_simp_chinese.yml")
    en_gc_path = os.path.join(GAME_DIR, "main_menu", "localization", "english", "game_concepts_l_english.yml")
    line_re = re.compile(r'^\s*(game_concept_[A-Za-z0-9_]+):\d*\s+"(.*)"\s*$')

    zh_gc, en_gc = {}, {}
    with open(zh_gc_path, encoding="utf-8-sig") as f:
        for line in f:
            m = line_re.match(line)
            if m:
                zh_gc[m.group(1)] = m.group(2)
    with open(en_gc_path, encoding="utf-8-sig") as f:
        for line in f:
            m = line_re.match(line)
            if m:
                en_gc[m.group(1)] = m.group(2)

    zh_merged = {**zh_kv, **zh_gc}
    en_merged = {**en_kv, **en_gc}

    zh_name_map, en_name_map = {}, {}
    for gc_map, target_map, merged in [(zh_gc, zh_name_map, zh_merged), (en_gc, en_name_map, en_merged)]:
        for k, v in gc_map.items():
            if not k.endswith("_desc") and not k.endswith("_title") and not k.endswith("_list"):
                cid = k[len("game_concept_"):]
                v2 = re.sub(r"\$([A-Za-z0-9_.\-]+)\$", lambda m: merged.get(m.group(1), m.group(1)), v)
                target_map[cid] = v2

    desc_keys = [k for k in zh_gc.keys() if k.endswith("_desc")]
    seen_entries = {}
    for dk in desc_keys:
        base_id = dk[len("game_concept_"):-len("_desc")]
        raw_desc_zh = zh_gc.get(dk, "")
        if not raw_desc_zh or raw_desc_zh.strip() == "TODO":
            continue
        m_ref = re.match(r"^\$(game_concept_[A-Za-z0-9_]+)\$$", raw_desc_zh.strip())
        if m_ref and m_ref.group(1) in zh_gc:
            raw_desc_zh = zh_gc[m_ref.group(1)]
        clean_zh_desc = clean_paradox_text(raw_desc_zh, zh_merged, defines, zh_name_map, lang="zh")
        if not clean_zh_desc or clean_zh_desc == "TODO":
            continue

        title_key = f"game_concept_{base_id}"
        if base_id.endswith(("_lower", "_upper", "_short", "_with_icon", "_no_icon", "_i")):
            continue
        if title_key not in zh_gc:
            continue
        name_zh = zh_name_map.get(base_id) or zh_gc.get(title_key) or base_id
        name_zh = clean_paradox_text(name_zh, zh_merged, defines, zh_name_map, lang="zh").replace("【", "").replace("】", "")
        name_en = en_name_map.get(base_id) or en_gc.get(title_key) or base_id.replace("_", " ").title()
        name_en = clean_paradox_text(name_en, en_merged, defines, en_name_map, lang="en")

        raw_desc_en = en_gc.get(dk, "")
        m_ref_en = re.match(r"^\$(game_concept_[A-Za-z0-9_]+)\$$", raw_desc_en.strip())
        if m_ref_en and m_ref_en.group(1) in en_gc:
            raw_desc_en = en_gc[m_ref_en.group(1)]
        clean_en_desc = clean_paradox_text(raw_desc_en, en_merged, defines, en_name_map, lang="en")

        # Strip redundant self-title prefix inside upper_desc concatenations like "国教 国教..."
        for nm, txt_key in [(name_zh, "zh")]:
            pass
        if clean_zh_desc.startswith(name_zh + " "):
            clean_zh_desc = clean_zh_desc[len(name_zh) + 1:].strip()
        if clean_en_desc.lower().startswith(name_en.lower() + " "):
            pass

        seen_entries[base_id] = {
            "id": base_id,
            "zh": name_zh,
            "en": name_en,
            "pillar": categorize_concept(base_id, name_zh, clean_zh_desc),
            "desc": clean_zh_desc,
            "desc_en": clean_en_desc,
        }

    # Extract official pop types and estates from pops_l_* & estate_l_* into glossary
    supplement_defs = [
        ("pop", "economy", ["nobles", "clergy", "burghers", "peasants", "laborers", "soldiers", "slaves", "tribesmen"]),
        ("estate", "state", ["nobles_estate", "clergy_estate", "burghers_estate", "peasants_estate", "crown_estate"]),
    ]
    for _kind, pil, keys in supplement_defs:
        for cid in keys:
            if cid in seen_entries or cid not in zh_merged or f"{cid}_desc" not in zh_merged:
                continue
            nz = clean_paradox_text(zh_merged[cid], zh_merged, defines, zh_name_map, lang="zh").replace("【", "").replace("】", "")
            ne = clean_paradox_text(en_merged.get(cid, cid.replace("_", " ").title()), en_merged, defines, en_name_map, lang="en")
            dz = clean_paradox_text(zh_merged[f"{cid}_desc"], zh_merged, defines, zh_name_map, lang="zh")
            de = clean_paradox_text(en_merged.get(f"{cid}_desc", ""), en_merged, defines, en_name_map, lang="en")
            if dz:
                seen_entries[cid] = {"id": cid, "zh": nz, "en": ne, "pillar": pil, "desc": dz, "desc_en": de}

    extra_concepts = [
        {
            "id": "estate_interactions",
            "zh": "阶层直接互动与绝境行动",
            "en": "Estate Interactions & Emergency Actions",
            "pillar": "state",
            "desc": "在阶层面板可直接执行的主动行动，分为常规互动（贿赂阶层、削减阶层力量强拆建筑、向阶层出售艺术品、征用私兵）与绝境行动（要求扩大征召、征收特别税、召开紧急议会及五大阶层专属求助如向市民无息紧急拨款）。处于防御性战争时，绝境行动消耗与满意度惩罚全部减半。",
            "desc_en": "Direct actions performed on estates including Bribe Estate, Perform Reduction, Sell Work of Art, Press Private Regiments, and Emergency Actions (costs & satisfaction hits halved in defensive wars).",
        },
        {
            "id": "uncontrolled_wealth",
            "zh": "未受控财富",
            "en": "Uncontrolled Wealth",
            "pillar": "economy",
            "desc": "地点产出财富中未被国家控制力覆盖的部分，即 地点财富 × (1 − 控制力)。这部分财富不会消失，而是按阶层份额直接流入当地阶层金库，进而资助阶层在低控制力（<75%）地点建造高阶建筑、膨胀政治力量的阶层建筑以及私人军团。",
            "desc_en": "Location wealth not captured by control (Wealth × (1 - Control)), flowing directly into local estate gold pools.",
        },
        {
            "id": "cabinet_bottleneck",
            "zh": "内阁席位瓶颈",
            "en": "Cabinet Slot Bottleneck",
            "pillar": "state",
            "desc": "EU5 核心治理与扩张制约：同一时间全国只能运行与内阁席位等量的内阁行动，而整合未整合省份（Integrate Province）、灾后恢复（Recovery Effort）、提升控制力、推广文化均需占用席位。在解锁地区级整合行动前，内阁席位直接决定版图消化上限。",
            "desc_en": "Core strategic bottleneck where cabinet seats limit parallel province integration, recovery, assimilation, and control boosting.",
        },
    ]
    for ec in extra_concepts:
        seen_entries[ec["id"]] = ec

    glossary_list = sorted(seen_entries.values(), key=lambda x: (x["pillar"], x["zh"]))
    with open(os.path.join(DATA_DIR, "glossary.json"), "w", encoding="utf-8") as f:
        json.dump(glossary_list, f, ensure_ascii=False, indent=2)
    print(f"Extracted glossary: {len(glossary_list)} clean bilingual concepts.")
    return glossary_list


def load_atlas_catalog(name):
    p = os.path.join(ATLAS_DIR, "dist", "catalog-data", f"{name}.js")
    with open(p, encoding="utf-8") as f:
        s = f.read()
    m = re.search(r"window\.atlasRegister\((\{.*\})\)", s, re.S)
    obj = json.loads(m.group(1))
    return obj.get("records", [])


def parse_raw_subject_types(zh_kv):
    st_dir = os.path.join(GAME_DIR, "in_game", "common", "subject_types")
    pays_map = {
        "subject_pays_vassal": "基础附庸贡赋",
        "subject_pays_fiefdom": "封地贡赋",
        "subject_pays_march": "边疆伯爵领（减免贡赋）",
        "subject_pays_tributary": "朝贡贡金",
        "subject_pays_colonial_nation": "殖民领税收上缴",
        "subject_pays_dominion": "自治领税费",
        "subject_pays_pronoia": "普罗尼亚军赋",
        "subject_pays_appanage": "王室采邑贡赋",
        "subject_pays_samanta": "萨曼塔藩属贡赋",
        "subject_pays_hanseatic_member": "汉萨成员贸易分红",
    }
    records = []
    for fn in sorted(os.listdir(st_dir)):
        if not fn.endswith(".txt") or fn == "readme.txt":
            continue
        p = os.path.join(st_dir, fn)
        with open(p, encoding="utf-8-sig", errors="ignore") as f:
            txt = f.read()
        i = 0
        while i < len(txt):
            m = re.search(r"([a-zA-Z0-9_]+)\s*=\s*\{", txt[i:])
            if not m:
                break
            key = m.group(1)
            brace_idx = i + m.end() - 1
            line_start = txt.rfind("\n", 0, i + m.start()) + 1
            if txt[line_start:i + m.start()].strip() != "":
                i = brace_idx + 1
                continue
            depth = 0
            j = brace_idx
            while j < len(txt):
                if txt[j] == "{":
                    depth += 1
                elif txt[j] == "}":
                    depth -= 1
                    if depth == 0:
                        break
                j += 1
            block = txt[brace_idx + 1:j]
            i = j + 1

            def get_val(k, default="—"):
                mm = re.search(rf"^\s*{k}\s*=\s*([^\s#\{{]+)", block, re.M)
                return mm.group(1) if mm else default

            zh_name = zh_kv.get(key) or zh_kv.get(f"{key}_name") or key
            pays_key = get_val("subject_pays", "无/特殊")
            annex_spd = get_val("annexation_speed", "0")
            can_annex = "可吞并" if annex_spd not in ("0", "0.0", "—") else "不可直接吞并"
            records.append({
                "id": key,
                "zh": zh_name,
                "en": key.replace("_", " ").title(),
                "level": get_val("level"),
                "subject_pays": pays_map.get(pays_key, pays_key.replace("subject_pays_", "")),
                "diplo_cost_scale": get_val("diplomatic_capacity_cost_scale", "1.0"),
                "strength_vs_overlord": get_val("strength_vs_overlord", "0"),
                "same_ruler": "是" if get_val("has_overlords_ruler", "no") == "yes" else "否",
                "can_annex": can_annex,
                "annex_speed": annex_spd,
                "annex_min_years": get_val("annexation_min_years_before", "—"),
                "annex_min_opinion": get_val("annexation_min_opinion", "—"),
                "source": f"in_game/common/subject_types/{fn}#{key}",
            })
    return records


def extract_ledgers():
    zh_kv = load_yml_kv("simp_chinese")

    with open(os.path.join(ATLAS_DIR, "research", "goods-fields.json"), encoding="utf-8") as f:
        goods_raw = json.load(f)
    src_icons = os.path.join(ATLAS_DIR, "dist", "goods-icons")
    goods = []
    for g in goods_raw:
        icon_name = f"{g['id']}.webp"
        src_p = os.path.join(src_icons, icon_name)
        if os.path.exists(src_p):
            shutil.copy2(src_p, os.path.join(ICONS_DST, icon_name))
        method_zh = {
            "gathering": "采集",
            "farming": "农牧",
            "mining": "采矿",
            "forestry": "林业",
            "hunting": "狩猎",
            "manufacturing": "工坊制造",
        }.get(g.get("method", ""), g.get("method", "—"))
        group_zh = "原材料 (RGO)" if g.get("group") == "raw" else "制成品 (工坊)"
        goods.append({
            "id": g["id"],
            "zh": g["zh"],
            "en": g["en"],
            "group": group_zh,
            "method": method_zh,
            "price": g.get("price", 0),
            "food": g.get("food", 0),
            "transport": g.get("transport", 1),
            "base": g.get("base", 0),
            "icon": f"assets/goods-icons/{icon_name}" if os.path.exists(src_p) else "",
        })

    sv_raw = load_atlas_catalog("societal_values")
    societal_values = []
    for r in sv_raw:
        zh_title = r["zh"].replace("\xa0", " ")
        parts = [p.strip() for p in re.split(r"\s+vs\s+", zh_title, flags=re.I)]
        left_pole = parts[0] if len(parts) > 0 else zh_title
        right_pole = parts[1] if len(parts) > 1 else ""
        detail = r.get("detail", "")
        m_cat = re.match(r"^([^·]+)·\s*([A-Za-z &]+)", detail)
        cat = m_cat.group(1).strip() if m_cat else "通用"
        m_left = re.search(r"左端\s*[−-]100\s*·\s*主要效果\s*(.*?)\s*·\s*右端", detail, re.S)
        m_right = re.search(r"右端\s*\+100\s*·\s*主要效果\s*(.*?)(?:\s*·\s*最早时代|$)", detail, re.S)
        m_era = re.search(r"最早时代与资格\s*(.+)$", detail)
        societal_values.append({
            "id": r["id"],
            "zh": zh_title,
            "en": r["en"],
            "category": cat,
            "left_pole": left_pole,
            "right_pole": right_pole,
            "left_effects": (m_left.group(1).strip().replace("\n", "；") if m_left else ""),
            "right_effects": (m_right.group(1).strip().replace("\n", "；") if m_right else ""),
            "era": (m_era.group(1).strip() if m_era else "第 1 时代"),
        })

    # Fixed indexing: 0=kind, 1=target, 2=cost, 3=effect, 4=cooldown
    ea_raw = load_atlas_catalog("estate_actions")
    estate_actions = []
    for r in ea_raw:
        segs = [x.strip() for x in r.get("detail", "").split("·")]
        estate_actions.append({
            "id": r["id"],
            "zh": r["zh"],
            "en": r["en"],
            "kind": segs[0] if len(segs) > 0 else "",
            "target": segs[1] if len(segs) > 1 else "",
            "cost": segs[2] if len(segs) > 2 else "",
            "effect": segs[3] if len(segs) > 3 else r.get("detail", ""),
            "cooldown": segs[4] if len(segs) > 4 else "无冷却",
            "scope": r.get("scopeLabel", "通用"),
        })
    # Also include sell_work_of_art_to_estates from generic_actions
    if not any(x["id"] == "sell_work_of_art_to_estates" for x in estate_actions):
        estate_actions.append({
            "id": "sell_work_of_art_to_estates",
            "zh": "向阶层出售艺术品",
            "en": "Sell Work of Art to Estates",
            "kind": "阶层互动 / Estate interaction",
            "target": "本国非无价、非帝国御宝且未损毁的艺术品",
            "cost": "永久销毁所选艺术品，失去其威望与文化传统增益",
            "effect": "国库立即获得该艺术品价格 60% 的金币",
            "cooldown": "无独立冷却",
            "scope": "通用 / General",
        })

    ca_raw = load_atlas_catalog("cabinet_actions")
    cabinet_actions = []
    for r in ca_raw:
        segs = [x.strip() for x in r.get("detail", "").split("·")]
        ability_seg = segs[0] if segs else ""
        ability = "ADM" if "行政" in ability_seg else ("DIP" if "外交" in ability_seg else ("MIL" if "军事" in ability_seg else "混合"))
        cabinet_actions.append({
            "id": r["id"],
            "zh": r["zh"],
            "en": r["en"],
            "ability": ability,
            "target": segs[2] if len(segs) > 2 else "",
            "effect": segs[3] if len(segs) > 3 else r.get("detail", ""),
            "scope": "通用" if r.get("scope") == "general" else ("国别/地区" if r.get("scope") == "country" else "特殊解锁"),
            "conditions": r.get("scopeConditions", ""),
        })

    ci_raw = load_atlas_catalog("character_interactions")
    character_interactions = []
    for r in ci_raw:
        character_interactions.append({
            "id": r["id"],
            "zh": r["zh"],
            "en": r["en"],
            "detail": r.get("detail", ""),
            "scope": "通用" if r.get("scope") == "general" else ("国别/文化" if r.get("scope") == "country" else "特殊解锁"),
            "conditions": r.get("scopeConditions", ""),
        })

    st_atlas = {r["id"]: r for r in load_atlas_catalog("subject_types")}
    st_parsed = parse_raw_subject_types(zh_kv)
    subject_types = []
    for item in st_parsed:
        atl = st_atlas.get(item["id"], {})
        item["zh"] = atl.get("zh", item["zh"])
        item["en"] = atl.get("en", item["en"])
        subject_types.append(item)
    seen_st = {x["id"] for x in subject_types}
    for sid, atl in st_atlas.items():
        if sid not in seen_st:
            subject_types.append({
                "id": sid, "zh": atl["zh"], "en": atl["en"], "level": "—",
                "subject_pays": "见细则", "diplo_cost_scale": "—", "strength_vs_overlord": "—",
                "same_ruler": "—", "can_annex": "—", "annex_speed": "—", "annex_min_years": "—",
                "annex_min_opinion": "—", "source": atl.get("source", ""),
            })

    bur_raw = load_atlas_catalog("bureaucracies")
    bureaucracies = [{
        "id": r["id"], "zh": r["zh"], "en": r["en"],
        "detail": re.sub(r"图像\s+[^\s。]+。?", "", r.get("detail", "")).strip(),
        "scope": "通用" if r.get("scope") == "general" else "国别/特殊",
        "conditions": r.get("scopeConditions", ""),
    } for r in bur_raw]

    tr_raw = load_atlas_catalog("town_rights")
    town_rights = []
    for r in tr_raw:
        d = r.get("detail", "")
        d = d.replace("scope:target", "目标地点").replace("is_port 是", "须为港口").replace("has_town_rights ", "已有城市特权 ")
        town_rights.append({
            "id": r["id"], "zh": r["zh"], "en": r["en"],
            "detail": d,
            "scope": "通用" if r.get("scope") == "general" else "国别/特殊",
        })

    cb_raw = load_atlas_catalog("casus_belli")
    casus_belli = []
    for r in cb_raw:
        d = r.get("detail", "")
        d = d.replace("war_goal_type ", "战争目标：").replace("no_cb 是。", "无宣战理由（高稳耗/高敌意）。").replace("allow_release_areas 是", "允许和约释放地区")
        casus_belli.append({
            "id": r["id"], "zh": r["zh"], "en": r["en"],
            "detail": d.strip(),
            "scope": "通用" if r.get("scope") == "general" else "局势/特殊",
        })

    def clean_ev(s):
        s = re.sub(r"图像\s+[^\s。]+。?", "", s)
        s = re.sub(r"content_priority\s+\d+。?", "", s)
        s = re.sub(r"is_content_highlighted\s+是。?", "", s)
        s = re.sub(r"monthly_spawn_chance\s+([0-9.]+)", r"每月触发检定权重 \1", s)
        return s.replace("fire_only_once 是。", "单局仅触发一次。").strip()

    situations = [{
        "id": r["id"], "zh": r["zh"], "en": r["en"], "kind": "历史局势",
        "scope": "通用" if r.get("scope") == "general" else "特定触发",
        "detail": clean_ev(r.get("detail", "")),
    } for r in load_atlas_catalog("situations")]

    disasters = [{
        "id": r["id"], "zh": r["zh"], "en": r["en"], "kind": "国家灾难",
        "scope": "通用" if r.get("scope") == "general" else "特定触发",
        "detail": clean_ev(r.get("detail", "")),
    } for r in load_atlas_catalog("disasters")]

    ledgers = {
        "goods": goods,
        "societal_values": societal_values,
        "estate_actions": estate_actions,
        "cabinet_actions": cabinet_actions,
        "character_interactions": character_interactions,
        "subject_types": subject_types,
        "bureaucracies": bureaucracies,
        "town_rights": town_rights,
        "casus_belli": casus_belli,
        "situations": situations,
        "disasters": disasters,
    }
    with open(os.path.join(DATA_DIR, "ledgers.json"), "w", encoding="utf-8") as f:
        json.dump(ledgers, f, ensure_ascii=False, indent=2)
    print("Extracted clean ledgers:", {k: len(v) for k, v in ledgers.items()})
    return ledgers


class _AtlasTbodyParser(HTMLParser):
    """Parse structured tbody row pairs (summary row + detail dl row) from eu5-atlas HTML tables."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.tbodies = []
        self._in_tbody = False
        self._in_tr = False
        self._cell_tag = None
        self._in_cell = False
        self._in_dt = False
        self._in_dd = False
        self._in_b = False
        self._in_small_en = False
        self._in_scope_badge = False
        self._skip_toggle = False
        self._cur_tbody = None
        self._cur_tr = None
        self._cur_cell = None
        self._cur_dt = []
        self._cur_dd = []

    def handle_starttag(self, tag, attrs):
        ad = dict(attrs)
        if tag == "tbody":
            self._in_tbody = True
            self._cur_tbody = []
        elif self._in_tbody and tag == "tr":
            self._in_tr = True
            self._cur_tr = {"cells": [], "details": []}
        elif self._in_tr and tag in ("th", "td"):
            self._cell_tag = tag
            self._in_cell = True
            self._cur_cell = {
                "tag": tag,
                "field": ad.get("data-field", ""),
                "value": ad.get("data-value", ""),
                "id": "",
                "zh": [],
                "en": [],
                "scope": [],
                "parts": [],
            }
        elif self._in_cell:
            cls = ad.get("class", "")
            if tag == "button" and "dir-item" in cls:
                ctrl = ad.get("aria-controls", "")
                if ctrl.startswith("detail-"):
                    self._cur_cell["id"] = ctrl[len("detail-"):]
            elif tag == "b" and self._cell_tag == "th":
                self._in_b = True
            elif tag == "small" and (ad.get("lang") == "en" or "dir-cell-en" in cls):
                self._in_small_en = True
                if "dir-cell-en" in cls:
                    self._cur_cell["parts"].append(" · ")
            elif tag == "span" and "scope-badge" in cls:
                self._in_scope_badge = True
            elif tag == "span" and "dir-toggle" in cls:
                self._skip_toggle = True
            elif tag == "br":
                self._cur_cell["parts"].append(" / ")
            elif tag == "dt":
                self._in_dt = True
                self._cur_dt = []
            elif tag == "dd":
                self._in_dd = True
                self._cur_dd = []

    def handle_endtag(self, tag):
        if tag == "dt" and self._in_dt:
            self._in_dt = False
        elif tag == "dd" and self._in_dd:
            self._in_dd = False
            k = re.sub(r"\s+", " ", "".join(self._cur_dt)).strip()
            v = re.sub(r"\s+", " ", "".join(self._cur_dd)).strip()
            if k or v:
                self._cur_tr["details"].append([k, v])
        elif tag == "b" and self._in_b:
            self._in_b = False
        elif tag == "small" and self._in_small_en:
            self._in_small_en = False
        elif tag == "span":
            if self._in_scope_badge:
                self._in_scope_badge = False
            if self._skip_toggle:
                self._skip_toggle = False
        elif self._in_cell and tag == self._cell_tag:
            self._in_cell = False
            self._cell_tag = None
            self._cur_tr["cells"].append(self._cur_cell)
        elif self._in_tr and tag == "tr":
            self._in_tr = False
            self._cur_tbody.append(self._cur_tr)
        elif self._in_tbody and tag == "tbody":
            self._in_tbody = False
            self.tbodies.append(self._cur_tbody)

    def handle_data(self, data):
        if not self._in_cell or self._skip_toggle:
            return
        if self._in_dt:
            self._cur_dt.append(data)
            return
        if self._in_dd:
            self._cur_dd.append(data)
            return
        if self._in_b:
            self._cur_cell["zh"].append(data)
        elif self._in_small_en and self._cell_tag == "th":
            self._cur_cell["en"].append(data)
        elif self._in_scope_badge:
            self._cur_cell["scope"].append(data)
        else:
            self._cur_cell["parts"].append(data)


RICH_TABLE_SPECS = [
    ("building_types", "buildings.html", ["group", "price", "jobs", "employees", "time", "ranks", "output"]),
    ("unit_types", "military-units.html", ["category", "age", "unit_type", "troops", "combat_power", "cannons", "hull", "build_time"]),
    ("estate_privileges", "estate-privileges.html", ["estate", "power_mod", "sat_eq", "effects"]),
    ("laws", "laws.html", ["category", "target_scope", "policies_count", "impl_times", "groups"]),
    ("government_reforms", "government-reforms.html", ["age", "government", "societal_req", "impl_years", "effects"]),
    ("government_types", "government-types.html", ["gov_power", "default_estate", "heir_count", "noble_marriage", "gen_consorts"]),
    ("road_types", "roads.html", ["level", "cost", "time", "move_cost", "market_cost", "prox_red"]),
    ("industry_types", "industries.html", ["goods", "area_out", "pop_demand", "grant_cost"]),
    ("diplomatic_actions", "diplomatic-actions.html", ["kind", "cost", "acceptance", "effect"]),
    ("international_organizations", "international-organizations-table.html", ["group", "membership", "leadership", "instances", "war", "effects"]),
    ("religions", "religions.html", ["group", "liturgical", "aspect_slots", "mechanics", "effects"]),
    ("wargoals", "war-goals.html", ["goal_type", "ticking", "conquest_fac", "subjugation_fac", "antagonism_fac"]),
]


def _clean_cell_text(cell):
    txt = "".join(cell["parts"]).strip()
    txt = re.sub(r"\s+", " ", txt).strip()
    txt = re.sub(r"\s*·\s*$", "", txt).strip()
    return txt


def extract_rich_ledgers_and_catalogs(base_ledgers):
    # 1. Extract all 12 rich tables from eu5-atlas HTML and verify 1-to-1 length with catalog-data
    rich_tables = {}
    for cid, html_name, field_names in RICH_TABLE_SPECS:
        html_path = os.path.join(ATLAS_DIR, "dist", html_name)
        with open(html_path, encoding="utf-8") as f:
            raw_html = f.read()
        parser = _AtlasTbodyParser()
        parser.feed(raw_html)
        cat_recs = load_atlas_catalog(cid)
        if len(parser.tbodies) != len(cat_recs):
            raise RuntimeError(f"Row mismatch for {cid}: HTML tbodies={len(parser.tbodies)} vs catalog={len(cat_recs)}")
        rows = []
        for idx, tb in enumerate(parser.tbodies):
            cat_rec = cat_recs[idx]
            r0 = tb[0] if tb else {"cells": []}
            r1 = tb[1] if len(tb) > 1 else {"details": []}
            c0 = r0["cells"][0] if r0["cells"] else {}
            rid = c0.get("id") or cat_rec["id"]
            zh = re.sub(r"\s+", " ", "".join(c0.get("zh", []))).strip() or cat_rec.get("zh", rid)
            en = re.sub(r"\s+", " ", "".join(c0.get("en", []))).strip() or cat_rec.get("en", rid)
            scope = re.sub(r"\s+", " ", "".join(c0.get("scope", []))).strip() or cat_rec.get("scopeLabel", "通用 / General")
            item = {
                "id": rid,
                "zh": zh,
                "en": en,
                "scope": scope,
                "scope_code": cat_rec.get("scope", "general"),
                "scopeConditions": cat_rec.get("scopeConditions", ""),
                "source": cat_rec.get("source", ""),
                "detail": cat_rec.get("detail", ""),
                "detail_pairs": r1.get("details", []),
            }
            data_cells = r0["cells"][1:]
            num_map = {}
            for col_i, fname in enumerate(field_names):
                cell = data_cells[col_i] if col_i < len(data_cells) else {"parts": [], "value": ""}
                item[fname] = _clean_cell_text(cell) or "—"
                if cell.get("value") not in (None, ""):
                    try:
                        num_map[fname] = float(cell["value"])
                    except ValueError:
                        pass
            if num_map:
                item["_num"] = num_map
            rows.append(item)
        rich_tables[cid] = rows
        print(f"Parsed rich HTML table {cid}: {len(rows)} rows (1:1 verified)")

    # 2. Prepare combined 22 modular ledger JS files under docs/assets/ledgers/<id>.js
    situ_combined = list(base_ledgers.get("situations", [])) + list(base_ledgers.get("disasters", []))
    all_22_ledgers = {
        "building_types": rich_tables["building_types"],
        "goods": base_ledgers["goods"],
        "unit_types": rich_tables["unit_types"],
        "estate_privileges": rich_tables["estate_privileges"],
        "laws": rich_tables["laws"],
        "government_reforms": rich_tables["government_reforms"],
        "government_types": rich_tables["government_types"],
        "road_types": rich_tables["road_types"],
        "industry_types": rich_tables["industry_types"],
        "societal_values": base_ledgers["societal_values"],
        "estate_actions": base_ledgers["estate_actions"],
        "cabinet_actions": base_ledgers["cabinet_actions"],
        "character_interactions": base_ledgers["character_interactions"],
        "bureaucracies": base_ledgers["bureaucracies"],
        "town_rights": base_ledgers["town_rights"],
        "subject_types": base_ledgers["subject_types"],
        "diplomatic_actions": rich_tables["diplomatic_actions"],
        "international_organizations": rich_tables["international_organizations"],
        "casus_belli": base_ledgers["casus_belli"],
        "wargoals": rich_tables["wargoals"],
        "religions": rich_tables["religions"],
        "situations_disasters": situ_combined,
    }
    assert len(all_22_ledgers) == 22, f"Expected 22 ledgers, got {len(all_22_ledgers)}"

    ledger_summary = {}
    for lid, rows in all_22_ledgers.items():
        js_path = os.path.join(LEDGERS_JS_DIR, f"{lid}.js")
        with open(js_path, "w", encoding="utf-8") as f:
            f.write(f"window.__EU5_LEDGER_REGISTER__({json.dumps(lid)}, {json.dumps(rows, ensure_ascii=False)});\n")
        # Save compact search projection (id, zh, en, subtext) for search-index.js builder
        ledger_summary[lid] = [
            {
                "id": r.get("id", ""),
                "zh": r.get("zh", ""),
                "en": r.get("en", ""),
                "sub": (
                    r.get("effect") or r.get("effects") or r.get("group") or r.get("category")
                    or r.get("estate") or r.get("goal_type") or r.get("left_effects")
                    or r.get("detail") or ""
                )[:90],
            }
            for r in rows
        ]

    with open(os.path.join(DATA_DIR, "rich_ledgers_summary.json"), "w", encoding="utf-8") as f:
        json.dump(ledger_summary, f, ensure_ascii=False)
    print(f"Exported 22 lazy ledger bundles to docs/assets/ledgers/ (total rows={sum(len(v) for v in all_22_ledgers.values())})")

    # 3. Export all 72 catalogs (23,216 records) into docs/assets/catalogs/<id>.js
    cm_path = os.path.join(ATLAS_DIR, "dist", "catalog-manifest.js")
    with open(cm_path, encoding="utf-8") as f:
        cm_txt = f.read()
    manifest = json.loads(re.search(r"window\.catalogueManifest\s*=\s*(\[.*\])", cm_txt, re.S).group(1))

    pillar_assign = {
        "location_ranks": "geography", "topography": "geography", "vegetation": "geography",
        "climates": "geography", "diseases": "geography", "road_types": "geography",
        "building_types": "economy", "recipes": "economy", "goods": "economy",
        "industry_types": "economy", "town_rights": "economy", "populations": "economy",
        "government_types": "politics", "government_reforms": "politics", "laws": "politics",
        "law-options": "politics", "bureaucracies": "politics", "cabinet_actions": "politics",
        "societal_values": "politics", "estate_actions": "politics", "estate_privileges": "politics",
        "heir_selections": "politics", "character_interactions": "politics", "child_educations": "politics",
        "traits": "politics", "parliament_types": "politics", "parliament_agendas": "politics",
        "parliament_issues": "politics", "rebel_demands": "politics", "movements": "politics",
        "cultures": "culture", "languages": "culture", "religions": "culture",
        "religious_aspects": "culture", "religious_schools": "culture", "religious_focuses": "culture",
        "religious_order_types": "culture", "religious_order_callings": "culture",
        "gods": "culture", "holy_sites": "culture", "artist_work": "culture",
        "historical-art": "culture", "event-art": "culture", "chivalric_orders": "culture",
        "age": "culture", "institution": "culture", "advances": "culture",
        "expedition_types": "culture", "colonial_charter_goals": "culture",
        "unit_types": "military", "unit_abilities": "military", "casus_belli": "military",
        "wargoals": "military", "peace_treaties": "military",
        "diplomatic_actions": "diplomacy", "country_interactions": "diplomacy",
        "subject_types": "diplomacy", "international_organizations": "diplomacy",
        "resolutions": "diplomacy",
        "starting-scenarios": "world", "starting-country-regions": "world",
        "regional-countries": "world", "country-definitions": "world",
        "formable-countries": "world", "situations": "world", "disasters": "world",
        "decisions": "world", "missions": "world", "country-events": "world",
        "achievements": "world", "game_rules": "world", "encyclopedia": "world", "wiki-concepts": "world",
    }

    ledger_map = {
        "building_types": "building_types", "goods": "goods", "unit_types": "unit_types",
        "estate_privileges": "estate_privileges", "laws": "laws",
        "government_reforms": "government_reforms", "government_types": "government_types",
        "road_types": "road_types", "industry_types": "industry_types",
        "societal_values": "societal_values", "estate_actions": "estate_actions",
        "cabinet_actions": "cabinet_actions", "character_interactions": "character_interactions",
        "bureaucracies": "bureaucracies", "town_rights": "town_rights",
        "subject_types": "subject_types", "diplomatic_actions": "diplomatic_actions",
        "international_organizations": "international_organizations",
        "casus_belli": "casus_belli", "wargoals": "wargoals", "religions": "religions",
        "situations": "situations_disasters", "disasters": "situations_disasters",
    }

    total_cat_recs = 0
    manifest_out = []
    for entry in manifest:
        cid = entry["id"]
        src_js = os.path.join(ATLAS_DIR, "dist", "catalog-data", f"{cid}.js")
        with open(src_js, encoding="utf-8") as f:
            raw_js = f.read()
        obj = json.loads(re.search(r"window\.atlasRegister\((\{.*\})\)", raw_js, re.S).group(1))
        recs = obj.get("records", [])
        total_cat_recs += len(recs)

        dst_js = os.path.join(CATALOGS_JS_DIR, f"{cid}.js")
        with open(dst_js, "w", encoding="utf-8") as f:
            f.write(f"window.__EU5_CATALOG_REGISTER__({json.dumps(cid)}, {json.dumps(obj, ensure_ascii=False)});\n")

        m_item = {
            "id": cid,
            "zh": entry["zh"],
            "en": entry["en"],
            "count": len(recs),
            "pillar": pillar_assign.get(cid, "world"),
        }
        if cid in ledger_map:
            m_item["ledger"] = ledger_map[cid]
        manifest_out.append(m_item)

    with open(os.path.join(DATA_DIR, "catalog_manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest_out, f, ensure_ascii=False, indent=2)
    with open(os.path.join(ASSETS_DIR, "catalog-manifest.js"), "w", encoding="utf-8") as f:
        f.write("window.__EU5_CATALOG_MANIFEST__ = " + json.dumps(manifest_out, ensure_ascii=False) + ";\n")
    print(f"Exported {len(manifest_out)} modular catalogs to docs/assets/catalogs/ (total records={total_cat_recs})")

    # 4. Export Population Goods Demand Matrix (8 classes x 75 goods = 600 rows)
    pd_src = os.path.join(ATLAS_DIR, "dist", "pop-demand-data.json")
    with open(pd_src, encoding="utf-8") as f:
        pd = json.load(f)
    total_pd_rows = 0
    pd_summary = []
    for cls_obj in pd.get("classes", []):
        non_zero = 0
        for row in cls_obj.get("rows", []):
            icon_p = os.path.join(ICONS_DST, f"{row['id']}.webp")
            row["icon"] = f"assets/goods-icons/{row['id']}.webp" if os.path.exists(icon_p) else ""
            if (row.get("baseDemand") or 0) > 0 or (row.get("classBaseDemand") or 0) > 0:
                non_zero += 1
        total_pd_rows += len(cls_obj.get("rows", []))
        pd_summary.append({
            "id": cls_obj["id"],
            "zh": cls_obj["zh"],
            "en": cls_obj["en"],
            "upper": cls_obj.get("upper", False),
            "total": len(cls_obj.get("rows", [])),
            "non_zero": non_zero,
        })

    with open(os.path.join(ASSETS_DIR, "pop-demand-data.js"), "w", encoding="utf-8") as f:
        f.write("window.__EU5_POP_DEMAND__ = " + json.dumps(pd, ensure_ascii=False) + ";\n")
    with open(os.path.join(DATA_DIR, "pop_demand_summary.json"), "w", encoding="utf-8") as f:
        json.dump(pd_summary, f, ensure_ascii=False, indent=2)
    print(f"Exported pop-demand-data.js ({len(pd.get('classes', []))} classes, {total_pd_rows} total rows)")

    # 5. Export compact Version Update data (1.4.8 -> 1.4.9) for Chapter 12
    vu_src = os.path.join(ATLAS_DIR, "dist", "version-update-data.json")
    with open(vu_src, encoding="utf-8") as f:
        vu = json.load(f)
    manifest_zh = {m["id"]: m["zh"] for m in manifest_out}
    vu_clean = {
        "version": vu.get("version"),
        "officialChecksum": vu.get("officialChecksum"),
        "date": vu.get("date"),
        "steamBuild": vu.get("steamBuild"),
        "previous": vu.get("previous"),
        "checks": vu.get("checks", []),
        "tableChanges": [
            {
                "id": tc.get("id"),
                "zh": tc.get("zh") or manifest_zh.get(tc.get("id", ""), tc.get("id", "")),
                "total": tc.get("count", tc.get("total", 0)),
                "changed_count": len(tc.get("changed", [])) if isinstance(tc.get("changed"), list) else tc.get("changed", 0),
                "changed": tc.get("changed", [])[:10] if isinstance(tc.get("changed"), list) else [],
            }
            for tc in vu.get("tableChanges", [])
        ],
        "unresolved": vu.get("unresolved", []),
    }
    with open(os.path.join(DATA_DIR, "version_update.json"), "w", encoding="utf-8") as f:
        json.dump(vu_clean, f, ensure_ascii=False, indent=2)
    print(f"Exported version_update.json ({len(vu_clean['checks'])} checks, {len(vu_clean['tableChanges'])} tableChanges)")


if __name__ == "__main__":
    defs = parse_defines()
    extract_glossary(defs)
    base_ledgers = extract_ledgers()
    extract_rich_ledgers_and_catalogs(base_ledgers)
