"""Initialize database and create indices."""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import create_engine
from elasticsearch import Elasticsearch
from pymilvus import connections, FieldSchema, CollectionSchema, DataType, Collection

from data.models import Base
from config.settings import settings


def init_postgres():
    """Create PostgreSQL tables."""
    print("Initializing PostgreSQL...")
    engine = create_engine(settings.database_url)
    Base.metadata.create_all(bind=engine)
    print("✓ PostgreSQL tables created")


def init_elasticsearch():
    """Create Elasticsearch index."""
    print("Initializing Elasticsearch...")
    try:
        es = Elasticsearch([settings.elasticsearch_url])
        
        if es.indices.exists(index=settings.elasticsearch_index):
            print(f"Index {settings.elasticsearch_index} already exists")
            return
        
        mapping = {
            "mappings": {
                "properties": {
                    "title": {"type": "text", "analyzer": "standard"},
                    "abstract": {"type": "text", "analyzer": "standard"},
                    "full_text": {"type": "text", "analyzer": "standard"},
                    "authors": {"type": "keyword"},
                    "doi": {"type": "keyword"},
                    "publication_date": {"type": "date"},
                    "source_type": {"type": "keyword"},
                    "quality_score": {"type": "float"},
                    "citation_count": {"type": "integer"}
                }
            }
        }
        
        es.indices.create(index=settings.elasticsearch_index, body=mapping)
        print(f"✓ Elasticsearch index '{settings.elasticsearch_index}' created")
    
    except Exception as e:
        print(f"✗ Elasticsearch initialization failed: {e}")


def init_milvus():
    """Create Milvus collection."""
    print("Initializing Milvus...")
    try:
        connections.connect(host=settings.milvus_host, port=settings.milvus_port)
        
        # Check if collection exists
        from pymilvus import utility
        if utility.has_collection(settings.milvus_collection):
            print(f"Collection {settings.milvus_collection} already exists")
            return
        
        # Define schema
        fields = [
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
            FieldSchema(name="doc_id", dtype=DataType.VARCHAR, max_length=255),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=384),  # all-MiniLM-L6-v2
            FieldSchema(name="title", dtype=DataType.VARCHAR, max_length=1000),
            FieldSchema(name="abstract", dtype=DataType.VARCHAR, max_length=5000)
        ]
        
        schema = CollectionSchema(
            fields=fields,
            description="Clinical document embeddings"
        )
        
        collection = Collection(
            name=settings.milvus_collection,
            schema=schema
        )
        
        # Create index
        index_params = {
            "metric_type": "L2",
            "index_type": "IVF_FLAT",
            "params": {"nlist": 128}
        }
        collection.create_index("embedding", index_params)
        
        print(f"✓ Milvus collection '{settings.milvus_collection}' created")
    
    except Exception as e:
        print(f"✗ Milvus initialization failed: {e}")


def main():
    """Initialize all data stores."""
    print("=" * 60)
    print("Clinical Guideline Assistant - Database Initialization")
    print("=" * 60)
    
    init_postgres()
    init_elasticsearch()
    init_milvus()
    
    print("\n" + "=" * 60)
    print("Initialization complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
