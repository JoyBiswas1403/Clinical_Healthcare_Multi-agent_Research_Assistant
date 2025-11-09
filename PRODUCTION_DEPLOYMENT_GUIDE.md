# Clinical Guideline Assistant - Production Deployment Guide (Windows CMD)

## 📋 Prerequisites Checklist

Before starting, ensure you have:
- ✅ Docker Desktop installed and running
- ✅ Python 3.11 installed at `C:\Users\bjoy2\AppData\Local\Programs\Python\Python311\`
- ✅ Ollama installed (for free LLM) OR OpenAI API key (costs money)
- ✅ Git installed (optional, for version control)

---

## 🚀 Step-by-Step Production Deployment

### **STEP 1: Navigate to Project Directory**

```cmd
cd C:\Users\bjoy2\clinical-guideline-assistant
```

---

### **STEP 2: Verify Environment Configuration**

Check that your `.env` file exists and has correct settings:

```cmd
type .env
```

**Expected output should include:**
```
OPENAI_API_KEY=your-key-here
API_KEY_SECRET=my-seceret-key-super
LLM_MODEL=gpt-4o-mini
ELASTICSEARCH_URL=http://localhost:9201
DATABASE_URL=postgresql://clinicaluser:clinicalpass@localhost:5432/clinical_guidelines
REDIS_URL=redis://localhost:6379/0
MILVUS_HOST=localhost
MILVUS_PORT=19530
```

**If file is missing or incorrect**, edit it manually or recreate it.

---

### **STEP 3: Start Infrastructure Services (Docker)**

Start all backend services (PostgreSQL, Elasticsearch, Milvus, Redis, etc.):

```cmd
docker-compose up -d
```

**Wait ~30 seconds** for services to initialize, then verify they're running:

```cmd
docker-compose ps
```

**Expected output:** All services should show `Up` status:
- `postgres` (port 5432)
- `elasticsearch` (port 9201)
- `milvus-standalone` (port 19530)
- `redis` (port 6379)
- `minio` (ports 9000, 9001)
- `temporal` (port 7233)
- `temporal-web` (port 8088)
- `prometheus` (port 9090)
- `jaeger` (port 16686)

**If any service fails**, check logs:
```cmd
docker-compose logs [service-name]
```

---

### **STEP 4: Install Python Dependencies**

Install all required Python packages:

```cmd
py311.bat -m pip install --upgrade pip
py311.bat -m pip install -r requirements.txt
```

**Expected:** Installation completes without errors. If you see dependency conflicts, they should auto-resolve.

---

### **STEP 5: Initialize Database Schema**

Create database tables and schema:

```cmd
py311.bat scripts\init_db.py
```

**Expected output:**
```
✅ Database initialized successfully!
Created tables: documents, queries, results, citations, audit_logs
```

**If this fails** with "port 5432 already in use", you have a local PostgreSQL running. Either:
- Stop your local PostgreSQL, OR
- Change the Docker port in `docker-compose.yml` (e.g., `5433:5432`)

---

### **STEP 6: Start Ollama (Free LLM Option)**

**Option A: Using Ollama (FREE - Recommended)**

Start Ollama service:
```cmd
ollama serve
```

Keep this window open (Ollama runs in foreground). Open a **new CMD window** for next steps.

Verify Ollama is running:
```cmd
ollama list
```

**Expected:** Should show `llama3.2:3b` model

**If model is missing:**
```cmd
ollama pull llama3.2:3b
```

---

**Option B: Using OpenAI (COSTS MONEY)**

If you prefer OpenAI instead, ensure `.env` has valid `OPENAI_API_KEY` and skip Ollama setup.

---

### **STEP 7: Index Sample Documents (Optional)**

Load sample clinical documents into the system:

```cmd
py311.bat scripts\index_sample_documents.py
```

**Expected:** 
```
Indexing 50 sample documents...
✅ Indexed 50 documents to Elasticsearch and Milvus
```

**Note:** This requires Elasticsearch and Milvus to be running (Step 3).

---

### **STEP 8: Test Individual Agents**

Test Agent 1 (Query+Filter) with Ollama:

```cmd
py311.bat test_with_ollama.py
```

**Expected output (~15 seconds):**
```
Testing Agent 1 with Ollama...
✅ Agent 1 completed in 15.23s
📊 Expanded Queries: 3
🏷️  MeSH Terms: 5
💰 Cost: $0.00
```

---

### **STEP 9: Run Full 3-Agent Pipeline Demo**

Execute complete workflow with all 3 agents:

```cmd
py311.bat demo_full_pipeline.py
```

**Expected output (~25 seconds):**
```
🏥 CLINICAL GUIDELINE RESEARCH ASSISTANT - FULL DEMO

▶ STEP 1: AGENT 1: Query+Filter
   ✓ Completed in 7.54s
   📊 Expanded Queries (3)
   🏷️  MeSH Terms (4)

▶ STEP 2: AGENT 2: Retriever+Summarizer
   ✓ Retrieved 3 documents
   📄 Synthesis generated

▶ STEP 3: AGENT 3: Fact-Check+Writer
   ✓ Completed in 16.97s
   📋 Executive Brief (266 words)
   ⚠️  Risk Flags: 4

✅ PIPELINE COMPLETE
💰 Total Cost: $0.00
⏱️  Total Time: 24.51s
```

---

### **STEP 10: Start Production API Server**

Start the FastAPI gateway for production use:

```cmd
py311.bat -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

**Expected output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

**Access API:**
- API docs: http://localhost:8000/docs
- Health check: http://localhost:8000/health

Keep this window open (API server runs in foreground).

---

