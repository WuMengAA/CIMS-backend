import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock, AsyncMock

from cims.ManagementServer.api import api, get_tenant_id

# Mock the get_tenant_id dependency
async def override_get_tenant_id():
    return 1

api.dependency_overrides[get_tenant_id] = override_get_tenant_id

client = TestClient(api)

def test_manifest_endpoint():
    with patch("cims.ManagementServer.api.Datas", new_callable=MagicMock) as mock_datas:
        mock_datas.ProfileConfig.get_profile_config.return_value = {
            "ClassPlan": "default",
            "TimeLayout": "default",
            "Subjects": "default",
            "Settings": "default",
            "Policy": "default",
        }

        response = client.get("/api/v1/client/test_client/manifest")

        assert response.status_code == 200
        data = response.json()
        assert data["ServerKind"] == 1
        assert "ClassPlanSource" in data

def test_policy_endpoint_valid():
    with patch("cims.ManagementServer.api.Datas", new_callable=MagicMock) as mock_datas:
        mock_datas.ClassPlan.read.return_value = {"test": "data"}

        response = client.get("/api/v1/client/ClassPlan?name=default")

        assert response.status_code == 200
        assert response.json() == {"test": "data"}

def test_policy_endpoint_invalid():
    response = client.get("/api/v1/client/InvalidResourceType?name=default")

    assert response.status_code == 404

def test_refresh_endpoint():
    with patch("cims.ManagementServer.api.Settings", new_callable=MagicMock) as mock_settings:
        mock_settings.refresh = AsyncMock()

        response = client.get("/api/refresh")

        assert response.status_code == 200
