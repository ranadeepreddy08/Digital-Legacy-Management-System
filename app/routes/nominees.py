import uuid
from datetime import datetime, timezone
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Query
from app.database import run_query
from app.models.nominee import NomineeCreate, NomineeUpdate, NomineeResponse

router = APIRouter()

@router.get("", response_model=List[NomineeResponse], summary="List Nominees with Associated Users & Assets")
def list_nominees(search: Optional[str] = Query(None, description="Search by name, relationship, or email")):
    """
    List all nominees with their appointing user and designated assets.
    """
    where_clause = ""
    params = {}
    if search:
        where_clause = "WHERE toLower(n.name) CONTAINS toLower($search) OR toLower(n.relationship) CONTAINS toLower($search) OR toLower(n.email) CONTAINS toLower($search)"
        params["search"] = search

    query = f"""
    MATCH (n:Nominee)
    {where_clause}
    OPTIONAL MATCH (u:User)-[:HAS_NOMINEE]->(n)
    OPTIONAL MATCH (n)-[:DESIGNATED_FOR]->(a:DigitalAsset)
    RETURN n.id AS id,
           n.name AS name,
           n.relationship AS relationship,
           n.email AS email,
           n.phone AS phone,
           n.allocation_percentage AS allocation_percentage,
           n.created_at AS created_at,
           u.id AS user_id,
           u.name AS user_name,
           collect(DISTINCT a.title) AS designated_assets
    ORDER BY n.created_at DESC
    """
    return run_query(query, params)

@router.get("/{nominee_id}", summary="Get Nominee Details with Full Inheritance Links")
def get_nominee_details(nominee_id: str):
    """
    Get deep details of a nominee and all assets/plans where they are named.
    """
    query = """
    MATCH (n:Nominee {id: $nominee_id})
    OPTIONAL MATCH (u:User)-[:HAS_NOMINEE]->(n)
    OPTIONAL MATCH (n)-[des:DESIGNATED_FOR]->(a:DigitalAsset)
    OPTIONAL MATCH (p:LegacyPlan)-[:ASSIGNS_NOMINEE]->(n)
    RETURN n.id AS id,
           n.name AS name,
           n.relationship AS relationship,
           n.email AS email,
           n.phone AS phone,
           n.allocation_percentage AS allocation_percentage,
           n.created_at AS created_at,
           {id: u.id, name: u.name, email: u.email} AS user,
           collect(DISTINCT {id: a.id, title: a.title, type: a.asset_type, share: des.share_pct}) AS designated_assets,
           collect(DISTINCT {id: p.id, title: p.title, status: p.status}) AS associated_plans
    """
    results = run_query(query, {"nominee_id": nominee_id})
    if not results or not results[0].get("id"):
        raise HTTPException(status_code=404, detail=f"Nominee with ID '{nominee_id}' not found.")
    return results[0]

@router.post("", response_model=NomineeResponse, status_code=201, summary="Create Nominee")
def create_nominee(payload: NomineeCreate):
    """
    Create a new Nominee node, linking to user and designated asset.
    """
    nominee_id = payload.id.strip() if payload.id and payload.id.strip() else f"nom_{uuid.uuid4().hex[:8]}"
    created_at = datetime.now(timezone.utc).isoformat()

    query = """
    CREATE (n:Nominee {
        id: $id,
        name: $name,
        relationship: $relationship,
        email: $email,
        phone: $phone,
        allocation_percentage: $allocation_percentage,
        created_at: $created_at
    })
    RETURN n.id AS id, n.name AS name, n.relationship AS relationship,
           n.email AS email, n.phone AS phone,
           n.allocation_percentage AS allocation_percentage,
           n.created_at AS created_at
    """
    params = {
        "id": nominee_id,
        "name": payload.name,
        "relationship": payload.relationship,
        "email": payload.email,
        "phone": payload.phone or "",
        "allocation_percentage": payload.allocation_percentage,
        "created_at": created_at
    }
    run_query(query, params)

    if payload.user_id:
        link_user = """
        MATCH (u:User {id: $user_id}), (n:Nominee {id: $nominee_id})
        MERGE (u)-[:HAS_NOMINEE]->(n)
        """
        run_query(link_user, {"user_id": payload.user_id, "nominee_id": nominee_id})

    if payload.designated_asset_id:
        link_asset = """
        MATCH (n:Nominee {id: $nominee_id}), (a:DigitalAsset {id: $asset_id})
        MERGE (n)-[:DESIGNATED_FOR {share_pct: $share_pct, designation_type: 'Primary Beneficiary'}]->(a)
        """
        run_query(link_asset, {
            "nominee_id": nominee_id,
            "asset_id": payload.designated_asset_id,
            "share_pct": payload.allocation_percentage
        })

    # Return refreshed nominee
    refreshed = """
    MATCH (n:Nominee {id: $nominee_id})
    OPTIONAL MATCH (u:User)-[:HAS_NOMINEE]->(n)
    OPTIONAL MATCH (n)-[:DESIGNATED_FOR]->(a:DigitalAsset)
    RETURN n.id AS id, n.name AS name, n.relationship AS relationship,
           n.email AS email, n.phone AS phone,
           n.allocation_percentage AS allocation_percentage,
           n.created_at AS created_at,
           u.id AS user_id, u.name AS user_name,
           collect(DISTINCT a.title) AS designated_assets
    """
    res = run_query(refreshed, {"nominee_id": nominee_id})
    return res[0]

