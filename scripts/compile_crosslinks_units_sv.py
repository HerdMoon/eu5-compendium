# -*- coding: utf-8 -*-
"""
Compiler for:
1. Global Entity Cross-Link Dictionary (docs/assets/entity-links.js)
2. 17 Societal Values Full Effects & Non-Event Drift Sources (docs/assets/ledgers/societal_values.js + data/societal_drift.json)
3. 401 Military Units Age Progression Matrix & Unique-vs-Base Stat Deltas (docs/assets/units-data.js + docs/assets/ledgers/unit_types.js)
"""
import collections
import json
import os
import re
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)

from extract_game_data import load_yml_kv
from humanize_data import (
    GROUP_LABELS_ZH,
    build_metrics_bundle,
    clean_source_zh,
    format_item_modifiers,
    humanize_condition,
    load_game_context,
    load_metric_sources,
    resolve_source_href,
)

PROJ_DIR = os.path.dirname(SCRIPT_DIR)
DATA_DIR = os.path.join(PROJ_DIR, "data")
DOCS_DIR = os.path.join(PROJ_DIR, "docs")
ASSETS_DIR = os.path.join(DOCS_DIR, "assets")
LEDGERS_DIR = os.path.join(ASSETS_DIR, "ledgers")
CATALOGS_DIR = os.path.join(ASSETS_DIR, "catalogs")


def _read_ledger_js(lid):
    p = os.path.join(LEDGERS_DIR, f"{lid}.js")
    txt = open(p, encoding="utf-8").read()
    return json.loads(txt[txt.index("["):txt.rindex("]") + 1])


def _write_ledger_js(lid, arr):
    p = os.path.join(LEDGERS_DIR, f"{lid}.js")
    with open(p, "w", encoding="utf-8") as f:
        f.write(f"window.__EU5_LEDGER_REGISTER__({json.dumps(lid)}, {json.dumps(arr, ensure_ascii=False)});\n")


def _read_catalog_js(cid):
    p = os.path.join(CATALOGS_DIR, f"{cid}.js")
    txt = open(p, encoding="utf-8").read()
    start = txt.find(", ") + 2
    end = txt.rfind(");")
    return json.loads(txt[start:end])


# Generic everyday/mechanic terms that must NOT be auto-linked unquoted in free prose
INLINE_STOPWORDS = {
    "发展", "发展度", "繁荣", "繁荣度", "控制", "控制力", "最大控制力", "邻近度",
    "稳定", "稳定度", "正统", "正统性", "共和传统", "奉献度", "游牧团结", "部落凝聚力",
    "威望", "敌意", "信任", "好感", "人情", "忠诚", "忠诚度", "满意度", "识字率",
    "人口", "人口容量", "市场", "贸易", "商业", "农业", "工业", "林业", "采矿", "财政", "税收",
    "城市", "集镇", "乡村", "农村", "大都市", "聚落", "省份", "地区", "区域", "大陆", "次大陆", "首都",
    "港口", "海岸", "沿海", "内陆", "河流", "海峡", "大洋", "深洋", "内海",
    "山地", "丘陵", "高原", "平原", "森林", "疏林", "丛林", "湿地", "沼泽", "沙漠", "荒原", "农田", "草地", "极地",
    "陆军", "海军", "步兵", "骑兵", "炮兵", "重步兵", "轻步兵", "重骑兵", "轻骑兵", "辅助兵",
    "重型战舰", "轻型战舰", "桨帆战舰", "运输船", "常备军", "征召兵", "雇佣兵", "私掠者",
    "贵族", "教士", "市民", "农民", "平民", "劳工", "士兵", "奴隶", "部落", "部落民", "齐米", "哥萨克", "王室",
    "内阁", "议会", "法律", "政策", "改革", "特权", "思潮", "革新", "时代",
    "传统", "文艺复兴", "地理大发现", "宗教改革", "专制主义", "大革命", "革命时代",
    "进攻", "防御", "质量", "数量", "创新", "守旧", "人文", "属灵", "陆权", "海权", "好战", "亲善", "外向", "内向",
    "同盟", "保障独立", "军事通行权", "战争", "和平", "独立", "吞并", "殖民", "探索", "附庸", "朝贡",
    "君主制", "君主国", "共和制", "共和国", "神权制", "神权国", "草原游牧", "部落制",
    "天主教", "东正教", "新教", "伊斯兰教", "佛教", "印度教",
    "训练度", "军事战术", "士气", "主动性", "要塞", "补给", "人力", "水手", "海上存在",
}


