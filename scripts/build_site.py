# -*- coding: utf-8 -*-
"""
Static Site Generator for 《欧陆风云 V · 系统图谱与速查典》 (EU5 1.4.9).
Outputs cleanly to docs/ with zero external dependencies and full offline file:// support.
"""
import json
import os
import re
import sys
from html import escape
from urllib.parse import quote

PROJ_DIR = r"C:\Users\seepath\.gemini\antigravity\scratch\eu5-compendium"
SCRIPTS_DIR = os.path.join(PROJ_DIR, "scripts")
DATA_DIR = os.path.join(PROJ_DIR, "data")
DOCS_DIR = os.path.join(PROJ_DIR, "docs")
ASSETS_DIR = os.path.join(DOCS_DIR, "assets")

sys.path.insert(0, SCRIPTS_DIR)
from chapters_1_5 import CHAPTERS_1_5
from chapters_6_10 import CHAPTERS_6_10
from chapters_11_12 import CHAPTERS_11_12
from svg_diagrams import CHAPTER_DIAGRAMS, build_home_svg

ALL_CHAPTERS = CHAPTERS_1_5 + CHAPTERS_6_10 + CHAPTERS_11_12
GLOSSARY_COUNT = 752


def load_json(name):
    with open(os.path.join(DATA_DIR, name), encoding="utf-8") as f:
        return json.load(f)


def build_sidebar(active_slug):
    tools = [
        ("index.html", "总览与导览 · Overview", "var(--accent)"),
        ("metrics.html", "核心数值与1,364修正反查", "#b52b3b"),
        ("ledgers.html", "22 大核心速查表 (含501建筑)", "var(--p-economy)"),
        ("directory.html", "全量 72 游戏名录库 (23,216条)", "var(--p-military)"),
        ("pop-demand.html", "人口商品需求矩阵 (8阶级×75货)", "var(--p-territory)"),
        ("map.html", "交互概念因果星图 (36节点)", "var(--accent-2)"),
        ("lab.html", "红线墙 / 实算器 / 排障台", "var(--p-state)"),
        ("glossary.html", f"双语百科词典 ({GLOSSARY_COUNT}词条)", "var(--p-culture)"),
    ]
    pillar_colors = {
        "territory": "var(--p-territory)",
        "economy": "var(--p-economy)",
        "state": "var(--p-state)",
        "culture": "var(--p-culture)",
        "military": "var(--p-military)",
        "diplomacy": "var(--p-diplomacy)",
    }

    tool_links = []
    for href, lbl, dot in tools:
        cls = "nav-link active" if active_slug == href else "nav-link"
        tool_links.append(f'<a href="{href}" class="{cls}"><span class="nav-dot" style="background:{dot}"></span><span>{escape(lbl)}</span></a>')

    ch_links = []
    for ch in ALL_CHAPTERS:
        cls = "nav-link active" if active_slug == ch["slug"] else "nav-link"
        dot = pillar_colors.get(ch["pillar"], "var(--accent)")
        ch_links.append(
            f'<a href="{ch["slug"]}" class="{cls}">'
            f'<span class="nav-dot" style="background:{dot}"></span>'
            f'<span>{ch["num"]} · {escape(ch["title"].split("、")[0].split("，")[0])}</span></a>'
        )

    return f'''<aside class="sidebar" aria-label="主导航">
  <a href="index.html" class="brand-box">
    <div class="brand-mark">V</div>
    <div class="brand-meta">
      <strong>欧陆风云 V · 图谱典</strong>
      <small>EU5 1.4.9 · COMPENDIUM</small>
    </div>
  </a>
  <div class="sidebar-controls">
    <button type="button" class="btn-pill btn-search" data-open-search>
      <span>秒查概念 / 数值</span>
      <span class="kbd">Ctrl+K</span>
    </button>
    <button type="button" class="btn-pill" data-theme-toggle title="切换明暗主题">☾</button>
  </div>
  <div class="nav-group">
    <div class="nav-caption">枢纽与速查工具</div>
    {"".join(tool_links)}
  </div>
  <div class="nav-group">
    <div class="nav-caption">六大支柱 · 十二章深度精讲</div>
    {"".join(ch_links)}
  </div>
  <div class="sidebar-foot">
    基准版本：EU5 1.4.9 (Build 26655995 / 3ed0)<br>
    底层校验：00_defines / 静态修正 / 本地化<br>
    悬停正文中虚线术语可即时查看释义
  </div>
</aside>'''


def wrap_page(title, desc, active_slug, page_kind, main_html, right_toc_html="", scripts=()):
    sidebar = build_sidebar(active_slug)
    grid_cls = "content-grid" if right_toc_html else "content-grid wide"
    toc_block = f'<aside class="toc-panel"><div class="toc-title">本页章节目录</div><div class="toc-list">{right_toc_html}</div></aside>' if right_toc_html else ""
    extra_scripts = "\n".join(f'<script defer src="{s}"></script>' for s in scripts)
    return f'''<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(title)} · 欧陆风云 V 系统图谱与速查典</title>
  <meta name="description" content="{escape(desc)}">
  <link rel="stylesheet" href="assets/styles.css">
  <script defer src="assets/glossary-data.js"></script>
  <script defer src="assets/search-index.js"></script>
  {extra_scripts}
  <script defer src="assets/app.js"></script>
  <script defer src="assets/interactive.js"></script>
</head>
<body data-page="{escape(page_kind)}">
  <a class="skip-link" href="#main">跳到正文</a>
  <header class="mobile-bar">
    <button type="button" class="btn-pill" data-nav-toggle>☰ 目录</button>
    <strong style="font-size:14px">{escape(title)}</strong>
    <div style="display:flex;gap:6px">
      <button type="button" class="btn-pill" data-open-search>搜</button>
      <button type="button" class="btn-pill" data-theme-toggle>☾</button>
    </div>
  </header>
  <div class="app-shell">
    {sidebar}
    <main id="main" class="main-area">
      <div class="{grid_cls}">
        <div class="article-col">{main_html}</div>
        {toc_block}
      </div>
    </main>
  </div>
  <div id="cmd-modal" class="cmd-backdrop" role="dialog" aria-modal="true" aria-label="全局快速检索">
    <div class="cmd-dialog">
      <div class="cmd-input-wrap">
        <span style="color:var(--ink-muted);font-weight:700">⌘</span>
        <input id="cmd-input" class="cmd-input" type="search" autocomplete="off" placeholder="输入中文概念、English、红线数字(如 75%、50%、90%)、内阁或阶层互动…">
        <span class="kbd">ESC</span>
      </div>
      <div id="cmd-results" class="cmd-results"></div>
    </div>
  </div>
</body>
</html>'''


