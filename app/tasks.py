from celery import current_task
from app.celery_app import celery_app
from app.database import SessionLocal
from app.models import AttackSimulationJob, SimulationResult, JobStatus
from app.security_tools import SecurityToolRunner
from app.report_generator import PDFReportGenerator
from app.enhanced_report_generator import EnhancedPDFReportGenerator
from app.ai_service import AIOrchestrator
from app.storage import StorageManager
from datetime import datetime
import logging
import asyncio

logger = logging.getLogger(__name__)


@celery_app.task(bind=True)
def run_simulation_task(self, job_id: int):
    """Run security simulation task with AI enhancement"""
    db = SessionLocal()
    
    try:
        # Get the job
        job = db.query(AttackSimulationJob).filter(AttackSimulationJob.id == job_id).first()
        if not job:
            logger.error(f"Job {job_id} not found")
            return
        
        # Update job status to running
        job.status = JobStatus.RUNNING
        job.started_at = datetime.utcnow()
        db.commit()
        
        # Update task state
        current_task.update_state(
            state="RUNNING",
            meta={"job_id": job_id, "status": "Running security simulation"}
        )
        
        # Run the security tool
        tool_runner = SecurityToolRunner()
        result = tool_runner.run_tool(
            tool_name=job.simulation_tool.value,
            target_description=job.target_system_description,
            severity_level=job.severity_level.value,
            attack_vectors=job.number_of_attack_vectors
        )
        
        # Update task state
        current_task.update_state(
            state="RUNNING",
            meta={"job_id": job_id, "status": "Performing AI analysis"}
        )
        
        # Perform AI analysis (run in event loop for async compatibility)
        ai_orchestrator = AIOrchestrator()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            ai_result = loop.run_until_complete(
                ai_orchestrator.analyze_simulation_results(job, result)
            )
        finally:
            loop.close()
        
        # Update task state
        current_task.update_state(
            state="RUNNING",
            meta={"job_id": job_id, "status": "Generating enhanced report"}
        )
        
        # Generate enhanced PDF report with AI analysis
        report_generator = EnhancedPDFReportGenerator()
        pdf_content = report_generator.generate_enhanced_report(
            job=job,
            ai_result=ai_result,
            tool_output=result.get("output", "")
        )
        
        # Store PDF and get signed URL
        storage_manager = StorageManager()
        pdf_url = storage_manager.store_pdf(
            pdf_content=pdf_content,
            filename=f"ai_enhanced_report_job_{job_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.pdf"
        )
        
        # Create simulation result with AI analysis
        simulation_result = SimulationResult(
            job_id=job.id,
            tool_output=result.get("output", ""),
            vulnerabilities_found=result.get("vulnerabilities", []),
            risk_score=ai_result.risk_score,  # Use AI-calculated risk score
            pdf_report_url=pdf_url
        )
        
        db.add(simulation_result)
        
        # Update job status to completed
        job.status = JobStatus.COMPLETED
        job.completed_at = datetime.utcnow()
        
        db.commit()
        
        # Update task state
        current_task.update_state(
            state="SUCCESS",
            meta={
                "job_id": job_id,
                "status": "Completed with AI enhancement",
                "pdf_url": pdf_url,
                "ai_risk_score": ai_result.risk_score,
                "ai_confidence": ai_result.confidence_score,
                "ai_cost": ai_result.cost_estimate,
                "vulnerabilities_found": len(ai_result.vulnerabilities),
                "mitigations_provided": len(ai_result.mitigations)
            }
        )
        
        logger.info(f"Job {job_id} completed successfully with AI enhancement")
        logger.info(f"AI Analysis - Risk Score: {ai_result.risk_score}, "
                   f"Confidence: {ai_result.confidence_score:.1%}, "
                   f"Cost: ${ai_result.cost_estimate:.4f}")
        
    except Exception as e:
        logger.error(f"Error running job {job_id}: {str(e)}")
        
        # Update job status to failed
        if job:
            job.status = JobStatus.FAILED
            job.completed_at = datetime.utcnow()
            db.commit()
        
        # Update task state
        current_task.update_state(
            state="FAILURE",
            meta={"job_id": job_id, "error": str(e)}
        )
        
        raise
    
    finally:
        db.close()


