from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Any
from sqlalchemy import func
from app.core.database import get_db
from app.models.survey import Survey
from app.services.excel_parser import parse_excel_to_json
from app.services.sync_service import sync_excel_folder
import shutil
import os

router = APIRouter(prefix="/api/surveys", tags=["Surveys"])

class SurveyRenderResponse(BaseModel):
    structure: dict[str, Any]
    is_latest: bool


class SurveyVersionItem(BaseModel):
    id: int
    version: int


@router.post("/upload")
async def upload_survey(file: UploadFile = File(...), db: Session = Depends(get_db)):
    # 1. vakidujemy, excel 
    if not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="file Excel")

     #save file to disk 
    upload_dir = "uploads"
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)

    file_path = os.path.join(upload_dir, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 2. read file content
    with open(file_path, "rb") as f:
        content = f.read()

    # 3. Converter Excel -> JSON 
   
    try:
        survey_json = parse_excel_to_json(content, file.filename)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"eror for Excel: {str(e)}")

    # Save the survey structure to the database
    new_survey = Survey(
        name=file.filename,
        structure=survey_json
    )
    db.add(new_survey)
    db.commit()
    db.refresh(new_survey)

    # 5. Return the survey ID and JSON schema to the frontend
    return {
        "status": "success",
        "survey_id": new_survey.id,
        "schema": survey_json #frontend will use this to render the survey immediately
    }


@router.post("/sync-folder")
async def sync_folder(db: Session = Depends(get_db)):
    sync_results = sync_excel_folder(db)
    if not sync_results:
        return {"message": "No Excel files found for synchronization."}
    return {"message": "Synchronization completed.", "details": sync_results}


@router.get("/{survey_id}/render", response_model=SurveyRenderResponse)
def render_survey(survey_id: int, db: Session = Depends(get_db)):
    """Return the SurveyJS JSON schema for a given survey ID."""
    survey = db.get(Survey, survey_id)
    if survey is None:
        raise HTTPException(status_code=404, detail="Survey not found")
    max_version = (
        db.query(func.max(Survey.version))
        .filter(Survey.name == survey.name)
        .scalar()
    )
    return {"structure": survey.structure, "is_latest": survey.version == max_version}


@router.get("/{filename}/versions", response_model=list[SurveyVersionItem])
def list_versions(filename: str, db: Session = Depends(get_db)):
    surveys = (
        db.query(Survey)
        .filter(Survey.name == filename)
        .order_by(Survey.version.desc())
        .all()
    )
    return [{"id": s.id, "version": s.version} for s in surveys]

