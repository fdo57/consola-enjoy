import os
import json
import sqlite3
import re
import streamlit as st

HEADERS = [
    "proyecto_id", "unidad_nombre", "proyecto_nombre", "proyecto_estado", "proyecto_descripcion",
    "tarea_id", "tarea_nombre", "tarea_descripcion", "tarea_responsable", "tarea_estado",
    "tarea_contraparte", "tarea_pct", "tarea_fecha_creacion", "fecha_legacy", "con_alerta",
    "fecha_inicio_proy", "fecha_inicio_real", "fecha_fin_proy", "fecha_fin_real"
]

DIR_PATH = os.path.dirname(os.path.abspath(__file__))
SQLITE_DB_PATH = os.path.join(DIR_PATH, "consola_enjoy.db")
DATA_JS_PATH = os.path.join(DIR_PATH, "data.js")
OFFICIAL_SPREADSHEET_ID = "1dpA2Nnk9dZ_NVkhJD1HHRBN4CH6Ry8bzm2Iuf_oXV8Y"

def extract_spreadsheet_id(target):
    """Parses a spreadsheet URL or raw string to get the 44-character ID."""
    if not target:
        return OFFICIAL_SPREADSHEET_ID
    s = str(target).strip()
    match = re.search(r"/d/([a-zA-Z0-9-_]+)", s)
    if match:
        return match.group(1)
    if len(s) >= 25 and not s.startswith("http"):
        return s
    return OFFICIAL_SPREADSHEET_ID

def get_spreadsheet_id(config_data=None):
    """Determines the target Google Spreadsheet ID from st.secrets or fallback to official ID."""
    try:
        if hasattr(st, "secrets"):
            secrets = st.secrets
            top_target = secrets.get("spreadsheet_id") or secrets.get("spreadsheet") or secrets.get("spreadsheet_url")
            if top_target:
                return extract_spreadsheet_id(top_target)

            gs = secrets.get("gsheets") or secrets.get("connections", {}).get("gsheets") or secrets.get("google_sheets")
            if isinstance(gs, dict):
                gs_target = gs.get("spreadsheet_id") or gs.get("spreadsheet") or gs.get("spreadsheet_url")
                if gs_target:
                    return extract_spreadsheet_id(gs_target)
    except Exception:
        pass

    if config_data and isinstance(config_data, dict):
        cfg_target = config_data.get("spreadsheet_id") or config_data.get("spreadsheet") or config_data.get("spreadsheet_url")
        if cfg_target:
            return extract_spreadsheet_id(cfg_target)

    return OFFICIAL_SPREADSHEET_ID

def get_gsheets_config():
    """Extracts Google Sheets configuration from st.secrets if available."""
    try:
        if not hasattr(st, "secrets"):
            return None, None
        secrets = st.secrets

        # 1. Service account nested config
        gs_secrets = secrets.get("gsheets") or secrets.get("connections", {}).get("gsheets") or secrets.get("google_sheets")
        if gs_secrets and isinstance(gs_secrets, dict):
            if "client_email" in gs_secrets and "private_key" in gs_secrets:
                return "service_account", gs_secrets
            if "web_app_url" in gs_secrets:
                return "web_app", {"url": gs_secrets["web_app_url"]}

        # 2. Service account at root level
        if secrets.get("client_email") and secrets.get("private_key"):
            return "service_account", dict(secrets)

        # 3. Web App URL at root level
        web_url = secrets.get("gsheets_url") or secrets.get("GAPPS_SCRIPT_URL") or secrets.get("web_app_url")
        if web_url:
            return "web_app", {"url": web_url}
    except Exception as e:
        print(f"Error reading st.secrets: {e}")

    return None, None

