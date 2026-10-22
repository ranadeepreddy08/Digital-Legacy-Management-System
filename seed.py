"""
Digital Legacy Vault - Standalone Database Seeding Script
Run this script to initialize schema constraints and populate sample data directly:
    python seed.py
"""
import sys
from pathlib import Path
from app.config import settings, BASE_DIR
from app.database import init_schema, run_query, check_connection

def main():
    print("=" * 65)
    print("  DIGITAL LEGACY VAULT – DA3: Neo4j Data Seeding Utility")
    print("=" * 65)
    print(f"Target URI:      {settings.NEO4J_URI}")
    print(f"Target Database: {settings.NEO4J_DATABASE}")
    print(f"Database User:   {settings.NEO4J_USER}")
    print("-" * 65)

    # 1. Check connection
    print("[1/3] Testing Neo4j graph database connectivity...")
    status = check_connection()
    if not status.get("connected"):
        print("\n[ERROR] Could not connect to Neo4j:")
        print(f"  {status.get('message')}")
        print("\nTroubleshooting tips:")
        print("  1. If using Docker, run 'docker-compose up -d' or 'start_neo4j.bat'.")
        print("  2. If using Neo4j Desktop, ensure your database is started.")
        print("  3. Check .env to verify NEO4J_URI, NEO4J_USER, and NEO4J_PASSWORD.\n")
        sys.exit(1)

    print(f"  Connected to {status.get('version')} ({status.get('edition')} edition).")

    # 2. Apply constraints & indexes
    print("\n[2/3] Applying uniqueness constraints and performance indexes...")
    schema_res = init_schema()
    print(f"  Executed {schema_res.get('statements_executed')}/{schema_res.get('total_statements')} schema statements.")

    # 3. Read and execute seed.cypher
    print("\n[3/3] Seeding interconnected synthetic digital legacy graph...")
    seed_path = BASE_DIR / "cypher" / "seed.cypher"
    if not seed_path.exists():
        print(f"[ERROR] Could not find seed file at {seed_path}")
        sys.exit(1)

    content = seed_path.read_text(encoding="utf-8")
    statements = [stmt.strip() for stmt in content.split(";") if stmt.strip() and not stmt.strip().startswith("//")]

    success_count = 0
    for stmt in statements:
        lines = [line for line in stmt.splitlines() if not line.strip().startswith("//")]
        clean_stmt = "\n".join(lines).strip()
        if not clean_stmt:
            continue
        try:
            run_query(clean_stmt)
            success_count += 1
        except Exception as e:
            print(f"  Warning on statement: {e}")

    print(f"  Executed {success_count} Cypher seed statements.")

    # 4. Print final statistics
    counts_res = run_query("""
    RETURN {
      users: count { MATCH (:User) },
      assets: count { MATCH (:DigitalAsset) },
      nominees: count { MATCH (:Nominee) },
      executors: count { MATCH (:TrustedExecutor) },
      plans: count { MATCH (:LegacyPlan) },
      releases: count { MATCH (:ScheduledRelease) },
      relationships: count { MATCH ()-[]->() }
    } AS counts
    """)
    counts = counts_res[0]["counts"] if counts_res else {}

    print("-" * 65)
    print("Database seeding completed successfully! Current Graph Summary:")
    print(f"  Users:             {counts.get('users')}")
    print(f"  Digital Assets:    {counts.get('assets')}")
    print(f"  Nominees:          {counts.get('nominees')}")
    print(f"  Trusted Executors: {counts.get('executors')}")
    print(f"  Legacy Plans:      {counts.get('plans')}")
    print(f"  Scheduled Releases:{counts.get('releases')}")
    print(f"  Total Graph Edges: {counts.get('relationships')}")
    print("=" * 65)

if __name__ == "__main__":
    main()
