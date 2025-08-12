from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models import User, AttackSimulationJob, SimulationResult, JobStatus
from app.schemas import (
    AttackSimulationJobCreate, 
    AttackSimulationJob as JobSchema,
    SimulationResult as ResultSchema,
    JobResponse,
    JobsListResponse
)
from app.auth import get_current_active_user
from app.celery_app import run_simulation_task
from datetime import datetime

router = APIRouter(prefix="/jobs", tags=["attack simulation jobs"])


@router.post("/", response_model=JobSchema)
async def create_job(
    job: AttackSimulationJobCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks = None
):
    """Create a new attack simulation job"""
    # Create the job
    db_job = AttackSimulationJob(
        user_id=current_user.id,
        **job.dict()
    )
    
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    
    # Start the simulation task in background
    if background_tasks:
        background_tasks.add_task(run_simulation_task, db_job.id)
    
    return db_job


@router.get("/", response_model=JobsListResponse)
async def get_jobs(
    skip: int = 0,
    limit: int = 100,
    status_filter: Optional[JobStatus] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all jobs for the current user"""
    query = db.query(AttackSimulationJob).filter(AttackSimulationJob.user_id == current_user.id)
    
    if status_filter:
        query = query.filter(AttackSimulationJob.status == status_filter)
    
    total = query.count()
    jobs = query.offset(skip).limit(limit).all()
    
    return JobsListResponse(jobs=jobs, total=total)


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific job by ID"""
    job = db.query(AttackSimulationJob).filter(
        AttackSimulationJob.id == job_id,
        AttackSimulationJob.user_id == current_user.id
    ).first()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Get the result if it exists
    result = db.query(SimulationResult).filter(SimulationResult.job_id == job_id).first()
    
    return JobResponse(job=job, result=result)


@router.delete("/{job_id}")
async def delete_job(
    job_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a job (only if it's not running)"""
    job = db.query(AttackSimulationJob).filter(
        AttackSimulationJob.id == job_id,
        AttackSimulationJob.user_id == current_user.id
    ).first()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    if job.status == JobStatus.RUNNING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete a running job"
        )
    
    # Delete associated results first
    db.query(SimulationResult).filter(SimulationResult.job_id == job_id).delete()
    
    # Delete the job
    db.delete(job)
    db.commit()
    
    return {"message": "Job deleted successfully"}


@router.put("/{job_id}/status")
async def update_job_status(
    job_id: int,
    status_update: dict,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update job status (admin only or for status updates)"""
    job = db.query(AttackSimulationJob).filter(
        AttackSimulationJob.id == job_id,
        AttackSimulationJob.user_id == current_user.id
    ).first()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Update status
    if "status" in status_update:
        job.status = status_update["status"]
    
    if "started_at" in status_update and status_update["started_at"]:
        job.started_at = datetime.fromisoformat(status_update["started_at"])
    
    if "completed_at" in status_update and status_update["completed_at"]:
        job.completed_at = datetime.fromisoformat(status_update["completed_at"])
    
    db.commit()
    db.refresh(job)
    
    return job 