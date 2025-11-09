"""Complete demo of all 3 agents working together (FREE with Ollama)."""
import sys
import os
import json
sys.path.insert(0, os.path.dirname(__file__))

from agents.query_filter_agent import QueryFilterAgent
from agents.retriever_summarizer_agent import RetrieverSummarizerAgent
from agents.fact_check_writer_agent import FactCheckWriterAgent

# Sample mock documents for demonstration
MOCK_DOCUMENTS = [
    {
        "doc_id": "doc1",
        "source": {
            "title": "Diabetes Management in Elderly: Updated Guidelines 2023",
            "abstract": "Individualized HbA1c targets of 7.0-8.0% reduce hypoglycemia risk in elderly patients. Metformin remains first-line when renal function permits.",
            "authors": ["Smith J", "Johnson M"],
            "doi": "10.1234/diabetes.2023",
            "publication_date": "2023-05",
            "source_type": "clinical_guideline",
            "citation_count": 145
        }
    },
    {
        "doc_id": "doc2",
        "source": {
            "title": "SGLT2 Inhibitors: Benefits and Risks in Geriatric Populations",
            "abstract": "SGLT2 inhibitors show cardiovascular benefits but require monitoring for dehydration and UTIs in elderly patients over 75 years.",
            "authors": ["Lee A", "Chen B"],
            "doi": "10.5678/cardio.2023",
            "publication_date": "2023-08",
            "source_type": "meta_analysis",
            "citation_count": 89
        }
    },
    {
        "doc_id": "doc3",
        "source": {
            "title": "Hypoglycemia Prevention Strategies in Elderly Diabetics",
            "abstract": "Evidence shows that relaxed glycemic targets prevent severe hypoglycemia events. Regular glucose monitoring and medication review essential.",
            "authors": ["Garcia R", "Martinez E"],
            "doi": "10.9012/endo.2023",
            "publication_date": "2023-06",
            "source_type": "rct",
            "citation_count": 67
        }
    }
]

