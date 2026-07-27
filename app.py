import streamlit as st
import streamlit.components.v1 as components
import os

st.set_page_config(
    page_title="Gestión de Proyectos - Casinos de Chile",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Remove Streamlit default margins and padding for full-bleed experience
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

with open(os.path.join(dir_path, "index.html"), "r", encoding="utf-8") as f:
    html_content = f.read()

with open(os.path.join(dir_path, "styles.css"), "r", encoding="utf-8") as f:
    css_content = f.read()

with open(os.path.join(dir_path, "data.js"), "r", encoding="utf-8") as f:
    data_js = f.read()

with open(os.path.join(dir_path, "app.js"), "r", encoding="utf-8") as f:
    app_js = f.read()

xlsx_js_path = os.path.join(dir_path, "lib", "xlsx.full.min.js")
if os.path.exists(xlsx_js_path):
    with open(xlsx_js_path, "r", encoding="utf-8") as f:
        xlsx_js = f.read()
else:
    xlsx_js = ""

bundled_html = html_content.replace(
    '<link rel="stylesheet" href="styles.css">',
    f'<style>\n{css_content}\n</style>'
).replace(
    '<script src="lib/xlsx.full.min.js"></script>',
    f'<script>\n{xlsx_js}\n</script>'
).replace(
    '<script src="data.js"></script>',
    f'<script>\n{data_js}\n</script>'
).replace(
    '<script src="app.js"></script>',
    f'<script>\n{app_js}\n</script>'
)

components.html(bundled_html, height=1000, scrolling=True)
