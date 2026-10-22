import uuid
from datetime import datetime, timezone
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Query
from app.database import run_query
from app.models.plan import LegacyPlanCreate, LegacyPlanUpdate, LegacyPlanResponse

router = APIRouter()

@router.get("", response_model=List[LegacyPlanResponse], summary="List Legacy Plans")
def list_plans(search: Optional[str] = Query(None, description="Search by title, condition, or status")):
    """
    List all legacy plans with owner, assets, nominees, executors, and release date.
    """
    where_clause = ""
    params = {}
    if search:
        where_clause = "WHERE toLower(p.title) CONTAINS toLower($search) OR toLower(p.trigger_condition) CONTAINS toLower($search) OR toLower(p.status) CONTAINS toLower($search)"
        params["search"] = search

    query = f"""
    MATCH (p:LegacyPlan)
    {where_clause}
    OPTIONAL MATCH (u:User)-[:HAS_PLAN]->(p)
    OPTIONAL MATCH (p)-[:INCLUDES_ASSET]->(a:DigitalAsset)
    OPTIONAL MATCH (p)-[:ASSIGNS_NOMINEE]->(n:Nominee)
    OPTIONAL MATCH (p)-[:OVERSEEN_BY]->(e:TrustedExecutor)
    OPTIONAL MATCH (p)-[:HAS_RELEASE]->(r:ScheduledRelease)
    RETURN p.id AS id,
           p.title AS title,
           p.trigger_condition AS trigger_condition,
           p.status AS status,
           p.notes AS notes,
           p.created_at AS created_at,
           u.id AS user_id,
           u.name AS user_name,
           collect(DISTINCT a.title) AS included_assets,
           collect(DISTINCT n.name) AS assigned_nominees,
           collect(DISTINCT e.name) AS overseeing_executors,
           r.id AS release_id,
           r.release_date AS release_date
    ORDER BY p.created_at DESC
    """
    return run_query(query, params)

@router.get("/{plan_id}", summary="Get Legacy Plan with Complete Graph Connections")
def get_plan_details(plan_id: str):
    """
    Get deep graph relationships of a specific legacy plan.
    """
    query = """
    MATCH (p:LegacyPlan {id: $plan_id})
    OPTIONAL MATCH (u:User)-[:HAS_PLAN]->(p)
    OPTIONAL MATCH (p)-[:INCLUDES_ASSET]->(a:DigitalAsset)
    OPTIONAL MATCH (p)-[:ASSIGNS_NOMINEE]->(n:Nominee)
    OPTIONAL MATCH (p)-[:OVERSEEN_BY]->(e:TrustedExecutor)
    OPTIONAL MATCH (p)-[:HAS_RELEASE]->(r:ScheduledRelease)
    RETURN p.id AS id,
           p.title AS title,
           p.trigger_condition AS trigger_condition,
           p.status AS status,
           p.notes AS notes,
           p.created_at AS created_at,
           {id: u.id, name: u.name, email: u.email} AS user,
           collect(DISTINCT {id: a.id, title: a.title, type: a.asset_type, priority: a.priority}) AS assets,
           collect(DISTINCT {id: n.id, name: n.name, relationship: n.relationship}) AS nominees,
           collect(DISTINCT {id: e.id, name: e.name, status: e.verification_status}) AS executors,
           collect(DISTINCT {id: r.id, date: r.release_date, status: r.status, method: r.notification_method}) AS releases
    """
    results = run_query(query, {"plan_id": plan_id})
    if not results or not results[0].get("id"):
        raise HTTPException(status_code=404, detail=f"Legacy Plan with ID '{plan_id}' not found.")
    return results[0]

