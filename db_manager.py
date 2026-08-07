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

# ---------------------------------------------------------
# Helper Normalization Functions
# ---------------------------------------------------------
def _normalize_value(val):
    """Normalizes None, 'None', 'null', 'undefined', 'nan' to empty string ''."""
    if val is None:
        return ""
    s = str(val).strip()
    if s.lower() in ("none", "null", "undefined", "nan"):
        return ""
    return s

def _normalize_record_dict(rec_dict):
    """Normalizes all fields in a record dictionary to ensure no 'None' strings exist."""
    if not isinstance(rec_dict, dict):
        return {h: "" for h in HEADERS}
    obj = {}
    for h in HEADERS:
        raw_val = rec_dict.get(h)
        obj[h] = _normalize_value(raw_val)
    return obj

# ---------------------------------------------------------
# 1. PostgreSQL Production Runtime Adapter (ENJOY_DB_DSN)
# ---------------------------------------------------------
def get_pg_dsn():
    """Retrieves PostgreSQL DSN from environment variable ENJOY_DB_DSN or fallback keys."""
    dsn = os.environ.get("ENJOY_DB_DSN") or os.environ.get("DATABASE_URL")
    if not dsn:
        secrets = get_st_secrets_dict()
        if secrets:
            dsn = secrets.get("ENJOY_DB_DSN") or secrets.get("DATABASE_URL")
            if not dsn and isinstance(secrets.get("postgres"), dict):
                dsn = secrets.get("postgres", {}).get("url") or secrets.get("postgres", {}).get("dsn")
    return dsn

def _get_pg_connection():
    """Establishes connection to PostgreSQL using psycopg2, psycopg3, or SQLAlchemy."""
    dsn = get_pg_dsn()
    if not dsn:
        return None, None

    # 1. Try psycopg2
    try:
        import psycopg2
        return psycopg2.connect(dsn), dsn
    except Exception:
        pass

    # 2. Try psycopg (psycopg 3)
    try:
        import psycopg
        return psycopg.connect(dsn), dsn
    except Exception:
        pass

    # 3. Try sqlalchemy raw connection
    try:
        from sqlalchemy import create_engine
        engine = create_engine(dsn)
        return engine.raw_connection(), dsn
    except Exception:
        pass

    return None, dsn

def _load_from_postgresql(custom_conn=None):
    """Loads all records from PostgreSQL table enjoy_records preserving JSONB with clean null normalization."""
    conn = custom_conn
    should_close = False
    if conn is None:
        conn, dsn = _get_pg_connection()
        should_close = True
        if conn is None:
            raise Exception("No se pudo conectar a PostgreSQL: driver no disponible o DSN inválido.")

    try:
        cur = conn.cursor()
        cur.execute("SELECT position, tarea_id, record, updated_at FROM enjoy_records ORDER BY position ASC, updated_at ASC;")
        rows = cur.fetchall()
        records = []
        for r in rows:
            rec_val = r[2]
            if isinstance(rec_val, str):
                try:
                    rec_dict = json.loads(rec_val)
                except Exception:
                    rec_dict = {"tarea_id": str(r[1]), "tarea_nombre": str(rec_val)}
            elif isinstance(rec_val, dict):
                rec_dict = rec_val
            else:
                rec_dict = {}

            # Ensure tarea_id from column if missing in JSON
            if not rec_dict.get("tarea_id"):
                rec_dict["tarea_id"] = str(r[1]) if r[1] is not None else ""

            normalized_obj = _normalize_record_dict(rec_dict)
            records.append(normalized_obj)
        cur.close()
        return records
    finally:
        if should_close and conn:
            conn.close()

