"""
Dependencias compartidas para la API
"""
from utils.database_connector import DatabaseConnector

# Crear una instancia global del conector
_db_connector = None

def get_db_connector():
    """
    Obtener instancia del conector de base de datos
    Singleton pattern para reutilizar conexiones
    """
    global _db_connector
    if _db_connector is None:
        _db_connector = DatabaseConnector()
    return _db_connector
