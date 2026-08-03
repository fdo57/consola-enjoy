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

# Render status warning or error banner if configuration is incomplete in production
if central_res["status"] == "warning":
    st.warning(f"⚠️ {central_res['message']}")
elif central_res["status"] == "error":
    st.error(f"❌ {central_res['message']}")

# Session state management for central database
if "central_db" not in st.session_state or central_res["status"] == "ok":
    st.session_state["central_db"] = central_res.get("data", [])

current_db_data = st.session_state["central_db"]

# ---------------------------------------------------------
# 2. Single Component Strategy (declare_component)
# ---------------------------------------------------------
consola_component = components.declare_component("consola_enjoy", path=dir_path)

# Pass central data & status to component iframe
component_value = consola_component(
    initial_data=current_db_data,
    db_status=central_res,
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
        if new_data and isinstance(new_data, list):
            save_result = db_manager.save_central_data(new_data)
            if save_result["status"] == "ok":
                st.session_state["central_db"] = new_data
                st.rerun()
            else:
                st.error(f"❌ Error al guardar en base central: {save_result.get('message')}")
