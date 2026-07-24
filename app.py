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
    
    /* Compact Indicator Cards */
    .metric-card {
        background: white;
        border-radius: 10px;
        padding: 0.8rem 1rem;
        border: 1px solid #e2e8f0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.03);
        margin-bottom: 0.8rem;
    }
    .metric-card h4 {
        margin: 0 0 8px 0;
        color: #1e293b;
        font-size: 1.05rem;
        font-weight: 700;
        border-bottom: 2px solid #e2e8f0;
        padding-bottom: 6px;
    }
    
    /* Standardized Compact List Items */
    .metric-item {
        display: flex;
        align-items: center;
        justify-content: flex-start;
        gap: 10px;
        padding: 6px 0;
        border-bottom: 1px solid #f1f5f9;
        font-size: 0.9rem;
    }
    .metric-item:last-child {
        border-bottom: none;
    }
    
    .unit-list-item {
        padding: 6px 0;
        border-bottom: 1px solid #f1f5f9;
        display: flex;
        flex-direction: column;
        align-items: flex-start;
        width: 100%;
    }
    .unit-list-item:last-child {
        border-bottom: none;
    }
    
    .unit-item-title {
        font-size: 0.95rem;
        font-weight: 700;
        color: #0f172a;
        margin-bottom: 2px;
        line-height: 1.2;
    }
    .unit-item-subtitle {
        font-size: 0.85rem;
        color: #475569;
        line-height: 1.3;
    }
    
    /* Circle Badges for Numbers Only (Left Aligned) */
    .metric-val-circle {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        min-width: 28px;
        height: 28px;
        border-radius: 50%;
        background-color: #1e293b;
        color: #ffffff;
        font-weight: 800;
        font-size: 0.88rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        flex-shrink: 0;
    }
    .badge-atencion-circle {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        min-width: 28px;
        height: 28px;
        border-radius: 50%;
        background-color: #ef4444;
        color: #ffffff;
        font-weight: 800;
        font-size: 0.88rem;
        box-shadow: 0 2px 4px rgba(239, 68, 68, 0.2);
        flex-shrink: 0;
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
    
    # Proyectos Table
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
    
    # Tareas Table with tarea_fecha_fin_real
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
    
    # Migration check for existing DBs
    cursor.execute("PRAGMA table_info(Tareas)")
    cols = [col[1] for col in cursor.fetchall()]
    if "tarea_fecha_fin_real" not in cols:
        cursor.execute("ALTER TABLE Tareas ADD COLUMN tarea_fecha_fin_real DATE")
        
    conn.commit()
    conn.close()

def seed_demo_data():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM Tareas")
    cursor.execute("DELETE FROM Proyectos")
    
    proyectos_seed = [
        ("PROJ-001", "Remodelación Salón VIP", "Casino Pucón", "En Ejecución", "🟢 Verde", "Actualización de infraestructura y servicios del salón VIP.", "Carlos Mendoza"),
        ("PROJ-002", "Renovación Climatización HVAC", "Hotel Coquimbo", "En Ejecución", "🟡 Amarillo", "Mantenimiento y reemplazo de climatización en torre A.", "Ana María Silva"),
        ("PROJ-003", "Kioscos Autoatención Play", "Enjoy Viña", "En Planificación", "🟢 Verde", "Implementación de tótems digitales para agilizar la atención.", "Roberto Gómez"),
        ("PROJ-004", "Ampliación Red Wi-Fi Huéspedes", "Enjoy Santiago", "Pausado", "🔴 Rojo", "Reemplazo de antenas por demoras en proveedor de fibra.", "Marcela Fuentes")
    ]
    
    cursor.executemany("""
        INSERT INTO Proyectos (proyecto_id, proyecto_nombre, unidad_negocio, proyecto_estatus, proyecto_salud, proyecto_descripcion, proyecto_responsable)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, proyectos_seed)
    
    today_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    tareas_seed = [
        # PROJ-001
        ("TAR-001", "PROJ-001", "Diseño e iluminación decorativa", "Felipe Soto", 1, "Completada", 100, "2026-06-01", "2026-06-30", "2026-06-30", "2026-06-28", "Entregado a conformidad por arquitecto.", today_str),
        ("TAR-002", "PROJ-001", "Instalación alfombra alto tráfico", "Jorge Rivas", 1, "En Proceso", 65, "2026-07-01", "2026-07-25", "2026-07-28", None, "Avance continuo, leve espera de remate.", today_str),
        ("TAR-003", "PROJ-001", "Permiso Municipal de Funcionamiento", "Felipe Soto", 0, "En Proceso", 0, "2026-06-15", "2026-07-30", "2026-08-05", None, "Trámite en inspección municipal (Sin % numérico - Hito por Estatus).", today_str),

        # PROJ-002
        ("TAR-004", "PROJ-002", "Desmontaje de chillers antiguos", "Marcos Ugarte", 1, "Completada", 100, "2026-06-10", "2026-06-20", "2026-06-20", "2026-06-19", "Completado sin observaciones.", today_str),
        ("TAR-005", "PROJ-002", "Aprobación de Importación de Tuberías", "Ana María Silva", 0, "En Proceso", 0, "2026-06-21", "2026-07-15", "2026-08-10", None, "Aduana solicitó certificación ambiental (Alerta activada).", today_str),

        # PROJ-003
        ("TAR-006", "PROJ-003", "Licitación Tótems Kiosco", "Roberto Gómez", 0, "Pendiente", 0, "2026-08-01", "2026-08-20", "2026-08-20", None, "Pliegos listos para publicación.", today_str),
        ("TAR-007", "PROJ-003", "Integración Software POS", "Camila Torres", 1, "En Proceso", 35, "2026-07-10", "2026-09-01", "2026-09-01", None, "Desarrollo de API en etapa de testing.", today_str),

        # PROJ-004
        ("TAR-008", "PROJ-004", "Estudio de Cobertura Radiante", "Marcela Fuentes", 1, "Completada", 100, "2026-05-01", "2026-05-15", "2026-05-15", "2026-05-14", "Informe técnico aprobatorio.", today_str),
        ("TAR-009", "PROJ-004", "Firma de Contrato Proveedor Fibra", "Marcela Fuentes", 0, "Pendiente", 0, "2026-06-01", "2026-06-15", "2026-08-30", None, "Detenido por negociación presupuestaria.", today_str)
    ]
    
    cursor.executemany("""
        INSERT INTO Tareas (tarea_id, proyecto_id, tarea_nombre, tarea_responsable, aplica_porcentaje, tarea_estatus, tarea_porcentaje, tarea_fecha_inicio, tarea_fecha_fin_base, tarea_fecha_fin_proyectada, tarea_fecha_fin_real, tarea_comentarios, fecha_ultima_actualizacion)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
# SIDEBAR NAVIGATION (NO ICONS, LARGE FONT)
# ---------------------------------------------------------
st.sidebar.markdown("## NAVEGACIÓN")

vista_seleccionada = st.sidebar.radio(
    "Navegación principal:",
    ["DASHBOARD", "GESTIÓN DE PROYECTOS", "ADMIN"],
    label_visibility="collapsed"
)

UNIDADES_NEGOCIO = [
    "Casino Pucón",
    "Hotel Coquimbo",
    "Enjoy Viña",
    "Enjoy Santiago",
    "Enjoy Antofagasta",
    "Enjoy Chiloé",
    "Corporativo / Central"
]

# ---------------------------------------------------------
# VISTA 1: DASHBOARD
# ---------------------------------------------------------
if vista_seleccionada == "DASHBOARD":
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
                        st.markdown(f"""
                            <div class="metric-item">
                                <span class="metric-val-circle">{u_row['proyecto_id']}</span>
                                <span><b>{u_row['unidad_negocio']}</b></span>
                            </div>
                        """, unsafe_allow_html=True)
            else:
                st.write("No hay proyectos registrados.")
            st.markdown("</div>", unsafe_allow_html=True)
            
        # 2. Tareas pendientes por proyecto (sin proyecto_id)
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
                        st.markdown(f"""
                            <div class="metric-item">
                                <span class="metric-val-circle">{p_row['tarea_id']}</span>
                                <span><b>{p_row['proyecto_nombre']}</b></span>
                            </div>
                        """, unsafe_allow_html=True)
            else:
                st.write("No hay tareas registradas.")
            st.markdown("</div>", unsafe_allow_html=True)
            
        # 3. Requieren Atención (por unidad)
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
                            st.markdown(f"""
                                <div class="metric-item">
                                    <span class="badge-atencion-circle">{a_row['proyecto_id']}</span>
                                    <span><b>{a_row['unidad_negocio']}</b></span>
                                </div>
                            """, unsafe_allow_html=True)
                else:
                    for _, a_row in unit_atencion.iterrows():
                        st.markdown(f"""
                            <div class="metric-item">
                                <span class="badge-atencion-circle">{a_row['tarea_id']}</span>
                                <span><b>{a_row['unidad_negocio']}</b></span>
                            </div>
                        """, unsafe_allow_html=True)
            else:
                st.write("Sin datos.")
            st.markdown("</div>", unsafe_allow_html=True)

    # ---------------------------------------------------------
    # CASO B: FILTRO = Unidad Específica
    # ---------------------------------------------------------
    else:
        df_p_sub = df_p[df_p["unidad_negocio"] == unidad_filtro]
        
        c1, c2, c3 = st.columns(3)
        
        # 1. Proyectos activos (Título sin nombre de unidad, altura compacta)
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
                    st.markdown(f"""
                        <div class="unit-list-item">
                            <div class="unit-item-title">{p_row['proyecto_nombre']}</div>
                            <div class="unit-item-subtitle">Salud: {p_row['proyecto_salud']} &nbsp;|&nbsp; Estatus: <code>{p_row['proyecto_estatus']}</code></div>
                        </div>
                    """, unsafe_allow_html=True)
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
                        st.markdown(f"""
                            <div class="unit-list-item">
                                <div class="unit-item-title">{t_row['proyecto_nombre']}</div>
                                <div class="unit-item-subtitle">Tarea: <b>{t_row['tarea_nombre']}</b> &nbsp;|&nbsp; Estatus: <code>{t_row['tarea_estatus']}</code></div>
                            </div>
                        """, unsafe_allow_html=True)
            else:
                st.write("No hay tareas pendientes.")
            st.markdown("</div>", unsafe_allow_html=True)

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
                        st.markdown(f"""
                            <div class="unit-list-item">
                                <div class="unit-item-title">{a_row['proyecto_nombre']} <span style="font-size:0.85rem; font-weight:normal;">({a_row['proyecto_salud']})</span></div>
                                <div class="unit-item-subtitle">Tarea: <b>{a_row['tarea_nombre']}</b></div>
                                {f'<div style="font-size:0.82rem; color:#dc2626; margin-top:2px;">💬 {a_row["tarea_comentarios"]}</div>' if a_row["tarea_comentarios"] else ''}
                            </div>
                        """, unsafe_allow_html=True)
            else:
                st.write("Sin novedades de atención.")
            st.markdown("</div>", unsafe_allow_html=True)

    # ---------------------------------------------------------
    # SECCIÓN: TAREAS TERMINADAS (MATRIZ)
    # ---------------------------------------------------------
    st.markdown("---")
    
    show_completed = st.button("📋 Ver Sección: Tareas Terminadas", use_container_width=True)
    
    if "show_completed_state" not in st.session_state:
        st.session_state.show_completed_state = False
        
    if show_completed:
        st.session_state.show_completed_state = not st.session_state.show_completed_state

    if st.session_state.show_completed_state:
        st.markdown("### 🏁 Tareas Terminadas")
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
# VISTA 2: GESTIÓN DE PROYECTOS
# ---------------------------------------------------------
elif vista_seleccionada == "GESTIÓN DE PROYECTOS":
    st.subheader("📝 Gestión y Carga de Proyectos y Tareas")
    
    tab1, tab2, tab3 = st.tabs([
        "➕ / ✏️ Formulario A: Proyecto",
        "📌 Formulario B: Nueva Tarea",
        "🔄 Formulario C: Actualizar Avance"
    ])
    
    # ---------------------------------------------------------
    # TAB 1: FORMULARIO A - CREAR / EDITAR PROYECTO
    # ---------------------------------------------------------
    with tab1:
        st.markdown("#### Formulario A: Crear o Modificar Proyecto")
        
        modo_proj = st.radio("Acción a realizar:", ["Crear Nuevo Proyecto", "Editar Proyecto Existente"], horizontal=True)
        
        conn = get_db_connection()
        df_p_all = pd.read_sql_query("SELECT * FROM Proyectos", conn)
        conn.close()
        
        if modo_proj == "Editar Proyecto Existente" and df_p_all.empty:
            st.warning("No hay proyectos registrados para editar. Por favor crea uno nuevo primero.")
        else:
            proj_selected = None
            if modo_proj == "Editar Proyecto Existente":
                proj_dict = {f"{r['proyecto_id']} - {r['proyecto_nombre']} ({r['unidad_negocio']})": r['proyecto_id'] for _, r in df_p_all.iterrows()}
                selected_label = st.selectbox("Selecciona el Proyecto a Editar:", list(proj_dict.keys()))
                p_id_edit = proj_dict[selected_label]
                proj_selected = df_p_all[df_p_all["proyecto_id"] == p_id_edit].iloc[0]
            
            with st.form("form_proyecto", clear_on_submit=(modo_proj == "Crear Nuevo Proyecto")):
                c_id, c_nom = st.columns([1, 2])
                with c_id:
                    new_p_id = proj_selected["proyecto_id"] if proj_selected is not None else generate_new_id("PROJ", "Proyectos", "proyecto_id")
                    p_id_input = st.text_input("Código de Proyecto:", value=new_p_id, disabled=True)
                with c_nom:
                    p_nombre = st.text_input("Nombre del Proyecto *", value=proj_selected["proyecto_nombre"] if proj_selected is not None else "", placeholder="Ej: Renovación Salón de Juegos")
                
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
                    p_resp = st.text_input("Responsable del Proyecto", value=proj_selected["proyecto_responsable"] if proj_selected is not None else "", placeholder="Ej: María José Pérez")
                with c_desc:
                    p_desc = st.text_area("Descripción / Objetivo", value=proj_selected["proyecto_descripcion"] if proj_selected is not None else "", placeholder="Detalla los aspectos clave del proyecto...")
                
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

    # ---------------------------------------------------------
    # TAB 2: FORMULARIO B - AGREGAR NUEVA TAREA
    # ---------------------------------------------------------
    with tab2:
        st.markdown("#### Formulario B: Agregar Nueva Tarea a un Proyecto")
        
        conn = get_db_connection()
        df_p_all = pd.read_sql_query("SELECT * FROM Proyectos", conn)
        conn.close()
        
        if df_p_all.empty:
            st.warning("No existen proyectos registrados. Primero debes crear un proyecto en el Formulario A.")
        else:
            proj_options = {f"{r['proyecto_id']} - {r['proyecto_nombre']} ({r['unidad_negocio']})": r['proyecto_id'] for _, r in df_p_all.iterrows()}
            
            with st.form("form_nueva_tarea", clear_on_submit=True):
                p_label_sel = st.selectbox("Selecciona el Proyecto Asociado *", list(proj_options.keys()))
                p_id_selected = proj_options[p_label_sel]
                
                t_id_new = generate_new_id("TAR", "Tareas", "tarea_id")
                
                c_tid, c_tnom = st.columns([1, 2])
                with c_tid:
                    st.text_input("Código de Tarea:", value=t_id_new, disabled=True)
                with c_tnom:
                    t_nombre = st.text_input("Nombre de la Tarea *", placeholder="Ej: Cotización e inspección técnica")
                
                c_tresp, c_taplica = st.columns(2)
                with c_tresp:
                    t_resp = st.text_input("Responsable de la Tarea", placeholder="Ej: Juan Ovalle")
                with c_taplica:
                    aplica_porcentaje_sel = st.selectbox(
                        "¿Aplica porcentaje de avance numérico? *",
                        ["Sí (Porcentaje 0-100%)", "No (Hito por Estatus Binario/Cualitativo)"],
                        help="Usa 'No' para hitos como firmas, permisos o entregas binarias donde no aplica medir % gradual."
                    )
                    aplica_pct_val = 1 if "Sí" in aplica_porcentaje_sel else 0
                
                c_test, c_tpct = st.columns(2)
                with c_test:
                    t_estatus = st.selectbox("Estatus Inicial *", ["Pendiente", "En Proceso", "Completada"])
                with c_tpct:
                    if aplica_pct_val == 1:
                        t_porcentaje = st.slider("% Avance Inicial", 0, 100, 0)
                    else:
                        st.info("ℹ️ Al seleccionar 'No aplica porcentaje', la tarea medirá su avance por Estatus.")
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
                
                t_comentarios = st.text_area("Comentarios u Observaciones Iniciales", placeholder="Notas adicionales sobre la tarea...")
                
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
    # TAB 3: FORMULARIO C - ACTUALIZAR AVANCE DE TAREA
    # ---------------------------------------------------------
    with tab3:
        st.markdown("#### Formulario C: Actualizar Avance y Estado de Tarea")
        
        conn = get_db_connection()
        df_p_all = pd.read_sql_query("SELECT * FROM Proyectos", conn)
        df_t_all = pd.read_sql_query("SELECT * FROM Tareas", conn)
        conn.close()
        
        if df_t_all.empty:
            st.warning("No hay tareas registradas para actualizar.")
        else:
            proj_dict = {f"{r['proyecto_id']} - {r['proyecto_nombre']}": r['proyecto_id'] for _, r in df_p_all.iterrows()}
            p_sel_lbl = st.selectbox("1. Selecciona el Proyecto:", list(proj_dict.keys()), key="update_p_sel")
            p_id_cur = proj_dict[p_sel_lbl]
            
            df_t_filt = df_t_all[df_t_all["proyecto_id"] == p_id_cur]
            
            if df_t_filt.empty:
                st.info("Este proyecto no tiene tareas creadas aún.")
            else:
                tarea_dict = {f"{r['tarea_id']} - {r['tarea_nombre']} (Estado: {r['tarea_estatus']})": r['tarea_id'] for _, r in df_t_filt.iterrows()}
                t_sel_lbl = st.selectbox("2. Selecciona la Tarea a Actualizar:", list(tarea_dict.keys()), key="update_t_sel")
                t_id_cur = tarea_dict[t_sel_lbl]
                
                t_data = df_t_filt[df_t_filt["tarea_id"] == t_id_cur].iloc[0]
                
                st.markdown("---")
                st.markdown(f"##### 🔄 Editando: `{t_data['tarea_id']}` - **{t_data['tarea_nombre']}**")
                
                with st.form("form_update_avance"):
                    c_up1, c_up2 = st.columns(2)
                    with c_up1:
                        estatus_list = ["Pendiente", "En Proceso", "Completada"]
                        idx_est = estatus_list.index(t_data["tarea_estatus"]) if t_data["tarea_estatus"] in estatus_list else 0
                        new_estatus = st.selectbox("Nuevo Estatus:", estatus_list, index=idx_est)
                    
                    with c_up2:
                        if t_data["aplica_porcentaje"] == 1:
                            curr_pct = int(t_data["tarea_porcentaje"]) if t_data["tarea_porcentaje"] is not None else 0
                            new_pct = st.slider("% Avance Actualizado:", 0, 100, curr_pct)
                        else:
                            st.info("ℹ️ Tarea configurada como **Hito por Estatus**.")
                            new_pct = 100 if new_estatus == "Completada" else 0
                    
                    c_fp1, c_fp2 = st.columns(2)
                    with c_fp1:
                        try:
                            f_proj_init = datetime.strptime(t_data["tarea_fecha_fin_proyectada"], "%Y-%m-%d").date()
                        except:
                            f_proj_init = date.today()
                        new_f_proj = st.date_input("Nueva Fecha Fin Proyectada:", value=f_proj_init)
                    
                    with c_fp2:
                        if new_estatus == "Completada":
                            try:
                                f_real_init = datetime.strptime(t_data["tarea_fecha_fin_real"], "%Y-%m-%d").date() if t_data["tarea_fecha_fin_real"] else date.today()
                            except:
                                f_real_init = date.today()
                            new_f_real = st.date_input("Fecha Fin Real (Término):", value=f_real_init)
                        else:
                            new_f_real = None
                            
                    new_comentarios = st.text_area("Alertas, Avances o Comentarios Recientes:", value=t_data["tarea_comentarios"] or "")
                    
                    submit_update = st.form_submit_button("🚀 Actualizar Avance y Guardar", use_container_width=True)
                    
                    if submit_update:
                        conn = get_db_connection()
                        cursor = conn.cursor()
                        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        
                        f_real_val_str = str(new_f_real) if new_f_real else None
                        
                        cursor.execute("""
                            UPDATE Tareas
                            SET tarea_estatus = ?, tarea_porcentaje = ?, tarea_fecha_fin_proyectada = ?, tarea_fecha_fin_real = ?, tarea_comentarios = ?, fecha_ultima_actualizacion = ?
                            WHERE tarea_id = ?
                        """, (new_estatus, new_pct, str(new_f_proj), f_real_val_str, new_comentarios, now_str, t_id_cur))
                        
                        conn.commit()
                        conn.close()
                        st.success(f"✅ ¡Avance de la tarea **{t_id_cur}** registrado exitosamente a las {now_str}!")
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
