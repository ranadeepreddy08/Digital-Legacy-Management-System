import uuid
from datetime import datetime, timezone
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Query
from app.database import run_query
from app.models.executor import ExecutorCreate, ExecutorUpdate, ExecutorResponse

router = APIRouter()

@router.get("", response_model=List[ExecutorResponse], summary="List Trusted Executors")
def list_executors(search: Optional[str] = Query(None, description="Search by name, email, or role")):
    """
    List all trusted executors with their appointing user and managed assets.
    """
    where_clause = ""
    params = {}
    if search:
        where_clause = "WHERE toLower(e.name) CONTAINS toLower($search) OR toLower(e.email) CONTAINS toLower($search) OR toLower(e.role_description) CONTAINS toLower($search)"
        params["search"] = search

    query = f"""
    MATCH (e:TrustedExecutor)
    {where_clause}
    OPTIONAL MATCH (u:User)-[:HAS_EXECUTOR]->(e)
    OPTIONAL MATCH (e)-[:CAN_MANAGE]->(a:DigitalAsset)
    RETURN e.id AS id,
           e.name AS name,
           e.email AS email,
           e.phone AS phone,
           e.verification_status AS verification_status,
           e.role_description AS role_description,
           e.created_at AS created_at,
           u.id AS user_id,
           u.name AS user_name,
           collect(DISTINCT a.title) AS managed_assets
    ORDER BY e.created_at DESC
    """
    return run_query(query, params)

@router.get("/{executor_id}", summary="Get Executor Details with Authorization Scopes")
def get_executor_details(executor_id: str):
    """
    Get deep details of an executor, including all managed assets and overseen legacy plans.
    """
    query = """
    MATCH (e:TrustedExecutor {id: $executor_id})
    OPTIONAL MATCH (u:User)-[:HAS_EXECUTOR]->(e)
    OPTIONAL MATCH (e)-[m:CAN_MANAGE]->(a:DigitalAsset)
    OPTIONAL MATCH (p:LegacyPlan)-[:OVERSEEN_BY]->(e)
    RETURN e.id AS id,
           e.name AS name,
           e.email AS email,
           e.phone AS phone,
           e.verification_status AS verification_status,
           e.role_description AS role_description,
           e.created_at AS created_at,
           {id: u.id, name: u.name, email: u.email} AS user,
           collect(DISTINCT {id: a.id, title: a.title, type: a.asset_type, auth_level: m.auth_level}) AS managed_assets,
           collect(DISTINCT {id: p.id, title: p.title, status: p.status}) AS overseen_plans
    """
    results = run_query(query, {"executor_id": executor_id})
    if not results or not results[0].get("id"):
        raise HTTPException(status_code=404, detail=f"Executor with ID '{executor_id}' not found.")
    return results[0]

@router.post("", response_model=ExecutorResponse, status_code=201, summary="Create Trusted Executor")
def create_executor(payload: ExecutorCreate):
    """
    Create a new TrustedExecutor node and link to User and Assets.
    """
    executor_id = payload.id.strip() if payload.id and payload.id.strip() else f"exe_{uuid.uuid4().hex[:8]}"
    created_at = datetime.now(timezone.utc).isoformat()

    query = """
    CREATE (e:TrustedExecutor {
        id: $id,
        name: $name,
        email: $email,
        phone: $phone,
        verification_status: $verification_status,
        role_description: $role_description,
        created_at: $created_at
    })
    RETURN e.id AS id, e.name AS name, e.email AS email, e.phone AS phone,
           e.verification_status AS verification_status,
           e.role_description AS role_description,
           e.created_at AS created_at
    """
    params = {
        "id": executor_id,
        "name": payload.name,
        "email": payload.email,
        "phone": payload.phone or "",
        "verification_status": payload.verification_status,
        "role_description": payload.role_description or "Digital Estate Custodian",
        "created_at": created_at
    }
    run_query(query, params)

    if payload.user_id:
        link_user = """
        MATCH (u:User {id: $user_id}), (e:TrustedExecutor {id: $executor_id})
        MERGE (u)-[:HAS_EXECUTOR]->(e)
        """
        run_query(link_user, {"user_id": payload.user_id, "executor_id": executor_id})

    if payload.authorized_asset_ids:
        for aid in payload.authorized_asset_ids:
            link_asset = """
            MATCH (e:TrustedExecutor {id: $executor_id}), (a:DigitalAsset {id: $asset_id})
            MERGE (e)-[:CAN_MANAGE {auth_level: 'Full Administration', verified: true}]->(a)
            """
            run_query(link_asset, {"executor_id": executor_id, "asset_id": aid})

    refreshed = """
    MATCH (e:TrustedExecutor {id: $executor_id})
    OPTIONAL MATCH (u:User)-[:HAS_EXECUTOR]->(e)
    OPTIONAL MATCH (e)-[:CAN_MANAGE]->(a:DigitalAsset)
    RETURN e.id AS id, e.name AS name, e.email AS email, e.phone AS phone,
           e.verification_status AS verification_status,
           e.role_description AS role_description,
           e.created_at AS created_at,
           u.id AS user_id, u.name AS user_name,
           collect(DISTINCT a.title) AS managed_assets
    """
    res = run_query(refreshed, {"executor_id": executor_id})
    return res[0]

