import uuid
from datetime import datetime, timezone
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Query
from app.database import run_query
from app.models.release import ScheduledReleaseCreate, ScheduledReleaseUpdate, ScheduledReleaseResponse

router = APIRouter()

@router.get("", response_model=List[ScheduledReleaseResponse], summary="List Scheduled Releases")
def list_releases(
    status: Optional[str] = Query(None, description="Filter by status (Scheduled, In Review, Released, Cancelled)"),
    search: Optional[str] = Query(None, description="Search by notes or notification method")
):
    """
    List scheduled release records with linked legacy plans and assets.
    """
    where_clauses = []
    params = {}
    if status:
        where_clauses.append("r.status = $status")
        params["status"] = status
    if search:
        where_clauses.append("(toLower(r.notes) CONTAINS toLower($search) OR toLower(r.notification_method) CONTAINS toLower($search))")
        params["search"] = search

    where_stmt = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

    query = f"""
    MATCH (r:ScheduledRelease)
    {where_stmt}
    OPTIONAL MATCH (p:LegacyPlan)-[:HAS_RELEASE]->(r)
    OPTIONAL MATCH (a:DigitalAsset)-[:HAS_RELEASE]->(r)
    RETURN r.id AS id,
           r.release_date AS release_date,
           r.status AS status,
           r.notification_method AS notification_method,
           r.notes AS notes,
           r.created_at AS created_at,
           p.id AS plan_id,
           p.title AS plan_title,
           a.id AS asset_id,
           a.title AS asset_title
    ORDER BY r.release_date ASC
    """
    return run_query(query, params)

@router.get("/{release_id}", summary="Get Scheduled Release Details")
def get_release_details(release_id: str):
    """
    Get full details of a specific scheduled release including its plan, assets, and beneficiaries.
    """
    query = """
    MATCH (r:ScheduledRelease {id: $release_id})
    OPTIONAL MATCH (p:LegacyPlan)-[:HAS_RELEASE]->(r)
    OPTIONAL MATCH (u:User)-[:HAS_PLAN]->(p)
    OPTIONAL MATCH (p)-[:INCLUDES_ASSET]->(a:DigitalAsset)
    OPTIONAL MATCH (p)-[:ASSIGNS_NOMINEE]->(n:Nominee)
    OPTIONAL MATCH (p)-[:OVERSEEN_BY]->(e:TrustedExecutor)
    RETURN r.id AS id,
           r.release_date AS release_date,
           r.status AS status,
           r.notification_method AS notification_method,
           r.notes AS notes,
           r.created_at AS created_at,
           {id: p.id, title: p.title, status: p.status} AS plan,
           {id: u.id, name: u.name} AS owner,
           collect(DISTINCT {id: a.id, title: a.title, type: a.asset_type}) AS assets,
           collect(DISTINCT {id: n.id, name: n.name}) AS nominees,
           collect(DISTINCT {id: e.id, name: e.name}) AS executors
    """
    results = run_query(query, {"release_id": release_id})
    if not results or not results[0].get("id"):
        raise HTTPException(status_code=404, detail=f"Scheduled Release with ID '{release_id}' not found.")
    return results[0]

@router.post("", response_model=ScheduledReleaseResponse, status_code=201, summary="Create Scheduled Release")
def create_release(payload: ScheduledReleaseCreate):
    """
    Create a new ScheduledRelease node and link to Plan and Asset.
    """
    release_id = payload.id.strip() if payload.id and payload.id.strip() else f"rel_{uuid.uuid4().hex[:8]}"
    created_at = datetime.now(timezone.utc).isoformat()

    query = """
    CREATE (r:ScheduledRelease {
        id: $id,
        release_date: $release_date,
        status: $status,
        notification_method: $notification_method,
        notes: $notes,
        created_at: $created_at
    })
    RETURN r.id AS id, r.release_date AS release_date,
           r.status AS status, r.notification_method AS notification_method,
           r.notes AS notes, r.created_at AS created_at
    """
    params = {
        "id": release_id,
        "release_date": payload.release_date,
        "status": payload.status,
        "notification_method": payload.notification_method,
        "notes": payload.notes or "",
        "created_at": created_at
    }
    run_query(query, params)

    if payload.plan_id:
        link_plan = """
        MATCH (p:LegacyPlan {id: $plan_id}), (r:ScheduledRelease {id: $release_id})
        MERGE (p)-[:HAS_RELEASE]->(r)
        """
        run_query(link_plan, {"plan_id": payload.plan_id, "release_id": release_id})

    if payload.asset_id:
        link_asset = """
        MATCH (a:DigitalAsset {id: $asset_id}), (r:ScheduledRelease {id: $release_id})
        MERGE (a)-[:HAS_RELEASE]->(r)
        """
        run_query(link_asset, {"asset_id": payload.asset_id, "release_id": release_id})

    refreshed = """
    MATCH (r:ScheduledRelease {id: $release_id})
    OPTIONAL MATCH (p:LegacyPlan)-[:HAS_RELEASE]->(r)
    OPTIONAL MATCH (a:DigitalAsset)-[:HAS_RELEASE]->(r)
    RETURN r.id AS id,
           r.release_date AS release_date,
           r.status AS status,
           r.notification_method AS notification_method,
           r.notes AS notes,
           r.created_at AS created_at,
           p.id AS plan_id,
           p.title AS plan_title,
           a.id AS asset_id,
           a.title AS asset_title
    """
    res = run_query(refreshed, {"release_id": release_id})
    return res[0]