@router.post("", response_model=LegacyPlanResponse, status_code=201, summary="Create Legacy Plan")
def create_plan(payload: LegacyPlanCreate):
    """
    Create a new LegacyPlan node and connect to User, Assets, Nominees, Executors, and Releases.
    """
    plan_id = payload.id.strip() if payload.id and payload.id.strip() else f"pln_{uuid.uuid4().hex[:8]}"
    created_at = datetime.now(timezone.utc).isoformat()

    query = """
    CREATE (p:LegacyPlan {
        id: $id,
        title: $title,
        trigger_condition: $trigger_condition,
        status: $status,
        notes: $notes,
        created_at: $created_at
    })
    RETURN p.id AS id, p.title AS title, p.trigger_condition AS trigger_condition,
           p.status AS status, p.notes AS notes, p.created_at AS created_at
    """
    params = {
        "id": plan_id,
        "title": payload.title,
        "trigger_condition": payload.trigger_condition,
        "status": payload.status,
        "notes": payload.notes or "",
        "created_at": created_at
    }
    run_query(query, params)

    if payload.user_id:
        link_user = """
        MATCH (u:User {id: $user_id}), (p:LegacyPlan {id: $plan_id})
        MERGE (u)-[:HAS_PLAN]->(p)
        """
        run_query(link_user, {"user_id": payload.user_id, "plan_id": plan_id})

    if payload.asset_ids:
        for aid in payload.asset_ids:
            link_asset = """
            MATCH (p:LegacyPlan {id: $plan_id}), (a:DigitalAsset {id: $asset_id})
            MERGE (p)-[:INCLUDES_ASSET]->(a)
            """
            run_query(link_asset, {"plan_id": plan_id, "asset_id": aid})

    if payload.nominee_ids:
        for nid in payload.nominee_ids:
            link_nominee = """
            MATCH (p:LegacyPlan {id: $plan_id}), (n:Nominee {id: $nominee_id})
            MERGE (p)-[:ASSIGNS_NOMINEE]->(n)
            """
            run_query(link_nominee, {"plan_id": plan_id, "nominee_id": nid})

    if payload.executor_ids:
        for eid in payload.executor_ids:
            link_executor = """
            MATCH (p:LegacyPlan {id: $plan_id}), (e:TrustedExecutor {id: $executor_id})
            MERGE (p)-[:OVERSEEN_BY]->(e)
            """
            run_query(link_executor, {"plan_id": plan_id, "executor_id": eid})

    if payload.release_id:
        link_rel = """
        MATCH (p:LegacyPlan {id: $plan_id}), (r:ScheduledRelease {id: $release_id})
        MERGE (p)-[:HAS_RELEASE]->(r)
        """
        run_query(link_rel, {"plan_id": plan_id, "release_id": payload.release_id})

    # Return refreshed plan
    refreshed = """
    MATCH (p:LegacyPlan {id: $plan_id})
    OPTIONAL MATCH (u:User)-[:HAS_PLAN]->(p)
    OPTIONAL MATCH (p)-[:INCLUDES_ASSET]->(a:DigitalAsset)
    OPTIONAL MATCH (p)-[:ASSIGNS_NOMINEE]->(n:Nominee)
    OPTIONAL MATCH (p)-[:OVERSEEN_BY]->(e:TrustedExecutor)
    OPTIONAL MATCH (p)-[:HAS_RELEASE]->(r:ScheduledRelease)
    RETURN p.id AS id,
           p.title AS title,
           p.trigger_condition AS trigger_condition,
           p.status AS status,
           p.notes AS notes,
           p.created_at AS created_at,
           u.id AS user_id,
           u.name AS user_name,
           collect(DISTINCT a.title) AS included_assets,
           collect(DISTINCT n.name) AS assigned_nominees,
           collect(DISTINCT e.name) AS overseeing_executors,
           r.id AS release_id,
           r.release_date AS release_date
    """
    res = run_query(refreshed, {"plan_id": plan_id})
    return res[0]

