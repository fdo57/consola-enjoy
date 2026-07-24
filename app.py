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
    
    /* Header Styling */
    .app-header {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        color: white;
        padding: 1.5rem 2rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .app-header h1 {
        color: #ffffff;
        margin: 0;
        font-size: 1.8rem;
        font-weight: 700;
    }
    .app-header p {
        color: #94a3b8;
        margin: 0.2rem 0 0 0;
        font-size: 0.95rem;
    }
    
    /* Executive Cards */
    .proj-card {
        background: white;
        border-radius: 12px;
        padding: 1.25rem;
        border: 1px solid #e2e8f0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.04);
        margin-bottom: 1rem;
        transition: transform 0.2s, box-shadow 0.2s;
    }
    .proj-card:hover {
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.08);
    }
    
    /* Health Badges */
    .badge-verde {
        background-color: #dcfce7;
        color: #166534;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.85rem;
        display: inline-block;
    }
    .badge-amarillo {
        background-color: #fef9c3;
        color: #854d0e;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.85rem;
        display: inline-block;
    }
    .badge-rojo {
        background-color: #fee2e2;
        color: #991b1b;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.85rem;
        display: inline-block;
    }
    .badge-status {
        background-color: #e2e8f0;
        color: #334155;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.8rem;
        font-weight: 500;
    }
    
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
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
    
    # Tareas Table
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
            tarea_comentarios TEXT,
            fecha_ultima_actualizacion TIMESTAMP,
            FOREIGN KEY (proyecto_id) REFERENCES Proyectos (proyecto_id) ON DELETE CASCADE
        )
    """)
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
        ("TAR-001", "PROJ-001", "Diseño e iluminación decorativa", "Felipe Soto", 1, "Completada", 100, "2026-06-01", "2026-06-30", "2026-06-30", "Entregado a conformidad por arquitecto.", today_str),
        ("TAR-002", "PROJ-001", "Instalación alfombra alto tráfico", "Jorge Rivas", 1, "En Proceso", 65, "2026-07-01", "2026-07-25", "2026-07-28", "Avance continuo, leve espera de remate.", today_str),
        ("TAR-003", "PROJ-001", "Permiso Municipal de Funcionamiento", "Felipe Soto", 0, "En Proceso", 0, "2026-06-15", "2026-07-30", "2026-08-05", "Trámite en inspección municipal (Sin % numérico - Hito por Estatus).", today_str),

        # PROJ-002
        ("TAR-004", "PROJ-002", "Desmontaje de chillers antiguos", "Marcos Ugarte", 1, "Completada", 100, "2026-06-10", "2026-06-20", "2026-06-20", "Completado sin observaciones.", today_str),
        ("TAR-005", "PROJ-002", "Aprobación de Importación de Tuberías", "Ana María Silva", 0, "En Proceso", 0, "2026-06-21", "2026-07-15", "2026-08-10", "Aduana solicitó certificación ambiental (Alerta activada).", today_str),

        # PROJ-003
        ("TAR-006", "PROJ-003", "Licitación Tótems Kiosco", "Roberto Gómez", 0, "Pendiente", 0, "2026-08-01", "2026-08-20", "2026-08-20", "Pliegos listos para publicación.", today_str),
        ("TAR-007", "PROJ-003", "Integración Software POS", "Camila Torres", 1, "En Proceso", 35, "2026-07-10", "2026-09-01", "2026-09-01", "Desarrollo de API en etapa de testing.", today_str),

        # PROJ-004
        ("TAR-008", "PROJ-004", "Estudio de Cobertura Radiante", "Marcela Fuentes", 1, "Completada", 100, "2026-05-01", "2026-05-15", "2026-05-15", "Informe técnico aprobatorio.", today_str),
        ("TAR-009", "PROJ-004", "Firma de Contrato Proveedor Fibra", "Marcela Fuentes", 0, "Pendiente", 0, "2026-06-01", "2026-06-15", "2026-08-30", "Detenido por negociación presupuestaria.", today_str)
    ]
    
    cursor.executemany("""
        INSERT INTO Tareas (tarea_id, proyecto_id, tarea_nombre, tarea_responsable, aplica_porcentaje, tarea_estatus, tarea_porcentaje, tarea_fecha_inicio, tarea_fecha_fin_base, tarea_fecha_fin_proyectada, tarea_comentarios, fecha_ultima_actualizacion)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, tareas_seed)
    
    conn.commit()
    conn.close()

