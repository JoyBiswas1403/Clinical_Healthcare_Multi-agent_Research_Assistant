# Clinical Guideline Research Assistant - Project Summary

## 🎯 Project Overview

A production-ready 3-agent multi-agent system designed for healthcare clinical guideline research. The system generates evidence-based executive briefs with full provenance tracking, claim-level verification, and risk flagging for healthcare professionals.

**Key Value Proposition:** Transform clinical research queries into actionable, cited briefs in ~25 seconds with complete traceability from every claim to source passages.

---

## 🏗️ System Architecture

### Three-Agent Pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│                    User Query Input                              │
│         "Diabetes management in elderly patients"                │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│  AGENT 1: Query+Filter                                           │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│  • Expands query into 3-5 optimized searches                     │
│  • Generates MeSH terms and synonyms                             │
│  • Applies HIPAA/FDA policy filters                              │
│  • Vets results for relevance & credibility                      │
│                                                                   │
│  Output: Expanded queries + Vetted result set                    │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│  AGENT 2: Retriever+Summarizer                                   │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│  • Hybrid BM25 (Elasticsearch) + Vector (Milvus) search          │
│  • Re-ranks top-K results by relevance                           │
│  • Hierarchical summarization (chunk → doc → synthesis)          │
│  • Detects contradictions across sources                         │
│                                                                   │
│  Output: Ranked documents + Hierarchical summary                 │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│  AGENT 3: Fact-Check+Writer                                      │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│  • Extracts claims from summaries                                │
│  • Verifies each claim against source passages                   │
│  • Writes ≤300-word executive brief with inline citations        │
│  • Flags contradictions, contraindications, bias                 │
│  • Generates traceability appendix (claim → passage → source)    │
│                                                                   │
│  Output: Executive brief + Sources + Flags + Traceability        │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Deliverables Package                          │
│  • Executive Brief (≤300 words, citations [1][2][3])             │
│  • Source List (DOIs, URLs, metadata, quality scores)            │
│  • Risk Flags (contradictions, bias, study quality)              │
│  • Traceability Appendix (every claim mapped to passages)        │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Technology Stack

### Core Infrastructure

| Component | Technology | Purpose |
|-----------|------------|---------|
| **API Gateway** | FastAPI | REST endpoints, request validation |
| **Orchestration** | Temporal | Workflow management, fault tolerance |
| **Full-Text Search** | Elasticsearch | BM25 keyword search, document indexing |
| **Vector Search** | Milvus | Semantic similarity, embedding storage |
| **Database** | PostgreSQL | Structured data, audit logs |
| **Cache** | Redis | Session cache, task queue |
| **Object Storage** | MinIO (S3-compatible) | Document storage, large artifacts |
| **LLM** | Ollama / OpenAI | Query expansion, summarization, writing |
| **Embeddings** | sentence-transformers | Document/query vectorization |

### Observability Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Metrics** | Prometheus | Time-series metrics, dashboards |
| **Tracing** | Jaeger | Distributed tracing, latency analysis |
| **Logging** | Structured JSON logs | Audit trail, debugging |
| **Workflow UI** | Temporal Web | Workflow visualization, debugging |

---

## 📊 Performance Metrics

### Latency (3-agent pipeline)
- **Target**: <45 seconds (P95)
- **Current**: ~25 seconds (with Ollama llama3.2:3b)
- **Breakdown**:
  - Agent 1 (Query+Filter): ~8 seconds
  - Agent 2 (Retriever+Summarizer): ~15 seconds
  - Agent 3 (Fact-Check+Writer): ~17 seconds

### Quality Targets
- **Retrieval Recall@10**: >0.85
- **Fact-Check Precision**: >0.95
- **Brief Quality Score**: >4.2/5 (human evaluation)
- **Citation Accuracy**: >0.90

### Cost Comparison
| LLM Option | Cost per Query | Speed | Quality |
|------------|----------------|-------|---------|
| **Ollama (llama3.2:3b)** | $0.00 | ~25s | Good |
| OpenAI (gpt-4o-mini) | ~$0.03 | ~20s | Excellent |
| OpenAI (gpt-4-turbo) | ~$0.15 | ~25s | Best |

---

## 🔐 Security Features

- API key-based authentication
- Rate limiting (100 req/hour per key)
- PII detection and redaction
- Audit logging for all requests
- HIPAA-compliant data handling

---

## 📚 Documentation

- **README.md**: Quick start and overview
- **SETUP_GUIDE.md**: Detailed setup instructions
- **PRODUCTION_DEPLOYMENT_GUIDE.md**: Production deployment for Windows
- **docs/GETTING_STARTED.md**: Beginner-friendly guide
- **API Documentation**: http://localhost:8000/docs (when running)

---

## 📞 Support & Resources

- **GitHub**: https://github.com/JoyBiswas1403/Clinical_Healthcare_Multi-agent_Reseach_Assistant
- **API Docs**: http://localhost:8000/docs
- **Temporal UI**: http://localhost:8088
- **Prometheus**: http://localhost:9090
- **Jaeger**: http://localhost:16686

---

**Built for healthcare professionals who need fast, accurate, and trustworthy clinical research synthesis. 💙**
