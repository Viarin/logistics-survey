import pandas as pd
import io


def parse_excel_to_json(file_content: bytes, filename: str):
    # Читаємо Excel
    df = pd.read_excel(io.BytesIO(file_content))

    # Фільтруємо порожні рядки
    df = df.dropna(subset=['id', 'type'])

    final_elements = []
    panels = {}

    for _, row in df.iterrows():
        q_id = str(row["id"]).strip()
        q_type = str(row["type"]).strip().lower()

        # Базовий об'єкт питання
        element = {
            "name": q_id,
            "type": q_type,
            "title": str(row["title"]).strip()
        }

        # Обробка типу 'date'
        if q_type == "date":
            element["type"] = "text"
            element["inputType"] = "date"

        # Розділяємо варіанти відповідей (на скрінах через ';')
        if pd.notna(row.get("choices")):
            element["choices"] = [c.strip() for c in str(row["choices"]).split(";") if c.strip()]

        # Підтримка складної логіки
        if pd.notna(row.get("visibleIf")):
            element["visibleIf"] = str(row["visibleIf"]).strip()

        # Групування в панелі (стовпчик panel на скрінах)
        panel_name = row.get("panel")
        if pd.notna(panel_name):
            panel_name = str(panel_name).strip()
            if panel_name not in panels:
                panels[panel_name] = {
                    "type": "panel",
                    "name": f"panel_{len(panels)}",
                    "title": panel_name,
                    "elements": []
                }
                final_elements.append(panels[panel_name])
            panels[panel_name]["elements"].append(element)
        else:
            final_elements.append(element)

    return {
        "title": filename.split('.')[0],
        "showNavigationButtons": "none",
        "questionsOnPageMode": "singlePage",
        "pages": [{"name": "page1", "elements": final_elements}]
    }

