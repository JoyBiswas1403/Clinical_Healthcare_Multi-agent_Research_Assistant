"""Agent 1: Query+Filter - Policy-aware search query expansion and domain vetting."""
import time
from typing import List, Dict, Any
from openai import OpenAI
from data.models import AgentOutput
from config.settings import settings


QUERY_EXPANSION_PROMPT = """You are a clinical research query expert. Given a research topic, expand it into:
1. 3-5 optimized search queries for academic databases
2. Key MeSH terms and synonyms
3. Exclusion criteria (irrelevant topics to filter out)
4. Source type priorities (RCT, meta-analysis, clinical guidelines, etc.)

Topic: {topic}
Date Range: {date_range}
Include Gray Literature: {include_gray}

Return a JSON object with:
{{
  "expanded_queries": ["query1", "query2", ...],
  "mesh_terms": ["term1", "term2", ...],
  "synonyms": {{"concept": ["syn1", "syn2"]}},
  "exclusion_criteria": ["criterion1", "criterion2", ...],
  "source_priorities": ["type1", "type2", ...]
}}
"""


DOMAIN_VETTING_PROMPT = """You are a clinical domain expert. Assess whether the following search results are relevant and trustworthy for the research topic.

Topic: {topic}
Search Results: {results}

For each result, evaluate:
1. Domain relevance (0.0-1.0)
2. Source credibility (0.0-1.0)
3. Potential bias flags
4. Policy compliance (HIPAA, FDA guidelines, clinical standards)

Return JSON:
{{
  "vetted_results": [
    {{
      "result_id": "...",
      "relevance_score": 0.9,
      "credibility_score": 0.85,
      "bias_flags": ["industry_funded"],
      "policy_compliant": true,
      "keep": true,
      "reason": "..."
    }}
  ]
}}
"""


class QueryFilterAgent:
    """Agent 1: Expands queries and filters results by domain policy."""
    
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
        self.temperature = settings.query_filter_temperature
    
    def expand_query(
        self,
        topic: str,
        date_range: tuple = None,
        include_gray_literature: bool = False
    ) -> Dict[str, Any]:
        """Expand a research topic into optimized search queries."""
        date_str = f"{date_range[0]} to {date_range[1]}" if date_range else "Any"
        
        prompt = QUERY_EXPANSION_PROMPT.format(
            topic=topic,
            date_range=date_str,
            include_gray=include_gray_literature
        )
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a clinical research query expert."},
                {"role": "user", "content": prompt}
            ],
            temperature=self.temperature,
            response_format={"type": "json_object"}
        )
        
        import json
        return json.loads(response.choices[0].message.content)
    
    def vet_results(
        self,
        topic: str,
        search_results: List[Dict[str, Any]],
        quality_threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """Vet search results for domain relevance and policy compliance."""
        # Batch results for efficiency (process in chunks of 10)
        chunk_size = 10
        vetted_all = []
        
        for i in range(0, len(search_results), chunk_size):
            chunk = search_results[i:i + chunk_size]
            
            prompt = DOMAIN_VETTING_PROMPT.format(
                topic=topic,
                results=str(chunk)
            )
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a clinical domain vetting expert."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                response_format={"type": "json_object"}
            )
            
            import json
            vetted_chunk = json.loads(response.choices[0].message.content)
            vetted_all.extend(vetted_chunk.get("vetted_results", []))
        
        # Filter by quality threshold
        filtered = [
            r for r in vetted_all
            if r.get("keep", False)
            and (r.get("relevance_score", 0) + r.get("credibility_score", 0)) / 2 >= quality_threshold
        ]
        
        return filtered
    
    def run(
        self,
        topic: str,
        max_sources: int = 15,
        quality_threshold: float = 0.7,
        include_gray_literature: bool = False,
        date_range: tuple = None,
        mock_search_results: List[Dict[str, Any]] = None
    ) -> AgentOutput:
        """Execute the full query+filter pipeline."""
        start_time = time.time()
        errors = []
        metrics = {}
        
        try:
            # Step 1: Expand query
            expansion = self.expand_query(topic, date_range, include_gray_literature)
            metrics["expanded_queries_count"] = len(expansion.get("expanded_queries", []))
            metrics["mesh_terms_count"] = len(expansion.get("mesh_terms", []))
            
            # Step 2: Vet results (in production, this would vet actual search results)
            # For now, we pass through mock data or return expansion
            vetted = []
            if mock_search_results:
                vetted = self.vet_results(topic, mock_search_results, quality_threshold)
                metrics["results_before_vetting"] = len(mock_search_results)
                metrics["results_after_vetting"] = len(vetted)
                metrics["vetting_filter_rate"] = 1 - (len(vetted) / max(len(mock_search_results), 1))
            
            output_data = {
                "expansion": expansion,
                "vetted_results": vetted[:max_sources],
                "topic": topic
            }
            
        except Exception as e:
            errors.append(str(e))
            output_data = {"error": str(e)}
        
        execution_time_ms = (time.time() - start_time) * 1000
        
        return AgentOutput(
            agent_name="QueryFilterAgent",
            output_data=output_data,
            metrics=metrics,
            errors=errors,
            execution_time_ms=execution_time_ms
        )
