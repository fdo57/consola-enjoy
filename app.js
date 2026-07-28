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

function getUnitAbbr(name) {
  if (!name) return "TR";
  return UNIT_ABBR[name] || name.substring(0, 2).toUpperCase();
}

function toTitleCase(str) {
  if (!str) return "";
  return str.toLowerCase().split(' ').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ');
}

// Helper filter functions
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

// SVG Icons permitted by INSTRUCTIONS.md
const ICON_CHECK = `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>`;
const ICON_DELETE = `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/><line x1="10" y1="11" x2="10" y2="17"/><line x1="14" y1="11" x2="14" y2="17"/></svg>`;
const ICON_SAVE = `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/><polyline points="17 21 17 13 7 13 7 21"/><polyline points="7 3 7 8 15 8"/></svg>`;
const ICON_EDIT = `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>`;
const ICON_CALENDAR = `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>`;
const ICON_ALERT_RED = `<span class="semaforo-dot semaforo-red" style="margin-left: 6px; vertical-align: middle;" title="Proyecto con tareas en alerta"></span>`;

function renderDateCell(taskId, fieldName, dateVal) {
  const displayVal = dateVal && dateVal.trim() !== "" ? dateVal : "-";
  return `
    <div class="date-cell-container">
      <span class="date-text-val">${displayVal}</span>
      <div class="date-picker-btn-wrapper">
        <button type="button" class="date-picker-btn" title="Modificar fecha">${ICON_CALENDAR}</button>
        <input type="date" class="date-picker-hidden-input" value="${dateVal || ''}" onchange="updateTaskDate('${taskId}', '${fieldName}', this.value)">
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

// Initialize State
function initDB() {
  let loaded = false;
  try {
    const localData = localStorage.getItem("ENJOY_PROJECTS_DB_V3");
    if (localData) {
      const parsed = JSON.parse(localData);
      if (Array.isArray(parsed) && parsed.length > 0) {
        db = parsed;
        loaded = true;
      }
    }
  } catch (e) {
    console.warn("localStorage access restricted or failed:", e);
  }

  if (!loaded || !db || db.length === 0) {
    db = (window.INITIAL_DATA && window.INITIAL_DATA.length > 0) ? window.INITIAL_DATA : [];
    try {
      localStorage.setItem("ENJOY_PROJECTS_DB_V3", JSON.stringify(db));
    } catch (e) {}
  }

  fechaInforme = getTodayStr();
  renderFechaInformeDisplay();
}

function saveDB() {
  try {
    localStorage.setItem("ENJOY_PROJECTS_DB_V3", JSON.stringify(db));
  } catch (e) {
    console.warn("localStorage write failed:", e);
  }
}

function getTodayStr() {
  const d = new Date();
  const year = d.getFullYear();
  const month = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
}

function resetFechaInformeToToday() {
  fechaInforme = getTodayStr();
  renderFechaInformeDisplay();
}

function renderFechaInformeDisplay() {
  const inputEl = document.getElementById("sidebar-fecha-informe-input");
  if (inputEl) inputEl.value = fechaInforme;
}

function updateFechaInforme(val) {
  if (val) {
    fechaInforme = val;
    renderFechaInformeDisplay();
    renderCurrentView();
  }
}

// ---------------------------------------------------------
// Navigation & Router
// ---------------------------------------------------------
function switchView(viewName) {
  resetFechaInformeToToday();

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

let dashSelectedProjectId = "";

function selectDashProject(projId) {
  dashSelectedProjectId = projId;
  renderDashboard();
}

// ---------------------------------------------------------
// View: Fecha de Informe
// ---------------------------------------------------------
function renderFechaInforme() {
  const inputEl = document.getElementById("input-fecha-informe");
  if (inputEl) inputEl.value = fechaInforme;
}

function updateFechaInforme(val) {
  if (val) {
    fechaInforme = val;
    localStorage.setItem("ENJOY_FECHA_INFORME", fechaInforme);
    alert(`Fecha de informe actualizada a ${fechaInforme}`);
    renderCurrentView();
  }
}

// ---------------------------------------------------------
// View 1: Dashboard
// ---------------------------------------------------------
function renderDashboard() {
  const filterUnit = document.getElementById("dash-unit-filter").value;
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

  // Find all active project IDs in unit list order
  const activeProjIds = [];
  allUnits.forEach(uName => {
    if (unitsMap[uName]) {
      Object.keys(unitsMap[uName]).forEach(pid => activeProjIds.push(pid));
    }
  });

  // Default selected project to first project of first unit if not set or invalid
  if (!dashSelectedProjectId || !activeProjIds.includes(dashSelectedProjectId)) {
    dashSelectedProjectId = activeProjIds.length > 0 ? activeProjIds[0] : "";
  }

  // Zone 1: Proyectos por Unidad de Negocio List
  const unitListEl = document.getElementById("dash-unit-list");
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

function getSemaforoClass(task) {
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

  // Zone 2: Tareas en Curso List (Dynamic tasks of selected project with Semáforo indicator)
  const taskListEl = document.getElementById("dash-task-list");
  taskListEl.innerHTML = "";

  if (dashSelectedProjectId) {
    const projTasks = db.filter(item => item.proyecto_id === dashSelectedProjectId && isProjectActive(item.proyecto_estado) && isTaskActive(item.tarea_estado));
    projTasks.forEach(task => {
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

function getMondayTimestamp(dateStr) {
  if (!dateStr) return null;
  const s = String(dateStr).trim().substring(0, 10);
  if (!s || s.length < 10 || s.toLowerCase() === "nan") return null;

  const parts = s.split('-');
  if (parts.length < 3) return null;

  const year = parseInt(parts[0], 10);
  const month = parseInt(parts[1], 10) - 1;
  const day = parseInt(parts[2], 10);

  if (isNaN(year) || isNaN(month) || isNaN(day)) return null;

  const utcDate = new Date(Date.UTC(year, month, day, 12, 0, 0));
  if (isNaN(utcDate.getTime())) return null;

  const dayOfWeek = utcDate.getUTCDay();
  const diffToMonday = dayOfWeek === 0 ? -6 : 1 - dayOfWeek;

  const mondayDate = new Date(Date.UTC(year, month, day + diffToMonday, 0, 0, 0));
  return mondayDate.toISOString().substring(0, 10);
}

function isSameWeek(dateStr1, dateStr2) {
  const m1 = getMondayTimestamp(dateStr1);
  const m2 = getMondayTimestamp(dateStr2);
  if (!m1 || !m2) return false;
  return m1 === m2;
}

  // Zone 3: Avance Semanal (Divided into 2 stacked parts: Tareas Creadas & Tareas Terminadas)
  const alertListEl = document.getElementById("dash-alert-list");
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
    </div>
  `;

  const createdUl = document.getElementById("avance-created-ul");
  const finishedUl = document.getElementById("avance-finished-ul");

  // Part 1: Tareas Creadas in same week as fechaInforme
  const createdTasks = db.filter(item => {
    if (filterUnit !== "TODAS" && item.unidad_nombre !== filterUnit) return false;
    return isSameWeek(item.tarea_fecha_creacion, fechaInforme) ||
           isSameWeek(item.fecha_inicio_proy, fechaInforme) ||
           isSameWeek(item.fecha_inicio_real, fechaInforme) ||
           isSameWeek(item.fecha_legacy, fechaInforme);
  });

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

  // Part 2: Tareas Terminadas in same week as fechaInforme
  const finishedTasks = db.filter(item => {
    if (filterUnit !== "TODAS" && item.unidad_nombre !== filterUnit) return false;
    const isFinished = (item.tarea_estado || "").toLowerCase().trim() === "terminada";
    return isSameWeek(item.fecha_fin_real, fechaInforme) ||
           isSameWeek(item.fecha_fin_proy, fechaInforme) ||
           (isFinished && isSameWeek(item.fecha_legacy, fechaInforme));
  });

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

// ---------------------------------------------------------
// View 2: Proyectos Table
// ---------------------------------------------------------
function renderProyectosTable() {
  const tbody = document.getElementById("proyectos-table-body");
  tbody.innerHTML = "";

  const activeRows = db.filter(item => isProjectActive(item.proyecto_estado) && isTaskActive(item.tarea_estado));

  activeRows.forEach(item => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td><span class="table-link" onclick="openFichaUnidad('${item.unidad_nombre}')">${item.unidad_nombre}</span></td>
      <td><span class="table-link" onclick="openFichaProyecto('${item.proyecto_id}')">${item.proyecto_nombre}</span></td>
      <td><span class="table-link" onclick="openFichaTarea('${item.tarea_id}')">${item.tarea_nombre}</span></td>
      <td class="col-desc"><div class="desc-text-clamp">${item.tarea_descripcion || ""}</div></td>
      <td>${item.tarea_responsable || ""}</td>
      <td>${item.tarea_estado || ""}</td>
      <td>${item.tarea_pct !== "" ? item.tarea_pct + "%" : ""}</td>
      <td>${renderDateCell(item.tarea_id, 'fecha_legacy', item.fecha_legacy)}</td>
      <td>${renderDateCell(item.tarea_id, 'fecha_inicio_proy', item.fecha_inicio_proy)}</td>
      <td>${renderDateCell(item.tarea_id, 'fecha_fin_proy', item.fecha_fin_proy)}</td>
      <td>
        <select class="alert-select" onchange="updateTaskAlert('${item.tarea_id}', this.value)">
          <option value="no" ${item.con_alerta === "no" ? "selected" : ""}>no</option>
          <option value="si" ${item.con_alerta === "si" ? "selected" : ""}>si</option>
        </select>
      </td>
      <td>
        <button class="action-btn check-btn" onclick="completeTask('${item.tarea_id}')">${ICON_CHECK}</button>
      </td>
      <td>
        <button class="action-btn delete-btn" onclick="deleteTask('${item.tarea_id}')">${ICON_DELETE}</button>
      </td>
    `;
    tbody.appendChild(tr);
  });
}

function createNewProject() {
  switchView("crear-proyecto");
}

function createNewTask() {
  switchView("crear-tarea");
}

// Formulario Creación Nuevo Proyecto
function renderFormCrearProyecto() {
  const selectUnit = document.getElementById("np-unidad-nombre");
  selectUnit.innerHTML = "";
  const allUnits = ["Enjoy Rinconada", "Enjoy Pucón", "Enjoy Viña", "Enjoy Coquimbo", "Enjoy Chiloé", "Enjoy Transversales"];
  allUnits.forEach(u => {
    const opt = document.createElement("option");
    opt.value = u;
    opt.textContent = u;
    if (u === selectedUnit) opt.selected = true;
    selectUnit.appendChild(opt);
  });
  document.getElementById("np-proyecto-nombre").value = "";
  document.getElementById("np-proyecto-descripcion").value = "";
}

function saveNuevoProyectoForm() {
  const uName = document.getElementById("np-unidad-nombre").value;
  const pName = document.getElementById("np-proyecto-nombre").value.trim();
  const pDesc = document.getElementById("np-proyecto-descripcion").value.trim();

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
  const todayStr = new Date().toISOString().split('T')[0];

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
    fecha_legacy: todayStr,
    con_alerta: "no",
    fecha_inicio_proy: todayStr,
    fecha_inicio_real: todayStr,
    fecha_fin_proy: "",
    fecha_fin_real: ""
  };

  db.unshift(newRecord);
  saveDB();
  selectedProjectId = newProjId;
  alert(`Proyecto "${pName}" creado con éxito.`);
  switchView("ficha-proyecto");
}

// Formulario Creación Nueva Tarea
function renderFormCrearTarea() {
  const selectUnit = document.getElementById("nt-unidad-nombre");
  selectUnit.innerHTML = "";
  const allUnits = ["Enjoy Rinconada", "Enjoy Pucón", "Enjoy Viña", "Enjoy Coquimbo", "Enjoy Chiloé", "Enjoy Transversales"];
  allUnits.forEach(u => {
    const opt = document.createElement("option");
    opt.value = u;
    opt.textContent = u;
    if (u === selectedUnit) opt.selected = true;
    selectUnit.appendChild(opt);
  });

  onNuevaTareaUnitChange(selectUnit.value || allUnits[0]);

  const todayStr = new Date().toISOString().split('T')[0];
  document.getElementById("nt-tarea-nombre").value = "";
  document.getElementById("nt-tarea-descripcion").value = "";
  document.getElementById("nt-tarea-responsable").value = "";
  document.getElementById("nt-tarea-contraparte").value = "";
  document.getElementById("nt-con-alerta").value = "no";
  document.getElementById("nt-fecha-inicio-proy").value = todayStr;
  document.getElementById("nt-fecha-inicio-real").value = todayStr;
  document.getElementById("nt-fecha-fin-proy").value = "";
  document.getElementById("nt-fecha-fin-real").value = "";
}

function onNuevaTareaUnitChange(uName) {
  const selectProj = document.getElementById("nt-proyecto-nombre");
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
}

function onNuevaTareaProjectChange(val) {
  if (val === "__NUEVO_PROYECTO__") {
    switchView("crear-proyecto");
  }
}

function saveNuevaTareaForm() {
  const uName = document.getElementById("nt-unidad-nombre").value;
  const targetProjId = document.getElementById("nt-proyecto-nombre").value;

  if (targetProjId === "__NUEVO_PROYECTO__" || !targetProjId) {
    switchView("crear-proyecto");
    return;
  }

  const tName = document.getElementById("nt-tarea-nombre").value.trim();
  if (!tName) {
    alert("Por favor ingrese el nombre de la tarea.");
    return;
  }

  const projTask = db.find(item => item.proyecto_id === targetProjId);
  const pName = projTask ? projTask.proyecto_nombre : "PROYECTO";
  const pStatus = projTask ? projTask.proyecto_estado : "en desarrollo";
  const pDesc = projTask ? projTask.proyecto_descripcion || "" : "";

  const projTasks = db.filter(item => item.proyecto_id === targetProjId);
  const nextTaskNum = projTasks.length + 1;
  const seqStr = String(nextTaskNum).padStart(3, '0');
  const newTaskId = `${targetProjId}_${seqStr}`;

  const todayStr = new Date().toISOString().split('T')[0];

  const fInicioProy = document.getElementById("nt-fecha-inicio-proy").value || todayStr;
  const fInicioReal = document.getElementById("nt-fecha-inicio-real").value || todayStr;
  const fFinProy = document.getElementById("nt-fecha-fin-proy").value || "";
  const fFinReal = document.getElementById("nt-fecha-fin-real").value || "";

  const newRecord = {
    proyecto_id: targetProjId,
    unidad_nombre: uName,
    proyecto_nombre: pName,
    proyecto_estado: pStatus,
    proyecto_descripcion: pDesc,
    tarea_id: newTaskId,
    tarea_nombre: tName,
    tarea_descripcion: document.getElementById("nt-tarea-descripcion").value.trim(),
    tarea_responsable: document.getElementById("nt-tarea-responsable").value.trim(),
    tarea_estado: "en desarrollo",
    tarea_contraparte: document.getElementById("nt-tarea-contraparte").value.trim(),
    tarea_pct: 0,
    tarea_fecha_creacion: todayStr,
    fecha_legacy: todayStr,
    con_alerta: document.getElementById("nt-con-alerta").value,
    fecha_inicio_proy: fInicioProy,
    fecha_inicio_real: fInicioReal,
    fecha_fin_proy: fFinProy,
    fecha_fin_real: fFinReal
  };

  db.unshift(newRecord);
  saveDB();
  selectedTaskId = newTaskId;
  isEditingTarea = true;
  alert(`Tarea "${tName}" creada con éxito.`);
  switchView("ficha-tarea");
}

function updateTaskDate(taskId, fieldName, val) {
  const task = db.find(t => t.tarea_id === taskId);
  if (task) {
    task[fieldName] = val;
    saveDB();
    renderCurrentView();
  }
}

function updateTaskAlert(taskId, val) {
  const task = db.find(t => t.tarea_id === taskId);
  if (task) {
    task.con_alerta = val;
    saveDB();
    renderCurrentView();
  }
}

function completeTask(taskId) {
  const task = db.find(t => t.tarea_id === taskId);
  if (task) {
    task.tarea_estado = "terminada";
    saveDB();
    renderCurrentView();
  }
}

function deleteTask(taskId) {
  const task = db.find(t => t.tarea_id === taskId);
  if (task) {
    task.tarea_estado = "eliminada";
    saveDB();
    renderCurrentView();
  }
}

// ---------------------------------------------------------
// View 3: Admin
// ---------------------------------------------------------
function renderAdmin() {
  // Handlers attached in setupEventListeners
}

function downloadTemplateXLSX() {
  const ws = XLSX.utils.aoa_to_sheet([EXCEL_HEADERS]);
  const wb = XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(wb, ws, "Plantilla");
  XLSX.writeFile(wb, "carga_masiva.xlsx");
}

function downloadDBXLSX() {
  const rows = [EXCEL_HEADERS];
  db.forEach(item => {
    rows.push(EXCEL_HEADERS.map(h => item[h] !== undefined ? item[h] : ""));
  });
  const ws = XLSX.utils.aoa_to_sheet(rows);
  XLSX.utils.book_append_sheet(wb, ws, "Base_de_Datos");
  XLSX.writeFile(wb, "base_de_datos_proyectos.xlsx");
}

function handleFileUpload(e) {
  const file = e.target.files[0];
  if (!file) return;

  const reader = new FileReader();
  reader.onload = function(evt) {
    const data = new Uint8Array(evt.target.result);
    const workbook = XLSX.read(data, { type: 'array' });
    const firstSheetName = workbook.SheetNames[0];
    const worksheet = workbook.Sheets[firstSheetName];
    const jsonRows = XLSX.utils.sheet_to_json(worksheet, { defval: "" });

    if (jsonRows.length === 0) {
      alert("El archivo subido está vacío.");
      return;
    }

    const projIdMap = {};
    db = jsonRows.map(row => {
      const cleanObj = {};
      EXCEL_HEADERS.forEach(h => {
        cleanObj[h] = row[h] !== undefined ? String(row[h]).trim() : "";
      });
      
      const uName = cleanObj.unidad_nombre || "";
      const pName = cleanObj.proyecto_nombre || "";
      const key = `${uName}_${pName}`;
      
      if (!projIdMap[key]) {
        const baseId = cleanObj.proyecto_id || "";
        const existingIds = Object.values(projIdMap);
        if (existingIds.includes(baseId)) {
          const suffixNum = existingIds.filter(v => v.startsWith(baseId)).length + 1;
          projIdMap[key] = `${baseId}_${suffixNum}`;
        } else {
          projIdMap[key] = baseId;
        }
      }
      cleanObj.proyecto_id = projIdMap[key];
      return cleanObj;
    });

    saveDB();
    alert(`Carga masiva completada con éxito. Se importaron ${db.length} registros.`);
    switchView("proyectos");
  };
  reader.readAsArrayBuffer(file);
}

// ---------------------------------------------------------
// View 4: Ficha Unidad de Negocio
// ---------------------------------------------------------
function renderFichaUnidad() {
  const allUnits = ["Enjoy Rinconada", "Enjoy Pucón", "Enjoy Viña", "Enjoy Coquimbo", "Enjoy Chiloé", "Enjoy Transversales"];
  const selectEl = document.getElementById("select-ficha-unidad");
  selectEl.innerHTML = "";
  allUnits.forEach(u => {
    const opt = document.createElement("option");
    opt.value = u;
    opt.textContent = u;
    if (u === selectedUnit) opt.selected = true;
    selectEl.appendChild(opt);
  });

  const unitData = db.filter(item => item.unidad_nombre === selectedUnit);

  // Active Projects in Unit
  const activeProjsMap = {};
  unitData.forEach(item => {
    if (isProjectActive(item.proyecto_estado)) {
      activeProjsMap[item.proyecto_id] = item.proyecto_nombre;
    }
  });
  const projCount = Object.keys(activeProjsMap).length;

  // Active Tasks in Unit
  const activeTasks = unitData.filter(item => isProjectActive(item.proyecto_estado) && isTaskActive(item.tarea_estado));
  const taskCount = activeTasks.length;

  // Alert Tasks in Unit
  const alertTasks = activeTasks.filter(item => (item.con_alerta || "").toLowerCase() === "si");
  const alertListText = alertTasks.map(t => `<span class="table-link" onclick="openFichaTarea('${t.tarea_id}')">${t.tarea_nombre}</span>`).join(", ") || "Ninguna";

  // Card Content (2-Column Grid Layout: Labels Left, Values Left)
  const cardEl = document.getElementById("ficha-unidad-card");
  cardEl.innerHTML = `
    <div class="card-title">Resumen de Unidad</div>
    <div class="card-grid-table">
      <span class="card-grid-label">Unidad:</span>
      <span class="card-grid-val">${selectedUnit}</span>

      <span class="card-grid-label">Proyectos en curso:</span>
      <span class="card-grid-val">${projCount}</span>

      <span class="card-grid-label">Tareas en curso:</span>
      <span class="card-grid-val">${taskCount}</span>

      <span class="card-grid-label">Tareas en alerta:</span>
      <span class="card-grid-val">${alertListText}</span>
    </div>
  `;

  // Render Active Table
  const tbody = document.getElementById("ficha-unidad-table-body");
  tbody.innerHTML = "";
  activeTasks.forEach(item => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td><span class="table-link" onclick="openFichaProyecto('${item.proyecto_id}')">${item.proyecto_nombre}</span></td>
      <td><span class="table-link" onclick="openFichaTarea('${item.tarea_id}')">${item.tarea_nombre}</span></td>
      <td class="col-desc"><div class="desc-text-clamp">${item.tarea_descripcion || ""}</div></td>
      <td>${item.tarea_responsable || ""}</td>
      <td>${item.tarea_estado || ""}</td>
      <td>${item.tarea_pct !== "" ? item.tarea_pct + "%" : ""}</td>
      <td>${renderDateCell(item.tarea_id, 'fecha_legacy', item.fecha_legacy)}</td>
      <td>${renderDateCell(item.tarea_id, 'fecha_inicio_proy', item.fecha_inicio_proy)}</td>
      <td>${renderDateCell(item.tarea_id, 'fecha_fin_proy', item.fecha_fin_proy)}</td>
      <td>
        <select class="alert-select" onchange="updateTaskAlert('${item.tarea_id}', this.value)">
          <option value="no" ${item.con_alerta === "no" ? "selected" : ""}>no</option>
          <option value="si" ${item.con_alerta === "si" ? "selected" : ""}>si</option>
        </select>
      </td>
      <td><button class="action-btn check-btn" onclick="completeTask('${item.tarea_id}')">${ICON_CHECK}</button></td>
      <td><button class="action-btn delete-btn" onclick="deleteTask('${item.tarea_id}')">${ICON_DELETE}</button></td>
    `;
    tbody.appendChild(tr);
  });

  // Render Inactive/Terminated Projects Table
  const inactiveTbody = document.getElementById("ficha-unidad-inactive-table-body");
  inactiveTbody.innerHTML = "";
  const inactiveTasks = unitData.filter(item => !isProjectActive(item.proyecto_estado) || !isTaskActive(item.tarea_estado));
  inactiveTasks.forEach(item => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${item.proyecto_nombre}</td>
      <td>${item.tarea_nombre}</td>
      <td>${item.tarea_descripcion || ""}</td>
      <td>${item.tarea_responsable || ""}</td>
      <td>${item.tarea_estado || ""}</td>
      <td>${item.tarea_pct !== "" ? item.tarea_pct + "%" : ""}</td>
      <td>${item.fecha_legacy || "-"}</td>
      <td>${item.fecha_inicio_proy || "-"}</td>
      <td>${item.fecha_fin_proy || "-"}</td>
      <td>${item.con_alerta}</td>
      <td>-</td>
      <td>-</td>
    `;
    inactiveTbody.appendChild(tr);
  });
}

// ---------------------------------------------------------
// View 5: Ficha Proyecto
// ---------------------------------------------------------
function renderFichaProyecto() {
  if (!selectedProjectId) {
    const firstActive = db.find(item => isProjectActive(item.proyecto_estado));
    if (firstActive) selectedProjectId = firstActive.proyecto_id;
  }

  const currentProjTask = db.find(item => item.proyecto_id === selectedProjectId);
  if (!currentProjTask) return;

  const unitName = currentProjTask.unidad_nombre;

  // Dropdown options: projects in same unit
  const projSelectEl = document.getElementById("select-ficha-proyecto");
  projSelectEl.innerHTML = "";
  const projMap = {};
  db.filter(item => item.unidad_nombre === unitName).forEach(item => {
    projMap[item.proyecto_id] = item.proyecto_nombre;
  });

  Object.keys(projMap).forEach(pid => {
    const opt = document.createElement("option");
    opt.value = pid;
    opt.textContent = projMap[pid];
    if (pid === selectedProjectId) opt.selected = true;
    projSelectEl.appendChild(opt);
  });

  const projTasks = db.filter(item => item.proyecto_id === selectedProjectId);
  const activeTasks = projTasks.filter(item => isTaskActive(item.tarea_estado));
  const alertTasks = activeTasks.filter(item => (item.con_alerta || "").toLowerCase() === "si");
  const alertListText = alertTasks.map(t => `<span class="table-link" onclick="openFichaTarea('${t.tarea_id}')">${t.tarea_nombre}</span>`).join(", ") || "Ninguna";

  // Card Content (2-Column Grid Layout: Labels Left, Values Left)
  const cardEl = document.getElementById("ficha-proyecto-card");
  cardEl.innerHTML = `
    <div class="card-title">Ficha del Proyecto</div>
    <div class="card-grid-table">
      <span class="card-grid-label">Unidad de Negocio:</span>
      <span class="table-link" onclick="openFichaUnidad('${unitName}')">${unitName}</span>

      <span class="card-grid-label">Proyecto:</span>
      <input type="text" id="edit-proj-name" class="form-input" value="${currentProjTask.proyecto_nombre}" onchange="updateProjectName('${selectedProjectId}', this.value)" style="max-width: 300px;">

      <span class="card-grid-label">Descripción del Proyecto:</span>
      <textarea id="edit-proj-desc" class="form-textarea" onchange="updateProjectDesc('${selectedProjectId}', this.value)" style="max-width: 400px; min-height: 50px;">${currentProjTask.proyecto_descripcion || ''}</textarea>

      <span class="card-grid-label">Estado del Proyecto:</span>
      <select id="edit-proj-status" class="form-select" onchange="updateProjectStatus('${selectedProjectId}', this.value)" style="max-width: 200px;">
        <option value="por iniciar" ${currentProjTask.proyecto_estado === "por iniciar" ? "selected" : ""}>por iniciar</option>
        <option value="en desarrollo" ${currentProjTask.proyecto_estado === "en desarrollo" ? "selected" : ""}>en desarrollo</option>
        <option value="en construcción" ${currentProjTask.proyecto_estado === "en construcción" ? "selected" : ""}>en construcción</option>
        <option value="detenido" ${currentProjTask.proyecto_estado === "detenido" ? "selected" : ""}>detenido</option>
        <option value="terminado" ${currentProjTask.proyecto_estado === "terminado" ? "selected" : ""}>terminado</option>
        <option value="eliminado" ${currentProjTask.proyecto_estado === "eliminado" ? "selected" : ""}>eliminado</option>
      </select>

      <span class="card-grid-label">Tareas en curso:</span>
      <span class="card-grid-val">${activeTasks.length}</span>

      <span class="card-grid-label">Tareas en alerta:</span>
      <span class="card-grid-val">${alertListText}</span>
    </div>
  `;

  // Render Active Tasks Table
  const tbody = document.getElementById("ficha-proyecto-table-body");
  tbody.innerHTML = "";
  activeTasks.forEach(item => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td><span class="table-link" onclick="openFichaTarea('${item.tarea_id}')">${item.tarea_nombre}</span></td>
      <td class="col-desc"><div class="desc-text-clamp">${item.tarea_descripcion || ""}</div></td>
      <td>${item.tarea_responsable || ""}</td>
      <td>${item.tarea_estado || ""}</td>
      <td>${item.tarea_pct !== "" ? item.tarea_pct + "%" : ""}</td>
      <td>${item.tarea_contraparte || ""}</td>
      <td>${renderDateCell(item.tarea_id, 'fecha_legacy', item.fecha_legacy)}</td>
      <td>${renderDateCell(item.tarea_id, 'fecha_inicio_proy', item.fecha_inicio_proy)}</td>
      <td>${renderDateCell(item.tarea_id, 'fecha_fin_proy', item.fecha_fin_proy)}</td>
      <td>
        <select class="alert-select" onchange="updateTaskAlert('${item.tarea_id}', this.value)">
          <option value="no" ${item.con_alerta === "no" ? "selected" : ""}>no</option>
          <option value="si" ${item.con_alerta === "si" ? "selected" : ""}>si</option>
        </select>
      </td>
      <td><button class="action-btn check-btn" onclick="completeTask('${item.tarea_id}')">${ICON_CHECK}</button></td>
      <td><button class="action-btn delete-btn" onclick="deleteTask('${item.tarea_id}')">${ICON_DELETE}</button></td>
    `;
    tbody.appendChild(tr);
  });

  // Render Inactive Tasks Table
  const inactiveTbody = document.getElementById("ficha-proyecto-inactive-table-body");
  inactiveTbody.innerHTML = "";
  const inactiveTasks = projTasks.filter(item => !isTaskActive(item.tarea_estado));
  inactiveTasks.forEach(item => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${item.tarea_nombre}</td>
      <td>${item.tarea_descripcion || ""}</td>
      <td>${item.tarea_responsable || ""}</td>
      <td>${item.tarea_estado || ""}</td>
      <td>${item.tarea_pct !== "" ? item.tarea_pct + "%" : ""}</td>
      <td>${item.tarea_contraparte || ""}</td>
      <td>${item.fecha_legacy || "-"}</td>
      <td>${item.fecha_inicio_proy || "-"}</td>
      <td>${item.fecha_fin_proy || "-"}</td>
      <td>${item.con_alerta}</td>
      <td>-</td>
      <td>-</td>
    `;
    inactiveTbody.appendChild(tr);
  });
}

function updateProjectName(projId, newName) {
  db.forEach(item => {
    if (item.proyecto_id === projId) item.proyecto_nombre = newName;
  });
  saveDB();
  renderCurrentView();
}

function updateProjectDesc(projId, newDesc) {
  db.forEach(item => {
    if (item.proyecto_id === projId) item.proyecto_descripcion = newDesc;
  });
  saveDB();
  renderCurrentView();
}

function updateProjectStatus(projId, newStatus) {
  db.forEach(item => {
    if (item.proyecto_id === projId) item.proyecto_estado = newStatus;
  });
  saveDB();
  renderCurrentView();
}

// ---------------------------------------------------------
// View 6: Ficha Tarea
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
  taskSelectEl.innerHTML = "";
  const projTasks = db.filter(item => item.proyecto_id === projId);
  projTasks.forEach(t => {
    const opt = document.createElement("option");
    opt.value = t.tarea_id;
    opt.textContent = t.tarea_nombre;
    if (t.tarea_id === selectedTaskId) opt.selected = true;
    taskSelectEl.appendChild(opt);
  });

  // Title Case Header Title: unidad_nombre tarea_nombre
  const headerTitleText = `${toTitleCase(task.unidad_nombre)} ${toTitleCase(task.tarea_nombre)}`;
  const headerTitleEl = document.getElementById("ficha-tarea-header-title");
  if (headerTitleEl) headerTitleEl.textContent = headerTitleText;

  // Render 2 Cards without titles
  const containerEl = document.getElementById("ficha-tarea-container");

  if (!isEditingTarea) {
    // READ MODE: Plain Text Display
    containerEl.innerHTML = `
      <!-- Card 1: Descripción -->
      <div class="executive-card" style="width: 100%; margin-bottom: 20px; background-color: var(--color-white);">
        <div class="form-group full-width">
          <label class="form-label" style="font-size: 1.1rem; margin-bottom: 8px;">Descripción:</label>
          <p class="plain-text-val">${task.tarea_descripcion || '-'}</p>
        </div>
      </div>

      <!-- Card 2: Campos de la Tarea en Texto Plano -->
      <div class="executive-card" style="width: 100%; margin-bottom: 20px; background-color: var(--color-white);">
        <div class="card-grid-table">
          <span class="card-grid-label">Nombre de la tarea:</span>
          <span class="plain-text-val">${task.tarea_nombre || '-'}</span>

          <span class="card-grid-label">Estado de la tarea:</span>
          <span class="plain-text-val">${task.tarea_estado || '-'}</span>

          <span class="card-grid-label">Responsable:</span>
          <span class="plain-text-val">${task.tarea_responsable || '-'}</span>

          <span class="card-grid-label">Contraparte:</span>
          <span class="plain-text-val">${task.tarea_contraparte || '-'}</span>

          <span class="card-grid-label">Fecha según Minuta:</span>
          <span class="plain-text-val">${task.fecha_legacy || '-'}</span>

          <span class="card-grid-label">Fecha inicio:</span>
          <span class="plain-text-val">${task.fecha_inicio_proy || '-'}</span>

          <span class="card-grid-label">Fecha término:</span>
          <span class="plain-text-val">${task.fecha_fin_proy || '-'}</span>

          <span class="card-grid-label">Porcentaje de avance:</span>
          <span class="plain-text-val">${task.tarea_pct !== '' ? task.tarea_pct + '%' : '-'}</span>

          <span class="card-grid-label">Alerta:</span>
          <span class="plain-text-val">${(task.con_alerta || 'no').toLowerCase() === 'si' ? 'si' : 'no'}</span>
        </div>

        <div class="task-buttons-stack">
          <button type="button" class="btn-edit" onclick="enableTareaEditing()">${ICON_EDIT} Editar</button>
          <button type="button" class="btn-save" onclick="handleSaveButtonClick()">${ICON_SAVE} Guardar</button>
          <button type="button" class="btn-delete" onclick="deleteTaskFromFicha('${task.tarea_id}')">${ICON_DELETE} Eliminar</button>
        </div>
      </div>
    `;
  } else {
    // EDIT MODE: Form Controls Enabled (including tarea_nombre edit & con_alerta edit)
    containerEl.innerHTML = `
      <!-- Card 1: Descripción Editable -->
      <div class="executive-card" style="width: 100%; margin-bottom: 20px; background-color: var(--color-white);">
        <div class="form-group full-width">
          <label class="form-label" style="font-size: 1.1rem; margin-bottom: 8px;">Descripción:</label>
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
              <select id="t-estado" class="form-select">
                <option value="por iniciar" ${task.tarea_estado === "por iniciar" ? "selected" : ""}>por iniciar</option>
                <option value="en desarrollo" ${task.tarea_estado === "en desarrollo" ? "selected" : ""}>en desarrollo</option>
                <option value="detenida" ${task.tarea_estado === "detenida" ? "selected" : ""}>detenida</option>
                <option value="terminada" ${task.tarea_estado === "terminada" ? "selected" : ""}>terminada</option>
                <option value="eliminada" ${task.tarea_estado === "eliminada" ? "selected" : ""}>eliminada</option>
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
              <label class="form-label">Fecha según Minuta:</label>
              <input type="date" id="t-fecha-legacy" class="form-input" value="${task.fecha_legacy || ''}">
            </div>

            <div class="form-group">
              <label class="form-label">Fecha inicio:</label>
              <input type="date" id="t-fecha-inicio" class="form-input" value="${task.fecha_inicio_proy || ''}">
            </div>

            <div class="form-group">
              <label class="form-label">Fecha término:</label>
              <input type="date" id="t-fecha-fin" class="form-input" value="${task.fecha_fin_proy || ''}">
            </div>

            <div class="form-group">
              <label class="form-label">Porcentaje de avance (%):</label>
              <input type="number" id="t-pct" class="form-input" min="0" max="100" value="${task.tarea_pct !== '' ? task.tarea_pct : ''}">
            </div>
          </div>

          <div class="task-buttons-stack">
            <button type="button" class="btn-edit" onclick="enableTareaEditing()">${ICON_EDIT} Editar</button>
            <button type="submit" class="btn-save">${ICON_SAVE} Guardar</button>
            <button type="button" class="btn-delete" onclick="deleteTaskFromFicha('${task.tarea_id}')">${ICON_DELETE} Eliminar</button>
          </div>
        </form>
      </div>
    `;
  }

  document.getElementById("btn-back-to-project").onclick = function() {
    switchView("dashboard");
  };
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

  const newName = document.getElementById("t-nombre") ? document.getElementById("t-nombre").value.trim() : "";
  if (newName) task.tarea_nombre = newName;

  task.tarea_estado = document.getElementById("t-estado").value;
  if (document.getElementById("t-con-alerta")) {
    task.con_alerta = document.getElementById("t-con-alerta").value;
  }
  task.tarea_responsable = document.getElementById("t-responsable").value;
  task.tarea_contraparte = document.getElementById("t-contraparte").value;
  task.tarea_descripcion = document.getElementById("t-descripcion").value;
  task.fecha_legacy = document.getElementById("t-fecha-legacy").value;
  task.fecha_inicio_proy = document.getElementById("t-fecha-inicio").value;
  task.fecha_fin_proy = document.getElementById("t-fecha-fin").value;
  task.tarea_pct = document.getElementById("t-pct").value;

  isEditingTarea = false;
  saveDB();
  alert("Tarea guardada correctamente.");
  renderCurrentView();
}

function deleteTaskFromFicha(taskId) {
  const taskIndex = db.findIndex(item => item.tarea_id === taskId);
  if (taskIndex === -1) return;

  const currentTask = db[taskIndex];
  currentTask.tarea_estado = "eliminada";
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
  // Sidebar navigation - Ensure any click on sidebar navigation buttons resets fechaInforme to today
  document.querySelectorAll(".nav-btn").forEach(btn => {
    btn.addEventListener("click", function() {
      resetFechaInformeToToday();
      switchView(this.getAttribute("data-view"));
    });
  });

  // Dashboard unit filter
  document.getElementById("dash-unit-filter").addEventListener("change", renderDashboard);

  // Ficha selectors
  document.getElementById("select-ficha-unidad").addEventListener("change", function() {
    selectedUnit = this.value;
    renderFichaUnidad();
  });

  document.getElementById("select-ficha-proyecto").addEventListener("change", function() {
    selectedProjectId = this.value;
    renderFichaProyecto();
  });

  document.getElementById("select-ficha-tarea").addEventListener("change", function() {
    selectedTaskId = this.value;
    isEditingTarea = false;
    renderFichaTarea();
  });

  // Admin Buttons
  document.getElementById("btn-download-template").addEventListener("click", downloadTemplateXLSX);
  document.getElementById("btn-download-db").addEventListener("click", downloadDBXLSX);
  document.getElementById("btn-upload-file").addEventListener("click", function() {
    document.getElementById("upload-file-input").click();
  });
  document.getElementById("upload-file-input").addEventListener("change", handleFileUpload);

  // Volver buttons in Fichas returning to Dashboard
  document.querySelectorAll(".btn-back-dashboard").forEach(btn => {
    btn.addEventListener("click", function() {
      switchView("dashboard");
    });
  });
}

// Initialize on DOM Ready
document.addEventListener("DOMContentLoaded", function() {
  initDB();
  setupEventListeners();
  renderCurrentView();
});