def _get_gspread_client(sa_config):
    import gspread
    from google.oauth2.service_account import Credentials

    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    sa_info = dict(sa_config)
    if "private_key" in sa_info and isinstance(sa_info["private_key"], str):
        sa_info["private_key"] = sa_info["private_key"].replace("\\n", "\n")

    creds = Credentials.from_service_account_info(sa_info, scopes=scopes)
    return gspread.authorize(creds)

def _load_from_gsheets_sa(sa_config):
    client = _get_gspread_client(sa_config)
    sheet_id = get_spreadsheet_id(sa_config)

    sh = client.open_by_key(sheet_id)
    worksheet = sh.sheet1
    all_values = worksheet.get_all_values()

    if not all_values or len(all_values) <= 1:
        return [], sheet_id

    headers = [str(h).strip() for h in all_values[0]]
    records = []
    for row in all_values[1:]:
        if not any(row):
            continue
        obj = {}
        for h in HEADERS:
            if h in headers:
                idx = headers.index(h)
                val = row[idx] if idx < len(row) else ""
                obj[h] = "" if val is None else str(val).strip()
            else:
                obj[h] = ""
        records.append(obj)

    return records, sheet_id

def _save_to_gsheets_sa(sa_config, records):
    client = _get_gspread_client(sa_config)
    sheet_id = get_spreadsheet_id(sa_config)

    sh = client.open_by_key(sheet_id)
    worksheet = sh.sheet1

    rows = [HEADERS]
    for r in records:
        row = [str(r.get(h, "")) for h in HEADERS]
        rows.append(row)

    worksheet.clear()
    worksheet.update("A1", rows)

def _load_from_gsheets_webapp(url):
    import requests
    sheet_id = get_spreadsheet_id()
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    
    cleaned = []
    raw_list = []
    if isinstance(data, list):
        raw_list = data
    elif isinstance(data, dict) and "data" in data and isinstance(data["data"], list):
        raw_list = data["data"]

    for r in raw_list:
        obj = {h: str(r.get(h, "")).strip() for h in HEADERS}
        cleaned.append(obj)

    return cleaned, sheet_id

def _save_to_gsheets_webapp(url, records):
    import requests
    payload = {"records": records}
    resp = requests.post(url, json=payload, timeout=15)
    resp.raise_for_status()

