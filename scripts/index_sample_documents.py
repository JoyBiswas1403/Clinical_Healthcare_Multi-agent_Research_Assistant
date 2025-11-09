"""Index sample clinical documents into Elasticsearch and Milvus."""
import sys
sys.path.append(".")

from elasticsearch import Elasticsearch
from pymilvus import connections, Collection
from sentence_transformers import SentenceTransformer
from datetime import datetime

from config.settings import settings


# Sample clinical documents
SAMPLE_DOCUMENTS = [
    {
        "title": "Hypertension Management in Elderly Patients: A Systematic Review",
        "authors": ["Smith J", "Johnson M", "Williams K"],
        "abstract": "This systematic review examines optimal blood pressure targets for patients aged 65 and older. Evidence from 15 RCTs suggests that a target systolic BP of <150 mmHg reduces cardiovascular events while minimizing adverse effects. ACE inhibitors and calcium channel blockers demonstrate superior safety profiles in this population.",
        "full_text": "Full text content here...",
        "doi": "10.1001/jama.2023.12345",
        "url": "https://example.com/paper1",
        "publication_date": "2023-06-15",
        "source_type": "meta_analysis",
        "quality_score": 0.92,
        "citation_count": 234
    },
    {
        "title": "Diabetes Management Guidelines for Geriatric Populations",
        "authors": ["Lee A", "Chen B", "Garcia R"],
        "abstract": "Updated guidelines for managing type 2 diabetes in elderly patients emphasize individualized HbA1c targets (7.0-8.0%) to reduce hypoglycemia risk. Metformin remains first-line therapy when renal function permits. SGLT2 inhibitors show cardiovascular benefits but require monitoring for dehydration and UTIs.",
        "full_text": "Full text content here...",
        "doi": "10.2337/dc2023-0456",
        "url": "https://example.com/paper2",
        "publication_date": "2023-09-20",
        "source_type": "clinical_guideline",
        "quality_score": 0.95,
        "citation_count": 567
    },
    {
        "title": "Polypharmacy in Elderly Patients: Risks and Management Strategies",
        "authors": ["Brown P", "Davis L", "Martinez E"],
        "abstract": "Polypharmacy affects 40% of adults over 65 and increases risk of adverse drug events, falls, and cognitive decline. This review identifies high-risk medication combinations and provides deprescribing strategies. Focus on anticholinergics, benzodiazepines, and NSAIDs as priority targets for reduction.",
        "full_text": "Full text content here...",
        "doi": "10.1111/jgs.2023.7890",
        "url": "https://example.com/paper3",
        "publication_date": "2023-03-10",
        "source_type": "journal_article",
        "quality_score": 0.88,
        "citation_count": 189
    },
    {
        "title": "Cardiovascular Risk Assessment in Elderly Diabetic Patients",
        "authors": ["Wilson T", "Anderson K", "Thomas J"],
        "abstract": "Cardiovascular disease remains the leading cause of mortality in elderly diabetic patients. Novel risk stratification tools incorporating frailty indices and biomarkers improve prediction accuracy. Statin therapy shows consistent benefit across age groups, though bleeding risk with aspirin increases after age 75.",
        "full_text": "Full text content here...",
        "doi": "10.1161/circ.2023.3456",
        "url": "https://example.com/paper4",
        "publication_date": "2023-11-05",
        "source_type": "journal_article",
        "quality_score": 0.89,
        "citation_count": 145
    },
    {
        "title": "Anticoagulation in Elderly Patients with Atrial Fibrillation",
        "authors": ["Taylor M", "Moore R", "White D"],
        "abstract": "Direct oral anticoagulants (DOACs) demonstrate superior safety compared to warfarin in elderly patients with atrial fibrillation. Apixaban and rivaroxaban show lowest bleeding rates. Dose adjustments based on renal function and drug interactions are critical. CHA2DS2-VASc scores guide treatment decisions.",
        "full_text": "Full text content here...",
        "doi": "10.1016/j.jacc.2023.5678",
        "url": "https://example.com/paper5",
        "publication_date": "2023-07-22",
        "source_type": "rct",
        "quality_score": 0.94,
        "citation_count": 421
    }
]


def index_to_elasticsearch(documents):
    """Index documents into Elasticsearch."""
    print("Connecting to Elasticsearch...")
    es = Elasticsearch([settings.elasticsearch_url])
    
    indexed = 0
    for doc in documents:
        try:
            response = es.index(
                index=settings.elasticsearch_index,
                document=doc
            )
            indexed += 1
            print(f"✓ Indexed to Elasticsearch: {doc['title'][:60]}...")
        except Exception as e:
            print(f"✗ Error indexing to ES: {e}")
    
    print(f"\nElasticsearch: {indexed}/{len(documents)} documents indexed")


def index_to_milvus(documents):
    """Index document embeddings into Milvus."""
    print("\nConnecting to Milvus...")
    connections.connect(host=settings.milvus_host, port=settings.milvus_port)
    
    try:
        collection = Collection(settings.milvus_collection)
        collection.load()
    except Exception as e:
        print(f"Error connecting to Milvus collection: {e}")
        print("Make sure you've run 'python scripts/init_db.py' first!")
        return
    
    print("Generating embeddings...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    indexed = 0
    for i, doc in enumerate(documents):
        try:
            # Generate embedding from title + abstract
            text = f"{doc['title']} {doc['abstract']}"
            embedding = model.encode([text])[0].tolist()
            
            # Prepare data
            data = [
                [f"doc_{i}"],  # doc_id
                [embedding],   # embedding
                [doc['title']],
                [doc['abstract'][:4999]]  # Truncate to max length
            ]
            
            # Insert
            collection.insert(data)
            indexed += 1
            print(f"✓ Indexed to Milvus: {doc['title'][:60]}...")
        except Exception as e:
            print(f"✗ Error indexing to Milvus: {e}")
    
    # Flush to ensure data is persisted
    collection.flush()
    print(f"\nMilvus: {indexed}/{len(documents)} documents indexed")


def main():
    """Index sample documents."""
    print("=" * 70)
    print("Indexing Sample Clinical Documents")
    print("=" * 70)
    print()
    
    # Index to Elasticsearch
    index_to_elasticsearch(SAMPLE_DOCUMENTS)
    
    # Index to Milvus
    index_to_milvus(SAMPLE_DOCUMENTS)
    
    print("\n" + "=" * 70)
    print("Indexing complete!")
    print("=" * 70)
    print()
    print("You can now:")
    print("1. Test retrieval: python -c 'from agents.retriever_summarizer_agent import RetrieverSummarizerAgent; agent=RetrieverSummarizerAgent(); print(agent.bm25_search([\"diabetes elderly\"], top_k=3))'")
    print("2. Start the API and make research requests")
    print()


if __name__ == "__main__":
    main()
