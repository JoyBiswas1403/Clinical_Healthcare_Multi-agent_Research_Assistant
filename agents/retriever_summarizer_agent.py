"""Agent 2: Retriever+Summarizer - Hybrid BM25+vector retrieval with hierarchical summarization."""
import time
from typing import List, Dict, Any
from openai import OpenAI
from elasticsearch import Elasticsearch
from pymilvus import connections, Collection
from sentence_transformers import SentenceTransformer
from data.models import AgentOutput
from config.settings import settings


SUMMARIZATION_PROMPT = """You are a clinical research summarization expert. Create a hierarchical summary of the following sources.

Topic: {topic}
Sources: {sources}

Create:
1. High-level synthesis (2-3 sentences) - what are the key findings across all sources?
2. Source-level summaries - 1-2 sentences per source highlighting unique contributions
3. Contradiction detection - identify any conflicting findings
4. Quality assessment - note any methodological concerns

Return JSON:
{{
  "synthesis": "...",
  "source_summaries": [
    {{
      "source_id": "...",
      "summary": "...",
      "key_findings": ["finding1", "finding2"],
      "quality_notes": "..."
    }}
  ],
  "contradictions": [
    {{
      "claim": "...",
      "conflicting_sources": ["id1", "id2"],
      "severity": "high|medium|low"
    }}
  ],
  "overall_quality": "high|medium|low"
}}
"""


