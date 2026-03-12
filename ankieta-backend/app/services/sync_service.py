import os
import json
from sqlalchemy.orm import Session
from app.models.survey import Survey
from app.services.excel_parser import parse_excel_to_json

INPUT_DIR = "inputs"
BACKUP_DIR = "backups"


def sync_excel_folder(db: Session):
    # Створюємо папки, якщо їх немає
    for folder in [INPUT_DIR, BACKUP_DIR]:
        if not os.path.exists(folder):
            os.makedirs(folder)

    files = [f for f in os.listdir(INPUT_DIR) if f.endswith(('.xlsx', '.xls'))]

    results = []
    for filename in files:
        file_path = os.path.join(INPUT_DIR, filename)

        # 1. Читаємо файл
        with open(file_path, "rb") as f:
            content = f.read()

        # 2. Парсимо в JSON
        survey_json = parse_excel_to_json(content, filename)

        # 3. Визначаємо версію (дивимось скільки записів вже є в БД)
        current_version = db.query(Survey).filter(Survey.name == filename).count() + 1

        # 4. Зберігаємо в БД (Backup в базу)
        new_entry = Survey(
            name=filename,
            version=current_version,
            structure=survey_json
        )
        db.add(new_entry)

        # 5. Зберігаємо статичний JSON файл (Backup на диск)
        static_filename = f"{filename.split('.')[0]}_v{current_version}.json"
        static_path = os.path.join(BACKUP_DIR, static_filename)

        with open(static_path, "w", encoding="utf-8") as json_file:
            json.dump(survey_json, json_file, indent=4, ensure_ascii=False)

        results.append({"file": filename, "version": current_version, "static_path": static_path})

    db.commit()
    return results

