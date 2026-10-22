import uuid
from datetime import datetime, timezone
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Query
from app.database import run_query
from app.models.asset import DigitalAssetCreate, DigitalAssetUpdate, DigitalAssetResponse

router = APIRouter()

@router.get("", response_model=List[DigitalAssetResponse], summary="List Digital Assets with Ownership & Beneficiaries")
def list_assets(
    search: Optional[str] = Query(None, description="Search by title or type"),
    asset_type: Optional[str] = Query(None, description="Filter by asset type"),
    priority: Optional[str] = Query(None, description="Filter by priority"),
    orphan_only: bool = Query(False, description="Filter only orphaned assets without nominees")
):
    """
    List all digital assets with owner name, designated nominee, managing executor, and plan title.
    """
    where_clauses = []
    params = {}

    if search:
        where_clauses.append("(toLower(a.title) CONTAINS toLower($search) OR toLower(a.asset_type) CONTAINS toLower($search))")
        params["search"] = search
    if asset_type:
        where_clauses.append("a.asset_type = $asset_type")
        params["asset_type"] = asset_type
    if priority:
        where_clauses.append("a.priority = $priority")
        params["priority"] = priority
    if orphan_only:
        where_clauses.append("NOT (()-[*1..2]->(a)) OR NOT (()<-[:DESIGNATED_FOR]-(:Nominee))")

    where_stmt = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

    query = f"""
    MATCH (a:DigitalAsset)
    {where_stmt}
    OPTIONAL MATCH (u:User)-[:HAS_ASSET]->(a)
    OPTIONAL MATCH (n:Nominee)-[des:DESIGNATED_FOR]->(a)
    OPTIONAL MATCH (e:TrustedExecutor)-[:CAN_MANAGE]->(a)
    OPTIONAL MATCH (p:LegacyPlan)-[:INCLUDES_ASSET]->(a)
    RETURN a.id AS id,
           a.title AS title,
           a.asset_type AS asset_type,
           a.access_info_encrypted_hint AS access_info_encrypted_hint,
           a.priority AS priority,
           a.estimated_value AS estimated_value,
           a.created_at AS created_at,
           u.id AS owner_id,
           u.name AS owner_name,
           n.id AS designated_nominee_id,
           n.name AS designated_nominee_name,
           des.share_pct AS nominee_share_pct,
           e.id AS managing_executor_id,
           e.name AS managing_executor_name,
           p.title AS plan_title
    ORDER BY a.created_at DESC
    """
    return run_query(query, params)

@router.get("/{asset_id}", summary="Get Digital Asset Details with Full Provenance")
def get_asset_details(asset_id: str):
    """
    Get deep graph relationships of a specific digital asset.
    """
    query = """
    MATCH (a:DigitalAsset {id: $asset_id})
    OPTIONAL MATCH (u:User)-[:HAS_ASSET]->(a)
    OPTIONAL MATCH (n:Nominee)-[des:DESIGNATED_FOR]->(a)
    OPTIONAL MATCH (e:TrustedExecutor)-[m:CAN_MANAGE]->(a)
    OPTIONAL MATCH (p:LegacyPlan)-[:INCLUDES_ASSET]->(a)
    OPTIONAL MATCH (a)-[:HAS_RELEASE]->(r:ScheduledRelease)
    RETURN a.id AS id,
           a.title AS title,
           a.asset_type AS asset_type,
           a.access_info_encrypted_hint AS access_info_encrypted_hint,
           a.priority AS priority,
           a.estimated_value AS estimated_value,
           a.created_at AS created_at,
           {id: u.id, name: u.name, email: u.email} AS owner,
           collect(DISTINCT {id: n.id, name: n.name, relationship: n.relationship, share_pct: des.share_pct}) AS nominees,
           collect(DISTINCT {id: e.id, name: e.name, auth_level: m.auth_level}) AS executors,
           collect(DISTINCT {id: p.id, title: p.title, status: p.status}) AS plans,
           collect(DISTINCT {id: r.id, date: r.release_date, status: r.status}) AS releases
    """
    results = run_query(query, {"asset_id": asset_id})
    if not results or not results[0].get("id"):
        raise HTTPException(status_code=404, detail=f"Digital Asset with ID '{asset_id}' not found.")
    return results[0]

