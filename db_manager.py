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

def get_st_secrets_dict():
    """Safely retrieves st.secrets as a dict if available without raising StreamlitSecretNotFoundError."""
    try:
        if hasattr(st, "secrets"):
            s = st.secrets
            if len(s) > 0:
                return s
    except Exception as e:
        print(f"st.secrets access notice: {e}")
    return {}

def get_spreadsheet_id(config_data=None):
    """Determines the target Google Spreadsheet ID from st.secrets or fallback to official ID."""
    secrets = get_st_secrets_dict()
    if secrets:
        top_target = secrets.get("spreadsheet_id") or secrets.get("spreadsheet") or secrets.get("spreadsheet_url")
        if top_target:
            return extract_spreadsheet_id(top_target)

        gs = secrets.get("gsheets") or secrets.get("connections", {}).get("gsheets") or secrets.get("google_sheets")
        if isinstance(gs, dict):
            gs_target = gs.get("spreadsheet_id") or gs.get("spreadsheet") or gs.get("spreadsheet_url")
            if gs_target:
                return extract_spreadsheet_id(gs_target)

    if config_data and isinstance(config_data, dict):
        cfg_target = config_data.get("spreadsheet_id") or config_data.get("spreadsheet") or config_data.get("spreadsheet_url")
        if cfg_target:
            return extract_spreadsheet_id(cfg_target)

    return OFFICIAL_SPREADSHEET_ID

def get_gsheets_config():
    """
    Extracts Google Sheets configuration from st.secrets.
    Supports Web App (Apps Script) URLs (gsheets_url, GAPPS_SCRIPT_URL, web_app_url)
    as well as Service Account credentials.
    """
    secrets = get_st_secrets_dict()
    if not secrets:
        return None, None

    def is_sa_dict(d):
        return isinstance(d, dict) and "client_email" in d and "private_key" in d

    def get_web_url(val):
        if isinstance(val, str) and ("script.google.com" in val or "http" in val):
            return val
        if isinstance(val, dict):
            return val.get("web_app_url") or val.get("url") or val.get("GAPPS_SCRIPT_URL") or val.get("gsheets_url")
        return None

    # 1. Prioritize Web App URL (gsheets_url, GAPPS_SCRIPT_URL, web_app_url)
    web_url_candidates = [
        secrets.get("gsheets_url"),
        secrets.get("GAPPS_SCRIPT_URL"),
        secrets.get("web_app_url"),
        secrets.get("url"),
        secrets.get("gsheets"),
        secrets.get("google_sheets"),
        secrets.get("connections", {}).get("gsheets") if isinstance(secrets.get("connections"), dict) else None,
    ]
    for cand in web_url_candidates:
        url = get_web_url(cand)
        if url:
            return "web_app", {"url": url}

    # 2. Service Account in sub-dicts
    sa_candidates = [
        secrets.get("gsheets"),
        secrets.get("google_sheets"),
        secrets.get("connections", {}).get("gsheets") if isinstance(secrets.get("connections"), dict) else None,
        secrets.get("gcp_service_account"),
        secrets.get("service_account"),
        secrets.get("google", {}).get("service_account") if isinstance(secrets.get("google"), dict) else None,
    ]
    for cand in sa_candidates:
        if is_sa_dict(cand):
            return "service_account", cand

    # 3. Service Account at root level
    if is_sa_dict(secrets):
        return "service_account", dict(secrets)

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
    resp = requests.get(url, allow_redirects=True, timeout=15)
    resp.raise_for_status()
    data = resp.json()
    
    cleaned = []
    raw_list = []
    if isinstance(data, list):
        raw_list = data
    elif isinstance(data, dict):
        raw_list = data.get("records") or data.get("data") or []

    for r in raw_list:
        obj = {h: str(r.get(h, "")).strip() for h in HEADERS}
        cleaned.append(obj)

    return cleaned, sheet_id