def build_entity_links():
    """Compile exact (quoted/prefixed) and inline (unquoted) cross-link maps."""
    exact = {}
    inline = {}
    goods1 = {}

    def add_ent(zh, href, kind, allow_inline=True, min_inline_len=2):
        if not zh or not href:
            return
        zh = zh.strip()
        if not re.search(r"[\u4e00-\u9fff]", zh):
            return
        # Clean bilingual suffixes if any
        zh_base = zh.split(" / ")[0].strip()
        for cand in (zh_base,):
            if not cand:
                continue
            if cand not in exact:
                exact[cand] = [href, kind]
            if allow_inline and cand not in INLINE_STOPWORDS:
                if len(cand) >= min_inline_len and cand not in inline:
                    inline[cand] = [href, kind]

    # 1. Goods (highest priority! Handle 1-char goods via goods1 + common aliases)
    goods_rows = _read_ledger_js("goods")
    goods_id_map = {}
    for g in goods_rows:
        gid = g["id"]
        gzh = g["zh"].strip()
        href = f"ledgers.html#goods?id={gid}"
        goods_id_map[gid] = (gzh, href)
        exact[gzh] = [href, "商品"]
        if len(gzh) == 1:
            goods1[gzh] = [href, "商品"]
        elif gzh not in INLINE_STOPWORDS:
            inline[gzh] = [href, "商品"]

    goods_aliases = {
        "木材": "lumber", "原木": "lumber",
        "布匹": "cloth", "布料": "cloth",
        "黄金": "goods_gold", "金矿": "goods_gold",
        "白银": "silver", "银矿": "silver",
        "武器": "weaponry", "军械": "weaponry",
        "纸张": "paper", "书籍": "books",
        "战马": "horses", "马匹": "horses",
        "火炮": "cannons", "大炮": "cannons",
        "药材": "medicaments", "药物": "medicaments",
        "石料": "stone", "石材": "stone",
        "谷物": "wheat", "小麦": "wheat",
        "稻米": "rice", "牲畜": "livestock", "家畜": "livestock",
        "鱼类": "fish", "铁矿": "iron", "铜矿": "copper",
    }
    for alias, gid in goods_aliases.items():
        if gid in goods_id_map:
            _, href = goods_id_map[gid]
            exact.setdefault(alias, [href, "商品"])
            if len(alias) >= 2 and alias not in INLINE_STOPWORDS:
                inline.setdefault(alias, [href, "商品"])

    # 2. Buildings (501)
    for b in _read_ledger_js("building_types"):
        add_ent(b["zh"], f"ledgers.html#building_types?id={b['id']}", "建筑", allow_inline=True, min_inline_len=2)

    # 3. Military Units (non-template -> units.html#<id>)
    for u in _read_ledger_js("unit_types"):
        if u.get("unit_type") == "模板 · Template":
            continue
        add_ent(u["zh"], f"units.html#{u['id']}", "军事单位", allow_inline=True, min_inline_len=2)

    # 4. Estate Privileges (331)
    for p in _read_ledger_js("estate_privileges"):
        add_ent(p["zh"], f"ledgers.html#estate_privileges?id={p['id']}", "阶层特权", allow_inline=True, min_inline_len=3)

    # 5. Government Reforms (379)
    for r in _read_ledger_js("government_reforms"):
        add_ent(r["zh"], f"ledgers.html#government_reforms?id={r['id']}", "政府改革", allow_inline=True, min_inline_len=3)

    # 6. Laws (213) & Law Policies (832)
    for lw in _read_ledger_js("laws"):
        add_ent(lw["zh"], f"ledgers.html#laws?id={lw['id']}", "法律", allow_inline=True, min_inline_len=3)
    for pol in _read_catalog_js("law-options").get("records", []):
        add_ent(pol["zh"], f"directory.html#law-options?id={pol['id']}", "法律政策", allow_inline=True, min_inline_len=3)

    # 7. Bureaucracies (60), Town Rights (75), Cabinet Actions (81), Estate Actions (12), Roads (4)
    for b in _read_ledger_js("bureaucracies"):
        add_ent(b["zh"], f"ledgers.html#bureaucracies?id={b['id']}", "官僚机构", allow_inline=True, min_inline_len=2)
    for tr in _read_ledger_js("town_rights"):
        add_ent(tr["zh"], f"ledgers.html#town_rights?id={tr['id']}", "城镇特权", allow_inline=True, min_inline_len=3)
    for ca in _read_ledger_js("cabinet_actions"):
        add_ent(ca["zh"], f"ledgers.html#cabinet_actions?id={ca['id']}", "内阁行动", allow_inline=True, min_inline_len=3)
    for ea in _read_ledger_js("estate_actions"):
        add_ent(ea["zh"], f"ledgers.html#estate_actions?id={ea['id']}", "阶层互动", allow_inline=True, min_inline_len=3)
    for rd in _read_ledger_js("road_types"):
        add_ent(rd["zh"], f"ledgers.html#road_types?id={rd['id']}", "道路", allow_inline=True, min_inline_len=3)

    # 8. Societal Values (17 axes + unambiguous poles)
    for sv in _read_ledger_js("societal_values"):
        href = f"ledgers.html#societal_values?id={sv['id']}"
        add_ent(sv["zh"], href, "社会价值观", allow_inline=True, min_inline_len=4)
        for pole in (sv.get("left_pole", ""), sv.get("right_pole", "")):
            if pole:
                exact.setdefault(pole, [href, "价值观极点"])
                if len(pole) >= 3 and pole not in INLINE_STOPWORDS:
                    inline.setdefault(pole, [href, "价值观极点"])
                elif pole in ("农奴制", "自由民"):
                    inline.setdefault(pole, [href, "价值观极点"])

    # 9. Subject Types (22), IOs (37), Religions (293), Diseases (8), Recipes (346), Advances (3,592)
    for st in _read_ledger_js("subject_types"):
        add_ent(st["zh"], f"ledgers.html#subject_types?id={st['id']}", "属国类型", allow_inline=True, min_inline_len=3)
    for io in _read_ledger_js("international_organizations"):
        add_ent(io["zh"], f"ledgers.html#international_organizations?id={io['id']}", "国际组织", allow_inline=True, min_inline_len=3)
    for rel in _read_ledger_js("religions"):
        add_ent(rel["zh"], f"ledgers.html#religions?id={rel['id']}", "宗教", allow_inline=True, min_inline_len=3)
    for dis in _read_catalog_js("diseases").get("records", []):
        add_ent(dis["zh"], f"directory.html#diseases?id={dis['id']}", "疫病", allow_inline=True, min_inline_len=2)
    for rec in _read_catalog_js("recipes").get("records", []):
        add_ent(rec["zh"], f"directory.html#recipes?id={rec['id']}", "生产配方", allow_inline=False)
    for adv in _read_catalog_js("advances").get("records", []):
        # All 3,592 advances go into `exact` (matched in 《...》/「...」 or after 解锁革新/前置革新),
        # and >=4-char specific advances go into `inline`
        add_ent(adv["zh"], f"directory.html#advances?id={adv['id']}", "时代革新", allow_inline=True, min_inline_len=4)

    out_obj = {"exact": exact, "inline": inline, "goods1": goods1}
    out_path = os.path.join(ASSETS_DIR, "entity-links.js")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("window.__EU5_ENTITY_LINKS__ = " + json.dumps(out_obj, ensure_ascii=False) + ";\n")
    print(f"Exported entity-links.js: exact={len(exact)}, inline={len(inline)}, goods1={len(goods1)}")
    return out_obj