def _save_to_postgresql(records, custom_conn=None):
    """
    Saves/upserts records into PostgreSQL enjoy_records in a single transaction.
    - Preserves existing records not included in the payload.
    - Matches by tarea_id.
    - Inserts new tasks with sequential non-conflicting position.
    - Updates existing tasks without altering their position.
    - Updates record JSONB and updated_at = NOW().
    - Never executes DELETE FROM enjoy_records.
    """
    # 1. Validation of payload
    seen_ids = set()
    for idx, r in enumerate(records):
        if not isinstance(r, dict):
            raise Exception(f"El registro en el índice {idx} no es un diccionario válido.")
        tid = str(r.get("tarea_id", "")).strip()
        if not tid or tid.lower() in ("none", "null", "undefined"):
            raise Exception(f"Rechazado: el registro en el índice {idx} tiene 'tarea_id' vacío.")
        if tid in seen_ids:
            raise Exception(f"Rechazado: 'tarea_id' duplicado en el payload recibido ('{tid}').")
        seen_ids.add(tid)

    conn = custom_conn
    should_close = False
    if conn is None:
        conn, dsn = _get_pg_connection()
        should_close = True
        if conn is None:
            raise Exception("No se pudo conectar a PostgreSQL: driver no disponible o DSN inválido.")

    try:
        with conn:
            with conn.cursor() as cur:
                # Read existing rows to map tarea_id -> position and find max_position
                try:
                    cur.execute("SELECT position, tarea_id FROM enjoy_records FOR UPDATE;")
                except Exception:
                    cur.execute("SELECT position, tarea_id FROM enjoy_records;")

                existing_rows = cur.fetchall()
                existing_positions = {}
                max_pos = -1
                for row in existing_rows:
                    pos_val = row[0]
                    tid_val = str(row[1]) if row[1] is not None else ""
                    if tid_val:
                        existing_positions[tid_val] = pos_val
                    if isinstance(pos_val, int) and pos_val > max_pos:
                        max_pos = pos_val

                # Process all records in the payload
                for r in records:
                    tid = str(r.get("tarea_id", "")).strip()
                    cleaned_record = _normalize_record_dict(r)
                    record_json = json.dumps(cleaned_record, ensure_ascii=False)

                    if tid in existing_positions:
                        # Existing task: update record and updated_at, preserving position
                        cur.execute(
                            "UPDATE enjoy_records SET record = %s, updated_at = NOW() WHERE tarea_id = %s;",
                            (record_json, tid)
                        )
                    else:
                        # New task: assign next unique position
                        max_pos += 1
                        assigned_pos = max_pos
                        cur.execute(
                            "INSERT INTO enjoy_records (position, tarea_id, record, updated_at) VALUES (%s, %s, %s, NOW());",
                            (assigned_pos, tid, record_json)
                        )
                        existing_positions[tid] = assigned_pos

        return len(records)
    finally:
        if should_close and conn:
            conn.close()

# ---------------------------------------------------------
# 2. Google Sheets Development & Backup Adapter
# ---------------------------------------------------------
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
                obj[h] = _normalize_value(val)
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
        cleaned = _normalize_record_dict(r)
        row = [str(cleaned.get(h, "")) for h in HEADERS]
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
        cleaned_obj = _normalize_record_dict(r)
        cleaned.append(cleaned_obj)

    return cleaned, sheet_id

def _save_to_gsheets_webapp(url, records):
    import requests
    sheet_id = get_spreadsheet_id()
    cleaned_records = [_normalize_record_dict(r) for r in records]
    payload = {"records": cleaned_records}
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
            raw_dict = {h: r[h] if h in r.keys() else "" for h in HEADERS}
            records.append(_normalize_record_dict(raw_dict))
        conn.close()
        return records, OFFICIAL_SPREADSHEET_ID
    except Exception as e:
        print(f"Error loading from sqlite dev: {e}")
        return [], OFFICIAL_SPREADSHEET_ID

def _save_to_sqlite_dev(records):
    try:
        conn = sqlite3.connect(SQLITE_DB_PATH)
        cursor = conn.cursor()
        for r in records:
            cleaned = _normalize_record_dict(r)
            tid = cleaned.get("tarea_id")
            cols = [h for h in HEADERS if h in cleaned]
            vals = [cleaned[h] for h in cols]
            
            cursor.execute("SELECT COUNT(*) FROM proyectos_tareas WHERE tarea_id = ?", (tid,))
            exists = cursor.fetchone()[0] > 0
            if exists:
                set_clause = ", ".join([f"{h} = ?" for h in cols])
                cursor.execute(f"UPDATE proyectos_tareas SET {set_clause} WHERE tarea_id = ?", vals + [tid])
            else:
                placeholders = ", ".join(["?"] * len(cols))
                col_names = ", ".join(cols)
                cursor.execute(f"INSERT INTO proyectos_tareas ({col_names}) VALUES ({placeholders})", vals)
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error saving to sqlite dev: {e}")
        raise e

