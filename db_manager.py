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
DEFAULT_SPREADSHEET_ID = "1dpA2Nnk9dZ_NVkhJD1HHRBN4CH6Ry8bzm2Iuf_oXV8Y"

def load_seed_data():
    """Loads seed data from data.js if central DB is empty."""
    if not os.path.exists(DATA_JS_PATH):
        return []
    try:
        with open(DATA_JS_PATH, "r", encoding="utf-8") as f:
            content = f.read()
        match = re.search(r"window\.INITIAL_DATA\s*=\s*(\[[\s\S]*?\]);", content)
        if match:
            raw_json = match.group(1)
            records = json.loads(raw_json)
            cleaned = []
            for r in records:
                obj = {}
                for h in HEADERS:
                    val = r.get(h, "")
                    obj[h] = "" if val is None else str(val).strip()
                cleaned.append(obj)
            return cleaned
    except Exception as e:
        print(f"Error reading seed data from data.js: {e}")
    return []

def get_gsheets_config():
    """Extracts Google Sheets configuration from st.secrets if available."""
    try:
        if not hasattr(st, "secrets"):
            return None, None
        secrets = st.secrets
        web_url = secrets.get("gsheets_url") or secrets.get("GAPPS_SCRIPT_URL") or secrets.get("web_app_url")
        if web_url:
            return "web_app", {"url": web_url}

        gs_secrets = secrets.get("gsheets") or secrets.get("connections", {}).get("gsheets") or secrets.get("google_sheets")
        if gs_secrets and isinstance(gs_secrets, dict):
            if "web_app_url" in gs_secrets:
                return "web_app", {"url": gs_secrets["web_app_url"]}
            if "client_email" in gs_secrets and "private_key" in gs_secrets:
                return "service_account", gs_secrets
    except Exception:
        pass

    return None, None

def _get_gspread_client(sa_config):
    import gspread
    from google.oauth2.service_account import Credentials

    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    sa_info = dict(sa_config)
    # Ensure private key formatting
    if "private_key" in sa_info:
        sa_info["private_key"] = sa_info["private_key"].replace("\\n", "\n")

    creds = Credentials.from_service_account_info(sa_info, scopes=scopes)
    return gspread.authorize(creds)

def _load_from_gsheets_sa(sa_config):
    client = _get_gspread_client(sa_config)
    sheet_target = sa_config.get("spreadsheet") or sa_config.get("spreadsheet_url") or sa_config.get("spreadsheet_id") or DEFAULT_SPREADSHEET_ID

    if sheet_target.startswith("http://") or sheet_target.startswith("https://"):
        sh = client.open_by_url(sheet_target)
    else:
        sh = client.open_by_key(sheet_target) if len(sheet_target) > 20 else client.open(sheet_target)

    worksheet = sh.sheet1
    all_values = worksheet.get_all_values()

    if not all_values or len(all_values) <= 1:
        # Sheet is empty, seed it
        seed = load_seed_data()
        if seed:
            _save_to_gsheets_sa(sa_config, seed)
            return seed
        return []

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

    return records

def _save_to_gsheets_sa(sa_config, records):
    client = _get_gspread_client(sa_config)
    sheet_target = sa_config.get("spreadsheet") or sa_config.get("spreadsheet_url") or sa_config.get("spreadsheet_id") or DEFAULT_SPREADSHEET_ID

    if sheet_target.startswith("http://") or sheet_target.startswith("https://"):
        sh = client.open_by_url(sheet_target)
    else:
        sh = client.open_by_key(sheet_target) if len(sheet_target) > 20 else client.open(sheet_target)

    worksheet = sh.sheet1
    
    rows = [HEADERS]
    for r in records:
        row = [str(r.get(h, "")) for h in HEADERS]
        rows.append(row)

    worksheet.clear()
    worksheet.update("A1", rows)

def _load_from_gsheets_webapp(url):
    import requests
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    if isinstance(data, list):
        if len(data) == 0:
            seed = load_seed_data()
            if seed:
                _save_to_gsheets_webapp(url, seed)
                return seed
            return []
        cleaned = []
        for r in data:
            obj = {h: str(r.get(h, "")).strip() for h in HEADERS}
            cleaned.append(obj)
        return cleaned
    return []

def _save_to_gsheets_webapp(url, records):
    import requests
    payload = {"records": records}
    resp = requests.post(url, json=payload, timeout=15)
    resp.raise_for_status()

