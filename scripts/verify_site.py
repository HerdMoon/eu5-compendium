import json
import re
import subprocess
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
DATA = ROOT / "data"
ORIG_ATLAS = Path(r"C:\Users\seepath\Documents\Codex\2026-11-02\x20\work\eu5-atlas")

EXPECTED_HTML = [
    "index.html",
    "metrics.html",
    "ch01-territory-core.html",
    "ch02-population-food.html",
    "ch03-economy-market-trade.html",
    "ch04-government-cabinet.html",
    "ch05-estates-rebels.html",
    "ch06-culture-religion.html",
    "ch07-ages-colonial.html",
    "ch08-military-combat.html",
    "ch09-navy-war-peace.html",
    "ch10-diplomacy-subjects.html",
    "ch11-scenarios-missions-dlc.html",
    "ch12-gameplay-automation-updates.html",
    "map.html",
    "lab.html",
    "ledgers.html",
    "pop-demand.html",
    "directory.html",
    "glossary.html",
]

EXPECTED_JS = [
    "assets/app.js",
    "assets/interactive.js",
    "assets/graph-data.js",
    "assets/glossary-data.js",
    "assets/metrics-data.js",
    "assets/pop-demand-data.js",
    "assets/catalog-manifest.js",
    "assets/search-index.js",
    "assets/styles.css",
]

EXPECTED_22_LEDGERS = [
    "building_types", "goods", "unit_types", "estate_privileges", "laws",
    "government_reforms", "government_types", "road_types", "industry_types",
    "societal_values", "estate_actions", "cabinet_actions", "character_interactions",
    "bureaucracies", "town_rights", "subject_types", "diplomatic_actions",
    "international_organizations", "casus_belli", "wargoals", "religions",
    "situations_disasters",
]

BANNED_MACHINE_PHRASES = [
    "特殊单位 是",
    "每级岗位参数",
    "最高等级参数",
    "工期参数",
    "建材配方 ",
    "乡村 是",
    "集镇 是",
    "城市 是",
    "country_potential",
    "location_potential",
    "scope:actor",
    "has_or_had_tag",
    "驻军规模 0.1",
    "countrytax_base",
    "非（ 是）",
    "None（",
    "{T(",
]