# ---------------------------------------------------------
# Public API
# ---------------------------------------------------------
def load_central_data():
    """
    Main entrypoint to load data from central DB.
    Prioritizes PostgreSQL (ENJOY_DB_DSN) in production runtime.
    Falls back to Google Sheets (service account / web app) or SQLite in local development.
    """
    # 1. Check PostgreSQL runtime connection
    pg_dsn = get_pg_dsn()
    if pg_dsn:
        try:
            records = _load_from_postgresql()
            return {
                "status": "ok",
                "message": "Conexión exitosa a PostgreSQL enjoy_records (VPS).",
                "source": "postgresql_vps",
                "spreadsheet_id": "postgresql-vps",
                "row_count": len(records),
                "data": records
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error al conectar con PostgreSQL (ENJOY_DB_DSN): {e}",
                "source": "postgresql_vps",
                "spreadsheet_id": "postgresql-vps",
                "row_count": 0,
                "data": []
            }

    # 2. Check Google Sheets configuration (Dev / backup)
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

    # 3. Fallback to local SQLite development DB
    sqlite_records, active_sheet_id = _load_from_sqlite_dev()
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
    Prioritizes PostgreSQL (ENJOY_DB_DSN).
    Falls back to Google Sheets or SQLite dev.
    """
    if not isinstance(records, list):
        return {
            "status": "error",
            "message": "Los datos deben ser una lista.",
            "source": "desconocida",
            "data": []
        }

    # Validate empty or duplicate tarea_id before dispatching
    seen_ids = set()
    for idx, r in enumerate(records):
        if not isinstance(r, dict):
            return {
                "status": "error",
                "message": f"El registro en el índice {idx} no es un objeto válido.",
                "source": "validacion",
                "data": []
            }
        tid = str(r.get("tarea_id", "")).strip()
        if not tid or tid.lower() in ("none", "null", "undefined"):
            return {
                "status": "error",
                "message": f"Rechazado: el registro en el índice {idx} tiene 'tarea_id' vacío.",
                "source": "validacion",
                "data": []
            }
        if tid in seen_ids:
            return {
                "status": "error",
                "message": f"Rechazado: 'tarea_id' duplicado en el payload recibido ('{tid}').",
                "source": "validacion",
                "data": []
            }
        seen_ids.add(tid)

    # 1. PostgreSQL (ENJOY_DB_DSN)
    pg_dsn = get_pg_dsn()
    if pg_dsn:
        try:
            count = _save_to_postgresql(records)
            return {
                "status": "ok",
                "message": f"Guardado exitoso en PostgreSQL enjoy_records ({count} tareas procesadas).",
                "source": "postgresql_vps",
                "data": records
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error al guardar en PostgreSQL enjoy_records: {e}",
                "source": "postgresql_vps",
                "data": []
            }

    # 2. Google Sheets
    config_type, config_data = get_gsheets_config()
    sheet_id = config_data.get("spreadsheet_id", OFFICIAL_SPREADSHEET_ID) if isinstance(config_data, dict) else OFFICIAL_SPREADSHEET_ID

    if config_type == "service_account":
        try:
            _save_to_gsheets_sa(config_data, records)
            return {
                "status": "ok",
                "message": "Guardado exitoso en Google Sheets vía Service Account.",
                "source": "google_sheets_service_account",
                "spreadsheet_id": sheet_id,
                "data": records
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error al guardar en Google Sheets: {e}",
                "source": "google_sheets_service_account",
                "spreadsheet_id": sheet_id,
                "data": []
            }

    elif config_type == "web_app":
        try:
            _save_to_gsheets_webapp(config_data["url"], records)
            return {
                "status": "ok",
                "message": "Guardado exitoso en Google Sheets (Web App).",
                "source": "google_sheets_web_app",
                "spreadsheet_id": sheet_id,
                "data": records
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Error al guardar en Web App: {e}",
                "source": "google_sheets_web_app",
                "spreadsheet_id": sheet_id,
                "data": []
            }

    # 3. SQLite dev
    try:
        _save_to_sqlite_dev(records)
        return {
            "status": "ok",
            "message": "Guardado exitoso en base local de desarrollo (SQLite).",
            "source": "sqlite_local_dev",
            "data": records
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error al guardar en SQLite local: {e}",
            "source": "sqlite_local_dev",
            "data": []
        }
