import uuid
from datetime import datetime, timezone
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Query
from app.database import run_query
from app.models.user import UserCreate, UserUpdate, UserResponse

router = APIRouter()

@router.get("", response_model=List[UserResponse], summary="List Users with Connected Counts")
def list_users(search: Optional[str] = Query(None, description="Search by name or email")):
    """
    List all users in the graph with counts of their assets, nominees, and plans.
    """
    if search:
        query = """
        MATCH (u:User)
        WHERE toLower(u.name) CONTAINS toLower($search) OR toLower(u.email) CONTAINS toLower($search)
        OPTIONAL MATCH (u)-[:HAS_ASSET]->(a:DigitalAsset)
        OPTIONAL MATCH (u)-[:HAS_NOMINEE]->(n:Nominee)
        OPTIONAL MATCH (u)-[:HAS_PLAN]->(p:LegacyPlan)
        RETURN u.id AS id, u.name AS name, u.email AS email, u.phone AS phone,
               u.status AS status, u.created_at AS created_at,
               count(DISTINCT a) AS asset_count,
               count(DISTINCT n) AS nominee_count,
               count(DISTINCT p) AS plan_count
        ORDER BY u.created_at DESC
        """
        return run_query(query, {"search": search})
    else:
        query = """
        MATCH (u:User)
        OPTIONAL MATCH (u)-[:HAS_ASSET]->(a:DigitalAsset)
        OPTIONAL MATCH (u)-[:HAS_NOMINEE]->(n:Nominee)
        OPTIONAL MATCH (u)-[:HAS_PLAN]->(p:LegacyPlan)
        RETURN u.id AS id, u.name AS name, u.email AS email, u.phone AS phone,
               u.status AS status, u.created_at AS created_at,
               count(DISTINCT a) AS asset_count,
               count(DISTINCT n) AS nominee_count,
               count(DISTINCT p) AS plan_count
        ORDER BY u.created_at DESC
        """
        return run_query(query)

@router.get("/{user_id}", summary="Get User Details with Connected Graph Entities")
def get_user_details(user_id: str):
    """
    Retrieve a single user along with their owned assets, nominated beneficiaries,
    assigned executors, and legacy plans.
    """
    query = """
    MATCH (u:User {id: $user_id})
    OPTIONAL MATCH (u)-[:HAS_ASSET]->(a:DigitalAsset)
    OPTIONAL MATCH (u)-[:HAS_NOMINEE]->(n:Nominee)
    OPTIONAL MATCH (u)-[:HAS_EXECUTOR]->(e:TrustedExecutor)
    OPTIONAL MATCH (u)-[:HAS_PLAN]->(p:LegacyPlan)
    RETURN u.id AS id, u.name AS name, u.email AS email, u.phone AS phone,
           u.status AS status, u.created_at AS created_at,
           collect(DISTINCT {id: a.id, title: a.title, type: a.asset_type, priority: a.priority}) AS assets,
           collect(DISTINCT {id: n.id, name: n.name, relationship: n.relationship}) AS nominees,
           collect(DISTINCT {id: e.id, name: e.name, status: e.verification_status}) AS executors,
           collect(DISTINCT {id: p.id, title: p.title, status: p.status}) AS plans
    """
    results = run_query(query, {"user_id": user_id})
    if not results or not results[0].get("id"):
        raise HTTPException(status_code=404, detail=f"User with ID '{user_id}' not found.")
    return results[0]

@router.post("", response_model=UserResponse, status_code=201, summary="Create a New User")
def create_user(payload: UserCreate):
    """
    Create a new User node with unique ID constraint.
    """
    user_id = payload.id.strip() if payload.id and payload.id.strip() else f"usr_{uuid.uuid4().hex[:8]}"
    created_at = datetime.now(timezone.utc).isoformat()

    query = """
    CREATE (u:User {
        id: $id,
        name: $name,
        email: $email,
        phone: $phone,
        status: $status,
        created_at: $created_at
    })
    RETURN u.id AS id, u.name AS name, u.email AS email, u.phone AS phone,
           u.status AS status, u.created_at AS created_at,
           0 AS asset_count, 0 AS nominee_count, 0 AS plan_count
    """
    params = {
        "id": user_id,
        "name": payload.name,
        "email": payload.email,
        "phone": payload.phone or "",
        "status": payload.status,
        "created_at": created_at
    }
    results = run_query(query, params)
    return results[0]

@router.put("/{user_id}", response_model=UserResponse, summary="Update an Existing User")
def update_user(user_id: str, payload: UserUpdate):
    """
    Update properties of an existing User node.
    """
    # Build dynamic SET clause
    set_clauses = []
    params = {"user_id": user_id}

    if payload.name is not None:
        set_clauses.append("u.name = $name")
        params["name"] = payload.name
    if payload.email is not None:
        set_clauses.append("u.email = $email")
        params["email"] = payload.email
    if payload.phone is not None:
        set_clauses.append("u.phone = $phone")
        params["phone"] = payload.phone
    if payload.status is not None:
        set_clauses.append("u.status = $status")
        params["status"] = payload.status

    if not set_clauses:
        raise HTTPException(status_code=400, detail="No fields provided to update.")

    query = f"""
    MATCH (u:User {id: $user_id})
    SET {', '.join(set_clauses)}
    WITH u
    OPTIONAL MATCH (u)-[:HAS_ASSET]->(a:DigitalAsset)
    OPTIONAL MATCH (u)-[:HAS_NOMINEE]->(n:Nominee)
    OPTIONAL MATCH (u)-[:HAS_PLAN]->(p:LegacyPlan)
    RETURN u.id AS id, u.name AS name, u.email AS email, u.phone AS phone,
           u.status AS status, u.created_at AS created_at,
           count(DISTINCT a) AS asset_count,
           count(DISTINCT n) AS nominee_count,
           count(DISTINCT p) AS plan_count
    """
    results = run_query(query, params)
    if not results:
        raise HTTPException(status_code=404, detail=f"User with ID '{user_id}' not found.")
    return results[0]

@router.delete("/{user_id}", summary="Delete User and Detach Relationships")
def delete_user(user_id: str):
    """
    Safely delete a User node and all its connected relationships in Neo4j.
    """
    query = """
    MATCH (u:User {id: $user_id})
    WITH u, u.name AS deleted_name
    DETACH DELETE u
    RETURN deleted_name
    """
    results = run_query(query, {"user_id": user_id})
    if not results:
        raise HTTPException(status_code=404, detail=f"User with ID '{user_id}' not found.")
    return {
        "status": "success",
        "message": f"User '{results[0]['deleted_name']}' ({user_id}) deleted successfully."
    }
