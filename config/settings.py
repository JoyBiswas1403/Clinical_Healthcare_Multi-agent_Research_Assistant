"""Configuration management using Pydantic Settings."""
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )
    
    # API Configuration
    api_host: str = Field(default="0.0.0.0")
    api_port: int = Field(default=8000)
    api_key_secret: str = Field(default="dev-secret-change-in-production")
    rate_limit_per_hour: int = Field(default=100)
    
    # LLM Configuration
    openai_api_key: str = Field(default="")
    anthropic_api_key: str = Field(default="")
    llm_model: str = Field(default="gpt-4-turbo-preview")
    embedding_model: str = Field(default="text-embedding-3-small")
    
    # Database
    postgres_host: str = Field(default="localhost")
    postgres_port: int = Field(default=5432)
    postgres_db: str = Field(default="clinical_guidelines")
    postgres_user: str = Field(default="postgres")
    postgres_password: str = Field(default="postgres")
    
    @property
    def database_url(self) -> str:
        """Construct database connection URL."""
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )
    
    # Elasticsearch
    elasticsearch_url: str = Field(default="http://localhost:9200")
    elasticsearch_index: str = Field(default="clinical_documents")
    
    # Vector DB - Milvus
    milvus_host: str = Field(default="localhost")
    milvus_port: int = Field(default=19530)
    milvus_collection: str = Field(default="document_embeddings")
    
    # Weaviate (Alternative)
    weaviate_url: str = Field(default="http://localhost:8080")
    weaviate_class: str = Field(default="ClinicalDocument")
    
    # Storage
    minio_endpoint: str = Field(default="localhost:9000")
    minio_access_key: str = Field(default="minioadmin")
    minio_secret_key: str = Field(default="minioadmin")
    minio_bucket: str = Field(default="clinical-docs")
    minio_secure: bool = Field(default=False)
    
    # Redis
    redis_host: str = Field(default="localhost")
    redis_port: int = Field(default=6379)
    redis_db: int = Field(default=0)
    
    @property
    def redis_url(self) -> str:
        """Construct Redis connection URL."""
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"
    
    # Celery
    celery_broker_url: str = Field(default="redis://localhost:6379/0")
    celery_result_backend: str = Field(default="redis://localhost:6379/0")
    
    # Temporal
    temporal_host: str = Field(default="localhost")
    temporal_port: int = Field(default=7233)
    temporal_namespace: str = Field(default="default")
    
    # Observability
    prometheus_port: int = Field(default=9090)
    jaeger_agent_host: str = Field(default="localhost")
    jaeger_agent_port: int = Field(default=6831)
    otel_exporter_jaeger_endpoint: str = Field(
        default="http://localhost:14268/api/traces"
    )
    
    # Agent Configuration
    query_filter_temperature: float = Field(default=0.3)
    retriever_top_k: int = Field(default=20)
    retriever_rerank_top_k: int = Field(default=10)
    summarizer_temperature: float = Field(default=0.4)
    fact_check_temperature: float = Field(default=0.1)
    writer_temperature: float = Field(default=0.5)
    brief_max_words: int = Field(default=300)
    
    # Quality Thresholds
    min_source_quality: float = Field(default=0.7)
    min_citation_confidence: float = Field(default=0.8)
    max_contradiction_score: float = Field(default=0.3)
    
    # Logging
    log_level: str = Field(default="INFO")
    log_format: str = Field(default="json")


# Global settings instance
settings = Settings()
