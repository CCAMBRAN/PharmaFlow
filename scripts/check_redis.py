import os
import sys
import traceback
import redis
from dotenv import load_dotenv
load_dotenv()

def main():
    host = os.getenv('REDIS_HOST', 'localhost')
    port = int(os.getenv('REDIS_PORT', 6379))
    password = os.getenv('REDIS_PASSWORD', None)
    db = int(os.getenv('REDIS_DB', 0))
    try:
        r = redis.Redis(host=host, port=port, password=password, db=db,
                        socket_connect_timeout=float(os.getenv('REDIS_SOCKET_CONNECT_TIMEOUT', 3)),
                        socket_timeout=float(os.getenv('REDIS_SOCKET_TIMEOUT', 3)))
        r.ping()
        print(f'✅ Conexión Redis OK — host: {host}, port: {port}, db: {db}')
        # Prueba de escritura/lectura
        r.set('test_key', 'redis_ok')
        val = r.get('test_key')
        print(f'Valor de test_key: {val.decode() if val else None}')
        r.delete('test_key')
        return 0
    except Exception:
        print('❌ Error conectando a Redis:')
        traceback.print_exc()
        return 3

if __name__ == '__main__':
    sys.exit(main())
