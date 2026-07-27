import openpyxl
import json
import datetime
import math

def clean_val(val):
    if val is None:
        return ""
    if isinstance(val, float) and math.isnan(val):
        return ""
    if isinstance(val, (datetime.datetime, datetime.date)):
        return val.strftime("%Y-%m-%d")
    s = str(val).strip()
    if s.lower() in ["nan", "nat", "none", "null"]:
        return ""
    return s

wb = openpyxl.load_workbook("carga_masiva.xlsx")
ws = wb.active

rows = list(ws.iter_rows(values_only=True))
headers = [str(h).strip() for h in rows[0]]

# Ensure proyecto_descripcion exists in headers
if "proyecto_descripcion" not in headers:
    headers.insert(4, "proyecto_descripcion")

proj_id_map = {}
proj_task_counter = {}

data = []
for row in rows[1:]:
    if not any(row):
        continue
    item = {}
    for h, cell in zip(headers, row):
        item[h] = clean_val(cell) if cell is not None else ""

    # Clean accents if any encoding glitches exist
    for k in ["unidad_nombre", "proyecto_nombre", "tarea_nombre", "tarea_descripcion", "tarea_contraparte"]:
        if item.get(k):
            item[k] = item[k].replace("", "")
            
    u_name = item.get("unidad_nombre", "")
    p_name = item.get("proyecto_nombre", "")
    key = (u_name, p_name)
    
    # Custom fix for Pucón TRASPASO A MONEDA to have distinct 2025_PU019 ID
    if u_name == "Enjoy Pucón" and "TRASPASO" in p_name.upper():
        proj_id_map[key] = "2025_PU019"
    elif key not in proj_id_map:
        base_id = item.get("proyecto_id", "")
        existing_ids = list(proj_id_map.values())
        if base_id in existing_ids:
            # Generate next correlative project ID e.g. 2025_PU019
            parts = base_id.split("_")
            if len(parts) == 2:
                year, un_code = parts[0], parts[1][:2]
                num_str = parts[1][2:]
                try:
                    num_val = int(num_str) + 1
                    base_id = f"{year}_{un_code}{num_val:03d}"
                except:
                    base_id = f"{base_id}_2"
        proj_id_map[key] = base_id

    item["proyecto_id"] = proj_id_map[key]
    
    # Update tarea_id to match unique proyecto_id
    if key not in proj_task_counter:
        proj_task_counter[key] = 1
    else:
        proj_task_counter[key] += 1
    
    t_seq = proj_task_counter[key]
    item["tarea_id"] = f"{item['proyecto_id']}_{t_seq:03d}"

    # Ensure proyecto_descripcion field exists
    if "proyecto_descripcion" not in item:
        item["proyecto_descripcion"] = ""

    # Standardize tarea_estado ("en proceso" -> "en desarrollo")
    if item.get("tarea_estado", "").lower() == "en proceso":
        item["tarea_estado"] = "en desarrollo"
        
    # Standardize con_alerta ("si" / "no")
    alerta_val = str(item.get("con_alerta", "")).lower()
    if alerta_val in ["si", "sí", "true", "1", "yes"]:
        item["con_alerta"] = "si"
    else:
        item["con_alerta"] = "no"

    # Standardize pct
    try:
        if item.get("tarea_pct") != "":
            pct_num = float(item["tarea_pct"])
            if pct_num <= 1.0 and pct_num > 0:
                item["tarea_pct"] = round(pct_num * 100)
            else:
                item["tarea_pct"] = round(pct_num)
    except:
        pass
        
    data.append(item)

js_content = f"// Initial database preloaded from carga_masiva.xlsx\nwindow.INITIAL_DATA = {json.dumps(data, indent=2, ensure_ascii=False)};\n"

with open("data.js", "w", encoding="utf-8") as f:
    f.write(js_content)

print(f"Successfully converted {len(data)} records into data.js with {len(proj_id_map)} distinct projects.")
for k, v in proj_id_map.items():
    print(f"  - Unit: '{k[0]}', Project: '{k[1]}' -> ID: '{v}'")
