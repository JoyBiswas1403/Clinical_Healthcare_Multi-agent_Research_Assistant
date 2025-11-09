"""Tests for the 3-agent system."""
import pytest
from unittest.mock import Mock, patch

from agents.query_filter_agent import QueryFilterAgent
from agents.retriever_summarizer_agent import RetrieverSummarizerAgent
from agents.fact_check_writer_agent import FactCheckWriterAgent


class TestQueryFilterAgent:
    """Tests for Agent 1: Query+Filter."""
    
    def test_expand_query(self):
        """Test query expansion."""
        agent = QueryFilterAgent()
        
        # Mock OpenAI response
        mock_response = {
            "expanded_queries": [
                "hypertension management elderly patients",
                "blood pressure control geriatric population"
            ],
            "mesh_terms": ["Hypertension", "Aged", "Blood Pressure"],
            "synonyms": {"elderly": ["aged", "geriatric", "senior"]},
            "exclusion_criteria": ["pediatric", "pregnancy"],
            "source_priorities": ["meta_analysis", "rct", "clinical_guideline"]
        }
        
        with patch.object(agent.client.chat.completions, 'create') as mock_create:
            mock_create.return_value = Mock(
                choices=[Mock(message=Mock(content=str(mock_response)))]
            )
            
            result = agent.expand_query("hypertension in elderly")
            
            assert "expanded_queries" in result
            assert len(result["expanded_queries"]) > 0
    
    def test_agent_run(self):
        """Test full agent execution."""
        agent = QueryFilterAgent()
        
        with patch.object(agent, 'expand_query') as mock_expand:
            mock_expand.return_value = {
                "expanded_queries": ["query1", "query2"],
                "mesh_terms": ["term1"]
            }
            
            result = agent.run(
                topic="test topic",
                max_sources=10,
                quality_threshold=0.7
            )
            
            assert result.agent_name == "QueryFilterAgent"
            assert "expansion" in result.output_data
            assert result.metrics["expanded_queries_count"] == 2


class TestRetrieverSummarizerAgent:
    """Tests for Agent 2: Retriever+Summarizer."""
    
    def test_hybrid_fusion(self):
        """Test BM25+vector fusion."""
        agent = RetrieverSummarizerAgent()
        
        bm25_results = [
            {"doc_id": "doc1", "score": 0.9, "source": {"title": "Doc 1"}},
            {"doc_id": "doc2", "score": 0.7, "source": {"title": "Doc 2"}}
        ]
        
        vector_results = [
            {"doc_id": "doc2", "score": 0.8, "source": {"title": "Doc 2"}},
            {"doc_id": "doc3", "score": 0.6, "source": {"title": "Doc 3"}}
        ]
        
        fused = agent.hybrid_fusion(bm25_results, vector_results, alpha=0.5)
        
        assert len(fused) == 3  # 3 unique docs
        assert all("hybrid_score" in doc for doc in fused)
        # Doc 2 should rank highest (in both results)
        assert fused[0]["doc_id"] == "doc2"


class TestFactCheckWriterAgent:
    """Tests for Agent 3: Fact-Check+Writer."""
    
    def test_extract_citations(self):
        """Test citation extraction from brief."""
        agent = FactCheckWriterAgent()
        
        brief_text = "Evidence shows benefits [1]. However, risks exist [2][3]."
        sources = [
            {"doc_id": "doc1", "source": {"abstract": "Abstract 1"}},
            {"doc_id": "doc2", "source": {"abstract": "Abstract 2"}},
            {"doc_id": "doc3", "source": {"abstract": "Abstract 3"}}
        ]
        
        citations = agent.extract_citations_from_brief(brief_text, sources)
        
        assert len(citations) == 3
        assert all(c.citation_id in ["1", "2", "3"] for c in citations)
    
    def test_agent_run(self):
        """Test full agent execution."""
        agent = FactCheckWriterAgent()
        
        with patch.object(agent, 'write_brief') as mock_write, \
             patch.object(agent, 'assess_risks') as mock_risks:
            
            mock_write.return_value = {
                "brief_text": "Test brief [1].",
                "word_count": 50,
                "claims": [{"claim_text": "Test claim", "location": "p1"}]
            }
            
            mock_risks.return_value = []
            
            result = agent.run(
                topic="test",
                retrieved_docs=[{"doc_id": "1", "source": {}}],
                summary_data={"synthesis": "test"}
            )
            
            assert result.agent_name == "FactCheckWriterAgent"
            assert "research_brief" in result.output_data
            assert result.metrics["word_count"] == 50


@pytest.mark.integration
class TestEndToEnd:
    """End-to-end integration tests."""
    
    def test_full_pipeline(self):
        """Test complete 3-agent pipeline."""
        # This would require mocking all external services
        # or using a test environment with real infrastructure
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
