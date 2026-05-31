import os
import sys
import pytest
from unittest.mock import MagicMock, AsyncMock, patch

# Añadir el directorio raíz de este microservicio al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from fastapi.testclient import TestClient
from app.main import app
from app.routers.sync_router import get_db

def override_get_db():
    return MagicMock()

@pytest.fixture(autouse=True)
def setup_overrides():
    app.dependency_overrides[get_db] = override_get_db
    yield
    app.dependency_overrides.pop(get_db, None)

def test_analytics_health():
    client = TestClient(app)
    response = client.get("/api/v1/analytics/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["service"] == "ms-ANALYTICS"

def test_sync_data_success():
    client = TestClient(app)
    
    # Payload que cumple con SyncPayloadSchema -> TransformedRecordSchema
    payload = {
        "data": [
            {
                "zone_code": "001",
                "zone_name": "UPZ Test",
                "region": "Bogota",
                "metrics": {
                    "score_poblacion": 0.8,
                    "score_ingresos": 0.7,
                    "score_competencia": 0.6,
                    "score_final": 0.7
                }
            }
        ]
    }
    
    with patch("app.routers.sync_router.PostgresAnalyticsRepository") as mock_repo_class, \
         patch("app.routers.sync_router.SyncAnalyticsDataService") as mock_service_class:
        
        mock_service = MagicMock()
        mock_service.execute = AsyncMock(return_value={"records_synced": 1})
        mock_service_class.return_value = mock_service
        
        response = client.post("/api/v1/analytics/internal/sync/dataset_123", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["records_synced"] == 1
        mock_service.execute.assert_called_once()

def test_sync_data_value_error():
    client = TestClient(app)
    payload = {"data": []} # Payload vacío
    
    with patch("app.routers.sync_router.PostgresAnalyticsRepository") as mock_repo_class, \
         patch("app.routers.sync_router.SyncAnalyticsDataService") as mock_service_class:
        
        mock_service = MagicMock()
        mock_service.execute = AsyncMock(side_effect=ValueError("No hay registros que sincronizar"))
        mock_service_class.return_value = mock_service
        
        response = client.post("/api/v1/analytics/internal/sync/dataset_123", json=payload)
        
        assert response.status_code == 400
        assert "No hay registros que sincronizar" in response.json()["detail"]
