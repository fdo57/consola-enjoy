import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, date

# ---------------------------------------------------------
# PAGE CONFIG & CUSTOM STYLING
# ---------------------------------------------------------
st.set_page_config(
    page_title="Consola de Proyectos | ENJOY",
    page_icon="🏨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Executive CSS Styling
st.markdown("""
    <style>
    /* Main Theme Overrides */
    .main {
        background-color: #f8f9fa;
    }
    
    /* Sidebar Radio Customization - Large Font, No Icons */
    div[data-testid="stRadio"] label {
        padding: 10px 14px !important;
        margin-bottom: 8px !important;
        border-radius: 8px !important;
        background-color: #f1f5f9;
        border: 1px solid #cbd5e1;
        transition: all 0.2s ease-in-out;
    }
    div[data-testid="stRadio"] label:hover {
        background-color: #e2e8f0;
    }
    div[data-testid="stRadio"] label p {
        font-size: 1.25rem !important;
        font-weight: 800 !important;
        color: #0f172a !important;
        letter-spacing: 0.5px !important;
        margin: 0 !important;
    }
    div[data-testid="stRadio"] div[role="radiogroup"] label[data-checked="true"] {
        background-color: #1e293b !important;
        border-color: #0f172a !important;
    }
    div[data-testid="stRadio"] div[role="radiogroup"] label[data-checked="true"] p {
        color: #ffffff !important;
    }
    
    /* Custom Indicator Cards */
    .metric-card {
        background: white;
        border-radius: 10px;
        padding: 1rem;
        border: 1px solid #e2e8f0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.03);
        margin-bottom: 0.8rem;
    }
    .metric-card h4 {
        margin: 0 0 8px 0;
        color: #1e293b;
        font-size: 1.1rem;
        font-weight: 700;
        border-bottom: 2px solid #e2e8f0;
        padding-bottom: 6px;
    }
    
    /* Reduce row spacing between projects and tasks by 40% */
    div[data-testid="stHorizontalBlock"] {
        margin-bottom: -10px !important;
        padding-top: 0px !important;
        padding-bottom: 0px !important;
    }
    div[data-testid="element-container"] {
        margin-bottom: 2px !important;
    }
    
    /* Custom Circle Buttons Styling */
    .btn-dark-gray div.stButton > button,
    .btn-dark-gray div.stButton > button:enabled,
    .btn-dark-gray div.stButton > button[data-testid="stBaseButton-secondary"] {
        border-radius: 50% !important;
        width: 34px !important;
        height: 34px !important;
        min-width: 34px !important;
        padding: 0 !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        font-weight: 800 !important;
        font-size: 0.95rem !important;
        background-color: #1e293b !important;
        background: #1e293b !important;
        color: #ffffff !important;
        border: none !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1) !important;
    }
    .btn-dark-gray div.stButton > button:hover,
    .btn-dark-gray div.stButton > button:focus,
    .btn-dark-gray div.stButton > button:active {
        background-color: #334155 !important;
        background: #334155 !important;
        color: #ffffff !important;
    }
    .btn-dark-gray div.stButton > button p,
    .btn-dark-gray div.stButton > button span {
        color: #ffffff !important;
        font-weight: 800 !important;
    }
    
    .btn-red div.stButton > button,
    .btn-red div.stButton > button:enabled,
    .btn-red div.stButton > button[data-testid="stBaseButton-secondary"],
    .btn-red div.stButton > button[data-testid="stBaseButton-primary"] {
        border-radius: 50% !important;
        width: 34px !important;
        height: 34px !important;
        min-width: 34px !important;
        padding: 0 !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        font-weight: 800 !important;
        font-size: 0.95rem !important;
        background-color: #ef4444 !important;
        background: #ef4444 !important;
        color: #ffffff !important;
        border: none !important;
        box-shadow: 0 2px 4px rgba(239, 68, 68, 0.2) !important;
    }
    .btn-red div.stButton > button:hover,
    .btn-red div.stButton > button:focus,
    .btn-red div.stButton > button:active {
        background-color: #dc2626 !important;
        background: #dc2626 !important;
        color: #ffffff !important;
    }
    .btn-red div.stButton > button p,
    .btn-red div.stButton > button span {
        color: #ffffff !important;
        font-weight: 800 !important;
    }

    /* Section Button: Tareas Terminadas (Outline text style, no background fill) */
    .btn-completed-link div.stButton > button {
        background-color: transparent !important;
        background: transparent !important;
        color: #0f172a !important;
        border: 2px solid #cbd5e1 !important;
        border-radius: 8px !important;
        width: 100% !important;
        height: auto !important;
        min-width: auto !important;
        padding: 8px 16px !important;
        font-weight: 700 !important;
        font-size: 1.05rem !important;
    }
    .btn-completed-link div.stButton > button:hover {
        background-color: #f1f5f9 !important;
        background: #f1f5f9 !important;
        border-color: #94a3b8 !important;
        color: #0284c7 !important;
    }
    .btn-completed-link div.stButton > button p,
    .btn-completed-link div.stButton > button span {
        font-size: 1.05rem !important;
        font-weight: 700 !important;
        color: inherit !important;
    }
    
    /* Health Badges */
    .badge-verde {
        background-color: #dcfce7;
        color: #166534;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .badge-amarillo {
        background-color: #fef9c3;
        color: #854d0e;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .badge-rojo {
        background-color: #fee2e2;
        color: #991b1b;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# DATABASE ENGINE (SQLite)
# ---------------------------------------------------------
DB_FILE = "consola_enjoy.db"

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Proyectos (
            proyecto_id TEXT PRIMARY KEY,
            proyecto_nombre TEXT NOT NULL,
            unidad_negocio TEXT NOT NULL,
            proyecto_estatus TEXT NOT NULL,
            proyecto_salud TEXT NOT NULL,
            proyecto_descripcion TEXT,
            proyecto_responsable TEXT
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Tareas (
            tarea_id TEXT PRIMARY KEY,
            proyecto_id TEXT NOT NULL,
            tarea_nombre TEXT NOT NULL,
            tarea_responsable TEXT,
            aplica_porcentaje INTEGER DEFAULT 1,
            tarea_estatus TEXT NOT NULL,
            tarea_porcentaje INTEGER DEFAULT 0,
            tarea_fecha_inicio DATE,
            tarea_fecha_fin_base DATE,
            tarea_fecha_fin_proyectada DATE,
            tarea_fecha_fin_real DATE,
            tarea_comentarios TEXT,
            fecha_ultima_actualizacion TIMESTAMP,
            FOREIGN KEY (proyecto_id) REFERENCES Proyectos (proyecto_id) ON DELETE CASCADE
        )
    """)
    
    cursor.execute("PRAGMA table_info(Tareas)")
    cols = [col[1] for col in cursor.fetchall()]
    if "tarea_fecha_fin_real" not in cols:
        cursor.execute("ALTER TABLE Tareas ADD COLUMN tarea_fecha_fin_real DATE")
        
    # Auto-migrate projects to have unit prefixes
    cursor.execute("SELECT proyecto_nombre FROM Proyectos WHERE proyecto_id = 'PROJ-001'")
    row = cursor.fetchone()
    if not row or row["proyecto_nombre"] != "RI - ARENA":
        cursor.execute("DELETE FROM Tareas")
        cursor.execute("DELETE FROM Proyectos")
        
        proyectos_seed = [
            ("PROJ-001", "RI - ARENA", "Enjoy Rinconada", "En Ejecución", "🟢 Verde", "Proyecto ARENA Rinconada", "Por asignar"),
            ("PROJ-002", "RI - REMODELACIÓN OFICINA", "Enjoy Rinconada", "En Ejecución", "🟢 Verde", "Remodelación de oficinas Rinconada", "Por asignar"),
            ("PROJ-003", "RI - NUEVAS INICIATIVAS", "Enjoy Rinconada", "En Planificación", "🟢 Verde", "Nuevas iniciativas Rinconada", "Por asignar"),
            ("PROJ-004", "VI - RECEPCIÓN FINAL SALÓN AMERICANO", "Enjoy Viña", "En Ejecución", "🟢 Verde", "Recepción final salón americano Viña", "Por asignar"),
            ("PROJ-005", "PU - REGULARIZACIÓN CASINO", "Enjoy Pucón", "En Ejecución", "🟢 Verde", "Regularización Casino Pucón", "Por asignar"),
            ("PROJ-006", "CQ - OVO BEACH", "Enjoy Coquimbo", "En Ejecución", "🟢 Verde", "OVO Beach Coquimbo", "Por asignar"),
            ("PROJ-007", "TR - MANTENIMIENTO", "Enjoy Transversal", "En Ejecución", "🟢 Verde", "Mantenimiento Transversal", "Por asignar")
        ]
        cursor.executemany("""
            INSERT INTO Proyectos (proyecto_id, proyecto_nombre, unidad_negocio, proyecto_estatus, proyecto_salud, proyecto_descripcion, proyecto_responsable)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, proyectos_seed)

        today_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        today_date = date.today().strftime("%Y-%m-%d")
        tareas_seed = [
            ("TAR-001", "PROJ-001", "Definición de Compra de Galpón", "Por asignar", 1, "Pendiente", 0, today_date, today_date, today_date, None, "", today_str),
            ("TAR-002", "PROJ-002", "Reunión de coordinación con constructora.", "Por asignar", 1, "Pendiente", 0, today_date, today_date, today_date, None, "", today_str),
            ("TAR-003", "PROJ-002", "Inicio de obras.", "Por asignar", 1, "Pendiente", 0, today_date, today_date, today_date, None, "", today_str),
            ("TAR-004", "PROJ-003", "Definición de ampliación TGM exterior", "Por asignar", 1, "Pendiente", 0, today_date, today_date, today_date, None, "", today_str),
            ("TAR-005", "PROJ-003", "Definición de ampliación terrazas", "Por asignar", 1, "Pendiente", 0, today_date, today_date, today_date, None, "", today_str),
            ("TAR-006", "PROJ-003", "Definición de aumentos en CENIT", "Por asignar", 1, "Pendiente", 0, today_date, today_date, today_date, None, "", today_str),
            ("TAR-007", "PROJ-004", "Envío de expediente a revisora", "Por asignar", 1, "Pendiente", 0, today_date, today_date, today_date, None, "", today_str),
            ("TAR-008", "PROJ-006", "Definición sobre costos de regularización", "Por asignar", 1, "Pendiente", 0, today_date, today_date, today_date, None, "", today_str)
        ]
        cursor.executemany("""
            INSERT INTO Tareas (
                tarea_id, proyecto_id, tarea_nombre, tarea_responsable, aplica_porcentaje,
                tarea_estatus, tarea_porcentaje, tarea_fecha_inicio, tarea_fecha_fin_base,
                tarea_fecha_fin_proyectada, tarea_fecha_fin_real, tarea_comentarios, fecha_ultima_actualizacion
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, tareas_seed)

    conn.commit()
    conn.close()

def seed_demo_data():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM Tareas")
    cursor.execute("DELETE FROM Proyectos")
    
    proyectos_seed = [
        ("PROJ-001", "RI - ARENA", "Enjoy Rinconada", "En Ejecución", "🟢 Verde", "Proyecto ARENA Rinconada", "Por asignar"),
        ("PROJ-002", "RI - REMODELACIÓN OFICINA", "Enjoy Rinconada", "En Ejecución", "🟢 Verde", "Remodelación de oficinas Rinconada", "Por asignar"),
        ("PROJ-003", "RI - NUEVAS INICIATIVAS", "Enjoy Rinconada", "En Planificación", "🟢 Verde", "Nuevas iniciativas Rinconada", "Por asignar"),
        ("PROJ-004", "VI - RECEPCIÓN FINAL SALÓN AMERICANO", "Enjoy Viña", "En Ejecución", "🟢 Verde", "Recepción final salón americano Viña", "Por asignar"),
        ("PROJ-005", "PU - REGULARIZACIÓN CASINO", "Enjoy Pucón", "En Ejecución", "🟢 Verde", "Regularización Casino Pucón", "Por asignar"),
        ("PROJ-006", "CQ - OVO BEACH", "Enjoy Coquimbo", "En Ejecución", "🟢 Verde", "OVO Beach Coquimbo", "Por asignar"),
        ("PROJ-007", "TR - MANTENIMIENTO", "Enjoy Transversal", "En Ejecución", "🟢 Verde", "Mantenimiento Transversal", "Por asignar")
    ]
    
    cursor.executemany("""
        INSERT INTO Proyectos (proyecto_id, proyecto_nombre, unidad_negocio, proyecto_estatus, proyecto_salud, proyecto_descripcion, proyecto_responsable)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, proyectos_seed)

    today_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    today_date = date.today().strftime("%Y-%m-%d")
    tareas_seed = [
        ("TAR-001", "PROJ-001", "Definición de Compra de Galpón", "Por asignar", 1, "Pendiente", 0, today_date, today_date, today_date, None, "", today_str),
        ("TAR-002", "PROJ-002", "Reunión de coordinación con constructora.", "Por asignar", 1, "Pendiente", 0, today_date, today_date, today_date, None, "", today_str),
        ("TAR-003", "PROJ-002", "Inicio de obras.", "Por asignar", 1, "Pendiente", 0, today_date, today_date, today_date, None, "", today_str),
        ("TAR-004", "PROJ-003", "Definición de ampliación TGM exterior", "Por asignar", 1, "Pendiente", 0, today_date, today_date, today_date, None, "", today_str),
        ("TAR-005", "PROJ-003", "Definición de ampliación terrazas", "Por asignar", 1, "Pendiente", 0, today_date, today_date, today_date, None, "", today_str),
        ("TAR-006", "PROJ-003", "Definición de aumentos en CENIT", "Por asignar", 1, "Pendiente", 0, today_date, today_date, today_date, None, "", today_str),
        ("TAR-007", "PROJ-004", "Envío de expediente a revisora", "Por asignar", 1, "Pendiente", 0, today_date, today_date, today_date, None, "", today_str),
        ("TAR-008", "PROJ-006", "Definición sobre costos de regularización", "Por asignar", 1, "Pendiente", 0, today_date, today_date, today_date, None, "", today_str)
    ]
    
    cursor.executemany("""
        INSERT INTO Tareas (
            tarea_id, proyecto_id, tarea_nombre, tarea_responsable, aplica_porcentaje,
            tarea_estatus, tarea_porcentaje, tarea_fecha_inicio, tarea_fecha_fin_base,
            tarea_fecha_fin_proyectada, tarea_fecha_fin_real, tarea_comentarios, fecha_ultima_actualizacion
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, tareas_seed)
    
    conn.commit()
    conn.close()

def generate_new_id(prefix, table_name, col_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f"SELECT {col_id} FROM {table_name}")
    rows = cursor.fetchall()
    conn.close()
    
    max_num = 0
    for row in rows:
        val = str(row[col_id])
        if val.startswith(prefix + "-"):
            try:
                num = int(val.split("-")[1])
                if num > max_num:
                    max_num = num
            except ValueError:
                pass
    return f"{prefix}-{max_num + 1:03d}"

# Initialize Database
init_db()

# ---------------------------------------------------------
# SESSION STATE INITIALIZATION & ROUTING
# ---------------------------------------------------------
if "nav_page" not in st.session_state:
    st.session_state.nav_page = "DASHBOARD"
if "selected_proj_id" not in st.session_state:
    st.session_state.selected_proj_id = None
if "selected_task_id" not in st.session_state:
    st.session_state.selected_task_id = None
if "proyectos_subtab" not in st.session_state:
    st.session_state.proyectos_subtab = "📁 Ficha de Proyecto"

def open_ficha_proyecto(p_id):
    st.session_state.selected_proj_id = p_id
    st.session_state.nav_page = "PROYECTOS"
    st.session_state.proyectos_subtab = "📁 Ficha de Proyecto"

def open_ficha_tarea(t_id, p_id=None):
    st.session_state.selected_task_id = t_id
    if p_id:
        st.session_state.selected_proj_id = p_id
    st.session_state.nav_page = "PROYECTOS"
    st.session_state.proyectos_subtab = "📌 Ficha de Tarea"

# ---------------------------------------------------------
# SIDEBAR NAVIGATION (NO ICONS, LARGE FONT)
# ---------------------------------------------------------
st.sidebar.markdown("## NAVEGACIÓN")

nav_options = ["DASHBOARD", "PROYECTOS", "ADMIN"]
nav_index = nav_options.index(st.session_state.nav_page) if st.session_state.nav_page in nav_options else 0

vista_seleccionada = st.sidebar.radio(
    "Navegación principal:",
    nav_options,
    index=nav_index,
    label_visibility="collapsed"
)

if vista_seleccionada != st.session_state.nav_page:
    st.session_state.nav_page = vista_seleccionada

UNIDADES_NEGOCIO = [
    "Enjoy Rinconada",
    "Enjoy Viña",
    "Enjoy Pucón",
    "Enjoy Coquimbo",
    "Enjoy Transversal",
    "Enjoy Santiago",
    "Enjoy Antofagasta",
    "Enjoy Chiloé",
    "Corporativo / Central"
]

# ---------------------------------------------------------
# VISTA 1: DASHBOARD
# ---------------------------------------------------------
if st.session_state.nav_page == "DASHBOARD":
    # Top Filter by Business Unit
    col_filter, col_empty = st.columns([1, 2])
    with col_filter:
        unidad_filtro = st.selectbox(
            "📍 Seleccionar Unidad de Negocio:",
            ["Todas"] + UNIDADES_NEGOCIO
        )
    
    conn = get_db_connection()
    df_p = pd.read_sql_query("SELECT * FROM Proyectos", conn)
    df_t = pd.read_sql_query("SELECT * FROM Tareas", conn)
    conn.close()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # ---------------------------------------------------------
    # CASO A: FILTRO = "Todas"
    # ---------------------------------------------------------
    if unidad_filtro == "Todas":
        c1, c2, c3 = st.columns(3)
        
        # 1. Proyectos activos por unidad
        with c1:
            st.markdown("""
                <div class="metric-card">
                    <h4>📍 Proyectos Activos por Unidad</h4>
            """, unsafe_allow_html=True)
            
            if not df_p.empty:
                df_p_activos = df_p[df_p["proyecto_estatus"] != "Finalizado"]
                unit_counts = df_p_activos.groupby("unidad_negocio")["proyecto_id"].count().reset_index()
                unit_counts = unit_counts[unit_counts["proyecto_id"] > 0]
                
                if unit_counts.empty:
                    st.write("No hay proyectos activos.")
                else:
                    for _, u_row in unit_counts.iterrows():
                        u_name = u_row['unidad_negocio']
                        cnt = u_row['proyecto_id']
                        
                        col_btn, col_txt = st.columns([1, 4], vertical_alignment="center")
                        with col_btn:
                            st.markdown('<div class="btn-dark-gray">', unsafe_allow_html=True)
                            if st.button(f"{cnt}", key=f"dash_u_act_{u_name}", help=f"Ver proyectos de {u_name}"):
                                p_sub = df_p_activos[df_p_activos["unidad_negocio"] == u_name]
                                if not p_sub.empty:
                                    open_ficha_proyecto(p_sub.iloc[0]["proyecto_id"])
                                    st.rerun()
                            st.markdown('</div>', unsafe_allow_html=True)
                        with col_txt:
                            st.markdown(f"<b>{u_name}</b>", unsafe_allow_html=True)
            else:
                st.write("No hay proyectos registrados.")
            st.markdown("</div>", unsafe_allow_html=True)
            
        # 2. Tareas pendientes por proyecto
        with c2:
            st.markdown("""
                <div class="metric-card">
                    <h4>📌 Tareas Pendientes por Proyecto</h4>
            """, unsafe_allow_html=True)
            
            if not df_t.empty and not df_p.empty:
                df_t_pend = df_t[df_t["tarea_estatus"] != "Completada"]
                merged_t = pd.merge(df_t_pend, df_p, on="proyecto_id", how="inner")
                proj_t_counts = merged_t.groupby(["proyecto_id", "proyecto_nombre"])["tarea_id"].count().reset_index()
                
                if proj_t_counts.empty:
                    st.write("No hay tareas pendientes.")
                else:
                    for _, p_row in proj_t_counts.iterrows():
                        cnt = p_row['tarea_id']
                        p_nom = p_row['proyecto_nombre']
                        
                        col_btn, col_txt = st.columns([1, 4], vertical_alignment="center")
                        with col_btn:
                            st.markdown('<div class="btn-dark-gray">', unsafe_allow_html=True)
                            if st.button(f"{cnt}", key=f"dash_proj_count_{p_row['proyecto_id']}", help="Ver Ficha de Proyecto"):
                                open_ficha_proyecto(p_row['proyecto_id'])
                                st.rerun()
                            st.markdown('</div>', unsafe_allow_html=True)
                        with col_txt:
                            st.markdown(f"<b>{p_nom}</b>", unsafe_allow_html=True)
            else:
                st.write("No hay tareas registradas.")
            st.markdown("</div>", unsafe_allow_html=True)
            
        # 3. Requieren Atención
        with c3:
            st.markdown("""
                <div class="metric-card">
                    <h4>⚠️ Requieren Atención</h4>
            """, unsafe_allow_html=True)
            
            if not df_p.empty:
                df_atencion_proj = df_p[df_p["proyecto_salud"].isin(["🟡 Amarillo", "🔴 Rojo"])]
                if not df_t.empty:
                    merged_atencion = pd.merge(df_t[df_t["tarea_estatus"] != "Completada"], df_atencion_proj, on="proyecto_id", how="inner")
                    unit_atencion = merged_atencion.groupby("unidad_negocio")["tarea_id"].count().reset_index()
                else:
                    unit_atencion = pd.DataFrame()
                    
                if unit_atencion.empty:
                    unit_atencion_proj = df_atencion_proj.groupby("unidad_negocio")["proyecto_id"].count().reset_index()
                    if unit_atencion_proj.empty:
                        st.write("🟢 Todas las unidades están en regla.")
                    else:
                        for _, a_row in unit_atencion_proj.iterrows():
                            u_name = a_row['unidad_negocio']
                            cnt = a_row['proyecto_id']
                            col_btn, col_txt = st.columns([1, 4], vertical_alignment="center")
                            with col_btn:
                                st.markdown('<div class="btn-red">', unsafe_allow_html=True)
                                if st.button(f"{cnt}", key=f"dash_atn_p_{u_name}", help=f"Ver elementos en atención en {u_name}"):
                                    p_sub = df_atencion_proj[df_atencion_proj["unidad_negocio"] == u_name]
                                    if not p_sub.empty:
                                        open_ficha_proyecto(p_sub.iloc[0]["proyecto_id"])
                                        st.rerun()
                                st.markdown('</div>', unsafe_allow_html=True)
                            with col_txt:
                                st.markdown(f"<b>{u_name}</b>", unsafe_allow_html=True)
                else:
                    for _, a_row in unit_atencion.iterrows():
                        u_name = a_row['unidad_negocio']
                        cnt = a_row['tarea_id']
                        col_btn, col_txt = st.columns([1, 4], vertical_alignment="center")
                        with col_btn:
                            st.markdown('<div class="btn-red">', unsafe_allow_html=True)
                            if st.button(f"{cnt}", key=f"dash_atn_u_{u_name}", help=f"Ver tareas en atención en {u_name}"):
                                p_sub = df_atencion_proj[df_atencion_proj["unidad_negocio"] == u_name]
                                if not p_sub.empty:
                                    open_ficha_proyecto(p_sub.iloc[0]["proyecto_id"])
                                    st.rerun()
                            st.markdown('</div>', unsafe_allow_html=True)
                        with col_txt:
                            st.markdown(f"<b>{u_name}</b>", unsafe_allow_html=True)
            else:
                st.write("Sin datos.")
            st.markdown("</div>", unsafe_allow_html=True)

    # ---------------------------------------------------------
    # CASO B: FILTRO = Unidad Específica
    # ---------------------------------------------------------
    else:
        df_p_sub = df_p[df_p["unidad_negocio"] == unidad_filtro]
        
        c1, c2, c3 = st.columns(3)
        
        # 1. Proyectos activos
        with c1:
            st.markdown("""
                <div class="metric-card">
                    <h4>🏢 Proyectos Activos</h4>
            """, unsafe_allow_html=True)
            
            df_activos_sub = df_p_sub[df_p_sub["proyecto_estatus"] != "Finalizado"]
            if df_activos_sub.empty:
                st.write("No hay proyectos activos.")
            else:
                for _, p_row in df_activos_sub.iterrows():
                    if st.button(f"📁 {p_row['proyecto_nombre']}", key=f"btn_p_{p_row['proyecto_id']}", help="Abrir Ficha de Proyecto"):
                        open_ficha_proyecto(p_row['proyecto_id'])
                        st.rerun()
                    st.caption(f"Salud: {p_row['proyecto_salud']} | Estatus: {p_row['proyecto_estatus']}")
                    st.markdown("<div style='margin-bottom:4px;'></div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        # 2. Tareas pendientes por proyecto
        with c2:
            st.markdown("""
                <div class="metric-card">
                    <h4>📌 Tareas Pendientes por Proyecto</h4>
            """, unsafe_allow_html=True)
            
            if not df_t.empty and not df_p_sub.empty:
                merged_sub_t = pd.merge(df_t[df_t["tarea_estatus"] != "Completada"], df_p_sub, on="proyecto_id", how="inner")
                if merged_sub_t.empty:
                    st.write("No hay tareas pendientes.")
                else:
                    for _, t_row in merged_sub_t.iterrows():
                        if st.button(f"📌 {t_row['tarea_nombre']}", key=f"btn_t_{t_row['tarea_id']}", help=f"Proyecto: {t_row['proyecto_nombre']}"):
                            open_ficha_tarea(t_row['tarea_id'], t_row['proyecto_id'])
                            st.rerun()
                        st.caption(f"Proyecto: {t_row['proyecto_nombre']} | Estatus: {t_row['tarea_estatus']}")
                        st.markdown("<div style='margin-bottom:4px;'></div>", unsafe_allow_html=True)
            else:
                st.write("No hay tareas pendientes.")

        # 3. Requiere atención
        with c3:
            st.markdown("""
                <div class="metric-card">
                    <h4>⚠️ Requieren Atención</h4>
            """, unsafe_allow_html=True)
            
            if not df_p_sub.empty and not df_t.empty:
                df_atencion_sub_p = df_p_sub[df_p_sub["proyecto_salud"].isin(["🟡 Amarillo", "🔴 Rojo"])]
                merged_atencion_t = pd.merge(df_t[df_t["tarea_estatus"] != "Completada"], df_atencion_sub_p, on="proyecto_id", how="inner")
                
                if merged_atencion_t.empty:
                    st.write("🟢 Ninguna tarea requiere atención urgente.")
                else:
                    for _, a_row in merged_atencion_t.iterrows():
                        if st.button(f"⚠️ {a_row['tarea_nombre']}", key=f"btn_atn_{a_row['tarea_id']}", help="Abrir Ficha de Tarea"):
                            open_ficha_tarea(a_row['tarea_id'], a_row['proyecto_id'])
                            st.rerun()
                        st.caption(f"{a_row['proyecto_nombre']} ({a_row['proyecto_salud']})")
                        if a_row["tarea_comentarios"]:
                            st.caption(f"💬 {a_row['tarea_comentarios']}")
                        st.markdown("<div style='margin-bottom:4px;'></div>", unsafe_allow_html=True)
            else:
                st.write("Sin novedades de atención.")

    # ---------------------------------------------------------
    # SECCIÓN: TAREAS TERMINADAS (MATRIZ)
    # ---------------------------------------------------------
    st.markdown("---")
    
    st.markdown('<div class="btn-completed-link">', unsafe_allow_html=True)
    show_completed = st.button("📋 Ver Sección: Tareas Terminadas", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    if "show_completed_state" not in st.session_state:
        st.session_state.show_completed_state = False
        
    if show_completed:
        st.session_state.show_completed_state = not st.session_state.show_completed_state

    if st.session_state.show_completed_state:
        st.markdown("### Tareas Terminadas")
        st.caption("Matriz de historial de tareas completadas y fechas de término reales.")
        
        if not df_t.empty and not df_p.empty:
            df_completed_t = df_t[df_t["tarea_estatus"] == "Completada"].copy()
            
            if unidad_filtro != "Todas":
                p_ids_filter = df_p[df_p["unidad_negocio"] == unidad_filtro]["proyecto_id"].tolist()
                df_completed_t = df_completed_t[df_completed_t["proyecto_id"].isin(p_ids_filter)]
                
            if df_completed_t.empty:
                st.info("No hay tareas completadas para la unidad seleccionada.")
            else:
                matrix_df = pd.merge(df_completed_t, df_p, on="proyecto_id", how="inner")
                matrix_df["tarea_fecha_fin_real"] = matrix_df["tarea_fecha_fin_real"].fillna(matrix_df["tarea_fecha_fin_proyectada"])
                
                final_matrix = matrix_df[[
                    "unidad_negocio",
                    "proyecto_nombre",
                    "tarea_nombre",
                    "tarea_fecha_inicio",
                    "tarea_fecha_fin_real"
                ]].rename(columns={
                    "unidad_negocio": "Unidad",
                    "proyecto_nombre": "Proyecto",
                    "tarea_nombre": "Tarea",
                    "tarea_fecha_inicio": "Fecha de inicio",
                    "tarea_fecha_fin_real": "Fecha de término"
                })
                
                st.dataframe(final_matrix, use_container_width=True, hide_index=True)
        else:
            st.info("No existen tareas registradas.")

# ---------------------------------------------------------
# VISTA 2: PROYECTOS (FICHAS INTERACTIVAS & CARGA)
# ---------------------------------------------------------
elif st.session_state.nav_page == "PROYECTOS":
    st.subheader("📁 Módulo de Proyectos y Fichas Interactivas")
    
    conn = get_db_connection()
    df_p_all = pd.read_sql_query("SELECT * FROM Proyectos", conn)
    df_t_all = pd.read_sql_query("SELECT * FROM Tareas", conn)
    conn.close()
    
    subtab_list = ["📁 Ficha de Proyecto", "📌 Ficha de Tarea", "📝 Carga / Edición"]
    sub_index = subtab_list.index(st.session_state.proyectos_subtab) if st.session_state.proyectos_subtab in subtab_list else 0
    
    subtab1, subtab2, subtab3 = st.tabs(subtab_list)
    
    # ---------------------------------------------------------
    # SUBTAB 1: FICHA INTERACTIVA DE PROYECTO
    # ---------------------------------------------------------
    with subtab1:
        if df_p_all.empty:
            st.warning("No hay proyectos registrados en el sistema.")
        else:
            proj_dict = {f"{r['proyecto_id']} - {r['proyecto_nombre']} ({r['unidad_negocio']})": r['proyecto_id'] for _, r in df_p_all.iterrows()}
            
            default_index = 0
            if st.session_state.selected_proj_id:
                for idx, pid in enumerate(proj_dict.values()):
                    if pid == st.session_state.selected_proj_id:
                        default_index = idx
                        break
                        
            selected_proj_label = st.selectbox("🔍 Selecciona un Proyecto para consultar su Ficha:", list(proj_dict.keys()), index=default_index, key="sb_ficha_proj")
            cur_p_id = proj_dict[selected_proj_label]
            st.session_state.selected_proj_id = cur_p_id
            
            p_data = df_p_all[df_p_all["proyecto_id"] == cur_p_id].iloc[0]
            df_t_proj = df_t_all[df_t_all["proyecto_id"] == cur_p_id]
            
            total_t = len(df_t_proj)
            comp_t = len(df_t_proj[df_t_proj["tarea_estatus"] == "Completada"])
            pend_t = total_t - comp_t
            
            st.markdown(f"""
                <div class="ficha-card">
                    <div class="ficha-header">
                        <div>
                            <h2 class="ficha-title">{p_data['proyecto_nombre']}</h2>
                            <small style="color:#64748b; font-size:0.95rem;">Código: <b>{p_data['proyecto_id']}</b> &nbsp;|&nbsp; 📍 Unidad: <b>{p_data['unidad_negocio']}</b></small>
                        </div>
                        <div>
                            <span class="badge-verde">{p_data['proyecto_salud']}</span>
                            <span style="background-color:#e2e8f0; color:#334155; padding:4px 10px; border-radius:6px; font-size:0.85rem; font-weight:600;">{p_data['proyecto_estatus']}</span>
                        </div>
                    </div>
                    <div style="margin-bottom: 12px; font-size: 0.95rem; color: #334155;">
                        👤 <b>Responsable:</b> {p_data['proyecto_responsable'] or 'No asignado'}
                    </div>
                    <div style="font-size: 0.95rem; color: #475569; margin-bottom: 16px;">
                        📝 <b>Descripción / Objetivo:</b><br>{p_data['proyecto_descripcion'] or 'Sin descripción registrada.'}
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Total Tareas", f"{total_t}")
            m2.metric("Pendientes", f"{pend_t}")
            m3.metric("Completadas", f"{comp_t}")
            
            if total_t > 0:
                def calc_eff(r):
                    if r["aplica_porcentaje"] == 1:
                        return float(r["tarea_porcentaje"] or 0)
                    return 100.0 if r["tarea_estatus"] == "Completada" else (50.0 if r["tarea_estatus"] == "En Proceso" else 0.0)
                df_t_proj_cp = df_t_proj.copy()
                df_t_proj_cp["eff"] = df_t_proj_cp.apply(calc_eff, axis=1)
                avg_pct = round(df_t_proj_cp["eff"].mean(), 1)
            else:
                avg_pct = 0.0
                
            m4.metric("% Avance Ponderado", f"{avg_pct}%")
            st.progress(int(min(max(avg_pct, 0), 100)))
            
            st.markdown("---")
            st.markdown("### 📌 Tareas Asociadas al Proyecto")
            
            if df_t_proj.empty:
                st.info("Este proyecto no tiene tareas registradas aún.")
            else:
                for _, t_row in df_t_proj.iterrows():
                    c_t1, c_t2, c_t3 = st.columns([3, 2, 2])
                    with c_t1:
                        if st.button(f"📌 {t_row['tarea_nombre']}", key=f"f_proj_t_btn_{t_row['tarea_id']}", help="Abrir Ficha de esta Tarea"):
                            open_ficha_tarea(t_row['tarea_id'], cur_p_id)
                            st.rerun()
                        st.caption(f"Responsable: {t_row['tarea_responsable'] or 'N/A'}")
                    with c_t2:
                        st.write(f"Estatus: `{t_row['tarea_estatus']}`")
                        if t_row["aplica_porcentaje"] == 1:
                            st.caption(f"Avance: {t_row['tarea_porcentaje']}%")
                        else:
                            st.caption("Avance: Hito por Estatus")
                    with c_t3:
                        st.write(f"Término Proyectado: `{t_row['tarea_fecha_fin_proyectada']}`")
                        if t_row["tarea_comentarios"]:
                            st.caption(f"💬 {t_row['tarea_comentarios']}")
                    st.divider()

    # ---------------------------------------------------------
    # SUBTAB 2: FICHA INTERACTIVA DE TAREA
    # ---------------------------------------------------------
    with subtab2:
        if df_t_all.empty:
            st.warning("No hay tareas registradas en el sistema.")
        else:
            task_dict = {f"{r['tarea_id']} - {r['tarea_nombre']} (Proyecto: {r['proyecto_id']})": r['tarea_id'] for _, r in df_t_all.iterrows()}
            
            default_t_idx = 0
            if st.session_state.selected_task_id:
                for idx, tid in enumerate(task_dict.values()):
                    if tid == st.session_state.selected_task_id:
                        default_t_idx = idx
                        break
                        
            selected_task_label = st.selectbox("🔍 Selecciona una Tarea para consultar su Ficha:", list(task_dict.keys()), index=default_t_idx, key="sb_ficha_task")
            cur_t_id = task_dict[selected_task_label]
            st.session_state.selected_task_id = cur_t_id
            
            t_info = df_t_all[df_t_all["tarea_id"] == cur_t_id].iloc[0]
            p_associated = df_p_all[df_p_all["proyecto_id"] == t_info["proyecto_id"]].iloc[0] if not df_p_all[df_p_all["proyecto_id"] == t_info["proyecto_id"]].empty else None
            
            st.markdown(f"""
                <div class="ficha-card">
                    <div class="ficha-header">
                        <div>
                            <h2 class="ficha-title">📌 {t_info['tarea_nombre']}</h2>
                            <small style="color:#64748b; font-size:0.95rem;">Código: <b>{t_info['tarea_id']}</b> &nbsp;|&nbsp; Proyecto: <b>{p_associated['proyecto_nombre'] if p_associated is not None else t_info['proyecto_id']}</b></small>
                        </div>
                        <div>
                            <span style="background-color:#0284c7; color:white; padding:4px 12px; border-radius:20px; font-weight:600; font-size:0.85rem;">{t_info['tarea_estatus']}</span>
                        </div>
                    </div>
                    <div style="margin-bottom: 12px; font-size: 0.95rem; color: #334155;">
                        👤 <b>Responsable:</b> {t_info['tarea_responsable'] or 'No asignado'} &nbsp;|&nbsp; ⚙️ <b>Medición:</b> {'Porcentaje (0-100%)' if t_info['aplica_porcentaje']==1 else 'Hito por Estatus'}
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            c_dates1, c_dates2, c_dates3, c_dates4 = st.columns(4)
            c_dates1.metric("Fecha Inicio", t_info['tarea_fecha_inicio'] or "-")
            c_dates2.metric("Fecha Fin Base", t_info['tarea_fecha_fin_base'] or "-")
            c_dates3.metric("Fecha Fin Proyectada", t_info['tarea_fecha_fin_proyectada'] or "-")
            c_dates4.metric("Fecha Fin Real", t_info['tarea_fecha_fin_real'] or "En curso")
            
            if t_info["tarea_comentarios"]:
                st.info(f"💬 **Alertas / Comentarios:** {t_info['tarea_comentarios']}")
                
            st.markdown("---")
            st.markdown("#### ⚡ Actualización Rápida de esta Tarea")
            
            with st.form(f"form_quick_update_{cur_t_id}"):
                cu1, cu2 = st.columns(2)
                with cu1:
                    est_list = ["Pendiente", "En Proceso", "Completada"]
                    i_est = est_list.index(t_info["tarea_estatus"]) if t_info["tarea_estatus"] in est_list else 0
                    quick_est = st.selectbox("Nuevo Estatus:", est_list, index=i_est)
                with cu2:
                    if t_info["aplica_porcentaje"] == 1:
                        quick_pct = st.slider("% Avance:", 0, 100, int(t_info["tarea_porcentaje"] or 0))
                    else:
                        quick_pct = 100 if quick_est == "Completada" else 0
                        st.caption("ℹ️ Hito por Estatus (Sin % numérico)")
                        
                c_fproj, c_freal = st.columns(2)
                with c_fproj:
                    try:
                        dt_p_init = datetime.strptime(t_info["tarea_fecha_fin_proyectada"], "%Y-%m-%d").date()
                    except:
                        dt_p_init = date.today()
                    quick_f_proj = st.date_input("Nueva Fecha Fin Proyectada:", value=dt_p_init)
                with c_freal:
                    if quick_est == "Completada":
                        try:
                            dt_r_init = datetime.strptime(t_info["tarea_fecha_fin_real"], "%Y-%m-%d").date() if t_info["tarea_fecha_fin_real"] else date.today()
                        except:
                            dt_r_init = date.today()
                        quick_f_real = st.date_input("Fecha Fin Real:", value=dt_r_init)
                    else:
                        quick_f_real = None
                        
                quick_comentarios = st.text_area("Comentarios / Novedades:", value=t_info["tarea_comentarios"] or "")
                
                btn_sub_quick = st.form_submit_button("🚀 Guardar Avance", use_container_width=True)
                if btn_sub_quick:
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    now_s = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    fr_val = str(quick_f_real) if quick_f_real else None
                    cursor.execute("""
                        UPDATE Tareas
                        SET tarea_estatus = ?, tarea_porcentaje = ?, tarea_fecha_fin_proyectada = ?, tarea_fecha_fin_real = ?, tarea_comentarios = ?, fecha_ultima_actualizacion = ?
                        WHERE tarea_id = ?
                    """, (quick_est, quick_pct, str(quick_f_proj), fr_val, quick_comentarios, now_s, cur_t_id))
                    conn.commit()
                    conn.close()
                    st.success("✅ ¡Ficha de tarea actualizada correctamente!")
                    st.rerun()

    # ---------------------------------------------------------
    # SUBTAB 3: CARGA / EDICIÓN (FORMULARIOS)
    # ---------------------------------------------------------
    with subtab3:
        st.markdown("#### 📝 Carga y Edición General")
        
        tab_a, tab_b = st.tabs(["Formulario A: Crear / Editar Proyecto", "Formulario B: Nueva Tarea"])
        
        with tab_a:
            modo_proj = st.radio("Acción a realizar:", ["Crear Nuevo Proyecto", "Editar Proyecto Existente"], horizontal=True)
            proj_selected = None
            if modo_proj == "Editar Proyecto Existente":
                proj_dict = {f"{r['proyecto_id']} - {r['proyecto_nombre']} ({r['unidad_negocio']})": r['proyecto_id'] for _, r in df_p_all.iterrows()}
                selected_label = st.selectbox("Selecciona el Proyecto a Editar:", list(proj_dict.keys()))
                p_id_edit = proj_dict[selected_label]
                proj_selected = df_p_all[df_p_all["proyecto_id"] == p_id_edit].iloc[0]
            
            with st.form("form_proyecto_p", clear_on_submit=(modo_proj == "Crear Nuevo Proyecto")):
                c_id, c_nom = st.columns([1, 2])
                with c_id:
                    new_p_id = proj_selected["proyecto_id"] if proj_selected is not None else generate_new_id("PROJ", "Proyectos", "proyecto_id")
                    p_id_input = st.text_input("Código de Proyecto:", value=new_p_id, disabled=True)
                with c_nom:
                    p_nombre = st.text_input("Nombre del Proyecto *", value=proj_selected["proyecto_nombre"] if proj_selected is not None else "")
                
                c_u, c_est, c_sal = st.columns(3)
                with c_u:
                    idx_u = UNIDADES_NEGOCIO.index(proj_selected["unidad_negocio"]) if proj_selected is not None and proj_selected["unidad_negocio"] in UNIDADES_NEGOCIO else 0
                    p_unidad = st.selectbox("Unidad de Negocio *", UNIDADES_NEGOCIO, index=idx_u)
                with c_est:
                    estatus_opts = ["En Planificación", "En Ejecución", "Pausado", "Finalizado"]
                    idx_e = estatus_opts.index(proj_selected["proyecto_estatus"]) if proj_selected is not None and proj_selected["proyecto_estatus"] in estatus_opts else 0
                    p_estatus = st.selectbox("Estatus del Proyecto *", estatus_opts, index=idx_e)
                with c_sal:
                    salud_opts = ["🟢 Verde", "🟡 Amarillo", "🔴 Rojo"]
                    idx_s = salud_opts.index(proj_selected["proyecto_salud"]) if proj_selected is not None and proj_selected["proyecto_salud"] in salud_opts else 0
                    p_salud = st.selectbox("Semáforo de Salud *", salud_opts, index=idx_s)
                
                c_resp, c_desc = st.columns([1, 2])
                with c_resp:
                    p_resp = st.text_input("Responsable del Proyecto", value=proj_selected["proyecto_responsable"] if proj_selected is not None else "")
                with c_desc:
                    p_desc = st.text_area("Descripción / Objetivo", value=proj_selected["proyecto_descripcion"] if proj_selected is not None else "")
                
                submit_proj = st.form_submit_button("💾 Guardar Proyecto", use_container_width=True)
                
                if submit_proj:
                    if not p_nombre.strip():
                        st.error("⚠️ El Nombre del Proyecto es obligatorio.")
                    else:
                        conn = get_db_connection()
                        cursor = conn.cursor()
                        if modo_proj == "Crear Nuevo Proyecto":
                            cursor.execute("""
                                INSERT INTO Proyectos (proyecto_id, proyecto_nombre, unidad_negocio, proyecto_estatus, proyecto_salud, proyecto_descripcion, proyecto_responsable)
                                VALUES (?, ?, ?, ?, ?, ?, ?)
                            """, (p_id_input, p_nombre, p_unidad, p_estatus, p_salud, p_desc, p_resp))
                            st.success(f"✅ ¡Proyecto **{p_id_input} - {p_nombre}** creado exitosamente!")
                        else:
                            cursor.execute("""
                                UPDATE Proyectos
                                SET proyecto_nombre = ?, unidad_negocio = ?, proyecto_estatus = ?, proyecto_salud = ?, proyecto_descripcion = ?, proyecto_responsable = ?
                                WHERE proyecto_id = ?
                            """, (p_nombre, p_unidad, p_estatus, p_salud, p_desc, p_resp, p_id_input))
                            st.success(f"✅ ¡Proyecto **{p_id_input}** actualizado exitosamente!")
                        conn.commit()
                        conn.close()
                        st.rerun()

        with tab_b:
            if df_p_all.empty:
                st.warning("Primero debes crear un proyecto.")
            else:
                proj_options = {f"{r['proyecto_id']} - {r['proyecto_nombre']} ({r['unidad_negocio']})": r['proyecto_id'] for _, r in df_p_all.iterrows()}
                with st.form("form_nueva_tarea_p", clear_on_submit=True):
                    p_label_sel = st.selectbox("Selecciona el Proyecto Asociado *", list(proj_options.keys()))
                    p_id_selected = proj_options[p_label_sel]
                    t_id_new = generate_new_id("TAR", "Tareas", "tarea_id")
                    
                    c_tid, c_tnom = st.columns([1, 2])
                    with c_tid:
                        st.text_input("Código de Tarea:", value=t_id_new, disabled=True)
                    with c_tnom:
                        t_nombre = st.text_input("Nombre de la Tarea *")
                    
                    c_tresp, c_taplica = st.columns(2)
                    with c_tresp:
                        t_resp = st.text_input("Responsable de la Tarea")
                    with c_taplica:
                        aplica_porcentaje_sel = st.selectbox(
                            "¿Aplica porcentaje de avance numérico? *",
                            ["Sí (Porcentaje 0-100%)", "No (Hito por Estatus Binario/Cualitativo)"]
                        )
                        aplica_pct_val = 1 if "Sí" in aplica_porcentaje_sel else 0
                    
                    c_test, c_tpct = st.columns(2)
                    with c_test:
                        t_estatus = st.selectbox("Estatus Inicial *", ["Pendiente", "En Proceso", "Completada"])
                    with c_tpct:
                        if aplica_pct_val == 1:
                            t_porcentaje = st.slider("% Avance Inicial", 0, 100, 0)
                        else:
                            t_porcentaje = 0
                    
                    c_f1, c_f2, c_f3 = st.columns(3)
                    with c_f1:
                        t_f_ini = st.date_input("Fecha Inicio", value=date.today())
                    with c_f2:
                        t_f_base = st.date_input("Fecha Fin Base", value=date.today())
                    with c_f3:
                        t_f_proj = st.date_input("Fecha Fin Proyectada", value=date.today())
                    
                    t_f_real = None
                    if t_estatus == "Completada":
                        t_f_real = st.date_input("Fecha Fin Real:", value=date.today())
                    
                    t_comentarios = st.text_area("Comentarios u Observaciones Iniciales")
                    submit_tarea = st.form_submit_button("📌 Registrar Tarea", use_container_width=True)
                    
                    if submit_tarea:
                        if not t_nombre.strip():
                            st.error("⚠️ El Nombre de la Tarea es obligatorio.")
                        else:
                            conn = get_db_connection()
                            cursor = conn.cursor()
                            today_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            f_real_str = str(t_f_real) if t_f_real else None
                            cursor.execute("""
                                INSERT INTO Tareas (
                                    tarea_id, proyecto_id, tarea_nombre, tarea_responsable, aplica_porcentaje,
                                    tarea_estatus, tarea_porcentaje, tarea_fecha_inicio, tarea_fecha_fin_base,
                                    tarea_fecha_fin_proyectada, tarea_fecha_fin_real, tarea_comentarios, fecha_ultima_actualizacion
                                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """, (
                                t_id_new, p_id_selected, t_nombre, t_resp, aplica_pct_val,
                                t_estatus, t_porcentaje, str(t_f_ini), str(t_f_base),
                                str(t_f_proj), f_real_str, t_comentarios, today_str
                            ))
                            conn.commit()
                            conn.close()
                            st.success(f"✅ ¡Tarea **{t_id_new} - {t_nombre}** agregada exitosamente!")
                            st.rerun()

# ---------------------------------------------------------
# VISTA 3: ADMIN
# ---------------------------------------------------------
else:
    st.subheader("⚙️ Mantenimiento del Sistema (ADMIN)")
    st.caption("Herramientas para reiniciar el entorno, cargar datos iniciales de prueba e inspeccionar las tablas SQLite directamente.")
    
    col_adm1, col_adm2 = st.columns(2)
    
    with col_adm1:
        st.markdown("#### 🚀 Carga Inicial de Datos Demo")
        st.write("Genera proyectos y tareas de prueba para las sedes Casino Pucón, Hotel Coquimbo, Enjoy Viña y Enjoy Santiago.")
        if st.button("🌱 Sembrar Datos de Prueba", use_container_width=True):
            seed_demo_data()
            st.success("✅ ¡Datos de prueba cargados correctamente en SQLite!")
            st.rerun()
            
    with col_adm2:
        st.markdown("#### ⚠️ Reinicio de Base de Datos")
        st.write("Elimina todos los registros de proyectos y tareas para dejar el sistema en cero.")
        if st.button("🗑️ Vaciar Base de Datos", use_container_width=True):
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Tareas")
            cursor.execute("DELETE FROM Proyectos")
            conn.commit()
            conn.close()
            st.warning("⚠️ Base de datos vaciada por completo.")
            st.rerun()
            
    st.markdown("---")
    st.markdown("### 🗄️ Inspección Directa de Tablas SQLite")
    
    conn = get_db_connection()
    df_p_view = pd.read_sql_query("SELECT * FROM Proyectos", conn)
    df_t_view = pd.read_sql_query("SELECT * FROM Tareas", conn)
    conn.close()
    
    t_v1, t_v2 = st.tabs(["Tabla Proyectos", "Tabla Tareas"])
    with t_v1:
        st.dataframe(df_p_view, use_container_width=True)
    with t_v2:
        st.dataframe(df_t_view, use_container_width=True)
