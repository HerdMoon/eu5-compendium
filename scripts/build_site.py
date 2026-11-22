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

PROJ_DIR = r"C:\Users\seepath\.gemini\antigravity\scratch\eu5-compendium"
SCRIPTS_DIR = os.path.join(PROJ_DIR, "scripts")
DATA_DIR = os.path.join(PROJ_DIR, "data")
DOCS_DIR = os.path.join(PROJ_DIR, "docs")
ASSETS_DIR = os.path.join(DOCS_DIR, "assets")

sys.path.insert(0, SCRIPTS_DIR)
from chapters_1_5 import CHAPTERS_1_5
from chapters_6_10 import CHAPTERS_6_10
from svg_diagrams import CHAPTER_DIAGRAMS, build_home_svg

ALL_CHAPTERS = CHAPTERS_1_5 + CHAPTERS_6_10
GLOSSARY_COUNT = 752


def load_json(name):
    with open(os.path.join(DATA_DIR, name), encoding="utf-8") as f:
        return json.load(f)


def build_sidebar(active_slug):
    tools = [
        ("index.html", "总览与导览 · Overview", "var(--accent)"),
        ("map.html", "交互概念因果星图 (36节点)", "var(--accent-2)"),
        ("lab.html", "红线墙 / 实算器 / 排障台", "var(--p-state)"),
        ("ledgers.html", "10 大高频实战数据典", "var(--p-economy)"),
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
    <div class="nav-caption">六大支柱 · 十章体系精讲</div>
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
        ("为什么整合完还不是核心(Core)？", "ch01-territory-core.html#integration-core"),
        ("12 项阶层互动与市民无息抽水", "ch05-estates-rebels.html#estate-interactions"),
        ("国库为何因「自动买粮」暴跌破产？", "ch02-population-food.html#food-chain"),
        ("自动海巡 90% 就跑怎么锁 100%？", "ch09-navy-war-peace.html#maritime-presence"),
        ("81 项内阁行动瓶颈怎么排？", "ch04-government-cabinet.html#cabinet-actions"),
        ("叛军起义要塞怎么全叛变了？", "lab.html#calc"),
        ("高产工坊为何不进国库反喂阶层？", "ch03-economy-market-trade.html#wealth-to-treasury"),
        ("如何用属国减半敌意(AE)与解 PU？", "ch10-diplomacy-subjects.html#subjects-annex"),
    ]
    hot_pills = "".join(f'<a href="{h}" class="btn-pill">{escape(q)}</a>' for q, h in hot_questions)

    main_html = f'''
<section class="hero-banner">
  <div class="eyebrow">EUROPA UNIVERSALIS V · MECHANICS COMPENDIUM</div>
  <h1>欧陆风云 V · 系统图谱与速查典</h1>
  <p class="subtitle">专为已经跨过基础扫盲、想彻底打通<strong>概念之间因果联结</strong>并随时<strong>按红线与名录反查实数</strong>的进阶玩家设计。全书基于本地 <strong>1.4.9 (Build 26655995 / 校验码 3ed0)</strong> 定义文件、静态修正与本地化重写梳理。</p>
  <div class="hero-meta-row">
    <span class="meta-chip">10 章因果精讲</span>
    <span class="meta-chip">36 节点交互依赖星图</span>
    <span class="meta-chip">37 条决定胜负的红线常数</span>
    <span class="meta-chip">4 合 1 实算模拟器</span>
    <span class="meta-chip">10 大高频数据典 + {GLOSSARY_COUNT} 双语词条</span>
  </div>
</section>

<div class="three-col">
  <a href="map.html" class="card" style="border-top:4px solid var(--accent-2);text-decoration:none;color:inherit">
    <h3>① 看懂系统连带：36 节点星图</h3>
    <p>搞不清「控制力」「阶层金库」「市场接入度」「核心」互相谁影响谁？点一下节点直接亮出绿线原因与红线后果。</p>
  </a>
  <a href="lab.html" class="card" style="border-top:4px solid var(--p-state);text-decoration:none;color:inherit">
    <h3>② 秒查红线、演练实算与排障</h3>
    <p>一站查尽 37 条核心红线（50%核心、25%征召、75%拆楼、90%海巡、100年破产信用），附四台交互实算器与 16 症状逆查表。</p>
  </a>
  <a href="ledgers.html" class="card" style="border-top:4px solid var(--p-economy);text-decoration:none;color:inherit">
    <h3>③ 极速翻查 10 大底层数据典</h3>
    <p>75 带图商品、17 对社会价值观、12 阶层互动、81 内阁行动、34 角色互动、22 属国类型、60 官僚、75 城镇特权、113 宣战理由、24 局势与 38 灾难。</p>
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
  <h3 style="margin-bottom:10px">玩家最高频「为什么……」一秒直达</h3>
  <div style="display:flex;flex-wrap:wrap;gap:8px">{hot_pills}</div>
</div>

<h2 style="font-family:var(--font-serif);margin:0 0 14px">六大支柱 · 十章深度因果精讲</h2>
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
  <div class="eyebrow">DATA COMPENDIUM · 1.4.9</div>
  <h1>10 大高频实战数据速查典</h1>
  <p class="subtitle">涵盖 75 种商品实值、17 对社会价值观轴线、12 项阶层互动与绝境求助、81 项内阁行动、34 项角色互动、22 种属国类型、60 官僚部门、75 城镇特权、113 宣战理由以及局势灾难总表，全部经由中文结构化清洗。</p>
</section>

<div id="ledger-tabs" class="tab-bar"></div>

<div class="filter-bar">
  <input id="ledger-search" class="input-ctrl" type="search" placeholder="输入中文名、英文名、ID 或数值效果过滤…">
  <select id="ledger-subfilter" class="select-ctrl"></select>
  <span id="ledger-count" style="font-size:12.5px;color:var(--ink-muted)"></span>
</div>

<div class="table-wrap">
  <table class="data-table">
    <thead id="ledger-thead"></thead>
    <tbody id="ledger-tbody"></tbody>
  </table>
</div>
'''
    html_out = wrap_page("高频实战数据典", "EU5 商品、社会价值观、阶层互动、内阁、角色、属国、官僚与宣战理由速查", "ledgers.html", "ledgers", main_html, scripts=("assets/ledgers-data.js",))
    with open(os.path.join(DOCS_DIR, "ledgers.html"), "w", encoding="utf-8") as f:
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


