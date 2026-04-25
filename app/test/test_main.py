import pytest
from unittest.mock import patch
from httpx import AsyncClient, ASGITransport

from app.main import app, lifespan

@pytest.mark.asyncio
async def test_health():
    """
    Prueba el endpoint de health
    """
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok", "service": "ms-ANALYTICS"}

@pytest.mark.asyncio
async def test_lifespan_success():
    """
    Prueba el ciclo de vida de la app de forma exitosa (creación de tablas y conexión a DB correctos)
    """
    with patch("app.main.Base.metadata.create_all") as mock_create_all, \
         patch("app.main.check_db_connection", return_value=True) as mock_check_db_connection:
        
        async with lifespan(app):
            pass
            
        mock_create_all.assert_called_once()
        mock_check_db_connection.assert_called_once()

@pytest.mark.asyncio
async def test_lifespan_failure_handling():
    """
    Prueba el manejo de errores durante el ciclo de vida de la app
    """
    with patch("app.main.Base.metadata.create_all", side_effect=Exception("Mocked DB error")) as mock_create_all, \
         patch("app.main.check_db_connection", return_value=False) as mock_check_db_connection:
        
        async with lifespan(app):
            pass
            
        mock_create_all.assert_called_once()
        mock_check_db_connection.assert_called_once()