def wrap_tables(html_str):
    return re.sub(r'(<table class="data-table">.*?</table>)', r'<div class="table-wrap">\1</div>', html_str, flags=re.S)


def build_chapters():
    pillar_names = {
        "territory": "支柱一 · 疆域与控制",
        "economy": "支柱二 · 人口、市场与财政",
        "state": "支柱三 · 政府、内阁与阶层",
        "culture": "支柱四 · 文化、信仰与科技",
        "military": "支柱五 · 军事、海权与和约",
        "diplomacy": "支柱六 · 外交、属国与国际秩序",
    }
    for i, ch in enumerate(ALL_CHAPTERS):
        pcol = f"var(--p-{ch['pillar']})"
        plabel = pillar_names[ch["pillar"]]

        up_lis = "".join(f'<li><a href="{href}">{escape(lbl)}</a>：{escape(note)}</li>' for lbl, href, note in ch["upstream"])
        down_lis = "".join(f'<li><a href="{href}">{escape(lbl)}</a>：{escape(note)}</li>' for lbl, href, note in ch["downstream"])

        diagram_fn = CHAPTER_DIAGRAMS[ch["id"]]
        svg_html = diagram_fn()

        secs_html = []
        toc_links = []
        for s in ch["sections"]:
            toc_links.append(f'<a href="#{s["id"]}">{escape(s["title"])}</a>')
            body = wrap_tables(s["html"])
            secs_html.append(f'''<section id="{s["id"]}" class="mech-section">
  <h2>{escape(s["title"])}</h2>
  <span class="sec-en">{escape(s["en"])}</span>
  {body}
</section>''')

        redlines_html = "".join(
            f'<div class="redline-item"><div class="redline-val">{escape(v)}</div><h4>{escape(t)}</h4><p>{escape(d)}</p></div>'
            for v, t, d in ch["redlines"]
        )
        toc_links.append('<a href="#redlines-strip">本章关键红线</a>')
        toc_links.append('<a href="#discussion-box">实战排障专栏</a>')

        qlinks_html = " · ".join(f'<a href="{href}" class="btn-pill">{escape(lbl)}</a>' for lbl, href in ch["quick_links"])
        prev_ch = ALL_CHAPTERS[i - 1] if i > 0 else None
        next_ch = ALL_CHAPTERS[i + 1] if i < len(ALL_CHAPTERS) - 1 else None
        prev_btn = f'<a href="{prev_ch["slug"]}" class="btn-pill">← {prev_ch["num"]} · {escape(prev_ch["title"])}</a>' if prev_ch else '<a href="index.html" class="btn-pill">← 返回总览首页</a>'
        next_btn = f'<a href="{next_ch["slug"]}" class="btn-pill">{next_ch["num"]} · {escape(next_ch["title"])} →</a>' if next_ch else '<a href="map.html" class="btn-pill">进入全站交互因果星图 →</a>'

        main_html = f'''
<section class="hero-banner">
  <div class="eyebrow"><span class="pillar-badge" style="background:{pcol}">{escape(plabel)}</span> <span>CHAPTER {ch["num"]}</span></div>
  <h1>{escape(ch["title"])}</h1>
  <p class="subtitle">{escape(ch["subtitle"])}</p>
  <div class="hero-meta-row">
    <span class="meta-chip">{escape(ch["en"])}</span>
    <span class="meta-chip">基准：EU5 1.4.9 (3ed0)</span>
  </div>
</section>

<div class="context-grid">
  <div class="context-box">
    <h4>↑ 上游输入（谁决定本章）</h4>
    <ul>{up_lis}</ul>
  </div>
  <div class="context-box">
    <h4>⚙ 本章核心机制引擎</h4>
    <p style="margin:0;font-size:13px">{escape(ch["engine"])}</p>
  </div>
  <div class="context-box">
    <h4>↓ 下游出口（本章驱动谁）</h4>
    <ul>{down_lis}</ul>
  </div>
</div>

{svg_html}

{"".join(secs_html)}

<section id="redlines-strip">
  <div class="redline-strip">{redlines_html}</div>
</section>

<section id="discussion-box" class="discussion-card">
  <h2>{escape(ch["discussion"]["title"])}</h2>
  {ch["discussion"]["html"]}
</section>

<div class="card" style="display:flex;flex-wrap:wrap;gap:8px;align-items:center;justify-content:space-between">
  <strong style="font-size:13.5px">关联速查与仿真工具：</strong>
  <div style="display:flex;flex-wrap:wrap;gap:8px">{qlinks_html}</div>
</div>

<nav class="ch-pager" aria-label="章节翻页">
  {prev_btn}
  {next_btn}
</nav>
'''
        html_out = wrap_page(ch["title"], ch["subtitle"], ch["slug"], "chapter", main_html, right_toc_html="".join(toc_links))
        with open(os.path.join(DOCS_DIR, ch["slug"]), "w", encoding="utf-8") as f:
            f.write(html_out)


