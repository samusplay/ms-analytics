import pytest
from unittest.mock import patch, MagicMock

from app.infrastructure.database import check_db_connection, get_db

def test_check_db_connection_success():
    with patch("app.infrastructure.database.engine.connect") as mock_connect:
        # Mocking the connection context manager
        mock_connection = MagicMock()
        mock_connect.return_value.__enter__.return_value = mock_connection
        
        result = check_db_connection()
        
        assert result is True
        mock_connection.execute.assert_called_once()

def test_check_db_connection_failure():
    with patch("app.infrastructure.database.engine.connect", side_effect=Exception("Connection Error")):
        result = check_db_connection()
        
        assert result is False

def test_get_db():
    with patch("app.infrastructure.database.SessionLocal") as mock_session_local:
        mock_session = MagicMock()
        mock_session_local.return_value = mock_session
        
        # Otenemos el generador
        db_generator = get_db()
        
        # Consumimos el primer valor del generador (el yield)
        db = next(db_generator)
        
        assert db == mock_session
        mock_session.close.assert_not_called()
        
        # Consumimos el generador hasta que termine para que pase por el "finally"
        try:
            next(db_generator)
        except StopIteration:
            pass
            
        mock_session.close.assert_called_once()