def compile_societal_values_drift(ms, mods_by_item, clean_zh_kv, game_ctx):
    """Enrich all 17 societal_values rows with full pole modifiers + complete non-event drift sources."""
    sv_rows = _read_ledger_js("societal_values")
    game_sv_path = r"D:\SteamLibrary\steamapps\common\Europa Universalis V\game\in_game\common\societal_values\00_default.txt"
    raw_sv_txt = open(game_sv_path, encoding="utf-8-sig", errors="ignore").read()

    # Parse left_modifier and right_modifier keys per axis from 00_default.txt to split mods_by_item cleanly
    def extract_pole_mod_keys(axis_id, block_name):
        m = re.search(rf"{re.escape(axis_id)}\s*=\s*\{{(.*?)(?:\n[a-z_]+_vs_[a-z_]+\s*=|\Z)", raw_sv_txt, re.S)
        if not m:
            return set()
        body = m.group(1)
        mb = re.search(rf"{block_name}\s*=\s*\{{([^}}]*)\}}", body, re.S)
        if not mb:
            return set()
        keys = set()
        for ln in mb.group(1).splitlines():
            ln = ln.split("#", 1)[0].strip()
            if "=" in ln:
                keys.add(ln.split("=", 1)[0].strip())
        return keys

    def collect_push_sources(mod_key):
        minfo = ms.get(mod_key, {})
        grouped = collections.defaultdict(list)
        seen = collections.defaultdict(set)
        for s in minfo.get("sources", []):
            g_zh = GROUP_LABELS_ZH.get(s["group"], s["group"])
            disp = s["display"]
            cond = humanize_condition(s.get("condition", ""), clean_zh_kv, game_ctx)
            for boring in ("持有这项阶层特权时", "采用这项政府改革时", "研发这项革新后", "机构的常规修正"):
                if cond == boring:
                    cond = ""
            cond_s = cond[:95]
            szh = clean_source_zh(s["zh"])
            sig = (szh, disp, cond_s)
            if sig in seen[g_zh]:
                continue
            seen[g_zh].add(sig)
            entry = {"zh": szh, "val": disp, "cond": cond_s}
            href = resolve_source_href(s["group"], s.get("id", ""))
            if href:
                entry["href"] = href
            grouped[g_zh].append(entry)

        # Order groups by practical gameplay importance
        priority = [
            "内阁行动", "阶层属性", "国家自动修正", "基础状态与环境修正", "属国类型", "社会价值观",
            "建筑", "官僚机构", "法律政策", "阶层特权", "政府改革",
            "宗教信条", "宗教学派", "时代革新", "议会议案", "议会制度", "国际组织", "人物特质", "摄政状态",
        ]
        ordered = []
        for g in priority:
            if g in grouped:
                ordered.append([g, grouped[g], len(grouped[g])])
        for g, items in grouped.items():
            if g not in priority:
                ordered.append([g, items, len(items)])
        return ordered, sum(len(v) for v in grouped.values())

    def summarize_pushes(push_groups):
        parts = []
        for gname, items, cnt in push_groups:
            if gname in ("人物特质", "摄政状态") and len(parts) >= 4:
                continue
            sample = "、".join(f"{it['zh']}({it['val']})" for it in items[:3])
            if cnt > 3:
                sample += f" 等{cnt}项"
            parts.append(f"{gname}：{sample}")
        return " ｜ ".join(parts[:5]) if parts else "主要由通用外交内阁行动「改变社会价值观」(+0.10/月×内阁倍率)推动"

    drift_summary = []
    for row in sv_rows:
        sv_id = row["id"]
        left_k, _, right_k = sv_id.partition("_vs_")
        left_mod_keys = extract_pole_mod_keys(sv_id, "left_modifier")
        right_mod_keys = extract_pole_mod_keys(sv_id, "right_modifier")

        all_sv_mods = mods_by_item.get(("societal_values", sv_id), [])
        # Filter strictly by pole name in condition ("向<left_pole>一端移动时") and skip AI importance/bias noise
        real_left = [
            m for m in all_sv_mods
            if row["left_pole"] in m.get("condition", "") and "importance" not in m["mod_key"] and "bias_for" not in m["mod_key"]
        ]
        real_right = [
            m for m in all_sv_mods
            if row["right_pole"] in m.get("condition", "") and "importance" not in m["mod_key"] and "bias_for" not in m["mod_key"]
        ]
        if real_left:
            row["left_effects"] = format_item_modifiers(real_left, max_items=12)
        if real_right:
            row["right_effects"] = format_item_modifiers(real_right, max_items=12)

        l_groups, l_total = collect_push_sources(f"monthly_towards_{left_k}")
        r_groups, r_total = collect_push_sources(f"monthly_towards_{right_k}")

        row["left_push_key"] = f"monthly_towards_{left_k}"
        row["right_push_key"] = f"monthly_towards_{right_k}"
        row["left_push_total"] = l_total
        row["right_push_total"] = r_total
        row["left_pushes"] = l_groups
        row["right_pushes"] = r_groups
        row["left_push_summary"] = summarize_pushes(l_groups)
        row["right_push_summary"] = summarize_pushes(r_groups)

        drift_summary.append({
            "id": sv_id,
            "zh": row["zh"],
            "era": row["era"],
            "left_pole": row["left_pole"],
            "right_pole": row["right_pole"],
            "left_effects": row["left_effects"],
            "right_effects": row["right_effects"],
            "left_push_total": l_total,
            "right_push_total": r_total,
            "left_push_summary": row["left_push_summary"],
            "right_push_summary": row["right_push_summary"],
        })

    _write_ledger_js("societal_values", sv_rows)
    with open(os.path.join(DATA_DIR, "societal_drift.json"), "w", encoding="utf-8") as f:
        json.dump(drift_summary, f, ensure_ascii=False, indent=2)
    print(f"Enriched societal_values.js: 17 axes with full pole effects and non-event drift sources.")
    return drift_summary


