# Complete Setup & Testing Guide

## Step-by-Step Setup

### Step 0: Choose Your LLM Option

**Option A: Ollama (FREE - Recommended for testing)**

1. Install Ollama:
```bash
# Windows
winget install Ollama.Ollama

# Linux/macOS
curl -fsSL https://ollama.com/install.sh | sh
```

2. Pull model:
```bash
ollama pull llama3.2:3b
```

3. Start Ollama (keep running in separate terminal):
```bash
ollama serve
```

4. In `.env`, ensure this is set:
```bash
USE_OLLAMA=true
```

**Option B: OpenAI (Costs money)**

1. Edit `.env` file:
```bash
# Windows
notepad .env

# Linux/macOS
nano .env
```

2. Update this line:
```bash
OPENAI_API_KEY=sk-your-actual-key-here
USE_OLLAMA=false
```

3. Save and close.

---

### Step 1: Configure Environment

Create `.env` from template:
```bash
# Windows
copy .env.example .env

# Linux/macOS
cp .env.example .env
```

### Step 2: Start Infrastructure

```bash
# Start all Docker services
docker-compose up -d

# Wait for services to be ready (~30 seconds)

# Check if services are running
docker-compose ps
```

You should see all services "Up" and "healthy".

### Step 3: Initialize Databases

```bash
# Install Python dependencies first
python -m pip install -r requirements.txt

# Initialize PostgreSQL, Elasticsearch, and Milvus
python scripts/init_db.py
```

Expected output:
```
============================================================
Clinical Guideline Assistant - Database Initialization
============================================================

Initializing PostgreSQL...
✓ PostgreSQL tables created

Initializing Elasticsearch...
✓ Elasticsearch index 'clinical_documents' created

Initializing Milvus...
✓ Milvus collection 'document_embeddings' created

============================================================
Initialization complete!
============================================================
```

### Step 4: Load Sample Clinical Documents

```powershell
python scripts/index_sample_documents.py
```

This will index 5 sample clinical papers about:
- Hypertension management in elderly
- Diabetes management guidelines
- Polypharmacy risks
- Cardiovascular risk assessment
- Anticoagulation therapy

Expected output:
```
======================================================================
Indexing Sample Clinical Documents
======================================================================

Connecting to Elasticsearch...
✓ Indexed to Elasticsearch: Hypertension Management in Elderly Patients...
✓ Indexed to Elasticsearch: Diabetes Management Guidelines...
[...]

Elasticsearch: 5/5 documents indexed

Connecting to Milvus...
Generating embeddings...
✓ Indexed to Milvus: Hypertension Management in Elderly Patients...
[...]

Milvus: 5/5 documents indexed
```

### Step 5: Test the System

**Quick Demo (recommended first):**
```bash
# Instant demo showing all 3 agents
python demo_quick.py

# Full pipeline with live Ollama (~25 seconds)
python demo_full_pipeline.py

# Single agent test
python test_with_ollama.py
```

### Step 6: Start Production Services (Optional)

**Start Temporal Worker** - Open a new terminal:

```bash
python scripts/start_worker.py
```

Expected output:
```
============================================================
Starting Temporal Worker
============================================================
Connected to Temporal at localhost:7233
Worker started. Waiting for tasks...
Press Ctrl+C to stop
============================================================
```

**Start API Server** - Open another new terminal:

```bash
python -m uvicorn api.main:app --reload --port 8000
```

Expected output:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
Connected to Temporal at localhost:7233
INFO:     Application startup complete.
```

## Testing the System

### Test 1: Health Check

```powershell
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2025-11-09T10:40:00.000Z",
  "temporal_connected": true
}
```

### Test 2: Create a Research Request

```powershell
$body = @{
    topic = "diabetes management in elderly patients"
    max_sources = 10
    quality_threshold = 0.7
} | ConvertTo-Json

$response = Invoke-RestMethod -Method Post -Uri "http://localhost:8000/api/v1/research" `
    -ContentType "application/json" `
    -Headers @{"X-API-Key"="dev-key"} `
    -Body $body

$response
```

You'll receive a `request_id`. Save it:

```powershell
$requestId = $response.request_id
Write-Host "Request ID: $requestId"
```

### Test 3: Check Request Status

Wait 30-60 seconds, then:

```powershell
$result = Invoke-RestMethod -Method Get `
    -Uri "http://localhost:8000/api/v1/research/$requestId" `
    -Headers @{"X-API-Key"="dev-key"}

$result
```

Expected result structure:
```json
{
  "request_id": "...",
  "status": "completed",
  "brief": {
    "executive_brief": "...(≤300 words with [1][2] citations)...",
    "word_count": 287,
    "sources": [...],
    "citations": [...],
    "risk_flags": [...],
    "traceability": [...]
  },
  "created_at": "...",
  "completed_at": "...",
  "processing_time_seconds": 45.3
}
```

### Test 4: Run Unit Tests

```powershell
pytest tests/test_agents.py -v
```

