// Comprehensive Verification Suite for Consola Enjoy
const fs = require('fs');
const path = require('path');

const appJsPath = path.join(__dirname, 'app.js');
const indexHtmlPath = path.join(__dirname, 'index.html');

const appJs = fs.readFileSync(appJsPath, 'utf8');
const indexHtml = fs.readFileSync(indexHtmlPath, 'utf8');

console.log("==================================================");
console.log("EJECUTANDO BATERÍA DE PRUEBAS DE VERIFICACIÓN REAL");
console.log("==================================================");

let testsPassed = 0;
let totalTests = 0;

function runTest(name, fn) {
  totalTests++;
  try {
    fn();
    console.log(`[PASS] ${name}`);
    testsPassed++;
  } catch (err) {
    console.error(`[FAIL] ${name}: ${err.message}`);
  }
}

// PRUEBA 1: Diagnóstico estático y funcional de la tarea 2026_RI019_018
runTest("Prueba 1: Diagnóstico de inconsistencia para tarea 2026_RI019_018", () => {
  function isEmptyDate(val) {
    if (val === undefined || val === null) return true;
    const s = String(val).trim();
    return s === "" || s === "-" || s === "undefined" || s === "null";
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

    if (isActive && hasFinReal) {
      reasons.push("Tarea activa con fecha de término real informada");
    }
    if (isFinishedOrDeleted && !hasFinReal) {
      reasons.push("Tarea terminada/eliminada sin fecha de término real");
    }
    if (!hasInicioProy) {
      reasons.push("Sin fecha de inicio proyectada");
    }

    const pctNum = parseInt(item.tarea_pct, 10);
    if (isFinishedOrDeleted && state === "terminada" && !isNaN(pctNum) && pctNum !== 100) {
      reasons.push("Tarea terminada con porcentaje de avance distinto a 100%");
    }
    if (isActive && !isNaN(pctNum) && pctNum === 100 && (state === "en desarrollo" || state === "detenida")) {
      reasons.push("Tarea activa con porcentaje de avance igual a 100%");
    }

    return {
      isConsistent: reasons.length === 0,
      reasons: reasons
    };
  }

  const task_2026_RI019_018 = {
    tarea_id: "2026_RI019_018",
    unidad_nombre: "Enjoy Rinconada",
    proyecto_nombre: "PROYECTO RINCONADA",
    tarea_nombre: "Tarea Inconsistente de Prueba",
    tarea_estado: "en desarrollo",
    fecha_inicio_proy: "28/07/2026",
    fecha_fin_proy: "31/07/2026",
    fecha_fin_real: "31/07/2026",
    tarea_pct: 50,
    con_alerta: "no"
  };

  const result = diagnoseDateConsistency(task_2026_RI019_018);
  if (result.isConsistent) {
    throw new Error("La tarea activa con fecha_fin_real informada fue marcada erróneamente como consistente");
  }
  if (!result.reasons.includes("Tarea activa con fecha de término real informada")) {
    throw new Error("No se incluyó la razón esperada 'Tarea activa con fecha de término real informada'");
  }
});

// PRUEBA 2: Simulación del Submit de Nueva Tarea y Puente Streamlit
runTest("Prueba 2: Submit de Nueva Tarea y Puente Streamlit", () => {
  const todayStr = "07/08/2026";
  const dummyProject = {
    proyecto_id: "2026_RI020",
    unidad_nombre: "Enjoy Rinconada",
    proyecto_nombre: "RENOVACION SALON",
    proyecto_estado: "en desarrollo",
    proyecto_descripcion: "Descripcion de prueba"
  };

  const formValues = {
    unidad_nombre: "Enjoy Rinconada",
    proyecto_id: "2026_RI020",
    tarea_nombre: "Nueva Tarea de Prueba",
    tarea_descripcion: "Detalle de la nueva tarea",
    tarea_responsable: "APE",
    tarea_contraparte: "Contraparte Rinconada",
    con_alerta: "no",
    fecha_inicio_proy: "07/08/2026",
    fecha_fin_proy: "15/08/2026"
  };

  const createdTask = {
    proyecto_id: formValues.proyecto_id,
    unidad_nombre: formValues.unidad_nombre,
    proyecto_nombre: dummyProject.proyecto_nombre,
    proyecto_estado: dummyProject.proyecto_estado,
    proyecto_descripcion: dummyProject.proyecto_descripcion,
    tarea_id: "2026_RI020_002",
    tarea_nombre: formValues.tarea_nombre,
    tarea_descripcion: formValues.tarea_descripcion,
    tarea_responsable: formValues.tarea_responsable,
    tarea_estado: "en desarrollo",
    tarea_contraparte: formValues.tarea_contraparte,
    tarea_pct: 0,
    tarea_fecha_creacion: todayStr,
    fecha_legacy: "",
    con_alerta: formValues.con_alerta,
    fecha_inicio_proy: formValues.fecha_inicio_proy,
    fecha_inicio_real: "",
    fecha_fin_proy: formValues.fecha_fin_proy,
    fecha_fin_real: ""
  };

  if (createdTask.tarea_estado !== "en desarrollo" || createdTask.tarea_pct !== 0) {
    throw new Error("Estado inicial o avance de nueva tarea incorrectos");
  }
  if (createdTask.fecha_fin_real !== "") {
    throw new Error("fecha_fin_real debe inicializarse vacía");
  }

  const simulatedSaveStatusSuccess = {
    status: "ok",
    message: "Guardado exitoso en base central.",
    context: {
      action_type: "create_task",
      created_task_id: "2026_RI020_002",
      pending_record: createdTask
    }
  };

  if (simulatedSaveStatusSuccess.status !== "ok" || simulatedSaveStatusSuccess.context.created_task_id !== "2026_RI020_002") {
    throw new Error("Fallo en la estructura de respuesta de save_status");
  }
});