@celery_app.task
def run_ai_analysis_task(self, job_id: int):
    """Run AI analysis on existing simulation results"""
    db = SessionLocal()
    
    try:
        # Get the job and results
        job = db.query(AttackSimulationJob).filter(AttackSimulationJob.id == job_id).first()
        if not job:
            logger.error(f"Job {job_id} not found")
            return
        
        result = db.query(SimulationResult).filter(SimulationResult.job_id == job_id).first()
        if not result:
            logger.error(f"No results found for job {job_id}")
            return
        
        # Update task state
        current_task.update_state(
            state="RUNNING",
            meta={"job_id": job_id, "status": "Performing AI analysis on existing results"}
        )
        
        # Perform AI analysis (run in event loop for async compatibility)
        ai_orchestrator = AIOrchestrator()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            ai_result = loop.run_until_complete(
                ai_orchestrator.analyze_simulation_results(job, result)
            )
        finally:
            loop.close()
        
        # Update task state
        current_task.update_state(
            state="RUNNING",
            meta={"job_id": job_id, "status": "Generating enhanced report"}
        )
        
        # Generate enhanced PDF report
        report_generator = EnhancedPDFReportGenerator()
        pdf_content = report_generator.generate_enhanced_report(
            job=job,
            ai_result=ai_result,
            tool_output=result.tool_output or ""
        )
        
        # Store enhanced PDF
        storage_manager = StorageManager()
        enhanced_pdf_url = storage_manager.store_pdf(
            pdf_content=pdf_content,
            filename=f"ai_enhanced_report_job_{job_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.pdf"
        )
        
        # Update the result with AI analysis data
        result.risk_score = ai_result.risk_score
        result.pdf_report_url = enhanced_pdf_url
        
        db.commit()
        
        # Update task state
        current_task.update_state(
            state="SUCCESS",
            meta={
                "job_id": job_id,
                "status": "AI analysis completed",
                "enhanced_pdf_url": enhanced_pdf_url,
                "ai_risk_score": ai_result.risk_score,
                "ai_confidence": ai_result.confidence_score,
                "ai_cost": ai_result.cost_estimate
            }
        )
        
        logger.info(f"AI analysis completed for job {job_id}")
        
    except Exception as e:
        logger.error(f"Error in AI analysis for job {job_id}: {str(e)}")
        
        # Update task state
        current_task.update_state(
            state="FAILURE",
            meta={"job_id": job_id, "error": str(e)}
        )
        
        raise
    
    finally:
        db.close()


@celery_app.task
def cleanup_old_jobs():
    """Clean up old completed jobs (older than 30 days)"""
    db = SessionLocal()
    
    try:
        from datetime import timedelta
        
        cutoff_date = datetime.utcnow() - timedelta(days=30)
        
        # Find old completed jobs
        old_jobs = db.query(AttackSimulationJob).filter(
            AttackSimulationJob.status == JobStatus.COMPLETED,
            AttackSimulationJob.completed_at < cutoff_date
        ).all()
        
        for job in old_jobs:
            # Delete associated results
            db.query(SimulationResult).filter(SimulationResult.job_id == job.id).first()
            # Delete the job
            db.delete(job)
        
        db.commit()
        logger.info(f"Cleaned up {len(old_jobs)} old jobs")
        
    except Exception as e:
        logger.error(f"Error cleaning up old jobs: {str(e)}")
        db.rollback()
        raise
    
    finally:
        db.close()


@celery_app.task
def analyze_job_batch():
    """Analyze multiple jobs in batch for cost optimization"""
    db = SessionLocal()
    
    try:
        # Find jobs that need AI analysis
        pending_jobs = db.query(AttackSimulationJob).filter(
            AttackSimulationJob.status == JobStatus.COMPLETED
        ).limit(10).all()  # Process in batches
        
        if not pending_jobs:
            logger.info("No jobs pending for AI analysis")
            return
        
        logger.info(f"Starting batch AI analysis for {len(pending_jobs)} jobs")
        
        # Process jobs in parallel (within cost limits)
        total_cost = 0.0
        processed_jobs = 0
        
        for job in pending_jobs:
            try:
                # Check if we're within cost limits
                if total_cost >= 0.05:  # $0.05 batch limit
                    logger.info(f"Batch cost limit reached: ${total_cost:.4f}")
                    break
                
                # Run AI analysis (run in event loop for async compatibility)
                ai_orchestrator = AIOrchestrator()
                result = db.query(SimulationResult).filter(SimulationResult.job_id == job.id).first()
                
                if result:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    try:
                        ai_result = loop.run_until_complete(
                            ai_orchestrator.analyze_simulation_results(job, result)
                        )
                    finally:
                        loop.close()
                    
                    total_cost += ai_result.cost_estimate
                    processed_jobs += 1
                    
                    logger.info(f"Processed job {job.id}, cost: ${ai_result.cost_estimate:.4f}, "
                               f"total: ${total_cost:.4f}")
                
            except Exception as e:
                logger.error(f"Error processing job {job.id}: {str(e)}")
                continue
        
        logger.info(f"Batch processing completed. Processed: {processed_jobs}, "
                   f"Total cost: ${total_cost:.4f}")
        
    except Exception as e:
        logger.error(f"Error in batch analysis: {str(e)}")
        raise
    
    finally:
        db.close() 