# ---------------------------------------------------------
# SQLite Local Fallback (Only for local dev without st.secrets)
# ---------------------------------------------------------
def _load_from_sqlite():
    if not os.path.exists(SQLITE_DB_PATH):
        return []
    conn = sqlite3.connect(SQLITE_DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute(f"SELECT {', '.join(HEADERS)} FROM proyectos_tareas")
        rows = cursor.fetchall()
        conn.close()
        records = []
        for r in rows:
            obj = {HEADERS[i]: "" if r[i] is None else str(r[i]).strip() for i in range(len(HEADERS))}
            records.append(obj)
        return records
    except Exception:
        conn.close()
        return []

def _save_to_sqlite(records):
    conn = sqlite3.connect(SQLITE_DB_PATH)
    cursor = conn.cursor()
    columns_def = ", ".join([f"{h} TEXT" for h in HEADERS])
    cursor.execute(f"CREATE TABLE IF NOT EXISTS proyectos_tareas ({columns_def})")
    cursor.execute("DELETE FROM proyectos_tareas")

    placeholders = ", ".join(["?"] * len(HEADERS))
    query = f"INSERT INTO proyectos_tareas ({', '.join(HEADERS)}) VALUES ({placeholders})"

    data_tuples = []
    for r in records:
        tup = tuple(str(r.get(h, "")).strip() for h in HEADERS)
        data_tuples.append(tup)

    cursor.executemany(query, data_tuples)
    conn.commit()
    conn.close()

# ---------------------------------------------------------
# Public API
# ---------------------------------------------------------
def load_central_data():
    """
    Main entrypoint to load data from central DB.
    Guarantees no fallbacks to old seed data or SQLite in production.
    """
    config_type, config_data = get_gsheets_config()
    sheet_id = get_spreadsheet_id(config_data)

    if config_type == "service_account":
        try:
            records, active_sheet_id = _load_from_gsheets_sa(config_data)
            return {
                "status": "ok",
                "message": f"Cargados {len(records)} registros desde Google Sheets (Service Account).",
                "source": "google_sheets_service_account",
                "spreadsheet_id": active_sheet_id,
                "row_count": len(records),
                "data": records
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error al conectar con Google Sheets (Service Account): {e}",
                "source": "google_sheets_service_account",
                "spreadsheet_id": sheet_id,
                "row_count": 0,
                "data": []
            }

    elif config_type == "web_app":
        try:
            records, active_sheet_id = _load_from_gsheets_webapp(config_data["url"])
            return {
                "status": "ok",
                "message": f"Cargados {len(records)} registros desde Google Sheets (Web App).",
                "source": "google_sheets_web_app",
                "spreadsheet_id": active_sheet_id,
                "row_count": len(records),
                "data": records
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error al conectar con Google Sheets Web App: {e}",
                "source": "google_sheets_web_app",
                "spreadsheet_id": sheet_id,
                "row_count": 0,
                "data": []
            }

    # Check if running in hosted/production environment
    is_hosted = bool(
        os.environ.get("STREAMLIT_SERVER_PORT") or 
        os.environ.get("IS_STREAMLIT_CLOUD") or 
        os.environ.get("STREAMLIT_SHARING_MODE") or
        hasattr(st, "secrets")
    )

    if is_hosted:
        return {
            "status": "warning",
            "message": "Sin credenciales en st.secrets: Configure Google Sheets en st.secrets de Streamlit Cloud para conectar la BD central oficial.",
            "source": "desconectado_produccion",
            "spreadsheet_id": sheet_id,
            "row_count": 0,
            "data": []
        }
    else:
        # Local development only when st.secrets is absent
        records = _load_from_sqlite()
        return {
            "status": "ok",
            "message": f"Modo Desarrollo Local: Utilizando SQLite local (consola_enjoy.db) con {len(records)} filas.",
            "source": "sqlite_local_dev",
            "spreadsheet_id": sheet_id,
            "row_count": len(records),
            "data": records
        }

def save_central_data(records):
    """Main entrypoint to save data to central DB."""
    if not isinstance(records, list):
        return {"status": "error", "message": "Los datos deben ser una lista.", "data": []}

    config_type, config_data = get_gsheets_config()
    sheet_id = get_spreadsheet_id(config_data)

    if config_type == "service_account":
        try:
            _save_to_gsheets_sa(config_data, records)
            return {"status": "ok", "message": "Guardado exitosamente en Google Sheets.", "spreadsheet_id": sheet_id, "data": records}
        except Exception as e:
            return {"status": "error", "message": f"Error al guardar en Google Sheets: {e}", "spreadsheet_id": sheet_id, "data": []}

    elif config_type == "web_app":
        try:
            _save_to_gsheets_webapp(config_data["url"], records)
            return {"status": "ok", "message": "Guardado exitosamente en Google Sheets (Web App).", "spreadsheet_id": sheet_id, "data": records}
        except Exception as e:
            return {"status": "error", "message": f"Error al guardar en Web App: {e}", "spreadsheet_id": sheet_id, "data": []}

    is_hosted = bool(
        os.environ.get("STREAMLIT_SERVER_PORT") or 
        os.environ.get("IS_STREAMLIT_CLOUD") or 
        os.environ.get("STREAMLIT_SHARING_MODE") or
        hasattr(st, "secrets")
    )

    if is_hosted:
        return {"status": "error", "message": "Imposible guardar: Configure st.secrets en Streamlit Cloud.", "spreadsheet_id": sheet_id, "data": []}
    else:
        _save_to_sqlite(records)
        return {"status": "ok", "message": "Guardado localmente en SQLite.", "spreadsheet_id": sheet_id, "data": records}
