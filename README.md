# Clinical Guideline Research Assistant

A production-ready 3-agent multi-agent system for healthcare clinical guideline research briefs with full provenance tracking.

## Architecture

### Three-Agent Pipeline

1. **Query+Filter Agent**: Policy-aware search query expansion and domain vetting
2. **Retriever+Summarizer Agent**: Hybrid BM25+vector retrieval with hierarchical summarization
3. **Fact-Check+Writer Agent**: Claim-level verification, inline citations, and traceability appendix

### Tech Stack

- **Gateway**: FastAPI
- **Orchestration**: Temporal/Celery
- **Search**: Elasticsearch (BM25)
- **Vector DB**: Milvus/Weaviate
- **Storage**: MinIO/S3 + PostgreSQL
- **Parsing**: PyMuPDF, Unstructured
- **Observability**: Prometheus, Jaeger, OpenTelemetry

## Deliverables

Each research request generates:
- **Executive Brief**: ≤300 words with inline citations
- **Source List**: DOIs, URLs, publication metadata
- **Risk Flags**: Contradictions, contraindications, study quality issues
- **Traceability Appendix**: Every claim mapped to source passages

## Quick Start

```bash
# Copy environment template
cp .env.example .env

# Start infrastructure
docker-compose up -d

# Install dependencies
pip install -r requirements.txt

# Run migrations
python scripts/init_db.py

# Start API
uvicorn api.main:app --reload --port 8000
```

## API Usage

```bash
curl -X POST http://localhost:8000/api/v1/research \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "hypertension management in elderly patients",
    "max_sources": 15,
    "quality_threshold": 0.7
  }'
```

## Project Structure

```
├── agents/              # Three agent implementations
├── api/                 # FastAPI gateway
├── orchestration/       # Temporal workflows
├── data/                # Schemas, models, repositories
├── config/              # Configuration management
├── docker/              # Dockerfiles and compose
├── docs/                # Additional documentation
├── tests/               # Test suite
└── scripts/             # Utilities and migrations
```

## Development

```bash
# Run tests
pytest tests/ -v

# Type checking
mypy agents/ api/ orchestration/

# Linting
ruff check .

# Format
ruff format .
```

## KPIs & Monitoring

- **Retrieval Recall@10**: Target >0.85
- **Fact-Check Precision**: Target >0.95
- **Brief Quality Score**: Target >4.2/5
- **Latency P95**: Target <45s end-to-end

Metrics exposed at `/metrics` endpoint.

## Security

- API key authentication
- Rate limiting (100 req/hour per key)
- PII detection and redaction
- Audit logging for all requests

## License

MIT