def build_js_bundles(graph_bundle, glossary, ledgers):
    with open(os.path.join(ASSETS_DIR, "graph-data.js"), "w", encoding="utf-8") as f:
        f.write("window.__EU5_GRAPH__ = " + json.dumps(graph_bundle, ensure_ascii=False) + ";\n")

    with open(os.path.join(ASSETS_DIR, "glossary-data.js"), "w", encoding="utf-8") as f:
        f.write("window.__EU5_GLOSSARY__ = " + json.dumps(glossary, ensure_ascii=False) + ";\n")

    with open(os.path.join(ASSETS_DIR, "ledgers-data.js"), "w", encoding="utf-8") as f:
        f.write("window.__EU5_LEDGERS__ = " + json.dumps(ledgers, ensure_ascii=False) + ";\n")

    # Build global search index for Ctrl+K Command Palette
    search_items = []
    # Chapters & sections
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

    # Ledger highlights
    for k, lbl in [
        ("estate_actions", "阶层互动"),
        ("cabinet_actions", "内阁行动"),
        ("character_interactions", "角色互动"),
        ("subject_types", "属国类型"),
        ("societal_values", "社会价值观"),
        ("goods", "商品"),
        ("bureaucracies", "官僚部门"),
        ("town_rights", "城镇特权"),
        ("casus_belli", "宣战理由"),
    ]:
        for item in ledgers.get(k, []):
            search_items.append({
                "title": f"{item['zh']} ({item.get('en', item['id'])})",
                "sub": f"{lbl} · {item.get('effect') or item.get('detail') or item.get('left_effects') or ''}"[:110],
                "href": f"ledgers.html#{k}",
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
    ledgers = load_json("ledgers.json")
    GLOSSARY_COUNT = len(glossary)

    build_js_bundles(graph_bundle, glossary, ledgers)
    build_chapters()
    build_index(graph_bundle)
    build_map_page(graph_bundle)
    build_lab_page(graph_bundle)
    build_ledgers_page()
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