@router.post("", response_model=DigitalAssetResponse, status_code=201, summary="Create Digital Asset")
def create_asset(payload: DigitalAssetCreate):
    """
    Create a new DigitalAsset node and link to owner, nominee, or executor.
    """
    asset_id = payload.id.strip() if payload.id and payload.id.strip() else f"ast_{uuid.uuid4().hex[:8]}"
    created_at = datetime.now(timezone.utc).isoformat()

    # Create the asset node
    query = """
    CREATE (a:DigitalAsset {
        id: $id,
        title: $title,
        asset_type: $asset_type,
        access_info_encrypted_hint: $access_hint,
        priority: $priority,
        estimated_value: $estimated_value,
        created_at: $created_at
    })
    RETURN a.id AS id, a.title AS title, a.asset_type AS asset_type,
           a.access_info_encrypted_hint AS access_info_encrypted_hint,
           a.priority AS priority, a.estimated_value AS estimated_value,
           a.created_at AS created_at
    """
    params = {
        "id": asset_id,
        "title": payload.title,
        "asset_type": payload.asset_type,
        "access_hint": payload.access_info_encrypted_hint,
        "priority": payload.priority,
        "estimated_value": payload.estimated_value or "Not Specified",
        "created_at": created_at
    }
    run_query(query, params)

    # Link Owner if provided
    if payload.owner_id:
        link_owner_query = """
        MATCH (u:User {id: $owner_id}), (a:DigitalAsset {id: $asset_id})
        MERGE (u)-[:HAS_ASSET]->(a)
        """
        run_query(link_owner_query, {"owner_id": payload.owner_id, "asset_id": asset_id})

    # Link Nominee if provided
    if payload.designated_nominee_id:
        link_nominee_query = """
        MATCH (n:Nominee {id: $nominee_id}), (a:DigitalAsset {id: $asset_id})
        MERGE (n)-[:DESIGNATED_FOR {share_pct: $share_pct, designation_type: 'Primary Beneficiary'}]->(a)
        """
        run_query(link_nominee_query, {
            "nominee_id": payload.designated_nominee_id,
            "asset_id": asset_id,
            "share_pct": payload.nominee_share_pct or 100
        })

    # Link Executor if provided
    if payload.managing_executor_id:
        link_executor_query = """
        MATCH (e:TrustedExecutor {id: $executor_id}), (a:DigitalAsset {id: $asset_id})
        MERGE (e)-[:CAN_MANAGE {auth_level: 'Full Administration', verified: true}]->(a)
        """
        run_query(link_executor_query, {"executor_id": payload.managing_executor_id, "asset_id": asset_id})

    # Return refreshed response
    detail_query = """
    MATCH (a:DigitalAsset {id: $asset_id})
    OPTIONAL MATCH (u:User)-[:HAS_ASSET]->(a)
    OPTIONAL MATCH (n:Nominee)-[des:DESIGNATED_FOR]->(a)
    OPTIONAL MATCH (e:TrustedExecutor)-[:CAN_MANAGE]->(a)
    OPTIONAL MATCH (p:LegacyPlan)-[:INCLUDES_ASSET]->(a)
    RETURN a.id AS id, a.title AS title, a.asset_type AS asset_type,
           a.access_info_encrypted_hint AS access_info_encrypted_hint,
           a.priority AS priority, a.estimated_value AS estimated_value,
           a.created_at AS created_at,
           u.id AS owner_id, u.name AS owner_name,
           n.id AS designated_nominee_id, n.name AS designated_nominee_name,
           des.share_pct AS nominee_share_pct,
           e.id AS managing_executor_id, e.name AS managing_executor_name,
           p.title AS plan_title
    """
    res = run_query(detail_query, {"asset_id": asset_id})
    return res[0]

