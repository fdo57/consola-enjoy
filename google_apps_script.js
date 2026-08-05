/**
 * ====================================================================
 * GOOGLE APPS SCRIPT WEB APP - CONSOLA ENJOY
 * Spreadsheet ID: 1dpA2Nnk9dZ_NVkhJD1HHRBN4CH6Ry8bzm2Iuf_oXV8Y
 * Hoja objetivo: Base_de_Datos (o la primera hoja activa)
 * ====================================================================
 *
 * INSTRUCCIONES DE DESPLIEGUE EN GOOGLE APPS SCRIPT:
 * 1. Abre tu Google Sheet oficial: https://docs.google.com/spreadsheets/d/1dpA2Nnk9dZ_NVkhJD1HHRBN4CH6Ry8bzm2Iuf_oXV8Y
 * 2. Ve al menú superior: Extensiones ➔ Apps Script.
 * 3. Reemplaza todo el código por este script.
 * 4. Haz clic en "Implementar" (Deploy) ➔ "Nueva implementación" (New deployment).
 * 5. Selecciona el tipo: "Aplicación Web" (Web app).
 * 6. Configuración:
 *    - Descripción: Consola Enjoy API
 *    - Ejecutar como: "Yo" (Me)
 *    - Quién tiene acceso: "Cualquier persona" (Anyone)  <-- ¡CRÍTICO!
 * 7. Haz clic en "Implementar" y autoriza los permisos requeridos.
 * 8. Copia la URL asignada (debe terminar en /exec).
 * 9. En Streamlit Cloud ➔ App Settings ➔ Secrets, configura:
 *    gsheets_url = "URL_DE_TU_WEB_APP"
 * ====================================================================
 */

const SPREADSHEET_ID = "1dpA2Nnk9dZ_NVkhJD1HHRBN4CH6Ry8bzm2Iuf_oXV8Y";
const TARGET_SHEET_NAME = "Base_de_Datos";

const OFFICIAL_HEADERS = [
  "proyecto_id", "unidad_nombre", "proyecto_nombre", "proyecto_estado", "proyecto_descripcion",
  "tarea_id", "tarea_nombre", "tarea_descripcion", "tarea_responsable", "tarea_estado",
  "tarea_contraparte", "tarea_pct", "tarea_fecha_creacion", "fecha_legacy", "con_alerta",
  "fecha_inicio_proy", "fecha_inicio_real", "fecha_fin_proy", "fecha_fin_real"
];

function getTargetSheet() {
  const ss = SpreadsheetApp.openById(SPREADSHEET_ID);
  let sheet = ss.getSheetByName(TARGET_SHEET_NAME);
  if (!sheet) {
    sheet = ss.getSheets()[0]; // Fallback a la primera pestaña
  }
  return sheet;
}

// GET handler: Devuelve JSON de todos los registros de la base
function doGet(e) {
  try {
    const sheet = getTargetSheet();
    const data = sheet.getDataRange().getValues();
    
    if (!data || data.length <= 1) {
      return ContentService
        .createTextOutput(JSON.stringify([]))
        .setMimeType(ContentService.MimeType.JSON);
    }
    
    const headers = data[0].map(h => String(h).trim());
    const records = [];
    
    for (let i = 1; i < data.length; i++) {
      const row = data[i];
      if (!row || row.every(cell => String(cell).trim() === "")) continue;
      
      const obj = {};
      OFFICIAL_HEADERS.forEach(h => {
        const idx = headers.indexOf(h);
        if (idx !== -1) {
          const val = row[idx];
          obj[h] = (val === null || val === undefined) ? "" : String(val).trim();
        } else {
          obj[h] = "";
        }
      });
      records.push(obj);
    }
    
    return ContentService
      .createTextOutput(JSON.stringify(records))
      .setMimeType(ContentService.MimeType.JSON);

  } catch (err) {
    return ContentService
      .createTextOutput(JSON.stringify({ status: "error", message: err.toString() }))
      .setMimeType(ContentService.MimeType.JSON);
  }
}

// POST handler: Recibe {"records": [...]} y reemplaza la hoja completa manteniendo encabezados oficiales
function doPost(e) {
  try {
    const sheet = getTargetSheet();
    let bodyData = {};
    
    if (e && e.postData && e.postData.contents) {
      bodyData = JSON.parse(e.postData.contents);
    }
    
    const records = bodyData.records || bodyData.data || (Array.isArray(bodyData) ? bodyData : []);
    
    if (!Array.isArray(records)) {
      return ContentService
        .createTextOutput(JSON.stringify({ status: "error", message: "Payload invalido: 'records' debe ser una lista." }))
        .setMimeType(ContentService.MimeType.JSON);
    }
    
    // Limpiar hoja actual
    sheet.clear();
    
    // Construir matriz de filas iniciando con encabezados oficiales
    const rows = [OFFICIAL_HEADERS];
    records.forEach(r => {
      const row = OFFICIAL_HEADERS.map(h => {
        const val = r[h];
        return (val === null || val === undefined) ? "" : String(val).trim();
      });
      rows.push(row);
    });
    
    // Escribir en un solo bloque A1
    sheet.getRange(1, 1, rows.length, OFFICIAL_HEADERS.length).setValues(rows);
    
    return ContentService
      .createTextOutput(JSON.stringify({
        status: "success",
        message: "Base de datos actualizada exitosamente en Google Sheets.",
        count: records.length
      }))
      .setMimeType(ContentService.MimeType.JSON);

  } catch (err) {
    return ContentService
      .createTextOutput(JSON.stringify({ status: "error", message: err.toString() }))
      .setMimeType(ContentService.MimeType.JSON);
  }
}