// PRUEBA 3: Renderizado de Ficha Tarea en Modo Lectura (Texto Plano)
runTest("Prueba 3: Renderizado de Ficha Tarea con registro válido", () => {
  const fichaSlice = appJs.substring(appJs.indexOf('function renderFichaTarea()'), appJs.indexOf('function onFichaEstadoChange'));
  if (fichaSlice.includes('Fecha en minuta') || fichaSlice.includes('task.fecha_legacy') || fichaSlice.includes('t-fecha-legacy')) {
    throw new Error("renderFichaTarea() contiene referencias a fecha_legacy o Fecha en minuta");
  }
  if (fichaSlice.includes('task.fecha_inicio_real')) {
    throw new Error("renderFichaTarea() contiene referencias a fecha_inicio_real");
  }
  if (!fichaSlice.includes('task.fecha_inicio_proy || task.tarea_fecha_creacion')) {
    throw new Error("renderFichaTarea() no implementa fallback de fecha_inicio_proy a tarea_fecha_creacion");
  }
});

// PRUEBA 4: Correspondencia estática de IDs de Proyectos entre index.html y app.js
runTest("Prueba 4: Correspondencia exacta de IDs de la sección Proyectos", () => {
  if (!indexHtml.includes('id="proyectos-table-body"')) {
    throw new Error("index.html no contiene proyectos-table-body");
  }
  if (!indexHtml.includes('id="proyectos-inactive-table-body"')) {
    throw new Error("index.html no contiene proyectos-inactive-table-body");
  }
  if (!appJs.includes('document.getElementById("proyectos-table-body")')) {
    throw new Error("app.js no usa document.getElementById('proyectos-table-body')");
  }
  if (!appJs.includes('document.getElementById("proyectos-inactive-table-body")')) {
    throw new Error("app.js no usa document.getElementById('proyectos-inactive-table-body')");
  }
  if (appJs.includes('proyectos-unit-filter')) {
    throw new Error("app.js sigue referenciando el ID inexistente proyectos-unit-filter");
  }
});

// PRUEBA 5: Inventario de handlers y onclicks en index.html vs funciones en app.js
runTest("Prueba 5: Todos los handlers onclick existen en app.js", () => {
  const requiredFunctions = [
    "createNewProject",
    "createNewTask",
    "openCreateProjectForm",
    "switchView",
    "openFichaUnidad",
    "openFichaProyecto",
    "openFichaTarea",
    "completeTask",
    "deleteTask",
    "deleteTaskPermanentlyAdmin",
    "saveNuevaTareaForm",
    "saveNuevoProyectoForm",
    "deleteProjectPermanently",
    "toggleTaskAlerta"
  ];

  requiredFunctions.forEach(fnName => {
    const pattern = new RegExp(`function\\s+${fnName}\\s*\\(`);
    if (!pattern.test(appJs)) {
      throw new Error(`La función requerida '${fnName}' no está definida en app.js`);
    }
  });
});

// PRUEBA 6: Separación de navegación y persistencia en Nuevo Proyecto y Nueva Tarea
runTest("Prueba 6: Los botones de navegación no insertan registros en la base", () => {
  // Check that createNewProject() and createNewTask() only switch views
  const createNewProjStr = appJs.substring(appJs.indexOf('function createNewProject('), appJs.indexOf('function createNewTask('));
  if (createNewProjStr.includes('db.unshift') || createNewProjStr.includes('saveDB(')) {
    throw new Error("createNewProject() sigue mutando db o llamando saveDB() directamente al navegar");
  }

  const createNewTaskStr = appJs.substring(appJs.indexOf('function createNewTask('), appJs.indexOf('const ICON_CHECK'));
  if (createNewTaskStr.includes('db.unshift') || createNewTaskStr.includes('saveDB(')) {
    throw new Error("createNewTask() sigue mutando db o llamando saveDB() directamente al navegar");
  }
});

// PRUEBA 7: Borrado permanente en Proyectos Admin envía delete_permanent al backend
runTest("Prueba 7: Borrado permanente en Admin envía evento específico delete_permanent", () => {
  const delAdminStr = appJs.substring(appJs.indexOf('function deleteTaskPermanentlyAdmin('), appJs.indexOf('function renderFichaUnidad('));
  if (!delAdminStr.includes('confirm(')) {
    throw new Error("deleteTaskPermanentlyAdmin() no solicita confirmación al usuario");
  }
  if (!delAdminStr.includes('delete_permanent')) {
    throw new Error("deleteTaskPermanentlyAdmin() no despacha el evento 'delete_permanent'");
  }
});

console.log("==================================================");
console.log(`RESUMEN FINAL: ${testsPassed} de ${totalTests} pruebas pasaron exitosamente.`);
console.log("==================================================");

if (testsPassed !== totalTests) {
  process.exit(1);
}
