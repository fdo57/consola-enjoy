// ---------------------------------------------------------
// Consola de Gestión de Proyectos - Casinos de Chile SpA
// Application Core Logic (State Management & Reactive UI)
// ---------------------------------------------------------

// Column headers matching INSTRUCTIONS.md
const EXCEL_HEADERS = [
  "proyecto_id", "unidad_nombre", "proyecto_nombre", "proyecto_estado", "proyecto_descripcion",
  "tarea_id", "tarea_nombre", "tarea_descripcion", "tarea_responsable",
  "tarea_estado", "tarea_contraparte", "tarea_pct", "tarea_fecha_creacion", "fecha_legacy",
  "con_alerta", "fecha_inicio_proy", "fecha_inicio_real", "fecha_fin_proy", "fecha_fin_real"
];

// Unit abbreviation mapping
const UNIT_ABBR = {
  "Enjoy Rinconada": "RI",
  "Rinconada": "RI",
  "Enjoy Pucón": "PU",
  "Pucón": "PU",
  "Enjoy Viña": "VI",
  "Viña": "VI",
  "Enjoy Coquimbo": "CQ",
  "Coquimbo": "CQ",
  "Enjoy Chiloé": "CH",
  "Chiloé": "CH",
  "Enjoy Transversales": "TR",
  "Transversales": "TR"
};

// ---------------------------------------------------------
// Global Helper Functions (Available to all modules/views)
// ---------------------------------------------------------
function isEmptyDate(val) {
  if (val === null || val === undefined) return true;
  const s = String(val).trim().toLowerCase();
  return s === "" || s === "-" || s === "nan" || s === "null" || s === "undefined";
}

function normalizeEstado(st) {
  if (!st) return "";
  return String(st).toLowerCase().trim();
}

function getUnitAbbr(name) {
  if (!name) return "TR";
  return UNIT_ABBR[name] || name.substring(0, 2).toUpperCase();
}

function toTitleCase(str) {
  if (!str) return "";
  return str.toLowerCase().split(' ').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ');
}

function isProjectActive(status) {
  if (!status) return true;
  const s = String(status).toLowerCase().trim();
  return s !== "terminado" && s !== "eliminado";
}

function isTaskActive(status) {
  if (!status) return true;
  const s = String(status).toLowerCase().trim();
  return s !== "terminada" && s !== "eliminada";
}

function getSemaforoClass(task) {
  if (!task) return "semaforo-green";
  const alerta = (task.con_alerta || "").toLowerCase().trim();
  const estado = (task.tarea_estado || "").toLowerCase().trim();

  if (alerta === "si" || alerta === "sí") {
    return "semaforo-red";
  }
  if (estado === "detenida") {
    return "semaforo-yellow";
  }
  return "semaforo-green";
}

function getTodayStr() {
  const d = new Date();
  const year = d.getFullYear();
  const month = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  return `${day}/${month}/${year}`;
}

function formatDateDDMMYYYY(dateStr) {
  if (!dateStr || String(dateStr).trim() === "" || String(dateStr).trim() === "-") return "-";
  const str = String(dateStr).trim();
  const ddmmyyyyMatch = str.match(/^(\d{1,2})\/(\d{1,2})\/(\d{4})/);
  if (ddmmyyyyMatch) {
    const day = ddmmyyyyMatch[1].padStart(2, '0');
    const month = ddmmyyyyMatch[2].padStart(2, '0');
    const year = ddmmyyyyMatch[3];
    return `${day}/${month}/${year}`;
  }
  const isoMatch = str.match(/^(\d{4})-(\d{1,2})-(\d{1,2})/);
  if (isoMatch) {
    const year = isoMatch[1];
    const month = isoMatch[2].padStart(2, '0');
    const day = isoMatch[3].padStart(2, '0');
    return `${day}/${month}/${year}`;
  }
  const d = new Date(str);
  if (!isNaN(d.getTime())) {
    const day = String(d.getDate()).padStart(2, '0');
    const month = String(d.getMonth() + 1).padStart(2, '0');
    const year = d.getFullYear();
    return `${day}/${month}/${year}`;
  }
  return str;
}

function parseToYYYYMMDD(dateStr) {
  if (!dateStr || String(dateStr).trim() === "" || String(dateStr).trim() === "-") return "";
  const str = String(dateStr).trim();
  const isoMatch = str.match(/^(\d{4})-(\d{1,2})-(\d{1,2})/);
  if (isoMatch) {
    const year = isoMatch[1];
    const month = isoMatch[2].padStart(2, '0');
    const day = isoMatch[3].padStart(2, '0');
    return `${year}-${month}-${day}`;
  }
  const ddmmyyyy = str.match(/^(\d{1,2})\/(\d{1,2})\/(\d{4})/);
  if (ddmmyyyy) {
    const day = ddmmyyyy[1].padStart(2, '0');
    const month = ddmmyyyy[2].padStart(2, '0');
    const year = ddmmyyyy[3];
    return `${year}-${month}-${day}`;
  }
  return "";
}

function parseDateForSort(dateStr) {
  const ymd = parseToYYYYMMDD(dateStr);
  if (ymd) {
    const time = new Date(ymd).getTime();
    if (!isNaN(time)) return time;
  }
  return 0;
}

function sortTasksByCreationDesc(taskList) {
  return taskList.slice().sort((a, b) => {
    const dateA = parseDateForSort(a.tarea_fecha_creacion || a.fecha_inicio_proy || a.fecha_legacy);
    const dateB = parseDateForSort(b.tarea_fecha_creacion || b.fecha_inicio_proy || b.fecha_legacy);
    if (dateB !== dateA) {
      return dateB - dateA;
    }
    return (b.tarea_id || "").localeCompare(a.tarea_id || "");
  });
}

function getMondayTimestamp(dateStr) {
  if (isEmptyDate(dateStr)) return null;
  const s = String(dateStr).trim();

  let year, month, day;
  const isoMatch = s.match(/^(\d{4})-(\d{1,2})-(\d{1,2})/);
  const ddmmyyyyMatch = s.match(/^(\d{1,2})\/(\d{1,2})\/(\d{4})/);

  if (isoMatch) {
    year = parseInt(isoMatch[1], 10);
    month = parseInt(isoMatch[2], 10) - 1;
    day = parseInt(isoMatch[3], 10);
  } else if (ddmmyyyyMatch) {
    day = parseInt(ddmmyyyyMatch[1], 10);
    month = parseInt(ddmmyyyyMatch[2], 10) - 1;
    year = parseInt(ddmmyyyyMatch[3], 10);
  } else {
    const d = new Date(s);
    if (!isNaN(d.getTime())) {
      year = d.getFullYear();
      month = d.getMonth();
      day = d.getDate();
    } else {
      return null;
    }
  }

  if (isNaN(year) || isNaN(month) || isNaN(day)) return null;

  const utcDate = new Date(Date.UTC(year, month, day, 12, 0, 0));
  if (isNaN(utcDate.getTime())) return null;

  const dayOfWeek = utcDate.getUTCDay();
  const diffToMonday = dayOfWeek === 0 ? -6 : 1 - dayOfWeek;

  const mondayDate = new Date(Date.UTC(year, month, day + diffToMonday, 0, 0, 0));
  return mondayDate.toISOString().substring(0, 10);
}

function isSameWeek(dateStr1, dateStr2) {
  if (isEmptyDate(dateStr1) || isEmptyDate(dateStr2)) return false;
  const m1 = getMondayTimestamp(dateStr1);
  const m2 = getMondayTimestamp(dateStr2);
  if (!m1 || !m2) return false;
  return m1 === m2;
}

function setTaskState(taskOrId, newState) {
  const task = typeof taskOrId === "string" ? db.find(t => t.tarea_id === taskOrId) : taskOrId;
  if (!task) return null;

  const oldState = (task.tarea_estado || "").toLowerCase().trim();
  const normalizedNewState = (newState || "").toLowerCase().trim();

  task.tarea_estado = newState;

  const isNewFinished = (normalizedNewState === "terminada" || normalizedNewState === "eliminada");
  const isOldFinished = (oldState === "terminada" || oldState === "eliminada");

  if (isNewFinished) {
    if (isEmptyDate(task.fecha_fin_real)) {
      task.fecha_fin_real = getTodayStr();
    }
  } else if (isOldFinished && !isNewFinished) {
    task.fecha_fin_real = "";
  }

  return task;
}

function normalizeDateStr(val) {
  if (isEmptyDate(val)) return "";
  return parseToYYYYMMDD(val) || String(val).trim();
}

function diagnoseDateConsistency(item) {
  if (!item) return { isConsistent: true, reasons: [] };
  const reasons = [];

  const state = (item.tarea_estado || "").toLowerCase().trim();
  const isActive = (state === "por iniciar" || state === "en desarrollo" || state === "detenida");
  const isFinishedOrDeleted = (state === "terminada" || state === "eliminada");

  const hasFinProy = !isEmptyDate(item.fecha_fin_proy);
  const hasFinReal = !isEmptyDate(item.fecha_fin_real);
  const hasInicioProy = !isEmptyDate(item.fecha_inicio_proy);

  // 1. Tarea activa con fecha_fin_real o fecha_fin_proy informada
  if (isActive && hasFinReal) {
    reasons.push("Tarea activa con fecha de término real informada");
  }
  if (isActive && hasFinProy) {
    reasons.push("Tarea activa con fecha de término proyectada informada");
  }

  // 2. Tareas terminadas o eliminadas sin fecha_fin_real
  if (isFinishedOrDeleted && !hasFinReal) {
    reasons.push("Tarea terminada/eliminada sin fecha de término real");
  }

  // 3. Tareas sin fecha_inicio_proy
  if (!hasInicioProy) {
    reasons.push("Sin fecha de inicio proyectada");
  }

  // 4. Tareas terminadas con porcentaje de avance distinto a 100
  const pctNum = parseInt(item.tarea_pct, 10);
  if (isFinishedOrDeleted && state === "terminada" && !isNaN(pctNum) && pctNum !== 100) {
    reasons.push("Tarea terminada con porcentaje de avance distinto a 100%");
  }

  // 5. Tareas activas con porcentaje de avance igual a 100
  if (isActive && !isNaN(pctNum) && pctNum === 100 && (state === "en desarrollo" || state === "detenida")) {
    reasons.push("Tarea activa con porcentaje de avance igual a 100%");
  }

  return {
    isConsistent: reasons.length === 0,
    reasons: reasons
  };
}

// Global Actions for Table Rows
function completeTask(taskId) {
  const task = db.find(t => t.tarea_id === taskId);
  if (!task) return;
  setTaskState(task, "terminada");
  task.tarea_pct = 100;
  saveDB();
  renderCurrentView();
}

