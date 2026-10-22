from fastapi import APIRouter
from app.database import run_query

router = APIRouter()

@router.get("/stats", summary="Get Dashboard Statistic Counts")
def get_dashboard_stats():
    """
    Returns counts of all primary entities and relationships directly from Neo4j.
    """
    query = """
    RETURN {
      users: count { MATCH (:User) },
      assets: count { MATCH (:DigitalAsset) },
      nominees: count { MATCH (:Nominee) },
      executors: count { MATCH (:TrustedExecutor) },
      plans: count { MATCH (:LegacyPlan) },
      releases: count { MATCH (:ScheduledRelease) },
      total_relationships: count { MATCH ()-[]->() }
    } AS stats
    """
    results = run_query(query)
    if results and "stats" in results[0]:
        return results[0]["stats"]
    return {
        "users": 0, "assets": 0, "nominees": 0,
        "executors": 0, "plans": 0, "releases": 0,
        "total_relationships": 0
    }

@router.get("/recent-activity", summary="Get Recent Entity Additions and Updates")
def get_recent_activity():
    """
    Fetches the 8 most recently added items across Users, Assets, and Plans.
    """
    query = """
    CALL {
      MATCH (u:User)
      RETURN u.id AS id, u.name AS title, 'User' AS type, u.created_at AS timestamp, u.status AS status
      UNION ALL
      MATCH (a:DigitalAsset)
      RETURN a.id AS id, a.title AS title, 'DigitalAsset' AS type, a.created_at AS timestamp, a.priority AS status
      UNION ALL
      MATCH (p:LegacyPlan)
      RETURN p.id AS id, p.title AS title, 'LegacyPlan' AS type, p.created_at AS timestamp, p.status AS status
    }
    RETURN id, title, type, timestamp, status
    ORDER BY timestamp DESC
    LIMIT 8
    """
    return run_query(query)

@router.get("/upcoming-releases", summary="Get Upcoming Scheduled Releases")
def get_upcoming_releases():
    """
    Returns scheduled release records ordered by release date.
    """
    query = """
    MATCH (r:ScheduledRelease)
    OPTIONAL MATCH (p:LegacyPlan)-[:HAS_RELEASE]->(r)
    OPTIONAL MATCH (u:User)-[:HAS_PLAN]->(p)
    OPTIONAL MATCH (p)-[:INCLUDES_ASSET]->(a:DigitalAsset)
    OPTIONAL MATCH (p)-[:ASSIGNS_NOMINEE]->(n:Nominee)
    RETURN r.id AS id,
           r.release_date AS release_date,
           r.status AS status,
           r.notification_method AS notification_method,
           p.title AS plan_title,
           u.name AS owner_name,
           collect(DISTINCT a.title) AS assets,
           collect(DISTINCT n.name) AS nominees
    ORDER BY r.release_date ASC
    LIMIT 6
    """
    return run_query(query)
