from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from app.database import get_db
from app.models import User, AttackSimulationJob, SimulationResult
from app.auth import get_current_active_user
from app.ai_service import AIOrchestrator
from app.celery_app import run_ai_analysis_task
from app.schemas import JobResponse
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ai", tags=["AI analysis"])


@router.get("/models")
async def get_available_models(
    current_user: User = Depends(get_current_active_user)
) -> List[Dict[str, str]]:
    """Get list of available AI models and their status"""
    try:
        ai_orchestrator = AIOrchestrator()
        models = await ai_orchestrator.get_available_models()
        return models
    except Exception as e:
        logger.error(f"Error getting available models: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve AI model information"
        )


@router.post("/analyze/{job_id}")
async def request_ai_analysis(
    job_id: int,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Request AI analysis for an existing simulation job"""
    
    # Verify job exists and belongs to user
    job = db.query(AttackSimulationJob).filter(
        AttackSimulationJob.id == job_id,
        AttackSimulationJob.user_id == current_user.id
    ).first()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Check if job has results
    result = db.query(SimulationResult).filter(SimulationResult.job_id == job_id).first()
    if not result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No simulation results found for this job"
        )
    
    # Check if AI analysis is already available
    if result.risk_score and result.risk_score > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="AI analysis already completed for this job"
        )
    
    try:
        # Start AI analysis in background
        background_tasks.add_task(run_ai_analysis_task, job_id)
        
        return {
            "message": "AI analysis started",
            "job_id": job_id,
            "status": "processing",
            "estimated_completion": "5-10 minutes"
        }
        
    except Exception as e:
        logger.error(f"Error starting AI analysis for job {job_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to start AI analysis"
        )


@router.get("/status/{job_id}")
async def get_ai_analysis_status(
    job_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get the status of AI analysis for a specific job"""
    
    # Verify job exists and belongs to user
    job = db.query(AttackSimulationJob).filter(
        AttackSimulationJob.id == job_id,
        AttackSimulationJob.user_id == current_user.id
    ).first()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Get simulation result
    result = db.query(SimulationResult).filter(SimulationResult.job_id == job_id).first()
    if not result:
        return {
            "job_id": job_id,
            "ai_status": "no_results",
            "message": "No simulation results found"
        }
    
    # Check AI analysis status
    if result.risk_score and result.risk_score > 0:
        return {
            "job_id": job_id,
            "ai_status": "completed",
            "risk_score": result.risk_score,
            "pdf_url": result.pdf_report_url,
            "message": "AI analysis completed successfully"
        }
    else:
        return {
            "job_id": job_id,
            "ai_status": "pending",
            "message": "AI analysis not yet performed"
        }


@router.get("/costs")
async def get_ai_cost_summary(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get AI analysis cost summary for the current user"""
    
    try:
        # Get all completed jobs for the user
        completed_jobs = db.query(AttackSimulationJob).filter(
            AttackSimulationJob.user_id == current_user.id,
            AttackSimulationJob.status == "completed"
        ).all()
        
        total_jobs = len(completed_jobs)
        ai_analyzed_jobs = 0
        estimated_total_cost = 0.0
        
        for job in completed_jobs:
            result = db.query(SimulationResult).filter(SimulationResult.job_id == job.id).first()
            if result and result.risk_score and result.risk_score > 0:
                ai_analyzed_jobs += 1
                # Estimate cost based on typical analysis
                estimated_total_cost += 0.002  # $0.002 per job (Groq pricing)
        
        return {
            "total_jobs": total_jobs,
            "ai_analyzed_jobs": ai_analyzed_jobs,
            "estimated_total_cost": round(estimated_total_cost, 4),
            "cost_per_job": 0.002,
            "currency": "USD"
        }
        
    except Exception as e:
        logger.error(f"Error getting AI cost summary: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve cost information"
        )


@router.post("/batch-analyze")
async def request_batch_ai_analysis(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Request AI analysis for multiple completed jobs (batch processing)"""
    
    try:
        # Find jobs that need AI analysis
        pending_jobs = db.query(AttackSimulationJob).filter(
            AttackSimulationJob.user_id == current_user.id,
            AttackSimulationJob.status == "completed"
        ).all()
        
        if not pending_jobs:
            return {
                "message": "No jobs pending for AI analysis",
                "jobs_queued": 0
            }
        
        # Queue jobs for AI analysis
        queued_count = 0
        for job in pending_jobs:
            result = db.query(SimulationResult).filter(SimulationResult.job_id == job.id).first()
            if result and (not result.risk_score or result.risk_score == 0):
                background_tasks.add_task(run_ai_analysis_task, job.id)
                queued_count += 1
        
        return {
            "message": f"Batch AI analysis started for {queued_count} jobs",
            "jobs_queued": queued_count,
            "estimated_completion": f"{queued_count * 5}-{queued_count * 10} minutes"
        }
        
    except Exception as e:
        logger.error(f"Error starting batch AI analysis: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to start batch AI analysis"
        )


@router.get("/health")
async def ai_service_health() -> Dict[str, Any]:
    """Check AI service health and availability"""
    
    try:
        ai_orchestrator = AIOrchestrator()
        models = await ai_orchestrator.get_available_models()
        
        # Check if any AI models are available
        ai_available = any(
            model["provider"] != "fallback" and model["status"] == "available" 
            for model in models
        )
        
        return {
            "status": "healthy",
            "ai_available": ai_available,
            "available_models": len([m for m in models if m["status"] == "available"]),
            "fallback_available": True,  # Always available
            "timestamp": "2024-01-01T00:00:00Z"  # You can make this dynamic
        }
        
    except Exception as e:
        logger.error(f"Error checking AI service health: {e}")
        return {
            "status": "degraded",
            "ai_available": False,
            "available_models": 0,
            "fallback_available": True,
            "error": str(e),
            "timestamp": "2024-01-01T00:00:00Z"
        } 