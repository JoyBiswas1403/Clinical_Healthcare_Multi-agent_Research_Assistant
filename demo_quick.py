"""Quick demo showing 3-agent pipeline results (using cached/mock outputs)."""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

def print_header(title):
    """Print formatted section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def main():
    """Display what the 3-agent system produces."""
    
    print_header("🏥 CLINICAL GUIDELINE RESEARCH ASSISTANT - DEMO")
    print("\n✅ 3-Agent System: Query+Filter → Retriever+Summarizer → Fact-Check+Writer")
    print("📋 Example Query: 'diabetes management in elderly patients'")
    print("💰 Cost: $0.00 (FREE with Ollama!)\n")
    
    # ==================================================================
    # AGENT 1 OUTPUT
    # ==================================================================
    print("\n▶ AGENT 1: Query+Filter Agent")
    print("-" * 70)
    print("Task: Expand query into optimized searches with MeSH terms\n")
    
    print("📊 Expanded Queries:")
    print("   1. (diabetes mellitus AND elderly) AND (management OR treatment)")
    print("   2. elderly population AND diabetes complications")
    print("   3. geriatric care AND glycemic control")
    
    print("\n🏷️  MeSH Terms Generated:")
    print("   • Diabetes Mellitus [MeSH]")
    print("   • Aged [MeSH]")
    print("   • Geriatrics [MeSH]")
    print("   • Blood Glucose Management [MeSH]")
    
    print("\n✓ Domain Vetting: HIPAA compliant, FDA policy checked")
    
    # ==================================================================
    # AGENT 2 OUTPUT
    # ==================================================================
    print("\n▶ AGENT 2: Retriever+Summarizer Agent")
    print("-" * 70)
    print("Task: Hybrid BM25+Vector search, then hierarchical summarization\n")
    
    print("🔍 Retrieved 3 Clinical Documents:")
    print("   1. Diabetes Management in Elderly: Updated Guidelines 2023")
    print("   2. SGLT2 Inhibitors: Benefits and Risks in Geriatric Populations")
    print("   3. Hypoglycemia Prevention Strategies in Elderly Diabetics")
    
    print("\n📄 Hierarchical Summary:")
    print("   Synthesis: Current evidence supports individualized HbA1c targets")
    print("   of 7.0-8.0% for elderly diabetic patients to minimize hypoglycemia")
    print("   risk. Metformin remains first-line therapy when renal function permits.")
    
    print("\n⚠️  Contradictions Detected: 1")
    print("   • SGLT2 inhibitors show cardiovascular benefits but require careful")
    print("     monitoring for dehydration in patients >75 years")
    
    # ==================================================================
    # AGENT 3 OUTPUT
    # ==================================================================
    print("\n▶ AGENT 3: Fact-Check+Writer Agent")
    print("-" * 70)
    print("Task: Verify claims, write brief with citations, generate traceability\n")
    
    print("📋 Executive Brief (287 words):")
    print("-" * 70)
    brief = """
Diabetes management in elderly patients requires careful individualization 
to balance glycemic control with safety [1]. Current guidelines recommend 
HbA1c targets between 7.0-8.0% for most patients aged 65 and older, 
recognizing the increased risk of severe hypoglycemia in this population [1][2].

Metformin remains the first-line pharmacological therapy when renal function 
is adequate (eGFR >30 mL/min/1.73m²) [1]. For patients requiring additional 
glucose-lowering therapy, SGLT2 inhibitors offer cardiovascular benefits but 
require monitoring for dehydration and urinary tract infections, particularly 
in those over 75 years [2].

Key risk mitigation strategies include regular glucose monitoring, medication 
review every 6 months, and patient education on hypoglycemia recognition [3]. 
Relaxed glycemic targets have been shown to reduce severe hypoglycemia events 
by up to 40% without significantly increasing long-term complications [3].

CONTRAINDICATION WARNING: SGLT2 inhibitors should be used cautiously in elderly 
patients with recurrent UTIs or volume depletion risk [2].
    """
    print(brief.strip())
    print("-" * 70)
    
    print("\n📚 Sources: 3")
    print("   [1] Smith J, Johnson M. \"Diabetes Management in Elderly\" (2023)")
    print("       DOI: 10.1234/diabetes.2023, Citations: 145")
    print("   [2] Lee A, Chen B. \"SGLT2 Inhibitors in Geriatric Populations\" (2023)")
    print("       DOI: 10.5678/cardio.2023, Citations: 89")
    print("   [3] Garcia R, Martinez E. \"Hypoglycemia Prevention Strategies\" (2023)")
    print("       DOI: 10.9012/endo.2023, Citations: 67")
    
    print("\n⚠️  Risk Flags: 2")
    print("   • [MEDIUM] Contraindication: SGLT2 use in volume-depleted elderly")
    print("   • [LOW] Study bias: Industry-funded SGLT2 trials")
    
    print("\n🔍 Traceability Appendix (3 claims verified):")
    print("   Claim 1: \"HbA1c targets 7.0-8.0% for elderly\"")
    print("   → Source [1], Confidence: 0.95, Status: VERIFIED")
    print("   → Passage: \"Individualized HbA1c targets of 7.0-8.0% reduce...")
    
    print("   Claim 2: \"SGLT2 inhibitors show cardiovascular benefits\"")
    print("   → Source [2], Confidence: 0.88, Status: VERIFIED")
    print("   → Passage: \"SGLT2 inhibitors show cardiovascular benefits...")
    
    print("   Claim 3: \"Relaxed targets reduce hypoglycemia by 40%\"")
    print("   → Source [3], Confidence: 0.92, Status: VERIFIED")
    print("   → Passage: \"Evidence shows that relaxed glycemic targets...")
    
    # ==================================================================
    # SUMMARY
    # ==================================================================
    print_header("✅ COMPLETE DELIVERABLE PACKAGE")
    
    print("\n📦 Generated Outputs:")
    print("   ✓ Executive Brief (287 words) with inline citations [1][2][3]")
    print("   ✓ Source List with DOIs, authors, quality scores")
    print("   ✓ Risk Flags for contradictions and safety concerns")
    print("   ✓ Traceability Appendix mapping every claim → source passages")
    
    print("\n🎯 Quality Metrics:")
    print("   • Sources Retrieved: 3")
    print("   • Citations Confidence: >0.85")
    print("   • Claims Verified: 3/3 (100%)")
    print("   • Contradictions Detected: 1")
    print("   • Risk Flags: 2")
    
    print("\n💰 Total Cost: $0.00 (FREE with Ollama!)")
    print("⏱️  Processing Time: ~25-35 seconds (all 3 agents)")
    
    print_header("🚀 SYSTEM CAPABILITIES DEMONSTRATED")
    
    print("\n✨ What This System Does:")
    print("   1. Expands clinical queries with MeSH terms (Agent 1)")
    print("   2. Searches BM25+Vector databases (Agent 2)")
    print("   3. Generates hierarchical summaries (Agent 2)")
    print("   4. Fact-checks every claim (Agent 3)")
    print("   5. Writes professional briefs with citations (Agent 3)")
    print("   6. Detects contradictions and safety risks (All agents)")
    print("   7. Provides full traceability claim→source (Agent 3)")
    
    print("\n🔧 To Run Live:")
    print("   1. Ensure Ollama is running: ollama serve")
    print("   2. Run single agent: .\\py311.bat test_with_ollama.py")
    print("   3. Run full pipeline: .\\py311.bat demo_full_pipeline.py (slower)")
    
    print("\n" + "=" * 70 + "\n")


if __name__ == "__main__":
    main()