function deleteTask(taskId) {
  const task = db.find(t => t.tarea_id === taskId);
  if (!task) return;
  setTaskState(task, "eliminada");
  saveDB();
  renderCurrentView();
}

// Navigation helpers
function openCreateProjectForm() {
  switchView("crear-proyecto");
}

function createNewProject(uName, pName, pDesc) {
  if (!uName && !pName) {
    openCreateProjectForm();
    return;
  }
}

function createNewTask(optProjectId) {
  if (optProjectId) {
    selectedProjectId = optProjectId;
  }
  switchView("crear-tarea");
}

// SVG Icons permitted by INSTRUCTIONS.md
const ICON_CHECK = `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>`;
const ICON_DELETE = `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/><line x1="10" y1="11" x2="10" y2="17"/><line x1="14" y1="11" x2="14" y2="17"/></svg>`;
const ICON_SAVE = `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/><polyline points="17 21 17 13 7 13 7 21"/><polyline points="7 3 7 8 15 8"/></svg>`;
const ICON_EDIT = `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>`;
const ICON_CALENDAR = `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>`;
const ICON_ALERT_RED = `<span class="semaforo-dot semaforo-red" style="margin-left: 6px; vertical-align: middle;" title="Proyecto con tareas en alerta"></span>`;

function renderDateCell(taskId, fieldName, dateVal) {
  const formattedVal = formatDateDDMMYYYY(dateVal);
  const displayVal = formattedVal !== "" ? formattedVal : "-";
  const isoVal = parseToYYYYMMDD(dateVal);
  return `
    <div class="date-cell-container">
      <span class="date-text-val">${displayVal}</span>
      <div class="date-picker-btn-wrapper">
        <button type="button" class="date-picker-btn" title="Modificar fecha">${ICON_CALENDAR}</button>
        <input type="date" class="date-picker-hidden-input" value="${isoVal}" onchange="updateTaskDate('${taskId}', '${fieldName}', this.value)">
      </div>
    </div>
  `;
}

// Data State
let db = [];
let currentView = "dashboard";
let selectedUnit = "Enjoy Rinconada";
let selectedProjectId = "";
let selectedTaskId = "";
let isEditingTarea = false;
let fechaInforme = new Date().toISOString().split('T')[0];

let isStreamlitConnected = false;
let dashSelectedProjectId = "";

// Streamlit Custom Component Communication Bridge
function sendToStreamlit(action, data, context) {
  const payload = {
    action: action,
    data: data,
    context: context || null,
    _ts: Date.now()
  };

  const taskInfo = context && context.created_task_id ? context.created_task_id : (context && context.deleted_task_id ? context.deleted_task_id : "N/A");
  console.log(`[PUENTE_STREAMLIT] 3. Despachando mensaje '${action}' a Streamlit | Filas: ${data ? data.length : 0} | Tarea ID: ${taskInfo}`);

  try {
    if (window.Streamlit && typeof window.Streamlit.setComponentValue === "function") {
      window.Streamlit.setComponentValue(payload);
    } else {
      window.parent.postMessage({
        isStreamlitMessage: true,
        type: "streamlit:setComponentValue",
        value: payload
      }, "*");
    }
  } catch (e) {
    console.warn("[PUENTE_STREAMLIT] sendToStreamlit postMessage falló:", e);
  }
}

function notifyStreamlitReady() {
  try {
    window.parent.postMessage({
      isStreamlitMessage: true,
      type: "streamlit:componentReady",
      apiVersion: 1
    }, "*");

    const contentHeight = Math.max(document.documentElement.scrollHeight, document.body.scrollHeight, 1000);
    window.parent.postMessage({
      isStreamlitMessage: true,
      type: "streamlit:setFrameHeight",
      height: contentHeight
    }, "*");
  } catch (e) {}
}

function showSaveToast(isSuccess, optMsg) {
  const toast = document.getElementById("save-toast");
  if (!toast) return;
  toast.className = "save-toast-banner " + (isSuccess ? "save-toast-success" : "save-toast-error");
  toast.textContent = optMsg || (isSuccess ? "Guardado" : "Error: no se pudo guardar");
  toast.style.display = "block";
  toast.style.opacity = "1";

  if (window._saveToastTimer) clearTimeout(window._saveToastTimer);
  window._saveToastTimer = setTimeout(() => {
    toast.style.opacity = "0";
    setTimeout(() => {
      toast.style.display = "none";
    }, 300);
  }, 2500);
}

function renderStatusBanner() {
  const banner = document.getElementById("db-status-banner");
  if (!banner) return;

  const statusObj = window.DB_STATUS || {};
  const status = statusObj.status || "ok";
  const source = statusObj.source || (isStreamlitConnected ? "streamlit" : "desconectado_local");
  const rowCount = db ? db.length : 0;
  const sheetId = statusObj.spreadsheet_id || "1dpA2Nnk9dZ_NVkhJD1HHRBN4CH6Ry8bzm2Iuf_oXV8Y";

  const diagInfo = `📊 <strong>DIAGNÓSTICO BD:</strong> Fuente: <code>${source}</code> | Filas cargadas: <code>${rowCount}</code> | Spreadsheet ID: <code>${sheetId}</code>`;

  if (!isStreamlitConnected) {
    banner.style.display = "block";
    banner.style.backgroundColor = "#fff3cd";
    banner.style.color = "#856404";
    banner.style.border = "1px solid #ffeeba";
    banner.innerHTML = `⚠️ Advertencia: Modo local sin conexión a Streamlit. | ${diagInfo}`;
    return;
  }

  if (status === "warning") {
    banner.style.display = "block";
    banner.style.backgroundColor = "#fff3cd";
    banner.style.color = "#856404";
    banner.style.border = "1px solid #ffeeba";
    banner.innerHTML = `⚠️ Advertencia: ${statusObj.message || 'Sin conexión a BD central.'} | ${diagInfo}`;
  } else if (status === "error") {
    banner.style.display = "block";
    banner.style.backgroundColor = "#f8d7da";
    banner.style.color = "#721c24";
    banner.style.border = "1px solid #f5c6cb";
    banner.innerHTML = `❌ Error: ${statusObj.message || 'Error en BD central.'} | ${diagInfo}`;
  } else {
    banner.style.display = "block";
    banner.style.backgroundColor = "#e8f4f8";
    banner.style.color = "#31708f";
    banner.style.border = "1px solid #bce8f1";
    banner.innerHTML = diagInfo;
  }
}

// Initialize State
function initDB() {
  notifyStreamlitReady();

  setTimeout(() => {
    renderStatusBanner();
  }, 1200);

  fechaInforme = getTodayStr();
  renderFechaInformeDisplay();
}

function saveDB(recordsToSave, contextPayload) {
  const dataToSave = recordsToSave || db;
  const taskInfo = contextPayload && contextPayload.created_task_id ? contextPayload.created_task_id : (contextPayload && contextPayload.deleted_task_id ? contextPayload.deleted_task_id : "N/A");

  console.log(`[PUENTE_STREAMLIT] 2. saveDB() invocado | isStreamlitConnected: ${isStreamlitConnected} | Filas: ${dataToSave ? dataToSave.length : 0} | Tarea ID: ${taskInfo}`);

  // Verify connection to Streamlit and central database
  const isCentralSourceActive = window.DB_STATUS && window.DB_STATUS.status === "ok" && 
    (
      window.DB_STATUS.source === "google_sheets_service_account" || 
      window.DB_STATUS.source === "google_sheets" || 
      window.DB_STATUS.source === "google_sheets_web_app" ||
      window.DB_STATUS.source === "postgresql_vps"
    );

  if (isStreamlitConnected && isCentralSourceActive) {
    sendToStreamlit("save_db", dataToSave, contextPayload);
  } else {
    console.warn(`[PUENTE_STREAMLIT] saveDB() abortado: sin conexión a Streamlit o base central no disponible | isStreamlitConnected: ${isStreamlitConnected}`);
    const errMsg = isStreamlitConnected ? "Error: Base de datos central no disponible." : "Advertencia: Sin conexión a Streamlit / BD central.";
    showSaveToast(false, errMsg);
    renderStatusBanner();
  }
}

function resetFechaInformeToToday() {
  fechaInforme = formatDateDDMMYYYY(getTodayStr());
  renderFechaInformeDisplay();
  renderCurrentView();
}

function renderFechaInformeDisplay() {
  const inputEl = document.getElementById("sidebar-fecha-informe-input");
  if (inputEl) inputEl.value = formatDateDDMMYYYY(fechaInforme);
  const pickerEl = document.getElementById("sidebar-fecha-informe-picker");
  if (pickerEl) pickerEl.value = parseToYYYYMMDD(fechaInforme);
}

function updateFechaInforme(val) {
  if (val) {
    fechaInforme = formatDateDDMMYYYY(val);
    renderFechaInformeDisplay();
    renderCurrentView();
  }
}

// ---------------------------------------------------------
// Navigation & Router
// ---------------------------------------------------------
function switchView(viewName) {
  currentView = viewName;
  document.querySelectorAll(".view-section").forEach(sec => sec.classList.remove("active"));
  document.querySelectorAll(".nav-btn").forEach(btn => {
    btn.classList.toggle("active", btn.getAttribute("data-view") === viewName);
  });

  const targetView = document.getElementById(`view-${viewName}`);
  if (targetView) targetView.classList.add("active");

  renderCurrentView();
}

function renderCurrentView() {
  renderFechaInformeDisplay();
  if (currentView === "dashboard") renderDashboard();
  else if (currentView === "proyectos") renderProyectosTable();
  else if (currentView === "admin") renderAdmin();
  else if (currentView === "ficha-unidad") renderFichaUnidad();
  else if (currentView === "ficha-proyecto") renderFichaProyecto();
  else if (currentView === "ficha-tarea") renderFichaTarea();
  else if (currentView === "crear-proyecto") renderFormCrearProyecto();
  else if (currentView === "crear-tarea") renderFormCrearTarea();
  else if (currentView === "admin-db") renderAdminDB();
}

function openFichaUnidad(unitName) {
  selectedUnit = unitName || "Enjoy Rinconada";
  switchView("ficha-unidad");
}

function openFichaProyecto(projId) {
  selectedProjectId = projId;
  switchView("ficha-proyecto");
}

function openFichaTarea(taskId) {
  selectedTaskId = taskId;
  isEditingTarea = false;
  switchView("ficha-tarea");
}

function selectDashProject(projId) {
  if (dashSelectedProjectId === projId) {
    dashSelectedProjectId = "";
  } else {
    dashSelectedProjectId = projId;
  }
  renderDashboard();
}