@router.put("/{nominee_id}", response_model=NomineeResponse, summary="Update Nominee")
def update_nominee(nominee_id: str, payload: NomineeUpdate):
    """
    Update nominee properties and re-link user or assets.
    """
    set_clauses = []
    params = {"nominee_id": nominee_id}

    if payload.name is not None:
        set_clauses.append("n.name = $name")
        params["name"] = payload.name
    if payload.relationship is not None:
        set_clauses.append("n.relationship = $relationship")
        params["relationship"] = payload.relationship
    if payload.email is not None:
        set_clauses.append("n.email = $email")
        params["email"] = payload.email
    if payload.phone is not None:
        set_clauses.append("n.phone = $phone")
        params["phone"] = payload.phone
    if payload.allocation_percentage is not None:
        set_clauses.append("n.allocation_percentage = $alloc")
        params["alloc"] = payload.allocation_percentage

    if set_clauses:
        run_query(f"MATCH (n:Nominee {{id: $nominee_id}}) SET {', '.join(set_clauses)}", params)

    if payload.user_id is not None:
        relink_user = """
        MATCH (n:Nominee {id: $nominee_id})
        OPTIONAL MATCH (:User)-[r:HAS_NOMINEE]->(n)
        DELETE r
        WITH n
        MATCH (u:User {id: $user_id})
        MERGE (u)-[:HAS_NOMINEE]->(n)
        """
        run_query(relink_user, {"nominee_id": nominee_id, "user_id": payload.user_id})

    refreshed = """
    MATCH (n:Nominee {id: $nominee_id})
    OPTIONAL MATCH (u:User)-[:HAS_NOMINEE]->(n)
    OPTIONAL MATCH (n)-[:DESIGNATED_FOR]->(a:DigitalAsset)
    RETURN n.id AS id, n.name AS name, n.relationship AS relationship,
           n.email AS email, n.phone AS phone,
           n.allocation_percentage AS allocation_percentage,
           n.created_at AS created_at,
           u.id AS user_id, u.name AS user_name,
           collect(DISTINCT a.title) AS designated_assets
    """
    res = run_query(refreshed, {"nominee_id": nominee_id})
    if not res:
        raise HTTPException(status_code=404, detail=f"Nominee with ID '{nominee_id}' not found.")
    return res[0]

@router.delete("/{nominee_id}", summary="Delete Nominee")
def delete_nominee(nominee_id: str):
    """
    Delete a Nominee node and detach relationships.
    """
    query = """
    MATCH (n:Nominee {id: $nominee_id})
    WITH n, n.name AS deleted_name
    DETACH DELETE n
    RETURN deleted_name
    """
    results = run_query(query, {"nominee_id": nominee_id})
    if not results:
        raise HTTPException(status_code=404, detail=f"Nominee with ID '{nominee_id}' not found.")
    return {
        "status": "success",
        "message": f"Nominee '{results[0]['deleted_name']}' ({nominee_id}) deleted successfully."
    }
