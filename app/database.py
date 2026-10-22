import logging
from typing import Any, Dict, List, Optional
from neo4j import GraphDatabase, Driver, exceptions
from fastapi import HTTPException
from app.config import settings

logger = logging.getLogger("digital_legacy.database")

_driver: Optional[Driver] = None

def get_driver() -> Driver:
    """
    Get or initialize the singleton Neo4j driver instance.
    Configured with official neo4j driver connection pooling.
    """
    global _driver
    if _driver is None:
        try:
            logger.info(f"Connecting to Neo4j instance at {settings.NEO4J_URI}...")
            _driver = GraphDatabase.driver(
                settings.NEO4J_URI,
                auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD),
                max_connection_lifetime=30 * 60,
                max_connection_pool_size=50,
                connection_acquisition_timeout=5.0
            )
        except Exception as e:
            logger.error(f"Failed to initialize Neo4j driver: {e}")
            raise HTTPException(
                status_code=503,
                detail=f"Neo4j connection error: {str(e)}. Please ensure Neo4j is running at {settings.NEO4J_URI}."
            )
    return _driver

def close_driver() -> None:
    """Gracefully close the Neo4j driver connection pool."""
    global _driver
    if _driver is not None:
        logger.info("Closing Neo4j driver connection pool.")
        _driver.close()
        _driver = None

def check_connection() -> Dict[str, Any]:
    """
    Verify Neo4j connectivity and fetch basic status and node counts.
    Returns status dictionary for the /api/health endpoint.
    """
    try:
        driver = get_driver()
        driver.verify_connectivity()
        
        # Ping and get database edition / version
        records, summary, keys = driver.execute_query(
            "CALL dbms.components() YIELD name, versions, edition RETURN name, versions[0] AS version, edition",
            database_=settings.NEO4J_DATABASE
        )
        version_info = "Neo4j 5.x"
        edition_info = "Community"
        if records:
            version_info = f"{records[0].get('name', 'Neo4j')} {records[0].get('version', '')}"
            edition_info = records[0].get('edition', 'Community')

        # Count nodes by label
        count_records, _, _ = driver.execute_query(
            """
            RETURN {
              users: count { MATCH (:User) },
              assets: count { MATCH (:DigitalAsset) },
              nominees: count { MATCH (:Nominee) },
              executors: count { MATCH (:TrustedExecutor) },
              plans: count { MATCH (:LegacyPlan) },
              releases: count { MATCH (:ScheduledRelease) },
              total_relationships: count { MATCH ()-[]->() }
            } AS counts
            """,
            database_=settings.NEO4J_DATABASE
        )
        counts = count_records[0]["counts"] if count_records else {}

        return {
            "connected": True,
            "uri": settings.NEO4J_URI,
            "database": settings.NEO4J_DATABASE,
            "version": version_info,
            "edition": edition_info,
            "counts": counts,
            "message": "Neo4j graph database is connected and operational."
        }
    except Exception as e:
        logger.warning(f"Neo4j connectivity check failed: {e}")
        return {
            "connected": False,
            "uri": settings.NEO4J_URI,
            "database": settings.NEO4J_DATABASE,
            "error": str(e),
            "message": (
                "Cannot connect to Neo4j. Please start Neo4j (e.g. via 'start_neo4j.bat' or "
                f"Neo4j Desktop on {settings.NEO4J_URI}) and verify .env credentials."
            ),
            "counts": {
                "users": 0, "assets": 0, "nominees": 0,
                "executors": 0, "plans": 0, "releases": 0,
                "total_relationships": 0
            }
        }

def run_query(cypher: str, parameters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """
    Execute a parameterized Cypher query and return results as Python dictionaries.
    Uses official driver execute_query with automatic routing and session management.
    """
    try:
        driver = get_driver()
        records, summary, keys = driver.execute_query(
            cypher,
            parameters or {},
            database_=settings.NEO4J_DATABASE
        )
        results = []
        for record in records:
            # record.data() converts Record to pure dictionary
            results.append(record.data())
        return results
    except exceptions.ServiceUnavailable as e:
        logger.error(f"Neo4j Service Unavailable: {e}")
        raise HTTPException(
            status_code=503,
            detail=f"Neo4j database unavailable at {settings.NEO4J_URI}. Please verify that the Neo4j service is running."
        )
    except exceptions.ConstraintError as e:
        logger.warning(f"Neo4j Constraint Violation: {e}")
        raise HTTPException(
            status_code=400,
            detail=f"Integrity Constraint Violation: {e.message}"
        )
    except exceptions.CypherError as e:
        logger.error(f"Cypher Execution Error: {e}")
        raise HTTPException(
            status_code=400,
            detail=f"Database Query Error: {e.message}"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected Database Error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal Database Error: {str(e)}"
        )

def init_schema() -> Dict[str, Any]:
    """
    Initialize schema constraints and indexes.
    Idempotent execution using IF NOT EXISTS.
    """
    constraints_and_indexes = [
        # Uniqueness Constraints
        "CREATE CONSTRAINT user_id_unique IF NOT EXISTS FOR (u:User) REQUIRE u.id IS UNIQUE",
        "CREATE CONSTRAINT asset_id_unique IF NOT EXISTS FOR (a:DigitalAsset) REQUIRE a.id IS UNIQUE",
        "CREATE CONSTRAINT nominee_id_unique IF NOT EXISTS FOR (n:Nominee) REQUIRE n.id IS UNIQUE",
        "CREATE CONSTRAINT executor_id_unique IF NOT EXISTS FOR (e:TrustedExecutor) REQUIRE e.id IS UNIQUE",
        "CREATE CONSTRAINT plan_id_unique IF NOT EXISTS FOR (p:LegacyPlan) REQUIRE p.id IS UNIQUE",
        "CREATE CONSTRAINT release_id_unique IF NOT EXISTS FOR (r:ScheduledRelease) REQUIRE r.id IS UNIQUE",
        # Performance Indexes
        "CREATE INDEX user_email_idx IF NOT EXISTS FOR (u:User) ON (u.email)",
        "CREATE INDEX asset_type_idx IF NOT EXISTS FOR (a:DigitalAsset) ON (a.asset_type)",
        "CREATE INDEX asset_title_idx IF NOT EXISTS FOR (a:DigitalAsset) ON (a.title)",
        "CREATE INDEX release_date_idx IF NOT EXISTS FOR (r:ScheduledRelease) ON (r.release_date)",
        "CREATE INDEX release_status_idx IF NOT EXISTS FOR (r:ScheduledRelease) ON (r.status)"
    ]

    executed = 0
    errors = []
    for stmt in constraints_and_indexes:
        try:
            run_query(stmt)
            executed += 1
        except Exception as e:
            logger.warning(f"Constraint/Index execution warning: {e}")
            errors.append(str(e))

    return {
        "status": "success" if not errors else "partial",
        "statements_executed": executed,
        "total_statements": len(constraints_and_indexes),
        "errors": errors
    }