def build_index(graph_bundle):
    home_svg = build_home_svg(graph_bundle["home_nodes"], graph_bundle["home_edges"])
    pillar_labels = {p["id"]: (p["zh"], p["color"]) for p in graph_bundle["pillars"]}
    ch_cards = []
    for ch in ALL_CHAPTERS:
        pzh, pcol = pillar_labels[ch["pillar"]]
        up_s = " · ".join(x[0] for x in ch["upstream"][:2])
        down_s = " · ".join(x[0] for x in ch["downstream"][:2])
        ch_cards.append(f'''<article class="ch-card">
  <div class="ch-card-head">
    <span class="ch-num">CH {ch["num"]}</span>
    <span class="pillar-badge" style="background:{pcol}">{escape(pzh)}</span>
  </div>
  <h3><a href="{ch["slug"]}">{escape(ch["title"])}</a></h3>
  <p>{escape(ch["subtitle"])}</p>
  <div class="ch-flow"><strong>链路：</strong>{escape(up_s)} → <strong>本章</strong> → {escape(down_s)}</div>
</article>''')

    hot_questions = [
        ("哪些因素能提升「加工生产效率」？", "metrics.html#production_efficiency"),
        ("「发展度」与「繁荣度」的区别及各自基准值？", "metrics.html#development"),
        ("501 种建筑造价、配方与效果全表", "ledgers.html#building_types"),
        ("最大控制力与月度控制力各自的基准值？", "metrics.html#max_control"),
        ("为什么已整合省份还不是核心(Core)？", "ch01-territory-core.html#integration-core"),
        ("王室力量与各阶层满意度均衡点基准值？", "ch05-estates-rebels.html#power-balance"),
        ("8 阶级各自消费哪些商品？", "pop-demand.html"),
        ("训练度、军事战术、围城与要塞防御拆解", "ch08-military-combat.html#battle-mechanics"),
    ]
    hot_pills = "".join(f'<a href="{h}" class="btn-pill">{escape(q)}</a>' for q, h in hot_questions)

    main_html = f'''
<section class="hero-banner">
  <div class="eyebrow">EUROPA UNIVERSALIS V · MECHANICS COMPENDIUM · 1.4.9</div>
  <h1>欧陆风云 V · 机制原理与全量数据速查典</h1>
  <p class="subtitle">面向具备基础认知、希望<strong>清晰掌握每一项独立数值的基准值、正负变化来源与系统间因果关系</strong>并<strong>快速检索可读游戏数据</strong>的玩家编写。完整覆盖 <strong>EU5 1.4.9 (Build 26655995 / 校验码 3ed0)</strong> 全部机制公式、<strong>66 项独立拆分核心数值（全标基准值 + 按词条分栏反查 1,364 项修正）</strong>、<strong>22 张精排数据表（含 501 建筑）</strong>、<strong>8×75 人口需求矩阵</strong>及<strong>可读化重构的全部 72 类 23,216 条游戏名录</strong>。</p>
  <div class="hero-meta-row">
    <span class="meta-chip">12 章系统机制与算例</span>
    <span class="meta-chip">66 项独立核心数值(含基准值) + 1,364 修正反查</span>
    <span class="meta-chip">22 大精排表 (含 501 建筑 / 401 兵种)</span>
    <span class="meta-chip">72 类 23,216 条中文可读名录</span>
    <span class="meta-chip">36 节点因果星图 + 实算器 + {GLOSSARY_COUNT} 词条</span>
  </div>
</section>

<div class="four-col">
  <a href="metrics.html" class="card" style="border-top:4px solid #b52b3b;text-decoration:none;color:inherit">
    <h3>① 66 项独立核心数值 &amp; 修正反查</h3>
    <p>发展度与繁荣度、晋升与降级、围城与要塞防御等全部拆分为独立条目，逐项标明官方基准值并按具体修正词条分栏反查。</p>
  </a>
  <a href="ledgers.html#building_types" class="card" style="border-top:4px solid var(--p-economy);text-decoration:none;color:inherit">
    <h3>② 22 大精排数据表 (含 501 建筑)</h3>
    <p>建筑 501（造价/建材/雇员/运转配方/修正）、兵种 401、特权 331、法律 213、改革 379、商品 75 支持排序与展开。</p>
  </a>
  <a href="directory.html" class="card" style="border-top:4px solid var(--p-military);text-decoration:none;color:inherit">
    <h3>③ 72 类全量可读名录 &amp; 需求表</h3>
    <p>直通清晰中文重构的 23,216 条名录（3,592 革新 / 4,213 事件 / 346 配方 / 163 成立国）与 <span style="color:var(--accent-2);font-weight:600">8×75 人口商品需求矩阵</span>。</p>
  </a>
  <a href="map.html" class="card" style="border-top:4px solid var(--accent-2);text-decoration:none;color:inherit">
    <h3>④ 36 节点因果星图 &amp; 实算器</h3>
    <p>交互点亮概念上下游传导链，搭配红线常量墙与财富分流、要塞留忠、属国连通、接敌概率计算器。</p>
  </a>
</div>

<section class="diagram-card">
  <figcaption class="diagram-head">
    <span>全局结构图 · 点击六大支柱模块直接进入对应篇章</span>
    <strong>《欧陆风云 V》六大系统核心流转全图</strong>
  </figcaption>
  <div class="diagram-scroll">{home_svg}</div>
</section>

<div class="card" style="margin-bottom:24px">
  <h3 style="margin-bottom:10px">玩家最高频「为什么 / 在哪查……」一秒直达</h3>
  <div style="display:flex;flex-wrap:wrap;gap:8px">{hot_pills}</div>
</div>

<h2 style="font-family:var(--font-serif);margin:0 0 14px">六大支柱 · 十二章全量深度因果精讲</h2>
<div class="chapter-grid">
  {"".join(ch_cards)}
</div>
'''
    html_out = wrap_page("全景总览", "欧陆风云 V (1.4.9) 系统因果图谱、缺失核心与阶层机制补全、红线速查典", "index.html", "home", main_html)
    with open(os.path.join(DOCS_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(html_out)


def build_map_page(graph_bundle):
    options = '<option value="all">显示全部六大支柱 (36 个核心枢纽节点)</option>' + "".join(
        f'<option value="{p["id"]}">仅突出：{escape(p["zh"])}</option>' for p in graph_bundle["pillars"]
    )
    main_html = f'''
<section class="hero-banner">
  <div class="eyebrow">INTERACTIVE CAUSAL ATLAS</div>
  <h1>全游戏 36 核心概念因果关系星图</h1>
  <p class="subtitle">点击图中任意概念卡片，即可高亮其<strong>所有直接上游决定因素（绿色）</strong>与<strong>直接下游受影响系统（红色）</strong>，查看精确公式与红线警告，并直达对应精讲小节。</p>
</section>

<div class="filter-bar">
  <label for="map-pillar-filter" style="font-size:13px;font-weight:700">按系统支柱筛选高亮：</label>
  <select id="map-pillar-filter" class="select-ctrl">{options}</select>
  <span style="font-size:12.5px;color:var(--ink-muted)">提示：图内可横向拖动或滚轮浏览；按下 <span class="kbd">Ctrl+K</span> 也能秒搜节点</span>
</div>

<div class="map-layout">
  <div class="map-canvas-box">
    <svg id="map-svg" viewBox="0 0 1380 795" class="map-svg" role="img" aria-label="EU5核心概念依赖星图"></svg>
  </div>
  <aside id="map-detail" class="map-detail">
    <h3>全景交互星图指南</h3>
    <p style="font-size:13.5px;color:var(--ink-muted)">请在左侧点击任意概念节点（如 <strong>核心领土</strong>、<strong>控制力</strong>、<strong>三级粮食链</strong>、<strong>阶层金库与私建</strong> 或 <strong>敌意与包围网</strong>），这里会立刻展开该系统的完整输入输出关系链。</p>
    <div style="display:flex;flex-wrap:wrap;gap:6px;margin-top:12px">
      <a href="#core" class="btn-pill">核心领土</a>
      <a href="#control" class="btn-pill">控制力</a>
      <a href="#food_system" class="btn-pill">三级粮食链</a>
      <a href="#estate_actions" class="btn-pill">阶层互动</a>
      <a href="#navy_maritime" class="btn-pill">海上存在(90%)</a>
      <a href="#antagonism" class="btn-pill">敌意包围网</a>
    </div>
  </aside>
</div>
'''
    html_out = wrap_page("交互概念因果星图", "36个EU5核心机制节点因果依存交互图", "map.html", "map", main_html, scripts=("assets/graph-data.js",))
    with open(os.path.join(DOCS_DIR, "map.html"), "w", encoding="utf-8") as f:
        f.write(html_out)


def build_lab_page(graph_bundle):
    pillar_opts = '<option value="all">全部六大支柱 (37 条)</option>' + "".join(
        f'<option value="{p["id"]}">{escape(p["zh"])}</option>' for p in graph_bundle["pillars"]
    )
    main_html = f'''
<section class="hero-banner">
  <div class="eyebrow">REDLINES · SIMULATORS · TROUBLESHOOTING</div>
  <h1>核心数值红线墙 · 4合1实算实验室 · 16症状排障台</h1>
  <p class="subtitle">所有常量与公式直接取自游戏 <code>00_defines.txt</code> 与静态修正文件（EU5 1.4.9）。用于速查临界值、实机验算地点分流和叛军要塞保卫概率。</p>
</section>

<div class="tab-bar">
  <button type="button" class="tab-btn active" data-lab-tab="redlines">37 条核心数值红线墙</button>
  <button type="button" class="tab-btn" data-lab-tab="calc">4 合 1 实机常数计算器</button>
  <button type="button" class="tab-btn" data-lab-tab="troubleshoot">16 大高频痛点排障表</button>
</div>

<div data-lab-panel="redlines">
  <div class="filter-bar">
    <input id="red-search" class="input-ctrl" type="search" placeholder="搜索红线数值或关键词（如 75%、50%、核心、海巡、破产、240）…">
    <select id="red-pillar" class="select-ctrl">{pillar_opts}</select>
  </div>
  <div id="redline-grid" class="glossary-grid"></div>
</div>

<div data-lab-panel="calc" hidden>
  <div class="calc-grid">
    <div class="calc-card">
      <h3>① 地点财富 → 控制力 → 国库 vs 阶层分流器</h3>
      <div class="calc-row">
        <label><span>首都/总督到达邻近度</span><span id="c1-prox-v">80%</span></label>
        <input id="c1-prox" type="range" min="0" max="100" value="80">
      </div>
      <div class="calc-row">
        <label><span>整合状态</span></label>
        <select id="c1-integ" class="select-ctrl" style="width:100%">
          <option value="-10">1. 未整合（征服）：−10% 上限</option>
          <option value="0">2. 殖民地：0% 上限</option>
          <option value="5">3. 已整合（内阁完成，核心文化&lt;50%）：+5% 上限</option>
          <option value="20" selected>4. 核心（Core，核心文化≥50%）：+20% 上限</option>
        </select>
      </div>
      <div class="calc-row">
        <label><span>其他上限加成（城级/满意度/提控内阁）</span><span id="c1-extra-v">+10%</span></label>
        <input id="c1-extra" type="range" min="-20" max="40" value="10">
      </div>
      <div class="calc-row">
        <label><span>名义地点满产月财富 (RGO+建筑)</span><span id="c1-wealth-v">10.0 杜卡特</span></label>
        <input id="c1-wealth" type="range" min="1" max="50" step="0.5" value="10">
      </div>
      <div class="calc-row">
        <label><span>所属市场接入度</span><span id="c1-access-v">90%</span></label>
        <input id="c1-access" type="range" min="10" max="100" value="90">
      </div>
      <div class="calc-row">
        <label><span>加权平均阶层有效税率</span><span id="c1-tax-v">25%</span></label>
        <input id="c1-tax" type="range" min="0" max="60" value="25">
      </div>
      <div id="c1-out" class="calc-result"></div>
    </div>

    <div class="calc-card">
      <h3>② 叛乱起义瞬间「要塞守军忠诚检定」演算器</h3>
      <div class="calc-row">
        <label><span>相关阶层当前满意度</span><span id="c2-sat-v">40%</span></label>
        <input id="c2-sat" type="range" min="0" max="100" value="40">
      </div>
      <div class="calc-row"><label><input id="c2-cat" type="checkbox" checked> 守军来自同一造反阶层类别 (−15)</label></div>
      <div class="calc-row"><label><input id="c2-unrest" type="checkbox"> 当地叛乱度低于 3 (+10)</label></div>
      <div class="calc-row"><label><input id="c2-cult" type="checkbox" checked> 所在地为本国主流文化 (+10)</label></div>
      <div class="calc-row"><label><input id="c2-rel" type="checkbox" checked> 所在地为本国主导宗教 (+10)</label></div>
      <div class="calc-row"><label><input id="c2-prog" type="checkbox"> 叛乱运动进度已越过 80% (−20！)</label></div>
      <div id="c2-out" class="calc-result"></div>
    </div>

    <div class="calc-card">
      <h3>③ 属国集团实力惩戒、领土连通 &amp; 强盟饱和</h3>
      <div class="calc-row">
        <label><span>全部属国在总合体中占比 (军/入/口)</span><span id="c3-sub-v">28%</span></label>
        <input id="c3-sub" type="range" min="0" max="70" value="28">
      </div>
      <div class="calc-row">
        <label><span>陆路连接经过 0% 控制地区数</span><span id="c3-areas-v">2 个 0%控地区</span></label>
        <input id="c3-areas" type="range" min="0" max="6" value="2">
      </div>
      <div class="calc-row">
        <label><span>已结盟列强盟友数量 (权重 1.0/个)</span><span id="c3-gp-v">2 个列强</span></label>
        <input id="c3-gp" type="range" min="0" max="5" value="2">
      </div>
      <div class="calc-row">
        <label><span>已结盟区域强权数量 (权重 0.5/个)</span><span id="c3-rp-v">1 个区域强权</span></label>
        <input id="c3-rp" type="range" min="0" max="6" value="1">
      </div>
      <div id="c3-out" class="calc-result"></div>
    </div>

    <div class="calc-card">
      <h3>④ 默认按日步进接敌概率 &amp; 兵种混编校验</h3>
      <div class="calc-row">
        <label><span>军团有效主动性 (Initiative)</span><span id="c4-init-v">8</span></label>
        <input id="c4-init" type="range" min="0" max="15" value="8">
      </div>
      <div class="calc-row">
        <label><span>作战已持续天数</span><span id="c4-days-v">第 3 天</span></label>
        <input id="c4-days" type="range" min="0" max="12" value="3">
      </div>
      <div class="calc-row">
        <label><span>单一最大兵种类别兵力占比</span><span id="c4-share-v">45%</span></label>
        <input id="c4-share" type="range" min="20" max="100" value="45">
      </div>
      <div class="calc-row">
        <label><span>所含独立兵种类别总数</span><span id="c4-cats-v">3 种类别</span></label>
        <input id="c4-cats" type="range" min="1" max="5" value="3">
      </div>
      <div id="c4-out" class="calc-result"></div>
    </div>
  </div>
</div>

<div data-lab-panel="troubleshoot" hidden>
  <div class="filter-bar">
    <input id="ts-search" class="input-ctrl" type="search" placeholder="输入症状关键词（例如：核心、买粮、征召、阶层建筑、巡逻、PU、包围网）…">
  </div>
  <div id="troubleshoot-list"></div>
</div>
'''
    html_out = wrap_page("红线墙与实算排障台", "EU5 1.4.9 核心常量红线、4合1交互实算器、16高频症状排障表", "lab.html", "lab", main_html, scripts=("assets/graph-data.js",))
    with open(os.path.join(DOCS_DIR, "lab.html"), "w", encoding="utf-8") as f:
        f.write(html_out)


def build_ledgers_page():
    main_html = '''
<section class="hero-banner">
  <div class="eyebrow">DATA COMPENDIUM · 22 STRUCTURED LEDGERS · 1.4.9</div>
  <h1>22 大核心实战数据速查表（含 501 建筑全表）</h1>
  <p class="subtitle">完整囊括 <strong>501 建筑、75 实图商品、401 兵种单位、331 阶层特权、213 法律、379 政府改革、5 大政体、4 道路、8 产业政策、194 外交行动、37 国际组织、293 宗教、78 战争目标、113 宣战理由、81 内阁、60 官僚、75 城镇特权、34 角色互动、22 属国、17 价值观、12 阶层互动、24 局势与 38 灾难</strong>。全部支持按列点击排序、按需分片瞬时加载及展开源码明细。</p>
</section>

<div id="ledger-tabs" class="tab-groups"></div>

<div class="filter-bar">
  <input id="ledger-search" class="input-ctrl" type="search" placeholder="输入中文名、英文名、ID、前置条件或效果数值过滤…">
  <select id="ledger-subfilter" class="select-ctrl"></select>
  <span id="ledger-count" style="font-size:12.5px;color:var(--ink-muted)"></span>
</div>

<div class="table-wrap">
  <table class="data-table">
    <thead id="ledger-thead"></thead>
    <tbody id="ledger-tbody"></tbody>
  </table>
</div>
<div id="ledger-pager" class="pager-bar" hidden></div>
'''
    html_out = wrap_page("22 大核心数据速查表", "EU5 1.4.9 建筑501、兵种401、特权331、法律213、改革379、商品与外交全精排数据表", "ledgers.html", "ledgers", main_html)
    with open(os.path.join(DOCS_DIR, "ledgers.html"), "w", encoding="utf-8") as f:
        f.write(html_out)


def build_pop_demand_page():
    main_html = '''
<section class="hero-banner">
  <div class="eyebrow">POPULATION DEMAND MATRIX · 8 CLASSES × 75 GOODS</div>
  <h1>八大社会阶级商品消费需求矩阵（600 项精细参数）</h1>
  <p class="subtitle">基于游戏内 <code>in_game/common/goods_demand/pop_demands.txt</code> 与 <code>pop_types/00_default.txt</code> 抽取。精确展示贵族、教士、市民、农民、劳工、士兵、奴隶与部落民八大阶级对全游戏 75 种商品的基准需求、阶级倍率、基础价支出及冬季/地形/财富/识字触发门槛。</p>
</section>

<div id="pd-tabs" class="tab-bar"></div>

<div class="filter-bar">
  <input id="pd-search" class="input-ctrl" type="search" placeholder="搜索商品名、English 或冬夏/地形条件…">
  <label style="display:inline-flex;align-items:center;gap:6px;font-size:13px;font-weight:600;cursor:pointer">
    <input id="pd-nonzero" type="checkbox" checked> 仅显示有基础需求的商品
  </label>
  <span id="pd-count" style="font-size:12.5px;color:var(--ink-muted)"></span>
</div>

<div class="table-wrap">
  <table class="data-table">
    <thead id="pd-thead"></thead>
    <tbody id="pd-tbody"></tbody>
  </table>
</div>
'''
    html_out = wrap_page("人口商品需求矩阵", "EU5 八大社会阶级对 75 种商品的基准消费量与环境解锁条件全矩阵", "pop-demand.html", "pop-demand", main_html, scripts=("assets/pop-demand-data.js",))
    with open(os.path.join(DOCS_DIR, "pop-demand.html"), "w", encoding="utf-8") as f:
        f.write(html_out)


def build_directory_page():
    main_html = '''
<section class="hero-banner">
  <div class="eyebrow">FULL GAME DIRECTORY · 72 CATALOGS · 23,216 RECORDS</div>
  <h1>全游戏 72 类底层名录完全典藏库（23,216 条）</h1>
  <p class="subtitle">完整囊括原版游戏目录抽出的全部 <strong>72 个类别共 23,216 条定义</strong>——包含 <strong>3,592 时代革新、4,213 国别历史事件、2,354 国家开局资料、2,087 文化、832 法律政策、528 语言、346 建筑配方、178 决议、163 可成立国家、161 议题、150 特质、127 神祇、257 圣地、87 成就与 31 开局规则</strong> 等。所有列表按需分片毫秒懒加载并支持条件展开与源码溯源。</p>
</section>

<div id="dir-pillar-tabs" class="tab-bar"></div>
<div id="dir-picker" class="catalog-picker"></div>

<div id="dir-active-head" class="card" style="display:flex;flex-wrap:wrap;justify-content:space-between;align-items:center;gap:10px;margin-bottom:14px;padding:12px 16px"></div>

<div class="filter-bar">
  <input id="dir-search" class="input-ctrl" type="search" placeholder="在当前名录中按中文名、English、ID、条件或文本筛选…">
  <select id="dir-scope" class="select-ctrl"></select>
  <span id="dir-count" style="font-size:12.5px;color:var(--ink-muted)"></span>
</div>

<div class="table-wrap">
  <table class="data-table">
    <thead><tr><th>条目标题 / ID</th><th>适用口径</th><th>定义机制与前置触发条件</th><th>游戏源文件位置</th></tr></thead>
    <tbody id="dir-tbody"></tbody>
  </table>
</div>
<div id="dir-pager" class="pager-bar" hidden></div>
'''
    html_out = wrap_page("全游戏 72 类名录典藏库", "EU5 1.4.9 全游戏 72 大类别共 23,216 条完整数据结构化名录检索库", "directory.html", "directory", main_html, scripts=("assets/catalog-manifest.js",))
    with open(os.path.join(DOCS_DIR, "directory.html"), "w", encoding="utf-8") as f:
        f.write(html_out)


def build_metrics_page(graph_bundle):
    fm_total = len(load_json("metrics_summary.json").get("flagships", []))
    pillar_opts = f'<option value="all">全部六大支柱 ({fm_total} 项独立核心机制数值)</option>' + "".join(
        f'<option value="{p["id"]}">{escape(p["zh"])}</option>' for p in graph_bundle["pillars"]
    )
    main_html = f'''
<section class="hero-banner">
  <div class="eyebrow">SEPARATED METRICS · BASE VALUES · 1,364 MODIFIER SOURCES · EU5 1.4.9</div>
  <h1>{fm_total} 项独立核心数值拆解（含基准值） &amp; 1,364 项修正来源反查器</h1>
  <p class="subtitle">所有易混淆数值（如<strong>发展度 vs 繁荣度</strong>、<strong>最大控制力 vs 月度控制力</strong>、<strong>晋升速度 vs 降级速度</strong>、<strong>围城能力 vs 要塞防御</strong>、<strong>文化影响力 vs 文化传统</strong>）均已<strong>完全拆分为独立条目</strong>：每项先标明官方 <code>country_base_values / location_base_values / 00_defines.txt</code> <strong>基准值与范围</strong>，再逐类说明正负变化，展开后<strong>按具体修正词条分栏展示来源</strong>，绝不混同。</p>
</section>

<div class="tab-bar">
  <button type="button" class="tab-btn active" data-met-tab="flagships">{fm_total} 项独立核心数值拆解（含基准值）</button>
  <button type="button" class="tab-btn" data-met-tab="allmods">全游戏 1,364 项修正词条全量反查</button>
</div>

<div data-met-panel="flagships">
  <div class="filter-bar">
    <input id="fm-search" class="input-ctrl" type="search" placeholder="搜索独立数值、基准值或来源（如：发展度、繁荣度、生产效率、最大控制力、要塞防御、训练度、识字率）…">
    <select id="fm-pillar" class="select-ctrl">{pillar_opts}</select>
    <span id="fm-count" style="font-size:12.5px;color:var(--ink-muted)"></span>
  </div>
  <div id="fm-list" class="metrics-stack"></div>
</div>

<div data-met-panel="allmods" hidden>
  <div class="filter-bar">
    <input id="am-search" class="input-ctrl" type="search" placeholder="搜索全部 1,364 项修正中文名、英文名、代码键或来源建筑/改革/特权…">
    <select id="am-cat" class="select-ctrl"></select>
    <span id="am-count" style="font-size:12.5px;color:var(--ink-muted)"></span>
  </div>
  <div class="table-wrap">
    <table class="data-table">
      <thead><tr><th>修正名称 / 代码键</th><th>作用层级</th><th>来源总数</th><th>主要来源类别预览（点击展开全部具体条目与数值）</th></tr></thead>
      <tbody id="am-tbody"></tbody>
    </table>
  </div>
  <div id="am-pager" class="pager-bar" hidden></div>
</div>
'''
    html_out = wrap_page(
        "核心数值与修正来源反查器",
        "EU5 1.4.9 31项核心数值影响因素详解与全游戏1,364项修正来源反查表",
        "metrics.html",
        "metrics",
        main_html,
        scripts=("assets/metrics-data.js",),
    )
    with open(os.path.join(DOCS_DIR, "metrics.html"), "w", encoding="utf-8") as f:
        f.write(html_out)


def build_glossary_page(graph_bundle):
    pillar_opts = f'<option value="all">全部六大支柱 ({GLOSSARY_COUNT} 条)</option>' + "".join(
        f'<option value="{p["id"]}">{escape(p["zh"])}</option>' for p in graph_bundle["pillars"]
    )
    main_html = f'''
<section class="hero-banner">
  <div class="eyebrow">BILINGUAL ENCYCLOPEDIA · {GLOSSARY_COUNT} ENTRIES</div>
  <h1>官方百科全量与深度机制双语词典</h1>
  <p class="subtitle">直接从 EU5 1.4.9 游戏内 <code>game_concepts_l_simp_chinese.yml</code> 与 <code>00_defines.txt</code> 提取并彻底解析掉脚本标签，补全了核心（Core）、整合状态、阶层互动与阶级定义等关键内容。</p>
</section>

<div class="filter-bar">
  <input id="gloss-search" class="input-ctrl" type="search" placeholder="搜索中文术语、English、英文 ID 或定义文字…">
  <select id="gloss-pillar" class="select-ctrl">{pillar_opts}</select>
  <span id="gloss-count" style="font-size:12.5px;color:var(--ink-muted)"></span>
</div>

<div id="gloss-grid" class="glossary-grid"></div>
'''
    html_out = wrap_page("双语官方百科词典", f"EU5 1.4.9 全量 {GLOSSARY_COUNT} 条清洗版双语游戏概念词典", "glossary.html", "glossary", main_html)
    with open(os.path.join(DOCS_DIR, "glossary.html"), "w", encoding="utf-8") as f:
        f.write(html_out)


def build_js_bundles(graph_bundle, glossary):
    with open(os.path.join(ASSETS_DIR, "graph-data.js"), "w", encoding="utf-8") as f:
        f.write("window.__EU5_GRAPH__ = " + json.dumps(graph_bundle, ensure_ascii=False) + ";\n")

    with open(os.path.join(ASSETS_DIR, "glossary-data.js"), "w", encoding="utf-8") as f:
        f.write("window.__EU5_GLOSSARY__ = " + json.dumps(glossary, ensure_ascii=False) + ";\n")

    old_ledgers_js = os.path.join(ASSETS_DIR, "ledgers-data.js")
    if os.path.exists(old_ledgers_js):
        os.remove(old_ledgers_js)

    ledger_summary = load_json("rich_ledgers_summary.json")
    catalog_manifest = load_json("catalog_manifest.json")
    pd_summary = load_json("pop_demand_summary.json")
    metrics_summary = load_json("metrics_summary.json")

    # Build comprehensive global search index for Ctrl+K Command Palette
    search_items = []
    # 66 Separated Flagship Metrics & top 500 Modifiers (high priority!)
    for fm in metrics_summary.get("flagships", []):
        search_items.append({
            "title": f"核心数值：{fm['zh']} ({fm['en']})",
            "sub": f"基准值：{fm.get('base_value', '')[:85]}…（关联 {fm['total_sources']} 处来源）",
            "href": f"metrics.html#{fm['id']}",
            "kind": "核心数值",
            "kw": fm["id"],
        })
    for m in metrics_summary.get("modifiers", []):
        search_items.append({
            "title": f"修正反查：{m['zh']} ({m['en']})",
            "sub": f"{m['cat']} · 共 {m['total']} 处建筑/特权/改革/革新来源",
            "href": f"metrics.html#mod:{m['id']}",
            "kind": "修正来源",
            "kw": m["id"],
        })
    # Chapters & sections (all 12)
    for ch in ALL_CHAPTERS:
        search_items.append({
            "title": f"{ch['num']} · {ch['title']}",
            "sub": ch["subtitle"],
            "href": ch["slug"],
            "kind": "章节",
            "kw": ch["en"],
        })
        for sec in ch["sections"]:
            search_items.append({
                "title": sec["title"],
                "sub": f"第 {ch['num']} 章 · {sec['en']}",
                "href": f"{ch['slug']}#{sec['id']}",
                "kind": "小节",
                "kw": ch["title"],
            })

    # Map Nodes
    for n in graph_bundle["nodes"]:
        search_items.append({
            "title": f"星图：{n['zh']} ({n['en']})",
            "sub": n["summary"],
            "href": f"map.html#{n['id']}",
            "kind": "核心星图",
            "kw": n["formula"] + " " + n["redline"],
        })

    # Redlines
    for r in graph_bundle["redlines"]:
        search_items.append({
            "title": f"红线 {r['value']} · {r['title']}",
            "sub": r["desc"],
            "href": "lab.html#redlines",
            "kind": "红线常数",
            "kw": r["key"],
        })

    # Troubleshoot
    for t in graph_bundle["troubleshoot"]:
        search_items.append({
            "title": t["symptom"],
            "sub": t["fix"],
            "href": t["href"],
            "kind": "症状排障",
            "kw": t["cause"],
        })

    # Pop-Demand class portals
    for c in pd_summary:
        search_items.append({
            "title": f"人口消费矩阵：{c['zh']} ({c['en']})",
            "sub": f"涵盖全部 {c['total']} 种商品消费参数（其中 {c['non_zero']} 种含基准需求）",
            "href": f"pop-demand.html#{c['id']}",
            "kind": "人口需求",
            "kw": c["id"],
        })

    # All 72 Catalog portals
    for cm in catalog_manifest:
        search_items.append({
            "title": f"全量名录：{cm['zh']} ({cm['en']} · {cm['count']} 条)",
            "sub": f"原盘名录分类 {cm['id']}，点击立即按需载入筛选检索",
            "href": f"directory.html#{cm['id']}",
            "kind": "72名录入口",
            "kw": cm["id"],
        })

    # All 22 rich ledgers records (2,995 entries incl. 501 buildings, 401 units, 331 privileges, etc.)
    LEDGER_LABELS = [
        ("building_types", "建筑"),
        ("goods", "商品"),
        ("unit_types", "军事单位"),
        ("estate_privileges", "阶层特权"),
        ("laws", "法律"),
        ("government_reforms", "政府改革"),
        ("government_types", "政体"),
        ("road_types", "道路"),
        ("industry_types", "产业政策"),
        ("societal_values", "社会价值观"),
        ("estate_actions", "阶层互动"),
        ("cabinet_actions", "内阁行动"),
        ("character_interactions", "角色互动"),
        ("bureaucracies", "官僚部门"),
        ("town_rights", "城镇特权"),
        ("subject_types", "属国类型"),
        ("diplomatic_actions", "外交行动"),
        ("international_organizations", "国际组织"),
        ("casus_belli", "宣战理由"),
        ("wargoals", "战争目标"),
        ("religions", "宗教"),
        ("situations_disasters", "局势灾难"),
    ]
    for k, lbl in LEDGER_LABELS:
        for item in ledger_summary.get(k, []):
            q_part = quote(item["zh"]) if item.get("zh") else ""
            href = f"ledgers.html#{k}?q={q_part}" if q_part else f"ledgers.html#{k}"
            search_items.append({
                "title": f"{item['zh']} ({item.get('en') or item['id']})",
                "sub": f"{lbl} · {item.get('sub', '')}",
                "href": href,
                "kind": lbl,
                "kw": item["id"],
            })

    # Glossary entries
    for g in glossary:
        search_items.append({
            "title": f"{g['zh']} ({g['en']})",
            "sub": g["desc"][:110],
            "href": f"glossary.html#{g['id']}",
            "kind": "百科词条",
            "kw": g["id"],
        })

    with open(os.path.join(ASSETS_DIR, "search-index.js"), "w", encoding="utf-8") as f:
        f.write("window.__EU5_SEARCH__ = " + json.dumps(search_items, ensure_ascii=False) + ";\n")

    print(f"Built JS bundles. Search index entries: {len(search_items)}")


def main():
    global GLOSSARY_COUNT
    os.makedirs(DOCS_DIR, exist_ok=True)
    os.makedirs(ASSETS_DIR, exist_ok=True)

    graph_bundle = load_json("graph_bundle.json")
    glossary = load_json("glossary.json")
    GLOSSARY_COUNT = len(glossary)

    build_js_bundles(graph_bundle, glossary)
    build_chapters()
    build_index(graph_bundle)
    build_metrics_page(graph_bundle)
    build_map_page(graph_bundle)
    build_lab_page(graph_bundle)
    build_ledgers_page()
    build_pop_demand_page()
    build_directory_page()
    build_glossary_page(graph_bundle)

    # Write GitHub Pages helper files
    with open(os.path.join(DOCS_DIR, ".nojekyll"), "w", encoding="utf-8") as f:
        f.write("")
    with open(os.path.join(PROJ_DIR, ".gitignore"), "w", encoding="utf-8") as f:
        f.write("__pycache__/\n*.pyc\n.DS_Store\n")

    html_files = [fn for fn in sorted(os.listdir(DOCS_DIR)) if fn.endswith(".html")]
    print(f"Generated {len(html_files)} HTML pages: {html_files}")


if __name__ == "__main__":
    main()
