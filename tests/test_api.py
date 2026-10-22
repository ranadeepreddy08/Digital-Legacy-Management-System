import pytest
from unittest.mock import patch
from pydantic import ValidationError
from app.models.user import UserCreate, UserUpdate
from app.models.asset import DigitalAssetCreate
from app.models.nominee import NomineeCreate
from app.models.executor import ExecutorCreate
from app.models.plan import LegacyPlanCreate
from app.models.release import ScheduledReleaseCreate
from app.config import BASE_DIR

# ------------------------------------------------------------------------------
# 1. API Health & Static Route Tests
# ------------------------------------------------------------------------------
def test_health_check_endpoint(client):
    """Verify that /api/health returns appropriate status structure."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert "connected" in data
    assert "uri" in data
    assert "database" in data
    assert "counts" in data
    assert isinstance(data["connected"], bool)

def test_home_serves_index_html(client):
    """Verify that GET / returns the frontend HTML."""
    response = client.get("/")
    assert response.status_code == 200
    assert "Digital Legacy Vault" in response.text
    assert "Legacy Vault" in response.text

# ------------------------------------------------------------------------------
# 2. Pydantic Model Validation Tests
# ------------------------------------------------------------------------------
def test_user_model_validation():
    """Test User model constraints and email validation."""
    valid_user = UserCreate(
        name="Eleanor Vance",
        email="eleanor@legacyvault.io",
        phone="+1-555-0101",
        status="Active"
    )
    assert valid_user.name == "Eleanor Vance"

    # Invalid email must raise ValidationError
    with pytest.raises(ValidationError):
        UserCreate(
            name="Invalid User",
            email="not-an-email",
            status="Active"
        )

def test_asset_model_validation():
    """Test DigitalAsset priority and type defaults."""
    asset = DigitalAssetCreate(
        title="Cold Bitcoin Wallet",
        asset_type="Cryptocurrency",
        access_info_encrypted_hint="Safe deposit box #402",
        priority="Critical"
    )
    assert asset.title == "Cold Bitcoin Wallet"
    assert asset.priority == "Critical"

def test_nominee_allocation_percentage_bounds():
    """Test Nominee allocation percentage bounds (1 to 100)."""
    nominee = NomineeCreate(
        name="Julian Vance",
        relationship="Spouse",
        email="julian@example.com",
        allocation_percentage=100
    )
    assert nominee.allocation_percentage == 100

    # Over 100% must fail
    with pytest.raises(ValidationError):
        NomineeCreate(
            name="Julian Vance",
            relationship="Spouse",
            email="julian@example.com",
            allocation_percentage=150
        )

    # Below 1% must fail
    with pytest.raises(ValidationError):
        NomineeCreate(
            name="Julian Vance",
            relationship="Spouse",
            email="julian@example.com",
            allocation_percentage=0
        )

def test_plan_and_release_model_validation():
    """Test LegacyPlan and ScheduledRelease models."""
    plan = LegacyPlanCreate(
        title="Crypto & IP Estate Plan",
        trigger_condition="Legal Death Certificate Verification",
        status="Active"
    )
    assert plan.status == "Active"

    release = ScheduledReleaseCreate(
        release_date="2026-12-01T00:00:00Z",
        status="Scheduled",
        notification_method="Encrypted Email"
    )
    assert release.status == "Scheduled"

# ------------------------------------------------------------------------------
# 3. Cypher Files Verification
# ------------------------------------------------------------------------------
def test_cypher_files_exist_and_non_empty():
    """Verify that all required Cypher scripts exist with executable statements."""
    schema_file = BASE_DIR / "cypher" / "schema.cypher"
    seed_file = BASE_DIR / "cypher" / "seed.cypher"
    queries_file = BASE_DIR / "cypher" / "queries.cypher"

    assert schema_file.exists(), "cypher/schema.cypher must exist"
    assert seed_file.exists(), "cypher/seed.cypher must exist"
    assert queries_file.exists(), "cypher/queries.cypher must exist"

    schema_content = schema_file.read_text(encoding="utf-8")
    assert "CREATE CONSTRAINT" in schema_content
    assert "CREATE INDEX" in schema_content

    seed_content = seed_file.read_text(encoding="utf-8")
    assert "MERGE" in seed_content
    assert "HAS_ASSET" in seed_content
    assert "DESIGNATED_FOR" in seed_content

    queries_content = queries_file.read_text(encoding="utf-8")
    assert "MATCH (u:User)" in queries_content

# ------------------------------------------------------------------------------
# 4. Mocked Route Operations Tests
# ------------------------------------------------------------------------------
@patch("app.routes.users.run_query")
def test_list_users_mocked(mock_run_query, client):
    """Test listing users returns correctly formatted JSON."""
    mock_run_query.return_value = [
        {
            "id": "usr_001",
            "name": "Eleanor Vance",
            "email": "eleanor@legacyvault.io",
            "phone": "+1-555-0101",
            "status": "Active",
            "created_at": "2026-01-15T09:30:00Z",
            "asset_count": 2,
            "nominee_count": 2,
            "plan_count": 1
        }
    ]
    response = client.get("/api/users")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Eleanor Vance"
    assert data[0]["asset_count"] == 2

@patch("app.routes.assets.run_query")
def test_list_assets_mocked(mock_run_query, client):
    """Test listing digital assets returns owner and priority badges."""
    mock_run_query.return_value = [
        {
            "id": "ast_001",
            "title": "Cold Storage Bitcoin Wallet",
            "asset_type": "Cryptocurrency",
            "access_info_encrypted_hint": "Ledger in safe box",
            "priority": "Critical",
            "estimated_value": "$125,000 USD",
            "created_at": "2026-01-16T10:00:00Z",
            "owner_id": "usr_001",
            "owner_name": "Eleanor Vance",
            "designated_nominee_id": "nom_001",
            "designated_nominee_name": "Julian Vance",
            "nominee_share_pct": 100,
            "managing_executor_id": "exe_001",
            "managing_executor_name": "Robert Sterling, Esq.",
            "plan_title": "Comprehensive Succession Plan"
        }
    ]
    response = client.get("/api/assets")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Cold Storage Bitcoin Wallet"
    assert data[0]["priority"] == "Critical"

@patch("app.routes.graph.run_query")
def test_graph_topology_mocked(mock_run_query, client):
    """Test graph topology endpoint converts Cypher results into Vis.js format."""
    mock_run_query.return_value = [
        {
            "nodes": [
                {"id": "usr_001", "label": "User", "name": "Eleanor Vance", "properties": {"name": "Eleanor Vance"}},
                {"id": "ast_001", "label": "DigitalAsset", "name": "Cold Wallet", "properties": {"title": "Cold Wallet"}}
            ],
            "edges": [
                {"id": 1, "from": "usr_001", "to": "ast_001", "label": "HAS_ASSET", "properties": {}}
            ]
        }
    ]
    response = client.get("/api/graph/topology")
    assert response.status_code == 200
    data = response.json()
    assert "nodes" in data
    assert "edges" in data
    assert len(data["nodes"]) == 2
    assert len(data["edges"]) == 1
    assert data["nodes"][0]["group"] == "User"
    assert data["edges"][0]["label"] == "HAS_ASSET"
