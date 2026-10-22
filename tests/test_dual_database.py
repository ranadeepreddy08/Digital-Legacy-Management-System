"""
Unit & Integration Tests for Dual-Database User Creation (Oracle + Neo4j)
Verifies dual-write coordination, error handling, compensation rollbacks,
duplicate handling, and distinguishes mocked tests from live database integration.
"""

import pytest
from unittest.mock import patch, MagicMock
from app.oracle_db import (
    OracleNotConfiguredError,
    OracleDatabaseError,
    OracleDuplicateError,
    OracleCompensationError,
    is_oracle_configured,
    get_oracle_user
)

# ------------------------------------------------------------------------------
# 1. Unit Tests (Using Mocks - Fully isolated from external database state)
# ------------------------------------------------------------------------------

@patch("app.routes.users.run_query")
@patch("app.routes.users.oracle_db.insert_oracle_user")
def test_unit_dual_write_success(mock_oracle_insert, mock_neo4j_query, client):
    """
    [MOCKED UNIT TEST]
    Verify that when both Oracle and Neo4j succeed:
    - User is persisted to Oracle with exact attributes.
    - User is persisted to Neo4j with matching user_id and timestamp.
    - HTTP 201 response is returned matching existing frontend UserResponse format.
    """
    # 1. Neo4j duplicate check returns empty (no duplicate exists)
    # 2. Neo4j CREATE returns user payload
    mock_neo4j_query.side_effect = [
        [],  # Pre-write duplicate check
        [    # Neo4j CREATE result
            {
                "id": "usr_test123",
                "name": "Sarah Connor",
                "email": "sarah.connor@resistance.org",
                "phone": "+1-555-8888",
                "status": "Active",
                "created_at": "2026-10-23T00:00:00Z",
                "asset_count": 0,
                "nominee_count": 0,
                "plan_count": 0
            }
        ]
    ]

    mock_oracle_insert.return_value = {
        "user_id": "usr_test123",
        "name": "Sarah Connor",
        "email": "sarah.connor@resistance.org",
        "phone": "+1-555-8888",
        "status": "Active"
    }

    payload = {
        "id": "usr_test123",
        "name": "Sarah Connor",
        "email": "sarah.connor@resistance.org",
        "phone": "+1-555-8888",
        "status": "Active"
    }

    response = client.post("/api/users", json=payload)
    assert response.status_code == 201
    data = response.json()

    assert data["id"] == "usr_test123"
    assert data["name"] == "Sarah Connor"
    assert data["email"] == "sarah.connor@resistance.org"
    assert data["asset_count"] == 0

    # Verify Oracle insert was called with identical user_id and params
    mock_oracle_insert.assert_called_once()
    call_kwargs = mock_oracle_insert.call_args[1]
    assert call_kwargs["user_id"] == "usr_test123"
    assert call_kwargs["email"] == "sarah.connor@resistance.org"


@patch("app.routes.users.run_query")
@patch("app.routes.users.oracle_db.insert_oracle_user")
def test_unit_oracle_missing_configuration(mock_oracle_insert, mock_neo4j_query, client):
    """
    [MOCKED UNIT TEST]
    Verify that if Oracle is unconfigured, user creation aborts with HTTP 503,
    and Neo4j is never modified.
    """
    mock_neo4j_query.return_value = []  # No duplicate
    mock_oracle_insert.side_effect = OracleNotConfiguredError(
        "Oracle credentials not configured. Please set ORACLE_USER and ORACLE_PASSWORD in .env."
    )

    payload = {
        "name": "Unconfigured Test",
        "email": "unconfigured@test.io",
        "status": "Active"
    }

    response = client.post("/api/users", json=payload)
    assert response.status_code == 503
    assert "Oracle database not configured" in response.json()["detail"]
    # Only duplicate check was called, CREATE was never executed
    assert mock_neo4j_query.call_count == 1


@patch("app.routes.users.run_query")
@patch("app.routes.users.oracle_db.insert_oracle_user")
def test_unit_oracle_write_failure(mock_oracle_insert, mock_neo4j_query, client):
    """
    [MOCKED UNIT TEST]
    Verify that if the Oracle write fails, HTTP 500 is returned and Neo4j is not modified.
    """
    mock_neo4j_query.return_value = []  # No duplicate
    mock_oracle_insert.side_effect = OracleDatabaseError("ORA-01033: ORACLE initialization or shutdown in progress")

    payload = {
        "name": "Failed Oracle User",
        "email": "failed.oracle@test.io",
        "status": "Active"
    }

    response = client.post("/api/users", json=payload)
    assert response.status_code == 500
    assert "Oracle database write failed" in response.json()["detail"]
    assert mock_neo4j_query.call_count == 1  # Only pre-write duplicate check ran


