"""Data models for the clinical guideline research system."""
from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from sqlalchemy import Column, String, Integer, Float, JSON, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID
import uuid


Base = declarative_base()


# ============================================================================
# Pydantic Models (API & Internal)
# ============================================================================

class ResearchStatus(str, Enum):
    """Status of a research request."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ResearchRequest(BaseModel):
    """Input request for clinical guideline research."""
    topic: str = Field(..., description="Clinical research topic or query")
    max_sources: int = Field(default=15, ge=5, le=50, description="Maximum number of sources to retrieve")
    quality_threshold: float = Field(default=0.7, ge=0.0, le=1.0, description="Minimum source quality score")
    include_gray_literature: bool = Field(default=False, description="Include gray literature sources")
    date_range_start: Optional[str] = Field(default=None, description="Start date for publication filter (YYYY-MM-DD)")
    date_range_end: Optional[str] = Field(default=None, description="End date for publication filter (YYYY-MM-DD)")


class SourceMetadata(BaseModel):
    """Metadata for a single source."""
    source_id: str
    title: str
    authors: List[str]
    publication_date: Optional[str]
    doi: Optional[str]
    url: Optional[str]
    source_type: str  # journal_article, clinical_guideline, meta_analysis, etc.
    quality_score: float
    citation_count: Optional[int]


class Citation(BaseModel):
    """Individual citation in the brief."""
    citation_id: str
    source_id: str
    passage: str
    confidence: float


class RiskFlag(BaseModel):
    """Risk or quality flag identified in the research."""
    flag_type: str  # contradiction, contraindication, low_quality, bias, etc.
    severity: str  # high, medium, low
    description: str
    affected_sources: List[str]


class TraceabilityEntry(BaseModel):
    """Maps a claim to its supporting sources."""
    claim: str
    claim_location: str  # paragraph or sentence location in brief
    supporting_passages: List[Dict[str, Any]]  # source_id, passage, confidence
    verification_status: str  # verified, uncertain, unsupported


class ResearchBrief(BaseModel):
    """Complete research brief output."""
    executive_brief: str = Field(..., description="Main brief text (≤300 words)")
    word_count: int
    sources: List[SourceMetadata]
    citations: List[Citation]
    risk_flags: List[RiskFlag]
    traceability: List[TraceabilityEntry]
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ResearchResponse(BaseModel):
    """API response for research request."""
    request_id: str
    status: ResearchStatus
    brief: Optional[ResearchBrief] = None
    error: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
    processing_time_seconds: Optional[float] = None


class AgentOutput(BaseModel):
    """Generic output structure for agents."""
    agent_name: str
    output_data: Dict[str, Any]
    metrics: Dict[str, float] = Field(default_factory=dict)
    errors: List[str] = Field(default_factory=list)
    execution_time_ms: float


# ============================================================================
# SQLAlchemy Models (Database)
# ============================================================================

class ResearchRequestDB(Base):
    """Database model for research requests."""
    __tablename__ = "research_requests"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    topic = Column(Text, nullable=False)
    max_sources = Column(Integer, default=15)
    quality_threshold = Column(Float, default=0.7)
    include_gray_literature = Column(Boolean, default=False)
    date_range_start = Column(String(10), nullable=True)
    date_range_end = Column(String(10), nullable=True)
    
    status = Column(String(20), default=ResearchStatus.PENDING.value)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    processing_time_seconds = Column(Float, nullable=True)
    
    # Store full result as JSON
    brief_data = Column(JSON, nullable=True)
    error = Column(Text, nullable=True)
    
    # Metadata
    user_id = Column(String(255), nullable=True)
    api_key_hash = Column(String(255), nullable=True)


class DocumentDB(Base):
    """Database model for indexed documents."""
    __tablename__ = "documents"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(Text, nullable=False)
    authors = Column(JSON)  # List of author names
    publication_date = Column(String(10), nullable=True)
    doi = Column(String(255), unique=True, nullable=True)
    url = Column(Text, nullable=True)
    source_type = Column(String(50))
    
    # Content
    abstract = Column(Text, nullable=True)
    full_text = Column(Text, nullable=True)
    storage_path = Column(String(500), nullable=True)  # S3/MinIO path
    
    # Quality metrics
    quality_score = Column(Float, default=0.0)
    citation_count = Column(Integer, default=0)
    
    # Indexing metadata
    indexed_at = Column(DateTime, default=datetime.utcnow)
    embedding_id = Column(String(255), nullable=True)  # Reference to vector DB
    elasticsearch_id = Column(String(255), nullable=True)


class AuditLogDB(Base):
    """Audit log for all API requests."""
    __tablename__ = "audit_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    timestamp = Column(DateTime, default=datetime.utcnow)
    request_id = Column(UUID(as_uuid=True), nullable=True)
    endpoint = Column(String(255))
    method = Column(String(10))
    user_id = Column(String(255), nullable=True)
    api_key_hash = Column(String(255), nullable=True)
    ip_address = Column(String(45))
    response_status = Column(Integer)
    response_time_ms = Column(Float)