class RetrieverSummarizerAgent:
    """Agent 2: Performs hybrid retrieval and hierarchical summarization."""
    
    def __init__(self, use_ollama=False):
        if use_ollama:
            # Use free local Ollama
            self.llm_client = OpenAI(
                base_url="http://localhost:11434/v1",
                api_key="ollama"
            )
            self.model = "llama3.2:3b"
        else:
            # Use OpenAI (requires credits)
            self.llm_client = OpenAI(api_key=settings.openai_api_key)
            self.model = settings.llm_model
        self.temperature = settings.summarizer_temperature
        
        # Elasticsearch for BM25
        self.es_client = None
        try:
            self.es_client = Elasticsearch([settings.elasticsearch_url])
        except Exception as e:
            print(f"Elasticsearch connection failed: {e}")
        
        # Embedding model for vector search
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Milvus for vector search
        self.milvus_collection = None
        try:
            connections.connect(host=settings.milvus_host, port=settings.milvus_port)
            self.milvus_collection = Collection(settings.milvus_collection)
        except Exception as e:
            print(f"Milvus connection failed: {e}")
    
    def bm25_search(self, queries: List[str], top_k: int = 20) -> List[Dict[str, Any]]:
        """Perform BM25 keyword search via Elasticsearch."""
        if not self.es_client:
            return []
        
        results = []
        for query in queries:
            try:
                response = self.es_client.search(
                    index=settings.elasticsearch_index,
                    body={
                        "query": {
                            "multi_match": {
                                "query": query,
                                "fields": ["title^3", "abstract^2", "full_text"],
                                "type": "best_fields"
                            }
                        },
                        "size": top_k
                    }
                )
                
                for hit in response['hits']['hits']:
                    results.append({
                        "doc_id": hit['_id'],
                        "score": hit['_score'],
                        "source": hit['_source'],
                        "retrieval_method": "bm25"
                    })
            except Exception as e:
                print(f"BM25 search error for query '{query}': {e}")
        
        return results
    
    def vector_search(self, queries: List[str], top_k: int = 20) -> List[Dict[str, Any]]:
        """Perform semantic vector search via Milvus."""
        if not self.milvus_collection:
            return []
        
        results = []
        for query in queries:
            try:
                # Generate embedding
                query_embedding = self.embedding_model.encode([query])[0].tolist()
                
                # Search Milvus
                search_params = {"metric_type": "L2", "params": {"nprobe": 10}}
                search_results = self.milvus_collection.search(
                    data=[query_embedding],
                    anns_field="embedding",
                    param=search_params,
                    limit=top_k,
                    output_fields=["doc_id", "title", "abstract"]
                )
                
                for hits in search_results:
                    for hit in hits:
                        results.append({
                            "doc_id": hit.entity.get("doc_id"),
                            "score": 1.0 / (1.0 + hit.distance),  # Convert distance to similarity
                            "source": {
                                "title": hit.entity.get("title"),
                                "abstract": hit.entity.get("abstract")
                            },
                            "retrieval_method": "vector"
                        })
            except Exception as e:
                print(f"Vector search error for query '{query}': {e}")
        
        return results
    
    def hybrid_fusion(
        self,
        bm25_results: List[Dict[str, Any]],
        vector_results: List[Dict[str, Any]],
        alpha: float = 0.5
    ) -> List[Dict[str, Any]]:
        """Fuse BM25 and vector search results using reciprocal rank fusion."""
        doc_scores = {}
        
        # Reciprocal Rank Fusion
        for rank, result in enumerate(bm25_results, start=1):
            doc_id = result["doc_id"]
            doc_scores[doc_id] = doc_scores.get(doc_id, {"source": result["source"]})
            doc_scores[doc_id]["bm25_score"] = 1.0 / (60 + rank)
        
        for rank, result in enumerate(vector_results, start=1):
            doc_id = result["doc_id"]
            if doc_id not in doc_scores:
                doc_scores[doc_id] = {"source": result["source"]}
            doc_scores[doc_id]["vector_score"] = 1.0 / (60 + rank)
        
        # Compute hybrid score
        fused = []
        for doc_id, data in doc_scores.items():
            bm25 = data.get("bm25_score", 0)
            vector = data.get("vector_score", 0)
            hybrid_score = alpha * bm25 + (1 - alpha) * vector
            
            fused.append({
                "doc_id": doc_id,
                "source": data["source"],
                "hybrid_score": hybrid_score,
                "bm25_score": bm25,
                "vector_score": vector
            })
        
        # Sort by hybrid score
        fused.sort(key=lambda x: x["hybrid_score"], reverse=True)
        return fused
    
    def rerank(self, results: List[Dict[str, Any]], topic: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """Rerank results using LLM-based relevance scoring."""
        # Simplified reranking - in production, use a reranker model
        return results[:top_k]
    
    def hierarchical_summarize(
        self,
        topic: str,
        retrieved_docs: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Create hierarchical summary of retrieved documents."""
        # Format sources for LLM
        sources_text = []
        for i, doc in enumerate(retrieved_docs):
            source = doc.get("source", {})
            sources_text.append(
                f"Source {i+1} (ID: {doc['doc_id']}):\n"
                f"Title: {source.get('title', 'N/A')}\n"
                f"Abstract: {source.get('abstract', 'N/A')[:500]}..."
            )
        
        prompt = SUMMARIZATION_PROMPT.format(
            topic=topic,
            sources="\n\n".join(sources_text[:10])  # Limit to first 10 for context
        )
        
        response = self.llm_client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a clinical research summarization expert."},
                {"role": "user", "content": prompt}
            ],
            temperature=self.temperature,
            response_format={"type": "json_object"}
        )
        
        import json
        return json.loads(response.choices[0].message.content)
    
    def run(
        self,
        topic: str,
        expanded_queries: List[str],
        top_k: int = 20,
        rerank_top_k: int = 10
    ) -> AgentOutput:
        """Execute hybrid retrieval and summarization pipeline."""
        start_time = time.time()
        errors = []
        metrics = {}
        
        try:
            # Step 1: BM25 search
            bm25_results = self.bm25_search(expanded_queries, top_k)
            metrics["bm25_results_count"] = len(bm25_results)
            
            # Step 2: Vector search
            vector_results = self.vector_search(expanded_queries, top_k)
            metrics["vector_results_count"] = len(vector_results)
            
            # Step 3: Hybrid fusion
            fused_results = self.hybrid_fusion(bm25_results, vector_results)
            metrics["fused_results_count"] = len(fused_results)
            
            # Step 4: Rerank
            reranked = self.rerank(fused_results, topic, rerank_top_k)
            metrics["final_results_count"] = len(reranked)
            
            # Step 5: Hierarchical summarization
            summary = self.hierarchical_summarize(topic, reranked)
            
            output_data = {
                "retrieved_documents": reranked,
                "summary": summary,
                "topic": topic
            }
            
        except Exception as e:
            errors.append(str(e))
            output_data = {"error": str(e)}
        
        execution_time_ms = (time.time() - start_time) * 1000
        
        return AgentOutput(
            agent_name="RetrieverSummarizerAgent",
            output_data=output_data,
            metrics=metrics,
            errors=errors,
            execution_time_ms=execution_time_ms
        )