def get_proyectos_df(unidad_filter=None):
    conn = get_db_connection()
    query = "SELECT * FROM Proyectos"
    params = []
    if unidad_filter and unidad_filter != "Todas":
        query += " WHERE unidad_negocio = ?"
        params.append(unidad_filter)
    
    df_proj = pd.read_sql_query(query, conn, params=params)
    df_tareas = pd.read_sql_query("SELECT * FROM Tareas", conn)
    conn.close()
    
    if not df_proj.empty:
        if not df_tareas.empty:
            def calc_effective_pct(row):
                if row["aplica_porcentaje"] == 1:
                    return float(row["tarea_porcentaje"] if row["tarea_porcentaje"] is not None else 0)
                else:
                    estatus = str(row["tarea_estatus"]).lower()
                    if "completad" in estatus:
                        return 100.0
                    elif "proceso" in estatus:
                        return 50.0
                    else:
                        return 0.0
            
            df_tareas["pct_efectivo"] = df_tareas.apply(calc_effective_pct, axis=1)
            
            proj_stats = df_tareas.groupby("proyecto_id").agg(
                avance_promedio=("pct_efectivo", "mean"),
                max_fecha_proyectada=("tarea_fecha_fin_proyectada", "max"),
                total_tareas=("tarea_id", "count")
            ).reset_index()
            
            df_proj = pd.merge(df_proj, proj_stats, on="proyecto_id", how="left")
            df_proj["avance_promedio"] = df_proj["avance_promedio"].fillna(0).round(1)
            df_proj["total_tareas"] = df_proj["total_tareas"].fillna(0).astype(int)
            df_proj["max_fecha_proyectada"] = df_proj["max_fecha_proyectada"].fillna("-")
        else:
            df_proj["avance_promedio"] = 0.0
            df_proj["max_fecha_proyectada"] = "-"
            df_proj["total_tareas"] = 0
            
    return df_proj

