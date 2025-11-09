"""Simple test of Query+Filter Agent without database."""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from agents.query_filter_agent import QueryFilterAgent

print("=" * 60)
print("Testing Query+Filter Agent")
print("=" * 60)

agent = QueryFilterAgent()

print("\nExpanding query: 'diabetes management in elderly patients'")
result = agent.run(
    topic="diabetes management in elderly patients",
    max_sources=10,
    quality_threshold=0.7
)

print(f"\n✓ Agent: {result.agent_name}")
print(f"✓ Execution time: {result.execution_time_ms:.2f}ms")
print(f"✓ Errors: {result.errors if result.errors else 'None'}")

if 'expansion' in result.output_data:
    expansion = result.output_data['expansion']
    print(f"\n✓ Expanded queries ({len(expansion.get('expanded_queries', []))}):")
    for i, query in enumerate(expansion.get('expanded_queries', [])[:3], 1):
        print(f"   {i}. {query}")
    
    print(f"\n✓ MeSH terms ({len(expansion.get('mesh_terms', []))}):")
    for term in expansion.get('mesh_terms', [])[:5]:
        print(f"   - {term}")

print("\n" + "=" * 60)
print("✅ Test completed successfully!")
print("=" * 60)
