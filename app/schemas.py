from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.models import SeverityLevel, SimulationTool, JobStatus


# User schemas
class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    password: str


class UserLogin(UserBase):
    password: str


class User(UserBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# Token schemas
class Token(BaseModel):
    access_token: str
    token_type: str
    refresh_token: str


class TokenData(BaseModel):
    email: Optional[str] = None


# Attack Simulation Job schemas
class AttackSimulationJobBase(BaseModel):
    target_system_description: str
    simulation_tool: SimulationTool
    severity_level: SeverityLevel
    number_of_attack_vectors: int


class AttackSimulationJobCreate(AttackSimulationJobBase):
    pass


class AttackSimulationJob(AttackSimulationJobBase):
    id: int
    user_id: int
    status: JobStatus
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Simulation Result schemas
class SimulationResultBase(BaseModel):
    tool_output: Optional[str] = None
    vulnerabilities_found: Optional[Dict[str, Any]] = None
    risk_score: Optional[int] = None
    pdf_report_url: Optional[str] = None


class SimulationResultCreate(SimulationResultBase):
    job_id: int


class SimulationResult(SimulationResultBase):
    id: int
    job_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# Job Status Update
class JobStatusUpdate(BaseModel):
    status: JobStatus
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


# Response schemas
class JobResponse(BaseModel):
    job: AttackSimulationJob
    result: Optional[SimulationResult] = None


class JobsListResponse(BaseModel):
    jobs: List[AttackSimulationJob]
    total: int 