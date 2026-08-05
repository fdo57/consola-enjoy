import os
import json
import sqlite3
import re
import time
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

def _execute_with_backoff(func, *args, **kwargs):
    """
    Executes a function with exponential backoff for HTTP 429 / Rate Limit / Quota Exceeded errors.
    Delays: 2s, 5s, 10s.
    """
    delays = [2, 5, 10]
    for attempt in range(len(delays) + 1):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            err_str = str(e).lower()
            is_429 = "429" in err_str or "quota" in err_str or "resource_exhausted" in err_str or "too many requests" in err_str
            if is_429 and attempt < len(delays):
                time.sleep(delays[attempt])
            else:
                raise e

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
    Priority:
    1. Service Account ([gsheets], [google_sheets], [connections.gsheets] or root)
    2. Web App URL (gsheets_url / GAPPS_SCRIPT_URL / web_app_url) as fallback
    """
    secrets = get_st_secrets_dict()
    if not secrets:
        return None, {"missing": ["gsheets.client_email", "gsheets.private_key", "gsheets.spreadsheet_id"]}

    gs_section = None
    if "gsheets" in secrets and isinstance(secrets["gsheets"], dict):
        gs_section = secrets["gsheets"]
    elif "google_sheets" in secrets and isinstance(secrets["google_sheets"], dict):
        gs_section = secrets["google_sheets"]
    elif "connections" in secrets and isinstance(secrets["connections"], dict) and "gsheets" in secrets["connections"] and isinstance(secrets["connections"]["gsheets"], dict):
        gs_section = secrets["connections"]["gsheets"]
    elif "service_account" in secrets and isinstance(secrets["service_account"], dict):
        gs_section = secrets["service_account"]
    elif "client_email" in secrets or "private_key" in secrets:
        gs_section = dict(secrets)

    # 1. Primary Method: Evaluate Service Account
    if gs_section is not None:
        missing = []
        spreadsheet_id = gs_section.get("spreadsheet_id") or gs_section.get("spreadsheet") or gs_section.get("spreadsheet_url") or secrets.get("spreadsheet_id") or OFFICIAL_SPREADSHEET_ID
        client_email = gs_section.get("client_email")
        private_key = gs_section.get("private_key")

        if not spreadsheet_id:
            missing.append("gsheets.spreadsheet_id")
        if not client_email:
            missing.append("gsheets.client_email")
        if not private_key:
            missing.append("gsheets.private_key")

        active_sheet_id = extract_spreadsheet_id(spreadsheet_id)

        if missing:
            return "service_account_error", {
                "missing": missing,
                "spreadsheet_id": active_sheet_id
            }

        return "service_account", {
            "client_email": client_email,
            "private_key": private_key,
            "spreadsheet_id": active_sheet_id,
            "raw_section": gs_section
        }

    # 2. Fallback Method: Web App URL
    web_url = secrets.get("gsheets_url") or secrets.get("GAPPS_SCRIPT_URL") or secrets.get("web_app_url") or secrets.get("url")
    if web_url and isinstance(web_url, str):
        return "web_app", {"url": web_url, "spreadsheet_id": OFFICIAL_SPREADSHEET_ID}

    return None, {"missing": ["gsheets.client_email", "gsheets.private_key", "gsheets.spreadsheet_id"], "spreadsheet_id": OFFICIAL_SPREADSHEET_ID}

def _get_gspread_client(sa_config):
    import gspread
    from google.oauth2.service_account import Credentials

    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    sa_info = dict(sa_config.get("raw_section") or sa_config)
    sa_info.setdefault("type", "service_account")
    sa_info.setdefault("token_uri", "https://oauth2.googleapis.com/token")

    sa_info.pop("spreadsheet_id", None)
    sa_info.pop("spreadsheet", None)
    sa_info.pop("spreadsheet_url", None)
    sa_info.pop("raw_section", None)

    private_key = sa_info.get("private_key", "")
    if isinstance(private_key, str):
        sa_info["private_key"] = private_key.replace("\\n", "\n")

    creds = Credentials.from_service_account_info(sa_info, scopes=scopes)
    return gspread.authorize(creds)

def _load_from_gsheets_sa(sa_config):
    def _do_load():
        client = _get_gspread_client(sa_config)
        sheet_id = sa_config.get("spreadsheet_id") or OFFICIAL_SPREADSHEET_ID
        sh = client.open_by_key(sheet_id)
        try:
            worksheet = sh.worksheet("Base_de_Datos")
        except Exception:
            worksheet = sh.sheet1
        return worksheet.get_all_values(), sheet_id

    all_values, sheet_id = _execute_with_backoff(_do_load)

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
    def _do_save():
        client = _get_gspread_client(sa_config)
        sheet_id = sa_config.get("spreadsheet_id") or OFFICIAL_SPREADSHEET_ID
        sh = client.open_by_key(sheet_id)
        try:
            worksheet = sh.worksheet("Base_de_Datos")
        except Exception:
            worksheet = sh.sheet1

        rows = [HEADERS]
        for r in records:
            row = [str(r.get(h, "")) for h in HEADERS]
            rows.append(row)

        worksheet.clear()
        worksheet.update("A1", rows)

    _execute_with_backoff(_do_save)

def _load_from_gsheets_webapp(url):
    import requests
    sheet_id = get_spreadsheet_id()
    
    def _do_get():
        resp = requests.get(url, allow_redirects=True, timeout=15)
        resp.raise_for_status()
        return resp.json()

    data = _execute_with_backoff(_do_get)

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
    
    def _do_post():
        resp = requests.post(url, data=json.dumps(payload), headers=headers, allow_redirects=True, timeout=25)
        resp.raise_for_status()
        return resp.json()

    result = _execute_with_backoff(_do_post)
    if isinstance(result, dict) and result.get("status") == "error":
        raise Exception(result.get("message", "Error reportado por Google Apps Script Web App"))

# ---------------------------------------------------------
# Public API
# ---------------------------------------------------------
def load_central_data():
    """
    Main entrypoint to load data from central DB.
    Prioritizes Service Account and returns google_sheets_service_account source.
    """
    config_type, config_data = get_gsheets_config()
    sheet_id = config_data.get("spreadsheet_id", OFFICIAL_SPREADSHEET_ID) if isinstance(config_data, dict) else OFFICIAL_SPREADSHEET_ID

    if config_type == "service_account":
        try:
            records, active_sheet_id = _load_from_gsheets_sa(config_data)
            return {
                "status": "ok",
                "message": "Conexión exitosa a Google Sheets vía Service Account.",
                "source": "google_sheets_service_account",
                "spreadsheet_id": active_sheet_id,
                "row_count": len(records),
                "data": records
            }
        except Exception as e:
            err_msg = str(e)
            if "429" in err_msg or "quota" in err_msg.lower():
                err_msg = "Límite de cuota alcanzado en Google Sheets (Error 429). Por favor espere un momento antes de recargar."
            return {
                "status": "error",
                "message": f"Error al conectar con Google Sheets vía Service Account: {err_msg}",
                "source": "google_sheets_service_account",
                "spreadsheet_id": sheet_id,
                "row_count": 0,
                "data": []
            }

    elif config_type == "service_account_error":
        missing_list = config_data.get("missing", [])
        missing_str = ", ".join(missing_list)
        return {
            "status": "error",
            "message": f"Falta el campo requerido en st.secrets: {missing_str}",
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
                "message": "Conexión exitosa a Google Sheets vía Web App.",
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

    # Production environment check
    is_streamlit_env = False
    try:
        import streamlit.runtime as st_runtime
        is_streamlit_env = st_runtime.exists()
    except Exception:
        is_streamlit_env = hasattr(st, "secrets")

    if is_streamlit_env:
        missing_list = config_data.get("missing", ["gsheets.client_email", "gsheets.private_key", "gsheets.spreadsheet_id"]) if isinstance(config_data, dict) else ["gsheets.client_email", "gsheets.private_key", "gsheets.spreadsheet_id"]
        missing_str = ", ".join(missing_list)
        return {
            "status": "error",
            "message": f"Falta el campo requerido en st.secrets: {missing_str}",
            "source": "google_sheets_service_account",
            "spreadsheet_id": OFFICIAL_SPREADSHEET_ID,
            "row_count": 0,
            "data": []
        }
    else:
        return {
            "status": "error",
            "message": "Sin credenciales de Google Sheets configuradas en entorno local.",
            "source": "sqlite_local_dev",
            "spreadsheet_id": OFFICIAL_SPREADSHEET_ID,
            "row_count": 0,
            "data": []
        }

@st.cache_data(ttl=60, show_spinner=False)
def fetch_central_data_cached():
    """
    Cached reader for Google Sheets data (TTL 60s).
    Prevents repetitive 429 API quota calls across multiple Streamlit reruns.
    """
    return load_central_data()

def save_central_data(records):
    """
    Main entrypoint to save data to central DB.
    Prioritizes Service Account. Rejects saving if active source is not google_sheets_service_account or web_app.
    """
    if not isinstance(records, list):
        return {"status": "error", "message": "Los datos deben ser una lista.", "data": []}

    config_type, config_data = get_gsheets_config()
    sheet_id = config_data.get("spreadsheet_id", OFFICIAL_SPREADSHEET_ID) if isinstance(config_data, dict) else OFFICIAL_SPREADSHEET_ID

    if config_type == "service_account":
        try:
            _save_to_gsheets_sa(config_data, records)
            return {"status": "ok", "message": "Guardado exitoso en Google Sheets vía Service Account.", "spreadsheet_id": sheet_id, "data": records}
        except Exception as e:
            err_msg = str(e)
            if "429" in err_msg or "quota" in err_msg.lower():
                err_msg = "Límite de cuota alcanzado en Google Sheets (Error 429). Espere unos segundos."
            return {"status": "error", "message": f"Error al guardar en Google Sheets: {err_msg}", "spreadsheet_id": sheet_id, "data": []}

    elif config_type == "web_app":
        try:
            _save_to_gsheets_webapp(config_data["url"], records)
            return {"status": "ok", "message": "Guardado exitoso en Google Sheets (Web App).", "spreadsheet_id": sheet_id, "data": records}
        except Exception as e:
            return {"status": "error", "message": f"Error al guardar en Web App: {e}", "spreadsheet_id": sheet_id, "data": []}

    return {
        "status": "error",
        "message": "Guardado rechazado: No hay conexión activa con Service Account en st.secrets.",
        "spreadsheet_id": sheet_id,
        "data": []
    }
