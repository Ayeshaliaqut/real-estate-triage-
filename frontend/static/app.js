document.addEventListener("DOMContentLoaded", () => {
  // Buttons
  const processBtn = document.getElementById("processBtn");
  const processBtnTop = document.getElementById("processBtnTop");

  const pathInput = document.getElementById("pathInput");

  const searchInput = document.getElementById("searchInput");
  const tierFilter = document.getElementById("tierFilter");

  const leadsBody = document.getElementById("leadsBody");
  const summaryList = document.getElementById("summaryList");
  const leadsCount = document.getElementById("leadsCount");
  const lastRun = document.getElementById("lastRun");
  const detailModal = document.getElementById("detailModal");
  const leadJson = document.getElementById("leadJson");
  const closeModalTop = document.getElementById("closeModalTop");

  const chartCanvas = document.getElementById("hotChart");
  const chartEmpty = document.getElementById("chartEmpty");

  let hotChart = null;
  let currentLeads = [];

  //button click handelers
  processBtn.addEventListener("click", () => loadAndProcess());
  processBtnTop.addEventListener("click", () => loadAndProcess());

  // LOAD & PROCESS FUNCTION
  async function loadAndProcess() {
    disableButtons(true);

    const body = new URLSearchParams();
    const path = pathInput.value.trim();
    if (path) body.append("path", path);

    try {
      const resp = await fetch("/api/load_and_process", {
        method: "POST",
        body: body
      });

      const info = await resp.json();

      // fetch processed leads
      const leadsResp = await fetch("/api/leads");
      const leadsData = await leadsResp.json();
      currentLeads = leadsData.leads || [];

      leadsCount.textContent = currentLeads.length;
      lastRun.textContent = `Last run: ${new Date().toLocaleString()}`;

      renderLeads(currentLeads);
      renderReport(info.report || []);

    } catch (err) {
      console.error("Error:", err);
      alert("Failed to load/process. Check backend.");
    }

    disableButtons(false);
  }

  function disableButtons(state) {
    const text = state ? "Processing..." : "Load & Process";
    processBtn.disabled =
    processBtnTop.disabled = state;
    processBtn.textContent =
    processBtnTop.textContent = text;
  }

  // FILTER + SEARCH
  searchInput.addEventListener("input", applyFilters);
  tierFilter.addEventListener("change", applyFilters);

  function applyFilters() {
    const q = searchInput.value.trim().toLowerCase();
    const tier = tierFilter.value;
    let filtered = currentLeads.slice();

    if (tier !== "all") {
      filtered = filtered.filter(l => (l.tier || "").toLowerCase() === tier);
    }
    if (q) {
      filtered = filtered.filter(l => {
        const hay = `${l.name||""} ${l.message||""} ${l.source||""}`.toLowerCase();
        return hay.includes(q);
      });
    }
    renderLeads(filtered);
  }
  // RENDER LEADS TABLE
  function renderLeads(leads) {
    leadsBody.innerHTML = "";

    if (!leads || leads.length === 0) {
      leadsBody.innerHTML =
        `<tr><td colspan="8" class="text-center py-6 text-slate-500">No leads found</td></tr>`;
      return;
    }

    leads.forEach((l, idx) => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td class="px-4 py-3">${l.name || "—"}</td>
        <td class="px-4 py-3">${l.property_type || "—"}</td>
        <td class="px-4 py-3">${l.budget || "—"}</td>
        <td class="px-4 py-3">${l.tier || "—"}</td>
        <td class="px-4 py-3">${l.qualification_score || 0}</td>
        <td class="px-4 py-3">${l.intent_label || "—"}</td>
        <td class="px-4 py-3">${l.recommended_action || "—"}</td>
        <td class="px-4 py-3">
          <button class="openBtn text-emerald-600 font-semibold" data-idx="${idx}">
            Open
          </button>
        </td>
      `;
      leadsBody.appendChild(tr);
    });

    // wire modal buttons
    document.querySelectorAll(".openBtn").forEach(btn => {
      btn.addEventListener("click", () => {
        const idx = Number(btn.dataset.idx);
        leadJson.textContent = JSON.stringify(currentLeads[idx], null, 2);
        detailModal.classList.remove("hidden");
      });
    });
  }
  // RENDER REPORT + CHART
  function renderReport(report) {
    summaryList.innerHTML = "";

    if (!report || report.length === 0) {
      destroyChart();
      chartEmpty.classList.remove("hidden");
      summaryList.innerHTML = `<div class="text-slate-400">No report data</div>`;
      return;
    }

    // summary rows
    report.forEach(r => {
      summaryList.innerHTML += `
        <div class="flex justify-between text-sm">
          <div>${r.source}</div>
          <div class="text-slate-500">Hot: ${r.hot_count}/${r.total} (${r.hot_pct}%)</div>
        </div>
      `;
    });

    renderChart(report);
  }
  // CHART CODE -fixed
  function destroyChart() {
    if (hotChart) {
      try { hotChart.destroy(); } catch {}
      hotChart = null;
    }
  }

  function renderChart(report) {
    destroyChart();
    chartEmpty.classList.add("hidden");

    const labels = report.map(r => r.source);
    const values = report.map(r => r.hot_count);

    const ctx = chartCanvas.getContext("2d");
    hotChart = new Chart(ctx, {
      type: "bar",
      data: {
        labels,
        datasets: [{
          label: "Hot Leads",
          data: values,
          backgroundColor: "rgba(16,185,129,0.9)",
          borderRadius: 6
        }]
      },
      options: { responsive: true, maintainAspectRatio: false }
    });
  }
  // MODAL CLOSE
  closeModalTop.addEventListener("click", () => {
    detailModal.classList.add("hidden");
  });

});
