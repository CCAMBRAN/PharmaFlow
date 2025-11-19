import os
from dotenv import load_dotenv

load_dotenv()


class SecurityConfig:


    # -- General password policy (application-level, optional) --
    PASSWORD_MIN_LENGTH = int(os.getenv('SEC_PASSWORD_MIN_LENGTH', 12))
    PASSWORD_REQUIRE_UPPER = os.getenv('SEC_PASSWORD_REQUIRE_UPPER', '1') == '1'
    PASSWORD_REQUIRE_DIGIT = os.getenv('SEC_PASSWORD_REQUIRE_DIGIT', '1') == '1'

    # -- MySQL (Relational) credentials and TLS --
    MYSQL_USER = os.getenv('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', '')
    MYSQL_USE_SSL = os.getenv('MYSQL_USE_SSL', '0') == '1'
    MYSQL_SSL_CA = os.getenv('MYSQL_SSL_CA')  # path to CA cert
    MYSQL_SSL_CERT = os.getenv('MYSQL_SSL_CERT')  # client cert (optional)
    MYSQL_SSL_KEY = os.getenv('MYSQL_SSL_KEY')  # client key (optional)

    # -- MongoDB (Document) credentials and TLS --
    MONGODB_USER = os.getenv('MONGODB_USER', '')
    MONGODB_PASSWORD = os.getenv('MONGODB_PASSWORD', '')
    MONGODB_USE_TLS = os.getenv('MONGODB_USE_TLS', '1') == '1'
    MONGODB_TLS_CA_FILE = os.getenv('MONGODB_TLS_CA_FILE')
    MONGODB_TLS_ALLOW_INVALID = os.getenv('MONGODB_TLS_ALLOW_INVALID', '0') == '1'

    # -- Redis (Key-Value) credentials and TLS --
    REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', '')
    REDIS_USE_TLS = os.getenv('REDIS_USE_TLS', '0') == '1'

    # -- Neo4j (Graph) credentials and TLS/trust strategy --
    NEO4J_USER = os.getenv('NEO4J_USER', 'neo4j')
    NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD', '')
    NEO4J_ENCRYPTED = os.getenv('NEO4J_ENCRYPTED', '1') == '1'
    NEO4J_TRUST = os.getenv('NEO4J_TRUST', 'TRUST_SYSTEM')

    # -- Role-based (application) defaults -- keep synced with DB roles
    ROLES = {
        'gerente': {
            'can_manage_inventory': True,
            'can_manage_users': True,
            'can_register_sales': True,
        },
        'farmaceutico': {
            'can_manage_inventory': True,
            'can_register_sales': True,
            'can_manage_users': False,
        },
        'investigador': {
            'can_manage_inventory': False,
            'can_register_sales': False,
            'can_manage_users': False,
            'can_view_documents': True,
        }
    }

    @classmethod
    def mysql_ssl_options(cls):

        if not cls.MYSQL_USE_SSL:
            return {}
        opts = {}
        if cls.MYSQL_SSL_CA:
            opts['ssl_ca'] = cls.MYSQL_SSL_CA
        if cls.MYSQL_SSL_CERT:
            opts['ssl_cert'] = cls.MYSQL_SSL_CERT
        if cls.MYSQL_SSL_KEY:
            opts['ssl_key'] = cls.MYSQL_SSL_KEY
        return opts

    @classmethod
    def pymongo_tls_kwargs(cls):
        """Return kwargs for pymongo.MongoClient when using TLS."""
        if not cls.MONGODB_USE_TLS:
            return {}
        kwargs = {'tls': True}
        if cls.MONGODB_TLS_CA_FILE:
            kwargs['tlsCAFile'] = cls.MONGODB_TLS_CA_FILE
        if cls.MONGODB_TLS_ALLOW_INVALID:
            kwargs['tlsAllowInvalidCertificates'] = True
        return kwargs

    @classmethod
    def redis_kwargs(cls):
        """Return kwargs for redis.Redis.

        Use `ssl=True` when REDIS_USE_TLS is enabled and set `password` if provided.
        """
        k = {}
        if cls.REDIS_USE_TLS:
            k['ssl'] = True
        if cls.REDIS_PASSWORD:
            k['password'] = cls.REDIS_PASSWORD
        return k

    @classmethod
    def neo4j_auth_config(cls):
        """Return auth tuple and driver options for neo4j.GraphDatabase.driver"""
        auth = (cls.NEO4J_USER, cls.NEO4J_PASSWORD)
        driver_opts = {}
        # neo4j Python driver accepts 'encrypted' and 'trust' in some versions; keep minimal
        driver_opts['encrypted'] = cls.NEO4J_ENCRYPTED
        driver_opts['trust'] = cls.NEO4J_TRUST
        return auth, driver_opts


def _example_env_vars():
    return {
        'MYSQL_USE_SSL': '0  # 1 to enable, ensure MYSQL_SSL_CA is set',
        'MONGODB_USE_TLS': '1  # enable TLS for MongoDB',
        'MONGODB_TLS_CA_FILE': '/path/to/ca.pem',
        'REDIS_USE_TLS': '0',
        'NEO4J_ENCRYPTED': '1',
    }