def _save_to_gsheets_webapp(url, records):
    import requests
    sheet_id = get_spreadsheet_id()
    payload = {"records": records}
    headers = {"Content-Type": "application/json"}
    resp = requests.post(url, data=json.dumps(payload), headers=headers, allow_redirects=True, timeout=25)
    resp.raise_for_status()
    try:
        result = resp.json()
        if isinstance(result, dict) and result.get("status") == "error":
            raise Exception(result.get("message", "Error reportado por Google Apps Script Web App"))
    except Exception as e:
        if "Error reportado" in str(e):
            raise e

# ---------------------------------------------------------
# Public API
# ---------------------------------------------------------
def load_central_data():
    """
    Main entrypoint to load data from central DB.
    Guarantees 'google_sheets' source when connected via Web App or Service Account.
    Rejects sqlite_local_dev fallback in production.
    """
    config_type, config_data = get_gsheets_config()
    sheet_id = get_spreadsheet_id(config_data)

    if config_type == "web_app":
        try:
            records, active_sheet_id = _load_from_gsheets_webapp(config_data["url"])
            return {
                "status": "ok",
                "message": f"Conexión exitosa a Google Sheets (Web App). {len(records)} filas cargadas.",
                "source": "google_sheets",
                "spreadsheet_id": active_sheet_id,
                "row_count": len(records),
                "data": records
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error al conectar con Google Sheets Web App: {e}",
                "source": "google_sheets_error",
                "spreadsheet_id": sheet_id,
                "row_count": 0,
                "data": []
            }

    elif config_type == "service_account":
        try:
            records, active_sheet_id = _load_from_gsheets_sa(config_data)
            return {
                "status": "ok",
                "message": f"Conexión exitosa a Google Sheets (Service Account). {len(records)} filas cargadas.",
                "source": "google_sheets",
                "spreadsheet_id": active_sheet_id,
                "row_count": len(records),
                "data": records
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error al conectar con Google Sheets (Service Account): {e}",
                "source": "google_sheets_error",
                "spreadsheet_id": sheet_id,
                "row_count": 0,
                "data": []
            }

    # Check if running under Streamlit
    is_streamlit_env = False
    try:
        import streamlit.runtime as st_runtime
        is_streamlit_env = st_runtime.exists()
    except Exception:
        is_streamlit_env = hasattr(st, "secrets")

    if is_streamlit_env:
        return {
            "status": "error",
            "message": "Falta gsheets_url en st.secrets: Configure la URL de Google Apps Script Web App en Streamlit Cloud.",
            "source": "google_sheets_desconectado",
            "spreadsheet_id": sheet_id,
            "row_count": 0,
            "data": []
        }
    else:
        return {
            "status": "error",
            "message": "Sin credenciales gsheets_url configuradas.",
            "source": "sqlite_local_dev",
            "spreadsheet_id": sheet_id,
            "row_count": 0,
            "data": []
        }

def save_central_data(records):
    """
    Main entrypoint to save data to central DB.
    Rejects saving if active source is not google_sheets.
    """
    if not isinstance(records, list):
        return {"status": "error", "message": "Los datos deben ser una lista.", "data": []}

    config_type, config_data = get_gsheets_config()
    sheet_id = get_spreadsheet_id(config_data)

    if config_type == "web_app":
        try:
            _save_to_gsheets_webapp(config_data["url"], records)
            return {"status": "ok", "message": "Guardado exitoso en Google Sheets (Web App).", "spreadsheet_id": sheet_id, "data": records}
        except Exception as e:
            return {"status": "error", "message": f"Error al guardar en Web App: {e}", "spreadsheet_id": sheet_id, "data": []}

    elif config_type == "service_account":
        try:
            _save_to_gsheets_sa(config_data, records)
            return {"status": "ok", "message": "Guardado exitoso en Google Sheets central.", "spreadsheet_id": sheet_id, "data": records}
        except Exception as e:
            return {"status": "error", "message": f"Error al guardar en Google Sheets: {e}", "spreadsheet_id": sheet_id, "data": []}

    return {
        "status": "error",
        "message": "Guardado rechazado: La app está en producción sin conexión a Google Sheets. Configure gsheets_url en st.secrets.",
        "spreadsheet_id": sheet_id,
        "data": []
    }