// ---------------------------------------------------------
// View: Fecha de Informe
// ---------------------------------------------------------
function renderFechaInforme() {
  const inputEl = document.getElementById("input-fecha-informe");
  if (inputEl) inputEl.value = fechaInforme;
}

// ---------------------------------------------------------
// View 1: Dashboard
// ---------------------------------------------------------
function renderDashboard() {
  const filterUnitEl = document.getElementById("dash-unit-filter");
  const filterUnit = filterUnitEl ? filterUnitEl.value : "TODAS";
  const allUnits = ["Enjoy Rinconada", "Enjoy Pucón", "Enjoy Viña", "Enjoy Coquimbo", "Enjoy Chiloé", "Enjoy Transversales"];

  // Group active projects by unit
  const unitsMap = {};
  allUnits.forEach(u => unitsMap[u] = {});

  db.forEach(item => {
    if (isProjectActive(item.proyecto_estado)) {
      if (filterUnit === "TODAS" || item.unidad_nombre === filterUnit) {
        if (!unitsMap[item.unidad_nombre]) unitsMap[item.unidad_nombre] = {};
        unitsMap[item.unidad_nombre][item.proyecto_id] = item.proyecto_nombre;
      }
    }
  });

  // Zone 1: Proyectos por Unidad de Negocio List
  const unitListEl = document.getElementById("dash-unit-list");
  if (unitListEl) {
    unitListEl.innerHTML = "";

    allUnits.forEach(uName => {
      const projs = unitsMap[uName] || {};
      const projIds = Object.keys(projs);
      if (projIds.length > 0) {
        const containerDiv = document.createElement("div");
        containerDiv.className = "unit-block";

        const headerDiv = document.createElement("div");
        headerDiv.className = "unit-header";
        headerDiv.innerHTML = `
          <span class="badge-btn">${projIds.length}</span>
          <span class="unit-name-text">${uName}</span>
        `;
        containerDiv.appendChild(headerDiv);

        const subUl = document.createElement("ul");
        subUl.className = "proj-sublist";

        projIds.forEach(pid => {
          const pName = projs[pid];
          const projTasks = db.filter(item => item.proyecto_id === pid && isTaskActive(item.tarea_estado));
          const hasAlert = projTasks.some(t => (t.con_alerta || "").toLowerCase() === "si");
          const alertIconHtml = hasAlert ? ICON_ALERT_RED : "";

          const li = document.createElement("li");
          const isSelected = pid === dashSelectedProjectId;
          li.innerHTML = `
            <span class="dash-proj-link ${isSelected ? 'active' : ''}" onclick="selectDashProject('${pid}')">${pName} ${alertIconHtml}</span>
          `;
          subUl.appendChild(li);
        });

        containerDiv.appendChild(subUl);
        unitListEl.appendChild(containerDiv);
      }
    });
  }

  // Zone 2: Tareas en Curso List (Tasks ordered by creation date, newest to oldest)
  const taskListEl = document.getElementById("dash-task-list");
  if (taskListEl) {
    taskListEl.innerHTML = "";

    let tasksToRender = [];
    if (dashSelectedProjectId) {
      tasksToRender = db.filter(item => item.proyecto_id === dashSelectedProjectId && isProjectActive(item.proyecto_estado) && isTaskActive(item.tarea_estado));
    } else {
      tasksToRender = db.filter(item => {
        if (filterUnit !== "TODAS" && item.unidad_nombre !== filterUnit) return false;
        return isProjectActive(item.proyecto_estado) && isTaskActive(item.tarea_estado);
      });
    }

    const sortedTasks = sortTasksByCreationDesc(tasksToRender);
    if (sortedTasks.length === 0) {
      taskListEl.innerHTML = `<li class="task-row-item" style="color: #888; font-style: italic; font-size: 0.9rem;">Sin tareas en curso</li>`;
    } else {
      sortedTasks.forEach(task => {
        const semaforoClass = getSemaforoClass(task);

        const li = document.createElement("li");
        li.className = "task-row-item";
        li.innerHTML = `
          <div style="display: flex; align-items: center;">
            <span class="semaforo-dot ${semaforoClass}" title="Estado: ${task.tarea_estado}, Alerta: ${task.con_alerta}"></span>
            <span class="item-link" onclick="openFichaTarea('${task.tarea_id}')">${task.tarea_nombre}</span>
          </div>
          <span class="task-responsable-badge">${task.tarea_responsable || '-'}</span>
        `;
        taskListEl.appendChild(li);
      });
    }
  }

  // Zone 3: Avance Semanal (Divided into 3 stacked sub-sections: Tareas Creadas, Tareas Terminadas, Actualizar Fechas)
  const alertListEl = document.getElementById("dash-alert-list");
  if (alertListEl) {
    alertListEl.innerHTML = `
      <div style="display: flex; flex-direction: column; gap: 16px; width: 100%;">
        <div class="avance-section">
          <h3 class="avance-sub-header" style="font-size: 0.95rem; font-weight: 700; color: var(--color-title); margin-bottom: 8px; border-bottom: 1px solid var(--color-border); padding-bottom: 4px;">Tareas Creadas</h3>
          <ul id="avance-created-ul" class="item-list" style="margin: 0; padding: 0;"></ul>
        </div>

        <div class="avance-section">
          <h3 class="avance-sub-header" style="font-size: 0.95rem; font-weight: 700; color: var(--color-title); margin-bottom: 8px; border-bottom: 1px solid var(--color-border); padding-bottom: 4px;">Tareas Terminadas</h3>
          <ul id="avance-finished-ul" class="item-list" style="margin: 0; padding: 0;"></ul>
        </div>

        <div class="avance-section">
          <h3 class="avance-sub-header" style="font-size: 0.95rem; font-weight: 700; color: var(--color-title); margin-bottom: 8px; border-bottom: 1px solid var(--color-border); padding-bottom: 4px;">Actualizar Fechas</h3>
          <ul id="avance-update-ul" class="item-list" style="margin: 0; padding: 0;"></ul>
        </div>
      </div>
    `;

    const createdUl = document.getElementById("avance-created-ul");
    const finishedUl = document.getElementById("avance-finished-ul");
    const updateUl = document.getElementById("avance-update-ul");

    // Part 1: Tareas Creadas (fecha_inicio_proy en misma semana de Fecha de Informe)
    const createdTasks = db.filter(item => {
      if (filterUnit !== "TODAS" && item.unidad_nombre !== filterUnit) return false;
      const st = normalizeEstado(item.tarea_estado);
      if (st !== "en desarrollo" && st !== "detenida") return false;
      if (isEmptyDate(item.fecha_inicio_proy)) return false;
      if (!isSameWeek(item.fecha_inicio_proy, fechaInforme)) return false;
      if (!isEmptyDate(item.fecha_fin_real)) return false;
      return true;
    });

    if (createdUl) {
      if (createdTasks.length === 0) {
        createdUl.innerHTML = `<li class="alert-row-item" style="color: #888; font-style: italic; font-size: 0.9rem;">Sin tareas creadas esta semana</li>`;
      } else {
        createdTasks.forEach(task => {
          const semaforoClass = getSemaforoClass(task);
          const li = document.createElement("li");
          li.className = "alert-row-item";
          li.innerHTML = `
            <span class="alert-unit-name">${task.unidad_nombre}</span>
            <div style="display: flex; align-items: center; gap: 8px;">
              <span class="item-link" onclick="openFichaTarea('${task.tarea_id}')">${task.tarea_nombre}</span>
              <span class="semaforo-dot ${semaforoClass}" title="Estado: ${task.tarea_estado}, Alerta: ${task.con_alerta}"></span>
            </div>
          `;
          createdUl.appendChild(li);
        });
      }
    }

    // Part 2: Tareas Terminadas (fecha_fin_real en misma semana de Fecha de Informe)
    const finishedTasks = db.filter(item => {
      if (filterUnit !== "TODAS" && item.unidad_nombre !== filterUnit) return false;
      const st = normalizeEstado(item.tarea_estado);
      if (st !== "terminada" && st !== "eliminada") return false;
      if (isEmptyDate(item.fecha_fin_real)) return false;
      return isSameWeek(item.fecha_fin_real, fechaInforme);
    });

    if (finishedUl) {
      if (finishedTasks.length === 0) {
        finishedUl.innerHTML = `<li class="alert-row-item" style="color: #888; font-style: italic; font-size: 0.9rem;">Sin tareas terminadas esta semana</li>`;
      } else {
        finishedTasks.forEach(task => {
          const semaforoClass = getSemaforoClass(task);
          const li = document.createElement("li");
          li.className = "alert-row-item";
          li.innerHTML = `
            <span class="alert-unit-name">${task.unidad_nombre}</span>
            <div style="display: flex; align-items: center; gap: 8px;">
              <span class="item-link" onclick="openFichaTarea('${task.tarea_id}')">${task.tarea_nombre}</span>
              <span class="semaforo-dot ${semaforoClass}" title="Estado: ${task.tarea_estado}, Alerta: ${task.con_alerta}"></span>
            </div>
          `;
          finishedUl.appendChild(li);
        });
      }
    }

    // Part 3: Actualizar Fechas (inconsistencias diagnosticadas)
    const updateDateTasks = db.filter(item => {
      if (filterUnit !== "TODAS" && item.unidad_nombre !== filterUnit) return false;
      const diag = diagnoseDateConsistency(item);
      return !diag.isConsistent;
    });

    if (updateUl) {
      if (updateDateTasks.length === 0) {
        updateUl.innerHTML = `<li class="alert-row-item" style="color: #888; font-style: italic; font-size: 0.9rem;">Sin tareas pendientes de fecha</li>`;
      } else {
        updateDateTasks.forEach(task => {
          const diag = diagnoseDateConsistency(task);
          const reasonText = diag.reasons.join(", ");
          const semaforoClass = getSemaforoClass(task);
          const li = document.createElement("li");
          li.className = "alert-row-item";
          li.innerHTML = `
            <span class="alert-unit-name">${task.unidad_nombre}</span>
            <div style="display: flex; align-items: center; gap: 8px;">
              <span class="item-link" onclick="openFichaTarea('${task.tarea_id}')" title="${reasonText}">${task.tarea_nombre}</span>
              <span class="semaforo-dot ${semaforoClass}" title="Estado: ${task.tarea_estado}, Alerta: ${task.con_alerta} - ${reasonText}"></span>
            </div>
          `;
          updateUl.appendChild(li);
        });
      }
    }
  }
}