# ---------------------------------------------------------
# SQLite Local Fallback (For local dev only)
# ---------------------------------------------------------
def _init_sqlite_db():
    conn = sqlite3.connect(SQLITE_DB_PATH)
    cursor = conn.cursor()
    columns_def = ", ".join([f"{h} TEXT" for h in HEADERS])
    cursor.execute(f"CREATE TABLE IF NOT EXISTS proyectos_tareas ({columns_def})")
    conn.commit()
    
    cursor.execute("SELECT COUNT(*) FROM proyectos_tareas")
    count = cursor.fetchone()[0]
    if count == 0:
        seed = load_seed_data()
        if seed:
            _save_to_sqlite(seed)
    conn.close()

def _load_from_sqlite():
    _init_sqlite_db()
    conn = sqlite3.connect(SQLITE_DB_PATH)
    cursor = conn.cursor()
    cursor.execute(f"SELECT {', '.join(HEADERS)} FROM proyectos_tareas")
    rows = cursor.fetchall()
    conn.close()

    records = []
    for r in rows:
        obj = {HEADERS[i]: "" if r[i] is None else str(r[i]).strip() for i in range(len(HEADERS))}
        records.append(obj)

    return records

def _save_to_sqlite(records):
    conn = sqlite3.connect(SQLITE_DB_PATH)
    cursor = conn.cursor()
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
    Returns dict:
      {
        "status": "ok" | "warning" | "error",
        "message": str,
        "source": "google_sheets" | "sqlite_local_dev",
        "data": list of record dicts
      }
    """
    config_type, config_data = get_gsheets_config()

    if config_type == "service_account":
        try:
            records = _load_from_gsheets_sa(config_data)
            return {
                "status": "ok",
                "message": "Datos cargados exitosamente desde Google Sheets (Service Account).",
                "source": "google_sheets",
                "data": records
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error al conectar con Google Sheets: {e}",
                "source": "google_sheets",
                "data": []
            }

    elif config_type == "web_app":
        try:
            records = _load_from_gsheets_webapp(config_data["url"])
            return {
                "status": "ok",
                "message": "Datos cargados exitosamente desde Google Sheets (Web App).",
                "source": "google_sheets",
                "data": records
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error al conectar con Google Sheets Web App: {e}",
                "source": "google_sheets",
                "data": []
            }

    # No Google Sheets secret configured
    # Check if running in Streamlit Cloud / Hosted production environment
    is_streamlit_cloud = bool(os.environ.get("STREAMLIT_SERVER_PORT") or os.environ.get("IS_STREAMLIT_CLOUD"))

    if is_streamlit_cloud:
        return {
            "status": "warning",
            "message": "Configuración incompleta: No se detectaron credenciales de Google Sheets en st.secrets para el entorno de producción. La persistencia multiusuario requiere configurar Google Sheets.",
            "source": "none",
            "data": []
        }
    else:
        # Local development fallback
        try:
            records = _load_from_sqlite()
            return {
                "status": "ok",
                "message": "Modo Desarrollo Local: Utilizando SQLite local consola_enjoy.db (No apto para producción multiusuario).",
                "source": "sqlite_local_dev",
                "data": records
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error al cargar base local SQLite: {e}",
                "source": "sqlite_local_dev",
                "data": []
            }

def save_central_data(records):
    """
    Main entrypoint to save data to central DB.
    Returns dict:
      {
        "status": "ok" | "error",
        "message": str,
        "data": list of saved record dicts
      }
    """
    if not isinstance(records, list):
        return {"status": "error", "message": "Los datos recibidos deben ser una lista de registros.", "data": []}

    config_type, config_data = get_gsheets_config()

    if config_type == "service_account":
        try:
            _save_to_gsheets_sa(config_data, records)
            return {"status": "ok", "message": "Base de datos guardada exitosamente en Google Sheets.", "data": records}
        except Exception as e:
            return {"status": "error", "message": f"Error al guardar en Google Sheets: {e}", "data": []}

    elif config_type == "web_app":
        try:
            _save_to_gsheets_webapp(config_data["url"], records)
            return {"status": "ok", "message": "Base de datos guardada exitosamente en Google Sheets (Web App).", "data": records}
        except Exception as e:
            return {"status": "error", "message": f"Error al guardar en Google Sheets Web App: {e}", "data": []}

    # Fallback to local SQLite if not production
    is_streamlit_cloud = bool(os.environ.get("STREAMLIT_SERVER_PORT") or os.environ.get("IS_STREAMLIT_CLOUD"))

    if is_streamlit_cloud:
        return {
            "status": "error",
            "message": "Configuración incompleta: Imposible guardar. Configure las credenciales de Google Sheets en st.secrets.",
            "data": []
        }
    else:
        try:
            _save_to_sqlite(records)
            return {"status": "ok", "message": "Base de datos guardada localmente en SQLite.", "data": records}
        except Exception as e:
            return {"status": "error", "message": f"Error al guardar en SQLite local: {e}", "data": []}
