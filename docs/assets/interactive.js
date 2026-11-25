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

  let _entityMatcher = null;
  const _BRACKET_PAIRS = { "《": "》", "「": "」", "【": "】" };
  const _STRUCT_PREFIXES = [
    "征召解锁革新 ", "解锁革新 ", "前置革新 ", "所属法律 ", "现行政策 ", "解锁政策 ",
    "已采用改革 ", "已授予阶层特权 ", "至少有一级建筑 ", "优先升级型号 ", "限定升级型号 ",
  ];

  function getEntityMatcher() {
    if (_entityMatcher) return _entityMatcher;
    const src = window.__EU5_ENTITY_LINKS__;
    if (!src) return null;
    const trie = Object.create(null);
    const inline = src.inline || {};
    for (const key of Object.keys(inline)) {
      if (!key) continue;
      let node = trie;
      for (let i = 0; i < key.length; i++) {
        const ch = key[i];
        node = node[ch] || (node[ch] = Object.create(null));
      }
      node.$ = inline[key];
    }
    _entityMatcher = { exact: src.exact || {}, goods1: src.goods1 || {}, trie };
    return _entityMatcher;
  }

  function linkifyEntitiesHtml(rawText, skipTerm) {
    const s = String(rawText ?? "");
    if (!s || s === "—") return esc(s);
    const m = getEntityMatcher();
    if (!m) return esc(s);
    const { exact, goods1, trie } = m;

    let out = "";
    let plain = "";
    const flushPlain = () => {
      if (plain) {
        out += esc(plain);
        plain = "";
      }
    };
    const emitLink = (term, entry) => {
      flushPlain();
      out += `<a class="ent-link" href="${esc(entry[0])}" title="跳转查看${esc(entry[1])}：${esc(term)}">${esc(term)}</a>`;
    };

    let i = 0;
    const n = s.length;
    while (i < n) {
      const ch = s[i];
      // 1. Bracketed exact entity titles: 《...》 / 「...」 / 【...】
      const closeCh = _BRACKET_PAIRS[ch];
      if (closeCh) {
        const cIdx = s.indexOf(closeCh, i + 1);
        if (cIdx > i + 1 && cIdx - i <= 32) {
          const inner = s.slice(i + 1, cIdx).trim();
          const hit = exact[inner];
          if (hit && inner !== skipTerm) {
            plain += ch;
            emitLink(inner, hit);
            plain += closeCh;
            i = cIdx + 1;
            continue;
          }
        }
      }

      // 2. Structured prefix exact entity match (e.g. "前置革新 重型枪骑兵", "现行政策 长弓竞赛")
      let matchedPrefix = "";
      for (let p = 0; p < _STRUCT_PREFIXES.length; p++) {
        if (s.startsWith(_STRUCT_PREFIXES[p], i)) {
          matchedPrefix = _STRUCT_PREFIXES[p];
          break;
        }
      }
      if (matchedPrefix) {
        const tStart = i + matchedPrefix.length;
        let tEnd = tStart;
        while (tEnd < n && !/[\s/｜、，；。：（()）]/.test(s[tEnd])) tEnd++;
        const tok = s.slice(tStart, tEnd);
        const hit = exact[tok];
        if (hit && tok !== skipTerm) {
          plain += matchedPrefix;
          emitLink(tok, hit);
          i = tEnd;
          continue;
        }
      }

      // 3. Single-character good before numeric quantity (e.g. "铜 2.0", "盐 0.05")
      const g1 = goods1[ch];
      if (g1 && ch !== skipTerm) {
        const prevIsCjk = i > 0 && /[\u4e00-\u9fff]/.test(s[i - 1]);
        if (!prevIsCjk && /^\s+[+\-]?\d/.test(s.slice(i + 1, i + 10))) {
          emitLink(ch, g1);
          i += 1;
          continue;
        }
      }

      // 4. Longest-match Trie lookup over safe multi-char entity names
      let node = trie[ch];
      if (node) {
        let j = i + 1;
        let bestEnd = node.$ ? j : -1;
        let bestVal = node.$ || null;
        while (j < n && node[s[j]]) {
          node = node[s[j]];
          j++;
          if (node.$) {
            bestEnd = j;
            bestVal = node.$;
          }
        }
        if (bestVal && bestEnd > i) {
          const term = s.slice(i, bestEnd);
          if (term !== skipTerm) {
            emitLink(term, bestVal);
          } else {
            plain += term;
          }
          i = bestEnd;
          continue;
        }
      }

      plain += ch;
      i++;
    }
    flushPlain();
    return out;
  }

  function valBadgeHtml(val) {
    const s = String(val || "");
    let cls = "mod-val";
    if (s.startsWith("+") || s === "启用") cls += " pos";
    else if (s.startsWith("-") || s.startsWith("−") || s === "禁用") cls += " neg";
    return `<span class="${cls}">${esc(s)}</span>`;
  }

  function renderLinkedSourceGroupsHtml(groups, emptyMsg) {
    if (!groups || !groups.length) {
      return `<div style="font-size:12.5px;color:var(--ink-muted)">${esc(emptyMsg || "该项主要由基础公式与系统状态驱动。")}</div>`;
    }
    return `<div class="mod-groups-grid">${groups.map(([gname, items, totalCnt]) => `
      <div class="mod-group-box">
        <div class="mod-group-title"><span>${esc(gname)}</span><small>${totalCnt} 项</small></div>
        <ul class="mod-src-list">
          ${items.map((it) => {
            const nameHtml = it.href
              ? `<a class="ent-link" href="${esc(it.href)}" title="跳转查看「${esc(it.zh)}」详细词条">${esc(it.zh)}</a>`
              : linkifyEntitiesHtml(it.zh);
            const condHtml = it.cond ? ` <small class="mod-src-cond">(${linkifyEntitiesHtml(it.cond, it.zh)})</small>` : "";
            return `<li><span class="mod-src-name">${nameHtml}${condHtml}</span>${valBadgeHtml(it.val)}</li>`;
          }).join("")}
        </ul>
        ${totalCnt > items.length ? `<div class="mod-more-note">另有 ${totalCnt - items.length} 项同类来源（可在22速查表或72名录中检索）</div>` : ""}
      </div>
    `).join("")}</div>`;
  }

  function formatClausesHtml(detailStr, condStr, skipTerm) {
    const raw = String(detailStr || "—").trim();
    const parts = raw.split(" ｜ ").map((x) => x.trim()).filter(Boolean);
    const lines = parts.map((p) => {
      const idx = p.indexOf("：");
      if (idx > 0 && idx <= 12) {
        return `<div class="dir-clause"><strong>${esc(p.slice(0, idx + 1))}</strong>${linkifyEntitiesHtml(p.slice(idx + 1), skipTerm)}</div>`;
      }
      return `<div class="dir-clause">${linkifyEntitiesHtml(p, skipTerm)}</div>`;
    });
    if (condStr && !raw.includes("条件：")) {
      lines.push(`<div class="dir-clause dir-cond"><strong>获取/触发条件：</strong>${linkifyEntitiesHtml(condStr, skipTerm)}</div>`);
    }
    return `<div class="dir-clauses">${lines.join("")}</div>`;
  }

  function renderDetailDrawer(r, colspan) {
    const skipTerm = r.zh || "";
    const pairs = [];
    if (Array.isArray(r.detail_pairs) && r.detail_pairs.length) {
      r.detail_pairs.forEach(([k, v]) => pairs.push([k, v]));
    } else {
      if (r.detail) {
        String(r.detail).split(" ｜ ").map((x) => x.trim()).filter(Boolean).forEach((seg, i) => {
          const idx = seg.indexOf("：");
          if (idx > 0 && idx <= 14) pairs.push([seg.slice(0, idx), seg.slice(idx + 1)]);
          else pairs.push([i === 0 ? "核心属性" : `机制说明 ${i + 1}`, seg]);
        });
      }
      if (r.scopeConditions && !String(r.detail || "").includes("条件：")) pairs.push(["前置与限制条件", r.scopeConditions]);
      if (r.scopeReason) pairs.push(["适用口径说明", r.scopeReason]);
      if (r.tag) pairs.push(["国家标签", r.tag]);
      if (r.kind) pairs.push(["分类", r.kind]);
      if (r.source) pairs.push(["游戏源码位置", r.source]);
    }
    if (!pairs.length) {
      return `<tr class="detail-row"><td colspan="${colspan}"><div style="font-size:12.5px;color:var(--ink-muted)">ID: <code>${esc(r.id || "")}</code>（无附加展开字段）</div></td></tr>`;
    }
    return `<tr class="detail-row"><td colspan="${colspan}"><dl class="detail-dl">${pairs.map(([k, v]) => {
      const isCodeKey = /源码位置|文件位置|^ID$|国家标签/.test(String(k));
      const ddHtml = isCodeKey ? esc(v) : linkifyEntitiesHtml(v, skipTerm);
      return `<div><dt>${esc(k)}</dt><dd>${ddHtml}</dd></div>`;
    }).join("")}</dl></td></tr>`;
  }

  document.addEventListener("DOMContentLoaded", () => {
    const page = document.body.getAttribute("data-page");
    if (page === "metrics") initMetricsPage();
    else if (page === "map") initMapExplorer();
    else if (page === "lab") initLabPage();
    else if (page === "ledgers") initLedgersPage();
    else if (page === "pop-demand") initPopDemandPage();
    else if (page === "directory") initDirectoryPage();
    else if (page === "units") initUnitsPage();
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
      `<div>${expandable ? `<span class="row-toggle-mark">${expandedIds.has(r.id) ? "▾" : "▸"}</span>` : ""}<strong>${esc(r.zh)}</strong>${r.scope ? ` <span class="scope-tag">${esc(r.scope.split(" / ")[0])}</span>` : ""}<br><small style="color:var(--ink-muted)">${esc(r.en)} <code style="font-size:10.5px">${esc(r.id)}</code></small></div>`;

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
          { label: "产出商品 / 职能", key: "output", fn: (r) => linkifyEntitiesHtml(r.output, r.zh) },
        ],
      },
      {
        id: "goods", grp: "econ", label: "75 商品产业链", filterKey: "rgo_badge", expandable: true,
        cols: [
          {
            label: "商品（点击展开全链条）", key: "zh",
            fn: (r) => `<div class="good-cell"><span class="row-toggle-mark">${expandedIds.has(r.id) ? "▾" : "▸"}</span>${r.icon ? `<img class="good-icon" src="${esc(r.icon)}" alt="" loading="lazy">` : ""}<div><strong>${esc(r.zh)}</strong><br><small style="color:var(--ink-muted)">${esc(r.en)} <code>${esc(r.id)}</code></small></div></div>`,
          },
          {
            label: "市价 / 食 / 运", key: "price", num: true,
            fn: (r) => `<span class="num"><strong>${r.price}</strong>金</span><br><small style="color:var(--ink-muted)">${r.food > 0 ? `<span class="pos">食${r.food}</span> · ` : ""}运${r.transport}</small>`,
          },
          {
            label: "是否 RGO 产出", key: "rgo_badge",
            fn: (r) => `${r.is_rgo === "是" ? `<span class="delta-chip pos">${esc(r.rgo_badge)}</span>` : `<span class="scope-tag">${esc(r.rgo_badge || r.group)}</span>`}${r.base > 0 ? `<br><small style="color:var(--ink-muted)">保底产出 ${r.base}</small>` : ""}`,
          },
          {
            label: "是否建筑材料（施工耗材）", key: "con_bldg_count", num: true,
            fn: (r) => r.is_con_mat === "是"
              ? `<div><span class="delta-chip pos" style="margin-bottom:3px">是</span> <small>${linkifyEntitiesHtml(String(r.con_mat_summary || "").replace(/^是\s*·\s*/, ""), r.zh)}</small></div>`
              : `<span class="scope-tag">否</span>`,
          },
          {
            label: "什么建筑生产它（产出 / RGO增产）", key: "prod_bldg_count", num: true,
            fn: (r) => `<small>${linkifyEntitiesHtml(r.producers_summary || "—", r.zh)}</small>`,
          },
          {
            label: "什么建筑需要它（生产投入 / 日常维护）", key: "need_bldg_count", num: true,
            fn: (r) => `<small>${linkifyEntitiesHtml(r.consumers_summary || "—", r.zh)}</small>`,
          },
        ],
      },
      {
        id: "industry_types", grp: "econ", label: "8 产业政策", filterKey: "scope", expandable: true,
        cols: [
          { label: "产业名称", key: "zh", fn: (r) => nameCell(r, true) },
          { label: "涵盖商品", key: "goods", fn: (r) => linkifyEntitiesHtml(r.goods, r.zh) },
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
          { label: "特权名称", key: "zh", fn: (r) => `<strong>${esc(r.zh)}</strong><br><small>${esc(r.en)} <code>${esc(r.id)}</code></small>` },
          { label: "适用范围", key: "scope", fn: (r) => linkifyEntitiesHtml(r.scope, r.zh) },
          { label: "地点修正与冲突互斥规则", key: "detail", fn: (r) => linkifyEntitiesHtml(r.detail, r.zh) },
        ],
      },
      {
        id: "estate_privileges", grp: "gov", label: "331 阶层特权", filterKey: "estate", expandable: true,
        cols: [
          { label: "特权名称", key: "zh", fn: (r) => nameCell(r, true) },
          { label: "获授阶层", key: "estate", fn: (r) => `<span class="cmd-type">${esc(r.estate)}</span>` },
          { label: "阶层力量%", key: "power_mod", num: true, fn: (r) => `<span class="num">${esc(r.power_mod)}</span>` },
          { label: "满意度均衡Δ", key: "sat_eq", num: true, fn: (r) => `<span class="num">${esc(r.sat_eq)}</span>` },
          { label: "主要全国修正摘选", key: "effects", fn: (r) => linkifyEntitiesHtml(r.effects, r.zh) },
        ],
      },
      {
        id: "estate_actions", grp: "gov", label: "12 阶层互动", filterKey: "kind",
        cols: [
          { label: "互动名称", key: "zh", fn: (r) => `<strong>${esc(r.zh)}</strong><br><small>${esc(r.en)} (${esc(r.id)})</small>` },
          { label: "类别", key: "kind", fn: (r) => esc(r.kind) },
          { label: "适用目标与条件", key: "target", fn: (r) => linkifyEntitiesHtml(r.target, r.zh) },
          { label: "耗费与惩罚代价", key: "cost", fn: (r) => linkifyEntitiesHtml(r.cost, r.zh) },
          { label: "实际收益与冷却", key: "effect", fn: (r) => `${linkifyEntitiesHtml(r.effect, r.zh)}<br><small style="color:var(--ink-muted)">冷却：${esc(r.cooldown)}</small>` },
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
          { label: "指定政体/宗教/国家", key: "groups", fn: (r) => `<small>${linkifyEntitiesHtml(r.groups, r.zh)}</small>` },
        ],
      },
      {
        id: "government_reforms", grp: "gov", label: "379 政府改革", filterKey: "age", expandable: true,
        cols: [
          { label: "改革名称", key: "zh", fn: (r) => nameCell(r, true) },
          { label: "解锁时代", key: "age", fn: (r) => esc(r.age) },
          { label: "政体要求", key: "government", fn: (r) => linkifyEntitiesHtml(r.government, r.zh) },
          { label: "社会价值资格", key: "societal_req", fn: (r) => linkifyEntitiesHtml(r.societal_req, r.zh) },
          { label: "实施(年)", key: "impl_years", num: true, fn: (r) => `<span class="num">${esc(r.impl_years)}</span>` },
          { label: "主要效果摘选", key: "effects", fn: (r) => linkifyEntitiesHtml(r.effects, r.zh) },
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
          { label: "部门名称", key: "zh", fn: (r) => `<strong>${esc(r.zh)}</strong><br><small>${esc(r.en)} <code>${esc(r.id)}</code></small>` },
          { label: "资格", key: "scope", fn: (r) => linkifyEntitiesHtml(r.scope, r.zh) },
          { label: "常驻 / 满维正面 / 缺维负面修正", key: "detail", fn: (r) => `${linkifyEntitiesHtml(r.detail, r.zh)}${r.conditions ? `<br><small style="color:var(--ink-muted)">${linkifyEntitiesHtml(r.conditions, r.zh)}</small>` : ""}` },
        ],
      },
      {
        id: "cabinet_actions", grp: "gov", label: "81 内阁行动", filterKey: "ability",
        cols: [
          { label: "行动名称", key: "zh", fn: (r) => `<strong>${esc(r.zh)}</strong><br><small>${esc(r.en)} <code>${esc(r.id)}</code></small>` },
          { label: "系别 / 资格", key: "ability", fn: (r) => `<span class="cmd-type">${esc(r.ability)}</span> ${esc(r.scope)}` },
          { label: "作用对象", key: "target", fn: (r) => esc(r.target) },
          { label: "核心效果与前置条件", key: "effect", fn: (r) => `${linkifyEntitiesHtml(r.effect, r.zh)}${r.conditions ? `<br><small style="color:var(--ink-muted)">${linkifyEntitiesHtml(r.conditions, r.zh)}</small>` : ""}` },
        ],
      },
      {
        id: "character_interactions", grp: "gov", label: "34 角色互动", filterKey: "scope",
        cols: [
          { label: "互动名称", key: "zh", fn: (r) => `<strong>${esc(r.zh)}</strong><br><small>${esc(r.en)}</small>` },
          { label: "适用资格", key: "scope", fn: (r) => linkifyEntitiesHtml(r.scope, r.zh) },
          { label: "详细机制、花费与效果", key: "detail", fn: (r) => `${linkifyEntitiesHtml(r.detail, r.zh)}${r.conditions ? `<br><small style="color:var(--ink-muted)">${linkifyEntitiesHtml(r.conditions, r.zh)}</small>` : ""}` },
        ],
      },
      {
        id: "societal_values", grp: "gov", label: "17 社会价值观", filterKey: "category", expandable: true,
        cols: [
          { label: "轴线名称（点击展开全量推手）", key: "zh", fn: (r) => nameCell(r, true) },
          { label: "分类 / 时代", key: "category", fn: (r) => `${esc(r.category)}<br><small>${esc(r.era)}</small>` },
          {
            label: "← 左端极点 (−100) 满额效应与非事件推手", key: "left_pole",
            fn: (r) => `<strong>${esc(r.left_pole)}</strong> <span class="scope-tag">${r.left_push_total || 0} 项推手</span>：${linkifyEntitiesHtml(r.left_effects, r.zh)}<div class="sv-push-brief"><strong>← 非事件左推：</strong>${linkifyEntitiesHtml(r.left_push_summary || "", r.zh)}</div>`,
          },
          {
            label: "→ 右端极点 (+100) 满额效应与非事件推手", key: "right_pole",
            fn: (r) => `<strong>${esc(r.right_pole)}</strong> <span class="scope-tag">${r.right_push_total || 0} 项推手</span>：${linkifyEntitiesHtml(r.right_effects, r.zh)}<div class="sv-push-brief"><strong>→ 非事件右推：</strong>${linkifyEntitiesHtml(r.right_push_summary || "", r.zh)}</div>`,
          },
        ],
      },
      {
        id: "unit_types", grp: "mil", label: "401 军事单位", filterKey: "category", expandable: true,
        cols: [
          { label: "单位名称", key: "zh", fn: (r) => nameCell(r, true) },
          { label: "兵种类别", key: "category", fn: (r) => `<small>${esc(r.category)}</small>` },
          { label: "时代", key: "age", fn: (r) => `<small>${esc(r.age)}</small>` },
          { label: "满编(人)", key: "troops", num: true, fn: (r) => `<span class="num">${esc(r.troops)}</span>` },
          { label: "战力/舰炮", key: "combat_power", num: true, fn: (r) => `<span class="num">${r.cannons && r.cannons !== "—" ? `${esc(r.cannons)}炮` : esc(r.combat_power)}</span>` },
          { label: "每宽火力", key: "power_per_w", num: true, fn: (r) => `<span class="num"><strong>${esc(r.power_per_w || "—")}</strong></span>` },
          { label: "主动性", key: "initiative", num: true, fn: (r) => `<span class="num">${esc(r.initiative || "—")}</span>` },
          { label: "相比同代标准兵种(Δ)", key: "vs_base", fn: (r) => `<small>${linkifyEntitiesHtml(r.vs_base || "标准 / 模板", r.zh)}</small>` },
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
          { label: "宣战理由", key: "zh", fn: (r) => `<strong>${esc(r.zh)}</strong><br><small>${esc(r.en)} <code>${esc(r.id)}</code></small>` },
          { label: "范围", key: "scope", fn: (r) => linkifyEntitiesHtml(r.scope, r.zh) },
          { label: "战争目标与核心条件", key: "detail", fn: (r) => linkifyEntitiesHtml(r.detail, r.zh) },
        ],
      },
      {
        id: "diplomatic_actions", grp: "mil", label: "194 外交行动", filterKey: "kind", expandable: true,
        cols: [
          { label: "行动名称", key: "zh", fn: (r) => nameCell(r, true) },
          { label: "行动层级", key: "kind", fn: (r) => `<span class="cmd-type">${esc(r.kind)}</span>` },
          { label: "成本", key: "cost", fn: (r) => linkifyEntitiesHtml(r.cost, r.zh) },
          { label: "接受度规则", key: "acceptance", fn: (r) => linkifyEntitiesHtml(r.acceptance, r.zh) },
          { label: "核心结果", key: "effect", fn: (r) => linkifyEntitiesHtml(r.effect, r.zh) },
        ],
      },
      {
        id: "subject_types", grp: "mil", label: "22 属国类型", filterKey: "can_annex",
        cols: [
          { label: "属国名称", key: "zh", fn: (r) => `<strong>${esc(r.zh)}</strong><br><small>${esc(r.en)} (${esc(r.id)})</small>` },
          { label: "层级 / 同君", key: "level", num: true, fn: (r) => `等级 ${esc(r.level)} · 同君：${esc(r.same_ruler)}` },
          { label: "贡赋机制", key: "subject_pays", fn: (r) => linkifyEntitiesHtml(r.subject_pays, r.zh) },
          { label: "外交容倍率", key: "diplo_cost_scale", num: true, fn: (r) => `<span class="num">${esc(r.diplo_cost_scale)}</span>` },
          { label: "吞并规则（速/年/好感）", key: "can_annex", fn: (r) => `${esc(r.can_annex)}（速 ${esc(r.annex_speed)} / 最少 ${esc(r.annex_min_years)} 年 / 好感 ${esc(r.annex_min_opinion)}）` },
        ],
      },
      {
        id: "international_organizations", grp: "mil", label: "37 国际组织", filterKey: "group", expandable: true,
        cols: [
          { label: "组织名称", key: "zh", fn: (r) => nameCell(r, true) },
          { label: "分类", key: "group", fn: (r) => `<small>${esc(r.group)}</small>` },
          { label: "成员范围", key: "membership", fn: (r) => `<small>${linkifyEntitiesHtml(r.membership, r.zh)}</small>` },
          { label: "领袖形式", key: "leadership", fn: (r) => linkifyEntitiesHtml(r.leadership, r.zh) },
          { label: "战争协作", key: "war", fn: (r) => `<small>${linkifyEntitiesHtml(r.war, r.zh)}</small>` },
          { label: "成员与领袖效果", key: "effects", fn: (r) => `<small>${linkifyEntitiesHtml(r.effects, r.zh)}</small>` },
        ],
      },
      {
        id: "religions", grp: "hist", label: "293 种宗教", filterKey: "group", expandable: true,
        cols: [
          { label: "宗教名称", key: "zh", fn: (r) => nameCell(r, true) },
          { label: "宗教组", key: "group", fn: (r) => `<span class="cmd-type">${esc(r.group)}</span>` },
          { label: "礼仪语言", key: "liturgical", fn: (r) => esc(r.liturgical) },
          { label: "信条槽", key: "aspect_slots", num: true, fn: (r) => `<span class="num">${esc(r.aspect_slots)}</span>` },
          { label: "信仰机制", key: "mechanics", fn: (r) => `<small>${linkifyEntitiesHtml(r.mechanics, r.zh)}</small>` },
          { label: "定义修正摘选", key: "effects", fn: (r) => `<small>${linkifyEntitiesHtml(r.effects, r.zh)}</small>` },
        ],
      },
      {
        id: "situations_disasters", grp: "hist", label: "24 局势 & 38 灾难", filterKey: "kind",
        cols: [
          { label: "事件 / 进程", key: "zh", fn: (r) => `<strong>${esc(r.zh)}</strong><br><small>${esc(r.en)}</small>` },
          { label: "类型 / 范围", key: "kind", fn: (r) => `<span class="cmd-type">${esc(r.kind)}</span> ${esc(r.scope)}` },
          { label: "触发概率、惩罚修正与机制说明", key: "detail", fn: (r) => linkifyEntitiesHtml(r.detail, r.zh) },
        ],
      },
    ];

    let curId = "building_types";
    let sortKey = "";
    let sortDir = "asc";
    let pageIdx = 0;
    let focusItemId = "";
    let goodsQuickMode = "all";
    const PAGE_SIZE = 100;
    const expandedIds = new Set();

    // Optional top banner for specialized visual views (e.g. units.html / societal values inertia tip)
    let bannerEl = document.getElementById("ledger-special-banner");
    if (!bannerEl && countEl && countEl.parentElement) {
      bannerEl = document.createElement("div");
      bannerEl.id = "ledger-special-banner";
      bannerEl.style.marginBottom = "12px";
      countEl.parentElement.insertAdjacentElement("afterend", bannerEl);
    }

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

    function renderSocietalDrawer(r, colspan) {
      return `<tr class="detail-row"><td colspan="${colspan}">
        <div style="font-size:12.5px;margin-bottom:8px;color:var(--ink-muted)">
          <strong>通用主动推手：</strong>外交内阁行动「<a class="ent-link" href="ledgers.html#cabinet_actions?id=change_societal_values">改变社会价值观</a>」可向任一端提供 <code>+0.10/月 × (1 + 0.005×君主DIP + 0.005×大臣DIP + 内阁效率)</code>；无事件静态均衡点 = <code>clamp((右推之和 − 左推之和) × 100, −100, +100)</code>。
        </div>
        <div class="sv-poles-drawer">
          <div class="sv-pole-col">
            <div class="sv-pole-head">
              <span>← 推向【${esc(r.left_pole)}】(−100) 的全部非事件来源</span>
              <span class="scope-tag"><code>${esc(r.left_push_key || "")}</code> · 共 ${r.left_push_total || 0} 项</span>
            </div>
            ${renderLinkedSourceGroupsHtml(r.left_pushes, "该极点主要通过通用内阁行动「改变社会价值观」推动。")}
          </div>
          <div class="sv-pole-col">
            <div class="sv-pole-head">
              <span>→ 推向【${esc(r.right_pole)}】(+100) 的全部非事件来源</span>
              <span class="scope-tag"><code>${esc(r.right_push_key || "")}</code> · 共 ${r.right_push_total || 0} 项</span>
            </div>
            ${renderLinkedSourceGroupsHtml(r.right_pushes, "该极点主要通过通用内阁行动「改变社会价值观」推动。")}
          </div>
        </div>
      </td></tr>`;
    }

    function render(shouldScrollFocus) {
      const cfg = CONFIGS.find((c) => c.id === curId) || CONFIGS[0];
      const rows = ledgerCache[curId];
      if (bannerEl) {
        if (curId === "unit_types") {
          bannerEl.hidden = false;
          bannerEl.innerHTML = `<div class="card" style="padding:11px 16px;display:flex;flex-wrap:wrap;justify-content:space-between;align-items:center;gap:10px;border-left:4px solid var(--p-military)">
            <div style="font-size:13.2px"><strong>需要按时代横览招募表或对比特色兵种？</strong> 已提供「六大时代常备/征召/海军演进矩阵」与「258 项国家/文化特色兵种进步对比（Δ）」可视化专页。</div>
            <a href="units.html" class="btn-pill" style="background:var(--p-military);color:#fff;border-color:var(--p-military)">打开军事单位时代矩阵与特色兵种专页 →</a>
          </div>`;
        } else if (curId === "societal_values") {
          bannerEl.hidden = false;
          bannerEl.innerHTML = `<div class="card" style="padding:11px 16px;display:flex;flex-wrap:wrap;justify-content:space-between;align-items:center;gap:10px;border-left:4px solid var(--p-state)">
            <div style="font-size:13.2px"><strong>惯性均衡规则：</strong>拉条范围 −100~+100（中性 0），系统惯性 100；长期静态均衡位置 = <code>(右推之和 − 左推之和) × 100</code>。点击下方任意行即可并排展开左右两端全部非事件推动源（均可点击跳转）。</div>
            <a href="ch04-government-cabinet.html#societal-values" class="btn-pill">阅读第四章 8 大非事件移动规律精讲 →</a>
          </div>`;
        } else if (curId === "goods") {
          bannerEl.hidden = false;
          bannerEl.innerHTML = `<div class="card" style="padding:11px 16px;display:flex;flex-wrap:wrap;justify-content:space-between;align-items:center;gap:10px;border-left:4px solid var(--p-economy)">
            <div style="font-size:13px"><strong>商品产业链快筛：</strong>点击任意商品行即可展开<strong>全部生产建筑 / 加工消耗建筑 / 维护消耗建筑 / 施工建材全表 / 军需单位</strong>，所有建筑名均可直接点击跳转。</div>
            <div style="display:flex;flex-wrap:wrap;gap:6px">
              <button type="button" class="submod-pill ${goodsQuickMode === "all" ? "active" : ""}" data-gq="all">全部商品 (75)</button>
              <button type="button" class="submod-pill ${goodsQuickMode === "rgo" ? "active" : ""}" data-gq="rgo">仅 RGO 产出 (53)</button>
              <button type="button" class="submod-pill ${goodsQuickMode === "non_rgo" ? "active" : ""}" data-gq="non_rgo">仅非 RGO 制成品 (22)</button>
              <button type="button" class="submod-pill ${goodsQuickMode === "con_mat" ? "active" : ""}" data-gq="con_mat">仅施工建筑材料 (27)</button>
              <a href="pop-demand.html" class="btn-pill" style="font-size:12px">查 8 阶级人口消费需求 →</a>
            </div>
          </div>`;
          bannerEl.querySelectorAll("[data-gq]").forEach((btn) => {
            btn.addEventListener("click", () => {
              goodsQuickMode = btn.getAttribute("data-gq");
              focusItemId = "";
              pageIdx = 0;
              render();
            });
          });
        } else {
          bannerEl.hidden = true;
          bannerEl.innerHTML = "";
        }
      }

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
        if (curId === "goods") {
          if (goodsQuickMode === "rgo" && r.is_rgo !== "是") return false;
          if (goodsQuickMode === "non_rgo" && r.is_rgo === "是") return false;
          if (goodsQuickMode === "con_mat" && r.is_con_mat !== "是") return false;
        }
        if (!q) return true;
        return JSON.stringify(r).toLowerCase().includes(q);
      });

      if (sortKey) {
        const colDef = cfg.cols.find((c) => c.key === sortKey);
        if (colDef) filtered = sortRows(filtered, sortKey, sortDir, !!colDef.num);
      }

      if (focusItemId && shouldScrollFocus) {
        const fIdx = filtered.findIndex((r) => r.id === focusItemId);
        if (fIdx >= 0) {
          pageIdx = Math.floor(fIdx / PAGE_SIZE);
          if (cfg.expandable) expandedIds.add(focusItemId);
        }
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
        const rowCls = [cfg.expandable ? "row-expandable" : "", focusItemId === r.id ? "row-focused" : ""].filter(Boolean).join(" ");
        const mainRow = `<tr class="${rowCls}" data-row-id="${esc(r.id)}">${cfg.cols.map((c) => `<td>${c.fn(r)}</td>`).join("")}</tr>`;
        if (!isOpen) return mainRow;
        if (curId === "societal_values") return mainRow + renderSocietalDrawer(r, cfg.cols.length);
        return mainRow + renderDetailDrawer(r, cfg.cols.length);
      }).join("");

      if (cfg.expandable) {
        bodyEl.querySelectorAll("tr.row-expandable").forEach((tr) => {
          tr.addEventListener("click", (ev) => {
            if (ev.target.closest("a, button")) return;
            const rid = tr.getAttribute("data-row-id");
            if (expandedIds.has(rid)) expandedIds.delete(rid);
            else expandedIds.add(rid);
            render();
          });
        });
      }

      if (shouldScrollFocus && focusItemId) {
        const focusRow = bodyEl.querySelector(`tr[data-row-id="${CSS.escape ? CSS.escape(focusItemId) : focusItemId}"]`);
        if (focusRow) setTimeout(() => focusRow.scrollIntoView({ behavior: "smooth", block: "center" }), 60);
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

    async function selectLedger(id, qPrefill, targetItemId, keepHash) {
      const cleanId = String(id || "").split("?")[0];
      curId = CONFIGS.some((c) => c.id === cleanId) ? cleanId : "building_types";
      sortKey = "";
      sortDir = "asc";
      pageIdx = 0;
      goodsQuickMode = "all";
      focusItemId = targetItemId || "";
      expandedIds.clear();
      if (typeof qPrefill === "string") qEl.value = qPrefill;
      tabsEl.querySelectorAll(".tab-btn").forEach((b) => b.classList.toggle("active", b.getAttribute("data-id") === curId));
      if (!keepHash) {
        history.replaceState(null, "", "#" + curId + (focusItemId ? `?id=${encodeURIComponent(focusItemId)}` : ""));
      }

      const cfg = CONFIGS.find((c) => c.id === curId);
      if (!ledgerCache[curId]) {
        render(false);
        await loadScriptOnce(`assets/ledgers/${curId}.js`);
      }
      buildSubFilter(cfg, ledgerCache[curId] || []);
      render(Boolean(focusItemId));
    }

    function applyHashFromLocation() {
      const rawHash = decodeURIComponent(location.hash.replace("#", ""));
      const [hId, qs] = rawHash.split("?");
      const params = new URLSearchParams(qs || "");
      selectLedger(hId || "building_types", params.get("q") || "", params.get("id") || "", true);
    }

    tabsEl.querySelectorAll(".tab-btn").forEach((b) => b.addEventListener("click", () => selectLedger(b.getAttribute("data-id"), "", "", false)));
    qEl.addEventListener("input", () => { focusItemId = ""; pageIdx = 0; render(); });
    subFilterEl.addEventListener("change", () => { focusItemId = ""; pageIdx = 0; render(); });
    window.addEventListener("hashchange", applyHashFromLocation);

    applyHashFromLocation();
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
          <td><div class="good-cell"><span class="row-toggle-mark">▸</span>${r.icon ? `<img class="good-icon" src="${esc(r.icon)}" alt="" loading="lazy">` : ""}<div><a class="ent-link" href="ledgers.html#goods?id=${esc(r.id)}"><strong>${esc(r.zh)}</strong></a><br><small style="color:var(--ink-muted)">${esc(r.en)}</small></div></div></td>
          <td><span class="num">${fmtNum(r.baseDemand)}</span></td>
          <td><span class="num">${fmtNum(r.classBaseDemand)}</span></td>
          <td><span class="num">${r.basePrice}</span></td>
          <td><span class="num ${r.baseSpend > 0 ? "pos" : ""}">${fmtNum(r.baseSpend)}</span></td>
          <td><small>${conds.length ? linkifyEntitiesHtml(conds.join(" ｜ "), r.zh) : "无额外门槛"}</small></td>
        </tr>`;
        if (!isOpen) return mainRow;
        const pairs = (r.details || []).map((d) => [d.label, d.text]).concat((r.conditions || []).map((c) => [c.label, c.text]));
        if (r.source) pairs.push(["商品来源", r.source]);
        if (r.raw?.demandSource) pairs.push(["需求来源", r.raw.demandSource]);
        return mainRow + `<tr class="detail-row"><td colspan="6"><dl class="detail-dl">${pairs.map(([k, v]) => {
          const isSrc = /来源/.test(String(k));
          return `<div><dt>${esc(k)}</dt><dd>${isSrc ? esc(v) : linkifyEntitiesHtml(v, r.zh)}</dd></div>`;
        }).join("")}</dl></td></tr>`;
      }).join("");

      bodyEl.querySelectorAll("tr.row-expandable").forEach((tr) => {
        tr.addEventListener("click", (ev) => {
          if (ev.target.closest("a, button")) return;
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
    let curCatId = "advances";
    let pageIdx = 0;
    let focusRecId = "";
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
      pickerEl.querySelectorAll(".cat-pill").forEach((b) => b.addEventListener("click", () => selectCatalog(b.getAttribute("data-cid"), "", "", false)));
    }

    function renderTable(shouldScrollFocus) {
      const meta = manifest.find((m) => m.id === curCatId);
      const obj = catalogCache[curCatId];
      if (!meta || !obj) {
        headerEl.innerHTML = `<strong>正在载入：${esc(meta?.zh || curCatId)}…</strong>`;
        bodyEl.innerHTML = `<tr><td colspan="4" style="padding:24px;text-align:center">正在加载分片目录数据…</td></tr>`;
        pagerEl.hidden = true;
        return;
      }

      const ledgerBtn = meta.id === "unit_types"
        ? `<a href="units.html" class="btn-pill" style="background:var(--p-military);color:#fff;border-color:var(--p-military)">打开全时代兵种矩阵与特色对比 →</a>`
        : (meta.ledger
          ? `<a href="ledgers.html#${esc(meta.ledger)}" class="btn-pill" style="background:var(--accent-2);color:#fff;border-color:var(--accent-2)">打开精排数值对照表 →</a>`
          : "");
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

      if (focusRecId && shouldScrollFocus) {
        const fIdx = filtered.findIndex((r) => r.id === focusRecId);
        if (fIdx >= 0) {
          pageIdx = Math.floor(fIdx / PAGE_SIZE);
          expanded.add(`${curCatId}:${focusRecId}`);
        }
      }

      const totalPages = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE));
      if (pageIdx >= totalPages) pageIdx = 0;
      const start = pageIdx * PAGE_SIZE;
      const slice = filtered.slice(start, start + PAGE_SIZE);

      countEl.textContent = `筛选匹配 ${filtered.length} / ${obj.records.length} 条（第 ${pageIdx + 1}/${totalPages} 页） · 点击任意行查看完整源码与前置条件`;
      bodyEl.innerHTML = slice.map((r) => {
        const key = `${curCatId}:${r.id}`;
        const isOpen = expanded.has(key);
        const rowCls = ["row-expandable", focusRecId === r.id ? "row-focused" : ""].filter(Boolean).join(" ");
        const mainRow = `<tr class="${rowCls}" data-dkey="${esc(key)}" data-rec-id="${esc(r.id)}">
          <td><span class="row-toggle-mark">${isOpen ? "▾" : "▸"}</span><strong>${esc(r.zh)}</strong><br><small style="color:var(--ink-muted)">${esc(r.en)} <code>${esc(r.id)}</code></small></td>
          <td><span class="scope-tag">${esc((r.scopeLabel || r.scope || "通用").split(" / ")[0])}</span></td>
          <td>${formatClausesHtml(r.detail, r.scopeConditions, r.zh)}</td>
          <td><small style="color:var(--ink-muted)">${esc(r.source || "—")}</small></td>
        </tr>`;
        return isOpen ? mainRow + renderDetailDrawer(r, 4) : mainRow;
      }).join("");

      bodyEl.querySelectorAll("tr.row-expandable").forEach((tr) => {
        tr.addEventListener("click", (ev) => {
          if (ev.target.closest("a, button")) return;
          const k = tr.getAttribute("data-dkey");
          if (expanded.has(k)) expanded.delete(k);
          else expanded.add(k);
          renderTable();
        });
      });

      if (shouldScrollFocus && focusRecId) {
        const focusRow = bodyEl.querySelector(`tr[data-rec-id="${CSS.escape ? CSS.escape(focusRecId) : focusRecId}"]`);
        if (focusRow) setTimeout(() => focusRow.scrollIntoView({ behavior: "smooth", block: "center" }), 60);
      }

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

    async function selectCatalog(cid, qPrefill, targetRecId, keepHash) {
      curCatId = manifest.some((m) => m.id === cid) ? cid : manifest[0].id;
      pageIdx = 0;
      focusRecId = targetRecId || "";
      expanded.clear();
      if (typeof qPrefill === "string") qEl.value = qPrefill;
      renderPicker();
      if (!keepHash) {
        history.replaceState(null, "", "#" + curCatId + (focusRecId ? `?id=${encodeURIComponent(focusRecId)}` : ""));
      }
      if (!catalogCache[curCatId]) {
        renderTable(false);
        await loadScriptOnce(`assets/catalogs/${curCatId}.js`);
      }
      const recs = catalogCache[curCatId]?.records || [];
      const scopes = Array.from(new Set(recs.map((r) => r.scope || "general")));
      const SCOPE_NAMES = { general: "通用 (general)", conditional: "制度或地域限定 (conditional)", country: "国别/标签关联 (country)", "country-scope": "国别限定" };
      scopeEl.innerHTML = `<option value="all">全部适用口径 (${recs.length})</option>` +
        scopes.map((s) => `<option value="${esc(s)}">${esc(SCOPE_NAMES[s] || s)}</option>`).join("");
      renderTable(Boolean(focusRecId));
    }

    function applyDirHash() {
      const rawHash = decodeURIComponent(location.hash.replace("#", ""));
      const [cid, qs] = rawHash.split("?");
      const params = new URLSearchParams(qs || "");
      selectCatalog(cid || "advances", params.get("q") || "", params.get("id") || "", true);
    }

    qEl.addEventListener("input", () => { focusRecId = ""; pageIdx = 0; renderTable(); });
    scopeEl.addEventListener("change", () => { focusRecId = ""; pageIdx = 0; renderTable(); });
    window.addEventListener("hashchange", applyDirHash);

    applyDirHash();
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
          <p>${linkifyEntitiesHtml(g.desc, g.zh)}</p>
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

  // 7. Core Metrics & 1,364 Modifiers Reverse Lookup (metrics.html)
  function initMetricsPage() {
    const data = window.__EU5_METRICS__;
    if (!data) return;

    const PILLAR_ZH = {
      territory: "疆域与控制",
      economy: "人口、市场与财政",
      state: "政府、内阁与阶层",
      culture: "文化、信仰与科技",
      military: "军事、海权与和约",
      diplomacy: "外交、属国与秩序",
    };

    const tabs = document.querySelectorAll("[data-met-tab]");
    const panels = document.querySelectorAll("[data-met-panel]");
    function switchTab(t) {
      tabs.forEach((b) => b.classList.toggle("active", b.getAttribute("data-met-tab") === t));
      panels.forEach((p) => (p.hidden = p.getAttribute("data-met-panel") !== t));
    }
    tabs.forEach((b) => b.addEventListener("click", () => switchTab(b.getAttribute("data-met-tab"))));

    function renderSourceGroupsHtml(groups) {
      return renderLinkedSourceGroupsHtml(groups, "该指标主要由上方基础公式与系统状态驱动。");
    }

    // --- Tab 1: 66 Separated Single-Concept Flagship Metrics ---
    const fmSearch = document.getElementById("fm-search");
    const fmPillar = document.getElementById("fm-pillar");
    const fmCount = document.getElementById("fm-count");
    const fmList = document.getElementById("fm-list");
    const openFlagships = new Set(["development", "prosperity", "production_efficiency"]);
    const activeSubModFilter = {};

    const LEGACY_HASH_MAP = {
      development_prosperity: "development",
      pop_growth_migration: "pop_growth",
      food_supply: "food_production",
      building_cost_cap: "supported_building_levels",
      trade_capacity_advantage: "trade_capacity",
      trade_efficiency_maint: "trade_efficiencies",
      minting_inflation_credit: "minting_inflation",
      crown_estate_power: "crown_power",
      stability_legitimacy_pi: "stability",
      research_literacy: "research_speed",
      culture_capacity_assimilation: "cultural_capacity",
      religious_tolerance_conversion: "religious_tolerance",
      discipline_tactics: "discipline",
      morale_initiative: "morale",
      siege_fort_supply: "siege_ability",
      manpower_sailors_maritime: "manpower",
      diplo_capacity_reputation: "diplo_capacity",
      subject_loyalty_annexation: "subject_loyalty",
    };

    function renderSubModifiersHtml(fm) {
      const subs = fm.sub_modifiers || [];
      if (!subs.length) {
        return `<div style="font-size:12.5px;color:var(--ink-muted)">该指标主要由上方基础公式与系统状态驱动。</div>`;
      }
      const curSub = activeSubModFilter[fm.id] || "all";
      const filterBar = subs.length > 1
        ? `<div class="submod-filter-bar">
            <span style="font-size:12px;color:var(--ink-muted);font-weight:600">按具体修正词条筛选：</span>
            <button type="button" class="submod-pill ${curSub === "all" ? "active" : ""}" data-fm-sub="${esc(fm.id)}" data-sub-id="all">全部并列展示 (${subs.length} 个词条 · 共 ${fm.total_sources} 处)</button>
            ${subs.map((sm, i) => `<button type="button" class="submod-pill ${curSub === sm.id ? "active" : ""}" data-fm-sub="${esc(fm.id)}" data-sub-id="${esc(sm.id)}">${i + 1}. ${esc(sm.zh)} <code>${esc(sm.id)}</code> (${sm.total})</button>`).join("")}
          </div>`
        : "";
      const visibleSubs = curSub === "all" ? subs : subs.filter((sm) => sm.id === curSub);
      const blocks = visibleSubs.map((sm, idx) => `
        <div class="submod-section">
          <div class="submod-head">
            <div>
              <strong>${subs.length > 1 ? `词条 ${idx + 1} · ` : ""}${esc(sm.zh)}</strong>
              <span style="color:var(--ink-muted);font-size:12.5px;margin-left:6px">${esc(sm.en)}</span>
              <code style="margin-left:6px">${esc(sm.id)}</code>
            </div>
            <div style="display:flex;gap:6px;align-items:center">
              <span class="scope-tag">${esc(sm.cat)}</span>
              <span class="scope-tag">共 ${sm.total} 处来源</span>
            </div>
          </div>
          ${renderSourceGroupsHtml(sm.groups)}
        </div>
      `).join("");
      return filterBar + blocks;
    }

    function renderFlagships(focusId) {
      const q = (fmSearch.value || "").trim().toLowerCase();
      const pil = fmPillar.value;
      const filtered = data.flagships.filter((fm) => {
        if (pil !== "all" && fm.pillar !== pil) return false;
        if (!q) return true;
        const hay = (fm.zh + " " + fm.en + " " + fm.id + " " + (fm.base_value || "") + " " + fm.formula_role + " " + fm.core_drivers.join(" ") + " " + JSON.stringify(fm.sub_modifiers)).toLowerCase();
        return hay.includes(q);
      });

      fmCount.textContent = `显示 ${filtered.length} / ${data.flagships.length} 项独立核心机制数值（每项均含基准值与可交叉跳转来源）`;
      fmList.innerHTML = filtered.map((fm) => {
        const isOpen = openFlagships.has(fm.id) || Boolean(q);
        const subDesc = (fm.sub_modifiers || []).map((s) => `${s.zh}(${s.total})`).join(" · ");
        return `<article id="${esc(fm.id)}" class="card metric-card" style="border-top:4px solid var(--p-${fm.pillar})${focusId === fm.id ? ";box-shadow:0 0 0 2px var(--accent)" : ""}">
          <div class="metric-card-head">
            <div>
              <span class="pillar-badge" style="background:var(--p-${fm.pillar})">${esc(PILLAR_ZH[fm.pillar] || fm.pillar)}</span>
              <h2 class="metric-title">${esc(fm.zh)} <small>${esc(fm.en)}</small></h2>
            </div>
            <div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap">
              <span class="scope-tag">${(fm.sub_modifiers || []).length} 个修正词条 · 共 ${fm.total_sources} 处来源</span>
              <a href="${esc(fm.chapter_href)}" class="btn-pill">阅读章节推导与算例 →</a>
            </div>
          </div>
          <div class="metric-base-box">
            <span class="metric-base-tag">基准值与范围</span>${linkifyEntitiesHtml(fm.base_value || "", fm.zh)}
          </div>
          <div class="formula-box" style="margin:10px 0">
            <strong>公式与结算作用：</strong>${linkifyEntitiesHtml(fm.formula_role, fm.zh)}
          </div>
          <div style="margin:10px 0">
            <strong style="font-size:13.5px;color:var(--ink)">在基准值基础上的全部正负变化因素：</strong>
            <ul class="metric-drivers">
              ${fm.core_drivers.map((d) => {
                const idx = d.indexOf("：");
                return idx > 0 && idx <= 24
                  ? `<li><strong>${esc(d.slice(0, idx + 1))}</strong>${linkifyEntitiesHtml(d.slice(idx + 1), fm.zh)}</li>`
                  : `<li>${linkifyEntitiesHtml(d, fm.zh)}</li>`;
              }).join("")}
            </ul>
          </div>
          <div class="metric-drawer-toggle">
            <button type="button" class="btn-pill" data-toggle-fm="${esc(fm.id)}">
              ${isOpen ? "▾ 收起" : "▸ 展开按修正词条分栏查看"}具体建筑 / 特权 / 改革 / 政策 / 时代革新来源（${esc(subDesc)}）
            </button>
          </div>
          ${isOpen ? `<div class="metric-sources-panel">${renderSubModifiersHtml(fm)}</div>` : ""}
        </article>`;
      }).join("");

      fmList.querySelectorAll("[data-toggle-fm]").forEach((btn) => {
        btn.addEventListener("click", () => {
          const id = btn.getAttribute("data-toggle-fm");
          if (openFlagships.has(id)) openFlagships.delete(id);
          else openFlagships.add(id);
          renderFlagships();
        });
      });

      fmList.querySelectorAll("[data-fm-sub]").forEach((btn) => {
        btn.addEventListener("click", () => {
          const fid = btn.getAttribute("data-fm-sub");
          const sid = btn.getAttribute("data-sub-id");
          activeSubModFilter[fid] = sid;
          renderFlagships();
        });
      });

      if (focusId) {
        const el = document.getElementById(focusId);
        if (el) setTimeout(() => el.scrollIntoView({ behavior: "smooth", block: "start" }), 60);
      }
    }

    // --- Tab 2: All 1,364 Modifiers ---
    const amSearch = document.getElementById("am-search");
    const amCat = document.getElementById("am-cat");
    const amCount = document.getElementById("am-count");
    const amBody = document.getElementById("am-tbody");
    const amPager = document.getElementById("am-pager");
    let amPage = 0;
    const AM_PAGE_SIZE = 80;
    const openMods = new Set();

    const cats = Array.from(new Set(data.modifiers.map((m) => m.cat)));
    amCat.innerHTML = `<option value="all">全部作用层级 (${data.modifiers.length} 项修正)</option>` +
      cats.map((c) => `<option value="${esc(c)}">${esc(c)}</option>`).join("");

    function renderAllMods() {
      const q = (amSearch.value || "").trim().toLowerCase();
      const cv = amCat.value;
      const filtered = data.modifiers.filter((m) => {
        if (cv !== "all" && m.cat !== cv) return false;
        if (!q) return true;
        if ((m.zh + " " + m.en + " " + m.id).toLowerCase().includes(q)) return true;
        return JSON.stringify(m.groups).toLowerCase().includes(q);
      });

      const totalPages = Math.max(1, Math.ceil(filtered.length / AM_PAGE_SIZE));
      if (amPage >= totalPages) amPage = 0;
      const start = amPage * AM_PAGE_SIZE;
      const slice = filtered.slice(start, start + AM_PAGE_SIZE);

      amCount.textContent = `匹配 ${filtered.length} / ${data.modifiers.length} 项修正（第 ${amPage + 1}/${totalPages} 页） · 点击任意行展开具体来源列表`;
      amBody.innerHTML = slice.map((m) => {
        const isOpen = openMods.has(m.id);
        const preview = m.groups.slice(0, 6).map(([g, , cnt]) => `${esc(g)} (${cnt})`).join(" · ");
        const row = `<tr class="row-expandable" data-mid="${esc(m.id)}">
          <td><span class="row-toggle-mark">${isOpen ? "▾" : "▸"}</span><strong>${esc(m.zh)}</strong><br><small style="color:var(--ink-muted)">${esc(m.en)} <code>${esc(m.id)}</code></small></td>
          <td><span class="scope-tag">${esc(m.cat)}</span></td>
          <td><span class="num"><strong>${m.total}</strong> 处</span></td>
          <td><small>${preview}${m.groups.length > 6 ? " …" : ""}</small></td>
        </tr>`;
        return isOpen ? row + `<tr class="detail-row"><td colspan="4">${renderSourceGroupsHtml(m.groups)}</td></tr>` : row;
      }).join("");

      amBody.querySelectorAll("tr.row-expandable").forEach((tr) => {
        tr.addEventListener("click", (ev) => {
          if (ev.target.closest("a, button")) return;
          const mid = tr.getAttribute("data-mid");
          if (openMods.has(mid)) openMods.delete(mid);
          else openMods.add(mid);
          renderAllMods();
        });
      });

      amPager.hidden = totalPages <= 1;
      amPager.innerHTML = `
        <span style="font-size:12.5px;color:var(--ink-muted)">第 ${start + 1}–${Math.min(filtered.length, start + AM_PAGE_SIZE)} 项 / 共 ${filtered.length} 项</span>
        <div style="display:flex;gap:8px;align-items:center">
          <button type="button" class="btn-pill" id="am-prev" ${amPage === 0 ? "disabled" : ""}>← 上一页</button>
          <span style="font-size:12.5px">第 ${amPage + 1} / ${totalPages} 页</span>
          <button type="button" class="btn-pill" id="am-next" ${amPage >= totalPages - 1 ? "disabled" : ""}>下一页 →</button>
        </div>
      `;
      document.getElementById("am-prev")?.addEventListener("click", () => { amPage = Math.max(0, amPage - 1); renderAllMods(); });
      document.getElementById("am-next")?.addEventListener("click", () => { amPage = Math.min(totalPages - 1, amPage + 1); renderAllMods(); });
    }

    function applyHashRouting() {
      const rawH = decodeURIComponent(location.hash.replace("#", "")).trim();
      const h = LEGACY_HASH_MAP[rawH] || rawH;
      if (!h) {
        renderFlagships();
        renderAllMods();
        return;
      }
      if (h.startsWith("mod:")) {
        const modKey = h.slice(4);
        switchTab("allmods");
        amSearch.value = modKey;
        openMods.add(modKey);
        amPage = 0;
        renderAllMods();
        renderFlagships();
      } else if (data.flagships.some((x) => x.id === h)) {
        switchTab("flagships");
        fmPillar.value = "all";
        fmSearch.value = "";
        openFlagships.add(h);
        renderFlagships(h);
        renderAllMods();
      } else {
        renderFlagships();
        renderAllMods();
      }
    }

    fmSearch.addEventListener("input", () => renderFlagships());
    fmPillar.addEventListener("change", () => renderFlagships());
    amSearch.addEventListener("input", () => { amPage = 0; renderAllMods(); });
    amCat.addEventListener("change", () => { amPage = 0; renderAllMods(); });
    window.addEventListener("hashchange", applyHashRouting);

    applyHashRouting();
  }

  // 8. Military Units 6-Age Progression Matrix & Unique Units Delta Atlas (units.html)
  function initUnitsPage() {
    const units = window.__EU5_UNITS_ATLAS__;
    if (!units || !units.length) return;

    const unitMap = Object.create(null);
    units.forEach((u) => { unitMap[u.id] = u; });

    const tabs = document.querySelectorAll("[data-unit-tab]");
    const panels = document.querySelectorAll("[data-unit-panel]");
    let curTab = "matrix";

    function switchTab(t) {
      curTab = t;
      tabs.forEach((b) => b.classList.toggle("active", b.getAttribute("data-unit-tab") === t));
      panels.forEach((p) => (p.hidden = p.getAttribute("data-unit-panel") !== t));
    }
    tabs.forEach((b) => b.addEventListener("click", () => {
      const t = b.getAttribute("data-unit-tab");
      switchTab(t);
      history.replaceState(null, "", "#" + t);
    }));

    const AGES = [
      { idx: 1, zh: "① 传统时代", sub: "1337 起 · 步500/骑200" },
      { idx: 2, zh: "② 文艺复兴", sub: "步1,000 / 骑400 / 火炮登场" },
      { idx: 3, zh: "③ 地理大发现", sub: "步1,500 / 骑600 / 炮600" },
      { idx: 4, zh: "④ 宗教改革", sub: "步2,000(战1.5) / 骑800" },
      { idx: 5, zh: "⑤ 专制主义", sub: "步2,500(战2.25) / 骑1,000" },
      { idx: 6, zh: "⑥ 革命时代", sub: "步3,000(战3.0) / 骑1,200" },
    ];

    const MATRIX_ROWS = {
      land_reg: [
        { key: "heavy_infantry", zh: "重步兵", note: "基础承伤 1.00 · 侧翼防御 +5% · 主战填线核心" },
        { key: "light_infantry", zh: "轻步兵", note: "基础承伤 1.00 · 主动 5 · 天生杀伤-10%/士气承伤+10%" },
        { key: "heavy_cavalry", zh: "重骑兵", note: "基础承伤 0.30 · 侧击 1.6× · 破阵冲击主力" },
        { key: "light_cavalry", zh: "轻骑兵", note: "基础承伤 0.30 · 侧击 1.6× · 主动 5 · 高移速追击" },
        { key: "artillery", zh: "炮兵", note: "基础承伤 1.25 · 围城加点 + 战斗首阶段炮击弹幕" },
        { key: "auxiliary", zh: "辅助辎重", note: "非主战 · 单营高达 3,000 随军储粮支撑远征围城" },
      ],
      land_levy: [
        { key: "light_infantry", zh: "平民轻步征召", note: "农民/劳工/部落人口按比例征召 · 战时免常备维护" },
        { key: "heavy_infantry", zh: "城镇重步征召", note: "市民/自由民重装征召 · 前中期填补阵线宽度" },
        { key: "heavy_cavalry", zh: "贵族骑士征召", note: "贵族阶层精锐重骑 · 前两时代极具性价比的冲击核心" },
      ],
      navy: [
        { key: "heavy_ship", zh: "重型战舰", note: "占宽 1.5 · 巨量舰炮与船体耐久 · 大洋决战与轰城主力" },
        { key: "light_ship", zh: "轻型战舰", note: "占宽 1.0 · 最快航速 · 海上存在与护航/反海盗核心" },
        { key: "galley", zh: "桨帆战舰", note: "占宽 0.5 · 内陆海+25% / 海峡+50% · 深海-100%" },
        { key: "transport", zh: "运输船", note: "占宽 1.0 · 跨海运载陆军兵团登陆（随时代扩容）" },
      ],
    };

    // Include universal flagship / late galley upgrades in Naval matrix so Age 6 has zero empty gaps
    const EXTRA_MATRIX_IDS = new Set(["n_ship_of_the_line", "n_archipelago_frigate"]);

    // --- Tab 1: 6-Age Standard Progression Matrix ---
    const rolePills = document.querySelectorAll("[data-um-role]");
    const matrixWrap = document.getElementById("um-matrix-wrap");
    const matrixDetailEl = document.getElementById("um-selected-detail");
    let curRole = "land_reg";
    let selectedMatrixId = "a_footmen";

    function getMatrixCellUnits(role, catKey, ageIdx) {
      return units.filter((u) => {
        if (u.is_template || u.age_idx !== ageIdx || u.cat_key !== catKey) return false;
        if (role === "land_reg") return u.domain === "land" && !u.is_levy && !u.is_unique;
        if (role === "land_levy") return u.domain === "land" && u.is_levy && !u.is_unique;
        if (role === "navy") return u.domain === "navy" && (!u.is_unique || EXTRA_MATRIX_IDS.has(u.id));
        return false;
      });
    }

    function fmtSignedPct(v) {
      if (!v) return "";
      return (v > 0 ? "+" : "") + v + "%";
    }

    function renderMatrixDetail() {
      const u = unitMap[selectedMatrixId];
      if (!u || !matrixDetailEl) {
        if (matrixDetailEl) matrixDetailEl.innerHTML = "";
        return;
      }
      const sameSlotUniques = units.filter((x) => x.is_unique && x.age_idx === u.age_idx && x.cat_key === u.cat_key && x.is_levy === u.is_levy);
      const advHtml = u.adv_id
        ? `<a class="ent-link" href="directory.html#advances?id=${esc(u.adv_id)}">${esc(u.adv_zh)}</a>`
        : (u.adv_zh ? linkifyEntitiesHtml(u.adv_zh, u.zh) : "时代基础默认可募");
      const upgHtml = u.upg_id
        ? `<a class="ent-link" href="#${esc(u.upg_id)}">${esc(u.upg_zh)}</a>`
        : (u.upg_zh || "已至终极型号");

      const combatNotes = [];
      if (u.str_done) combatNotes.push(`兵力杀伤 ${fmtSignedPct(u.str_done)}`);
      if (u.str_taken) combatNotes.push(`兵力承伤 ${fmtSignedPct(u.str_taken)}`);
      if (u.mor_done) combatNotes.push(`士气杀伤 ${fmtSignedPct(u.mor_done)}`);
      if (u.mor_taken) combatNotes.push(`士气承伤 ${fmtSignedPct(u.mor_taken)}`);
      if (u.bombard_eff) combatNotes.push(`炮击效率 +${u.bombard_eff}%`);

      const statsSummary = u.domain === "land"
        ? `满编 <strong>${u.troops}</strong> 人 · 陆战战力 <strong>${u.combat_power}</strong> · 正面宽度 <strong>${u.frontage}</strong> · 每宽等效火力 <strong>${u.power_per_width}</strong> · 主动性 <strong>${u.initiative}</strong> · 参战速度 <strong>${u.combat_speed}</strong> · 侧击 <strong>${u.flanking}×</strong> · 兵种基础承伤系数 <strong>${u.cat_dmg_taken}</strong> · 行军移速 <strong>${u.move_speed}</strong> · 储粮/耗粮 <strong>${u.food_store}/${u.food_cons}</strong>`
        : `船员 <strong>${u.troops}</strong> 人 · 舰炮 <strong>${u.cannons}</strong> 门 · 船体耐久 <strong>${u.hull}</strong> · 正面宽度 <strong>${u.frontage}</strong> · 每宽舰炮 <strong>${u.cannons_per_width}</strong> · 航速 <strong>${u.move_speed}</strong> · 海上存在 <strong>${u.maritime}</strong>/月 · 封锁 <strong>${u.blockade}</strong> · 运兵量 <strong>${u.transport}</strong> 人`;

      const uniqLinks = sameSlotUniques.length
        ? `<div style="margin-top:10px;padding-top:9px;border-top:1px dashed var(--border);font-size:12.5px">
            <strong>同代同系国家/文化特色兵种（共 ${sameSlotUniques.length} 项，点击直接对比 Δ）：</strong>
            <div style="display:flex;flex-wrap:wrap;gap:6px;margin-top:6px">
              ${sameSlotUniques.slice(0, 24).map((x) => {
                const dBrief = (x.deltas || []).slice(0, 2).map((d) => `${d.stat}${d.diff}`).join(" ");
                return `<a class="btn-pill" href="#${esc(x.id)}" style="font-size:12px">${esc(x.zh)}${dBrief ? ` <small style="opacity:0.8">(${esc(dBrief)})</small>` : ""}</a>`;
              }).join("")}
              ${sameSlotUniques.length > 24 ? `<span style="font-size:12px;color:var(--ink-muted)">…等 ${sameSlotUniques.length} 项（切至上方标签②可全览）</span>` : ""}
            </div>
          </div>`
        : "";

      matrixDetailEl.innerHTML = `<div class="card" style="border-left:4px solid #b06c1d;padding:14px 18px">
        <div style="display:flex;flex-wrap:wrap;justify-content:space-between;align-items:baseline;gap:8px;margin-bottom:8px">
          <div>
            <span class="scope-tag">${esc(u.age_zh)}</span>
            <span class="scope-tag">${esc(u.cat_zh)} · ${esc(u.unit_type)}</span>
            <strong style="font-size:17px;margin-left:6px">${esc(u.zh)}</strong>
            <small style="color:var(--ink-muted);margin-left:6px">${esc(u.en)} <code>${esc(u.id)}</code></small>
          </div>
          <a class="btn-pill" href="ledgers.html#unit_types?id=${esc(u.id)}">在 401 单位速查表中展开源码级词条 →</a>
        </div>
        <div style="font-size:13px;line-height:1.65;margin-bottom:6px">${statsSummary}</div>
        <div class="uu-meta">
          ${combatNotes.length ? `<div><strong>固有攻防修正：</strong>${esc(combatNotes.join(" ｜ "))}</div>` : ""}
          ${u.terrain ? `<div><strong>地形作战修正：</strong>${esc(u.terrain)}</div>` : ""}
          <div><strong>解锁革新：</strong>${advHtml} &nbsp;｜&nbsp; <strong>下一代升级型号：</strong>${upgHtml}${u.build_time ? ` &nbsp;｜&nbsp; <strong>基础组建工期：</strong>${u.build_time} 天` : ""}</div>
          <div><strong>建造与维护商品需求：</strong>${linkifyEntitiesHtml(u.goods || "征召免常备建造费", u.zh)}</div>
        </div>
        ${uniqLinks}
      </div>`;
    }

    function renderMatrix() {
      rolePills.forEach((b) => b.classList.toggle("active", b.getAttribute("data-um-role") === curRole));
      const rowsCfg = MATRIX_ROWS[curRole] || MATRIX_ROWS.land_reg;

      const thead = `<thead><tr>
        <th>兵种序列与机制定位</th>
        ${AGES.map((a) => `<th><div>${esc(a.zh)}</div><small style="font-weight:400;color:var(--ink-muted)">${esc(a.sub)}</small></th>`).join("")}
      </tr></thead>`;

      const tbody = `<tbody>${rowsCfg.map((rc) => {
        const cells = AGES.map((a) => {
          const cellUnits = getMatrixCellUnits(curRole, rc.key, a.idx);
          if (!cellUnits.length) {
            return `<td><div class="um-empty">${a.idx === 1 && (rc.key === "artillery" || rc.key === "auxiliary" || rc.key === "heavy_ship" || rc.key === "light_ship") ? "本时代尚未解锁" : "沿用前代编制"}</div></td>`;
          }
          return `<td><div class="um-cell-stack">${cellUnits.map((u) => {
            const isSel = selectedMatrixId === u.id;
            const fireBadge = u.domain === "land"
              ? `火力 ${u.power_per_width}`
              : `${u.cannons_per_width} 炮/宽`;
            const statLine = u.domain === "land"
              ? `<span>${u.troops}人</span><span>战${u.combat_power}</span><span>主动${u.initiative}</span>${u.bombard_eff ? `<span>炮击+${u.bombard_eff}%</span>` : ""}${u.food_store >= 100 ? `<span>储粮${u.food_store}</span>` : ""}`
              : `<span>${u.cannons}炮</span><span>船体${u.hull}</span><span>速${u.move_speed}</span>${u.transport >= 200 ? `<span>运${u.transport}</span>` : `<span>海巡${u.maritime}</span>`}`;
            return `<div class="um-card ${isSel ? "active" : ""}" data-um-uid="${esc(u.id)}">
              <div class="um-card-title"><span>${esc(u.zh)}</span><span class="um-fire-badge">${esc(fireBadge)}</span></div>
              <div class="um-stat-grid">${statLine}</div>
              ${u.upg_zh ? `<div class="um-upg">→ ${esc(u.upg_zh)}</div>` : ""}
            </div>`;
          }).join("")}</div></td>`;
        }).join("");
        return `<tr><td><div><strong>${esc(rc.zh)}</strong></div><small style="color:var(--ink-muted);line-height:1.4;display:block;margin-top:3px">${esc(rc.note)}</small></td>${cells}</tr>`;
      }).join("")}</tbody>`;

      matrixWrap.innerHTML = `<table class="data-table unit-matrix-table">${thead}${tbody}</table>`;
      matrixWrap.querySelectorAll("[data-um-uid]").forEach((el) => {
        el.addEventListener("click", () => {
          selectedMatrixId = el.getAttribute("data-um-uid");
          renderMatrix();
        });
      });
      renderMatrixDetail();
    }

    rolePills.forEach((b) => b.addEventListener("click", () => {
      curRole = b.getAttribute("data-um-role");
      const firstHit = AGES.flatMap((a) => (MATRIX_ROWS[curRole] || []).flatMap((r) => getMatrixCellUnits(curRole, r.key, a.idx)))[0];
      if (firstHit) selectedMatrixId = firstHit.id;
      renderMatrix();
    }));

    // --- Tab 2: 258 Unique Country / Culture Units vs Same-Age Standard Base ---
    const uuSearch = document.getElementById("uu-search");
    const uuAge = document.getElementById("uu-age");
    const uuCat = document.getElementById("uu-cat");
    const uuRole = document.getElementById("uu-role");
    const uuCount = document.getElementById("uu-count");
    const uuList = document.getElementById("uu-list");
    const uuPager = document.getElementById("uu-pager");
    const uniqueUnits = units.filter((u) => u.is_unique).sort((a, b) => (a.age_idx - b.age_idx) || (a.cat_ord - b.cat_ord) || a.zh.localeCompare(b.zh, "zh-Hans-CN"));
    let uuPage = 0;
    let focusUniqueId = "";
    const UU_PAGE_SIZE = 60;

    function renderUniques(shouldScroll) {
      const q = (uuSearch.value || "").trim().toLowerCase();
      const ageV = uuAge.value;
      const catV = uuCat.value;
      const roleV = uuRole.value;

      const filtered = uniqueUnits.filter((u) => {
        if (ageV !== "all" && String(u.age_idx) !== ageV) return false;
        if (catV !== "all" && u.cat_key !== catV) return false;
        if (roleV === "reg" && u.is_levy) return false;
        if (roleV === "levy" && !u.is_levy) return false;
        if (!q) return true;
        const deltaStr = (u.deltas || []).map((d) => d.stat + d.diff).join(" ");
        const hay = `${u.zh} ${u.en} ${u.id} ${u.eligibility || ""} ${u.adv_zh || ""} ${u.base_zh || ""} ${u.terrain || ""} ${u.goods || ""} ${deltaStr}`.toLowerCase();
        return hay.includes(q);
      });

      if (focusUniqueId && shouldScroll) {
        const fIdx = filtered.findIndex((u) => u.id === focusUniqueId);
        if (fIdx >= 0) uuPage = Math.floor(fIdx / UU_PAGE_SIZE);
      }

      const totalPages = Math.max(1, Math.ceil(filtered.length / UU_PAGE_SIZE));
      if (uuPage >= totalPages) uuPage = 0;
      const start = uuPage * UU_PAGE_SIZE;
      const slice = filtered.slice(start, start + UU_PAGE_SIZE);

      uuCount.textContent = `匹配 ${filtered.length} / ${uniqueUnits.length} 项国家/文化特色单位（第 ${uuPage + 1}/${totalPages} 页）`;
      uuList.innerHTML = slice.map((u) => {
        const statsHtml = u.domain === "land"
          ? `<span>满编 <strong>${u.troops}</strong></span><span>战力 <strong>${u.combat_power}</strong></span><span>宽 <strong>${u.frontage}</strong></span><span>每宽火力 <strong>${u.power_per_width}</strong></span><span>主动 <strong>${u.initiative}</strong></span><span>侧击 <strong>${u.flanking}×</strong></span><span>承伤基数 <strong>${u.cat_dmg_taken}</strong></span>`
          : `<span>船员 <strong>${u.troops}</strong></span><span>舰炮 <strong>${u.cannons}</strong></span><span>船体 <strong>${u.hull}</strong></span><span>宽 <strong>${u.frontage}</strong></span><span>每宽舰炮 <strong>${u.cannons_per_width}</strong></span><span>航速 <strong>${u.move_speed}</strong></span><span>海巡 <strong>${u.maritime}</strong></span>`;

        const baseLink = u.base_id
          ? `<a class="ent-link" href="#${esc(u.base_id)}">${esc(u.base_zh)}</a>`
          : esc(u.base_zh || "同代标准模板");
        const deltas = u.deltas || [];
        const deltaChips = deltas.length
          ? `<div class="uu-delta-chips">${deltas.map((d) =>
              `<span class="delta-chip ${d.pol === "pos" ? "pos" : (d.pol === "neg" ? "neg" : "")}">${esc(d.stat)} ${esc(d.diff)} <small>(${esc(d.detail)})</small></span>`
            ).join("")}</div>`
          : `<div style="font-size:12px;color:var(--ink-muted)">核心战斗面板与同代基准持平（主要提供特殊文化征召渠道、专属兵营上限或更低维护物资）</div>`;

        const advPart = u.adv_id
          ? `解锁革新：<a class="ent-link" href="directory.html#advances?id=${esc(u.adv_id)}">${esc(u.adv_zh)}</a>`
          : (u.adv_zh ? `解锁革新：${linkifyEntitiesHtml(u.adv_zh, u.zh)}` : "");
        const upgPart = u.upg_id
          ? `后续升级：<a class="ent-link" href="#${esc(u.upg_id)}">${esc(u.upg_zh)}</a>`
          : (u.upg_zh ? `后续升级：${esc(u.upg_zh)}` : "");

        return `<article id="${esc(u.id)}" class="uu-card ${focusUniqueId === u.id ? "focused" : ""}">
          <div class="uu-head">
            <div>
              <h3 class="uu-title">${esc(u.zh)} <small>${esc(u.en)}</small></h3>
              <div style="margin-top:3px;display:flex;flex-wrap:wrap;gap:5px">
                <span class="scope-tag">${esc(u.age_zh)}</span>
                <span class="scope-tag">${esc(u.cat_zh)} · ${esc(u.unit_type)}</span>
                <code style="font-size:11px;color:var(--ink-muted)">${esc(u.id)}</code>
              </div>
            </div>
            <a class="btn-pill" href="ledgers.html#unit_types?id=${esc(u.id)}" style="font-size:11.5px;padding:3px 8px">源码明细</a>
          </div>
          <div class="uu-stats-bar">${statsHtml}</div>
          <div class="uu-delta-box">
            <div class="uu-delta-head">相比同代标准【${baseLink}】的数值进步与取舍（Δ）：</div>
            ${deltaChips}
          </div>
          <div class="uu-meta">
            ${u.eligibility ? `<div><strong>国家/文化与前置资格：</strong>${linkifyEntitiesHtml(u.eligibility, u.zh)}</div>` : ""}
            ${u.limit ? `<div><strong>招募上限规则：</strong>${linkifyEntitiesHtml(u.limit, u.zh)}</div>` : ""}
            ${(advPart || upgPart) ? `<div>${[advPart, upgPart].filter(Boolean).join(" &nbsp;｜&nbsp; ")}</div>` : ""}
            ${u.terrain ? `<div><strong>地形伤害修正：</strong>${esc(u.terrain)}</div>` : ""}
            <div><strong>建造与维护物资：</strong>${linkifyEntitiesHtml(u.goods || "免商品消耗", u.zh)}</div>
          </div>
        </article>`;
      }).join("");

      if (shouldScroll && focusUniqueId) {
        const el = document.getElementById(focusUniqueId);
        if (el) setTimeout(() => el.scrollIntoView({ behavior: "smooth", block: "center" }), 60);
      }

      uuPager.hidden = totalPages <= 1;
      uuPager.innerHTML = `
        <span style="font-size:12.5px;color:var(--ink-muted)">第 ${start + 1}–${Math.min(filtered.length, start + UU_PAGE_SIZE)} 项 / 共 ${filtered.length} 项</span>
        <div style="display:flex;gap:8px;align-items:center">
          <button type="button" class="btn-pill" id="uu-prev" ${uuPage === 0 ? "disabled" : ""}>← 上一页</button>
          <span style="font-size:12.5px">第 ${uuPage + 1} / ${totalPages} 页</span>
          <button type="button" class="btn-pill" id="uu-next" ${uuPage >= totalPages - 1 ? "disabled" : ""}>下一页 →</button>
        </div>
      `;
      document.getElementById("uu-prev")?.addEventListener("click", () => { uuPage = Math.max(0, uuPage - 1); renderUniques(); });
      document.getElementById("uu-next")?.addEventListener("click", () => { uuPage = Math.min(totalPages - 1, uuPage + 1); renderUniques(); });
    }

    uuSearch.addEventListener("input", () => { focusUniqueId = ""; uuPage = 0; renderUniques(); });
    uuAge.addEventListener("change", () => { focusUniqueId = ""; uuPage = 0; renderUniques(); });
    uuCat.addEventListener("change", () => { focusUniqueId = ""; uuPage = 0; renderUniques(); });
    uuRole.addEventListener("change", () => { focusUniqueId = ""; uuPage = 0; renderUniques(); });

    // --- Tab 3: All 401 Units Table ---
    const uaSearch = document.getElementById("ua-search");
    const uaHideTpl = document.getElementById("ua-hide-tpl");
    const uaCount = document.getElementById("ua-count");
    const uaBody = document.getElementById("ua-tbody");
    const uaPager = document.getElementById("ua-pager");
    let uaPage = 0;
    let focusAllId = "";
    const UA_PAGE_SIZE = 80;

    function renderAllUnits(shouldScroll) {
      const q = (uaSearch.value || "").trim().toLowerCase();
      const hideTpl = uaHideTpl.checked;
      const filtered = units.filter((u) => {
        if (hideTpl && u.is_template) return false;
        if (!q) return true;
        return (`${u.zh} ${u.en} ${u.id} ${u.cat_zh} ${u.age_zh} ${u.eligibility || ""}`).toLowerCase().includes(q);
      });

      if (focusAllId && shouldScroll) {
        const fIdx = filtered.findIndex((u) => u.id === focusAllId);
        if (fIdx >= 0) uaPage = Math.floor(fIdx / UA_PAGE_SIZE);
      }

      const totalPages = Math.max(1, Math.ceil(filtered.length / UA_PAGE_SIZE));
      if (uaPage >= totalPages) uaPage = 0;
      const start = uaPage * UA_PAGE_SIZE;
      const slice = filtered.slice(start, start + UA_PAGE_SIZE);

      uaCount.textContent = `显示 ${filtered.length} / ${units.length} 条单位记录（第 ${uaPage + 1}/${totalPages} 页）`;
      uaBody.innerHTML = slice.map((u) => {
        const pwrCell = u.domain === "land" ? `${u.combat_power}` : `${u.cannons}炮 / ${u.hull}体`;
        const fireW = u.domain === "land" ? `${u.power_per_width}` : `${u.cannons_per_width} 炮/宽`;
        const initSpd = u.domain === "land" ? `主${u.initiative} / 速${u.move_speed}` : `航速 ${u.move_speed}`;
        let diffSummary = "标准编制";
        if (u.is_template) diffSummary = "底层时代模板（供兵种继承）";
        else if (u.is_unique) {
          const ds = (u.deltas || []).slice(0, 4).map((d) => `${d.stat} ${d.diff}`).join("、");
          diffSummary = `特色单位（vs ${u.base_zh || "标准"}：${ds || "同面板专属渠道"}）`;
        }
        return `<tr class="${focusAllId === u.id ? "row-focused" : ""}" data-ua-id="${esc(u.id)}">
          <td><a class="ent-link" href="#${esc(u.id)}"><strong>${esc(u.zh)}</strong></a><br><small style="color:var(--ink-muted)">${esc(u.en)} <code>${esc(u.id)}</code></small></td>
          <td><small>${esc(u.age_zh)}</small></td>
          <td><span class="scope-tag">${esc(u.cat_zh)}</span> <small>${esc(u.unit_type)}</small></td>
          <td><span class="num">${u.troops || "—"}</span></td>
          <td><span class="num">${esc(pwrCell)}</span></td>
          <td><span class="num">${u.frontage}</span></td>
          <td><span class="num"><strong>${esc(fireW)}</strong></span></td>
          <td><span class="num">${esc(initSpd)}</span></td>
          <td><small>${linkifyEntitiesHtml(diffSummary, u.zh)}</small></td>
        </tr>`;
      }).join("");

      if (shouldScroll && focusAllId) {
        const row = uaBody.querySelector(`tr[data-ua-id="${CSS.escape ? CSS.escape(focusAllId) : focusAllId}"]`);
        if (row) setTimeout(() => row.scrollIntoView({ behavior: "smooth", block: "center" }), 60);
      }

      uaPager.hidden = totalPages <= 1;
      uaPager.innerHTML = `
        <span style="font-size:12.5px;color:var(--ink-muted)">第 ${start + 1}–${Math.min(filtered.length, start + UA_PAGE_SIZE)} 条 / 共 ${filtered.length} 条</span>
        <div style="display:flex;gap:8px;align-items:center">
          <button type="button" class="btn-pill" id="ua-prev" ${uaPage === 0 ? "disabled" : ""}>← 上一页</button>
          <span style="font-size:12.5px">第 ${uaPage + 1} / ${totalPages} 页</span>
          <button type="button" class="btn-pill" id="ua-next" ${uaPage >= totalPages - 1 ? "disabled" : ""}>下一页 →</button>
        </div>
      `;
      document.getElementById("ua-prev")?.addEventListener("click", () => { uaPage = Math.max(0, uaPage - 1); renderAllUnits(); });
      document.getElementById("ua-next")?.addEventListener("click", () => { uaPage = Math.min(totalPages - 1, uaPage + 1); renderAllUnits(); });
    }

    uaSearch.addEventListener("input", () => { focusAllId = ""; uaPage = 0; renderAllUnits(); });
    uaHideTpl.addEventListener("change", () => { focusAllId = ""; uaPage = 0; renderAllUnits(); });

    function applyUnitsHash() {
      const h = decodeURIComponent(location.hash.replace("#", "")).trim();
      if (!h || h === "matrix") {
        switchTab("matrix");
        renderMatrix();
        renderUniques(false);
        renderAllUnits(false);
        return;
      }
      if (h === "uniques" || h === "all") {
        switchTab(h);
        renderMatrix();
        renderUniques(false);
        renderAllUnits(false);
        return;
      }
      const target = unitMap[h];
      if (target) {
        if (target.is_unique && !EXTRA_MATRIX_IDS.has(target.id)) {
          switchTab("uniques");
          uuAge.value = "all";
          uuCat.value = "all";
          uuRole.value = "all";
          uuSearch.value = "";
          focusUniqueId = target.id;
          renderMatrix();
          renderUniques(true);
          renderAllUnits(false);
        } else if (!target.is_template) {
          switchTab("matrix");
          curRole = target.domain === "navy" ? "navy" : (target.is_levy ? "land_levy" : "land_reg");
          selectedMatrixId = target.id;
          renderMatrix();
          renderUniques(false);
          renderAllUnits(false);
          if (matrixDetailEl) setTimeout(() => matrixDetailEl.scrollIntoView({ behavior: "smooth", block: "center" }), 60);
        } else {
          switchTab("all");
          uaHideTpl.checked = false;
          uaSearch.value = "";
          focusAllId = target.id;
          renderMatrix();
          renderUniques(false);
          renderAllUnits(true);
        }
      } else {
        renderMatrix();
        renderUniques(false);
        renderAllUnits(false);
      }
    }

    window.addEventListener("hashchange", applyUnitsHash);
    applyUnitsHash();
  }
})();
