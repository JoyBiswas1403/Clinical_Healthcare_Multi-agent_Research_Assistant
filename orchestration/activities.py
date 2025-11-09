"""Temporal activities for agent execution and persistence."""
from temporalio import activity
from typing import Dict, Any
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from agents.query_filter_agent import QueryFilterAgent
from agents.retriever_summarizer_agent import RetrieverSummarizerAgent
from agents.fact_check_writer_agent import FactCheckWriterAgent
from data.models import ResearchRequestDB, ResearchStatus
from config.settings import settings


# Database setup
engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@activity.defn
async def run_query_filter_activity(request: Dict[str, Any]) -> Dict[str, Any]:
    """Execute Query+Filter Agent."""
    activity.logger.info("Executing Query+Filter Agent")
    
    agent = QueryFilterAgent()
    
    date_range = None
    if request.get("date_range_start") and request.get("date_range_end"):
        date_range = (request["date_range_start"], request["date_range_end"])
    
    result = agent.run(
        topic=request.get("topic"),
        max_sources=request.get("max_sources", 15),
        quality_threshold=request.get("quality_threshold", 0.7),
        include_gray_literature=request.get("include_gray_literature", False),
        date_range=date_range
    )
    
    return result.model_dump()


@activity.defn
async def run_retriever_summarizer_activity(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """Execute Retriever+Summarizer Agent."""
    activity.logger.info("Executing Retriever+Summarizer Agent")
    
    agent = RetrieverSummarizerAgent()
    
    expansion = input_data.get("expansion", {})
    expanded_queries = expansion.get("expanded_queries", [input_data.get("topic")])
    
    result = agent.run(
        topic=input_data.get("topic"),
        expanded_queries=expanded_queries,
        top_k=input_data.get("top_k", 20),
        rerank_top_k=settings.retriever_rerank_top_k
    )
    
    return result.model_dump()


@activity.defn
async def run_fact_check_writer_activity(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """Execute Fact-Check+Writer Agent."""
    activity.logger.info("Executing Fact-Check+Writer Agent")
    
    agent = FactCheckWriterAgent()
    
    result = agent.run(
        topic=input_data.get("topic"),
        retrieved_docs=input_data.get("retrieved_docs", []),
        summary_data=input_data.get("summary_data", {})
    )
    
    return result.model_dump()


@activity.defn
async def save_research_result_activity(data: Dict[str, Any]) -> Dict[str, Any]:
    """Save research results to database."""
    activity.logger.info(f"Saving research result for request_id: {data.get('request_id')}")
    
    db = SessionLocal()
    try:
        request_id = data.get("request_id")
        result = data.get("result", {})
        
        # Update research request record
        db_request = db.query(ResearchRequestDB).filter(
            ResearchRequestDB.id == request_id
        ).first()
        
        if db_request:
            db_request.status = result.get("status", ResearchStatus.COMPLETED.value)
            db_request.brief_data = result.get("brief")
            db_request.completed_at = datetime.utcnow()
            
            # Calculate processing time
            if db_request.created_at:
                processing_time = (datetime.utcnow() - db_request.created_at).total_seconds()
                db_request.processing_time_seconds = processing_time
            
            db.commit()
            activity.logger.info(f"Successfully saved research result for {request_id}")
        else:
            activity.logger.warning(f"Request {request_id} not found in database")
        
        return {"success": True}
    
    except Exception as e:
        db.rollback()
        activity.logger.error(f"Failed to save research result: {e}")
        return {"success": False, "error": str(e)}
    
    finally:
        db.close()
