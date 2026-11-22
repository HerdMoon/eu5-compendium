import json
import re
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
DATA = ROOT / "data"

EXPECTED_HTML = [
    "index.html",
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
    "map.html",
    "lab.html",
    "ledgers.html",
    "glossary.html",
]

EXPECTED_JS = [
    "assets/app.js",
    "assets/interactive.js",
    "assets/graph-data.js",
    "assets/glossary-data.js",
    "assets/ledgers-data.js",
    "assets/search-index.js",
    "assets/styles.css",
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

    # Runtime hash fragments handled dynamically by interactive.js / app.js (not static IDs)
    dynamic_routes = {
        "ledgers.html": {"goods", "societal_values", "estate_actions", "cabinet_actions", "character_interactions", "subject_types", "bureaucracies", "town_rights", "casus_belli", "situations_disasters"},
        "glossary.html": glossary_ids,
        "map.html": {n["id"] for n in graph.get("nodes", [])},
        "lab.html": {"redlines", "calc", "troubleshoot"},
    }

    missing_terms = set()
    dead_links = []
    raw_template_leaks = []

    for fname, txt in html_texts.items():
        # Check raw template syntax leaks
        if "{T(" in txt:
            raw_template_leaks.append((fname, "{T("))

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
                static_ok = frag in html_ids[target_file]
                dynamic_ok = frag in dynamic_routes.get(target_file, set())
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

    # Check graph_bundle.json chapter hrefs too
    for node in graph.get("nodes", []):
        ch = node.get("chapter", "")
        if ch:
            target_file, _, frag = ch.partition("#")
            if target_file not in html_texts:
                dead_links.append(("graph_bundle.json", ch, f"node {node['id']} missing page"))
            elif frag and frag not in html_ids[target_file]:
                dead_links.append(("graph_bundle.json", ch, f"node {node['id']} missing anchor #{frag}"))

    for rl in graph.get("redlines", []):
        ch = rl.get("chapter", "")
        if ch:
            target_file, _, frag = ch.partition("#")
            if target_file not in html_texts:
                dead_links.append(("graph_bundle.json", ch, f"redline {rl['name']} missing page"))
            elif frag and frag not in html_ids[target_file]:
                dead_links.append(("graph_bundle.json", ch, f"redline {rl['name']} missing anchor #{frag}"))

    if raw_template_leaks:
        errors.append(f"Raw template leaks: {raw_template_leaks}")
    if dead_links:
        errors.append(f"Dead links ({len(dead_links)}): {dead_links}")
    if missing_terms:
        errors.append(f"Unresolved .term data-concept IDs ({len(missing_terms)}): {sorted(missing_terms)}")

    # Print summary
    print(f"HTML pages checked: {len(html_texts)}")
    print(f"Glossary entries: {len(glossary_ids)}")
    print(f"Goods icons: {len(icons)}")
    print(f"Warnings: {len(warnings)}")
    for w in warnings:
        print("  WARN:", w)
    print(f"Errors: {len(errors)}")
    for e in errors:
        print("  ERR:", e)

    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
