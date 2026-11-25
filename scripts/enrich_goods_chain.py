# -*- coding: utf-8 -*-
"""
Compile complete RGO / Construction Material / Producer Buildings / Consumer Buildings
chains for all 75 goods directly from EU5 1.4.9 game scripts (in_game + dlc),
enriching docs/assets/ledgers/goods.js and data/ledgers.json.
"""
import collections
import glob
import json
import os
import re
import sys

PROJ_DIR = r"C:\Users\seepath\.gemini\antigravity\scratch\eu5-compendium"
DATA_DIR = os.path.join(PROJ_DIR, "data")
DOCS_DIR = os.path.join(PROJ_DIR, "docs")
LEDGERS_DIR = os.path.join(DOCS_DIR, "assets", "ledgers")
GAME_ROOT = r"D:\SteamLibrary\steamapps\common\Europa Universalis V\game"

METHOD_ZH = {
    "mining": "采矿",
    "farming": "农牧",
    "gathering": "采集",
    "forestry": "林业",
    "hunting": "狩猎",
    "produced": "工坊制造",
    "special": "特殊掳掠/贸易",
}

INFRA_DEMAND_LABELS = {
    "build_gravel_road_demand": ("铺设砂石路", "construction"),
    "build_paved_road_demand": ("铺设石铺路", "construction"),
    "build_modern_road_demand": ("铺设现代公路", "construction"),
    "build_railroad_demand": ("铺设铁路", "construction"),
    "build_town_demand": ("聚落晋升集镇", "construction"),
    "build_city_demand": ("集镇晋升城市", "construction"),
    "colony_construction": ("建立殖民地", "construction"),
    "upgrade_rgo_demand_mining": ("扩建采矿RGO", "construction"),
    "upgrade_rgo_demand_farming": ("扩建农牧RGO", "construction"),
    "upgrade_rgo_demand_hunting": ("扩建狩猎RGO", "construction"),
    "upgrade_rgo_demand_gathering": ("扩建采集RGO", "construction"),
    "upgrade_rgo_demand_forestry": ("扩建林业RGO", "construction"),
    "maintain_gravel_road_demand": ("砂石路日常维护", "maintenance"),
    "maintain_paved_road_demand": ("石铺路日常维护", "maintenance"),
    "maintain_modern_road_demand": ("现代公路日常维护", "maintenance"),
    "maintain_railroad_demand": ("铁路日常维护", "maintenance"),
}


def iter_top_blocks(txt):
    txt = re.sub(r"#.*", "", txt)
    i, n = 0, len(txt)
    while i < n:
        m = re.search(r"([A-Za-z0-9_]+)\s*=\s*\{", txt[i:])
        if not m:
            break
        key = m.group(1)
        start = i + m.end()
        depth = 1
        j = start
        while j < n and depth > 0:
            if txt[j] == "{":
                depth += 1
            elif txt[j] == "}":
                depth -= 1
            j += 1
        yield key, txt[start:j - 1]
        i = j


def read_ledger_js(lid):
    p = os.path.join(LEDGERS_DIR, f"{lid}.js")
    txt = open(p, encoding="utf-8").read()
    return json.loads(txt[txt.index("["):txt.rindex("]") + 1])


def write_ledger_js(lid, rows):
    p = os.path.join(LEDGERS_DIR, f"{lid}.js")
    with open(p, "w", encoding="utf-8") as f:
        f.write(f'window.__EU5_LEDGER_REGISTER__("{lid}", ')
        json.dump(rows, f, ensure_ascii=False, separators=(",", ":"))
        f.write(");\n")


def fmt_amt(v):
    return f"{round(v, 3):g}"


