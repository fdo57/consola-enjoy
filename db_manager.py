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
    """Extract Google Sheets configuration from st.secrets.

    Priority:
    1) Service Account in [gsheets] with spreadsheet_id/client_email/private_key.
    2) Service Account in other supported secret blocks.
    3) Apps Script Web App URL as fallback only.
    """
    try:
        if not hasattr(st, "secrets"):
            return None, None
        secrets = st.secrets

        def as_dict(value):
            try:
                return dict(value) if value is not None else None
            except Exception:
                return value if isinstance(value, dict) else None

        def valid_sa(d):
            return isinstance(d, dict) and bool(d.get("client_email")) and bool(d.get("private_key"))

        # 1. Main supported format: [gsheets]
        gsheets = as_dict(secrets.get("gsheets"))
        if valid_sa(gsheets):
            cfg = dict(gsheets)
            cfg["spreadsheet_id"] = cfg.get("spreadsheet_id") or cfg.get("spreadsheet") or cfg.get("spreadsheet_url") or OFFICIAL_SPREADSHEET_ID
            return "service_account", cfg

        # 2. Alternative service account blocks
        for key in ("google_sheets", "gcp_service_account", "service_account"):
            cand = as_dict(secrets.get(key))
            if valid_sa(cand):
                cfg = dict(cand)
                cfg["spreadsheet_id"] = cfg.get("spreadsheet_id") or cfg.get("spreadsheet") or cfg.get("spreadsheet_url") or OFFICIAL_SPREADSHEET_ID
                return "service_account", cfg

        google = as_dict(secrets.get("google"))
        if isinstance(google, dict):
            cand = as_dict(google.get("service_account"))
            if valid_sa(cand):
                cfg = dict(cand)
                cfg["spreadsheet_id"] = cfg.get("spreadsheet_id") or cfg.get("spreadsheet") or cfg.get("spreadsheet_url") or OFFICIAL_SPREADSHEET_ID
                return "service_account", cfg

        # 3. Root-level service account fields, if used
        root_sa = {
            "spreadsheet_id": secrets.get("spreadsheet_id") or secrets.get("spreadsheet") or OFFICIAL_SPREADSHEET_ID,
            "client_email": secrets.get("client_email"),
            "private_key": secrets.get("private_key"),
        }
        if valid_sa(root_sa):
            return "service_account", root_sa

        # 4. Web App URL fallback only
        web_url = secrets.get("gsheets_url") or secrets.get("GAPPS_SCRIPT_URL") or secrets.get("web_app_url")
        if not web_url and isinstance(gsheets, dict):
            web_url = gsheets.get("web_app_url") or gsheets.get("url") or gsheets.get("gsheets_url")
        if web_url:
            return "web_app", {"url": web_url, "spreadsheet_id": OFFICIAL_SPREADSHEET_ID}

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

    sa_info = dict(sa_config.get("raw_section") or sa_config)

    # Streamlit secrets may contain only the minimal service-account fields.
    # google.oauth2.service_account.Credentials requires token_uri and type.
    sa_info.setdefault("type", "service_account")
    sa_info.setdefault("token_uri", "https://oauth2.googleapis.com/token")

    # Remove app-only aliases that are not part of Google service account JSON.
    sa_info.pop("spreadsheet_id", None)
    sa_info.pop("spreadsheet", None)
    sa_info.pop("spreadsheet_url", None)
    sa_info.pop("raw_section", None)
    
    # Process private_key string escaping
    private_key = sa_info.get("private_key", "")
    if isinstance(private_key, str):
        sa_info["private_key"] = private_key.replace("\\n", "\n")

    creds = Credentials.from_service_account_info(sa_info, scopes=scopes)
    return gspread.authorize(creds)

def _load_from_gsheets_sa(sa_config):
    client = _get_gspread_client(sa_config)
    sheet_id = sa_config.get("spreadsheet_id") or OFFICIAL_SPREADSHEET_ID

    sh = client.open_by_key(sheet_id)
    try:
        worksheet = sh.worksheet("Base_de_Datos")
    except Exception:
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

def _load_from_sqlite_dev():
    if not os.path.exists(SQLITE_DB_PATH):
        return [], OFFICIAL_SPREADSHEET_ID
    try:
        conn = sqlite3.connect(SQLITE_DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM proyectos_tareas")
        rows = cursor.fetchall()
        records = []
        for r in rows:
            obj = {h: str(r[h] if r[h] is not None else "").strip() for h in HEADERS if h in r.keys()}
            records.append(obj)
        conn.close()
        return records, OFFICIAL_SPREADSHEET_ID
    except Exception as e:
        print(f"Error loading from sqlite dev: {e}")
        return [], OFFICIAL_SPREADSHEET_ID

# ---------------------------------------------------------
# Public API
# ---------------------------------------------------------
def load_central_data():
    """
    Main entrypoint to load data from central DB.
    Prioritizes Service Account and returns google_sheets_service_account source.
    Rejects sqlite_local_dev fallback in production.
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
            return {
                "status": "error",
                "message": f"Error al conectar con Google Sheets vía Service Account: {e}",
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

    # Fallback to local SQLite DB if Google Sheets credentials are not provided
    sqlite_records, active_sheet_id = _load_from_sqlite_dev()

    if is_streamlit_env and not sqlite_records:
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
            "status": "ok" if sqlite_records else "warning",
            "message": "Datos cargados desde base local de desarrollo (SQLite).",
            "source": "sqlite_local_dev",
            "spreadsheet_id": active_sheet_id,
            "row_count": len(sqlite_records),
            "data": sqlite_records
        }

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
            return {"status": "error", "message": f"Error al guardar en Google Sheets: {e}", "spreadsheet_id": sheet_id, "data": []}

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
