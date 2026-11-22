(() => {
  "use strict";
  const esc = (s) => (window.eu5EscapeHtml ? window.eu5EscapeHtml(s) : String(s ?? ""));

  document.addEventListener("DOMContentLoaded", () => {
    const page = document.body.getAttribute("data-page");
    if (page === "map") initMapExplorer();
    else if (page === "lab") initLabPage();
    else if (page === "ledgers") initLedgersPage();
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

    bundle.edges.forEach(([u, v, lbl], idx) => {
      const a = nodeMap[u], b = nodeMap[v];
      if (!a || !b) return;
      const dx = b.x - a.x, dy = b.y - a.y;
      const mx = (a.x + b.x) / 2, my = (a.y + b.y) / 2;
      // Offset curve gently for non-adjacent edges to reduce crossings
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
        const id = el.getAttribute("data-id");
        el.classList.toggle("dimmed", !activeSet.has(id));
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
          <div style="font-size:12px;font-weight:700;color:#b52b3b;margin-bottom:4px">下游它影响谁（${downs.length} 项）</div>
          <div style="display:flex;flex-wrap:wrap;gap:6px;margin-bottom:14px">
            ${downs.length ? downs.map((x) => `<button type="button" class="btn-pill" data-jump-node="${x.node.id}" title="${esc(x.lbl)}">${esc(x.node.zh)} · <small>${esc(x.lbl)}</small></button>`).join("") : '<span style="font-size:12px;color:var(--ink-muted)">终端成果指标</span>'}
          </div>
        </div>
        <div style="display:flex;gap:8px;flex-wrap:wrap">
          <a href="${esc(n.href)}" class="btn-pill" style="background:var(--accent-2);color:#fff;border-color:var(--accent-2)">进入章节精讲 →</a>
          <button type="button" class="btn-pill" id="map-reset-btn">重置全景视图</button>
        </div>
      `;
      detailEl.querySelectorAll("[data-jump-node]").forEach((b) => {
        b.addEventListener("click", () => selectNode(b.getAttribute("data-jump-node")));
      });
      document.getElementById("map-reset-btn")?.addEventListener("click", resetMap);
      history.replaceState(null, "", "#" + nid);
    }

    function resetMap() {
      svg.querySelectorAll(".map-node,.map-edge").forEach((el) => el.classList.remove("dimmed", "active-in", "active-out"));
      detailEl.innerHTML = `<h3>全景交互星图指南</h3><p style="font-size:13.5px;color:var(--ink-muted)">点击左侧任意 <strong>36 个核心概念节点</strong>，即可实时高亮它的所有直接上游原因（绿线）与直接下游影响（红线），并显示精确公式与红线。</p>`;
    }

    svg.querySelectorAll(".map-node").forEach((el) => {
      el.addEventListener("click", () => selectNode(el.getAttribute("data-id")));
    });

    if (pillarFilter) {
      pillarFilter.addEventListener("change", () => {
        const val = pillarFilter.value;
        if (val === "all") { resetMap(); return; }
        svg.querySelectorAll(".map-node").forEach((el) => {
          el.classList.toggle("dimmed", el.getAttribute("data-pillar") !== val);
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

    // Render 37 Redlines
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

    // Render 16 Troubleshooting cards
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

    // Calc 1: Wealth -> Control -> Tax Base vs Uncontrolled Estate Funnel
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
        <div>国库月实收税款：<strong>${treasury.toFixed(2)}</strong> &nbsp;|&nbsp; 流入阶层金库总额（未控+免税）：<strong>${estateKeep.toFixed(2)}</strong>（其中未受控漏水 ${uncontrolled.toFixed(2)}）</div>
        <div class="bar-split"><div class="bar-treasury" style="width:${tPct.toFixed(1)}%"></div><div class="bar-estate" style="width:${(100 - tPct).toFixed(1)}%"></div></div>
      `;
    }
    ["c1-prox", "c1-integ", "c1-extra", "c1-wealth", "c1-access", "c1-tax"].forEach((id) => {
      document.getElementById(id)?.addEventListener("input", updC1);
    });
    if (document.getElementById("c1-prox")) updC1();

    // Calc 2: Rebel Fort Loyalty Roll (00_defines REBEL_FORT_LOYALTY_*)
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

    // Calc 3: Subject Strength Bloc & Alliance Bloc Saturation
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

    // Calc 4: Daily Initiative Engage Chance & Combined Arms
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

  // 3. 10 Data Ledgers Page (ledgers.html)
  function initLedgersPage() {
    const ld = window.__EU5_LEDGERS__;
    if (!ld) return;
    const tabsEl = document.getElementById("ledger-tabs");
    const qEl = document.getElementById("ledger-search");
    const subFilterEl = document.getElementById("ledger-subfilter");
    const countEl = document.getElementById("ledger-count");
    const headEl = document.getElementById("ledger-thead");
    const bodyEl = document.getElementById("ledger-tbody");

    const CONFIGS = [
      {
        id: "goods", label: "75 种商品数值表", filterKey: "group",
        cols: [
          ["商品", (r) => `<div class="good-cell">${r.icon ? `<img class="good-icon" src="${esc(r.icon)}" alt="" loading="lazy">` : ""}<div><strong>${esc(r.zh)}</strong><br><small style="color:var(--ink-muted)">${esc(r.en)}</small></div></div>`],
          ["分类 / 产法", (r) => `${esc(r.group)}<br><small>${esc(r.method)}</small>`],
          ["基准市价", (r) => `<span class="num">${r.price}</span>`],
          ["食物值", (r) => r.food > 0 ? `<span class="num pos">${r.food}</span>` : '<span class="num" style="color:var(--ink-muted)">—</span>'],
          ["运输系数", (r) => `<span class="num">${r.transport}</span>`],
          ["基础月产", (r) => `<span class="num">${r.base}</span>`],
        ],
      },
      {
        id: "societal_values", label: "17 对社会价值观", filterKey: "category",
        cols: [
          ["轴线名称", (r) => `<strong>${esc(r.zh)}</strong><br><small>${esc(r.en)}</small>`],
          ["分类 / 时代", (r) => `${esc(r.category)}<br><small>${esc(r.era)}</small>`],
          ["左端极点 (−100) 满额效应", (r) => `<strong>${esc(r.left_pole)}：</strong>${esc(r.left_effects)}`],
          ["右端极点 (+100) 满额效应", (r) => `<strong>${esc(r.right_pole)}：</strong>${esc(r.right_effects)}`],
        ],
      },
      {
        id: "estate_actions", label: "12 项阶层互动与绝境求助", filterKey: "kind",
        cols: [
          ["互动名称", (r) => `<strong>${esc(r.zh)}</strong><br><small>${esc(r.en)} (${esc(r.id)})</small>`],
          ["类别", (r) => esc(r.kind)],
          ["适用目标与条件", (r) => esc(r.target)],
          ["耗费与惩罚代价", (r) => esc(r.cost)],
          ["实际收益与冷却", (r) => `${esc(r.effect)}<br><small style="color:var(--ink-muted)">冷却：${esc(r.cooldown)}</small>`],
        ],
      },
      {
        id: "cabinet_actions", label: "81 项内阁行动", filterKey: "ability",
        cols: [
          ["行动名称", (r) => `<strong>${esc(r.zh)}</strong><br><small>${esc(r.en)}</small>`],
          ["系别 / 资格", (r) => `<span class="cmd-type">${esc(r.ability)}</span> ${esc(r.scope)}`],
          ["作用对象", (r) => esc(r.target)],
          ["核心效果与前置条件", (r) => `${esc(r.effect)}${r.conditions ? `<br><small style="color:var(--ink-muted)">${esc(r.conditions)}</small>` : ""}`],
        ],
      },
      {
        id: "character_interactions", label: "34 项角色互动", filterKey: "scope",
        cols: [
          ["互动名称", (r) => `<strong>${esc(r.zh)}</strong><br><small>${esc(r.en)}</small>`],
          ["适用资格", (r) => esc(r.scope)],
          ["详细机制、花费与效果", (r) => `${esc(r.detail)}${r.conditions ? `<br><small style="color:var(--ink-muted)">${esc(r.conditions)}</small>` : ""}`],
        ],
      },
      {
        id: "subject_types", label: "22 种属国类型", filterKey: "can_annex",
        cols: [
          ["属国名称", (r) => `<strong>${esc(r.zh)}</strong><br><small>${esc(r.en)} (${esc(r.id)})</small>`],
          ["层级 / 同君", (r) => `等级 ${esc(r.level)} · 同君：${esc(r.same_ruler)}`],
          ["贡赋机制", (r) => esc(r.subject_pays)],
          ["外交容倍率", (r) => `<span class="num">${esc(r.diplo_cost_scale)}</span>`],
          ["吞并规则（速/年/好感）", (r) => `${esc(r.can_annex)}（速 ${esc(r.annex_speed)} / 最少 ${esc(r.annex_min_years)} 年 / 好感 ${esc(r.annex_min_opinion)}）`],
        ],
      },
      {
        id: "bureaucracies", label: "60 项官僚部门", filterKey: "scope",
        cols: [
          ["部门名称", (r) => `<strong>${esc(r.zh)}</strong><br><small>${esc(r.en)}</small>`],
          ["资格", (r) => esc(r.scope)],
          ["常驻 / 满维正面 / 缺维负面修正", (r) => `${esc(r.detail)}${r.conditions ? `<br><small style="color:var(--ink-muted)">${esc(r.conditions)}</small>` : ""}`],
        ],
      },
      {
        id: "town_rights", label: "75 项城镇特权", filterKey: "scope",
        cols: [
          ["特权名称", (r) => `<strong>${esc(r.zh)}</strong><br><small>${esc(r.en)}</small>`],
          ["适用范围", (r) => esc(r.scope)],
          ["地点修正与冲突互斥规则", (r) => esc(r.detail)],
        ],
      },
      {
        id: "casus_belli", label: "113 种宣战理由", filterKey: "scope",
        cols: [
          ["宣战理由", (r) => `<strong>${esc(r.zh)}</strong><br><small>${esc(r.en)}</small>`],
          ["范围", (r) => esc(r.scope)],
          ["战争目标与核心条件", (r) => esc(r.detail)],
        ],
      },
      {
        id: "situations_disasters", label: "24 局势 & 38 灾难", filterKey: "kind",
        cols: [
          ["事件 / 进程", (r) => `<strong>${esc(r.zh)}</strong><br><small>${esc(r.en)}</small>`],
          ["类型 / 范围", (r) => `<span class="cmd-type">${esc(r.kind)}</span> ${esc(r.scope)}`],
          ["触发概率、惩罚修正与机制说明", (r) => esc(r.detail)],
        ],
      },
    ];

    let curId = "goods";
    function getRows(id) {
      if (id === "situations_disasters") return [...ld.situations, ...ld.disasters];
      return ld[id] || [];
    }

    function buildSubFilter(cfg, rows) {
      const fk = cfg.filterKey;
      const vals = Array.from(new Set(rows.map((r) => r[fk]).filter(Boolean)));
      subFilterEl.innerHTML = `<option value="all">全部类别 (${rows.length})</option>` +
        vals.map((v) => `<option value="${esc(v)}">${esc(v)}</option>`).join("");
    }

    function render() {
      const cfg = CONFIGS.find((c) => c.id === curId) || CONFIGS[0];
      const rows = getRows(cfg.id);
      const q = (qEl.value || "").trim().toLowerCase();
      const fv = subFilterEl.value;
      const fk = cfg.filterKey;

      const filtered = rows.filter((r) => {
        if (fv !== "all" && r[fk] !== fv) return false;
        if (!q) return true;
        return JSON.stringify(r).toLowerCase().includes(q);
      });

      countEl.textContent = `显示 ${filtered.length} / ${rows.length} 条`;
      headEl.innerHTML = `<tr>${cfg.cols.map(([h]) => `<th>${esc(h)}</th>`).join("")}</tr>`;
      bodyEl.innerHTML = filtered.slice(0, 300).map((r) => `<tr>${cfg.cols.map(([, fn]) => `<td>${fn(r)}</td>`).join("")}</tr>`).join("");
      if (filtered.length > 300) {
        bodyEl.innerHTML += `<tr><td colspan="${cfg.cols.length}" style="text-align:center;color:var(--ink-muted)">仅显示前 300 条，请输入关键词进一步精确过滤…</td></tr>`;
      }
    }

    function selectLedger(id) {
      curId = CONFIGS.some((c) => c.id === id) ? id : "goods";
      tabsEl.querySelectorAll(".tab-btn").forEach((b) => b.classList.toggle("active", b.getAttribute("data-id") === curId));
      const cfg = CONFIGS.find((c) => c.id === curId);
      buildSubFilter(cfg, getRows(curId));
      render();
      history.replaceState(null, "", "#" + curId);
    }

    tabsEl.innerHTML = CONFIGS.map((c) => `<button type="button" class="tab-btn" data-id="${c.id}">${esc(c.label)}</button>`).join("");
    tabsEl.querySelectorAll(".tab-btn").forEach((b) => b.addEventListener("click", () => selectLedger(b.getAttribute("data-id"))));
    qEl.addEventListener("input", render);
    subFilterEl.addEventListener("change", render);

    const initHash = location.hash.replace("#", "");
    selectLedger(initHash || "goods");
  }

  // 4. 741-Entry Bilingual Encyclopedia Glossary (glossary.html)
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

      let filtered = items.filter((g) => {
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

    // If linked via #concept_id and current slice skips it, pre-filter or ensure it renders!
    const h = decodeURIComponent(location.hash.replace("#", ""));
    if (h && items.some((x) => x.id === h)) {
      const target = items.find((x) => x.id === h);
      if (target) qEl.value = target.zh;
    }
    render();
  }
})();
