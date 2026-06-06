import os
from datetime import datetime
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from database import get_db
from models.user import User
from models.job import Job
from routers.auth import get_current_user
from routers.templates import TEMPLATES
from services.gemini import extract_from_pdf, extract_from_text
from services.excel import generate_two_tab_excel
from config import MAX_UPLOAD_SIZE, ALLOWED_EXTENSIONS, OUTPUT_DIR

router = APIRouter(prefix="/api/v1", tags=["process"])

# MIME types that can be read as text
TEXT_MIMES = {"text/csv", "text/plain", "application/vnd.ms-excel"}
EXCEL_MIME = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


def _read_csv_or_text(file_bytes: bytes) -> str:
    """Try to decode bytes as UTF-8 or latin-1 text."""
    for encoding in ("utf-8", "utf-8-sig", "latin-1", "cp1252"):
        try:
            return file_bytes.decode(encoding)
        except UnicodeDecodeError:
            continue
    return file_bytes.decode("utf-8", errors="replace")


@router.post("/process")
async def process_file(
    file: UploadFile = File(...),
    template_name: str = Form(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # --- 1. Validate file extension ---
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{ext}'. Please upload a PDF, CSV, or Excel (.xlsx) file."
        )

    # --- 2. Read file bytes & check size ---
    file_bytes = await file.read()
    if len(file_bytes) > MAX_UPLOAD_SIZE:
        raise HTTPException(status_code=400, detail="File too large — maximum 10 MB")

    # --- 3. Load template ---
    template = TEMPLATES.get(template_name)
    if not template:
        raise HTTPException(status_code=404, detail=f"Template '{template_name}' not found")

    # --- 4. Extract data via Gemini ---
    prompt = template["gemini_prompt"]
    try:
        if ext == ".pdf":
            rows = extract_from_pdf(file_bytes, prompt)
        else:
            # CSV or Excel — read as text and send inline
            text_content = _read_csv_or_text(file_bytes)
            rows = extract_from_text(text_content, prompt)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"AI processing failed. Please try again. ({str(e)[:200]})"
        )

    if not rows:
        raise HTTPException(status_code=422, detail="No transaction records found in the file. Check that the file matches the selected template.")

    # --- 5. Generate 2-tab Excel ---
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_filename = f"{current_user.id}_{timestamp}.xlsx"
    out_path = os.path.join(OUTPUT_DIR, out_filename)
    generate_two_tab_excel(rows, template, file.filename, out_path)

    # --- 6. Save job history record ---
    job = Job(
        user_id=current_user.id,
        template_name=template.get("name", template_name),
        original_filename=file.filename,
        output_excel_path=out_path,
        rows_extracted=len(rows),
    )
    db.add(job)
    db.commit()

    # --- 7. Return file for browser auto-download ---
    download_name = os.path.splitext(file.filename)[0] + "_extracted.xlsx"
    return FileResponse(
        path=out_path,
        filename=download_name,
        media_type=EXCEL_MIME
    )
