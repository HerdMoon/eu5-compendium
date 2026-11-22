(() => {
  "use strict";

  // 1. Theme persistence
  const root = document.documentElement;
  const savedTheme = localStorage.getItem("eu5_compendium_theme");
  if (savedTheme === "dark") root.setAttribute("data-theme", "dark");

  function syncThemeLabel() {
    const isDark = root.getAttribute("data-theme") === "dark";
    document.querySelectorAll("[data-theme-toggle]").forEach((btn) => {
      btn.textContent = isDark ? "☀ 羊皮纸模式" : "☾ 深海图模式";
    });
  }

  document.addEventListener("DOMContentLoaded", () => {
    syncThemeLabel();

    document.querySelectorAll("[data-theme-toggle]").forEach((btn) => {
      btn.addEventListener("click", () => {
        const next = root.getAttribute("data-theme") === "dark" ? "light" : "dark";
        if (next === "dark") root.setAttribute("data-theme", "dark");
        else root.removeAttribute("data-theme");
        localStorage.setItem("eu5_compendium_theme", next);
        syncThemeLabel();
      });
    });

    // 2. Mobile drawer toggle
    const sidebar = document.querySelector(".sidebar");
    document.querySelectorAll("[data-nav-toggle]").forEach((btn) => {
      btn.addEventListener("click", () => {
        if (sidebar) sidebar.classList.toggle("open");
      });
    });
    document.addEventListener("click", (e) => {
      if (sidebar && sidebar.classList.contains("open")) {
        if (!sidebar.contains(e.target) && !e.target.closest("[data-nav-toggle]")) {
          sidebar.classList.remove("open");
        }
      }
    });

    // 3. SVG clickable node jump
    document.querySelectorAll("[data-jump]").forEach((el) => {
      el.addEventListener("click", () => {
        const target = el.getAttribute("data-jump");
        if (!target) return;
        const node = document.querySelector(target);
        if (node) {
          node.scrollIntoView({ behavior: "smooth", block: "start" });
          history.replaceState(null, "", target);
        }
      });
    });

    // 4. Right TOC ScrollSpy
    const tocLinks = Array.from(document.querySelectorAll(".toc-list a"));
    if (tocLinks.length > 0 && "IntersectionObserver" in window) {
      const sections = tocLinks
        .map((a) => document.querySelector(a.getAttribute("href")))
        .filter(Boolean);
      const obs = new IntersectionObserver(
        (entries) => {
          entries.forEach((ent) => {
            if (ent.isIntersecting) {
              const id = "#" + ent.target.id;
              tocLinks.forEach((l) => l.classList.toggle("active", l.getAttribute("href") === id));
            }
          });
        },
        { rootMargin: "-15% 0px -70% 0px", threshold: 0.01 }
      );
      sections.forEach((sec) => obs.observe(sec));
    }

    // 5. Concept Hover / Click Popover
    let activePopover = null;
    function closePopover() {
      if (activePopover) {
        activePopover.remove();
        activePopover = null;
      }
    }
    function openPopover(btn) {
      closePopover();
      const cid = btn.getAttribute("data-concept");
      const glossary = window.__EU5_GLOSSARY__ || [];
      const item = glossary.find((g) => g.id === cid);
      if (!item) return;

      const pop = document.createElement("div");
      pop.className = "term-popover";
      pop.innerHTML = `
        <div class="term-popover-head">
          <strong>${escapeHtml(item.zh)}</strong>
          <small>${escapeHtml(item.en)}</small>
        </div>
        <div>${escapeHtml(item.desc.slice(0, 260))}${item.desc.length > 260 ? "…" : ""}</div>
        <div class="term-popover-foot">
          <a href="glossary.html#${encodeURIComponent(item.id)}">查看完整词条 →</a>
          <button type="button" class="btn-pill" style="padding:2px 8px;font-size:11px" data-close-pop>关闭</button>
        </div>
      `;
      document.body.appendChild(pop);
      const r = btn.getBoundingClientRect();
      const pw = pop.offsetWidth;
      const ph = pop.offsetHeight;
      let left = Math.min(Math.max(12, r.left), window.innerWidth - pw - 12);
      let top = r.bottom + 8;
      if (top + ph > window.innerHeight - 12) top = Math.max(12, r.top - ph - 8);
      pop.style.left = left + "px";
      pop.style.top = top + "px";
      pop.querySelector("[data-close-pop]").addEventListener("click", closePopover);
      activePopover = pop;
    }

    document.addEventListener("click", (e) => {
      const termBtn = e.target.closest(".term[data-concept]");
      if (termBtn) {
        e.stopPropagation();
        openPopover(termBtn);
        return;
      }
      if (activePopover && !activePopover.contains(e.target)) closePopover();
    });

    // 6. Global Command Palette (Ctrl+K / /)
    const modal = document.getElementById("cmd-modal");
    const input = document.getElementById("cmd-input");
    const resultsEl = document.getElementById("cmd-results");
    let selectedIdx = 0;

    function openCmd() {
      if (!modal) return;
      modal.classList.add("open");
      input.value = "";
      renderCmdResults("");
      setTimeout(() => input.focus(), 20);
    }
    function closeCmd() {
      if (modal) modal.classList.remove("open");
    }

    document.querySelectorAll("[data-open-search]").forEach((b) => {
      b.addEventListener("click", openCmd);
    });
    if (modal) {
      modal.addEventListener("click", (e) => {
        if (e.target === modal) closeCmd();
      });
    }

    document.addEventListener("keydown", (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        openCmd();
      } else if (e.key === "/" && !["INPUT", "TEXTAREA", "SELECT"].includes(document.activeElement?.tagName)) {
        e.preventDefault();
        openCmd();
      } else if (e.key === "Escape") {
        closeCmd();
        closePopover();
      }
    });

    function renderCmdResults(qRaw) {
      if (!resultsEl) return;
      const items = window.__EU5_SEARCH__ || [];
      const q = qRaw.trim().toLowerCase();
      let hits;
      if (!q) {
        hits = items.slice(0, 14);
      } else {
        const terms = q.split(/\s+/);
        hits = items
          .map((it) => {
            const hay = (it.title + " " + (it.sub || "") + " " + (it.kw || "")).toLowerCase();
            const ok = terms.every((t) => hay.includes(t));
            if (!ok) return null;
            let score = 0;
            if (it.title.toLowerCase().startsWith(q)) score += 30;
            if (it.title.toLowerCase().includes(q)) score += 15;
            if (it.kind === "章节" || it.kind === "核心星图") score += 10;
            if (it.kind === "红线常数") score += 8;
            return { it, score };
          })
          .filter(Boolean)
          .sort((a, b) => b.score - a.score)
          .slice(0, 24)
          .map((x) => x.it);
      }
      selectedIdx = 0;
      if (!hits.length) {
        resultsEl.innerHTML = `<div style="padding:18px;text-align:center;color:var(--ink-muted)">未找到匹配项 —— 可尝试输入「核心」「阶层」「粮仓」「90%」「Core」「Estates」等关键词</div>`;
        return;
      }
      resultsEl.innerHTML = hits
        .map(
          (it, idx) => `
          <a href="${escapeHtml(it.href)}" class="cmd-item${idx === 0 ? " selected" : ""}">
            <div class="cmd-item-top">
              <span>${escapeHtml(it.title)}</span>
              <span class="cmd-type">${escapeHtml(it.kind)}</span>
            </div>
            <div class="cmd-item-sub">${escapeHtml(it.sub || "")}</div>
          </a>`
        )
        .join("");
      resultsEl.querySelectorAll(".cmd-item").forEach((a) => {
        a.addEventListener("click", closeCmd);
      });
    }

    if (input) {
      input.addEventListener("input", () => renderCmdResults(input.value));
      input.addEventListener("keydown", (e) => {
        const links = Array.from(resultsEl.querySelectorAll(".cmd-item"));
        if (!links.length) return;
        if (e.key === "ArrowDown") {
          e.preventDefault();
          selectedIdx = (selectedIdx + 1) % links.length;
        } else if (e.key === "ArrowUp") {
          e.preventDefault();
          selectedIdx = (selectedIdx - 1 + links.length) % links.length;
        } else if (e.key === "Enter") {
          e.preventDefault();
          links[selectedIdx]?.click();
          return;
        }
        links.forEach((l, i) => l.classList.toggle("selected", i === selectedIdx));
        links[selectedIdx]?.scrollIntoView({ block: "nearest" });
      });
    }
  });

  window.eu5EscapeHtml = escapeHtml;
  function escapeHtml(str) {
    return String(str ?? "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }
})();