Expected output:
```
tests/test_agents.py::TestQueryFilterAgent::test_expand_query PASSED
tests/test_agents.py::TestQueryFilterAgent::test_agent_run PASSED
tests/test_agents.py::TestRetrieverSummarizerAgent::test_hybrid_fusion PASSED
tests/test_agents.py::TestFactCheckWriterAgent::test_extract_citations PASSED
tests/test_agents.py::TestFactCheckWriterAgent::test_agent_run PASSED

========== 5 passed in 2.34s ==========
```

## Monitoring & Debugging

### View API Documentation

Open in browser: http://localhost:8000/docs

Interactive Swagger UI to test all endpoints.

### Monitor Workflows (Temporal UI)

Open in browser: http://localhost:8088

- View running/completed workflows
- See workflow execution history
- Debug failures with stack traces

### Check Metrics (Prometheus)

Open in browser: http://localhost:9090

Query examples:
- `research_requests_total` - Total requests by status
- `research_duration_seconds` - Latency histogram

### View Traces (Jaeger)

Open in browser: http://localhost:16686

Search for traces to see:
- Agent execution times
- Database queries
- API calls

### Check Logs

**API logs:**
```powershell
# In the terminal running uvicorn
# Watch for request logs, errors
```

**Worker logs:**
```powershell
# In the terminal running start_worker.py
# Watch for agent execution, errors
```

**Docker service logs:**
```powershell
docker-compose logs elasticsearch  # Elasticsearch
docker-compose logs milvus        # Milvus
docker-compose logs postgres      # PostgreSQL
docker-compose logs temporal      # Temporal
```

## Troubleshooting

### Issue: "Elasticsearch connection failed"

```bash
# Check if Elasticsearch is running
docker-compose ps elasticsearch

# Check Elasticsearch health (note: port 9201, not 9200)
curl http://localhost:9201/_cluster/health

# Restart if needed
docker-compose restart elasticsearch
# Wait 30 seconds for service to be ready
```

### Issue: "Milvus connection failed"

```powershell
# Check Milvus status
docker-compose ps milvus

# Check logs
docker-compose logs milvus

# Restart if needed
docker-compose restart milvus milvus-etcd milvus-minio
Start-Sleep -Seconds 30
```

### Issue: "Temporal workflow not starting"

```powershell
# Verify worker is running
# Check the terminal running start_worker.py

# Check Temporal UI
# Open http://localhost:8088
# Look for error messages

# Restart worker
# Press Ctrl+C in worker terminal, then:
python scripts/start_worker.py
```

### Issue: "OpenAI API key error"

```powershell
# Verify your .env file has the correct key
Get-Content .env | Select-String "OPENAI_API_KEY"

# Make sure to restart API server after changing .env
# Press Ctrl+C in API terminal, then:
uvicorn api.main:app --reload --port 8000
```

### Issue: "Out of memory"

```powershell
# Reduce Docker memory usage
# Edit docker-compose.yml, change:
# ES_JAVA_OPTS=-Xms512m -Xmx512m  # (reduce if needed)

# Restart services
docker-compose down
docker-compose up -d
```

## Next Steps

### Customize Agent Prompts

Edit the prompt templates in:
- `agents/query_filter_agent.py` - Lines 9-27, 30-55
- `agents/retriever_summarizer_agent.py` - Lines 12-43
- `agents/fact_check_writer_agent.py` - Lines 13-93

### Add More Documents

Create your own indexing script or extend `scripts/index_sample_documents.py`:

```python
# Add to SAMPLE_DOCUMENTS list
{
    "title": "Your Paper Title",
    "authors": ["Author A", "Author B"],
    "abstract": "Paper abstract...",
    "doi": "10.xxxx/xxxxx",
    # ... other fields
}
```

### Deploy to Production

1. **Build Docker image:**
```powershell
docker build -f docker/Dockerfile -t clinical-guideline-assistant:latest .
```

2. **Use managed services:**
- Replace PostgreSQL with RDS
- Replace Elasticsearch with AWS OpenSearch
- Replace Milvus with Pinecone/Weaviate Cloud
- Use AWS Secrets Manager for API keys

3. **Scale workers:**
```powershell
# Run multiple worker instances
python scripts/start_worker.py &  # Instance 1
python scripts/start_worker.py &  # Instance 2
python scripts/start_worker.py &  # Instance 3
```

## Support & Resources

- **API Documentation**: http://localhost:8000/docs
- **Temporal UI**: http://localhost:8088
- **Project Summary**: `PROJECT_SUMMARY.md`
- **Getting Started**: `docs/GETTING_STARTED.md`

## Success Checklist

- [ ] `.env` configured with API keys
- [ ] Docker services running (10 containers)
- [ ] Databases initialized (PostgreSQL, Elasticsearch, Milvus)
- [ ] Sample documents indexed (5 papers)
- [ ] Temporal worker running
- [ ] API server running
- [ ] Health check returns `healthy`
- [ ] Research request completes successfully
- [ ] Tests pass (`pytest tests/ -v`)

Once all checked, you're ready to customize and deploy! 🚀