@router.put("/{release_id}", response_model=ScheduledReleaseResponse, summary="Update Scheduled Release")
def update_release(release_id: str, payload: ScheduledReleaseUpdate):
    """
    Update release date, status workflow, or linked plan/asset.
    """
    set_clauses = []
    params = {"release_id": release_id}

    if payload.release_date is not None:
        set_clauses.append("r.release_date = $release_date")
        params["release_date"] = payload.release_date
    if payload.status is not None:
        set_clauses.append("r.status = $status")
        params["status"] = payload.status
    if payload.notification_method is not None:
        set_clauses.append("r.notification_method = $notif_method")
        params["notif_method"] = payload.notification_method
    if payload.notes is not None:
        set_clauses.append("r.notes = $notes")
        params["notes"] = payload.notes

    if set_clauses:
        run_query(f"MATCH (r:ScheduledRelease {{id: $release_id}}) SET {', '.join(set_clauses)}", params)

    if payload.plan_id is not None:
        relink_plan = """
        MATCH (r:ScheduledRelease {id: $release_id})
        OPTIONAL MATCH (:LegacyPlan)-[rel:HAS_RELEASE]->(r)
        DELETE rel
        WITH r
        MATCH (p:LegacyPlan {id: $plan_id})
        MERGE (p)-[:HAS_RELEASE]->(r)
        """
        run_query(relink_plan, {"release_id": release_id, "plan_id": payload.plan_id})

    if payload.asset_id is not None:
        relink_asset = """
        MATCH (r:ScheduledRelease {id: $release_id})
        OPTIONAL MATCH (:DigitalAsset)-[rel:HAS_RELEASE]->(r)
        DELETE rel
        WITH r
        MATCH (a:DigitalAsset {id: $asset_id})
        MERGE (a)-[:HAS_RELEASE]->(r)
        """
        run_query(relink_asset, {"release_id": release_id, "asset_id": payload.asset_id})

    refreshed = """
    MATCH (r:ScheduledRelease {id: $release_id})
    OPTIONAL MATCH (p:LegacyPlan)-[:HAS_RELEASE]->(r)
    OPTIONAL MATCH (a:DigitalAsset)-[:HAS_RELEASE]->(r)
    RETURN r.id AS id,
           r.release_date AS release_date,
           r.status AS status,
           r.notification_method AS notification_method,
           r.notes AS notes,
           r.created_at AS created_at,
           p.id AS plan_id,
           p.title AS plan_title,
           a.id AS asset_id,
           a.title AS asset_title
    """
    res = run_query(refreshed, {"release_id": release_id})
    if not res:
        raise HTTPException(status_code=404, detail=f"Scheduled Release with ID '{release_id}' not found.")
    return res[0]

@router.delete("/{release_id}", summary="Delete Scheduled Release")
def delete_release(release_id: str):
    """
    Delete a ScheduledRelease node and detach relationships.
    """
    query = """
    MATCH (r:ScheduledRelease {id: $release_id})
    WITH r, r.id AS deleted_id
    DETACH DELETE r
    RETURN deleted_id
    """
    results = run_query(query, {"release_id": release_id})
    if not results:
        raise HTTPException(status_code=404, detail=f"Scheduled Release with ID '{release_id}' not found.")
    return {
        "status": "success",
        "message": f"Scheduled Release '{results[0]['deleted_id']}' deleted successfully."
    }
