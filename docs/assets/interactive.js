(() => {
  "use strict";
  const esc = (s) => (window.eu5EscapeHtml ? window.eu5EscapeHtml(s) : String(s ?? ""));

  // Global lazy-load registries for 22 ledgers and 72 catalogs
  const ledgerCache = {};
  const catalogCache = {};
  const scriptPromises = {};

  window.__EU5_LEDGER_REGISTER__ = (id, rows) => {
    ledgerCache[id] = rows || [];
  };
  window.__EU5_CATALOG_REGISTER__ = (id, obj) => {
    catalogCache[id] = obj || { records: [] };
  };

  function loadScriptOnce(src) {
    if (scriptPromises[src]) return scriptPromises[src];
    scriptPromises[src] = new Promise((resolve, reject) => {
      const s = document.createElement("script");
      s.src = src;
      s.async = true;
      s.onload = () => resolve();
      s.onerror = () => reject(new Error("Failed to load " + src));
      document.head.appendChild(s);
    });
    return scriptPromises[src];
  }

  function sortRows(rows, key, dir, isNumeric, rawValFn) {
    const mult = dir === "desc" ? -1 : 1;
    return [...rows].sort((a, b) => {
      let va = rawValFn ? rawValFn(a) : (a._num && a._num[key] !== undefined ? a._num[key] : a[key]);
      let vb = rawValFn ? rawValFn(b) : (b._num && b._num[key] !== undefined ? b._num[key] : b[key]);
      if (isNumeric) {
        const na = parseFloat(String(va ?? "").replace(/[^0-9.\-]/g, ""));
        const nb = parseFloat(String(vb ?? "").replace(/[^0-9.\-]/g, ""));
        const fa = Number.isFinite(na) ? na : -Infinity;
        const fb = Number.isFinite(nb) ? nb : -Infinity;
        if (fa !== fb) return (fa - fb) * mult;
      }
      return String(va ?? "").localeCompare(String(vb ?? ""), "zh-Hans-CN", { numeric: true }) * mult;
    });
  }

  function renderDetailDrawer(r, colspan) {
    const pairs = [];
    if (Array.isArray(r.detail_pairs) && r.detail_pairs.length) {
      r.detail_pairs.forEach(([k, v]) => pairs.push([k, v]));
    } else {
      if (r.scopeReason) pairs.push(["适用口径说明", r.scopeReason]);
      if (r.scopeConditions) pairs.push(["前置与限制条件", r.scopeConditions]);
      if (r.detail) pairs.push(["完整定义摘要", r.detail]);
      if (r.tag) pairs.push(["国家标签", r.tag]);
      if (r.kind) pairs.push(["分类", r.kind]);
      if (r.source) pairs.push(["游戏源码位置", r.source]);
    }
    if (!pairs.length) {
      return `<tr class="detail-row"><td colspan="${colspan}"><div style="font-size:12.5px;color:var(--ink-muted)">ID: <code>${esc(r.id || "")}</code>（无附加展开字段）</div></td></tr>`;
    }
    return `<tr class="detail-row"><td colspan="${colspan}"><dl class="detail-dl">${pairs.map(([k, v]) =>
      `<div><dt>${esc(k)}</dt><dd>${esc(v)}</dd></div>`
    ).join("")}</dl></td></tr>`;
  }

  document.addEventListener("DOMContentLoaded", () => {
    const page = document.body.getAttribute("data-page");
    if (page === "map") initMapExplorer();
    else if (page === "lab") initLabPage();
    else if (page === "ledgers") initLedgersPage();
    else if (page === "pop-demand") initPopDemandPage();
    else if (page === "directory") initDirectoryPage();
    else if (page === "glossary") initGlossaryPage();
  });

  // 1. 36-Node Interactive Concept Dependency Graph (map.html)
  function initMapExplorer() {
    const bundle = window.__EU5_GRAPH__;
    const svg = document.getElementById("map-svg");
    const detailEl = document.getElementById("map-detail");
    const pillarFilter = document.getElementById("map-pillar-filter");
    if (!bundle || !svg || !detailEl) return;

    const pillarColors = {};
    bundle.pillars.forEach((p) => (pillarColors[p.id] = p.color));
    const nodeMap = {};
    bundle.nodes.forEach((n) => (nodeMap[n.id] = n));

    const W = 168, H = 58;
    let svgHtml = `<defs>
      <marker id="m-arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
        <path d="M0 1 L10 5 L0 9 z" fill="var(--ink-muted)" />
      </marker>
    </defs>`;

    bundle.edges.forEach(([u, v], idx) => {
      const a = nodeMap[u], b = nodeMap[v];
      if (!a || !b) return;
      const dx = b.x - a.x, dy = b.y - a.y;
      const mx = (a.x + b.x) / 2, my = (a.y + b.y) / 2;
      const dist = Math.hypot(dx, dy);
      const ox = dist > 260 ? -dy * 0.08 : 0;
      const oy = dist > 260 ? dx * 0.08 : 0;
      svgHtml += `<path id="edge-${idx}" data-from="${u}" data-to="${v}" class="map-edge"
        d="M${a.x},${a.y} Q${mx + ox},${my + oy} ${b.x},${b.y}"
        fill="none" stroke="var(--border)" stroke-width="1.5" marker-end="url(#m-arrow)" />`;
    });

    bundle.nodes.forEach((n) => {
      const col = pillarColors[n.pillar] || "#1c4e6f";
      const rx = n.x - W / 2, ry = n.y - H / 2;
      svgHtml += `<g class="map-node" data-id="${n.id}" data-pillar="${n.pillar}">
        <rect x="${rx}" y="${ry}" width="${W}" height="${H}" rx="10" fill="var(--surface)" stroke="${col}" stroke-width="2.2" />
        <rect x="${rx}" y="${ry}" width="6" height="${H}" rx="3" fill="${col}" />
        <text x="${n.x + 2}" y="${n.y - 4}" text-anchor="middle" font-size="13" font-weight="700" fill="var(--ink)">${esc(n.zh)}</text>
        <text x="${n.x + 2}" y="${n.y + 14}" text-anchor="middle" font-size="10.5" fill="var(--ink-muted)">${esc(n.en)}</text>
      </g>`;
    });

    svg.innerHTML = svgHtml;

    function selectNode(nid) {
      const n = nodeMap[nid];
      if (!n) return;
      const ups = bundle.edges.filter(([, to]) => to === nid).map(([from, , lbl]) => ({ node: nodeMap[from], lbl }));
      const downs = bundle.edges.filter(([from]) => from === nid).map(([, to, lbl]) => ({ node: nodeMap[to], lbl }));
      const activeSet = new Set([nid, ...ups.map((x) => x.node.id), ...downs.map((x) => x.node.id)]);

      svg.querySelectorAll(".map-node").forEach((el) => {
        el.classList.toggle("dimmed", !activeSet.has(el.getAttribute("data-id")));
      });
      svg.querySelectorAll(".map-edge").forEach((el) => {
        const f = el.getAttribute("data-from"), t = el.getAttribute("data-to");
        el.classList.remove("active-in", "active-out", "dimmed");
        if (t === nid) el.classList.add("active-in");
        else if (f === nid) el.classList.add("active-out");
        else el.classList.add("dimmed");
      });

      const col = pillarColors[n.pillar];
      detailEl.innerHTML = `
        <div class="eyebrow" style="color:${col}">${esc(bundle.pillars.find((p) => p.id === n.pillar)?.zh || "")}</div>
        <h3 style="margin:0 0 2px">${esc(n.zh)}</h3>
        <div style="font-size:12px;color:var(--ink-muted);margin-bottom:10px">${esc(n.en)}</div>
        <p style="font-size:13.5px;margin:0 0 10px">${esc(n.summary)}</p>
        <div class="formula-box" style="font-size:12.5px;margin:10px 0"><strong>核心关系 / 公式：</strong><br>${esc(n.formula)}</div>
        <div class="callout warn" style="font-size:12.5px;margin:10px 0"><strong>红线警示：</strong>${esc(n.redline)}</div>
        <div style="margin-top:12px">
          <div style="font-size:12px;font-weight:700;color:#1a7a4c;margin-bottom:4px">上游谁决定它（${ups.length} 项）</div>
          <div style="display:flex;flex-wrap:wrap;gap:6px;margin-bottom:10px">
            ${ups.length ? ups.map((x) => `<button type="button" class="btn-pill" data-jump-node="${x.node.id}" title="${esc(x.lbl)}">${esc(x.node.zh)} · <small>${esc(x.lbl)}</small></button>`).join("") : '<span style="font-size:12px;color:var(--ink-muted)">基础输入源</span>'}
          </div>
          <div style="font-size:12px;font-weight:700;color:#b52b3b;margin-bottom:4px">下游它驱动谁（${downs.length} 项）</div>
          <div style="display:flex;flex-wrap:wrap;gap:6px;margin-bottom:14px">
            ${downs.length ? downs.map((x) => `<button type="button" class="btn-pill" data-jump-node="${x.node.id}" title="${esc(x.lbl)}">${esc(x.node.zh)} · <small>${esc(x.lbl)}</small></button>`).join("") : '<span style="font-size:12px;color:var(--ink-muted)">终端表现输出</span>'}
          </div>
          <a href="${esc(n.href)}" class="btn-pill" style="background:var(--accent-2);color:#fff;border-color:var(--accent-2);width:100%;justify-content:center">深入阅读对应章节 →</a>
        </div>
      `;
      detailEl.querySelectorAll("[data-jump-node]").forEach((b) => {
        b.addEventListener("click", () => selectNode(b.getAttribute("data-jump-node")));
      });
      history.replaceState(null, "", "#" + nid);
    }

    svg.querySelectorAll(".map-node").forEach((el) => {
      el.addEventListener("click", () => selectNode(el.getAttribute("data-id")));
    });
    if (pillarFilter) {
      pillarFilter.addEventListener("change", () => {
        const val = pillarFilter.value;
        svg.querySelectorAll(".map-node").forEach((el) => {
          el.classList.toggle("dimmed", val !== "all" && el.getAttribute("data-pillar") !== val);
        });
        svg.querySelectorAll(".map-edge").forEach((el) => el.classList.add("dimmed"));
      });
    }

    const hashId = location.hash.replace("#", "");
    if (hashId && nodeMap[hashId]) selectNode(hashId);
  }

  // 2. Redlines + 4-in-1 Calculator + Troubleshooting Lab (lab.html)
  function initLabPage() {
    const bundle = window.__EU5_GRAPH__;
    if (!bundle) return;

    const tabs = document.querySelectorAll("[data-lab-tab]");
    const panels = document.querySelectorAll("[data-lab-panel]");
    function switchTab(id) {
      tabs.forEach((b) => b.classList.toggle("active", b.getAttribute("data-lab-tab") === id));
      panels.forEach((p) => (p.hidden = p.getAttribute("data-lab-panel") !== id));
    }
    tabs.forEach((b) => b.addEventListener("click", () => {
      const id = b.getAttribute("data-lab-tab");
      switchTab(id);
      history.replaceState(null, "", "#" + id);
    }));
    const h = location.hash.replace("#", "");
    if (["redlines", "calc", "troubleshoot"].includes(h)) switchTab(h);

    const redList = document.getElementById("redline-grid");
    const redPillar = document.getElementById("red-pillar");
    const redSearch = document.getElementById("red-search");
    function renderRedlines() {
      const p = redPillar.value;
      const q = (redSearch.value || "").trim().toLowerCase();
      const filtered = bundle.redlines.filter((r) => (p === "all" || r.pillar === p) && (!q || (r.title + r.value + r.key + r.desc).toLowerCase().includes(q)));
      redList.innerHTML = filtered.map((r) => `
        <article class="card redline-card" style="border-top:3px solid var(--p-${r.pillar})">
          <div class="redline-card-head">
            <span class="redline-val">${esc(r.value)}</span>
            <code class="redline-key">${esc(r.key)}</code>
          </div>
          <h4 style="margin:0 0 6px">${esc(r.title)}</h4>
          <p>${esc(r.desc)}</p>
        </article>
      `).join("");
    }
    if (redList) {
      redPillar.addEventListener("change", renderRedlines);
      redSearch.addEventListener("input", renderRedlines);
      renderRedlines();
    }

    const tsList = document.getElementById("troubleshoot-list");
    const tsSearch = document.getElementById("ts-search");
    function renderTs() {
      const q = (tsSearch.value || "").trim().toLowerCase();
      const filtered = bundle.troubleshoot.filter((t) => !q || (t.symptom + t.cause + t.fix).toLowerCase().includes(q));
      tsList.innerHTML = filtered.map((t) => `
        <article class="card" style="margin-bottom:12px;border-left:4px solid var(--p-${t.pillar})">
          <h4 style="margin:0 0 8px;color:var(--p-${t.pillar})">问：${esc(t.symptom)}</h4>
          <p style="margin:0 0 6px;color:var(--ink)"><strong>根因机制：</strong>${esc(t.cause)}</p>
          <p style="margin:0 0 8px"><strong>立即解法：</strong>${esc(t.fix)}</p>
          <a href="${esc(t.href)}" style="font-size:12.5px">前往对应章节详读 →</a>
        </article>
      `).join("");
    }
    if (tsList) {
      tsSearch.addEventListener("input", renderTs);
      renderTs();
    }

    function updC1() {
      const prox = +document.getElementById("c1-prox").value;
      const integ = +document.getElementById("c1-integ").value;
      const extra = +document.getElementById("c1-extra").value;
      const baseWealth = +document.getElementById("c1-wealth").value;
      const access = +document.getElementById("c1-access").value / 100;
      const taxRate = +document.getElementById("c1-tax").value / 100;

      document.getElementById("c1-prox-v").textContent = prox + "%";
      document.getElementById("c1-extra-v").textContent = (extra >= 0 ? "+" : "") + extra + "%";
      document.getElementById("c1-wealth-v").textContent = baseWealth.toFixed(1) + " 杜卡特";
      document.getElementById("c1-access-v").textContent = Math.round(access * 100) + "%";
      document.getElementById("c1-tax-v").textContent = Math.round(taxRate * 100) + "%";

      const maxCtrl = Math.max(0, Math.min(100, prox * 0.75 + integ + extra));
      const realWealth = baseWealth * access;
      const taxBase = realWealth * (maxCtrl / 100);
      const uncontrolled = realWealth - taxBase;
      const treasury = taxBase * taxRate;
      const estateKeep = realWealth - treasury;
      const ratioPct = baseWealth > 0 ? (taxBase / baseWealth) * 100 : 0;

      const tPct = realWealth > 0 ? (treasury / realWealth) * 100 : 0;
      const statusBadge = maxCtrl < 75 ? '<span class="neg">警告：控制力 < 75%，阶层可在此建私产建筑且王室无法直接强拆！</span>' : '<span class="pos">安全：控制力 ≥ 75%，可拆阶层私产且高额截流财富。</span>';

      document.getElementById("c1-out").innerHTML = `
        <div><strong>最大控制力上限：</strong><span class="num">${maxCtrl.toFixed(1)}%</span> &nbsp;|&nbsp; ${statusBadge}</div>
        <div>实际地点月财富（×接入）：<strong>${realWealth.toFixed(2)}</strong> &nbsp;→&nbsp; 可税基：<strong>${taxBase.toFixed(2)}</strong>（占名义财富 ${ratioPct.toFixed(0)}%）</div>
        <div><strong>国库实收税款：</strong><span class="pos">${treasury.toFixed(2)} 杜卡特</span> &nbsp;|&nbsp; <strong>漏入阶层总金库（未控+免税）：</strong><span class="neg">${estateKeep.toFixed(2)} 杜卡特</span>（含未控财富 ${uncontrolled.toFixed(2)}）</div>
        <div class="bar-split" title="蓝：国库税款，棕：流向阶层金库"><div class="bar-treasury" style="width:${tPct.toFixed(1)}%"></div><div class="bar-estate" style="width:${(100 - tPct).toFixed(1)}%"></div></div>
      `;
    }
    ["c1-prox", "c1-integ", "c1-extra", "c1-wealth", "c1-access", "c1-tax"].forEach((id) => {
      document.getElementById(id)?.addEventListener("input", updC1);
    });
    if (document.getElementById("c1-prox")) updC1();

    function updC2() {
      const sat = +document.getElementById("c2-sat").value / 100;
      const sameCat = document.getElementById("c2-cat").checked ? -15 : 0;
      const lowUnrest = document.getElementById("c2-unrest").checked ? 10 : 0;
      const cult = document.getElementById("c2-cult").checked ? 10 : 0;
      const rel = document.getElementById("c2-rel").checked ? 10 : 0;
      const highProg = document.getElementById("c2-prog").checked ? -20 : 0;
      document.getElementById("c2-sat-v").textContent = Math.round(sat * 100) + "%";

      const raw = 50 + 30 * sat + sameCat + lowUnrest + cult + rel + highProg;
      const clamped = Math.max(10, Math.min(90, raw));
      document.getElementById("c2-out").innerHTML = `
        <div><strong>要塞留存朝廷忠诚概率：</strong><span class="num" style="font-size:18px">${clamped.toFixed(1)}%</span>（引擎钳位 10% ~ 90%，原始计算 ${raw.toFixed(1)}%）</div>
        <div style="font-size:12.5px;color:var(--ink-muted)">构成：基础 50 + 阶层满意 ${(30 * sat).toFixed(1)} + 同类惩罚 ${sameCat} + 叛乱度 ${lowUnrest} + 文化 ${cult} + 宗教 ${rel} + >80%进度惩罚 ${highProg}</div>
      `;
    }
    ["c2-sat", "c2-cat", "c2-unrest", "c2-cult", "c2-rel", "c2-prog"].forEach((id) => {
      document.getElementById(id)?.addEventListener("input", updC2);
    });
    if (document.getElementById("c2-sat")) updC2();

    function updC3() {
      const subShare = +document.getElementById("c3-sub").value / 100;
      const areas = +document.getElementById("c3-areas").value;
      const gps = +document.getElementById("c3-gp").value;
      const rps = +document.getElementById("c3-rp").value;
      document.getElementById("c3-sub-v").textContent = Math.round(subShare * 100) + "%";
      document.getElementById("c3-areas-v").textContent = areas + " 个 0%控地区";
      document.getElementById("c3-gp-v").textContent = gps + " 个列强";
      document.getElementById("c3-rp-v").textContent = rps + " 个区域强权";

      const loyPen = subShare > 0.20 ? (subShare - 0.20) * -60 : 0;
      const conn = Math.max(0, 100 - areas * 20);
      const blocWt = gps * 1.0 + rps * 0.5;
      const satExtra = Math.max(0, blocWt - 1.0) * 0.3;

      document.getElementById("c3-out").innerHTML = `
        <div><strong>全属国集团忠诚惩戒：</strong><span class="${loyPen < 0 ? "neg" : "pos"}">${loyPen.toFixed(1)} 点忠诚度</span>（门槛 &gt;20% 按 −60 倍率扣）</div>
        <div><strong>陆路属国领土连通度：</strong><span class="num">${conn} / 100</span>（经过每 1 个 0% 控制地区狠扣 20 分）</div>
        <div><strong>联盟集团饱和总权重：</strong><span class="num">${blocWt.toFixed(1)}</span> → 若 >1.0，<strong>每一份同盟</strong>额外多扣 <span class="neg">+${satExtra.toFixed(2)}</span> 外交容量！</div>
      `;
    }
    ["c3-sub", "c3-areas", "c3-gp", "c3-rp"].forEach((id) => {
      document.getElementById(id)?.addEventListener("input", updC3);
    });
    if (document.getElementById("c3-sub")) updC3();

    function updC4() {
      const init = +document.getElementById("c4-init").value;
      const days = +document.getElementById("c4-days").value;
      const maxShare = +document.getElementById("c4-share").value;
      const cats = +document.getElementById("c4-cats").value;
      document.getElementById("c4-init-v").textContent = init;
      document.getElementById("c4-days-v").textContent = "第 " + days + " 天";
      document.getElementById("c4-share-v").textContent = maxShare + "%";
      document.getElementById("c4-cats-v").textContent = cats + " 种类别";

      const initTerm = Math.min(0.30, init * 0.025);
      const durTerm = days * 0.03;
      const prob = Math.min(1.0, 0.60 + initTerm + durTerm) * 100;
      const combinedOk = maxShare < 50 && cats >= 2;
      document.getElementById("c4-out").innerHTML = `
        <div><strong>每日步进接敌概率（D100）：</strong><span class="num" style="font-size:17px">${prob.toFixed(1)}%</span>（基础 60% + 主动项 ${(initTerm * 100).toFixed(1)}% + 天数项 ${(durTerm * 100).toFixed(1)}%）</div>
        <div><strong>兵种混编协同（Combined Arms）：</strong>${combinedOk ? `<span class="pos">生效中（额外 ${cats - 1} 类叠加战斗力加成）</span>` : '<span class="neg">失效！单一类别占比已达 ≥50% 或兵种不足 2 类</span>'}</div>
      `;
    }
    ["c4-init", "c4-days", "c4-share", "c4-cats"].forEach((id) => {
      document.getElementById(id)?.addEventListener("input", updC4);
    });
    if (document.getElementById("c4-init")) updC4();
  }

  // 3. 22 Rich Lazy-Loaded Data Ledgers (ledgers.html)
  function initLedgersPage() {
    const tabsEl = document.getElementById("ledger-tabs");
    const qEl = document.getElementById("ledger-search");
    const subFilterEl = document.getElementById("ledger-subfilter");
    const countEl = document.getElementById("ledger-count");
    const headEl = document.getElementById("ledger-thead");
    const bodyEl = document.getElementById("ledger-tbody");
    const pagerEl = document.getElementById("ledger-pager");
    if (!tabsEl || !headEl || !bodyEl) return;

    const nameCell = (r, expandable) =>
      `<div>${expandable ? '<span class="row-toggle-mark">▸</span>' : ""}<strong>${esc(r.zh)}</strong>${r.scope ? ` <span class="scope-tag">${esc(r.scope.split(" / ")[0])}</span>` : ""}<br><small style="color:var(--ink-muted)">${esc(r.en)} <code style="font-size:10.5px">${esc(r.id)}</code></small></div>`;

    const GROUPS = [
      { id: "econ", label: "经济建造" },
      { id: "gov", label: "政体阶层" },
      { id: "mil", label: "军事外交" },
      { id: "hist", label: "文化历史" },
    ];

    const CONFIGS = [
      {
        id: "building_types", grp: "econ", label: "501 建筑全表", filterKey: "group", expandable: true,
        cols: [
          { label: "建筑名称", key: "zh", fn: (r) => nameCell(r, true) },
          { label: "分类", key: "group", fn: (r) => `<span class="scope-tag">${esc(r.group)}</span>` },
          { label: "基价(金)", key: "price", num: true, fn: (r) => `<span class="num">${esc(r.price)}</span>` },
          { label: "岗位", key: "jobs", num: true, fn: (r) => `<span class="num">${esc(r.jobs)}</span>` },
          { label: "雇员工种", key: "employees", fn: (r) => esc(r.employees) },
          { label: "工期(天)", key: "time", num: true, fn: (r) => `<span class="num">${esc(r.time)}</span>` },
          { label: "可建等级", key: "ranks", fn: (r) => `<small>${esc(r.ranks)}</small>` },
          { label: "产出商品 / 职能", key: "output", fn: (r) => esc(r.output) },
        ],
      },
      {
        id: "goods", grp: "econ", label: "75 商品数值", filterKey: "group",
        cols: [
          { label: "商品", key: "zh", fn: (r) => `<div class="good-cell">${r.icon ? `<img class="good-icon" src="${esc(r.icon)}" alt="" loading="lazy">` : ""}<div><strong>${esc(r.zh)}</strong><br><small style="color:var(--ink-muted)">${esc(r.en)}</small></div></div>` },
          { label: "分类 / 产法", key: "group", fn: (r) => `${esc(r.group)}<br><small>${esc(r.method)}</small>` },
          { label: "基准市价", key: "price", num: true, fn: (r) => `<span class="num">${r.price}</span>` },
          { label: "食物值", key: "food", num: true, fn: (r) => r.food > 0 ? `<span class="num pos">${r.food}</span>` : '<span class="num" style="color:var(--ink-muted)">—</span>' },
          { label: "运输系数", key: "transport", num: true, fn: (r) => `<span class="num">${r.transport}</span>` },
          { label: "基础月产", key: "base", num: true, fn: (r) => `<span class="num">${r.base}</span>` },
        ],
      },
      {
        id: "industry_types", grp: "econ", label: "8 产业政策", filterKey: "scope", expandable: true,
        cols: [
          { label: "产业名称", key: "zh", fn: (r) => nameCell(r, true) },
          { label: "涵盖商品", key: "goods", fn: (r) => esc(r.goods) },
          { label: "地区产出(%)", key: "area_out", num: true, fn: (r) => `<span class="num pos">+${esc(r.area_out)}%</span>` },
          { label: "全国人口需求(%)", key: "pop_demand", num: true, fn: (r) => `<span class="num">${esc(r.pop_demand)}%</span>` },
          { label: "授予政治费", key: "grant_cost", num: true, fn: (r) => `<span class="num">${esc(r.grant_cost)}</span>` },
        ],
      },
      {
        id: "road_types", grp: "econ", label: "4 道路对照", filterKey: "scope", expandable: true,
        cols: [
          { label: "道路名称", key: "zh", fn: (r) => nameCell(r, true) },
          { label: "等级", key: "level", num: true, fn: (r) => `<span class="num">${esc(r.level)}</span>` },
          { label: "单距造价", key: "cost", num: true, fn: (r) => `<span class="num">${esc(r.cost)}</span>` },
          { label: "单距工期(天)", key: "time", num: true, fn: (r) => `<span class="num">${esc(r.time)}</span>` },
          { label: "移动成本", key: "move_cost", num: true, fn: (r) => `<span class="num pos">${esc(r.move_cost)}%</span>` },
          { label: "市场距成(%)", key: "market_cost", num: true, fn: (r) => `<span class="num pos">${esc(r.market_cost)}%</span>` },
          { label: "额外首都距减", key: "prox_red", num: true, fn: (r) => `<span class="num">${esc(r.prox_red)}</span>` },
        ],
      },
      {
        id: "town_rights", grp: "econ", label: "75 城镇特权", filterKey: "scope",
        cols: [
          { label: "特权名称", key: "zh", fn: (r) => `<strong>${esc(r.zh)}</strong><br><small>${esc(r.en)}</small>` },
          { label: "适用范围", key: "scope", fn: (r) => esc(r.scope) },
          { label: "地点修正与冲突互斥规则", key: "detail", fn: (r) => esc(r.detail) },
        ],
      },
      {
        id: "estate_privileges", grp: "gov", label: "331 阶层特权", filterKey: "estate", expandable: true,
        cols: [
          { label: "特权名称", key: "zh", fn: (r) => nameCell(r, true) },
          { label: "获授阶层", key: "estate", fn: (r) => `<span class="cmd-type">${esc(r.estate)}</span>` },
          { label: "阶层力量%", key: "power_mod", num: true, fn: (r) => `<span class="num">${esc(r.power_mod)}</span>` },
          { label: "满意度均衡Δ", key: "sat_eq", num: true, fn: (r) => `<span class="num">${esc(r.sat_eq)}</span>` },
          { label: "主要全国修正摘选", key: "effects", fn: (r) => esc(r.effects) },
        ],
      },
      {
        id: "estate_actions", grp: "gov", label: "12 阶层互动", filterKey: "kind",
        cols: [
          { label: "互动名称", key: "zh", fn: (r) => `<strong>${esc(r.zh)}</strong><br><small>${esc(r.en)} (${esc(r.id)})</small>` },
          { label: "类别", key: "kind", fn: (r) => esc(r.kind) },
          { label: "适用目标与条件", key: "target", fn: (r) => esc(r.target) },
          { label: "耗费与惩罚代价", key: "cost", fn: (r) => esc(r.cost) },
          { label: "实际收益与冷却", key: "effect", fn: (r) => `${esc(r.effect)}<br><small style="color:var(--ink-muted)">冷却：${esc(r.cooldown)}</small>` },
        ],
      },
      {
        id: "laws", grp: "gov", label: "213 法律", filterKey: "category", expandable: true,
        cols: [
          { label: "法律名称", key: "zh", fn: (r) => nameCell(r, true) },
          { label: "类别", key: "category", fn: (r) => `<span class="cmd-type">${esc(r.category)}</span>` },
          { label: "主体", key: "target_scope", fn: (r) => esc(r.target_scope) },
          { label: "政策项", key: "policies_count", num: true, fn: (r) => `<span class="num">${esc(r.policies_count)}</span>` },
          { label: "实施期", key: "impl_times", fn: (r) => esc(r.impl_times) },
          { label: "指定政体/宗教/国家", key: "groups", fn: (r) => `<small>${esc(r.groups)}</small>` },
        ],
      },
      {
        id: "government_reforms", grp: "gov", label: "379 政府改革", filterKey: "age", expandable: true,
        cols: [
          { label: "改革名称", key: "zh", fn: (r) => nameCell(r, true) },
          { label: "解锁时代", key: "age", fn: (r) => esc(r.age) },
          { label: "政体要求", key: "government", fn: (r) => esc(r.government) },
          { label: "社会价值资格", key: "societal_req", fn: (r) => esc(r.societal_req) },
          { label: "实施(年)", key: "impl_years", num: true, fn: (r) => `<span class="num">${esc(r.impl_years)}</span>` },
          { label: "主要效果摘选", key: "effects", fn: (r) => esc(r.effects) },
        ],
      },
      {
        id: "government_types", grp: "gov", label: "5 大政体", filterKey: "scope", expandable: true,
        cols: [
          { label: "政体名称", key: "zh", fn: (r) => nameCell(r, true) },
          { label: "政府影响力", key: "gov_power", fn: (r) => esc(r.gov_power) },
          { label: "默认阶层", key: "default_estate", fn: (r) => esc(r.default_estate) },
          { label: "继承法数", key: "heir_count", num: true, fn: (r) => `<span class="num">${esc(r.heir_count)}</span>` },
          { label: "贵族联姻", key: "noble_marriage", fn: (r) => esc(r.noble_marriage) },
          { label: "自动配偶", key: "gen_consorts", fn: (r) => esc(r.gen_consorts) },
        ],
      },
      {
        id: "bureaucracies", grp: "gov", label: "60 官僚部门", filterKey: "scope",
        cols: [
          { label: "部门名称", key: "zh", fn: (r) => `<strong>${esc(r.zh)}</strong><br><small>${esc(r.en)}</small>` },
          { label: "资格", key: "scope", fn: (r) => esc(r.scope) },
          { label: "常驻 / 满维正面 / 缺维负面修正", key: "detail", fn: (r) => `${esc(r.detail)}${r.conditions ? `<br><small style="color:var(--ink-muted)">${esc(r.conditions)}</small>` : ""}` },
        ],
      },
      {
        id: "cabinet_actions", grp: "gov", label: "81 内阁行动", filterKey: "ability",
        cols: [
          { label: "行动名称", key: "zh", fn: (r) => `<strong>${esc(r.zh)}</strong><br><small>${esc(r.en)}</small>` },
          { label: "系别 / 资格", key: "ability", fn: (r) => `<span class="cmd-type">${esc(r.ability)}</span> ${esc(r.scope)}` },
          { label: "作用对象", key: "target", fn: (r) => esc(r.target) },
          { label: "核心效果与前置条件", key: "effect", fn: (r) => `${esc(r.effect)}${r.conditions ? `<br><small style="color:var(--ink-muted)">${esc(r.conditions)}</small>` : ""}` },
        ],
      },
      {
        id: "character_interactions", grp: "gov", label: "34 角色互动", filterKey: "scope",
        cols: [
          { label: "互动名称", key: "zh", fn: (r) => `<strong>${esc(r.zh)}</strong><br><small>${esc(r.en)}</small>` },
          { label: "适用资格", key: "scope", fn: (r) => esc(r.scope) },
          { label: "详细机制、花费与效果", key: "detail", fn: (r) => `${esc(r.detail)}${r.conditions ? `<br><small style="color:var(--ink-muted)">${esc(r.conditions)}</small>` : ""}` },
        ],
      },
      {
        id: "societal_values", grp: "gov", label: "17 社会价值观", filterKey: "category",
        cols: [
          { label: "轴线名称", key: "zh", fn: (r) => `<strong>${esc(r.zh)}</strong><br><small>${esc(r.en)}</small>` },
          { label: "分类 / 时代", key: "category", fn: (r) => `${esc(r.category)}<br><small>${esc(r.era)}</small>` },
          { label: "左端极点 (−100) 满额效应", key: "left_pole", fn: (r) => `<strong>${esc(r.left_pole)}：</strong>${esc(r.left_effects)}` },
          { label: "右端极点 (+100) 满额效应", key: "right_pole", fn: (r) => `<strong>${esc(r.right_pole)}：</strong>${esc(r.right_effects)}` },
        ],
      },
      {
        id: "unit_types", grp: "mil", label: "401 军事单位", filterKey: "category", expandable: true,
        cols: [
          { label: "单位名称", key: "zh", fn: (r) => nameCell(r, true) },
          { label: "兵种类别", key: "category", fn: (r) => `<small>${esc(r.category)}</small>` },
          { label: "时代", key: "age", fn: (r) => `<small>${esc(r.age)}</small>` },
          { label: "满编(人)", key: "troops", num: true, fn: (r) => `<span class="num">${esc(r.troops)}</span>` },
          { label: "战力", key: "combat_power", num: true, fn: (r) => `<span class="num">${esc(r.combat_power)}</span>` },
          { label: "舰炮", key: "cannons", num: true, fn: (r) => `<span class="num">${esc(r.cannons)}</span>` },
          { label: "船体", key: "hull", num: true, fn: (r) => `<span class="num">${esc(r.hull)}</span>` },
          { label: "建期(天)", key: "build_time", num: true, fn: (r) => `<span class="num">${esc(r.build_time)}</span>` },
        ],
      },
      {
        id: "wargoals", grp: "mil", label: "78 战争目标", filterKey: "goal_type", expandable: true,
        cols: [
          { label: "目标名称", key: "zh", fn: (r) => nameCell(r, true) },
          { label: "目标类型", key: "goal_type", fn: (r) => esc(r.goal_type) },
          { label: "跳分参数", key: "ticking", num: true, fn: (r) => `<span class="num">${esc(r.ticking)}</span>` },
          { label: "割地倍率×", key: "conquest_fac", num: true, fn: (r) => `<span class="num">${esc(r.conquest_fac)}</span>` },
          { label: "附庸倍率×", key: "subjugation_fac", num: true, fn: (r) => `<span class="num">${esc(r.subjugation_fac)}</span>` },
          { label: "敌意倍率×", key: "antagonism_fac", num: true, fn: (r) => `<span class="num">${esc(r.antagonism_fac)}</span>` },
        ],
      },
      {
        id: "casus_belli", grp: "mil", label: "113 宣战理由", filterKey: "scope",
        cols: [
          { label: "宣战理由", key: "zh", fn: (r) => `<strong>${esc(r.zh)}</strong><br><small>${esc(r.en)}</small>` },
          { label: "范围", key: "scope", fn: (r) => esc(r.scope) },
          { label: "战争目标与核心条件", key: "detail", fn: (r) => esc(r.detail) },
        ],
      },
      {
        id: "diplomatic_actions", grp: "mil", label: "194 外交行动", filterKey: "kind", expandable: true,
        cols: [
          { label: "行动名称", key: "zh", fn: (r) => nameCell(r, true) },
          { label: "行动层级", key: "kind", fn: (r) => `<span class="cmd-type">${esc(r.kind)}</span>` },
          { label: "成本", key: "cost", fn: (r) => esc(r.cost) },
          { label: "接受度规则", key: "acceptance", fn: (r) => esc(r.acceptance) },
          { label: "核心结果", key: "effect", fn: (r) => esc(r.effect) },
        ],
      },
      {
        id: "subject_types", grp: "mil", label: "22 属国类型", filterKey: "can_annex",
        cols: [
          { label: "属国名称", key: "zh", fn: (r) => `<strong>${esc(r.zh)}</strong><br><small>${esc(r.en)} (${esc(r.id)})</small>` },
          { label: "层级 / 同君", key: "level", num: true, fn: (r) => `等级 ${esc(r.level)} · 同君：${esc(r.same_ruler)}` },
          { label: "贡赋机制", key: "subject_pays", fn: (r) => esc(r.subject_pays) },
          { label: "外交容倍率", key: "diplo_cost_scale", num: true, fn: (r) => `<span class="num">${esc(r.diplo_cost_scale)}</span>` },
          { label: "吞并规则（速/年/好感）", key: "can_annex", fn: (r) => `${esc(r.can_annex)}（速 ${esc(r.annex_speed)} / 最少 ${esc(r.annex_min_years)} 年 / 好感 ${esc(r.annex_min_opinion)}）` },
        ],
      },
      {
        id: "international_organizations", grp: "mil", label: "37 国际组织", filterKey: "group", expandable: true,
        cols: [
          { label: "组织名称", key: "zh", fn: (r) => nameCell(r, true) },
          { label: "分类", key: "group", fn: (r) => `<small>${esc(r.group)}</small>` },
          { label: "成员范围", key: "membership", fn: (r) => `<small>${esc(r.membership)}</small>` },
          { label: "领袖形式", key: "leadership", fn: (r) => esc(r.leadership) },
          { label: "战争协作", key: "war", fn: (r) => `<small>${esc(r.war)}</small>` },
          { label: "成员与领袖效果", key: "effects", fn: (r) => `<small>${esc(r.effects)}</small>` },
        ],
      },
      {
        id: "religions", grp: "hist", label: "293 种宗教", filterKey: "group", expandable: true,
        cols: [
          { label: "宗教名称", key: "zh", fn: (r) => nameCell(r, true) },
          { label: "宗教组", key: "group", fn: (r) => `<span class="cmd-type">${esc(r.group)}</span>` },
          { label: "礼仪语言", key: "liturgical", fn: (r) => esc(r.liturgical) },
          { label: "信条槽", key: "aspect_slots", num: true, fn: (r) => `<span class="num">${esc(r.aspect_slots)}</span>` },
          { label: "信仰机制", key: "mechanics", fn: (r) => `<small>${esc(r.mechanics)}</small>` },
          { label: "定义修正摘选", key: "effects", fn: (r) => `<small>${esc(r.effects)}</small>` },
        ],
      },
      {
        id: "situations_disasters", grp: "hist", label: "24 局势 & 38 灾难", filterKey: "kind",
        cols: [
          { label: "事件 / 进程", key: "zh", fn: (r) => `<strong>${esc(r.zh)}</strong><br><small>${esc(r.en)}</small>` },
          { label: "类型 / 范围", key: "kind", fn: (r) => `<span class="cmd-type">${esc(r.kind)}</span> ${esc(r.scope)}` },
          { label: "触发概率、惩罚修正与机制说明", key: "detail", fn: (r) => esc(r.detail) },
        ],
      },
    ];

    let curId = "building_types";
    let sortKey = "";
    let sortDir = "asc";
    let pageIdx = 0;
    const PAGE_SIZE = 100;
    const expandedIds = new Set();

    tabsEl.innerHTML = GROUPS.map((g) => {
      const items = CONFIGS.filter((c) => c.grp === g.id);
      return `<div class="tab-group-row"><span class="tab-group-label">${esc(g.label)}</span>` +
        items.map((c) => `<button type="button" class="tab-btn" data-id="${c.id}">${esc(c.label)}</button>`).join("") +
        `</div>`;
    }).join("");

    function buildSubFilter(cfg, rows) {
      const fk = cfg.filterKey;
      const vals = Array.from(new Set(rows.map((r) => r[fk]).filter((v) => v && v !== "—")));
      subFilterEl.innerHTML = `<option value="all">全部类别 (${rows.length})</option>` +
        vals.map((v) => `<option value="${esc(v)}">${esc(v)}</option>`).join("");
    }

    function render() {
      const cfg = CONFIGS.find((c) => c.id === curId) || CONFIGS[0];
      const rows = ledgerCache[curId];
      if (!rows) {
        countEl.textContent = "正在加载数据…";
        headEl.innerHTML = "";
        bodyEl.innerHTML = `<tr><td colspan="6" style="padding:24px;text-align:center">正在从分片脚本载入 ${esc(cfg.label)} …</td></tr>`;
        if (pagerEl) pagerEl.hidden = true;
        return;
      }

      const q = (qEl.value || "").trim().toLowerCase();
      const fv = subFilterEl.value;
      const fk = cfg.filterKey;

      let filtered = rows.filter((r) => {
        if (fv !== "all" && r[fk] !== fv) return false;
        if (!q) return true;
        return JSON.stringify(r).toLowerCase().includes(q);
      });

      if (sortKey) {
        const colDef = cfg.cols.find((c) => c.key === sortKey);
        if (colDef) filtered = sortRows(filtered, sortKey, sortDir, !!colDef.num);
      }

      const totalPages = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE));
      if (pageIdx >= totalPages) pageIdx = 0;
      const start = pageIdx * PAGE_SIZE;
      const slice = filtered.slice(start, start + PAGE_SIZE);

      countEl.textContent = `显示 ${filtered.length} / ${rows.length} 条（第 ${pageIdx + 1}/${totalPages} 页）` + (cfg.expandable ? " · 点击任意行可展开完整条件与效果明细" : "");
      headEl.innerHTML = `<tr>${cfg.cols.map((c) => {
        const cls = "sortable" + (sortKey === c.key ? (sortDir === "asc" ? " sort-asc" : " sort-desc") : "");
        return `<th class="${cls}" data-sort="${esc(c.key)}">${esc(c.label)}</th>`;
      }).join("")}</tr>`;

      headEl.querySelectorAll("th[data-sort]").forEach((th) => {
        th.addEventListener("click", () => {
          const k = th.getAttribute("data-sort");
          if (sortKey === k) sortDir = sortDir === "asc" ? "desc" : "asc";
          else { sortKey = k; sortDir = "asc"; }
          pageIdx = 0;
          render();
        });
      });

      bodyEl.innerHTML = slice.map((r) => {
        const isOpen = cfg.expandable && expandedIds.has(r.id);
        const mainRow = `<tr class="${cfg.expandable ? "row-expandable" : ""}" data-row-id="${esc(r.id)}">${cfg.cols.map((c) => `<td>${c.fn(r)}</td>`).join("")}</tr>`;
        return isOpen ? mainRow + renderDetailDrawer(r, cfg.cols.length) : mainRow;
      }).join("");

      if (cfg.expandable) {
        bodyEl.querySelectorAll("tr.row-expandable").forEach((tr) => {
          tr.addEventListener("click", () => {
            const rid = tr.getAttribute("data-row-id");
            if (expandedIds.has(rid)) expandedIds.delete(rid);
            else expandedIds.add(rid);
            render();
          });
        });
      }

      if (pagerEl) {
        pagerEl.hidden = totalPages <= 1;
        pagerEl.innerHTML = `
          <span style="font-size:12.5px;color:var(--ink-muted)">第 ${start + 1}–${Math.min(filtered.length, start + PAGE_SIZE)} 条 / 共 ${filtered.length} 条</span>
          <div style="display:flex;gap:8px;align-items:center">
            <button type="button" class="btn-pill" id="lg-prev" ${pageIdx === 0 ? "disabled" : ""}>← 上一页</button>
            <span style="font-size:12.5px">第 ${pageIdx + 1} / ${totalPages} 页</span>
            <button type="button" class="btn-pill" id="lg-next" ${pageIdx >= totalPages - 1 ? "disabled" : ""}>下一页 →</button>
          </div>
        `;
        document.getElementById("lg-prev")?.addEventListener("click", () => { pageIdx = Math.max(0, pageIdx - 1); render(); });
        document.getElementById("lg-next")?.addEventListener("click", () => { pageIdx = Math.min(totalPages - 1, pageIdx + 1); render(); });
      }
    }

    async function selectLedger(id, qPrefill) {
      const cleanId = String(id || "").split("?")[0];
      curId = CONFIGS.some((c) => c.id === cleanId) ? cleanId : "building_types";
      sortKey = "";
      sortDir = "asc";
      pageIdx = 0;
      expandedIds.clear();
      if (typeof qPrefill === "string") qEl.value = qPrefill;
      tabsEl.querySelectorAll(".tab-btn").forEach((b) => b.classList.toggle("active", b.getAttribute("data-id") === curId));
      history.replaceState(null, "", "#" + curId);

      const cfg = CONFIGS.find((c) => c.id === curId);
      if (!ledgerCache[curId]) {
        render();
        await loadScriptOnce(`assets/ledgers/${curId}.js`);
      }
      buildSubFilter(cfg, ledgerCache[curId] || []);
      render();
    }

    tabsEl.querySelectorAll(".tab-btn").forEach((b) => b.addEventListener("click", () => selectLedger(b.getAttribute("data-id"), "")));
    qEl.addEventListener("input", () => { pageIdx = 0; render(); });
    subFilterEl.addEventListener("change", () => { pageIdx = 0; render(); });
    window.addEventListener("hashchange", () => {
      const hId = location.hash.replace("#", "").split("?")[0];
      if (hId && hId !== curId) selectLedger(hId);
    });

    const rawHash = location.hash.replace("#", "");
    const [initId, qs] = rawHash.split("?");
    const params = new URLSearchParams(qs || "");
    selectLedger(initId || "building_types", params.get("q") || "");
  }

  // 4. 8 Classes x 75 Goods Population Demand Matrix (pop-demand.html)
  function initPopDemandPage() {
    const pd = window.__EU5_POP_DEMAND__;
    if (!pd) return;
    const tabsEl = document.getElementById("pd-tabs");
    const qEl = document.getElementById("pd-search");
    const nonZeroEl = document.getElementById("pd-nonzero");
    const countEl = document.getElementById("pd-count");
    const headEl = document.getElementById("pd-thead");
    const bodyEl = document.getElementById("pd-tbody");

    let curClsId = (location.hash.replace("#", "") || "nobles");
    if (!pd.classes.some((c) => c.id === curClsId)) curClsId = pd.classes[0].id;
    let sortKey = "baseSpend";
    let sortDir = "desc";
    const expanded = new Set();

    const COLS = [
      { label: "商品", key: "zh", num: false },
      { label: "基准需求量", key: "baseDemand", num: true },
      { label: "阶级基量", key: "classBaseDemand", num: true },
      { label: "基础市价", key: "basePrice", num: true },
      { label: "基准支出(金)", key: "baseSpend", num: true },
      { label: "解锁/缩放条件与环境修正", key: "wealthThreshold", num: false },
    ];

    tabsEl.innerHTML = pd.classes.map((c) => {
      const nz = c.rows.filter((r) => (r.baseDemand || 0) > 0 || (r.classBaseDemand || 0) > 0).length;
      return `<button type="button" class="tab-btn" data-cid="${c.id}">${esc(c.zh)} <small>(${nz}/${c.rows.length})</small></button>`;
    }).join("");

    function render() {
      const cls = pd.classes.find((c) => c.id === curClsId) || pd.classes[0];
      tabsEl.querySelectorAll(".tab-btn").forEach((b) => b.classList.toggle("active", b.getAttribute("data-cid") === cls.id));

      const q = (qEl.value || "").trim().toLowerCase();
      const onlyNZ = nonZeroEl.checked;
      let rows = cls.rows.filter((r) => {
        if (onlyNZ && !(r.baseDemand > 0 || r.classBaseDemand > 0)) return false;
        if (!q) return true;
        return (r.zh + " " + r.en + " " + r.id + " " + JSON.stringify(r.conditions || [])).toLowerCase().includes(q);
      });

      const col = COLS.find((c) => c.key === sortKey);
      if (col) {
        rows = sortRows(rows, sortKey, sortDir, col.num, (r) => r[sortKey] ?? "");
      }

      countEl.textContent = `${cls.zh}（${cls.en} · ${cls.upper ? "上层阶级" : "下层阶级"}）：显示 ${rows.length} / ${cls.rows.length} 种商品 · 点击任意行展开公式推导`;
      headEl.innerHTML = `<tr>${COLS.map((c) => {
        const sc = "sortable" + (sortKey === c.key ? (sortDir === "asc" ? " sort-asc" : " sort-desc") : "");
        return `<th class="${sc}" data-sort="${c.key}">${esc(c.label)}</th>`;
      }).join("")}</tr>`;
      headEl.querySelectorAll("th[data-sort]").forEach((th) => {
        th.addEventListener("click", () => {
          const k = th.getAttribute("data-sort");
          if (sortKey === k) sortDir = sortDir === "asc" ? "desc" : "asc";
          else { sortKey = k; sortDir = COLS.find((c) => c.key === k)?.num ? "desc" : "asc"; }
          render();
        });
      });

      const fmtNum = (n) => n ? Number(n).toFixed(4).replace(/\.?0+$/, "") : "0";
      bodyEl.innerHTML = rows.map((r) => {
        const key = `${cls.id}:${r.id}`;
        const isOpen = expanded.has(key);
        const conds = [];
        if (r.wealthThreshold !== null && r.wealthThreshold !== undefined) conds.push(`财富≥${r.wealthThreshold}`);
        if (r.developmentThreshold !== null && r.developmentThreshold !== undefined) conds.push(`发展≥${r.developmentThreshold}`);
        if (r.literacyFactor !== null && r.literacyFactor !== undefined) conds.push(`识字倍率 ${r.literacyFactor}`);
        (r.conditions || []).forEach((c) => conds.push(`${c.label}：${c.text}`));
        const mainRow = `<tr class="row-expandable" data-pd-key="${esc(key)}">
          <td><div class="good-cell"><span class="row-toggle-mark">▸</span>${r.icon ? `<img class="good-icon" src="${esc(r.icon)}" alt="" loading="lazy">` : ""}<div><strong>${esc(r.zh)}</strong><br><small style="color:var(--ink-muted)">${esc(r.en)}</small></div></div></td>
          <td><span class="num">${fmtNum(r.baseDemand)}</span></td>
          <td><span class="num">${fmtNum(r.classBaseDemand)}</span></td>
          <td><span class="num">${r.basePrice}</span></td>
          <td><span class="num ${r.baseSpend > 0 ? "pos" : ""}">${fmtNum(r.baseSpend)}</span></td>
          <td><small>${conds.length ? esc(conds.join(" ｜ ")) : "无额外门槛"}</small></td>
        </tr>`;
        if (!isOpen) return mainRow;
        const pairs = (r.details || []).map((d) => [d.label, d.text]).concat((r.conditions || []).map((c) => [c.label, c.text]));
        if (r.source) pairs.push(["商品来源", r.source]);
        if (r.raw?.demandSource) pairs.push(["需求来源", r.raw.demandSource]);
        return mainRow + `<tr class="detail-row"><td colspan="6"><dl class="detail-dl">${pairs.map(([k, v]) => `<div><dt>${esc(k)}</dt><dd>${esc(v)}</dd></div>`).join("")}</dl></td></tr>`;
      }).join("");

      bodyEl.querySelectorAll("tr.row-expandable").forEach((tr) => {
        tr.addEventListener("click", () => {
          const k = tr.getAttribute("data-pd-key");
          if (expanded.has(k)) expanded.delete(k);
          else expanded.add(k);
          render();
        });
      });
    }

    tabsEl.querySelectorAll(".tab-btn").forEach((b) => b.addEventListener("click", () => {
      curClsId = b.getAttribute("data-cid");
      history.replaceState(null, "", "#" + curClsId);
      render();
    }));
    qEl.addEventListener("input", render);
    nonZeroEl.addEventListener("change", render);
    render();
  }

  // 5. All 72 Game Catalogs Explorer (23,216 Records) (directory.html)
  function initDirectoryPage() {
    const manifest = window.__EU5_CATALOG_MANIFEST__;
    if (!manifest) return;
    const pillarTabsEl = document.getElementById("dir-pillar-tabs");
    const pickerEl = document.getElementById("dir-picker");
    const headerEl = document.getElementById("dir-active-head");
    const qEl = document.getElementById("dir-search");
    const scopeEl = document.getElementById("dir-scope");
    const countEl = document.getElementById("dir-count");
    const bodyEl = document.getElementById("dir-tbody");
    const pagerEl = document.getElementById("dir-pager");

    const PILLARS = [
      { id: "all", label: "全部 72 类 (23,216)" },
      { id: "economy", label: "经济建造" },
      { id: "politics", label: "政体阶层" },
      { id: "culture", label: "文化宗教科技" },
      { id: "military", label: "军事战争" },
      { id: "diplomacy", label: "外交组织" },
      { id: "geography", label: "地理与气候" },
      { id: "world", label: "开局事件与档案" },
    ];

    let curPillar = "all";
    let curCatId = location.hash.replace("#", "").split("?")[0] || "advances";
    if (!manifest.some((m) => m.id === curCatId)) curCatId = manifest[0].id;
    let pageIdx = 0;
    const PAGE_SIZE = 100;
    const expanded = new Set();

    function renderPicker() {
      pillarTabsEl.innerHTML = PILLARS.map((p) =>
        `<button type="button" class="tab-btn ${p.id === curPillar ? "active" : ""}" data-dp="${p.id}">${esc(p.label)}</button>`
      ).join("");
      pillarTabsEl.querySelectorAll(".tab-btn").forEach((b) => b.addEventListener("click", () => {
        curPillar = b.getAttribute("data-dp");
        renderPicker();
      }));

      const list = curPillar === "all" ? manifest : manifest.filter((m) => m.pillar === curPillar);
      pickerEl.innerHTML = list.map((m) =>
        `<button type="button" class="cat-pill ${m.id === curCatId ? "active" : ""}" data-cid="${esc(m.id)}">
          <span>${esc(m.zh)}</span><span class="cat-cnt">${m.count}</span>
        </button>`
      ).join("");
      pickerEl.querySelectorAll(".cat-pill").forEach((b) => b.addEventListener("click", () => selectCatalog(b.getAttribute("data-cid"))));
    }

    function renderTable() {
      const meta = manifest.find((m) => m.id === curCatId);
      const obj = catalogCache[curCatId];
      if (!meta || !obj) {
        headerEl.innerHTML = `<strong>正在载入：${esc(meta?.zh || curCatId)}…</strong>`;
        bodyEl.innerHTML = `<tr><td colspan="4" style="padding:24px;text-align:center">正在加载分片目录数据…</td></tr>`;
        pagerEl.hidden = true;
        return;
      }

      const ledgerBtn = meta.ledger
        ? `<a href="ledgers.html#${esc(meta.ledger)}" class="btn-pill" style="background:var(--accent-2);color:#fff;border-color:var(--accent-2)">打开精排数值对照表 →</a>`
        : "";
      headerEl.innerHTML = `
        <div><strong>${esc(meta.zh)}</strong> <small style="color:var(--ink-muted)">(${esc(meta.en)} · ${esc(meta.id)} · 共 ${obj.records.length} 条)</small></div>
        ${ledgerBtn}
      `;

      const q = (qEl.value || "").trim().toLowerCase();
      const sc = scopeEl.value;
      const filtered = obj.records.filter((r) => {
        if (sc !== "all" && (r.scope || "general") !== sc) return false;
        if (!q) return true;
        return ((r.zh || "") + " " + (r.en || "") + " " + (r.id || "") + " " + (r.detail || "") + " " + (r.scopeConditions || "") + " " + (r.tag || "")).toLowerCase().includes(q);
      });

      const totalPages = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE));
      if (pageIdx >= totalPages) pageIdx = 0;
      const start = pageIdx * PAGE_SIZE;
      const slice = filtered.slice(start, start + PAGE_SIZE);

      countEl.textContent = `筛选匹配 ${filtered.length} / ${obj.records.length} 条（第 ${pageIdx + 1}/${totalPages} 页） · 点击任意行查看完整源码与前置条件`;
      bodyEl.innerHTML = slice.map((r) => {
        const key = `${curCatId}:${r.id}`;
        const isOpen = expanded.has(key);
        const mainRow = `<tr class="row-expandable" data-dkey="${esc(key)}">
          <td><span class="row-toggle-mark">▸</span><strong>${esc(r.zh)}</strong><br><small style="color:var(--ink-muted)">${esc(r.en)} <code>${esc(r.id)}</code></small></td>
          <td><span class="scope-tag">${esc((r.scopeLabel || r.scope || "通用").split(" / ")[0])}</span></td>
          <td>${esc((r.detail || "—").slice(0, 220))}${(r.detail || "").length > 220 ? "…" : ""}${r.scopeConditions ? `<br><small style="color:var(--ink-muted)">条件：${esc(r.scopeConditions)}</small>` : ""}</td>
          <td><small style="color:var(--ink-muted)">${esc(r.source || "—")}</small></td>
        </tr>`;
        return isOpen ? mainRow + renderDetailDrawer(r, 4) : mainRow;
      }).join("");

      bodyEl.querySelectorAll("tr.row-expandable").forEach((tr) => {
        tr.addEventListener("click", () => {
          const k = tr.getAttribute("data-dkey");
          if (expanded.has(k)) expanded.delete(k);
          else expanded.add(k);
          renderTable();
        });
      });

      pagerEl.hidden = totalPages <= 1;
      pagerEl.innerHTML = `
        <span style="font-size:12.5px;color:var(--ink-muted)">第 ${start + 1}–${Math.min(filtered.length, start + PAGE_SIZE)} 条 / 共 ${filtered.length} 条</span>
        <div style="display:flex;gap:8px;align-items:center">
          <button type="button" class="btn-pill" id="dir-prev" ${pageIdx === 0 ? "disabled" : ""}>← 上一页</button>
          <span style="font-size:12.5px">第 ${pageIdx + 1} / ${totalPages} 页</span>
          <button type="button" class="btn-pill" id="dir-next" ${pageIdx >= totalPages - 1 ? "disabled" : ""}>下一页 →</button>
        </div>
      `;
      document.getElementById("dir-prev")?.addEventListener("click", () => { pageIdx = Math.max(0, pageIdx - 1); renderTable(); });
      document.getElementById("dir-next")?.addEventListener("click", () => { pageIdx = Math.min(totalPages - 1, pageIdx + 1); renderTable(); });
    }

    async function selectCatalog(cid) {
      curCatId = cid;
      pageIdx = 0;
      expanded.clear();
      renderPicker();
      history.replaceState(null, "", "#" + cid);
      if (!catalogCache[cid]) {
        renderTable();
        await loadScriptOnce(`assets/catalogs/${cid}.js`);
      }
      const recs = catalogCache[cid]?.records || [];
      const scopes = Array.from(new Set(recs.map((r) => r.scope || "general")));
      const SCOPE_NAMES = { general: "通用 (general)", conditional: "制度或地域限定 (conditional)", country: "国别/标签关联 (country)", "country-scope": "国别限定" };
      scopeEl.innerHTML = `<option value="all">全部适用口径 (${recs.length})</option>` +
        scopes.map((s) => `<option value="${esc(s)}">${esc(SCOPE_NAMES[s] || s)}</option>`).join("");
      renderTable();
    }

    qEl.addEventListener("input", () => { pageIdx = 0; renderTable(); });
    scopeEl.addEventListener("change", () => { pageIdx = 0; renderTable(); });
    window.addEventListener("hashchange", () => {
      const hId = location.hash.replace("#", "").split("?")[0];
      if (hId && hId !== curCatId && manifest.some((m) => m.id === hId)) selectCatalog(hId);
    });

    renderPicker();
    selectCatalog(curCatId);
  }

  // 6. Bilingual Encyclopedia Glossary (glossary.html)
  function initGlossaryPage() {
    const items = window.__EU5_GLOSSARY__;
    if (!items) return;
    const grid = document.getElementById("gloss-grid");
    const qEl = document.getElementById("gloss-search");
    const pillarEl = document.getElementById("gloss-pillar");
    const countEl = document.getElementById("gloss-count");

    const PILLAR_ZH = {
      territory: "疆域与控制",
      economy: "人口、市场与财政",
      state: "政府、内阁与阶层",
      culture: "文化、信仰与科技",
      military: "军事、海权与和约",
      diplomacy: "外交、属国与秩序",
    };

    function render() {
      const q = (qEl.value || "").trim().toLowerCase();
      const pil = pillarEl.value;
      const hashId = location.hash.replace("#", "");

      const filtered = items.filter((g) => {
        if (pil !== "all" && g.pillar !== pil) return false;
        if (!q) return true;
        return (g.zh + " " + g.en + " " + g.id + " " + g.desc).toLowerCase().includes(q);
      });

      countEl.textContent = `收录 ${filtered.length} / ${items.length} 条官方与深度核心词条`;
      let show = filtered.slice(0, 180);
      if (hashId) {
        const hit = items.find((g) => g.id === hashId);
        if (hit && !show.some((g) => g.id === hashId)) show = [hit, ...show];
      }
      grid.innerHTML = show.map((g) => `
        <article id="${esc(g.id)}" class="gloss-card" style="border-top:3px solid var(--p-${g.pillar})${hashId === g.id ? ";box-shadow:0 0 0 2px var(--accent)" : ""}">
          <h4><span>${esc(g.zh)}</span><small>${esc(g.en)}</small></h4>
          <div style="font-size:11px;color:var(--ink-muted)"><code>${esc(g.id)}</code> · ${esc(PILLAR_ZH[g.pillar] || g.pillar)}</div>
          <p>${esc(g.desc)}</p>
        </article>
      `).join("");

      if (hashId) {
        const el = document.getElementById(hashId);
        if (el) setTimeout(() => el.scrollIntoView({ behavior: "smooth", block: "center" }), 60);
      }
    }

    qEl.addEventListener("input", () => {
      if (location.hash) history.replaceState(null, "", location.pathname);
      render();
    });
    pillarEl.addEventListener("change", render);

    const h = decodeURIComponent(location.hash.replace("#", ""));
    if (h && items.some((x) => x.id === h)) {
      const target = items.find((x) => x.id === h);
      if (target) qEl.value = target.zh;
    }
    render();
  }
})();
