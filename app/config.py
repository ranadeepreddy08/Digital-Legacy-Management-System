import os
from pathlib import Path
from dotenv import load_dotenv

# Base directory of the repository
BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env file if present
load_dotenv(BASE_DIR / ".env")

class Settings:
    # Neo4j Graph Database Credentials
    NEO4J_URI: str = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    NEO4J_USER: str = os.getenv("NEO4J_USER", "neo4j")
    NEO4J_PASSWORD: str = os.getenv("NEO4J_PASSWORD", "password123")
    NEO4J_DATABASE: str = os.getenv("NEO4J_DATABASE", "neo4j")

    # FastAPI Application Config
    APP_HOST: str = os.getenv("APP_HOST", "127.0.0.1")
    APP_PORT: int = int(os.getenv("APP_PORT", "8000"))
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "info")

    PROJECT_NAME: str = "Digital Legacy Vault – DA3"
    PROJECT_DESCRIPTION: str = (
        "A Neo4j Graph-Powered Digital Legacy Management System demonstrating "
        "graph data modeling, Cypher traversals, and modern graph database engineering."
    )
    PROJECT_VERSION: str = "1.0.0"

settings = Settings()
