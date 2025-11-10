# Getting Started with Clinical Guideline Research Assistant

Welcome! This guide will help you get the Clinical Guideline Research Assistant up and running in under 10 minutes.

---

## What is This Project?

This is a **3-agent AI system** that helps healthcare professionals research clinical guidelines quickly. Give it a research topic like "diabetes management in elderly patients", and it will:

1. ✅ Search and filter relevant clinical literature
2. ✅ Summarize findings from multiple sources
3. ✅ Write an executive brief with citations
4. ✅ Flag contradictions and safety concerns
5. ✅ Show you exactly where each claim comes from

**Best part:** It's completely FREE to run using Ollama (local AI model).

---

## Quick Start (5 Minutes)

### Step 1: Install Prerequisites

**You need:**
- Docker Desktop ([Download](https://www.docker.com/products/docker-desktop))
- Python 3.11+ ([Download](https://www.python.org/downloads/))
- Ollama ([Download](https://ollama.com/))

### Step 2: Install Ollama Model

```bash
# Install Ollama (Windows)
winget install Ollama.Ollama

# Pull the AI model (this downloads ~2GB)
ollama pull llama3.2:3b

# Start Ollama (keep this running)
ollama serve
```

### Step 3: Clone and Setup

Open a **new terminal** (keep Ollama running in the first one):

```bash
# Clone the repository
git clone https://github.com/JoyBiswas1403/Clinical_Healthcare_Multi-agent_Reseach_Assistant.git
cd Clinical_Healthcare_Multi-agent_Reseach_Assistant

# Create configuration file
copy .env.example .env   # Windows
# OR
cp .env.example .env     # Linux/macOS

# Start backend services (takes ~30 seconds)
docker-compose up -d

# Install Python dependencies
python -m pip install -r requirements.txt
```

### Step 4: Run Your First Demo

```bash
# Quick demo (instant, shows example output)
python demo_quick.py

# Full demo (25 seconds, uses live AI)
python demo_full_pipeline.py
```

**That's it!** You should see a complete research brief with citations. 🎉

---

## Understanding the Output

When you run the demo, you'll get:

### 1. **Executive Brief** (≤300 words)
A concise summary with inline citations [1], [2], [3].

### 2. **Sources**
List of all cited papers with DOIs, authors, and quality scores.

### 3. **Risk Flags**
Automatic warnings about contradictions, safety concerns, or study quality issues.

### 4. **Traceability**
Every claim mapped back to the exact source passage with confidence scores.

---

## How the 3 Agents Work

### Agent 1: Query+Filter
Expands your question into optimized searches with MeSH terms and applies policy filters.

### Agent 2: Retriever+Summarizer
Hybrid search (keyword + semantic) → hierarchical summary → contradiction detection.

### Agent 3: Fact-Check+Writer
Verifies claims → writes brief → inserts citations → generates traceability.

---

## Cost & Speed

| Option | Cost | Speed | Quality |
|--------|------|-------|---------|
| **Ollama** (FREE) | $0.00 | ~25s | Good |
| OpenAI | $0.03-$0.15 | ~20s | Excellent |

---

## Troubleshooting

### "Ollama connection refused"
```bash
ollama serve
```

### "Port already in use"
Change port in `docker-compose.yml` or stop conflicting service.

### "Module not found"
```bash
python -m pip install -r requirements.txt
```

---

## Learning More

- **README.md** - Project overview
- **SETUP_GUIDE.md** - Detailed setup
- **PROJECT_SUMMARY.md** - Technical architecture
- **PRODUCTION_DEPLOYMENT_GUIDE.md** - Production deployment

---

**You're all set!** Try `python demo_full_pipeline.py` and explore. Happy researching! 🚀💙
