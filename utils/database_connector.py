import mysql.connector
from mysql.connector import Error
import pymongo
import redis
from neo4j import GraphDatabase
from config.database_config import DatabaseConfig
from config.security_config import SecurityConfig

class DatabaseConnector:
    def __init__(self):
        self.mysql_conn = None
        self.mongo_client = None
        self.redis_client = None
        self.neo4j_driver = None
    
    # Conexión MySQL (Relacional)
    def connect_mysql(self):
        try:
            # mysql.connector accepts 'connection_timeout' key
            cfg = DatabaseConfig.MYSQL_CONFIG.copy()
            # Fill credentials from SecurityConfig if not present in DatabaseConfig
            if not cfg.get('user') and SecurityConfig.MYSQL_USER:
                cfg['user'] = SecurityConfig.MYSQL_USER
            if not cfg.get('password') and SecurityConfig.MYSQL_PASSWORD:
                cfg['password'] = SecurityConfig.MYSQL_PASSWORD

            # Merge SSL options when configured
            ssl_opts = SecurityConfig.mysql_ssl_options() or {}
            connect_kwargs = {**cfg, **ssl_opts}

            self.mysql_conn = mysql.connector.connect(**connect_kwargs)
            print("✅ Conexión MySQL establecida")
            return self.mysql_conn
        except Exception as e:
            print(f"❌ Error conectando a MySQL: {e}. Check MYSQL_HOST/PORT and that the server is running.")
            return None
    
    # Conexión MongoDB (Documentos)
    def connect_mongodb(self):
        try:
            # Support either a full URI or host/port credentials
            mongo_cfg = DatabaseConfig.MONGODB_CONFIG
            uri = mongo_cfg.get('uri')
            if not uri:
                host = mongo_cfg.get('host', 'localhost')
                port = mongo_cfg.get('port', 27017)
                user = mongo_cfg.get('user')
                password = mongo_cfg.get('password')
                if user and password:
                    uri = f"mongodb://{user}:{password}@{host}:{port}"
                else:
                    uri = f"mongodb://{host}:{port}"

            # Use serverSelectionTimeoutMS to fail fast if the server is not reachable
            server_selection_ms = mongo_cfg.get('serverSelectionTimeoutMS', 3000)
            # Merge TLS kwargs from security config
            tls_kwargs = SecurityConfig.pymongo_tls_kwargs() or {}
            self.mongo_client = pymongo.MongoClient(uri, serverSelectionTimeoutMS=server_selection_ms, **tls_kwargs)
            db_name = mongo_cfg.get('database', 'pharmaflow')
            db = self.mongo_client[db_name]
            # Trigger server selection to catch connection problems early
            self.mongo_client.admin.command('ping')
            print("✅ Conexión MongoDB establecida")
            return db
        except Exception as e:
            print(f"❌ Error conectando a MongoDB: {e}. Check MONGODB_URI/host/port and credentials.")
            return None
    
    # Conexión Redis (Clave-Valor)
    def connect_redis(self):
        try:
            # Merge socket timeouts into redis config for faster failures
            cfg = DatabaseConfig.REDIS_CONFIG.copy()
            # If there is a separate socket config, merge it
            socket_cfg = getattr(DatabaseConfig, 'REDIS_SOCKET_CONFIG', {})
            cfg.update(socket_cfg)

            # Merge security-driven redis options (ssl, password) - SecurityConfig takes precedence
            sec_redis = SecurityConfig.redis_kwargs() or {}
            cfg.update(sec_redis)

            self.redis_client = redis.Redis(**cfg)
            # Test connection (may raise a ConnectionError)
            self.redis_client.ping()
            print("✅ Conexión Redis establecida")
            return self.redis_client
        except Exception as e:
            print(f"❌ Error conectando a Redis: {e}. Check REDIS_HOST/PORT and that Redis is running.")
            return None
    
    # Conexión Neo4j (Grafos)
    def connect_neo4j(self):
        try:
            neo_cfg = DatabaseConfig.NEO4J_CONFIG
            # Prefer credentials from DatabaseConfig, but allow SecurityConfig to provide driver options
            user = neo_cfg.get('user') or SecurityConfig.NEO4J_USER
            password = neo_cfg.get('password') or SecurityConfig.NEO4J_PASSWORD

            # auth tuple
            auth = (user, password)

            # driver options: combine DatabaseConfig options and SecurityConfig options
            opts = {}
            try:
                opts.update(DatabaseConfig.NEO4J_CONNECTION_OPTIONS)
            except Exception:
                pass
            try:
                _, sec_opts = SecurityConfig.neo4j_auth_config()
                opts.update(sec_opts or {})
            except Exception:
                pass

            self.neo4j_driver = GraphDatabase.driver(
                neo_cfg['uri'],
                auth=auth,
                **opts
            )
            # Test connection by running a lightweight query
            with self.neo4j_driver.session() as session:
                session.run("RETURN 1")
            print("✅ Conexión Neo4j establecida")
            return self.neo4j_driver
        except Exception as e:
            print(f"❌ Error conectando a Neo4j: {e}. Check NEO4J_URI and that the server is reachable.")
            return None
    
    def close_all_connections(self):
        if self.mysql_conn and self.mysql_conn.is_connected():
            self.mysql_conn.close()
            print("🔌 Conexión MySQL cerrada")
        
        if self.mongo_client:
            self.mongo_client.close()
            print("🔌 Conexión MongoDB cerrada")
        
        if self.redis_client:
            self.redis_client.close()
            print("🔌 Conexión Redis cerrada")
        
        if self.neo4j_driver:
            self.neo4j_driver.close()
            print("🔌 Conexión Neo4j cerrada")