def compile_units_atlas(game_ctx):
    """Parse all 401 units, expand goods recipes, compute Age Matrix & Unique-vs-Standard deltas."""
    units = _read_ledger_js("unit_types")
    adv_list = _read_catalog_js("advances").get("records", [])
    adv_cat = {r["id"]: r["zh"] for r in adv_list}
    adv_by_id = {r["id"]: r for r in adv_list}
    adv_by_unlock_zh = {}
    adv_by_zh = {}
    for r in adv_list:
        adv_by_zh.setdefault(r["zh"], r)
        m_ul = re.search(r"解锁兵种：([^\s｜、，]+)", r.get("detail", ""))
        if m_ul:
            adv_by_unlock_zh.setdefault(m_ul.group(1).strip(), r)
    unit_zh_to_id = {u["zh"]: u["id"] for u in units}
    unit_by_id = {u["id"]: u for u in units}

    AGE_MAP = {
        "传统 · Traditions": (1, "① 传统时代", "Traditions"),
        "文艺复兴 · Renaissance": (2, "② 文艺复兴", "Renaissance"),
        "地理大发现 · Discovery": (3, "③ 地理大发现", "Discovery"),
        "宗教改革 · Reformation": (4, "④ 宗教改革", "Reformation"),
        "专制主义 · Absolutism": (5, "⑤ 专制主义", "Absolutism"),
        "大革命 · Revolutions": (6, "⑥ 革命时代", "Revolutions"),
        "通用基础 · Base": (0, "底层基础", "Base"),
    }

    CAT_MAP = {
        "陆军 · 轻步兵 · Light Infantry": ("land", "light_infantry", "轻步兵", 1),
        "陆军 · 重步兵 · Heavy Infantry": ("land", "heavy_infantry", "重步兵", 2),
        "陆军 · 轻骑兵 · Light Cavalry": ("land", "light_cavalry", "轻骑兵", 3),
        "陆军 · 重骑兵 · Heavy Cavalry": ("land", "heavy_cavalry", "重骑兵", 4),
        "陆军 · 炮兵 · Artillery": ("land", "artillery", "炮兵", 5),
        "陆军 · 辅助兵 · Auxiliary": ("land", "auxiliary", "辅助辎重", 6),
        "海军 · 重型战舰 · Heavy Ship": ("navy", "heavy_ship", "重型战舰", 7),
        "海军 · 轻型战舰 · Light Ship": ("navy", "light_ship", "轻型战舰", 8),
        "海军 · 桨帆战舰 · Galley": ("navy", "galley", "桨帆战舰", 9),
        "海军 · 运输船 · Transport": ("navy", "transport", "运输船", 10),
    }

    # Parse raw unit_categories + unit_types scripts to resolve exact construction/maintenance demand IDs via copy_from
    from humanize_data import _parse_simple_kv_blocks
    game_common = r"D:\SteamLibrary\steamapps\common\Europa Universalis V\game\in_game\common"
    raw_cat_blocks = _parse_simple_kv_blocks(os.path.join(game_common, "unit_categories"))
    raw_ut_blocks = _parse_simple_kv_blocks(os.path.join(game_common, "unit_types"))

    def resolve_unit_demands(uid, seen=None):
        seen = seen or set()
        if uid in seen:
            return {}
        seen.add(uid)
        body = raw_ut_blocks.get(uid, "")
        res = {}
        m_cp = re.search(r"\bcopy_from\s*=\s*([A-Za-z0-9_]+)", body)
        m_cat = re.search(r"\bcategory\s*=\s*([A-Za-z0-9_]+)", body)
        if m_cat and m_cat.group(1) in raw_cat_blocks:
            cbody = raw_cat_blocks[m_cat.group(1)]
            for dk in ("construction_demand", "maintenance_demand", "repair_demand"):
                md = re.search(rf"\b{dk}\s*=\s*([A-Za-z0-9_]+)", cbody)
                if md:
                    res[dk] = md.group(1)
        if m_cp:
            res.update(resolve_unit_demands(m_cp.group(1), seen))
        for dk in ("construction_demand", "maintenance_demand", "repair_demand"):
            md = re.search(rf"\b{dk}\s*=\s*([A-Za-z0-9_]+)", body)
            if md:
                res[dk] = md.group(1)
        return res

    def expand_demand_clause(uid, val_str):
        raw_d = resolve_unit_demands(uid)
        b_id = raw_d.get("construction_demand", "")
        m_id = raw_d.get("maintenance_demand", "")
        r_id = raw_d.get("repair_demand", "") or b_id
        b_exp = game_ctx["demands"].get(b_id, "")
        m_exp = game_ctx["demands"].get(m_id, "")
        r_exp = game_ctx["demands"].get(r_id, "")
        if b_exp or m_exp:
            segs = []
            if b_exp: segs.append(f"建造：{b_exp}")
            if m_exp: segs.append(f"维护：{m_exp}")
            if r_exp and r_exp != b_exp: segs.append(f"修理：{r_exp}")
            return "；".join(segs)
        parts = []
        for seg in val_str.split("；"):
            if "：" in seg:
                lbl, dname = seg.split("：", 1)
                dname = dname.strip()
                expanded = game_ctx["demands"].get(dname) or game_ctx["demands"].get(dname.replace(" ", ""))
                parts.append(f"{lbl.strip()}：{expanded or dname}")
            else:
                parts.append(seg)
        return "；".join(parts)

    def parse_num(txt, pattern, default=None):
        m = re.search(pattern, txt)
        if not m:
            return default
        try:
            return float(m.group(1))
        except ValueError:
            return default

    parsed_units = []
    for u in units:
        uid = u["id"]
        age_idx, age_zh, age_en = AGE_MAP.get(u["age"], (0, u["age"], ""))
        domain, cat_key, cat_short, cat_ord = CAT_MAP.get(u["category"], ("land", "other", u["category"], 99))
        utype = u["unit_type"]
        is_template = utype == "模板 · Template"
        is_levy = "征召" in utype

        # Clean detail_pairs & expand goods demands (idempotent across re-runs)
        clean_pairs = []
        pairs_dict = {}
        for k, v in u.get("detail_pairs", []):
            if "关联定义" in k or k == "对比同代标准兵种":
                continue
            if "物资配方" in k:
                v = expand_demand_clause(uid, v)
            clean_pairs.append([k, v])
            pairs_dict[k.split("·")[0].strip()] = v
        u["detail_pairs"] = clean_pairs

        mov_txt = pairs_dict.get("机动与阵线", "")
        comb_txt = pairs_dict.get("攻防修正", "")
        naval_txt = pairs_dict.get("海上任务", "")
        food_txt = pairs_dict.get("粮食与损耗", "")
        terr_txt = pairs_dict.get("地形伤害修正", "")
        traits_txt = pairs_dict.get("单位特性", "")
        goods_txt = pairs_dict.get("物资配方", "")
        upg_txt = pairs_dict.get("优先升级型号", "") or pairs_dict.get("限定升级型号", "")
        adv_txt = pairs_dict.get("解锁革新", "") or pairs_dict.get("征召解锁革新", "")
        chain_txt = pairs_dict.get("继承顺序", "")

        troops = float(u["troops"]) if u["troops"] != "—" else 0.0
        cpower = float(u["combat_power"]) if u["combat_power"] != "—" else 0.0
        cannons = float(u["cannons"]) if u["cannons"] != "—" else 0.0
        hull = float(u["hull"]) if u["hull"] != "—" else 0.0
        btime = float(u["build_time"]) if u["build_time"] != "—" else 0.0

        move_spd = parse_num(mov_txt, r"地图移动速度[^0-9\-]*([0-9.]+)", 0.0)
        frontage = parse_num(mov_txt, r"正面宽度[^0-9\-]*([0-9.]+)", 1.0)
        init_v = parse_num(mov_txt, r"主动性[^0-9\-]*([0-9.\-]+)", 1.0)
        cspd = parse_num(mov_txt, r"战斗速度[^0-9\-]*([0-9.]+)", 1.0)
        flank = parse_num(mov_txt, r"侧击能力[^0-9\-]*([0-9.]+)", 1.0)
        sec_flank = parse_num(mov_txt, r"侧翼防御[^0-9\-+]*([+\-]?[0-9.]+)%", 0.0)

        cat_dmg_taken = parse_num(pairs_dict.get("兵种基础承伤系数", ""), r"([0-9.]+)", 1.0)
        str_done = parse_num(comb_txt, r"兵力杀伤[^0-9\-+]*([+\-]?[0-9.]+)%", 0.0)
        str_taken = parse_num(comb_txt, r"兵力承伤[^0-9\-+]*([+\-]?[0-9.]+)%", 0.0)
        mor_done = parse_num(comb_txt, r"(?:士气杀伤|士气打击)[^0-9\-+]*([+\-]?[0-9.]+)%", 0.0)
        mor_taken = parse_num(comb_txt, r"士气承伤[^0-9\-+]*([+\-]?[0-9.]+)%", 0.0)
        bombard_eff = parse_num(comb_txt, r"(?:炮击效率|炮兵弹幕|炮击|轰击)[^0-9\-+]*([+\-]?[0-9.]+)%", 0.0)

        maritime = parse_num(naval_txt, r"海上存在[^0-9\-]*([0-9.]+)", 0.0)
        blockade = parse_num(naval_txt, r"封锁能力[^0-9\-]*([0-9.]+)", 0.0)
        anti_piracy = parse_num(naval_txt, r"反海盗[^0-9\-]*([0-9.]+)", 0.0)
        transport_cap = parse_num(naval_txt, r"运输兵力[^0-9\-]*([0-9.]+)", 0.0)

        food_store = parse_num(food_txt, r"储粮[^0-9\-]*([0-9.]+)", 0.0)
        food_cons = parse_num(food_txt, r"耗粮[^0-9\-]*([0-9.]+)", 0.0)

        pwr_per_w = round((troops / 1000.0) * cpower / frontage, 2) if domain == "land" and frontage > 0 else 0.0
        can_per_w = round(cannons / frontage, 1) if domain == "navy" and frontage > 0 else 0.0

        # Resolve upgrade target ID & unlocking advance ID
        upg_zh = upg_txt.split("/")[0].strip() if upg_txt else ""
        upg_id = unit_zh_to_id.get(upg_zh, "")
        adv_zh = adv_txt.split("/")[0].strip() if adv_txt else ""
        adv_rec = adv_by_unlock_zh.get(u["zh"]) or (adv_by_zh.get(adv_zh) if adv_zh else None)
        adv_id = adv_rec["id"] if adv_rec else ""
        if not adv_zh and adv_rec:
            adv_zh = adv_rec["zh"]

        # Determine if unique / country / regional special unit vs universal age standard unit
        src_fn = u.get("source", "").split("#")[0].split("/")[-1]
        elig_parts = []
        for ek in ("国家资格", "地点资格", "当地征募条件", "征召文化", "征召国家条件"):
            if pairs_dict.get(ek):
                elig_parts.append(pairs_dict[ek])
        elif_cond = u.get("scopeConditions", "")
        eligibility = "；".join(elig_parts) or elif_cond
        if not eligibility and adv_rec and adv_rec.get("scopeConditions"):
            ac = re.sub(r"^可见条件（(.+)）$", r"\1", adv_rec["scopeConditions"].strip())
            eligibility = f"革新限定：{ac}"
        if not eligibility and pairs_dict.get("所属系列"):
            fam = pairs_dict["所属系列"]
            fam_adv = adv_by_zh.get(fam)
            if fam_adv and fam_adv.get("scopeConditions"):
                ac = re.sub(r"^可见条件（(.+)）$", r"\1", fam_adv["scopeConditions"].strip())
                eligibility = f"{fam}系列（{ac}）"
            else:
                eligibility = f"{fam}系列专属单位"

        is_unique = False
        if not is_template:
            if (
                "特殊单位" in traits_txt
                or "uniques" in src_fn
                or src_fn in ("3_camel_units.txt", "3_cawa_regiments.txt", "3_elephant_units.txt", "3_janissaries.txt", "3_qizilbash.txt", "a_bedouin_cavalry.txt", "a_nahuatl.txt", "a_north_american.txt", "D008_byzantine_unit_types.txt", "2_conquistador.txt", "0_tribal.txt")
                or u["scope_code"] in ("national", "special")
            ):
                if uid not in ("a_tribesmen", "a_villagers", "a_feudal_levy"):
                    is_unique = True
            elif u["scope_code"] == "conditional" and uid not in ("a_archers", "a_footmen", "a_footmen_levy", "a_peasant_levy", "a_villagers", "a_feudal_levy"):
                is_unique = True

        # Update ledger summary fields so ledgers.html#unit_types also benefits
        u["frontage"] = f"{frontage:g}"
        u["initiative"] = f"{init_v:g}"
        u["power_per_w"] = f"{pwr_per_w:g}" if domain == "land" else f"{can_per_w:g} 炮/宽"

        rec = {
            "id": uid,
            "zh": u["zh"],
            "en": u["en"],
            "age_idx": age_idx,
            "age_zh": age_zh,
            "domain": domain,
            "cat_key": cat_key,
            "cat_zh": cat_short,
            "cat_ord": cat_ord,
            "unit_type": utype.split("·")[0].strip(),
            "is_template": is_template,
            "is_levy": is_levy,
            "is_unique": is_unique,
            "troops": troops,
            "combat_power": cpower,
            "frontage": frontage,
            "power_per_width": pwr_per_w,
            "cannons": cannons,
            "hull": hull,
            "cannons_per_width": can_per_w,
            "move_speed": move_spd,
            "initiative": init_v,
            "combat_speed": cspd,
            "flanking": flank,
            "secure_flanks": sec_flank,
            "cat_dmg_taken": cat_dmg_taken,
            "str_done": str_done,
            "str_taken": str_taken,
            "mor_done": mor_done,
            "mor_taken": mor_taken,
            "bombard_eff": bombard_eff,
            "maritime": maritime,
            "blockade": blockade,
            "anti_piracy": anti_piracy,
            "transport": transport_cap,
            "food_store": food_store,
            "food_cons": food_cons,
            "build_time": btime,
            "terrain": terr_txt,
            "goods": goods_txt,
            "traits": traits_txt,
            "eligibility": eligibility,
            "limit": pairs_dict.get("数量上限", ""),
            "upg_zh": upg_zh,
            "upg_id": upg_id,
            "adv_zh": adv_zh,
            "adv_id": adv_id,
            "chain": chain_txt,
            "source": u.get("source", ""),
        }
        parsed_units.append(rec)

    # Build lookup of Standard Benchmark Units per (age_idx, cat_key, is_levy)
    # Prefer universal recruitable/levy units (e.g. a_footmen, a_men_at_arms, a_halberdiers, n_early_carrack),
    # falling back to the 00_age_templates_* template for that (age_idx, cat_key)
    std_by_slot = {}
    tpl_by_slot = {}
    PREFERRED_STD_IDS = {
        (1, "heavy_infantry", False): "a_footmen",
        (1, "light_infantry", False): "a_archers",
        (1, "light_cavalry", False): "a_horsemen",
        (1, "heavy_cavalry", False): "a_armored_horsemen",
        (1, "heavy_infantry", True): "a_footmen_levy",
        (1, "heavy_cavalry", True): "a_mailed_knights",
        (2, "heavy_infantry", False): "a_men_at_arms",
        (2, "light_infantry", False): "a_crossbowmen",
        (2, "light_cavalry", False): "a_cavalrymen",
        (2, "heavy_cavalry", False): "a_heavy_cavalrymen",
        (2, "artillery", False): "a_houfnice",
        (2, "auxiliary", False): "a_supply_carts",
        (2, "light_infantry", True): "a_peasant_levy",
        (2, "heavy_infantry", True): "a_men_at_arms_levy",
        (2, "heavy_cavalry", True): "a_plated_knights",
    }
    rec_by_id = {r["id"]: r for r in parsed_units}
    for r in parsed_units:
        slot_tpl = (r["age_idx"], r["cat_key"])
        if r["is_template"] and ("age_" in r["id"]):
            tpl_by_slot[slot_tpl] = r
        if not r["is_template"] and not r["is_unique"]:
            slot = (r["age_idx"], r["cat_key"], r["is_levy"])
            if slot not in std_by_slot:
                std_by_slot[slot] = r
    for slot, pid in PREFERRED_STD_IDS.items():
        if pid in rec_by_id:
            std_by_slot[slot] = rec_by_id[pid]

    def parse_terr_map(t_str):
        res = {}
        if not t_str:
            return res
        for seg in re.split(r"[、；;]", t_str):
            m = re.match(r"\s*(.+?)\s*([+\-][0-9.]+%)", seg)
            if m:
                res[m.group(1).strip()] = m.group(2)
        return res

    # Compute exact Unique-vs-Standard deltas for every unique unit!
    unique_with_deltas = 0
    for r in parsed_units:
        if not r["is_unique"]:
            continue
        base = std_by_slot.get((r["age_idx"], r["cat_key"], r["is_levy"]))
        if not base:
            base = std_by_slot.get((r["age_idx"], r["cat_key"], False)) or tpl_by_slot.get((r["age_idx"], r["cat_key"]))
        if not base or base["id"] == r["id"]:
            continue

        r["base_id"] = base["id"]
        r["base_zh"] = base["zh"]
        deltas = []

        def cmp_val(label, rv, bv, unit_s="", higher_is_good=True, is_pct_pt=False):
            if rv is None or bv is None or abs(rv - bv) < 1e-6:
                return
            diff = rv - bv
            sign = "+" if diff > 0 else ""
            if is_pct_pt:
                d_str = f"{sign}{diff:g}%"
                det = f"{bv:g}% → {rv:g}%"
            elif bv != 0 and label in ("满编兵力", "每宽等效火力", "舰炮", "船体"):
                pct = (diff / bv) * 100.0
                d_str = f"{sign}{diff:g}{unit_s} ({sign}{pct:.0f}%)"
                det = f"{bv:g} → {rv:g}"
            else:
                d_str = f"{sign}{diff:g}{unit_s}"
                det = f"{bv:g} → {rv:g}"
            good = (diff > 0) if higher_is_good else (diff < 0)
            deltas.append({
                "stat": label,
                "diff": d_str,
                "detail": det,
                "pol": "pos" if good else "neg",
            })

        if r["domain"] == "land":
            cmp_val("每宽等效火力", r["power_per_width"], base["power_per_width"], "", True)
            cmp_val("满编兵力", r["troops"], base["troops"], "人", True)
            cmp_val("陆战战力", r["combat_power"], base["combat_power"], "", True)
            cmp_val("正面宽度", r["frontage"], base["frontage"], "", False)
            cmp_val("主动性", r["initiative"], base["initiative"], "", True)
            cmp_val("参战速度", r["combat_speed"], base["combat_speed"], "", True)
            cmp_val("兵力杀伤", r["str_done"], base["str_done"], "", True, is_pct_pt=True)
            cmp_val("兵力承伤", r["str_taken"], base["str_taken"], "", False, is_pct_pt=True)
            cmp_val("士气杀伤", r["mor_done"], base["mor_done"], "", True, is_pct_pt=True)
            cmp_val("士气承伤", r["mor_taken"], base["mor_taken"], "", False, is_pct_pt=True)
            cmp_val("侧击能力", r["flanking"], base["flanking"], "×", True)
            cmp_val("侧翼防御", r["secure_flanks"], base["secure_flanks"], "", True, is_pct_pt=True)
            cmp_val("行军速度", r["move_speed"], base["move_speed"], "", True)
            cmp_val("单位耗粮", r["food_cons"], base["food_cons"], "", False)
            cmp_val("单位储粮", r["food_store"], base["food_store"], "", True)
        else:
            cmp_val("舰炮", r["cannons"], base["cannons"], "门", True)
            cmp_val("船体耐久", r["hull"], base["hull"], "", True)
            cmp_val("每宽舰炮", r["cannons_per_width"], base["cannons_per_width"], "", True)
            cmp_val("正面宽度", r["frontage"], base["frontage"], "", False)
            cmp_val("主动性", r["initiative"], base["initiative"], "", True)
            cmp_val("航速", r["move_speed"], base["move_speed"], "", True)
            cmp_val("兵力杀伤", r["str_done"], base["str_done"], "", True, is_pct_pt=True)
            cmp_val("兵力承伤", r["str_taken"], base["str_taken"], "", False, is_pct_pt=True)
            cmp_val("士气杀伤", r["mor_done"], base["mor_done"], "", True, is_pct_pt=True)
            cmp_val("士气承伤", r["mor_taken"], base["mor_taken"], "", False, is_pct_pt=True)
            cmp_val("海上存在", r["maritime"], base["maritime"], "/月", True)
            cmp_val("封锁能力", r["blockade"], base["blockade"], "", True)
            cmp_val("反海盗", r["anti_piracy"], base["anti_piracy"], "", True)
            cmp_val("运载兵力", r["transport"], base["transport"], "人", True)

        if r["build_time"] > 0 and base["build_time"] > 0:
            cmp_val("组建工期", r["build_time"], base["build_time"], "天", False)

        # Compare terrain combat bonuses!
        rt = parse_terr_map(r["terrain"])
        bt = parse_terr_map(base["terrain"])
        for tk in sorted(set(rt) | set(bt)):
            rv_s = rt.get(tk, "0%")
            bv_s = bt.get(tk, "0%")
            if rv_s != bv_s:
                rv_n = float(rv_s.replace("%", ""))
                bv_n = float(bv_s.replace("%", ""))
                diff_n = rv_n - bv_n
                sign = "+" if diff_n > 0 else ""
                deltas.append({
                    "stat": f"{tk}作战",
                    "diff": f"{sign}{diff_n:g}%",
                    "detail": f"{bv_s} → {rv_s}",
                    "pol": "pos" if diff_n > 0 else "neg",
                })

        r["deltas"] = deltas
        if deltas:
            unique_with_deltas += 1
            # Also inject delta summary into unit_types.js row so ledgers.html shows it too!
            u_orig = unit_by_id[r["id"]]
            delta_txt = "、".join(f"{d['stat']} {d['diff']}" for d in deltas[:6])
            u_orig["vs_base"] = f"对比【{base['zh']}】：{delta_txt}"
            u_orig["detail_pairs"].insert(0, ["对比同代标准兵种", f"基准型号【{base['zh']}】 → {delta_txt}"])

    _write_ledger_js("unit_types", units)
    out_units_js = os.path.join(ASSETS_DIR, "units-data.js")
    with open(out_units_js, "w", encoding="utf-8") as f:
        f.write("window.__EU5_UNITS_ATLAS__ = " + json.dumps(parsed_units, ensure_ascii=False) + ";\n")

    std_cnt = sum(1 for x in parsed_units if not x["is_template"] and not x["is_unique"])
    uniq_cnt = sum(1 for x in parsed_units if x["is_unique"])
    tpl_cnt = sum(1 for x in parsed_units if x["is_template"])
    print(f"Exported units-data.js: total={len(parsed_units)} (standard={std_cnt}, unique={uniq_cnt} [with_deltas={unique_with_deltas}], templates={tpl_cnt})")


def main():
    zh_kv = load_yml_kv("simp_chinese")
    clean_zh_kv = {
        k: re.sub(r"\[([^\[\]|]+)(?:\|[^\[\]]*)?\]", r"\1", re.sub(r"#[A-Za-z0-9_!]+", "", v)).strip()
        for k, v in zh_kv.items()
    }
    game_ctx = load_game_context(clean_zh_kv)
    ms, mods_by_item = load_metric_sources()

    # 1. Rebuild metrics-data.js with direct source hrefs
    build_metrics_bundle(ms, clean_zh_kv, game_ctx)
    # 2. Enrich 17 societal_values with full effects & non-event push sources
    compile_societal_values_drift(ms, mods_by_item, clean_zh_kv, game_ctx)
    # 3. Compile 401 units Age Matrix & Unique-vs-Standard deltas
    compile_units_atlas(game_ctx)
    # 4. Build Global Entity Cross-Link Dictionary
    build_entity_links()


if __name__ == "__main__":
    main()