// Inline Table Cell Renderers for Estado & Avance %
function renderTaskStatusCell(taskId, currentStatus) {
  const status = (currentStatus || "").toLowerCase().trim();
  return `
    <select class="status-select" onchange="updateTaskStatusInline('${taskId}', this.value)" style="padding: 3px 6px; border: 1px solid var(--color-border); border-radius: 4px; font-weight: 500; background: #fff;">
      <option value="por iniciar" ${status === "por iniciar" ? "selected" : ""}>por iniciar</option>
      <option value="en desarrollo" ${status === "en desarrollo" ? "selected" : ""}>en desarrollo</option>
      <option value="detenida" ${status === "detenida" ? "selected" : ""}>detenida</option>
      <option value="terminada" ${status === "terminada" ? "selected" : ""}>terminada</option>
      <option value="eliminada" ${status === "eliminada" ? "selected" : ""}>eliminada</option>
    </select>
  `;
}

function renderTaskPctCell(taskId, currentPct) {
  const val = currentPct !== undefined && currentPct !== null ? currentPct : "";
  return `
    <input type="number" class="form-input" style="width: 60px; padding: 2px 4px; text-align: right;" min="0" max="100" value="${val}" onchange="updateTaskPctInline('${taskId}', this.value)">
  `;
}

function updateTaskStatusInline(taskId, newStatus) {
  const task = db.find(t => t.tarea_id === taskId);
  if (!task) return;
  setTaskState(task, newStatus);
  saveDB();
  renderCurrentView();
}

function updateTaskPctInline(taskId, newPct) {
  const task = db.find(t => t.tarea_id === taskId);
  if (!task) return;
  const num = newPct !== "" ? parseInt(newPct, 10) : "";
  task.tarea_pct = !isNaN(num) ? num : "";
  saveDB();
  renderCurrentView();
}

// ---------------------------------------------------------
// View 2: Proyectos (Corregida con IDs reales de index.html)
// ---------------------------------------------------------
function renderProyectosTable() {
  const tbodyActivos = document.getElementById("proyectos-table-body");
  const tbodyInactivos = document.getElementById("proyectos-inactive-table-body");

  if (tbodyActivos) tbodyActivos.innerHTML = "";
  if (tbodyInactivos) tbodyInactivos.innerHTML = "";

  db.forEach(item => {
    const isProjAct = isProjectActive(item.proyecto_estado);
    const isTskAct = isTaskActive(item.tarea_estado);
    const isRowActive = isProjAct && isTskAct;

    const targetTbody = isRowActive ? tbodyActivos : tbodyInactivos;
    if (!targetTbody) return;

    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td><span class="table-link" onclick="openFichaUnidad('${item.unidad_nombre}')">${item.unidad_nombre || '-'}</span></td>
      <td><span class="table-link" onclick="openFichaProyecto('${item.proyecto_id}')">${item.proyecto_nombre || '-'}</span></td>
      <td><span class="table-link" onclick="openFichaTarea('${item.tarea_id}')">${item.tarea_nombre || '-'}</span></td>
      <td class="col-desc">${item.tarea_descripcion || '-'}</td>
      <td>${item.tarea_responsable || '-'}</td>
      <td>${renderTaskStatusCell(item.tarea_id, item.tarea_estado)}</td>
      <td>${renderTaskPctCell(item.tarea_id, item.tarea_pct)}</td>
      <td>${renderDateCell(item.tarea_id, 'fecha_inicio_proy', item.fecha_inicio_proy)}</td>
      <td>${renderDateCell(item.tarea_id, 'fecha_fin_proy', item.fecha_fin_proy)}</td>
      <td><span class="table-link" onclick="toggleTaskAlerta('${item.tarea_id}')">${(item.con_alerta || 'no').toLowerCase() === 'si' ? 'si' : 'no'}</span></td>
      <td><button class="action-btn check-btn" onclick="completeTask('${item.tarea_id}')">${ICON_CHECK}</button></td>
      <td><button class="action-btn delete-btn" onclick="deleteTask('${item.tarea_id}')">${ICON_DELETE}</button></td>
    `;
    targetTbody.appendChild(tr);
  });
}

function updateTaskDate(taskId, fieldName, newVal) {
  const task = db.find(t => t.tarea_id === taskId);
  if (!task) return;
  task[fieldName] = newVal ? formatDateDDMMYYYY(newVal) : "";
  saveDB();
  renderCurrentView();
}

function toggleTaskAlerta(taskId) {
  const task = db.find(t => t.tarea_id === taskId);
  if (!task) return;
  const curr = (task.con_alerta || "no").toLowerCase();
  task.con_alerta = curr === "si" ? "no" : "si";
  saveDB();
  renderCurrentView();
}

// ---------------------------------------------------------
// View 3: Crear Proyecto
// ---------------------------------------------------------
function renderFormCrearProyecto() {
  const selectUnit = document.getElementById("np-unidad-nombre");
  if (!selectUnit) return;
  selectUnit.innerHTML = "";
  const allUnits = ["Enjoy Rinconada", "Enjoy Pucón", "Enjoy Viña", "Enjoy Coquimbo", "Enjoy Chiloé", "Enjoy Transversales"];
  allUnits.forEach(u => {
    const opt = document.createElement("option");
    opt.value = u;
    opt.textContent = u;
    if (u === selectedUnit) opt.selected = true;
    selectUnit.appendChild(opt);
  });

  const nameEl = document.getElementById("np-proyecto-nombre");
  if (nameEl) nameEl.value = "";
  const descEl = document.getElementById("np-proyecto-descripcion");
  if (descEl) descEl.value = "";
}

function saveNuevoProyectoForm() {
  const uNameEl = document.getElementById("np-unidad-nombre");
  const pNameEl = document.getElementById("np-proyecto-nombre");
  const pDescEl = document.getElementById("np-proyecto-descripcion");

  const uName = uNameEl ? uNameEl.value : "Enjoy Rinconada";
  const pName = pNameEl ? pNameEl.value.trim() : "";
  const pDesc = pDescEl ? pDescEl.value.trim() : "";

  if (!pName) {
    alert("Por favor ingrese el nombre del proyecto.");
    return;
  }

  const currentYear = new Date().getFullYear();
  const abbr = getUnitAbbr(uName);

  let nextSeq = 1;
  db.forEach(item => {
    if (item.proyecto_id && item.proyecto_id.includes(`_${abbr}`)) {
      const parts = item.proyecto_id.split('_');
      if (parts.length >= 2) {
        const numPart = parseInt(parts[1].replace(abbr, ''), 10);
        if (!isNaN(numPart) && numPart >= nextSeq) nextSeq = numPart + 1;
      }
    }
  });

  const seqStr = String(nextSeq).padStart(3, '0');
  const newProjId = `${currentYear}_${abbr}${seqStr}`;
  const newTaskId = `${newProjId}_001`;
  const todayStr = getTodayStr();

  const newRecord = {
    proyecto_id: newProjId,
    unidad_nombre: uName,
    proyecto_nombre: pName,
    proyecto_estado: "en desarrollo",
    proyecto_descripcion: pDesc,
    tarea_id: newTaskId,
    tarea_nombre: "Tarea inicial",
    tarea_descripcion: "",
    tarea_responsable: "",
    tarea_estado: "por iniciar",
    tarea_contraparte: "",
    tarea_pct: 0,
    tarea_fecha_creacion: todayStr,
    fecha_legacy: "",
    con_alerta: "no",
    fecha_inicio_proy: todayStr,
    fecha_inicio_real: "",
    fecha_fin_proy: "",
    fecha_fin_real: ""
  };

  const recordsToSave = [newRecord, ...db];
  const contextPayload = {
    action_type: "create_project",
    created_project_id: newProjId,
    created_task_id: newTaskId,
    pending_record: newRecord
  };

  selectedProjectId = newProjId;
  saveDB(recordsToSave, contextPayload);
  switchView("ficha-proyecto");
}

function generateNextTaskId(targetProjId) {
  if (!targetProjId) return "";
  const projTasks = db.filter(item => item.proyecto_id === targetProjId);

  let maxNum = 0;
  projTasks.forEach(task => {
    if (task.tarea_id) {
      const parts = task.tarea_id.split('_');
      if (parts.length > 0) {
        const lastPart = parts[parts.length - 1];
        const num = parseInt(lastPart, 10);
        if (!isNaN(num) && num > maxNum) {
          maxNum = num;
        }
      }
    }
  });

  let nextNum = maxNum + 1;
  let candidateId = `${targetProjId}_${String(nextNum).padStart(3, '0')}`;

  while (db.some(item => item.tarea_id === candidateId)) {
    nextNum++;
    candidateId = `${targetProjId}_${String(nextNum).padStart(3, '0')}`;
  }

  return candidateId;
}

// Formulario Creación Nueva Tarea
function renderFormCrearTarea(pendingRecord) {
  const selectUnit = document.getElementById("nt-unidad-nombre");
  if (!selectUnit) return;
  selectUnit.innerHTML = "";
  const allUnits = ["Enjoy Rinconada", "Enjoy Pucón", "Enjoy Viña", "Enjoy Coquimbo", "Enjoy Chiloé", "Enjoy Transversales"];
  
  let defaultUnit = (pendingRecord && pendingRecord.unidad_nombre) ? pendingRecord.unidad_nombre : selectedUnit;
  if (!pendingRecord && selectedProjectId) {
    const pRecord = db.find(t => t.proyecto_id === selectedProjectId);
    if (pRecord && pRecord.unidad_nombre) {
      defaultUnit = pRecord.unidad_nombre;
    }
  }

  allUnits.forEach(u => {
    const opt = document.createElement("option");
    opt.value = u;
    opt.textContent = u;
    if (u === defaultUnit) opt.selected = true;
    selectUnit.appendChild(opt);
  });

  onNuevaTareaUnitChange(selectUnit.value || allUnits[0]);

  const targetPid = (pendingRecord && pendingRecord.proyecto_id) ? pendingRecord.proyecto_id : selectedProjectId;
  if (targetPid) {
    const selectProj = document.getElementById("nt-proyecto-nombre");
    if (selectProj && selectProj.querySelector(`option[value="${targetPid}"]`)) {
      selectProj.value = targetPid;
    }
  }

  const todayStr = getTodayStr();

  let existingProjInicio = "";
  if (targetPid) {
    const existingTask = db.find(t => t.proyecto_id === targetPid && !isEmptyDate(t.fecha_inicio_proy));
    if (existingTask && existingTask.fecha_inicio_proy && existingTask.fecha_inicio_proy !== "-") {
      existingProjInicio = existingTask.fecha_inicio_proy;
    }
  }

  const nameEl = document.getElementById("nt-tarea-nombre");
  if (nameEl) nameEl.value = pendingRecord ? (pendingRecord.tarea_nombre || "") : "";

  const descEl = document.getElementById("nt-tarea-descripcion");
  if (descEl) descEl.value = pendingRecord ? (pendingRecord.tarea_descripcion || "") : "";

  const respEl = document.getElementById("nt-tarea-responsable");
  if (respEl) respEl.value = pendingRecord ? (pendingRecord.tarea_responsable || "") : "";

  const contraEl = document.getElementById("nt-tarea-contraparte");
  if (contraEl) contraEl.value = pendingRecord ? (pendingRecord.tarea_contraparte || "") : "";

  const alertaEl = document.getElementById("nt-con-alerta");
  if (alertaEl) alertaEl.value = pendingRecord ? (pendingRecord.con_alerta || "no") : "no";

  const ntInicioProyEl = document.getElementById("nt-fecha-inicio-proy");
  if (ntInicioProyEl) {
    let initialDate = todayStr;
    if (pendingRecord && pendingRecord.fecha_inicio_proy && !isEmptyDate(pendingRecord.fecha_inicio_proy) && pendingRecord.fecha_inicio_proy !== "-") {
      initialDate = pendingRecord.fecha_inicio_proy;
    } else if (existingProjInicio && !isEmptyDate(existingProjInicio) && existingProjInicio !== "-") {
      initialDate = existingProjInicio;
    }
    ntInicioProyEl.value = formatDateDDMMYYYY(initialDate);
  }

  const ntFinProyEl = document.getElementById("nt-fecha-fin-proy");
  if (ntFinProyEl) {
    ntFinProyEl.value = (pendingRecord && pendingRecord.fecha_fin_proy && pendingRecord.fecha_fin_proy !== "-") ? formatDateDDMMYYYY(pendingRecord.fecha_fin_proy) : "";
  }
}

function onNuevaTareaUnitChange(uName) {
  const selectProj = document.getElementById("nt-proyecto-nombre");
  if (!selectProj) return;
  selectProj.innerHTML = "";

  const projsMap = {};
  db.forEach(item => {
    if (item.unidad_nombre === uName && isProjectActive(item.proyecto_estado)) {
      projsMap[item.proyecto_id] = item.proyecto_nombre;
    }
  });

  const pKeys = Object.keys(projsMap);
  pKeys.forEach(pid => {
    const opt = document.createElement("option");
    opt.value = pid;
    opt.textContent = projsMap[pid];
    selectProj.appendChild(opt);
  });

  const newOpt = document.createElement("option");
  newOpt.value = "__NUEVO_PROYECTO__";
  newOpt.textContent = "+ Nuevo proyecto";
  newOpt.style.fontWeight = "bold";
  newOpt.style.color = "#C04F15";
  selectProj.appendChild(newOpt);

  if (pKeys.length > 0) {
    onNuevaTareaProjectChange(pKeys[0]);
  }
}

function onNuevaTareaProjectChange(val) {
  if (val === "__NUEVO_PROYECTO__") {
    switchView("crear-proyecto");
    return;
  }
  const ntInicioProyEl = document.getElementById("nt-fecha-inicio-proy");
  if (ntInicioProyEl && val) {
    const existingTask = db.find(t => t.proyecto_id === val && !isEmptyDate(t.fecha_inicio_proy));
    const todayStr = getTodayStr();
    const projDate = (existingTask && existingTask.fecha_inicio_proy && existingTask.fecha_inicio_proy !== "-") ? existingTask.fecha_inicio_proy : "";
    ntInicioProyEl.value = (projDate && !isEmptyDate(projDate)) ? formatDateDDMMYYYY(projDate) : formatDateDDMMYYYY(todayStr);
  }
}

function saveNuevaTareaForm() {
  const uNameEl = document.getElementById("nt-unidad-nombre");
  const pNameEl = document.getElementById("nt-proyecto-nombre");
  const tNameEl = document.getElementById("nt-tarea-nombre");
  const tDescEl = document.getElementById("nt-tarea-descripcion");
  const tRespEl = document.getElementById("nt-tarea-responsable");
  const tContraEl = document.getElementById("nt-tarea-contraparte");
  const tAlertaEl = document.getElementById("nt-con-alerta");
  const tInicioEl = document.getElementById("nt-fecha-inicio-proy");
  const tFinEl = document.getElementById("nt-fecha-fin-proy");

  const uName = uNameEl ? uNameEl.value : "Enjoy Rinconada";
  const targetProjId = pNameEl ? pNameEl.value : "";

  if (targetProjId === "__NUEVO_PROYECTO__" || !targetProjId) {
    switchView("crear-proyecto");
    return;
  }

  const tName = tNameEl ? tNameEl.value.trim() : "";
  if (!tName) {
    alert("Por favor ingrese el nombre de la tarea.");
    return;
  }

  const projTask = db.find(item => item.proyecto_id === targetProjId);
  const pName = projTask ? projTask.proyecto_nombre : "PROYECTO";
  const pStatus = projTask ? projTask.proyecto_estado : "en desarrollo";
  const pDesc = projTask ? projTask.proyecto_descripcion || "" : "";

  const newTaskId = generateNextTaskId(targetProjId);
  const todayStr = getTodayStr();

  let existingProjInicio = "";
  if (targetProjId) {
    const existingTask = db.find(t => t.proyecto_id === targetProjId && !isEmptyDate(t.fecha_inicio_proy));
    if (existingTask && existingTask.fecha_inicio_proy && existingTask.fecha_inicio_proy !== "-") {
      existingProjInicio = existingTask.fecha_inicio_proy;
    }
  }

  const fInicioProy = (tInicioEl && tInicioEl.value.trim() && tInicioEl.value.trim() !== "-") ? formatDateDDMMYYYY(tInicioEl.value.trim()) : (formatDateDDMMYYYY(existingProjInicio) || todayStr);
  const fFinProy = (tFinEl && tFinEl.value.trim() && tFinEl.value.trim() !== "-") ? formatDateDDMMYYYY(tFinEl.value.trim()) : "";

  const newRecord = {
    proyecto_id: targetProjId,
    unidad_nombre: uName,
    proyecto_nombre: pName,
    proyecto_estado: pStatus,
    proyecto_descripcion: pDesc,
    tarea_id: newTaskId,
    tarea_nombre: tName,
    tarea_descripcion: tDescEl ? tDescEl.value.trim() : "",
    tarea_responsable: tRespEl ? tRespEl.value.trim() : "",
    tarea_estado: "en desarrollo",
    tarea_contraparte: tContraEl ? tContraEl.value.trim() : "",
    tarea_pct: 0,
    tarea_fecha_creacion: todayStr,
    fecha_legacy: "",
    con_alerta: tAlertaEl ? tAlertaEl.value : "no",
    fecha_inicio_proy: fInicioProy,
    fecha_inicio_real: "",
    fecha_fin_proy: fFinProy,
    fecha_fin_real: ""
  };

  const contextPayload = {
    action_type: "create_task",
    created_task_id: newTaskId,
    pending_record: newRecord
  };

  const recordsToSave = [newRecord, ...db];

  console.log(`[PUENTE_STREAMLIT] 1. Botón Guardar presionado -> saveNuevaTareaForm() | Tarea ID nueva: ${newTaskId} | Total filas enviadas: ${recordsToSave.length}`);

  saveDB(recordsToSave, contextPayload);
}

// ---------------------------------------------------------
// View 4: Admin
// ---------------------------------------------------------
function renderAdmin() {
  const container = document.getElementById("admin-projects-list");
  if (!container) return;
  container.innerHTML = "";

  const projectsMap = {};
  db.forEach(item => {
    if (!projectsMap[item.proyecto_id]) {
      projectsMap[item.proyecto_id] = {
        unidad_nombre: item.unidad_nombre,
        proyecto_id: item.proyecto_id,
        proyecto_nombre: item.proyecto_nombre,
        proyecto_estado: item.proyecto_estado,
        proyecto_descripcion: item.proyecto_descripcion || "",
        tareasCount: 0
      };
    }
    projectsMap[item.proyecto_id].tareasCount++;
  });

  const pList = Object.values(projectsMap);
  pList.forEach(p => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${p.unidad_nombre}</td>
      <td><strong>${p.proyecto_id}</strong></td>
      <td><input type="text" class="form-input" value="${p.proyecto_nombre}" onchange="updateProjectField('${p.proyecto_id}', 'proyecto_nombre', this.value)"></td>
      <td>
        <select class="form-select" onchange="updateProjectField('${p.proyecto_id}', 'proyecto_estado', this.value)">
          <option value="en desarrollo" ${p.proyecto_estado === 'en desarrollo' ? 'selected' : ''}>en desarrollo</option>
          <option value="terminado" ${p.proyecto_estado === 'terminado' ? 'selected' : ''}>terminado</option>
          <option value="eliminado" ${p.proyecto_estado === 'eliminado' ? 'selected' : ''}>eliminado</option>
        </select>
      </td>
      <td><input type="text" class="form-input" value="${p.proyecto_descripcion}" onchange="updateProjectField('${p.proyecto_id}', 'proyecto_descripcion', this.value)"></td>
      <td><span class="badge-btn">${p.tareasCount}</span></td>
      <td><button class="btn-delete" onclick="deleteProjectPermanently('${p.proyecto_id}')">${ICON_DELETE} Eliminar</button></td>
    `;
    container.appendChild(tr);
  });
}

