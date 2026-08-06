import streamlit as st
import streamlit.components.v1 as components
import os
import db_manager

st.set_page_config(
    page_title="Gestión de Proyectos - Casinos de Chile",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Full-bleed container layout styling
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        div.block-container {
            padding: 0rem !important;
            margin: 0rem !important;
            max-width: 100% !important;
        }
        iframe {
            border: none !important;
            width: 100% !important;
        }
    </style>
""", unsafe_allow_html=True)

dir_path = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------
# 1. Load Central Data (Google Sheets / db_manager)
# ---------------------------------------------------------
central_res = db_manager.load_central_data()

# Always refresh Session State from central DB if load succeeded
if central_res["status"] == "ok" and isinstance(central_res.get("data"), list):
    st.session_state["central_db"] = central_res["data"]
elif "central_db" not in st.session_state:
    st.session_state["central_db"] = central_res.get("data", [])

current_db_data = st.session_state["central_db"]

# Visible Diagnostic Indicator in Production
source_type = central_res.get("source", "desconocida")
row_count = len(current_db_data)
sheet_id = central_res.get("spreadsheet_id", "N/A")
msg = central_res.get("message", "")

st.info(
    f"📊 **DIAGNÓSTICO BD CENTRAL EN VIVO** | "
    f"**Fuente:** `{source_type}` | "
    f"**Filas cargadas:** `{row_count}` | "
    f"**Spreadsheet ID:** `{sheet_id}` | "
    f"**Estado:** {msg}"
)

# Fetch save_status if set during previous mutation
save_status = st.session_state.pop("save_status", None)

# ---------------------------------------------------------
# 2. Single Component Strategy (declare_component)
# ---------------------------------------------------------
consola_component = components.declare_component("consola_enjoy", path=dir_path)

component_value = consola_component(
    initial_data=current_db_data,
    db_status=central_res,
    save_status=save_status,
    default=None,
    key="consola_enjoy_component"
)

# ---------------------------------------------------------
# 3. Handle Frontend Mutation Events
# ---------------------------------------------------------
if component_value and isinstance(component_value, dict):
    action = component_value.get("action")
    if action == "save_db":
        new_data = component_value.get("data")
        context = component_value.get("context")
        if isinstance(new_data, list):
            try:
                save_result = db_manager.save_central_data(new_data)
                if isinstance(save_result, dict) and save_result.get("status") == "ok":
                    st.session_state["central_db"] = new_data
                    st.session_state["save_status"] = {
                        "status": "ok",
                        "message": "Guardado exitoso en base central.",
                        "context": context
                    }
                else:
                    raw_msg = save_result.get("message", "") if isinstance(save_result, dict) else "Error desconocido"
                    print(f"[SAVE_ERROR_LOG] Technical detail: {raw_msg}")
                    st.session_state["save_status"] = {
                        "status": "error",
                        "message": "No se pudo guardar la información en la base de datos central. Por favor intente nuevamente.",
                        "context": context
                    }
            except Exception as ex:
                print(f"[SAVE_EXCEPTION_LOG] Exception detail: {ex}")
                st.session_state["save_status"] = {
                    "status": "error",
                    "message": "No se pudo guardar la información en la base de datos central. Por favor intente nuevamente.",
                    "context": context
                }
            st.rerun()
