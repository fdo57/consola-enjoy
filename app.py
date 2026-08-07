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
# 1. Load Central Data (PostgreSQL / Google Sheets / db_manager)
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
# 3. Handle Frontend Mutation Events (save_db & delete_permanent)
# ---------------------------------------------------------
if component_value and isinstance(component_value, dict):
    action = component_value.get("action")
    context = component_value.get("context") or {}

    if action == "save_db":
        new_data = component_value.get("data")
        created_task_id = context.get("created_task_id", "N/A")
        action_type = context.get("action_type", "general_save")
        row_count = len(new_data) if isinstance(new_data, list) else 0

        print(f"[STREAMLIT_BRIDGE_LOG] Evento 'save_db' recibido en backend | Filas: {row_count} | Tarea ID: {created_task_id} | Acción: {action_type}")

        if isinstance(new_data, list):
            try:
                save_result = db_manager.save_central_data(new_data)
                if isinstance(save_result, dict) and save_result.get("status") == "ok":
                    print(f"[STREAMLIT_BRIDGE_LOG] Guardado exitoso en base central | Tarea ID: {created_task_id} | Filas: {row_count}")
                    st.session_state["central_db"] = new_data
                    st.session_state["save_status"] = {
                        "status": "ok",
                        "message": save_result.get("message", "Guardado exitoso en base central."),
                        "context": context
                    }
                else:
                    raw_msg = save_result.get("message", "") if isinstance(save_result, dict) else "Error desconocido"
                    print(f"[SAVE_ERROR_LOG] Detalle técnico de guardado: {raw_msg} | Tarea ID: {created_task_id}")
                    st.session_state["save_status"] = {
                        "status": "error",
                        "message": f"Error en base central: {raw_msg}",
                        "context": context
                    }
            except Exception as ex:
                print(f"[SAVE_EXCEPTION_LOG] Excepción técnica al guardar: {ex} | Tarea ID: {created_task_id}")
                st.session_state["save_status"] = {
                    "status": "error",
                    "message": f"Excepción técnica en servidor: {ex}",
                    "context": context
                }
            st.rerun()

    elif action == "delete_permanent":
        deleted_task_id = context.get("deleted_task_id", "N/A")
        print(f"[STREAMLIT_BRIDGE_LOG] Evento 'delete_permanent' recibido en backend | Tarea ID: {deleted_task_id}")

        if deleted_task_id and deleted_task_id != "N/A":
            try:
                del_result = db_manager.delete_permanent_task(deleted_task_id)
                if isinstance(del_result, dict) and del_result.get("status") == "ok":
                    print(f"[STREAMLIT_BRIDGE_LOG] Borrado permanente exitoso | Tarea ID: {deleted_task_id}")
                    fresh_res = db_manager.load_central_data()
                    if fresh_res.get("status") == "ok" and isinstance(fresh_res.get("data"), list):
                        st.session_state["central_db"] = fresh_res["data"]
                    else:
                        st.session_state["central_db"] = [t for t in current_db_data if t.get("tarea_id") != deleted_task_id]
                    st.session_state["save_status"] = {
                        "status": "ok",
                        "message": del_result.get("message", f"Tarea {deleted_task_id} eliminada permanentemente."),
                        "context": context
                    }
                else:
                    raw_msg = del_result.get("message", "") if isinstance(del_result, dict) else "Error al eliminar"
                    print(f"[DELETE_ERROR_LOG] Error al eliminar tarea {deleted_task_id}: {raw_msg}")
                    st.session_state["save_status"] = {
                        "status": "error",
                        "message": f"Error al eliminar: {raw_msg}",
                        "context": context
                    }
            except Exception as ex:
                print(f"[DELETE_EXCEPTION_LOG] Excepción al eliminar tarea {deleted_task_id}: {ex}")
                st.session_state["save_status"] = {
                    "status": "error",
                    "message": f"Excepción técnica al eliminar: {ex}",
                    "context": context
                }
            st.rerun()