def main():
    sys.stdout.reconfigure(encoding="utf-8")

    goods_rows = read_ledger_js("goods")
    bldg_rows = read_ledger_js("building_types")
    units_raw = open(os.path.join(DOCS_DIR, "assets", "units-data.js"), encoding="utf-8").read()
    units_rows = json.loads(units_raw[units_raw.index("["):units_raw.rindex("]") + 1])

    good_zh = {g["id"]: g["zh"] for g in goods_rows}
    bldg_zh = {b["id"]: b["zh"] for b in bldg_rows}

    # 1. Parse raw goods definitions
    raw_goods = {}
    for f in sorted(glob.glob(os.path.join(GAME_ROOT, "**", "common", "goods", "*.txt"), recursive=True)):
        if "readme" in os.path.basename(f).lower():
            continue
        for gid, body in iter_top_blocks(open(f, encoding="utf-8-sig").read()):
            cat_m = re.search(r"\bcategory\s*=\s*([A-Za-z0-9_]+)", body)
            meth_m = re.search(r"\bmethod\s*=\s*([A-Za-z0-9_]+)", body)
            slv_m = re.search(r"\bis_slaves\s*=\s*yes", body)
            infl_m = re.search(r"\binflation\s*=\s*yes", body)
            cat = cat_m.group(1) if cat_m else "raw_material"
            if cat == "raw_material":
                meth = meth_m.group(1) if meth_m else "farming"
            else:
                meth = "special" if slv_m else "produced"
            raw_goods[gid] = {
                "category": cat,
                "method": meth,
                "is_slaves": bool(slv_m),
                "inflation": bool(infl_m),
            }

    # 2. Parse all goods_demand blocks
    demands = {}
    for f in sorted(glob.glob(os.path.join(GAME_ROOT, "**", "common", "goods_demand", "*.txt"), recursive=True)):
        for did, body in iter_top_blocks(open(f, encoding="utf-8-sig").read()):
            cat_m = re.search(r"\bcategory\s*=\s*([A-Za-z0-9_]+)", body)
            gmap = {}
            for gm in re.finditer(r"\b([A-Za-z0-9_]+)\s*=\s*([0-9.]+)", body):
                gk, gv = gm.group(1), float(gm.group(2))
                if gk in good_zh and gv > 0:
                    gmap[gk] = gv
            demands[did] = {"category": cat_m.group(1) if cat_m else "", "goods": gmap}

    # 3. Parse shared production_methods
    shared_pms = {}
    for f in sorted(glob.glob(os.path.join(GAME_ROOT, "**", "common", "production_methods", "*.txt"), recursive=True)):
        if "readme" in os.path.basename(f).lower():
            continue
        for pid, body in iter_top_blocks(open(f, encoding="utf-8-sig").read()):
            prod_m = re.search(r"\bproduced\s*=\s*([A-Za-z0-9_]+)", body)
            out_m = re.search(r"\boutput\s*=\s*([0-9.]+)", body)
            cat_m = re.search(r"\bcategory\s*=\s*([A-Za-z0-9_]+)", body)
            ins = {}
            for gm in re.finditer(r"\b([A-Za-z0-9_]+)\s*=\s*([0-9.]+)", body):
                gk, gv = gm.group(1), float(gm.group(2))
                if gk in good_zh and gv > 0:
                    ins[gk] = gv
            shared_pms[pid] = {
                "out_good": prod_m.group(1) if (prod_m and prod_m.group(1) in good_zh) else None,
                "out_amt": float(out_m.group(1)) if out_m else 0.0,
                "inputs": ins,
                "category": cat_m.group(1) if cat_m else "",
            }

    # 4. Parse all raw building_types
    raw_buildings = {}
    for f in sorted(glob.glob(os.path.join(GAME_ROOT, "**", "common", "building_types", "*.txt"), recursive=True)):
        for bid, body in iter_top_blocks(open(f, encoding="utf-8-sig").read()):
            raw_buildings[bid] = body

    # Data collectors per good_id
    produced_by = collections.defaultdict(list)       # gid -> [(bid, bzh, out_amt)]
    rgo_boost_by = collections.defaultdict(list)      # gid -> [(bid, bzh, pct_str)]
    prod_input_by = collections.defaultdict(list)     # gid -> [(bid, bzh, in_amt, out_zh_set)]
    maint_input_by = collections.defaultdict(list)    # gid -> [(bid, bzh, in_amt)]
    con_bldg_by = collections.defaultdict(list)       # gid -> [(bid, bzh, con_amt)]
    con_infra_by = collections.defaultdict(list)      # gid -> [(label, amt)]
    maint_infra_by = collections.defaultdict(list)    # gid -> [(label, amt)]

    # Infrastructure demands (roads, RGO expansion, town/city founding, colonies)
    for did, (lbl, kind) in INFRA_DEMAND_LABELS.items():
        if did in demands:
            for gk, gv in demands[did]["goods"].items():
                if kind == "construction":
                    con_infra_by[gk].append((lbl, gv))
                else:
                    maint_infra_by[gk].append((lbl, gv))

    # Buildings analysis
    for b in bldg_rows:
        bid = b["id"]
        bzh = b["zh"]
        # Clean '基础建造' in building_types.js while we are here
        for pair in b.get("detail_pairs", []):
            if pair[0] == "建造所需材料" and pair[1] == "基础建造":
                pair[1] = "无商品消耗（防经济死锁基础建造）"

        body = raw_buildings.get(bid, "")
        if not body:
            continue

        # A. Construction demand
        cd_m = re.search(r"\bconstruction_demand\s*=\s*([A-Za-z0-9_]+)", body)
        if cd_m and cd_m.group(1) in demands:
            for gk, gv in demands[cd_m.group(1)]["goods"].items():
                con_bldg_by[gk].append((bid, bzh, gv))

        # B. RGO output modifier on building (`local_<good>_output_modifier = 0.1`)
        for mm in re.finditer(r"\blocal_([A-Za-z0-9_]+)_output_modifier\s*=\s*([+\-]?[0-9.]+)", body):
            gk = mm.group(1)
            if gk in good_zh:
                pct = float(mm.group(2)) * 100.0
                sign = "+" if pct > 0 else ""
                rgo_boost_by[gk].append((bid, bzh, f"{sign}{pct:g}%"))

        # C. Production methods (shared + unique)
        pm_list = []
        for pm_blk in re.findall(r"possible_production_methods\s*=\s*\{([^}]*)\}", body):
            for tok in re.findall(r"[A-Za-z0-9_]+", pm_blk):
                if tok in shared_pms:
                    pm_list.append(shared_pms[tok])

        for upm_m in re.finditer(r"unique_production_methods\s*=\s*\{", body):
            s0 = upm_m.end()
            d = 1
            j = s0
            while j < len(body) and d > 0:
                if body[j] == "{":
                    d += 1
                elif body[j] == "}":
                    d -= 1
                j += 1
            ubody = body[s0:j - 1]
            for _, pbody in iter_top_blocks(ubody):
                prod_m = re.search(r"\bproduced\s*=\s*([A-Za-z0-9_]+)", pbody)
                out_m = re.search(r"\boutput\s*=\s*([0-9.]+)", pbody)
                cat_m = re.search(r"\bcategory\s*=\s*([A-Za-z0-9_]+)", pbody)
                ins = {}
                for gm in re.finditer(r"\b([A-Za-z0-9_]+)\s*=\s*([0-9.]+)", pbody):
                    gk, gv = gm.group(1), float(gm.group(2))
                    if gk in good_zh and gv > 0:
                        ins[gk] = gv
                pm_list.append({
                    "out_good": prod_m.group(1) if (prod_m and prod_m.group(1) in good_zh) else None,
                    "out_amt": float(out_m.group(1)) if out_m else 0.0,
                    "inputs": ins,
                    "category": cat_m.group(1) if cat_m else "",
                })

        out_max = {}
        prod_in_max = {}    # gk -> (max_amt, set_of_out_good_zh)
        maint_in_max = {}   # gk -> max_amt

        for pm in pm_list:
            og = pm["out_good"]
            if og:
                out_max[og] = max(out_max.get(og, 0.0), pm["out_amt"])
                og_zh = good_zh[og]
                for gk, gv in pm["inputs"].items():
                    prev_v, prev_outs = prod_in_max.get(gk, (0.0, set()))
                    prev_outs.add(og_zh)
                    prod_in_max[gk] = (max(prev_v, gv), prev_outs)
            else:
                for gk, gv in pm["inputs"].items():
                    maint_in_max[gk] = max(maint_in_max.get(gk, 0.0), gv)

        for gk, gv in out_max.items():
            produced_by[gk].append((bid, bzh, gv))
        for gk, (gv, outs) in prod_in_max.items():
            prod_input_by[gk].append((bid, bzh, gv, sorted(outs)))
        for gk, gv in maint_in_max.items():
            if gk not in prod_in_max:
                maint_input_by[gk].append((bid, bzh, gv))

    # 5. Also check military units (non-template) that need each good for construction/maintenance
    unit_users_by = collections.defaultdict(list)
    for u in units_rows:
        if u.get("is_template"):
            continue
        gtxt = u.get("goods", "")
        if not gtxt:
            continue
        for gid, gname in good_zh.items():
            if re.search(rf"(?<![\u4e00-\u9fff]){re.escape(gname)}\s+[0-9.]", gtxt):
                unit_users_by[gid].append(u["zh"])

    def dedup_by_zh(seq):
        seen = set()
        out = []
        for item in seq:
            bzh = item[1]
            if bzh in seen:
                continue
            seen.add(bzh)
            out.append(item)
        return out

    # Sort building lists nicely (higher output / higher input first) and dedup same-name buildings
    for gid in good_zh:
        produced_by[gid].sort(key=lambda x: (-x[2], x[1]))
        produced_by[gid] = dedup_by_zh(produced_by[gid])
        rgo_boost_by[gid] = dedup_by_zh(rgo_boost_by[gid])
        prod_input_by[gid].sort(key=lambda x: (-x[2], x[1]))
        prod_input_by[gid] = dedup_by_zh(prod_input_by[gid])
        maint_input_by[gid].sort(key=lambda x: (-x[2], x[1]))
        maint_input_by[gid] = dedup_by_zh(maint_input_by[gid])
        con_bldg_by[gid].sort(key=lambda x: (-x[2], x[1]))
        con_bldg_by[gid] = dedup_by_zh(con_bldg_by[gid])

    # 6. Enrich all 75 goods rows
    for g in goods_rows:
        gid = g["id"]
        rg = raw_goods.get(gid, {"category": "raw_material", "method": "farming", "is_slaves": False, "inflation": False})
        is_rgo = rg["category"] == "raw_material"
        meth_zh = METHOD_ZH.get(rg["method"], rg["method"])

        if is_rgo:
            g["group"] = "原材料 (RGO)"
            g["method"] = meth_zh
            rgo_badge = f"是 · {meth_zh} RGO"
        elif rg["is_slaves"]:
            g["group"] = "特殊商品"
            g["method"] = meth_zh
            rgo_badge = "否 · 特殊商品"
        else:
            g["group"] = "制成品 (工坊)"
            g["method"] = meth_zh
            rgo_badge = "否 · 工坊制成品"

        g["is_rgo"] = "是" if is_rgo else "否"
        g["rgo_badge"] = rgo_badge

        # Construction Material status
        cb = con_bldg_by[gid]
        ci = con_infra_by[gid]
        is_con = bool(cb or ci)
        g["is_con_mat"] = "是" if is_con else "否"
        if is_con:
            parts = []
            if cb:
                sample_cb = "、".join(f"{bzh}({fmt_amt(amt)})" for _, bzh, amt in cb[:3])
                parts.append(f"{len(cb)} 种建筑（{sample_cb}{' 等' if len(cb) > 3 else ''}）")
            if ci:
                parts.append("基建：" + "、".join(f"{lbl}({fmt_amt(amt)})" for lbl, amt in ci[:4]))
            con_summary = "是 · " + "；".join(parts)
        else:
            con_summary = "否"
        g["con_mat_summary"] = con_summary
        g["con_bldg_count"] = len(cb)

        # Producer buildings summary
        pb = produced_by[gid]
        rb = rgo_boost_by[gid]
        prod_parts = []
        if pb:
            sample_pb = "、".join(f"{bzh}({fmt_amt(amt)})" for _, bzh, amt in pb[:6])
            if len(pb) > 6:
                sample_pb += f" 等 {len(pb)} 种"
            prod_parts.append(sample_pb)
        if rb:
            sample_rb = "、".join(f"{bzh}({pct})" for _, bzh, pct in rb[:4])
            prod_parts.append(f"RGO增产：{sample_rb}")
        if not prod_parts:
            prod_summary = f"无工坊产出（仅靠{meth_zh} RGO 产地）" if is_rgo else "特殊机制产出"
        else:
            prod_summary = " ｜ ".join(prod_parts)
        g["producers_summary"] = prod_summary
        g["prod_bldg_count"] = len(pb)

        # Consumer buildings summary (production inputs + daily operational maintenance)
        pib = prod_input_by[gid]
        mib = maint_input_by[gid]
        need_parts = []
        if pib:
            sample_pi = "、".join(f"{bzh}({fmt_amt(amt)})" for _, bzh, amt in [(x[0], x[1], x[2]) for x in pib[:5]])
            if len(pib) > 5:
                sample_pi += f" 等 {len(pib)} 种"
            need_parts.append(f"生产投入：{sample_pi}")
        if mib:
            sample_mi = "、".join(f"{bzh}({fmt_amt(amt)})" for _, bzh, amt in mib[:4])
            if len(mib) > 4:
                sample_mi += f" 等 {len(mib)} 种"
            need_parts.append(f"日常维护：{sample_mi}")
        if not need_parts:
            if cb:
                need_summary = f"无日常消耗（仅作 {len(cb)} 种建筑施工建材，主要供人口/军队消费）"
            else:
                need_summary = "无建筑消耗（主要供八大人口阶级或军队消费）"
        else:
            need_summary = " ｜ ".join(need_parts)
        g["consumers_summary"] = need_summary
        g["need_bldg_count"] = len(pib) + len(mib)

        # Full expanded detail_pairs for click-to-expand drawer!
        dp = []
        rgo_detail = f"{rgo_badge}；基准市价 {g['price']} 金；运输重量系数 {g['transport']}；食物供给 {g['food'] if g['food'] > 0 else '0（非食物）'}"
        if g.get("base", 0) > 0:
            rgo_detail += f"；无专属产地保底产出 {g['base']}"
        if rg["inflation"]:
            rgo_detail += "；大量开采可能带来贵金属通货膨胀压力"
        dp.append(["RGO 与基础属性", rgo_detail])

        if pb:
            dp.append([
                f"直接生产该商品的建筑（共 {len(pb)} 种）",
                "、".join(f"{bzh}（产出 {fmt_amt(amt)}）" for _, bzh, amt in pb),
            ])
        else:
            dp.append([
                "直接生产该商品的建筑",
                f"无直接加工建筑——仅通过地图上的「{meth_zh}」RGO 原料产地开采/生产" if is_rgo else "通过俘掠或特殊贸易事件获取",
            ])

        if rb:
            dp.append([
                f"提升本地该 RGO 产量的辅助建筑（共 {len(rb)} 种）",
                "、".join(f"{bzh}（本地产出 {pct}）" for _, bzh, pct in rb),
            ])

        if pib:
            dp.append([
                f"作为【生产原料】需要它的加工建筑（共 {len(pib)} 种）",
                "、".join(f"{bzh}（投入 {fmt_amt(amt)} → 产{'/'.join(outs)}）" for _, bzh, amt, outs in pib),
            ])
        else:
            dp.append(["作为【生产原料】需要它的加工建筑", "无下游加工配方需要该商品作为原料"])

        if mib or maint_infra_by[gid]:
            m_items = [f"{bzh}（月耗 {fmt_amt(amt)}）" for _, bzh, amt in mib]
            m_items += [f"{lbl}（{fmt_amt(amt)}）" for lbl, amt in maint_infra_by[gid]]
            dp.append([
                f"作为【日常运营维护】需要它的功能建筑（共 {len(mib)} 种）",
                "、".join(m_items),
            ])

        if is_con:
            c_items = [f"{lbl}（{fmt_amt(amt)}）" for lbl, amt in ci]
            c_items += [f"{bzh}（{fmt_amt(amt)}）" for _, bzh, amt in cb]
            dp.append([
                f"作为【施工建筑材料】需要它的建筑与基建（建筑 {len(cb)} 种" + (f" + 基建 {len(ci)} 项" if ci else "") + "）",
                "、".join(c_items),
            ])
        else:
            dp.append(["作为【施工建筑材料】用途", "否（没有任何建筑或道路在施工建造时直接消耗该商品）"])

        uu = unit_users_by[gid]
        if uu:
            u_str = "、".join(uu[:25]) + (f" 等共 {len(uu)} 种陆海军单位" if len(uu) > 25 else f"（共 {len(uu)} 种单位）")
            dp.append(["需要它的军事单位（招募/造船/维护）", u_str])

        g["detail_pairs"] = dp

    write_ledger_js("goods", goods_rows)
    write_ledger_js("building_types", bldg_rows)

    # Sync data/ledgers.json as well so verify_site.py & search index stay 100% in sync
    ledgers_json_path = os.path.join(DATA_DIR, "ledgers.json")
    if os.path.exists(ledgers_json_path):
        all_ledgers = json.load(open(ledgers_json_path, encoding="utf-8"))
        all_ledgers["goods"] = goods_rows
        all_ledgers["building_types"] = bldg_rows
        with open(ledgers_json_path, "w", encoding="utf-8") as f:
            json.dump(all_ledgers, f, ensure_ascii=False, indent=2)

    rgo_cnt = sum(1 for g in goods_rows if g["is_rgo"] == "是")
    con_cnt = sum(1 for g in goods_rows if g["is_con_mat"] == "是")
    print(f"Successfully enriched all {len(goods_rows)} goods: RGO={rgo_cnt}, ConstructionMaterials={con_cnt}")


if __name__ == "__main__":
    main()
