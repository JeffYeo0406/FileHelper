from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class JobResponse(BaseModel):
    id: int
    user_id: int
    template_name: str
    original_filename: str
    rows_extracted: int
    created_at: datetime

    model_config = {"from_attributes": True}


class JobListResponse(BaseModel):
    jobs: list[JobResponse]
    total: int
    page: int
    page_size: int
