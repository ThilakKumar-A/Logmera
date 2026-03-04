document.addEventListener('DOMContentLoaded', function() {
  const requiredElements = ['search', 'projectFilter', 'modelFilter', 'status', 'fromDate', 'toDate', 'clearFilters', 'refreshData', 'logsBody', 'emptyState', 'totalCount', 'filteredCount', 'avgLatency'];
  const missingElements = requiredElements.filter(id => !document.getElementById(id));
  
  if (missingElements.length > 0) {
    return;
  }

  bindEvents();
  fetchLogs();
});

const state = {
  logs: [],
  filtered: [],
};

const els = {
  search: document.getElementById("search"),
  project: document.getElementById("projectFilter"),
  model: document.getElementById("modelFilter"),
  status: document.getElementById("status"),
  fromDate: document.getElementById("fromDate"),
  toDate: document.getElementById("toDate"),
  clearBtn: document.getElementById("clearFilters"),
  refreshBtn: document.getElementById("refreshData"),
  body: document.getElementById("logsBody"),
  empty: document.getElementById("emptyState"),
  totalCount: document.getElementById("totalCount"),
  filteredCount: document.getElementById("filteredCount"),
  avgLatency: document.getElementById("avgLatency"),
};

function toDateOnly(value) {
  if (!value) return "";
  const d = new Date(value);
  if (Number.isNaN(d.getTime())) return "";
  return d.toISOString().slice(0, 10);
}

function escapeHtml(text) {
  return String(text ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;");
}

function matchesFilters(log) {
  const search = els.search.value.trim().toLowerCase();
  const project = els.project.value.trim().toLowerCase();
  const model = els.model.value.trim().toLowerCase();
  const status = els.status.value.trim().toLowerCase();
  const fromDate = els.fromDate.value;
  const toDate = els.toDate.value;

  const combined = [log.prompt, log.response, log.model, log.project_id].join(" ").toLowerCase();

  if (search && !combined.includes(search)) return false;
  if (project && !log.project_id.toLowerCase().includes(project)) return false;
  if (model && !log.model.toLowerCase().includes(model)) return false;
  if (status && String(log.status ?? "").toLowerCase() !== status) return false;

  const createdDate = toDateOnly(log.created_at);
  if (fromDate && createdDate < fromDate) return false;
  if (toDate && createdDate > toDate) return false;

  return true;
}

function renderSummary() {
  els.totalCount.textContent = state.logs.length;
  els.filteredCount.textContent = state.filtered.length;

  const latencyValues = state.filtered
    .map((item) => item.latency_ms)
    .filter((v) => Number.isFinite(v));

  if (latencyValues.length === 0) {
    els.avgLatency.textContent = "0";
    return;
  }

  const avg = latencyValues.reduce((sum, value) => sum + value, 0) / latencyValues.length;
  els.avgLatency.textContent = Math.round(avg).toString();
}

function renderRows() {
  if (state.filtered.length === 0) {
    els.body.innerHTML = "";
    els.empty.classList.remove("hidden");
    renderSummary();
    return;
  }

  els.empty.classList.add("hidden");
  const rows = state.filtered
    .map((log) => {
      const created = new Date(log.created_at).toLocaleString();
      return `
        <tr>
          <td>${escapeHtml(created)}</td>
          <td>${escapeHtml(log.project_id)}</td>
          <td>${escapeHtml(log.model)}</td>
          <td>${escapeHtml(log.status ?? "-")}</td>
          <td>${escapeHtml(log.latency_ms ?? "-")}</td>
          <td>${escapeHtml(log.prompt)}</td>
          <td>${escapeHtml(log.response)}</td>
        </tr>
      `;
    })
    .join("");

  els.body.innerHTML = rows;
  renderSummary();
}

function applyFilters() {
  state.filtered = state.logs.filter(matchesFilters);
  renderRows();
}

function populateStatusOptions() {
  const statuses = new Set();
  state.logs.forEach((item) => {
    if (item.status) statuses.add(item.status);
  });

  const current = els.status.value;
  els.status.innerHTML = '<option value="">All status</option>';

  Array.from(statuses)
    .sort((a, b) => a.localeCompare(b))
    .forEach((item) => {
      const option = document.createElement("option");
      option.value = item;
      option.textContent = item;
      els.status.appendChild(option);
    });

  if (current) {
    els.status.value = current;
  }
}

async function fetchLogs() {
  els.refreshBtn.disabled = true;
  els.refreshBtn.textContent = "Loading...";

  try {
    const response = await fetch("/logs", { headers: { Accept: "application/json" } });
    if (!response.ok) {
      throw new Error(`Failed to fetch logs (${response.status})`);
    }

    const data = await response.json();
    state.logs = Array.isArray(data) ? data : [];
    populateStatusOptions();
    applyFilters();
  } catch (error) {
    console.error("Error fetching logs:", error);
    els.body.innerHTML = `<tr><td colspan="7">${escapeHtml(error.message)}</td></tr>`;
    els.empty.classList.add("hidden");
    state.logs = [];
    state.filtered = [];
    renderSummary();
  } finally {
    els.refreshBtn.disabled = false;
    els.refreshBtn.textContent = "Refresh";
  }
}

function clearFilters() {
  els.search.value = "";
  els.project.value = "";
  els.model.value = "";
  els.status.value = "";
  els.fromDate.value = "";
  els.toDate.value = "";
  applyFilters();
}

function bindEvents() {
  [els.search, els.project, els.model, els.status, els.fromDate, els.toDate].forEach((el) => {
    el.addEventListener("input", applyFilters);
    el.addEventListener("change", applyFilters);
  });

  els.clearBtn.addEventListener("click", clearFilters);
  els.refreshBtn.addEventListener("click", fetchLogs);
}

bindEvents();
fetchLogs();
