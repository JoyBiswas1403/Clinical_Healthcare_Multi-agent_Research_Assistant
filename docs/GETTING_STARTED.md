# Getting Started Guide

## Prerequisites

- Docker & Docker Compose
- Python 3.11+
- OpenAI API key (or Anthropic)
- 8GB+ RAM recommended

## Quick Start (5 minutes)

### 1. Clone and Configure

```bash
cd clinical-guideline-assistant
cp .env.example .env
```

Edit `.env` and add your API keys:
```bash
OPENAI_API_KEY=sk-your-key-here
```

### 2. Start Infrastructure

```bash
docker-compose up -d
```

This starts:
- PostgreSQL (port 5432)
- Redis (port 6379)
- Elasticsearch (port 9200)
- Milvus (port 19530)
- MinIO (port 9002)
- Temporal (port 7233)
- Temporal UI (port 8088)
- Prometheus (port 9090)
- Jaeger (port 16686)

Wait 30-60 seconds for services to be ready.

### 3. Initialize Database

```bash
pip install -r requirements.txt
python scripts/init_db.py
```

### 4. Start Temporal Worker

In a new terminal:
```bash
python scripts/start_worker.py
```

### 5. Start API Server

In another terminal:
```bash
uvicorn api.main:app --reload --port 8000
```

### 6. Make Your First Request

```bash
curl -X POST http://localhost:8000/api/v1/research \
  -H "Content-Type: application/json" \
  -H "X-API-Key: dev-key" \
  -d '{
    "topic": "diabetes management in elderly patients",
    "max_sources": 10,
    "quality_threshold": 0.7
  }'
```

You'll receive a `request_id`. Check the status:

```bash
curl http://localhost:8000/api/v1/research/{request_id} \
  -H "X-API-Key: dev-key"
```

## Architecture Overview

### 3-Agent Pipeline

```
Request → Agent 1 (Query+Filter) → Agent 2 (Retriever+Summarizer) → Agent 3 (Fact-Check+Writer) → Response
```

**Agent 1: Query+Filter**
- Expands user query into optimized search terms
- Generates MeSH terms and synonyms
- Vets results for domain relevance and policy compliance

**Agent 2: Retriever+Summarizer**
- Hybrid BM25 (Elasticsearch) + Vector (Milvus) search
- Reciprocal rank fusion
- Hierarchical summarization with contradiction detection

**Agent 3: Fact-Check+Writer**
- Claim-level fact-checking
- Writes ≤300 word executive brief with inline citations
- Generates risk flags and traceability appendix

### Data Flow

1. API receives request → saves to PostgreSQL
2. Temporal workflow started
3. Agent 1 expands query
4. Agent 2 searches Elasticsearch + Milvus, summarizes
5. Agent 3 fact-checks, writes brief, maps claims to sources
6. Results saved to PostgreSQL
7. Client polls for completion

## Monitoring

### Temporal UI
http://localhost:8088

View workflow execution, retry history, and failures.

### Prometheus Metrics
http://localhost:9090

Query metrics like `research_requests_total`, `research_duration_seconds`.

### Jaeger Tracing
http://localhost:16686

Distributed tracing across agents and services.

### API Docs
http://localhost:8000/docs

Interactive OpenAPI documentation.

## Development Workflow

### Running Tests

```bash
pytest tests/ -v
pytest tests/test_agents.py::TestQueryFilterAgent -v
```

### Code Quality

```bash
# Type checking
mypy agents/ api/ orchestration/

# Linting
ruff check .

# Formatting
ruff format .
```

### Adding Documents

To index clinical documents for retrieval:

1. Upload PDF/DOCX to MinIO
2. Parse and extract text
3. Index in Elasticsearch (BM25)
4. Generate embeddings and store in Milvus

```python
# Example indexing script (create scripts/index_document.py)
from agents.retriever_summarizer_agent import RetrieverSummarizerAgent

agent = RetrieverSummarizerAgent()
# Add documents to ES and Milvus
```

## Production Considerations

### Security

- Replace `API_KEY_SECRET` in `.env`
- Implement proper API key validation in database
- Enable TLS for all services
- Use secrets management (AWS Secrets Manager, Vault)

### Scaling

- Use Kubernetes for orchestration
- Scale Temporal workers horizontally
- Use managed services (RDS, ElasticSearch Service, etc.)
- Implement caching layer (Redis)

### Cost Optimization

- Use smaller LLM models for non-critical tasks
- Batch requests where possible
- Cache query expansions
- Implement request deduplication

## Troubleshooting

### Worker Not Picking Up Tasks

- Check Temporal connection: `docker-compose logs temporal`
- Verify worker is running: `ps aux | grep start_worker`
- Check queue name matches in API and worker

### Elasticsearch Connection Failed

```bash
# Check if ES is ready
curl http://localhost:9200/_cluster/health

# View logs
docker-compose logs elasticsearch
```

### Out of Memory

- Increase Docker memory limit (Docker Desktop settings)
- Reduce `ES_JAVA_OPTS` heap size in docker-compose.yml
- Limit concurrent requests with rate limiting

### LLM API Errors

- Verify API keys in `.env`
- Check rate limits on OpenAI/Anthropic account
- Review error logs in worker terminal

## Next Steps

1. Review `docs/ARCHITECTURE.md` for detailed system design
2. Customize agent prompts in `agents/*.py`
3. Implement evaluation harness in `tests/eval_*.py`
4. Add custom document parsers
5. Integrate with your clinical data sources

## Support

For issues or questions:
- Check logs: `docker-compose logs [service-name]`
- Review Temporal UI for workflow failures
- Enable debug logging: `LOG_LEVEL=DEBUG` in `.env`
