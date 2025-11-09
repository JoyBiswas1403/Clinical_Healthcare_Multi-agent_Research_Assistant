"""Agent 3: Fact-Check+Writer - Claim-level verification, inline citations, traceability appendix."""
import time
import re
from typing import List, Dict, Any
from openai import OpenAI
from data.models import (
    AgentOutput, ResearchBrief, SourceMetadata, Citation, 
    RiskFlag, TraceabilityEntry
)
from config.settings import settings


FACT_CHECK_PROMPT = """You are a clinical fact-checking expert. Verify each claim against the provided sources.

Claim: {claim}
Sources: {sources}

For this claim:
1. Identify which sources support it
2. Extract exact passages that support the claim
3. Assess confidence level (0.0-1.0)
4. Flag any contradictions or uncertainties

Return JSON:
{{
  "claim": "...",
  "verification_status": "verified|uncertain|unsupported",
  "supporting_sources": [
    {{
      "source_id": "...",
      "passage": "...",
      "confidence": 0.9
    }}
  ],
  "contradictions": ["..."],
  "confidence": 0.9
}}
"""


BRIEF_WRITING_PROMPT = """You are a clinical research writer. Write a concise executive brief (≤300 words) with inline citations.

Topic: {topic}
Synthesis: {synthesis}
Source Summaries: {source_summaries}
Contradictions: {contradictions}

Requirements:
1. ≤300 words
2. Inline citations [1], [2], etc.
3. Clear, professional medical language
4. Address contradictions/limitations
5. Actionable insights for clinicians

Return JSON:
{{
  "brief_text": "...",
  "word_count": 250,
  "claims": [
    {{
      "claim_text": "...",
      "location": "paragraph 1, sentence 2",
      "citation_ids": ["1", "2"]
    }}
  ]
}}
"""


RISK_ASSESSMENT_PROMPT = """You are a clinical safety expert. Identify risks, contradictions, and quality issues.

Topic: {topic}
Sources: {sources}
Contradictions: {contradictions}

Identify:
1. Contradictions between sources (severity: high/medium/low)
2. Contraindications or safety concerns
3. Low-quality studies or bias
4. Data gaps or limitations

Return JSON:
{{
  "risk_flags": [
    {{
      "flag_type": "contradiction|contraindication|low_quality|bias",
      "severity": "high|medium|low",
      "description": "...",
      "affected_sources": ["id1", "id2"]
    }}
  ]
}}
"""


