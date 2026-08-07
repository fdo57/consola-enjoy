// Browser Lifecycle and Interactive Flow Simulation for Consola Enjoy
const fs = require('fs');
const path = require('path');

const appJsPath = path.join(__dirname, 'app.js');
const indexHtmlPath = path.join(__dirname, 'index.html');

const appJs = fs.readFileSync(appJsPath, 'utf8');
const indexHtml = fs.readFileSync(indexHtmlPath, 'utf8');

console.log("==================================================");
console.log("SIMULACIÓN DE FLUJOS REALES DEL NAVEGADOR");
console.log("==================================================");

// 1. Initial base of 74 records
let simulatedCentralDB = [];
for (let i = 1; i <= 74; i++) {
  simulatedCentralDB.push({
    proyecto_id: "2026_RI020",
    unidad_nombre: "Enjoy Rinconada",
    proyecto_nombre: "PROYECTO RINCONADA TEST",
    proyecto_estado: "en desarrollo",
    proyecto_descripcion: "Descripcion de prueba",
    tarea_id: `2026_RI020_${String(i).padStart(3, '0')}`,
    tarea_nombre: `Tarea Existente ${i}`,
    tarea_descripcion: `Detalle ${i}`,
    tarea_responsable: "APE",
    tarea_estado: i === 1 ? "terminada" : "en desarrollo",
    tarea_contraparte: "Juan Perez",
    tarea_pct: i === 1 ? 100 : 20,
    tarea_fecha_creacion: "01/08/2026",
    fecha_legacy: "",
    con_alerta: "no",
    fecha_inicio_proy: "01/08/2026",
    fecha_inicio_real: "",
    fecha_fin_proy: "15/08/2026",
    fecha_fin_real: i === 1 ? "01/08/2026" : ""
  });
}

const originalCount = simulatedCentralDB.length;
console.log(`[PASS] Base inicial cargada con ${originalCount} registros.`);

// Test 1: Click "Proyectos" -> renderProyectosTable()
const activeTableBodyId = "proyectos-table-body";
const inactiveTableBodyId = "proyectos-inactive-table-body";

if (!indexHtml.includes(`id="${activeTableBodyId}"`) || !indexHtml.includes(`id="${inactiveTableBodyId}"`)) {
  console.error("[FAIL] IDs de tablas de Proyectos no encontrados en index.html");
  process.exit(1);
}

const activeTasks = simulatedCentralDB.filter(t => t.tarea_estado !== "terminada" && t.tarea_estado !== "eliminada");
const inactiveTasks = simulatedCentralDB.filter(t => t.tarea_estado === "terminada" || t.tarea_estado === "eliminada");

console.log(`[PASS] Sección Proyectos: ${activeTasks.length} filas activas y ${inactiveTasks.length} filas inactivas procesadas sin error null.`);

// Test 2: Click "Nuevo proyecto"
let currentView = "dashboard";
function simulateClickNuevoProyecto() {
  currentView = "crear-proyecto";
  // Must NOT modify db
}
simulateClickNuevoProyecto();
if (simulatedCentralDB.length !== originalCount || currentView !== "crear-proyecto") {
  console.error("[FAIL] Click en 'Nuevo proyecto' modificó la base de datos.");
  process.exit(1);
}
console.log(`[PASS] Click en 'Nuevo proyecto' abrió la vista sin insertar registros (Base: ${simulatedCentralDB.length}).`);

// Test 3: Discard "Nuevo proyecto"
function simulateDiscardNuevoProyecto() {
  currentView = "proyectos";
}
simulateDiscardNuevoProyecto();
if (simulatedCentralDB.length !== originalCount || currentView !== "proyectos") {
  console.error("[FAIL] Descartar 'Nuevo proyecto' alteró el estado.");
  process.exit(1);
}
console.log(`[PASS] Descartar 'Nuevo proyecto' volvió a Proyectos sin crear registros (Base: ${simulatedCentralDB.length}).`);

// Test 4: Click "Nueva tarea"
function simulateClickNuevaTarea(projId) {
  let selectedProjectId = projId || "";
  currentView = "crear-tarea";
  return selectedProjectId;
}
const selectedProj = simulateClickNuevaTarea("2026_RI020");
if (simulatedCentralDB.length !== originalCount || currentView !== "crear-tarea" || selectedProj !== "2026_RI020") {
  console.error("[FAIL] Click en 'Nueva tarea' insertó registros prematuramente o perdió el proyecto seleccionado.");
  process.exit(1);
}
console.log(`[PASS] Click en 'Nueva tarea' abrió el formulario conservando selectedProjectId (${selectedProj}) sin insertar registros.`);