### **STEP 11: Start Temporal Worker (Optional - For Orchestration)**

In a **new CMD window**, start the Temporal workflow worker:

```cmd
cd C:\Users\bjoy2\clinical-guideline-assistant
py311.bat scripts\start_worker.py
```

**Expected output:**
```
🔄 Starting Temporal Worker...
✅ Worker started successfully
Listening for tasks on queue: clinical-guideline-queue
```

Keep this window open.

---

### **STEP 12: Test Production API**

In a **new CMD window**, test the API endpoint:

```cmd
curl -X POST http://localhost:8000/api/v1/research ^
  -H "Content-Type: application/json" ^
  -H "X-API-Key: my-seceret-key-super" ^
  -d "{\"query\": \"diabetes management in elderly patients\", \"max_results\": 5}"
```

**Expected:** JSON response with:
- `workflow_id`: Unique identifier
- `status`: "running" or "completed"
- `result`: Executive brief with citations

---

## 🎯 Production Checklist

After completing all steps, verify:

- [ ] Docker services running (`docker-compose ps`)
- [ ] Ollama serving (`ollama list` shows llama3.2:3b)
- [ ] Database initialized (tables exist)
- [ ] Sample documents indexed (optional)
- [ ] API server running on port 8000
- [ ] Temporal worker running (optional)
- [ ] Test query returns valid results

---

## 📊 Monitoring & Observability

Access monitoring dashboards:

| Service | URL | Purpose |
|---------|-----|---------|
| **API Docs** | http://localhost:8000/docs | FastAPI interactive docs |
| **Temporal UI** | http://localhost:8088 | Workflow orchestration |
| **Prometheus** | http://localhost:9090 | Metrics & monitoring |
| **Jaeger** | http://localhost:16686 | Distributed tracing |
| **MinIO Console** | http://localhost:9001 | Object storage (user: minioadmin/minioadmin) |

---

## 🛑 Stopping Services

### Stop API Server
Press `Ctrl+C` in the API server CMD window

### Stop Temporal Worker
Press `Ctrl+C` in the worker CMD window

### Stop Ollama
Press `Ctrl+C` in the Ollama CMD window

### Stop Docker Services
```cmd
docker-compose down
```

### Stop Everything and Clean Up
```cmd
docker-compose down -v
```
**Warning:** This deletes all data (databases, indexes, etc.)

---

## 🔧 Troubleshooting

### Issue: "Port already in use"
**Solution:** Change port in `docker-compose.yml` or stop conflicting service

### Issue: "Module not found"
**Solution:** 
```cmd
py311.bat -m pip install -r requirements.txt
```

### Issue: "Ollama connection refused"
**Solution:** Ensure Ollama is running:
```cmd
ollama serve
```

### Issue: "Database connection failed"
**Solution:** Check PostgreSQL is running:
```cmd
docker-compose ps postgres
docker-compose logs postgres
```

### Issue: "Milvus collection not found"
**Solution:** Index documents first:
```cmd
py311.bat scripts\index_sample_documents.py
```

### Issue: "OpenAI API quota exceeded"
**Solution:** Switch to free Ollama (see Step 6, Option A)

---

## 📚 Production Configuration

### Environment Variables (.env)

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | - | OpenAI API key (optional if using Ollama) |
| `API_KEY_SECRET` | my-seceret-key-super | API authentication key |
| `LLM_MODEL` | gpt-4o-mini | OpenAI model (ignored if using Ollama) |
| `ELASTICSEARCH_URL` | http://localhost:9201 | Elasticsearch endpoint |
| `DATABASE_URL` | postgresql://... | PostgreSQL connection string |
| `REDIS_URL` | redis://localhost:6379/0 | Redis connection string |
| `MILVUS_HOST` | localhost | Milvus vector DB host |
| `MILVUS_PORT` | 19530 | Milvus vector DB port |

### Docker Compose Services

| Service | Port(s) | Purpose |
|---------|---------|---------|
| `postgres` | 5432 | Primary database |
| `elasticsearch` | 9201, 9301 | Full-text search (BM25) |
| `milvus-standalone` | 19530, 9091 | Vector search |
| `redis` | 6379 | Caching & task queue |
| `minio` | 9000, 9001 | S3-compatible object storage |
| `temporal` | 7233 | Workflow orchestration |
| `temporal-web` | 8088 | Temporal UI |
| `prometheus` | 9090 | Metrics collection |
| `jaeger` | 16686 | Distributed tracing |

---

## 🚀 Next Steps After Deployment

1. **Load Real Clinical Documents**
   - Add PubMed/MEDLINE documents to `data/documents/`
   - Run indexing script: `py311.bat scripts\index_sample_documents.py`

2. **Configure Authentication**
   - Update `API_KEY_SECRET` in `.env`
   - Implement OAuth2/JWT for production

3. **Set Up HTTPS**
   - Use nginx reverse proxy with SSL certificates
   - Update API endpoints to use HTTPS

4. **Configure Monitoring Alerts**
   - Set up Prometheus alerts for errors, latency
   - Configure Jaeger sampling for production load

5. **Scale Services**
   - Add replicas in `docker-compose.yml`
   - Use Kubernetes for larger deployments

6. **Backup Strategy**
   - Schedule PostgreSQL backups
   - Export Milvus collections periodically
   - Backup MinIO object storage

---

## 📞 Support

- **Project README**: `README.md`
- **Setup Guide**: `SETUP_GUIDE.md`
- **Project Summary**: `PROJECT_SUMMARY.md`
- **Getting Started**: `docs/GETTING_STARTED.md`

---

**🎉 Deployment Complete! Your 3-agent clinical guideline research system is now running in production mode.**
