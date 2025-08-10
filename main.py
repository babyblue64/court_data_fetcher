from fastapi import FastAPI, BackgroundTasks, HTTPException, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Dict, Optional
import uuid
from scraper import run_scraper
import asyncio
from database import Case, get_db, init_db
from contextlib import asynccontextmanager
from typing import AsyncIterator
from fastapi.middleware.cors import CORSMiddleware
import os

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    # To create table in postgres
    init_db()
    yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Job queue
jobs: Dict[str, Dict] = {}

class CaseRequest(BaseModel):
    case_type: str
    case_number: str
    case_year: str

class CaseResult(BaseModel):
    petitioner: Optional[str] = None
    respondent: Optional[str] = None
    filing_date: Optional[str] = None
    next_hearing_date: Optional[str] = None
    error: Optional[str] = None

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INDEX_PATH = os.path.join(BASE_DIR, "static", "index.html")

@app.get("/")
async def serve_index():
    return FileResponse(INDEX_PATH)

@app.post("/search", status_code=202)
async def start_search(request: CaseRequest, background_tasks: BackgroundTasks):
    job_id = str(uuid.uuid4())
    
    jobs[job_id] = {
        "status": "processing",
        "request": request.model_dump(),
        "result": None,
        "error": None
    }
    
    background_tasks.add_task(run_scraper_task, job_id, request)
    
    return {"job_id": job_id, "status": "processing"}

@app.get("/result/{job_id}")
async def get_result(job_id: str, db: Session = Depends(get_db)):
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs[job_id]
    
    if job["status"] == "processing":
        return {"status": "processing"}
    
    if job["error"]:
        return {"status": "error", "error": job["error"]}
    
    try:
        new_case = Case(
            job_id = job_id,
            case_type = job["request"]["case_type"],
            case_number = job["request"]["case_number"],
            case_year = job["request"]["case_year"],
            petitioner = job["result"]["petitioner"],
            respondent = job["result"]["respondent"],
            filing_date = job["result"]["filing_date"],
            next_hearing_date = job["result"]["next_hearing_date"]
        )

        db.add(new_case)
        db.commit()
    except:
        raise HTTPException(status_code=404, detail="Record not found")
    
    return {
        "status": "complete",
        "result": CaseResult(**job["result"]).model_dump()
    }

async def run_scraper_task(job_id: str, request: CaseRequest):
    try:
        result = await asyncio.to_thread(
            run_scraper,
            request.case_type,
            request.case_number,
            request.case_year
        )
        
        jobs[job_id].update({
            "status": "complete",
            "result": result,
            "error": None
        })
        
    except Exception as e:
        jobs[job_id].update({
            "status": "error",
            "result": None,
            "error": str(e)
        })