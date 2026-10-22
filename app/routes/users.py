import uuid
import logging
from datetime import datetime, timezone
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Query
from app.database import run_query
from app.models.user import UserCreate, UserUpdate, UserResponse
from app import oracle_db

logger = logging.getLogger("digital_legacy.routes.users")

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

@router.post("", response_model=UserResponse, status_code=201, summary="Create a New User (Dual-Database: Oracle + Neo4j)")
def create_user(payload: UserCreate):
    """
    Create a new user with dual-database persistence in both Oracle (USERS table)
    and Neo4j (:User node) using a shared user_id and timestamp.

    Coordinated Dual-Write Behavior:
    1. Check for duplicates in Neo4j to prevent collision before writes.
    2. Persist to Oracle USERS table with parameterized SQL and explicit transaction.
    3. Persist to Neo4j graph with parameterized Cypher.
    4. If Neo4j write fails, perform a compensating delete in Oracle for only this request's ID.
    5. Return success only when both writes succeed.
    """
    # Generate single consistent identifier and creation timestamp for both databases
    user_id = payload.id.strip() if payload.id and payload.id.strip() else f"usr_{uuid.uuid4().hex[:8]}"
    created_at_dt = datetime.now(timezone.utc)
    created_at_iso = created_at_dt.isoformat()

    # 1. Pre-write duplicate check in Neo4j to avoid partial writes
    dup_check_query = """
    MATCH (u:User)
    WHERE u.id = $id OR toLower(u.email) = toLower($email)
    RETURN u.id AS id, u.email AS email
    LIMIT 1
    """
    existing_users = run_query(dup_check_query, {"id": user_id, "email": payload.email})
    if existing_users:
        raise HTTPException(
            status_code=409,
            detail=f"Conflict: User with ID '{user_id}' or email '{payload.email}' already exists in Neo4j."
        )

    # 2. Step 1: Write to Oracle USERS table
    try:
        oracle_db.insert_oracle_user(
            user_id=user_id,
            name=payload.name,
            email=payload.email,
            phone=payload.phone,
            status=payload.status,
            created_at=created_at_dt
        )
    except oracle_db.OracleNotConfiguredError as err:
        logger.error(f"Oracle write halted: {err}")
        raise HTTPException(
            status_code=503,
            detail=f"Oracle database not configured. Dual-database write requires both databases. Error: {str(err)}"
        )
    except oracle_db.OracleDuplicateError as err:
        logger.warning(f"Duplicate user in Oracle: {err}")
        raise HTTPException(
            status_code=409,
            detail=f"Conflict in Oracle database: {str(err)}"
        )
    except Exception as err:
        logger.error(f"Oracle write failed for user '{user_id}': {err}")
        raise HTTPException(
            status_code=500,
            detail=f"Oracle database write failed. User creation aborted; Neo4j was not modified. Error: {str(err)}"
        )

    # 3. Step 2: Write to Neo4j Graph Database
    neo4j_query = """
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
    neo4j_params = {
        "id": user_id,
        "name": payload.name,
        "email": payload.email,
        "phone": payload.phone or "",
        "status": payload.status,
        "created_at": created_at_iso
    }

    try:
        results = run_query(neo4j_query, neo4j_params)
        if not results:
            raise RuntimeError("Neo4j query did not return created user record.")
    except Exception as neo4j_err:
        logger.error(
            f"Neo4j write failed for user '{user_id}': {neo4j_err}. "
            f"Executing compensating delete in Oracle to maintain consistency..."
        )
        try:
            oracle_db.delete_oracle_user(user_id)
            comp_note = "A compensating delete was successfully executed on Oracle. Consistency maintained."
        except Exception as comp_err:
            logger.critical(
                f"RECONCILIATION REQUIRED: Both Neo4j write and Oracle compensating delete failed for user '{user_id}'! "
                f"User exists in Oracle USERS but NOT in Neo4j. "
                f"Neo4j error: {neo4j_err} | Oracle compensation error: {comp_err}."
            )
            comp_note = (
                f"CRITICAL: Compensating delete on Oracle also failed ({comp_err}). "
                f"Inconsistent record remains in Oracle USERS table for user_id='{user_id}'. "
                f"Manual reconciliation required: run SQL 'DELETE FROM USERS WHERE user_id = \\'{user_id}\\'; COMMIT;'."
            )
        raise HTTPException(
            status_code=500,
            detail=f"Neo4j write failed: {str(neo4j_err)}. {comp_note}"
        )

    logger.info(f"User '{user_id}' ({payload.email}) successfully created across both Oracle and Neo4j.")
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