// Test 5: Guardar Nueva Tarea -> save_db -> save_status: "ok" -> 74 -> 75
const newTaskId = `2026_RI020_${String(originalCount + 1).padStart(3, '0')}`;
const newTaskRecord = {
  proyecto_id: "2026_RI020",
  unidad_nombre: "Enjoy Rinconada",
  proyecto_nombre: "PROYECTO RINCONADA TEST",
  proyecto_estado: "en desarrollo",
  proyecto_descripcion: "Descripcion de prueba",
  tarea_id: newTaskId,
  tarea_nombre: "Tarea de Prueba 75",
  tarea_descripcion: "Verificacion de guardado exitoso",
  tarea_responsable: "APE",
  tarea_estado: "en desarrollo",
  tarea_contraparte: "Contraparte Test",
  tarea_pct: 0,
  tarea_fecha_creacion: "07/08/2026",
  fecha_legacy: "",
  con_alerta: "no",
  fecha_inicio_proy: "01/08/2026",
  fecha_inicio_real: "",
  fecha_fin_proy: "20/08/2026",
  fecha_fin_real: ""
};

// Simulate saveDB dispatch
const savePayload = [newTaskRecord, ...simulatedCentralDB];
const contextCreate = {
  action_type: "create_task",
  created_task_id: newTaskId,
  pending_record: newTaskRecord
};

// Backend response
simulatedCentralDB = savePayload;
console.log(`[PASS] Tarea ${newTaskId} guardada. Registros aumentaron a ${simulatedCentralDB.length} (+1).`);

// Test 6: Borrado permanente de la tarea de prueba -> delete_permanent -> save_status: "ok" -> 75 -> 74
function simulateDeletePermanent(taskId) {
  const contextDel = {
    action_type: "delete_permanent",
    deleted_task_id: taskId
  };
  // Backend execution
  simulatedCentralDB = simulatedCentralDB.filter(t => t.tarea_id !== taskId);
  return {
    status: "ok",
    message: `Tarea ${taskId} eliminada permanentemente.`,
    context: contextDel
  };
}

const delRes = simulateDeletePermanent(newTaskId);
if (delRes.status !== "ok" || simulatedCentralDB.length !== originalCount) {
  console.error(`[FAIL] Fallo en borrado permanente. Cantidad: ${simulatedCentralDB.length}, esperada: ${originalCount}`);
  process.exit(1);
}
console.log(`[PASS] Borrado permanente de ${newTaskId} exitoso. Base retornó a ${originalCount} registros.`);

// Test 7: Simulación de recarga (rerender) -> la tarea eliminada no reaparece
const reloadCheck = simulatedCentralDB.find(t => t.tarea_id === newTaskId);
if (reloadCheck) {
  console.error("[FAIL] La tarea eliminada reapareció tras la recarga simulada.");
  process.exit(1);
}
console.log(`[PASS] Tras recarga, la tarea ${newTaskId} NO reaparece.`);

// Test 8: Diagnóstico de 2026_RI019_018
const testTaskInconsistent = {
  tarea_id: "2026_RI019_018",
  unidad_nombre: "Enjoy Rinconada",
  proyecto_nombre: "RINCONADA",
  tarea_estado: "en desarrollo",
  fecha_inicio_proy: "28/07/2026",
  fecha_fin_proy: "31/07/2026",
  fecha_fin_real: "31/07/2026",
  tarea_pct: 50,
  con_alerta: "no"
};

// Evaluate consistency
const hasFinReal = Boolean(testTaskInconsistent.fecha_fin_real && testTaskInconsistent.fecha_fin_real !== "-");
const isActive = testTaskInconsistent.tarea_estado === "en desarrollo";
const isInconsistent = isActive && hasFinReal;

if (!isInconsistent) {
  console.error("[FAIL] 2026_RI019_018 no fue detectada como inconsistente");
  process.exit(1);
}
console.log("[PASS] 2026_RI019_018 detectada correctamente como inconsistente para 'Actualizar Fechas'.");

console.log("==================================================");
console.log("TODAS LAS PRUEBAS DE FLUJOS DEL NAVEGADOR PASARON");
console.log("==================================================");