function updateProjectField(projId, field, newVal) {
  db.forEach(item => {
    if (item.proyecto_id === projId) {
      item[field] = newVal;
    }
  });
  saveDB();
  renderCurrentView();
}

function deleteProjectPermanently(projId) {
  if (confirm(`¿Está seguro de eliminar permanentemente el proyecto ${projId} y todas sus tareas de la base de datos central?`)) {
    const tasksToDelete = db.filter(item => item.proyecto_id === projId);
    if (tasksToDelete.length === 0) return;
    
    // Dispatched via Streamlit bridge for permanent elimination
    tasksToDelete.forEach(t => {
      sendToStreamlit("delete_permanent", null, {
        action_type: "delete_permanent",
        deleted_task_id: t.tarea_id
      });
    });
  }
}

// ---------------------------------------------------------
// View 5: Proyectos Admin (Base Completa)
// ---------------------------------------------------------
function renderAdminDB() {
  const tbody = document.getElementById("admin-db-table-body");
  if (!tbody) return;
  tbody.innerHTML = "";

  db.forEach((item) => {
    const taskId = item.tarea_id;
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td><button class="btn-delete" style="padding: 2px 6px; font-size: 0.8rem;" onclick="deleteTaskPermanentlyAdmin('${taskId}')">${ICON_DELETE}</button></td>
      <td><strong>${item.proyecto_id || ''}</strong></td>
      <td><input type="text" class="form-input" style="padding: 3px 4px; font-size: 0.82rem;" value="${item.unidad_nombre || ''}" onchange="updateAdminDBField('${taskId}', 'unidad_nombre', this.value)"></td>
      <td><input type="text" class="form-input" style="padding: 3px 4px; font-size: 0.82rem;" value="${item.proyecto_nombre || ''}" onchange="updateAdminDBField('${taskId}', 'proyecto_nombre', this.value)"></td>
      <td>
        <select class="form-select" style="padding: 3px 4px; font-size: 0.82rem;" onchange="updateAdminDBField('${taskId}', 'proyecto_estado', this.value)">
          <option value="en desarrollo" ${item.proyecto_estado === 'en desarrollo' ? 'selected' : ''}>en desarrollo</option>
          <option value="terminado" ${item.proyecto_estado === 'terminado' ? 'selected' : ''}>terminado</option>
          <option value="eliminado" ${item.proyecto_estado === 'eliminado' ? 'selected' : ''}>eliminado</option>
        </select>
      </td>
      <td><input type="text" class="form-input" style="padding: 3px 4px; font-size: 0.82rem;" value="${item.proyecto_descripcion || ''}" onchange="updateAdminDBField('${taskId}', 'proyecto_descripcion', this.value)"></td>
      <td><strong>${item.tarea_id || ''}</strong></td>
      <td><input type="text" class="form-input" style="padding: 3px 4px; font-size: 0.82rem;" value="${item.tarea_nombre || ''}" onchange="updateAdminDBField('${taskId}', 'tarea_nombre', this.value)"></td>
      <td><input type="text" class="form-input" style="padding: 3px 4px; font-size: 0.82rem;" value="${item.tarea_descripcion || ''}" onchange="updateAdminDBField('${taskId}', 'tarea_descripcion', this.value)"></td>
      <td><input type="text" class="form-input" style="padding: 3px 4px; font-size: 0.82rem; width: 60px;" value="${item.tarea_responsable || ''}" onchange="updateAdminDBField('${taskId}', 'tarea_responsable', this.value)"></td>
      <td>
        <select class="form-select" style="padding: 3px 4px; font-size: 0.82rem;" onchange="updateAdminDBField('${taskId}', 'tarea_estado', this.value)">
          <option value="por iniciar" ${item.tarea_estado === 'por iniciar' ? 'selected' : ''}>por iniciar</option>
          <option value="en desarrollo" ${item.tarea_estado === 'en desarrollo' ? 'selected' : ''}>en desarrollo</option>
          <option value="detenida" ${item.tarea_estado === 'detenida' ? 'selected' : ''}>detenida</option>
          <option value="terminada" ${item.tarea_estado === 'terminada' ? 'selected' : ''}>terminada</option>
          <option value="eliminada" ${item.tarea_estado === 'eliminada' ? 'selected' : ''}>eliminada</option>
        </select>
      </td>
      <td><input type="text" class="form-input" style="padding: 3px 4px; font-size: 0.82rem;" value="${item.tarea_contraparte || ''}" onchange="updateAdminDBField('${taskId}', 'tarea_contraparte', this.value)"></td>
      <td><input type="number" class="form-input" style="padding: 3px 4px; font-size: 0.82rem; width: 55px;" min="0" max="100" value="${item.tarea_pct !== undefined ? item.tarea_pct : ''}" onchange="updateAdminDBField('${taskId}', 'tarea_pct', this.value)"></td>
      <td><input type="date" class="form-input" style="padding: 3px 4px; font-size: 0.82rem;" value="${parseToYYYYMMDD(item.tarea_fecha_creacion)}" onchange="updateAdminDBField('${taskId}', 'tarea_fecha_creacion', this.value)"></td>
      <td><input type="date" class="form-input" style="padding: 3px 4px; font-size: 0.82rem;" value="${parseToYYYYMMDD(item.fecha_legacy)}" onchange="updateAdminDBField('${taskId}', 'fecha_legacy', this.value)"></td>
      <td>
        <select class="form-select" style="padding: 3px 4px; font-size: 0.82rem; width: 55px;" onchange="updateAdminDBField('${taskId}', 'con_alerta', this.value)">
          <option value="no" ${(item.con_alerta || 'no').toLowerCase() === 'no' ? 'selected' : ''}>no</option>
          <option value="si" ${(item.con_alerta || 'no').toLowerCase() === 'si' ? 'selected' : ''}>si</option>
        </select>
      </td>
      <td><input type="date" class="form-input" style="padding: 3px 4px; font-size: 0.82rem;" value="${parseToYYYYMMDD(item.fecha_inicio_proy)}" onchange="updateAdminDBField('${taskId}', 'fecha_inicio_proy', this.value)"></td>
      <td><input type="date" class="form-input" style="padding: 3px 4px; font-size: 0.82rem;" value="${parseToYYYYMMDD(item.fecha_inicio_real)}" onchange="updateAdminDBField('${taskId}', 'fecha_inicio_real', this.value)"></td>
      <td><input type="date" class="form-input" style="padding: 3px 4px; font-size: 0.82rem;" value="${parseToYYYYMMDD(item.fecha_fin_proy)}" onchange="updateAdminDBField('${taskId}', 'fecha_fin_proy', this.value)"></td>
      <td><input type="date" class="form-input" style="padding: 3px 4px; font-size: 0.82rem;" value="${parseToYYYYMMDD(item.fecha_fin_real)}" onchange="updateAdminDBField('${taskId}', 'fecha_fin_real', this.value)"></td>
    `;
    tbody.appendChild(tr);
  });
}

function updateAdminDBField(taskId, field, rawVal) {
  const task = db.find(t => t.tarea_id === taskId);
  if (!task) return;

  if (field === 'tarea_pct') {
    task[field] = rawVal !== "" ? parseInt(rawVal, 10) : "";
  } else if (field === 'tarea_fecha_creacion' || field === 'fecha_legacy' || field === 'fecha_inicio_proy' || field === 'fecha_inicio_real' || field === 'fecha_fin_proy' || field === 'fecha_fin_real') {
    task[field] = rawVal ? formatDateDDMMYYYY(rawVal) : "";
  } else if (field === 'tarea_estado') {
    setTaskState(task, rawVal);
  } else {
    task[field] = rawVal;
  }

  saveDB();
}

function deleteTaskPermanentlyAdmin(taskId) {
  if (!taskId) return;
  if (!confirm(`¿Está seguro de eliminar permanentemente la tarea ${taskId} de la base de datos central? Esta acción es irreversible.`)) {
    return;
  }

  const contextPayload = {
    action_type: "delete_permanent",
    deleted_task_id: taskId
  };

  const isCentralActive = window.DB_STATUS && window.DB_STATUS.status === "ok" && 
    (
      window.DB_STATUS.source === "postgresql_vps" || 
      window.DB_STATUS.source === "google_sheets_service_account" || 
      window.DB_STATUS.source === "google_sheets_web_app"
    );

  if (isStreamlitConnected && isCentralActive) {
    sendToStreamlit("delete_permanent", null, contextPayload);
  } else {
    console.warn(`[PUENTE_STREAMLIT] delete_permanent falló: sin conexión central.`);
    showSaveToast(false, "Error: Sin conexión a base central para borrado permanente.");
    renderStatusBanner();
  }
}

// ---------------------------------------------------------
// View 6: Ficha Unidad
// ---------------------------------------------------------
function renderFichaUnidad() {
  const uName = selectedUnit || "Enjoy Rinconada";
  const selectEl = document.getElementById("select-ficha-unidad");
  if (selectEl) selectEl.value = uName;

  const headerTitleEl = document.getElementById("ficha-unidad-header-title");
  if (headerTitleEl) headerTitleEl.textContent = uName;

  const unitTasks = db.filter(item => item.unidad_nombre === uName);
  const activeUnitTasks = unitTasks.filter(item => isProjectActive(item.proyecto_estado));

  const projsMap = {};
  activeUnitTasks.forEach(t => {
    if (!projsMap[t.proyecto_id]) {
      projsMap[t.proyecto_id] = {
        proyecto_id: t.proyecto_id,
        proyecto_nombre: t.proyecto_nombre,
        proyecto_estado: t.proyecto_estado,
        proyecto_descripcion: t.proyecto_descripcion,
        tareasCount: 0,
        conAlerta: false
      };
    }
    projsMap[t.proyecto_id].tareasCount++;
    if ((t.con_alerta || "").toLowerCase() === "si") {
      projsMap[t.proyecto_id].conAlerta = true;
    }
  });

  const cardContainer = document.getElementById("ficha-unidad-cards");
  if (cardContainer) {
    const pList = Object.values(projsMap);
    cardContainer.innerHTML = pList.map(p => `
      <div class="executive-card" style="margin-bottom: 16px;">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 8px;">
          <h3 style="margin: 0; font-size: 1.15rem; color: var(--color-title);">
            <span class="table-link" onclick="openFichaProyecto('${p.proyecto_id}')">${p.proyecto_nombre}</span>
            ${p.conAlerta ? ICON_ALERT_RED : ''}
          </h3>
          <span class="badge-btn">${p.tareasCount} tareas</span>
        </div>
        <p style="margin: 4px 0; color: #666; font-size: 0.9rem;">${p.proyecto_descripcion || 'Sin descripción'}</p>
      </div>
    `).join("") || `<p style="color: #888; font-style: italic;">Sin proyectos activos en esta unidad</p>`;
  }

  const tbody = document.getElementById("ficha-unidad-table-body");
  if (tbody) {
    tbody.innerHTML = "";
    activeUnitTasks.forEach(item => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td><span class="table-link" onclick="openFichaProyecto('${item.proyecto_id}')">${item.proyecto_nombre}</span></td>
        <td><span class="table-link" onclick="openFichaTarea('${item.tarea_id}')">${item.tarea_nombre}</span></td>
        <td>${item.tarea_responsable || '-'}</td>
        <td>${renderTaskStatusCell(item.tarea_id, item.tarea_estado)}</td>
        <td>${renderTaskPctCell(item.tarea_id, item.tarea_pct)}</td>
        <td>${renderDateCell(item.tarea_id, 'fecha_inicio_proy', item.fecha_inicio_proy)}</td>
        <td>${renderDateCell(item.tarea_id, 'fecha_fin_proy', item.fecha_fin_proy)}</td>
        <td><span class="table-link" onclick="toggleTaskAlerta('${item.tarea_id}')">${(item.con_alerta || 'no').toLowerCase() === 'si' ? 'si' : 'no'}</span></td>
        <td>${item.tarea_contraparte || '-'}</td>
      `;
      tbody.appendChild(tr);
    });
  }
}

