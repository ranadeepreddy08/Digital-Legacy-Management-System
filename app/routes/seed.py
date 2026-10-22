from pathlib import Path
from fastapi import APIRouter, HTTPException
from app.database import run_query, init_schema
from app.config import BASE_DIR

router = APIRouter()

@router.post("/sample-data", summary="Seed Sample Data Idempotently")
def seed_sample_data():
    """
    Applies schema constraints and executes the seed.cypher script to create
    realistic interconnected test records for Users, DigitalAssets, Nominees,
    TrustedExecutors, LegacyPlans, and ScheduledReleases.
    """
    # 1. Ensure constraints and indexes are active
    init_schema()

    # 2. Read cypher/seed.cypher
    seed_file = BASE_DIR / "cypher" / "seed.cypher"
    if not seed_file.exists():
        raise HTTPException(status_code=500, detail="Seed file cypher/seed.cypher not found.")

    content = seed_file.read_text(encoding="utf-8")

    # Split cypher statements by semicolon
    statements = [stmt.strip() for stmt in content.split(";") if stmt.strip() and not stmt.strip().startswith("//")]

    executed_count = 0
    errors = []

    for stmt in statements:
        # Filter comments within statement
        lines = [line for line in stmt.splitlines() if not line.strip().startswith("//")]
        clean_stmt = "\n".join(lines).strip()
        if not clean_stmt:
            continue
        try:
            run_query(clean_stmt)
            executed_count += 1
        except Exception as e:
            errors.append(f"Error executing statement: {e}")

    # Fetch updated counts
    count_query = """
    RETURN {
      users: count { MATCH (:User) },
      assets: count { MATCH (:DigitalAsset) },
      nominees: count { MATCH (:Nominee) },
      executors: count { MATCH (:TrustedExecutor) },
      plans: count { MATCH (:LegacyPlan) },
      releases: count { MATCH (:ScheduledRelease) },
      total_relationships: count { MATCH ()-[]->() }
    } AS counts
    """
    counts_res = run_query(count_query)
    current_counts = counts_res[0]["counts"] if counts_res else {}

    return {
        "status": "success" if not errors else "partial_success",
        "message": "Sample data seeded successfully into Neo4j graph database.",
        "statements_executed": executed_count,
        "counts": current_counts,
        "errors": errors
    }

@router.post("/clear-database", summary="Reset Database (Delete All Nodes & Relationships)")
def clear_database():
    """
    Clears all nodes and relationships from the database.
    WARNING: Use only for testing or demonstration resets.
    """
    count_before = run_query("RETURN count { MATCH (n) } AS total_nodes")
    total_deleted = count_before[0]["total_nodes"] if count_before else 0

    run_query("MATCH (n) DETACH DELETE n")

    return {
        "status": "success",
        "message": f"Database cleared. Deleted {total_deleted} nodes and all associated relationships.",
        "nodes_deleted": total_deleted
    }
