import os
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import desc

from database import get_db
from models.job import Job
from routers.auth import get_current_user, require_admin
from schemas.job import JobResponse, JobListResponse

router = APIRouter(prefix="/api/v1", tags=["history"])

EXCEL_MIME = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


@router.get("/jobs", response_model=JobListResponse)
def list_my_jobs(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List the current user's jobs, most recent first."""
    total = db.query(Job).filter(Job.user_id == current_user.id).count()
    jobs = (
        db.query(Job)
        .filter(Job.user_id == current_user.id)
        .order_by(desc(Job.created_at))
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return JobListResponse(
        jobs=[JobResponse.model_validate(j) for j in jobs],
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/jobs/all", response_model=JobListResponse)
def list_all_jobs(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    current_user=Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Admin: list all users' jobs."""
    total = db.query(Job).count()
    jobs = (
        db.query(Job)
        .order_by(desc(Job.created_at))
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return JobListResponse(
        jobs=[JobResponse.model_validate(j) for j in jobs],
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/download/{job_id}")
def download_job(
    job_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Re-download the Excel output from a previous job."""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Users can only download their own jobs; admins can download any
    if job.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Access denied")

    if not os.path.exists(job.output_excel_path):
        raise HTTPException(status_code=404, detail="Output file no longer available")

    return FileResponse(
        path=job.output_excel_path,
        filename=f"{job.original_filename}_extracted.xlsx",
        media_type=EXCEL_MIME
    )
