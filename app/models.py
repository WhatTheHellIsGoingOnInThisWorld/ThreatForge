from sqlalchemy import Column, Integer, String, DateTime, Text, Enum, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum


class SeverityLevel(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SimulationTool(str, enum.Enum):
    METASPLOIT = "metasploit"
    OPENVAS = "openvas"
    CALDERA = "caldera"


class JobStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    jobs = relationship("AttackSimulationJob", back_populates="user")


class AttackSimulationJob(Base):
    __tablename__ = "attack_simulation_jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    target_system_description = Column(Text, nullable=False)
    simulation_tool = Column(Enum(SimulationTool), nullable=False)
    severity_level = Column(Enum(SeverityLevel), nullable=False)
    number_of_attack_vectors = Column(Integer, nullable=False)
    status = Column(Enum(JobStatus), default=JobStatus.PENDING)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="jobs")
    results = relationship("SimulationResult", back_populates="job")


class SimulationResult(Base):
    __tablename__ = "simulation_results"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("attack_simulation_jobs.id"), nullable=False)
    tool_output = Column(Text, nullable=True)
    vulnerabilities_found = Column(JSON, nullable=True)
    risk_score = Column(Integer, nullable=True)
    pdf_report_url = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    job = relationship("AttackSimulationJob", back_populates="results") 