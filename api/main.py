"""FastAPI application for Clinical Guideline Research Assistant."""
import uuid
from datetime import datetime
from typing import Optional
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import Counter, Histogram, generate_latest
from starlette.responses import Response
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from temporalio.client import Client as TemporalClient

from data.models import (
    ResearchRequest, ResearchResponse, ResearchStatus, 
    ResearchRequestDB, Base
)
from config.settings import settings
from orchestration.workflows import ResearchWorkflow


# ============================================================================
# App Initialization
# ============================================================================

app = FastAPI(
    title="Clinical Guideline Research Assistant",
    description="3-agent multi-agent system for healthcare clinical guideline research",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database
engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Temporal client (initialized on startup)
temporal_client: Optional[TemporalClient] = None


# ============================================================================
# Prometheus Metrics
# ============================================================================

research_requests_total = Counter(
    "research_requests_total",
    "Total number of research requests",
    ["status"]
)

research_duration_seconds = Histogram(
    "research_duration_seconds",
    "Time spent processing research requests"
)


# ============================================================================
# Dependencies
# ============================================================================

def get_db():
    """Database session dependency."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def verify_api_key(x_api_key: Optional[str] = Header(None)):
    """Simple API key authentication."""
    if not x_api_key:
        raise HTTPException(status_code=401, detail="API key required")
    # In production, validate against database
    return x_api_key


# ============================================================================
# Startup & Shutdown
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize connections on startup."""
    global temporal_client
    
    # Create database tables
    Base.metadata.create_all(bind=engine)
    
    # Connect to Temporal
    try:
        temporal_client = await TemporalClient.connect(
            f"{settings.temporal_host}:{settings.temporal_port}",
            namespace=settings.temporal_namespace
        )
        print(f"Connected to Temporal at {settings.temporal_host}:{settings.temporal_port}")
    except Exception as e:
        print(f"Failed to connect to Temporal: {e}")
        print("API will run but workflow execution will fail")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    pass


# ============================================================================
# API Routes
# ============================================================================

@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "service": "Clinical Guideline Research Assistant",
        "version": "1.0.0",
        "status": "operational"
    }


@app.get("/health")
async def health_check():
    """Detailed health check."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "temporal_connected": temporal_client is not None
    }


@app.post("/api/v1/research", response_model=ResearchResponse)
async def create_research_request(
    request: ResearchRequest,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Create a new research request and initiate workflow."""
    
    request_id = uuid.uuid4()
    
    # Save request to database
    db_request = ResearchRequestDB(
        id=request_id,
        topic=request.topic,
        max_sources=request.max_sources,
        quality_threshold=request.quality_threshold,
        include_gray_literature=request.include_gray_literature,
        date_range_start=request.date_range_start,
        date_range_end=request.date_range_end,
        status=ResearchStatus.PENDING.value,
        api_key_hash=api_key[:10]  # Store partial hash
    )
    
    db.add(db_request)
    db.commit()
    db.refresh(db_request)
    
    # Start Temporal workflow
    if temporal_client:
        try:
            workflow_input = {
                "request_id": str(request_id),
                "topic": request.topic,
                "max_sources": request.max_sources,
                "quality_threshold": request.quality_threshold,
                "include_gray_literature": request.include_gray_literature,
                "date_range_start": request.date_range_start,
                "date_range_end": request.date_range_end
            }
            
            await temporal_client.start_workflow(
                ResearchWorkflow.run,
                workflow_input,
                id=f"research-{request_id}",
                task_queue="research-queue"
            )
            
            db_request.status = ResearchStatus.PROCESSING.value
            db.commit()
            
            research_requests_total.labels(status="started").inc()
            
        except Exception as e:
            db_request.status = ResearchStatus.FAILED.value
            db_request.error = str(e)
            db.commit()
            
            research_requests_total.labels(status="failed").inc()
            raise HTTPException(status_code=500, detail=f"Failed to start workflow: {e}")
    else:
        raise HTTPException(status_code=503, detail="Workflow service unavailable")
    
    return ResearchResponse(
        request_id=str(request_id),
        status=ResearchStatus.PROCESSING,
        created_at=db_request.created_at
    )


@app.get("/api/v1/research/{request_id}", response_model=ResearchResponse)
async def get_research_result(
    request_id: str,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Get the status and result of a research request."""
    
    try:
        req_uuid = uuid.UUID(request_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid request ID format")
    
    db_request = db.query(ResearchRequestDB).filter(
        ResearchRequestDB.id == req_uuid
    ).first()
    
    if not db_request:
        raise HTTPException(status_code=404, detail="Research request not found")
    
    # Convert to response model
    response = ResearchResponse(
        request_id=str(db_request.id),
        status=ResearchStatus(db_request.status),
        brief=db_request.brief_data,
        error=db_request.error,
        created_at=db_request.created_at,
        completed_at=db_request.completed_at,
        processing_time_seconds=db_request.processing_time_seconds
    )
    
    return response


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    return Response(
        content=generate_latest(),
        media_type="text/plain"
    )


# ============================================================================
# Additional Utility Endpoints
# ============================================================================

@app.get("/api/v1/requests")
async def list_requests(
    limit: int = 10,
    offset: int = 0,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """List recent research requests."""
    
    requests = db.query(ResearchRequestDB).order_by(
        ResearchRequestDB.created_at.desc()
    ).offset(offset).limit(limit).all()
    
    return {
        "requests": [
            {
                "request_id": str(req.id),
                "topic": req.topic,
                "status": req.status,
                "created_at": req.created_at,
                "completed_at": req.completed_at
            }
            for req in requests
        ],
        "limit": limit,
        "offset": offset
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True
    )
