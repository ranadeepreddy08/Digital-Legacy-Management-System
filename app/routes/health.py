from fastapi import APIRouter
from app.database import check_connection, init_schema

router = APIRouter()

@router.get("", summary="Check Neo4j Database Connection & Health Status")
def get_health_status():
    """
    Returns connection status, server version, URI, and entity counts from Neo4j.
    """
    return check_connection()

@router.post("/init-schema", summary="Initialize Database Constraints and Indexes")
def run_schema_initialization():
    """
    Applies uniqueness constraints and indexes defined in cypher/schema.cypher idempotently.
    """
    return init_schema()