class FactCheckWriterAgent:
    """Agent 3: Verifies claims, writes brief with citations, generates traceability."""
    
    def __init__(self, use_ollama=False):
        if use_ollama:
            # Use free local Ollama
            self.client = OpenAI(
                base_url="http://localhost:11434/v1",
                api_key="ollama"
            )
            self.model = "llama3.2:3b"
        else:
            # Use OpenAI (requires credits)
            self.client = OpenAI(api_key=settings.openai_api_key)
            self.model = settings.llm_model
        self.fact_check_temp = settings.fact_check_temperature
        self.writer_temp = settings.writer_temperature
        self.max_words = settings.brief_max_words
    
    def fact_check_claim(
        self,
        claim: str,
        sources: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Fact-check a single claim against sources."""
        prompt = FACT_CHECK_PROMPT.format(
            claim=claim,
            sources=str(sources)
        )
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a clinical fact-checking expert."},
                {"role": "user", "content": prompt}
            ],
            temperature=self.fact_check_temp,
            response_format={"type": "json_object"}
        )
        
        import json
        return json.loads(response.choices[0].message.content)
    
    def write_brief(
        self,
        topic: str,
        summary_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Write executive brief with inline citations."""
        synthesis = summary_data.get("synthesis", "")
        source_summaries = summary_data.get("source_summaries", [])
        contradictions = summary_data.get("contradictions", [])
        
        prompt = BRIEF_WRITING_PROMPT.format(
            topic=topic,
            synthesis=synthesis,
            source_summaries=str(source_summaries),
            contradictions=str(contradictions)
        )
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a clinical research writer."},
                {"role": "user", "content": prompt}
            ],
            temperature=self.writer_temp,
            response_format={"type": "json_object"}
        )
        
        import json
        return json.loads(response.choices[0].message.content)
    
    def assess_risks(
        self,
        topic: str,
        sources: List[Dict[str, Any]],
        contradictions: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Assess risks, contradictions, and quality issues."""
        prompt = RISK_ASSESSMENT_PROMPT.format(
            topic=topic,
            sources=str(sources),
            contradictions=str(contradictions)
        )
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a clinical safety expert."},
                {"role": "user", "content": prompt}
            ],
            temperature=self.fact_check_temp,
            response_format={"type": "json_object"}
        )
        
        import json
        result = json.loads(response.choices[0].message.content)
        return result.get("risk_flags", [])
    
    def build_traceability(
        self,
        brief_claims: List[Dict[str, Any]],
        sources: List[Dict[str, Any]]
    ) -> List[TraceabilityEntry]:
        """Build traceability mapping from claims to sources."""
        traceability = []
        
        for claim_info in brief_claims:
            claim_text = claim_info.get("claim_text", "")
            
            # Fact-check the claim
            fact_check_result = self.fact_check_claim(claim_text, sources)
            
            supporting = []
            for source_info in fact_check_result.get("supporting_sources", []):
                supporting.append({
                    "source_id": source_info.get("source_id"),
                    "passage": source_info.get("passage"),
                    "confidence": source_info.get("confidence")
                })
            
            traceability.append(TraceabilityEntry(
                claim=claim_text,
                claim_location=claim_info.get("location", "unknown"),
                supporting_passages=supporting,
                verification_status=fact_check_result.get("verification_status", "uncertain")
            ))
        
        return traceability
    
    def extract_citations_from_brief(self, brief_text: str, sources: List[Dict]) -> List[Citation]:
        """Extract citation markers from brief and map to sources."""
        citations = []
        
        # Find all citation markers like [1], [2], etc.
        citation_pattern = r'\[(\d+)\]'
        matches = re.findall(citation_pattern, brief_text)
        
        for match in set(matches):
            idx = int(match) - 1
            if 0 <= idx < len(sources):
                source = sources[idx]
                citations.append(Citation(
                    citation_id=match,
                    source_id=source.get("doc_id", f"source_{idx}"),
                    passage=source.get("source", {}).get("abstract", "")[:200],
                    confidence=0.9
                ))
        
        return citations
    
    def run(
        self,
        topic: str,
        retrieved_docs: List[Dict[str, Any]],
        summary_data: Dict[str, Any]
    ) -> AgentOutput:
        """Execute fact-checking, writing, and traceability generation."""
        start_time = time.time()
        errors = []
        metrics = {}
        
        try:
            # Step 1: Write brief
            brief_data = self.write_brief(topic, summary_data)
            brief_text = brief_data.get("brief_text", "")
            word_count = brief_data.get("word_count", len(brief_text.split()))
            claims = brief_data.get("claims", [])
            
            metrics["word_count"] = word_count
            metrics["claims_count"] = len(claims)
            
            # Step 2: Extract sources metadata
            sources_metadata = []
            for doc in retrieved_docs:
                source = doc.get("source", {})
                sources_metadata.append(SourceMetadata(
                    source_id=doc.get("doc_id", "unknown"),
                    title=source.get("title", "Unknown"),
                    authors=source.get("authors", []),
                    publication_date=source.get("publication_date"),
                    doi=source.get("doi"),
                    url=source.get("url"),
                    source_type=source.get("source_type", "journal_article"),
                    quality_score=doc.get("hybrid_score", 0.0),
                    citation_count=source.get("citation_count", 0)
                ))
            
            # Step 3: Extract citations
            citations = self.extract_citations_from_brief(brief_text, retrieved_docs)
            metrics["citations_count"] = len(citations)
            
            # Step 4: Risk assessment
            contradictions = summary_data.get("contradictions", [])
            risk_flags_data = self.assess_risks(topic, retrieved_docs, contradictions)
            risk_flags = [RiskFlag(**rf) for rf in risk_flags_data]
            metrics["risk_flags_count"] = len(risk_flags)
            
            # Step 5: Build traceability
            traceability = self.build_traceability(claims, retrieved_docs)
            metrics["traceability_entries"] = len(traceability)
            
            # Step 6: Assemble final brief
            research_brief = ResearchBrief(
                executive_brief=brief_text,
                word_count=word_count,
                sources=sources_metadata,
                citations=citations,
                risk_flags=risk_flags,
                traceability=traceability,
                metadata={
                    "topic": topic,
                    "contradictions": contradictions,
                    "overall_quality": summary_data.get("overall_quality", "unknown")
                }
            )
            
            output_data = {
                "research_brief": research_brief.model_dump(),
                "topic": topic
            }
            
        except Exception as e:
            errors.append(str(e))
            output_data = {"error": str(e)}
        
        execution_time_ms = (time.time() - start_time) * 1000
        
        return AgentOutput(
            agent_name="FactCheckWriterAgent",
            output_data=output_data,
            metrics=metrics,
            errors=errors,
            execution_time_ms=execution_time_ms
        )