// ---------------------------------------------------------
// View 7: Ficha Proyecto
// ---------------------------------------------------------
function renderFichaProyecto() {
  if (!selectedProjectId) {
    const firstTask = db.find(item => isProjectActive(item.proyecto_estado));
    if (firstTask) selectedProjectId = firstTask.proyecto_id;
  }

  const projTasks = db.filter(item => item.proyecto_id === selectedProjectId);
  const currentProj = projTasks[0];

  const selectEl = document.getElementById("select-ficha-proyecto");
  if (selectEl) {
    selectEl.innerHTML = "";
    const projsMap = {};
    db.forEach(item => {
      if (isProjectActive(item.proyecto_estado)) {
        projsMap[item.proyecto_id] = `${item.unidad_nombre} - ${item.proyecto_nombre}`;
      }
    });
    Object.keys(projsMap).forEach(pid => {
      const opt = document.createElement("option");
      opt.value = pid;
      opt.textContent = projsMap[pid];
      if (pid === selectedProjectId) opt.selected = true;
      selectEl.appendChild(opt);
    });
  }

  const headerTitleEl = document.getElementById("ficha-proyecto-header-title");
  if (headerTitleEl) {
    headerTitleEl.textContent = currentProj ? `${currentProj.unidad_nombre} - ${currentProj.proyecto_nombre}` : "Proyecto";
  }

  const alertTasks = projTasks.filter(t => (t.con_alerta || "").toLowerCase() === "si");
  const alertListText = alertTasks.map(t => `<span class="table-link" onclick="openFichaTarea('${t.tarea_id}')">${t.tarea_nombre}</span>`).join(", ") || "Ninguna";

  const cardContainer = document.getElementById("ficha-proyecto-cards");
  if (cardContainer && currentProj) {
    cardContainer.innerHTML = `
      <div class="executive-card" style="width: 100%; margin-bottom: 20px; background-color: var(--color-white);">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 8px;">
          <h2 style="margin: 0; font-size: 1.25rem; color: var(--color-title);">${currentProj.proyecto_nombre}</h2>
          <span class="badge-btn">${projTasks.length} tareas</span>
        </div>
        <p style="margin: 6px 0; color: #555; font-size: 0.95rem;">${currentProj.proyecto_descripcion || 'Sin descripción'}</p>
        <div style="margin-top: 10px; font-size: 0.88rem; color: #666;">
          <strong>Unidad:</strong> <span class="table-link" onclick="openFichaUnidad('${currentProj.unidad_nombre}')">${currentProj.unidad_nombre}</span> | 
          <strong>Estado:</strong> ${currentProj.proyecto_estado} | 
          <strong>En Alerta:</strong> ${alertListText}
        </div>
      </div>
    `;
  }

  const tbody = document.getElementById("ficha-proyecto-table-body");
  if (tbody) {
    tbody.innerHTML = "";
    projTasks.forEach(item => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td><span class="table-link" onclick="openFichaTarea('${item.tarea_id}')">${item.tarea_nombre}</span></td>
        <td>${item.tarea_responsable || '-'}</td>
        <td>${renderTaskStatusCell(item.tarea_id, item.tarea_estado)}</td>
        <td>${renderTaskPctCell(item.tarea_id, item.tarea_pct)}</td>
        <td>${item.tarea_contraparte || '-'}</td>
        <td>${renderDateCell(item.tarea_id, 'fecha_inicio_proy', item.fecha_inicio_proy)}</td>
        <td>${renderDateCell(item.tarea_id, 'fecha_fin_proy', item.fecha_fin_proy)}</td>
        <td><span class="table-link" onclick="toggleTaskAlerta('${item.tarea_id}')">${(item.con_alerta || 'no').toLowerCase() === 'si' ? 'si' : 'no'}</span></td>
        <td>${item.tarea_descripcion || '-'}</td>
      `;
      tbody.appendChild(tr);
    });
  }
}

// ---------------------------------------------------------
// View 8: Ficha Tarea
// ---------------------------------------------------------
function enableTareaEditing() {
  isEditingTarea = true;
  renderFichaTarea();
}

function renderFichaTarea() {
  if (!selectedTaskId) {
    const firstActive = db.find(item => isTaskActive(item.tarea_estado));
    if (firstActive) selectedTaskId = firstActive.tarea_id;
  }

  const task = db.find(item => item.tarea_id === selectedTaskId);
  if (!task) return;

  const projId = task.proyecto_id;

  // Task Selector for Project
  const taskSelectEl = document.getElementById("select-ficha-tarea");
  if (taskSelectEl) {
    taskSelectEl.innerHTML = "";
    const projTasks = db.filter(item => item.proyecto_id === projId);
    projTasks.forEach(t => {
      const opt = document.createElement("option");
      opt.value = t.tarea_id;
      opt.textContent = t.tarea_nombre;
      if (t.tarea_id === selectedTaskId) opt.selected = true;
      taskSelectEl.appendChild(opt);
    });
  }

  // Title Case Header Title: unidad_nombre tarea_nombre
  const headerTitleText = `${toTitleCase(task.unidad_nombre)} ${toTitleCase(task.tarea_nombre)}`;
  const headerTitleEl = document.getElementById("ficha-tarea-header-title");
  if (headerTitleEl) headerTitleEl.textContent = headerTitleText;

  // Render 2 Cards without titles on white background
  const containerEl = document.getElementById("ficha-tarea-container");
  if (!containerEl) return;

  const displayFechaInicio = formatDateDDMMYYYY(task.fecha_inicio_proy || task.tarea_fecha_creacion);
  const displayFechaFin = formatDateDDMMYYYY(task.fecha_fin_proy);
  const currentProj = db.find(item => item.proyecto_id === task.proyecto_id);
  const isProjActive = currentProj ? isProjectActive(currentProj.proyecto_estado) : true;

  if (!isEditingTarea) {
    // READ MODE: Plain Text Display
    containerEl.innerHTML = `
      <!-- Card 1: Descripción -->
      <div class="executive-card" style="width: 100%; margin-bottom: 20px; background-color: var(--color-white);">
        <div class="form-group full-width">
          <label class="form-label" style="font-size: 1.1rem; margin-bottom: 8px; font-weight: bold;">Descripción:</label>
          <p class="plain-text-val">${task.tarea_descripcion || '-'}</p>
        </div>
      </div>

      <!-- Card 2: Campos de la Tarea en Texto Plano -->
      <div class="executive-card" style="width: 100%; margin-bottom: 20px; background-color: var(--color-white);">
        <div class="card-grid-table">
          <span class="card-grid-label">Unidad de Negocio:</span>
          <span class="plain-text-val"><span class="table-link" onclick="openFichaUnidad('${task.unidad_nombre}')">${task.unidad_nombre || '-'}</span></span>

          <span class="card-grid-label">Proyecto:</span>
          <span class="plain-text-val">${isProjActive ? `<span class="table-link" onclick="openFichaProyecto('${task.proyecto_id}')">${task.proyecto_nombre || '-'}</span>` : (task.proyecto_nombre || '-')}</span>

          <span class="card-grid-label">Descripción:</span>
          <span class="plain-text-val" style="font-weight: bold;">${task.tarea_descripcion || '-'}</span>

          <span class="card-grid-label">Estado de la tarea:</span>
          <span class="plain-text-val">${task.tarea_estado || '-'}</span>

          <span class="card-grid-label">Responsable:</span>
          <span class="plain-text-val">${task.tarea_responsable || '-'}</span>

          <span class="card-grid-label">Contraparte:</span>
          <span class="plain-text-val">${task.tarea_contraparte || '-'}</span>

          <span class="card-grid-label">Fecha inicio:</span>
          <span class="plain-text-val">${displayFechaInicio}</span>

          <span class="card-grid-label">Fecha término:</span>
          <span class="plain-text-val">${displayFechaFin}</span>

          <span class="card-grid-label">Porcentaje de avance:</span>
          <span class="plain-text-val">${task.tarea_pct !== undefined && task.tarea_pct !== '' ? task.tarea_pct + '%' : '-'}</span>

          <span class="card-grid-label">Alerta:</span>
          <span class="plain-text-val">${(task.con_alerta || 'no').toLowerCase() === 'si' ? 'si' : 'no'}</span>
        </div>

        <div class="task-buttons-stack">
          <button type="button" class="btn-edit" onclick="enableTareaEditing()">${ICON_EDIT} Editar</button>
          <button type="button" class="btn-save" onclick="handleSaveButtonClick()">${ICON_SAVE} Guardado</button>
          <button type="button" class="btn-delete" onclick="deleteTaskFromFicha('${task.tarea_id}')">${ICON_DELETE} Eliminar</button>
        </div>
      </div>
    `;
  } else {
    // EDIT MODE: Form Controls Enabled
    const tStatuses = ["por iniciar", "en desarrollo", "detenida", "terminada", "eliminada"];
    const isFinished = task.tarea_estado === "terminada" || task.tarea_estado === "eliminada";

    containerEl.innerHTML = `
      <!-- Card 1: Descripción Editable -->
      <div class="executive-card" style="width: 100%; margin-bottom: 20px; background-color: var(--color-white);">
        <div class="form-group full-width">
          <label class="form-label" style="font-size: 1.1rem; margin-bottom: 8px; font-weight: bold;">Descripción:</label>
          <textarea id="t-descripcion" class="form-textarea">${task.tarea_descripcion || ''}</textarea>
        </div>
      </div>

      <!-- Card 2: Formulario Editable -->
      <div class="executive-card" style="width: 100%; margin-bottom: 20px; background-color: var(--color-white);">
        <form id="tarea-form" onsubmit="event.preventDefault(); saveTareaForm();">
          <div class="form-grid">
            <div class="form-group full-width">
              <label class="form-label">Nombre de la tarea:</label>
              <input type="text" id="t-nombre" class="form-input" value="${task.tarea_nombre || ''}">
            </div>

            <div class="form-group">
              <label class="form-label">Estado de la tarea:</label>
              <select id="t-estado" class="form-select" onchange="onFichaEstadoChange(this.value)">
                ${tStatuses.map(s => `<option value="${s}" ${task.tarea_estado === s ? "selected" : ""}>${s}</option>`).join("")}
              </select>
            </div>

            <div class="form-group">
              <label class="form-label">Alerta:</label>
              <select id="t-con-alerta" class="form-select">
                <option value="no" ${(task.con_alerta || 'no').toLowerCase() === 'no' ? 'selected' : ''}>no</option>
                <option value="si" ${(task.con_alerta || 'no').toLowerCase() === 'si' ? 'selected' : ''}>si</option>
              </select>
            </div>

            <div class="form-group">
              <label class="form-label">Responsable:</label>
              <input type="text" id="t-responsable" class="form-input" value="${task.tarea_responsable || ''}">
            </div>

            <div class="form-group">
              <label class="form-label">Contraparte:</label>
              <input type="text" id="t-contraparte" class="form-input" value="${task.tarea_contraparte || ''}">
            </div>

            <div class="form-group">
              <label class="form-label">Fecha inicio:</label>
              <input type="date" id="t-fecha-inicio" class="form-input" value="${parseToYYYYMMDD(task.fecha_inicio_proy || task.tarea_fecha_creacion)}">
            </div>

            <div class="form-group">
              <label class="form-label">Fecha término:</label>
              <input type="date" id="t-fecha-fin" class="form-input" value="${parseToYYYYMMDD(task.fecha_fin_proy)}" ${isFinished ? "disabled" : ""}>
            </div>

            <div class="form-group">
              <label class="form-label">Porcentaje de avance (%):</label>
              <input type="number" id="t-pct" class="form-input" min="0" max="100" value="${task.tarea_pct !== undefined && task.tarea_pct !== '' ? task.tarea_pct : ''}">
            </div>
          </div>

          <div class="task-buttons-stack">
            <button type="button" class="btn-edit" onclick="enableTareaEditing()">${ICON_EDIT} Editar</button>
            <button type="submit" class="btn-save">${ICON_SAVE} Guardado</button>
            <button type="button" class="btn-delete" onclick="deleteTaskFromFicha('${task.tarea_id}')">${ICON_DELETE} Eliminar</button>
          </div>
        </form>
      </div>
    `;
  }

  const backBtn = document.getElementById("btn-back-to-project");
  if (backBtn) {
    backBtn.onclick = function() {
      switchView("dashboard");
    };
  }
}

function onFichaEstadoChange(newVal) {
  const finInput = document.getElementById("t-fecha-fin");
  if (!finInput) return;
  const st = (newVal || "").toLowerCase().trim();
  if (st === "terminada" || st === "eliminada") {
    finInput.disabled = true;
  } else {
    finInput.disabled = false;
  }
}

function handleSaveButtonClick() {
  if (!isEditingTarea) {
    alert("Haga clic en 'Editar' para habilitar la modificación de los campos antes de guardar.");
    return;
  }
  saveTareaForm();
}

function saveTareaForm() {
  const task = db.find(item => item.tarea_id === selectedTaskId);
  if (!task) return;

  const estadoEl = document.getElementById("t-estado");
  if (estadoEl) {
    const newState = estadoEl.value;
    setTaskState(task, newState);
  }

  const nombreEl = document.getElementById("t-nombre");
  if (nombreEl && nombreEl.value.trim()) {
    task.tarea_nombre = nombreEl.value.trim();
  }

  const alertaEl = document.getElementById("t-con-alerta");
  if (alertaEl) {
    task.con_alerta = alertaEl.value;
  }

  const respEl = document.getElementById("t-responsable");
  if (respEl) task.tarea_responsable = respEl.value.trim();

  const contraEl = document.getElementById("t-contraparte");
  if (contraEl) task.tarea_contraparte = contraEl.value.trim();

  const descEl = document.getElementById("t-descripcion");
  if (descEl) task.tarea_descripcion = descEl.value.trim();

  const inicioEl = document.getElementById("t-fecha-inicio");
  if (inicioEl && inicioEl.value) {
    task.fecha_inicio_proy = inicioEl.value;
  }

  const finEl = document.getElementById("t-fecha-fin");
  if (finEl) {
    task.fecha_fin_proy = finEl.value;
  }

  const pctEl = document.getElementById("t-pct");
  if (pctEl) {
    task.tarea_pct = pctEl.value !== "" ? parseInt(pctEl.value, 10) : "";
  }

  isEditingTarea = false;
  saveDB();
  renderCurrentView();
}

function deleteTaskFromFicha(taskId) {
  const taskIndex = db.findIndex(item => item.tarea_id === taskId);
  if (taskIndex === -1) return;

  const currentTask = db[taskIndex];
  setTaskState(currentTask, "eliminada");
  isEditingTarea = false;
  saveDB();

  // Find next task in project or loop to first
  const projTasks = db.filter(item => item.proyecto_id === currentTask.proyecto_id);
  const currentProjIndex = projTasks.findIndex(t => t.tarea_id === taskId);

  let nextTask = null;
  if (currentProjIndex !== -1 && currentProjIndex + 1 < projTasks.length) {
    nextTask = projTasks[currentProjIndex + 1];
  } else if (projTasks.length > 0) {
    nextTask = projTasks[0];
  }

  if (nextTask) {
    selectedTaskId = nextTask.tarea_id;
    renderFichaTarea();
  } else {
    openFichaProyecto(currentTask.proyecto_id);
  }
}

// ---------------------------------------------------------
// Event Listeners Setup
// ---------------------------------------------------------
function setupEventListeners() {
  // Sidebar navigation - Preserve fechaInforme when switching views
  document.querySelectorAll(".nav-btn").forEach(btn => {
    btn.addEventListener("click", function() {
      switchView(this.getAttribute("data-view"));
    });
  });

  const resetFechaBtn = document.getElementById("btn-reset-fecha-informe");
  if (resetFechaBtn) {
    resetFechaBtn.addEventListener("click", function() {
      resetFechaInformeToToday();
    });
  }

  // Dashboard unit filter
  const dashFilter = document.getElementById("dash-unit-filter");
  if (dashFilter) {
    dashFilter.addEventListener("change", renderDashboard);
  }

  // Ficha selectors
  const selUnit = document.getElementById("select-ficha-unidad");
  if (selUnit) {
    selUnit.addEventListener("change", function() {
      selectedUnit = this.value;
      renderFichaUnidad();
    });
  }

  const selProj = document.getElementById("select-ficha-proyecto");
  if (selProj) {
    selProj.addEventListener("change", function() {
      selectedProjectId = this.value;
      renderFichaProyecto();
    });
  }

  const selTask = document.getElementById("select-ficha-tarea");
  if (selTask) {
    selTask.addEventListener("change", function() {
      selectedTaskId = this.value;
      isEditingTarea = false;
      renderFichaTarea();
    });
  }

  // Admin Buttons
  const btnDownTpl = document.getElementById("btn-download-template");
  if (btnDownTpl) btnDownTpl.addEventListener("click", downloadTemplateXLSX);

  const btnDownDB = document.getElementById("btn-download-db");
  if (btnDownDB) btnDownDB.addEventListener("click", downloadDBXLSX);

  const btnUp = document.getElementById("btn-upload-file");
  if (btnUp) {
    btnUp.addEventListener("click", function() {
      const upInput = document.getElementById("upload-file-input");
      if (upInput) upInput.click();
    });
  }

  const upFileInput = document.getElementById("upload-file-input");
  if (upFileInput) upFileInput.addEventListener("change", handleFileUpload);

  // Volver buttons in Fichas returning to Dashboard
  document.querySelectorAll(".btn-back-dashboard").forEach(btn => {
    btn.addEventListener("click", function() {
      switchView("dashboard");
    });
  });
}

function downloadTemplateXLSX() {
  console.log("Descargar plantilla XLSX");
}

function downloadDBXLSX() {
  console.log("Descargar BD XLSX");
}

function handleFileUpload(e) {
  console.log("Carga masiva XLSX");
}

function showSaveErrorBanner(msg) {
  const banner = document.getElementById("db-status-banner");
  if (!banner) return;
  banner.style.display = "block";
  banner.style.backgroundColor = "#f8d7da";
  banner.style.color = "#721c24";
  banner.style.border = "1px solid #f5c6cb";
  banner.textContent = "";
  const errSpan = document.createElement("span");
  errSpan.textContent = `❌ Error: ${msg || 'No se pudo completar la operación en la base de datos central.'}`;
  banner.appendChild(errSpan);
}

// Listen for incoming Streamlit render & state updates
window.addEventListener("message", function(event) {
  if (event.data && event.data.type === "streamlit:render") {
    isStreamlitConnected = true;
    const args = event.data.args;
    if (args) {
      if (args.db_status) {
        window.DB_STATUS = args.db_status;
      }
      if (args.initial_data && Array.isArray(args.initial_data)) {
        // Prevalencia obligatoria de la BD central recibida desde Streamlit
        db = args.initial_data;
      }

      console.log(`[PUENTE_STREAMLIT] 1. Handshake confirmado: evento 'streamlit:render' recibido | isStreamlitConnected = true | Filas cargadas: ${db ? db.length : 0} | DB Source: ${window.DB_STATUS ? window.DB_STATUS.source : 'N/A'}`);

      renderStatusBanner();

      let isTaskCreationError = false;
      let pendingRecordToRestore = null;

      if (args.save_status && typeof args.save_status === "object") {
        const ctx = args.save_status.context || {};
        const isCreateTaskAction = ctx.action_type === "create_task";
        const isDeleteAction = ctx.action_type === "delete_permanent";
        const taskInfo = ctx.created_task_id || ctx.deleted_task_id || "N/A";

        console.log(`[PUENTE_STREAMLIT] 4. Respuesta save_status recibida: ${args.save_status.status} | Tarea ID: ${taskInfo} | Mensaje: ${args.save_status.message}`);

        if (args.save_status.status === "ok") {
          try {
            localStorage.setItem("ENJOY_PROJECTS_DB_V3", JSON.stringify(db));
          } catch (e) {}

          showSaveToast(true, isDeleteAction ? `Tarea ${taskInfo} eliminada` : "Guardado");

          if (isCreateTaskAction && ctx.created_task_id) {
            console.log(`[PUENTE_STREAMLIT] 5. Tarea ${ctx.created_task_id} creada exitosamente. Redirigiendo a vista 'ficha-tarea'.`);
            selectedTaskId = ctx.created_task_id;
            isEditingTarea = false;
            switchView("ficha-tarea");
            return;
          }
        } else if (args.save_status.status === "error") {
          console.warn(`[PUENTE_STREAMLIT] Error al procesar ${taskInfo}: ${args.save_status.message}`);
          showSaveToast(false, args.save_status.message || "Error al guardar en base central");
          showSaveErrorBanner(args.save_status.message);

          if (isCreateTaskAction) {
            isTaskCreationError = true;
            pendingRecordToRestore = ctx ? ctx.pending_record : null;
          }
        }
      }

      if (isTaskCreationError) {
        currentView = "crear-tarea";
        document.querySelectorAll(".view-section").forEach(sec => sec.classList.remove("active"));
        document.querySelectorAll(".nav-btn").forEach(btn => {
          btn.classList.toggle("active", btn.getAttribute("data-view") === "crear-tarea");
        });
        const targetView = document.getElementById("view-crear-tarea");
        if (targetView) targetView.classList.add("active");
        renderFormCrearTarea(pendingRecordToRestore);
      } else {
        renderCurrentView();
      }
    }
  }
});

// Initialize on DOM Ready
document.addEventListener("DOMContentLoaded", function() {
  initDB();
  setupEventListeners();
  renderCurrentView();
});