@router.put("/{plan_id}", response_model=LegacyPlanResponse, summary="Update Legacy Plan")
def update_plan(plan_id: str, payload: LegacyPlanUpdate):
    """
    Update legacy plan properties and re-link relationships.
    """
    set_clauses = []
    params = {"plan_id": plan_id}

    if payload.title is not None:
        set_clauses.append("p.title = $title")
        params["title"] = payload.title
    if payload.trigger_condition is not None:
        set_clauses.append("p.trigger_condition = $condition")
        params["condition"] = payload.trigger_condition
    if payload.status is not None:
        set_clauses.append("p.status = $status")
        params["status"] = payload.status
    if payload.notes is not None:
        set_clauses.append("p.notes = $notes")
        params["notes"] = payload.notes

    if set_clauses:
        run_query(f"MATCH (p:LegacyPlan {{id: $plan_id}}) SET {', '.join(set_clauses)}", params)

    if payload.user_id is not None:
        relink_user = """
        MATCH (p:LegacyPlan {id: $plan_id})
        OPTIONAL MATCH (:User)-[r:HAS_PLAN]->(p)
        DELETE r
        WITH p
        MATCH (u:User {id: $user_id})
        MERGE (u)-[:HAS_PLAN]->(p)
        """
        run_query(relink_user, {"plan_id": plan_id, "user_id": payload.user_id})

    if payload.asset_ids is not None:
        run_query("MATCH (p:LegacyPlan {id: $plan_id})-[r:INCLUDES_ASSET]->(:DigitalAsset) DELETE r", {"plan_id": plan_id})
        for aid in payload.asset_ids:
            run_query("""
            MATCH (p:LegacyPlan {id: $plan_id}), (a:DigitalAsset {id: $asset_id})
            MERGE (p)-[:INCLUDES_ASSET]->(a)
            """, {"plan_id": plan_id, "asset_id": aid})

    if payload.nominee_ids is not None:
        run_query("MATCH (p:LegacyPlan {id: $plan_id})-[r:ASSIGNS_NOMINEE]->(:Nominee) DELETE r", {"plan_id": plan_id})
        for nid in payload.nominee_ids:
            run_query("""
            MATCH (p:LegacyPlan {id: $plan_id}), (n:Nominee {id: $nominee_id})
            MERGE (p)-[:ASSIGNS_NOMINEE]->(n)
            """, {"plan_id": plan_id, "nominee_id": nid})

    if payload.executor_ids is not None:
        run_query("MATCH (p:LegacyPlan {id: $plan_id})-[r:OVERSEEN_BY]->(:TrustedExecutor) DELETE r", {"plan_id": plan_id})
        for eid in payload.executor_ids:
            run_query("""
            MATCH (p:LegacyPlan {id: $plan_id}), (e:TrustedExecutor {id: $executor_id})
            MERGE (p)-[:OVERSEEN_BY]->(e)
            """, {"plan_id": plan_id, "executor_id": eid})

    refreshed = """
    MATCH (p:LegacyPlan {id: $plan_id})
    OPTIONAL MATCH (u:User)-[:HAS_PLAN]->(p)
    OPTIONAL MATCH (p)-[:INCLUDES_ASSET]->(a:DigitalAsset)
    OPTIONAL MATCH (p)-[:ASSIGNS_NOMINEE]->(n:Nominee)
    OPTIONAL MATCH (p)-[:OVERSEEN_BY]->(e:TrustedExecutor)
    OPTIONAL MATCH (p)-[:HAS_RELEASE]->(r:ScheduledRelease)
    RETURN p.id AS id,
           p.title AS title,
           p.trigger_condition AS trigger_condition,
           p.status AS status,
           p.notes AS notes,
           p.created_at AS created_at,
           u.id AS user_id,
           u.name AS user_name,
           collect(DISTINCT a.title) AS included_assets,
           collect(DISTINCT n.name) AS assigned_nominees,
           collect(DISTINCT e.name) AS overseeing_executors,
           r.id AS release_id,
           r.release_date AS release_date
    """
    res = run_query(refreshed, {"plan_id": plan_id})
    if not res:
        raise HTTPException(status_code=404, detail=f"Legacy Plan with ID '{plan_id}' not found.")
    return res[0]

@router.delete("/{plan_id}", summary="Delete Legacy Plan")
def delete_plan(plan_id: str):
    """
    Delete a LegacyPlan node and detach all relationships.
    """
    query = """
    MATCH (p:LegacyPlan {id: $plan_id})
    WITH p, p.title AS deleted_title
    DETACH DELETE p
    RETURN deleted_title
    """
    results = run_query(query, {"plan_id": plan_id})
    if not results:
        raise HTTPException(status_code=404, detail=f"Legacy Plan with ID '{plan_id}' not found.")
    return {
        "status": "success",
        "message": f"Legacy Plan '{results[0]['deleted_title']}' ({plan_id}) deleted successfully."
    }
