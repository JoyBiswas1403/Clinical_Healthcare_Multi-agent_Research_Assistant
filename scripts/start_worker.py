"""Start Temporal worker to process research workflows."""
import asyncio
import sys
sys.path.append(".")

from temporalio.client import Client
from temporalio.worker import Worker

from orchestration.workflows import ResearchWorkflow
from orchestration.activities import (
    run_query_filter_activity,
    run_retriever_summarizer_activity,
    run_fact_check_writer_activity,
    save_research_result_activity
)
from config.settings import settings


async def main():
    """Start the Temporal worker."""
    print("=" * 60)
    print("Starting Temporal Worker")
    print("=" * 60)
    
    # Connect to Temporal
    client = await Client.connect(
        f"{settings.temporal_host}:{settings.temporal_port}",
        namespace=settings.temporal_namespace
    )
    
    print(f"Connected to Temporal at {settings.temporal_host}:{settings.temporal_port}")
    
    # Create and run worker
    worker = Worker(
        client,
        task_queue="research-queue",
        workflows=[ResearchWorkflow],
        activities=[
            run_query_filter_activity,
            run_retriever_summarizer_activity,
            run_fact_check_writer_activity,
            save_research_result_activity
        ]
    )
    
    print("Worker started. Waiting for tasks...")
    print("Press Ctrl+C to stop")
    print("=" * 60)
    
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
