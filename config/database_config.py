import os 
from dotenv import load_dotenv
load_dotenv()

class DatabaseConfig:
    #Relational MySQL (Tablas)
    MYSQL_CONFIG = {
        'host': os.getenv('MYSQL_HOST', 'localhost'),
        'user': os.getenv('MYSQL_USER', 'root'),
        'password': os.getenv('MYSQL_PASSWORD', 'black0204'),
        'database': os.getenv('MYSQL_DATABASE', 'pharmaflow'),
        'port': int(os.getenv('MYSQL_PORT', 3306)),
        # Connection timeout in seconds for quick failures when service is down
        'connection_timeout': int(os.getenv('MYSQL_CONNECTION_TIMEOUT', 5))
    }

    #Document-based  MongoDB (Documentos)
    MONGODB_CONFIG = {
        'host': os.getenv('MONGODB_HOST', 'localhost'),
        'port': int(os.getenv('MONGODB_PORT', 27017)),
        # Optional user/password or full URI
        'user': os.getenv('MONGODB_USER', ''),
        'password': os.getenv('MONGODB_PASSWORD', ''),
        # Prefer a full URI if provided; otherwise build one from host/port
        'uri': os.getenv('MONGODB_URI', None),
        'database': os.getenv('MONGODB_DATABASE', 'pharmaflow'),
        # Server selection timeout in milliseconds (pymongo expects ms)
        'serverSelectionTimeoutMS': int(os.getenv('MONGODB_SERVER_SELECTION_TIMEOUT_MS', 3000))
    }

    #Key-Value Redis (Clave-Valor)  

    REDIS_CONFIG = {
        'host': os.getenv('REDIS_HOST', 'localhost'),
        'port': int(os.getenv('REDIS_PORT', 6379)),
        'password': os.getenv('REDIS_PASSWORD', ''),
        'db': int(os.getenv('REDIS_DB', 0))
    }

    # Provide short socket timeouts for Redis to fail fast when not available
    REDIS_SOCKET_CONFIG = {
        'socket_connect_timeout': float(os.getenv('REDIS_SOCKET_CONNECT_TIMEOUT', 3)),
        'socket_timeout': float(os.getenv('REDIS_SOCKET_TIMEOUT', 3))
    }

    #Graph-based Neo4j (Grafos)
    NEO4J_CONFIG = {
        'uri': os.getenv('NEO4J_URI', 'bolt://localhost:7687'),
        'user': os.getenv('NEO4J_USER', 'neo4j'),
        'password': os.getenv('NEO4J_PASSWORD', 'password'),
        'database': os.getenv('NEO4J_DATABASE', 'neo4j')
    }

    # Neo4j driver connection timeout (seconds)
    NEO4J_CONNECTION_OPTIONS = {
        'connection_timeout': int(os.getenv('NEO4J_CONNECTION_TIMEOUT', 3))
    }