def main() -> int:
    errors = []
    warnings = []

    # 1. File existence checks
    for fname in EXPECTED_HTML:
        p = DOCS / fname
        if not p.exists() or p.stat().st_size == 0:
            errors.append(f"Missing or empty HTML: {p}")

    for rel in EXPECTED_JS:
        p = DOCS / rel
        if not p.exists() or p.stat().st_size == 0:
            errors.append(f"Missing or empty asset: {p}")

    if not (DOCS / ".nojekyll").exists():
        errors.append("Missing docs/.nojekyll")

    icons = list((DOCS / "assets" / "goods-icons").glob("*.webp"))
    if len(icons) < 75:
        errors.append(f"Expected >= 75 goods icons, found {len(icons)}")

    # Verify all 22 modular ledger JS files
    for lid in EXPECTED_22_LEDGERS:
        lp = DOCS / "assets" / "ledgers" / f"{lid}.js"
        if not lp.exists() or lp.stat().st_size == 0:
            errors.append(f"Missing or empty modular ledger JS: {lp}")

    # Verify all 72 modular catalog JS files and 23,216 total records
    catalog_manifest = json.loads((DATA / "catalog_manifest.json").read_text(encoding="utf-8"))
    if len(catalog_manifest) != 72:
        errors.append(f"Expected 72 catalogs in catalog_manifest.json, found {len(catalog_manifest)}")
    total_cat_recs = sum(c.get("count", 0) for c in catalog_manifest)
    if total_cat_recs != 23216:
        errors.append(f"Expected 23216 total catalog records, found {total_cat_recs}")
    for cm in catalog_manifest:
        cp = DOCS / "assets" / "catalogs" / f"{cm['id']}.js"
        if not cp.exists() or cp.stat().st_size == 0:
            errors.append(f"Missing or empty modular catalog JS: {cp}")

    # Verify pop-demand-data.js (8 classes, 600 rows)
    pd_raw = (DOCS / "assets" / "pop-demand-data.js").read_text(encoding="utf-8")
    pd_obj = json.loads(pd_raw[pd_raw.index("{"):pd_raw.rindex("}") + 1])
    pd_classes = pd_obj.get("classes", [])
    pd_rows = sum(len(c.get("rows", [])) for c in pd_classes)
    if len(pd_classes) != 8 or pd_rows != 600:
        errors.append(f"Expected 8 pop-demand classes and 600 rows, found {len(pd_classes)} classes / {pd_rows} rows")

    # Verify metrics_summary.json & metrics-data.js
    metrics_raw = (DOCS / "assets" / "metrics-data.js").read_text(encoding="utf-8")
    metrics = json.loads(metrics_raw[metrics_raw.index("{"):metrics_raw.rindex("}") + 1])
    flagships = metrics.get("flagships", [])
    modifiers = metrics.get("modifiers", [])
    if len(flagships) < 60:
        errors.append(f"Expected >= 60 separated flagship metrics, found {len(flagships)}")
    for fm in flagships:
        if not fm.get("base_value"):
            errors.append(f"Flagship {fm.get('id')} missing base_value")
        if not fm.get("sub_modifiers"):
            errors.append(f"Flagship {fm.get('id')} missing sub_modifiers")
    if len(modifiers) < 1300:
        errors.append(f"Expected >= 1300 modifiers in metrics-data.js, found {len(modifiers)}")

    # 2. Load JSON data
    glossary = json.loads((DATA / "glossary.json").read_text(encoding="utf-8"))
    ledgers = json.loads((DATA / "ledgers.json").read_text(encoding="utf-8"))
    graph = json.loads((DATA / "graph_bundle.json").read_text(encoding="utf-8"))

    glossary_ids = {item["id"] for item in glossary}

    # Check goods icons referenced in ledgers exist
    for g in ledgers.get("goods", []):
        icon = g.get("icon")
        if icon:
            ip = DOCS / icon
            if not ip.exists():
                errors.append(f"Missing goods icon referenced in ledgers: {icon}")

    # Check glossary leaks or raw define names
    leak_patterns = [
        (r"\[GetDefine[^\]]*\]", "GetDefine tag"),
        (r"\[Concept\([^\]]*\)\]", "Concept tag"),
        (r"#[A-Za-z!]", "Paradox color/format code"),
        (r"\$[A-Za-z0-9_.\-]+\$", "Paradox variable"),
        (r"[A-Z]{2,}_[A-Z0-9_]+", "Raw un-substituted define symbol"),
    ]
    glossary_leaks = []
    for item in glossary:
        text = f"{item.get('zh', '')}\n{item.get('en', '')}\n{item.get('desc', '')}\n{item.get('desc_en', '')}"
        for pat, desc in leak_patterns:
            if re.search(pat, text):
                glossary_leaks.append((item["id"], desc, re.search(pat, text).group(0)))

    if glossary_leaks:
        errors.append(f"Glossary markup/symbol leaks ({len(glossary_leaks)}): {glossary_leaks[:10]}")

    # 3. Parse all HTML IDs first
    html_texts = {}
    html_ids = {}
    for fname in EXPECTED_HTML:
        p = DOCS / fname
        if not p.exists():
            continue
        txt = p.read_text(encoding="utf-8")
        html_texts[fname] = txt
        html_ids[fname] = set(re.findall(r'\bid="([^"]+)"', txt))

    # Runtime hash fragments handled dynamically by interactive.js / app.js
    metrics_routes = {f["id"] for f in flagships} | {f"mod:{m['id']}" for m in modifiers}
    dynamic_routes = {
        "metrics.html": metrics_routes,
        "ledgers.html": set(EXPECTED_22_LEDGERS),
        "directory.html": {cm["id"] for cm in catalog_manifest},
        "pop-demand.html": {c["id"] for c in pd_classes},
        "glossary.html": glossary_ids,
        "map.html": {n["id"] for n in graph.get("nodes", [])},
        "lab.html": {"redlines", "calc", "troubleshoot"},
    }

    missing_terms = set()
    dead_links = []

    for fname, txt in html_texts.items():
        # Check local hrefs
        for href in re.findall(r'href="([^"]+)"', txt):
            if href.startswith(("http://", "https://", "mailto:", "javascript:", "data:")):
                continue
            target_file, _, frag = href.partition("#")
            target_file = target_file or fname
            target_file = unquote(target_file)
            if target_file.startswith("assets/"):
                if not (DOCS / target_file).exists():
                    dead_links.append((fname, href, "missing asset"))
                continue
            if target_file not in html_texts:
                dead_links.append((fname, href, "missing page"))
                continue
            if frag:
                frag_clean = frag.split("?")[0]
                static_ok = frag_clean in html_ids[target_file]
                dynamic_ok = frag_clean in dynamic_routes.get(target_file, set())
                if not static_ok and not dynamic_ok:
                    dead_links.append((fname, href, f"missing anchor #{frag} in {target_file}"))

        # Check SVG/node data-jump
        for jump in re.findall(r'data-jump="([^"]+)"', txt):
            if jump.startswith("#"):
                frag = jump[1:]
                if frag not in html_ids[fname]:
                    dead_links.append((fname, f"data-jump={jump}", "missing local anchor"))
            else:
                target_file, _, frag = jump.partition("#")
                if target_file not in html_texts:
                    dead_links.append((fname, f"data-jump={jump}", "missing page"))
                elif frag and frag not in html_ids[target_file] and frag not in dynamic_routes.get(target_file, set()):
                    dead_links.append((fname, f"data-jump={jump}", "missing remote anchor"))

        # Check .term[data-concept]
        for cid in re.findall(r'data-concept="([^"]+)"', txt):
            if cid not in glossary_ids:
                missing_terms.add((fname, cid))

        # Check local src
        for src in re.findall(r'src="([^"]+)"', txt):
            if not src.startswith(("http://", "https://")):
                if not (DOCS / src).exists():
                    dead_links.append((fname, f"src={src}", "missing src"))

    # Check graph_bundle.json hrefs
    for node in graph.get("nodes", []):
        ch = node.get("href", "") or node.get("chapter", "")
        if ch:
            target_file, _, frag = ch.partition("#")
            if target_file not in html_texts:
                dead_links.append(("graph_bundle.json", ch, f"node {node['id']} missing page"))
            elif frag and frag not in html_ids[target_file] and frag not in dynamic_routes.get(target_file, set()):
                dead_links.append(("graph_bundle.json", ch, f"node {node['id']} missing anchor #{frag}"))

    for ts in graph.get("troubleshoot", []):
        ch = ts.get("href", "")
        if ch:
            target_file, _, frag = ch.partition("#")
            if target_file not in html_texts:
                dead_links.append(("graph_bundle.json", ch, "troubleshoot missing page"))
            elif frag and frag not in html_ids[target_file] and frag not in dynamic_routes.get(target_file, set()):
                dead_links.append(("graph_bundle.json", ch, f"troubleshoot missing anchor #{frag}"))

    # Check metrics_summary.json chapter_hrefs
    for f in flagships:
        ch = f.get("chapter_href", "")
        if ch:
            target_file, _, frag = ch.partition("#")
            if target_file not in html_texts:
                dead_links.append(("metrics_summary.json", ch, f"flagship {f['id']} missing page"))
            elif frag and frag not in html_ids[target_file] and frag not in dynamic_routes.get(target_file, set()):
                dead_links.append(("metrics_summary.json", ch, f"flagship {f['id']} missing anchor #{frag}"))

    if dead_links:
        errors.append(f"Dead links ({len(dead_links)}): {dead_links}")
    if missing_terms:
        errors.append(f"Unresolved .term data-concept IDs ({len(missing_terms)}): {sorted(missing_terms)}")

    # 4. Readability Quality Gate across HTML, Ledgers, and Catalogs
    machine_leaks = []
    for fname, txt in html_texts.items():
        for phrase in BANNED_MACHINE_PHRASES:
            if phrase in txt:
                machine_leaks.append((f"docs/{fname}", phrase))

    for lid in EXPECTED_22_LEDGERS:
        lp = DOCS / "assets" / "ledgers" / f"{lid}.js"
        if lp.exists():
            ltxt = lp.read_text(encoding="utf-8")
            for phrase in BANNED_MACHINE_PHRASES:
                if phrase in ltxt:
                    machine_leaks.append((f"ledgers/{lid}.js", phrase))

    for cm in catalog_manifest:
        cp = DOCS / "assets" / "catalogs" / f"{cm['id']}.js"
        if cp.exists():
            ctxt = cp.read_text(encoding="utf-8")
            for phrase in BANNED_MACHINE_PHRASES:
                if phrase in ctxt:
                    machine_leaks.append((f"catalogs/{cm['id']}.js", phrase))

    if machine_leaks:
        errors.append(f"Readability quality gate failed ({len(machine_leaks)} leaks): {machine_leaks[:15]}")

    # 5. Verify original eu5-atlas workspace untouched
    if ORIG_ATLAS.exists():
        res = subprocess.run(
            ["git", "status", "--short"],
            cwd=str(ORIG_ATLAS),
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        if res.returncode == 0 and res.stdout.strip():
            errors.append(f"Original eu5-atlas modified! git status: {res.stdout.strip()}")

    # Print summary
    print(f"HTML pages checked: {len(html_texts)}")
    print(f"Flagship metrics: {len(flagships)} | All modifiers: {len(modifiers)}")
    print(f"Ledgers: {len(EXPECTED_22_LEDGERS)} | Catalogs: {len(catalog_manifest)} ({total_cat_recs} records)")
    print(f"Glossary entries: {len(glossary_ids)} | Goods icons: {len(icons)}")
    print(f"Warnings: {len(warnings)}")
    for w in warnings:
        print("  WARN:", w)
    print(f"Errors: {len(errors)}")
    for e in errors:
        print("  ERR:", e)

    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