@router.put("/{executor_id}", response_model=ExecutorResponse, summary="Update Trusted Executor")
def update_executor(executor_id: str, payload: ExecutorUpdate):
    """
    Update executor properties and re-link relationships.
    """
    set_clauses = []
    params = {"executor_id": executor_id}

    if payload.name is not None:
        set_clauses.append("e.name = $name")
        params["name"] = payload.name
    if payload.email is not None:
        set_clauses.append("e.email = $email")
        params["email"] = payload.email
    if payload.phone is not None:
        set_clauses.append("e.phone = $phone")
        params["phone"] = payload.phone
    if payload.verification_status is not None:
        set_clauses.append("e.verification_status = $ver_status")
        params["ver_status"] = payload.verification_status
    if payload.role_description is not None:
        set_clauses.append("e.role_description = $role_desc")
        params["role_desc"] = payload.role_description

    if set_clauses:
        run_query(f"MATCH (e:TrustedExecutor {{id: $executor_id}}) SET {', '.join(set_clauses)}", params)

    if payload.user_id is not None:
        relink_user = """
        MATCH (e:TrustedExecutor {id: $executor_id})
        OPTIONAL MATCH (:User)-[r:HAS_EXECUTOR]->(e)
        DELETE r
        WITH e
        MATCH (u:User {id: $user_id})
        MERGE (u)-[:HAS_EXECUTOR]->(e)
        """
        run_query(relink_user, {"executor_id": executor_id, "user_id": payload.user_id})

    if payload.authorized_asset_ids is not None:
        clear_links = """
        MATCH (e:TrustedExecutor {id: $executor_id})-[r:CAN_MANAGE]->(:DigitalAsset)
        DELETE r
        """
        run_query(clear_links, {"executor_id": executor_id})
        for aid in payload.authorized_asset_ids:
            relink_asset = """
            MATCH (e:TrustedExecutor {id: $executor_id}), (a:DigitalAsset {id: $asset_id})
            MERGE (e)-[:CAN_MANAGE {auth_level: 'Full Administration', verified: true}]->(a)
            """
            run_query(relink_asset, {"executor_id": executor_id, "asset_id": aid})

    refreshed = """
    MATCH (e:TrustedExecutor {id: $executor_id})
    OPTIONAL MATCH (u:User)-[:HAS_EXECUTOR]->(e)
    OPTIONAL MATCH (e)-[:CAN_MANAGE]->(a:DigitalAsset)
    RETURN e.id AS id, e.name AS name, e.email AS email, e.phone AS phone,
           e.verification_status AS verification_status,
           e.role_description AS role_description,
           e.created_at AS created_at,
           u.id AS user_id, u.name AS user_name,
           collect(DISTINCT a.title) AS managed_assets
    """
    res = run_query(refreshed, {"executor_id": executor_id})
    if not res:
        raise HTTPException(status_code=404, detail=f"Executor with ID '{executor_id}' not found.")
    return res[0]

@router.delete("/{executor_id}", summary="Delete Trusted Executor")
def delete_executor(executor_id: str):
    """
    Delete a TrustedExecutor node and detach relationships.
    """
    query = """
    MATCH (e:TrustedExecutor {id: $executor_id})
    WITH e, e.name AS deleted_name
    DETACH DELETE e
    RETURN deleted_name
    """
    results = run_query(query, {"executor_id": executor_id})
    if not results:
        raise HTTPException(status_code=404, detail=f"Executor with ID '{executor_id}' not found.")
    return {
        "status": "success",
        "message": f"Trusted Executor '{results[0]['deleted_name']}' ({executor_id}) deleted successfully."
    }