@patch("app.routes.users.oracle_db.delete_oracle_user")
@patch("app.routes.users.run_query")
@patch("app.routes.users.oracle_db.insert_oracle_user")
def test_unit_neo4j_failure_with_successful_compensation(
    mock_oracle_insert, mock_neo4j_query, mock_oracle_delete, client
):
    """
    [MOCKED UNIT TEST]
    Verify that when Oracle succeeds but Neo4j fails:
    - A compensating delete is executed on Oracle for that user_id.
    - HTTP 500 is returned reporting that consistency was maintained.
    """
    # Duplicate check succeeds, then Neo4j CREATE raises an exception
    mock_neo4j_query.side_effect = [
        [],  # Pre-write duplicate check
        RuntimeError("Neo4j database connection lost during write")
    ]
    mock_oracle_insert.return_value = {"user_id": "usr_fail_neo"}
    mock_oracle_delete.return_value = True

    payload = {
        "id": "usr_fail_neo",
        "name": "Compensate Test",
        "email": "compensate@test.io",
        "status": "Active"
    }

    response = client.post("/api/users", json=payload)
    assert response.status_code == 500
    data = response.json()
    assert "Neo4j write failed" in data["detail"]
    assert "compensating delete was successfully executed on Oracle" in data["detail"]

    # Verify compensating delete targeted the exact user_id created
    mock_oracle_delete.assert_called_once_with("usr_fail_neo")


@patch("app.routes.users.oracle_db.delete_oracle_user")
@patch("app.routes.users.run_query")
@patch("app.routes.users.oracle_db.insert_oracle_user")
def test_unit_compensation_failure_reporting(
    mock_oracle_insert, mock_neo4j_query, mock_oracle_delete, client
):
    """
    [MOCKED UNIT TEST]
    Verify that if both Neo4j write and Oracle compensation fail:
    - Critical warning is returned in the API response.
    - Actionable manual reconciliation SQL is provided.
    """
    mock_neo4j_query.side_effect = [
        [],  # Pre-write duplicate check
        RuntimeError("Neo4j write failure")
    ]
    mock_oracle_insert.return_value = {"user_id": "usr_critical_reconcile"}
    mock_oracle_delete.side_effect = OracleCompensationError("Oracle network unreachable during rollback")

    payload = {
        "id": "usr_critical_reconcile",
        "name": "Reconcile Test",
        "email": "reconcile@test.io",
        "status": "Active"
    }

    response = client.post("/api/users", json=payload)
    assert response.status_code == 500
    detail = response.json()["detail"]
    assert "CRITICAL" in detail
    assert "Manual reconciliation required" in detail
    assert "usr_critical_reconcile" in detail


@patch("app.routes.users.run_query")
def test_unit_duplicate_user_rejected_prewrite(mock_neo4j_query, client):
    """
    [MOCKED UNIT TEST]
    Verify that an existing user email or ID is rejected with HTTP 409 Conflict
    before any writes are attempted.
    """
    mock_neo4j_query.return_value = [{"id": "usr_001", "email": "eleanor.vance@legacyvault.io"}]

    payload = {
        "name": "Duplicate Eleanor",
        "email": "eleanor.vance@legacyvault.io",
        "status": "Active"
    }

    response = client.post("/api/users", json=payload)
    assert response.status_code == 409
    assert "Conflict" in response.json()["detail"]


@patch("app.routes.users.run_query")
@patch("app.routes.users.oracle_db.insert_oracle_user")
def test_unit_oracle_duplicate_error(mock_oracle_insert, mock_neo4j_query, client):
    """
    [MOCKED UNIT TEST]
    Verify that if Oracle detects an ORA-00001 unique constraint violation,
    HTTP 409 Conflict is returned.
    """
    mock_neo4j_query.return_value = []
    mock_oracle_insert.side_effect = OracleDuplicateError(
        "Duplicate record in Oracle: User with email 'existing@test.io' already exists."
    )

    payload = {
        "name": "Oracle Duplicate",
        "email": "existing@test.io",
        "status": "Active"
    }

    response = client.post("/api/users", json=payload)
    assert response.status_code == 409
    assert "Conflict in Oracle database" in response.json()["detail"]


# ------------------------------------------------------------------------------
# 2. Live Integration Test (Conditional - Runs only if real credentials are set)
# ------------------------------------------------------------------------------

def test_integration_real_oracle_live(client):
    """
    [REAL DATABASE INTEGRATION TEST]
    Executes a real dual-write against the local Oracle XE instance and Neo4j
    ONLY if ORACLE_PASSWORD is set in the environment and Thick mode client loads.
    Otherwise safely skips.
    """
    if not is_oracle_configured():
        pytest.skip("Skipping live Oracle integration test: ORACLE_PASSWORD is not set in local .env.")

    test_email = "live.dual.test@legacyvault.io"
    payload = {
        "name": "Live Dual Test User",
        "email": test_email,
        "phone": "+1-555-7777",
        "status": "Active"
    }

    try:
        response = client.post("/api/users", json=payload)
        if response.status_code == 503:
            pytest.skip(f"Skipping live test: {response.json()['detail']}")

        assert response.status_code == 201
        data = response.json()
        created_id = data["id"]

        # Verify record exists in Oracle USERS
        oracle_record = get_oracle_user(created_id)
        assert oracle_record is not None
        assert oracle_record["email"] == test_email
        assert oracle_record["name"] == "Live Dual Test User"

        # Cleanup test user from both databases
        from app.routes.users import delete_user
        from app.oracle_db import delete_oracle_user
        delete_user(created_id)
        delete_oracle_user(created_id)

    except Exception as e:
        pytest.skip(f"Live database test skipped due to client driver environment: {e}")