def get_tareas_by_proyecto(proyecto_id):
    conn = get_db_connection()
    df = pd.read_sql_query("SELECT * FROM Tareas WHERE proyecto_id = ? ORDER BY tarea_id", conn, params=[proyecto_id])
    conn.close()
    return df

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
# APP HEADER
# ---------------------------------------------------------
st.markdown("""
    <div class="app-header">
        <h1>🏨 Consola de Administración de Proyectos ENJOY</h1>
        <p>Plataforma Integral de Seguimiento Ejecutivo y Carga Operativa</p>
    </div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# SIDEBAR NAVIGATION & FILTERS
# ---------------------------------------------------------
st.sidebar.image("https://img.icons8.com/color/96/dashboard-layout.png", width=64)
st.sidebar.title("Navegación Principal")

vista_seleccionada = st.sidebar.radio(
    "Selecciona el Módulo:",
    [
        "📊 Dashboard Ejecutivo (Gerencia)",
        "📝 Gestión y Carga de Datos (Subgerencia)",
        "⚙️ Administración y Datos Semilla"
    ]
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
# VISTA 1: 📊 DASHBOARD EJECUTIVO (GERENTE GENERAL)
# ---------------------------------------------------------
if vista_seleccionada == "📊 Dashboard Ejecutivo (Gerencia)":
    st.subheader("📊 Resumen Ejecutivo Global por Unidad de Negocio")
    st.caption("Visión sintética de alto nivel para toma de decisiones y control de estado de salud.")
    
    # Top Filter
    col_f1, col_f2 = st.columns([1, 2])
    with col_f1:
        unidad_filtro = st.selectbox(
            "📍 Filtrar por Unidad de Negocio:",
            ["Todas"] + UNIDADES_NEGOCIO
        )
        
    df_proyectos = get_proyectos_df(unidad_filtro)
    
    if df_proyectos.empty:
        st.info("💡 No hay proyectos registrados para la unidad de negocio seleccionada. Ve al módulo de **Gestión y Carga** para agregar nuevos o a **Administración** para cargar datos demo.")
    else:
        # KPI Cards Calculation
        total_proj = len(df_proyectos)
        en_regla = len(df_proyectos[df_proyectos["proyecto_salud"] == "🟢 Verde"])
        en_riesgo = len(df_proyectos[df_proyectos["proyecto_salud"].isin(["🟡 Amarillo", "🔴 Rojo"])])
        avance_global = round(df_proyectos["avance_promedio"].mean(), 1)
        
        # Display Metric Cards
        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        kpi1.metric("Total Proyectos", f"{total_proj}", help="Proyectos bajo la unidad seleccionada")
        kpi2.metric("🟢 En Regla (Verde)", f"{en_regla}", delta=f"{round(en_regla/total_proj*100)}%" if total_proj>0 else "0%")
        kpi3.metric("⚠️ En Riesgo / Atención", f"{en_riesgo}", delta=f"-{en_riesgo}" if en_riesgo>0 else "0", delta_color="inverse")
        kpi4.metric("📈 Avance Promedio Global", f"{avance_global}%")
        
        st.markdown("---")
        st.markdown("### 📋 Proyectos Ejecutivos")
        
        # Grid layout for Executive Cards
        for idx, row in df_proyectos.iterrows():
            salud_raw = str(row["proyecto_salud"])
            if "Verde" in salud_raw:
                badge_class = "badge-verde"
            elif "Amarillo" in salud_raw:
                badge_class = "badge-amarillo"
            else:
                badge_class = "badge-rojo"
                
            with st.container():
                st.markdown(f"""
                    <div class="proj-card">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                            <h3 style="margin: 0; font-size: 1.2rem; color: #0f172a;">{row['proyecto_nombre']} <span style="font-size: 0.85rem; color: #64748b; font-weight: normal;">({row['proyecto_id']})</span></h3>
                            <div>
                                <span class="{badge_class}">{salud_raw}</span>
                                <span class="badge-status">{row['proyecto_estatus']}</span>
                            </div>
                        </div>
                        <div style="font-size: 0.9rem; color: #475569; margin-bottom: 10px;">
                            📍 <b>Unidad:</b> {row['unidad_negocio']} &nbsp;|&nbsp; 👤 <b>Responsable:</b> {row['proyecto_responsable']} &nbsp;|&nbsp; 🗓️ <b>Término Est.:</b> {row['max_fecha_proyectada']}
                        </div>
                        <div style="margin-bottom: 5px; font-size: 0.85rem; color: #334155;">
                            <b>Avance Ponderado del Proyecto:</b> {row['avance_promedio']}%
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                # Progress bar
                st.progress(int(min(max(row['avance_promedio'], 0), 100)))
                
                # Read-only task breakdown drilldown
                with st.expander(f"🔍 Ver Detalle de Tareas ({row['total_tareas']} tareas) - Solo Lectura"):
                    df_tareas_proj = get_tareas_by_proyecto(row["proyecto_id"])
                    
                    if df_tareas_proj.empty:
                        st.caption("No hay tareas registradas aún para este proyecto.")
                    else:
                        st.markdown("**Desglose Operativo:**")
                        for t_idx, t_row in df_tareas_proj.iterrows():
                            c1, c2, c3, c4 = st.columns([3, 2, 2, 3])
                            with c1:
                                st.markdown(f"**{t_row['tarea_nombre']}**")
                                st.caption(f"Responsable: {t_row['tarea_responsable']}")
                            with c2:
                                st.write(f"Estatus: `{t_row['tarea_estatus']}`")
                            with c3:
                                if t_row["aplica_porcentaje"] == 1:
                                    st.write(f"Avance Numérico: **{t_row['tarea_porcentaje']}%**")
                                    st.progress(int(t_row['tarea_porcentaje']))
                                else:
                                    st.write("Avance: `N/A - Hito por Estatus`")
                            with c4:
                                st.caption(f"Término Proyectado: {t_row['tarea_fecha_fin_proyectada']}")
                                if t_row["tarea_comentarios"]:
                                    st.info(f"💬 {t_row['tarea_comentarios']}")
                            st.divider()

# ---------------------------------------------------------
# VISTA 2: 📝 GESTIÓN Y CARGA DE DATOS (SUBGERENTA)
# ---------------------------------------------------------
elif vista_seleccionada == "📝 Gestión y Carga de Datos (Subgerencia)":
    st.subheader("📝 Centro de Carga y Actualización Operativa")
    st.caption("Diseñado para la edición rápida, directa e intuitiva de proyectos y tareas sin elementos ambiguos.")
    
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
                        st.info("ℹ️ Al seleccionar 'No aplica porcentaje', la tarea medirá su avance por Estatus (Pendiente=0%, En Proceso=50%, Completada=100%).")
                        t_porcentaje = 0
                
                c_f1, c_f2, c_f3 = st.columns(3)
                with c_f1:
                    t_f_ini = st.date_input("Fecha Inicio", value=date.today())
                with c_f2:
                    t_f_base = st.date_input("Fecha Fin Base", value=date.today())
                with c_f3:
                    t_f_proj = st.date_input("Fecha Fin Proyectada", value=date.today())
                
                t_comentarios = st.text_area("Comentarios u Observaciones Iniciales", placeholder="Notas adicionales sobre la tarea...")
                
                submit_tarea = st.form_submit_button("📌 Registrar Tarea", use_container_width=True)
                
                if submit_tarea:
                    if not t_nombre.strip():
                        st.error("⚠️ El Nombre de la Tarea es obligatorio.")
                    else:
                        conn = get_db_connection()
                        cursor = conn.cursor()
                        today_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        
                        cursor.execute("""
                            INSERT INTO Tareas (
                                tarea_id, proyecto_id, tarea_nombre, tarea_responsable, aplica_porcentaje,
                                tarea_estatus, tarea_porcentaje, tarea_fecha_inicio, tarea_fecha_fin_base,
                                tarea_fecha_fin_proyectada, tarea_comentarios, fecha_ultima_actualizacion
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            t_id_new, p_id_selected, t_nombre, t_resp, aplica_pct_val,
                            t_estatus, t_porcentaje, str(t_f_ini), str(t_f_base),
                            str(t_f_proj), t_comentarios, today_str
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
                            st.info("ℹ️ Tarea configurada como **Hito por Estatus**. No requiere porcentaje numérico.")
                            new_pct = 0
                    
                    try:
                        f_proj_init = datetime.strptime(t_data["tarea_fecha_fin_proyectada"], "%Y-%m-%d").date()
                    except:
                        f_proj_init = date.today()
                        
                    new_f_proj = st.date_input("Nueva Fecha Fin Proyectada:", value=f_proj_init)
                    new_comentarios = st.text_area("Alertas, Avances o Comentarios Recientes:", value=t_data["tarea_comentarios"] or "")
                    
                    submit_update = st.form_submit_button("🚀 Actualizar Avance y Notificar", use_container_width=True)
                    
                    if submit_update:
                        conn = get_db_connection()
                        cursor = conn.cursor()
                        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        
                        cursor.execute("""
                            UPDATE Tareas
                            SET tarea_estatus = ?, tarea_porcentaje = ?, tarea_fecha_fin_proyectada = ?, tarea_comentarios = ?, fecha_ultima_actualizacion = ?
                            WHERE tarea_id = ?
                        """, (new_estatus, new_pct, str(new_f_proj), new_comentarios, now_str, t_id_cur))
                        
                        conn.commit()
                        conn.close()
                        st.success(f"✅ ¡Avance de la tarea **{t_id_cur}** registrado exitosamente a las {now_str}!")
                        st.rerun()

# ---------------------------------------------------------
# VISTA 3: ⚙️ ADMINISTRACIÓN Y DATOS SEMILLA
# ---------------------------------------------------------
else:
    st.subheader("⚙️ Mantenimiento del Sistema y Diagnóstico (Administrador)")
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
