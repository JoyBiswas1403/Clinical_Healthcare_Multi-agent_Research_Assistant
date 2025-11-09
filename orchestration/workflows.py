"""Temporal workflows for orchestrating the 3-agent research pipeline."""
from datetime import timedelta
from temporalio import workflow
from temporalio.common import RetryPolicy
from typing import Dict, Any
import asyncio

from data.models import ResearchRequest, ResearchResponse, ResearchStatus, ResearchBrief
from orchestration.activities import (
    run_query_filter_activity,
    run_retriever_summarizer_activity,
    run_fact_check_writer_activity,
    save_research_result_activity
)


@workflow.defn
class ResearchWorkflow:
    """Main workflow orchestrating the 3-agent research pipeline."""
    
    @workflow.run
    async def run(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the complete research pipeline.
        
        Flow:
        1. Query+Filter Agent → expand queries and vet domain
        2. Retriever+Summarizer Agent → hybrid search and summarization
        3. Fact-Check+Writer Agent → verify claims and write brief
        4. Save results to database
        """
        
        retry_policy = RetryPolicy(
            initial_interval=timedelta(seconds=1),
            maximum_interval=timedelta(seconds=10),
            maximum_attempts=3
        )
        
        workflow.logger.info(f"Starting research workflow for topic: {request.get('topic')}")
        
        # Agent 1: Query+Filter
        workflow.logger.info("Running Query+Filter Agent...")
        agent1_output = await workflow.execute_activity(
            run_query_filter_activity,
            request,
            start_to_close_timeout=timedelta(seconds=60),
            retry_policy=retry_policy
        )
        
        if agent1_output.get("errors"):
            return {
                "status": ResearchStatus.FAILED.value,
                "error": f"Query+Filter Agent failed: {agent1_output['errors']}"
            }
        
        # Agent 2: Retriever+Summarizer
        workflow.logger.info("Running Retriever+Summarizer Agent...")
        agent2_input = {
            "topic": request.get("topic"),
            "expansion": agent1_output.get("output_data", {}).get("expansion", {}),
            "top_k": request.get("max_sources", 15)
        }
        
        agent2_output = await workflow.execute_activity(
            run_retriever_summarizer_activity,
            agent2_input,
            start_to_close_timeout=timedelta(seconds=120),
            retry_policy=retry_policy
        )
        
        if agent2_output.get("errors"):
            return {
                "status": ResearchStatus.FAILED.value,
                "error": f"Retriever+Summarizer Agent failed: {agent2_output['errors']}"
            }
        
        # Agent 3: Fact-Check+Writer
        workflow.logger.info("Running Fact-Check+Writer Agent...")
        agent3_input = {
            "topic": request.get("topic"),
            "retrieved_docs": agent2_output.get("output_data", {}).get("retrieved_documents", []),
            "summary_data": agent2_output.get("output_data", {}).get("summary", {})
        }
        
        agent3_output = await workflow.execute_activity(
            run_fact_check_writer_activity,
            agent3_input,
            start_to_close_timeout=timedelta(seconds=120),
            retry_policy=retry_policy
        )
        
        if agent3_output.get("errors"):
            return {
                "status": ResearchStatus.FAILED.value,
                "error": f"Fact-Check+Writer Agent failed: {agent3_output['errors']}"
            }
        
        # Save results
        workflow.logger.info("Saving research results...")
        research_brief = agent3_output.get("output_data", {}).get("research_brief")
        
        result = {
            "status": ResearchStatus.COMPLETED.value,
            "brief": research_brief,
            "metrics": {
                "agent1_time_ms": agent1_output.get("execution_time_ms", 0),
                "agent2_time_ms": agent2_output.get("execution_time_ms", 0),
                "agent3_time_ms": agent3_output.get("execution_time_ms", 0),
                "total_time_ms": (
                    agent1_output.get("execution_time_ms", 0) +
                    agent2_output.get("execution_time_ms", 0) +
                    agent3_output.get("execution_time_ms", 0)
                )
            }
        }
        
        await workflow.execute_activity(
            save_research_result_activity,
            {
                "request_id": request.get("request_id"),
                "result": result
            },
            start_to_close_timeout=timedelta(seconds=30),
            retry_policy=retry_policy
        )
        
        workflow.logger.info("Research workflow completed successfully")
        return result