def print_header(title):
    """Print formatted section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def print_step(step_num, description):
    """Print step header."""
    print(f"\n▶ STEP {step_num}: {description}")
    print("-" * 70)

def main():
    """Run complete 3-agent pipeline demo."""
    
    print_header("🏥 CLINICAL GUIDELINE RESEARCH ASSISTANT - FULL DEMO 🤖")
    print("\n✅ Using FREE Ollama (No API costs!)")
    print("📋 Research Topic: 'Diabetes management in elderly patients'")
    
    # ==================================================================
    # AGENT 1: Query+Filter
    # ==================================================================
    print_step(1, "AGENT 1: Query+Filter (Query Expansion & Domain Vetting)")
    
    agent1 = QueryFilterAgent(use_ollama=True)
    print("   Model: Llama 3.2 3B (local, free)")
    print("   Task: Expand query and generate MeSH terms...")
    
    result1 = agent1.run(
        topic="diabetes management in elderly patients",
        max_sources=10,
        quality_threshold=0.7
    )
    
    print(f"\n   ✓ Completed in {result1.execution_time_ms/1000:.2f}s")
    
    if 'expansion' in result1.output_data:
        expansion = result1.output_data['expansion']
        
        print(f"\n   📊 Expanded Queries ({len(expansion.get('expanded_queries', []))}):")
        for i, query in enumerate(expansion.get('expanded_queries', [])[:2], 1):
            print(f"      {i}. {query[:80]}...")
        
        mesh_terms = expansion.get('mesh_terms', [])
        if isinstance(mesh_terms, list):
            print(f"\n   🏷️  MeSH Terms ({len(mesh_terms)}):")
            for term in mesh_terms[:4]:
                print(f"      • {term}")
        else:
            print(f"\n   🏷️  MeSH Terms: {mesh_terms}")
    
    # ==================================================================
    # AGENT 2: Retriever+Summarizer
    # ==================================================================
    print_step(2, "AGENT 2: Retriever+Summarizer (Hybrid Search & Summarization)")
    
    agent2 = RetrieverSummarizerAgent(use_ollama=True)
    print("   Model: Llama 3.2 3B (local, free)")
    print("   Task: Retrieve documents and create hierarchical summary...")
    print("   Note: Using mock documents (real system would query Elasticsearch + Milvus)")
    
    # Simulate retrieval with mock documents
    expanded_queries = expansion.get('expanded_queries', ['diabetes elderly management'])
    
    # For demo, we'll skip actual retrieval and use mock docs
    # In production, agent2.run() would do BM25+vector search
    print(f"\n   🔍 Retrieved {len(MOCK_DOCUMENTS)} documents")
    for i, doc in enumerate(MOCK_DOCUMENTS, 1):
        print(f"      {i}. {doc['source']['title'][:60]}...")
    
    print("\n   📝 Generating hierarchical summary...")
    summary_result = agent2.hierarchical_summarize(
        topic="diabetes management in elderly patients",
        retrieved_docs=MOCK_DOCUMENTS
    )
    
    print(f"\n   ✓ Summary Generated")
    print(f"\n   📄 Synthesis:")
    synthesis = summary_result.get('synthesis', 'N/A')[:200]
    print(f"      {synthesis}...")
    
    if summary_result.get('contradictions'):
        print(f"\n   ⚠️  Contradictions Detected: {len(summary_result['contradictions'])}")
        for c in summary_result['contradictions'][:1]:
            print(f"      • {c.get('claim', 'N/A')[:80]}")
    
    # ==================================================================
    # AGENT 3: Fact-Check+Writer
    # ==================================================================
    print_step(3, "AGENT 3: Fact-Check+Writer (Verification & Brief Generation)")
    
    agent3 = FactCheckWriterAgent(use_ollama=True)
    print("   Model: Llama 3.2 3B (local, free)")
    print("   Task: Write executive brief with citations and traceability...")
    
    result3 = agent3.run(
        topic="diabetes management in elderly patients",
        retrieved_docs=MOCK_DOCUMENTS,
        summary_data=summary_result
    )
    
    print(f"\n   ✓ Completed in {result3.execution_time_ms/1000:.2f}s")
    
    if 'research_brief' in result3.output_data:
        brief = result3.output_data['research_brief']
        
        print(f"\n   📋 Executive Brief ({brief.get('word_count', 0)} words):")
        exec_brief = brief.get('executive_brief', 'N/A')
        # Print first 300 chars
        print(f"      {exec_brief[:300]}...")
        
        print(f"\n   📚 Sources: {len(brief.get('sources', []))}")
        print(f"   🔗 Citations: {len(brief.get('citations', []))}")
        print(f"   ⚠️  Risk Flags: {len(brief.get('risk_flags', []))}")
        print(f"   🔍 Traceability Entries: {len(brief.get('traceability', []))}")
        
        if brief.get('risk_flags'):
            print(f"\n   ⚠️  Risk Flags Detected:")
            for flag in brief['risk_flags'][:2]:
                print(f"      • [{flag.get('severity', 'N/A').upper()}] {flag.get('flag_type', 'N/A')}")
                print(f"        {flag.get('description', 'N/A')[:70]}...")
    
    # ==================================================================
    # FINAL RESULTS
    # ==================================================================
    print_header("✅ PIPELINE COMPLETE - FINAL DELIVERABLES")
    
    print("\n📦 Generated Outputs:")
    print("   1. Executive Brief (≤300 words) with inline citations [1][2][3]")
    print("   2. Source List with DOIs, authors, and quality scores")
    print("   3. Risk Flags for contradictions and safety concerns")
    print("   4. Traceability Appendix mapping claims → sources")
    
    print("\n💰 Total Cost: $0.00 (FREE with Ollama!)")
    print(f"⏱️  Total Time: {(result1.execution_time_ms + result3.execution_time_ms)/1000:.2f}s")
    
    print("\n🎯 Success Metrics:")
    print(f"   • Agent 1 Errors: {len(result1.errors)}")
    print(f"   • Agent 3 Errors: {len(result3.errors)}")
    print(f"   • Documents Retrieved: {len(MOCK_DOCUMENTS)}")
    print(f"   • Claims Verified: {result3.metrics.get('traceability_entries', 0)}")
    
    print_header("🚀 DEMO COMPLETE")
    print("\n✨ All 3 agents worked together successfully!")
    print("💡 Next: Load real clinical documents and run production queries")
    print("\n" + "=" * 70 + "\n")


if __name__ == "__main__":
    main()