@router.put("/{asset_id}", response_model=DigitalAssetResponse, summary="Update Digital Asset")
def update_asset(asset_id: str, payload: DigitalAssetUpdate):
    """
    Update digital asset properties and re-link relationships.
    """
    set_clauses = []
    params = {"asset_id": asset_id}

    if payload.title is not None:
        set_clauses.append("a.title = $title")
        params["title"] = payload.title
    if payload.asset_type is not None:
        set_clauses.append("a.asset_type = $asset_type")
        params["asset_type"] = payload.asset_type
    if payload.access_info_encrypted_hint is not None:
        set_clauses.append("a.access_info_encrypted_hint = $access_hint")
        params["access_hint"] = payload.access_info_encrypted_hint
    if payload.priority is not None:
        set_clauses.append("a.priority = $priority")
        params["priority"] = payload.priority
    if payload.estimated_value is not None:
        set_clauses.append("a.estimated_value = $estimated_value")
        params["estimated_value"] = payload.estimated_value

    if set_clauses:
        update_query = f"""
        MATCH (a:DigitalAsset {id: $asset_id})
        SET {', '.join(set_clauses)}
        """
        run_query(update_query, params)

    # Update Owner relationship if specified
    if payload.owner_id is not None:
        # Remove old owner relationship and add new one
        relink_owner = """
        MATCH (a:DigitalAsset {id: $asset_id})
        OPTIONAL MATCH (:User)-[r:HAS_ASSET]->(a)
        DELETE r
        WITH a
        MATCH (u:User {id: $owner_id})
        MERGE (u)-[:HAS_ASSET]->(a)
        """
        run_query(relink_owner, {"asset_id": asset_id, "owner_id": payload.owner_id})

    # Update Nominee designation if specified
    if payload.designated_nominee_id is not None:
        relink_nominee = """
        MATCH (a:DigitalAsset {id: $asset_id})
        OPTIONAL MATCH (:Nominee)-[r:DESIGNATED_FOR]->(a)
        DELETE r
        WITH a
        MATCH (n:Nominee {id: $nominee_id})
        MERGE (n)-[:DESIGNATED_FOR {share_pct: $share_pct, designation_type: 'Primary Beneficiary'}]->(a)
        """
        run_query(relink_nominee, {
            "asset_id": asset_id,
            "nominee_id": payload.designated_nominee_id,
            "share_pct": payload.nominee_share_pct or 100
        })

    # Return updated asset
    detail_query = """
    MATCH (a:DigitalAsset {id: $asset_id})
    OPTIONAL MATCH (u:User)-[:HAS_ASSET]->(a)
    OPTIONAL MATCH (n:Nominee)-[des:DESIGNATED_FOR]->(a)
    OPTIONAL MATCH (e:TrustedExecutor)-[:CAN_MANAGE]->(a)
    OPTIONAL MATCH (p:LegacyPlan)-[:INCLUDES_ASSET]->(a)
    RETURN a.id AS id, a.title AS title, a.asset_type AS asset_type,
           a.access_info_encrypted_hint AS access_info_encrypted_hint,
           a.priority AS priority, a.estimated_value AS estimated_value,
           a.created_at AS created_at,
           u.id AS owner_id, u.name AS owner_name,
           n.id AS designated_nominee_id, n.name AS designated_nominee_name,
           des.share_pct AS nominee_share_pct,
           e.id AS managing_executor_id, e.name AS managing_executor_name,
           p.title AS plan_title
    """
    res = run_query(detail_query, {"asset_id": asset_id})
    if not res:
        raise HTTPException(status_code=404, detail=f"Digital Asset with ID '{asset_id}' not found.")
    return res[0]

@router.delete("/{asset_id}", summary="Delete Digital Asset")
def delete_asset(asset_id: str):
    """
    Safely delete a DigitalAsset node and remove all attached graph edges.
    """
    query = """
    MATCH (a:DigitalAsset {id: $asset_id})
    WITH a, a.title AS deleted_title
    DETACH DELETE a
    RETURN deleted_title
    """
    results = run_query(query, {"asset_id": asset_id})
    if not results:
        raise HTTPException(status_code=404, detail=f"Digital Asset with ID '{asset_id}' not found.")
    return {
        "status": "success",
        "message": f"Digital Asset '{results[0]['deleted_title']}' ({asset_id}) deleted successfully."
    }
