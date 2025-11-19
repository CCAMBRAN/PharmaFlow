import json
from datetime import timedelta

class KeyValueService:
    def __init__(self, db_connector):
        self.db_connector = db_connector
        self.redis_client = self.db_connector.connect_redis()
    
    def almacenar_token_sesion(self, usuario_id, token_data, expiracion_horas=24):
        if not self.redis_client:
            return False, "Conexión a Redis no disponible"
        
        try:
            key = f"session:{usuario_id}"
            self.redis_client.setex(
                key, 
                timedelta(hours=expiracion_horas), 
                json.dumps(token_data)
            )
            return True, "Token almacenado"
        except Exception as e:
            return False, f"Error almacenando token: {e}"
    
    def obtener_token_sesion(self, usuario_id):
        if not self.redis_client:
            return None
        
        try:
            key = f"session:{usuario_id}"
            token_data = self.redis_client.get(key)
            return json.loads(token_data) if token_data else None
        except Exception as e:
            print(f"Error obteniendo token: {e}")
            return None
    
    def eliminar_token_sesion(self, usuario_id):
        if not self.redis_client:
            return False
        
        try:
            key = f"session:{usuario_id}"
            self.redis_client.delete(key)
            return True
        except Exception as e:
            print(f"Error eliminando token: {e}")
            return False
    
    def almacenar_precio_dolar(self, precio):
        if not self.redis_client:
            return False
        
        try:
            key = "precio:dolar:actual"
            self.redis_client.setex(key, timedelta(hours=1), str(precio))
            return True
        except Exception as e:
            print(f"Error almacenando precio dólar: {e}")
            return False
    
    def obtener_precio_dolar(self):
        if not self.redis_client:
            return None
        
        try:
            key = "precio:dolar:actual"
            precio = self.redis_client.get(key)
            return float(precio) if precio else None
        except Exception as e:
            print(f"Error obteniendo precio dólar: {e}")
            return None
    
    def almacenar_cache_consulta(self, clave, datos, expiracion_minutos=30):
        if not self.redis_client:
            return False
        
        try:
            self.redis_client.setex(
                clave, 
                timedelta(minutes=expiracion_minutos), 
                json.dumps(datos)
            )
            return True
        except Exception as e:
            print(f"Error almacenando cache: {e}")
            return False
    
    def obtener_cache_consulta(self, clave):
        if not self.redis_client:
            return None
        
        try:
            datos = self.redis_client.get(clave)
            return json.loads(datos) if datos else None
        except Exception as e:
            print(f"Error obteniendo cache: {e}")
            return None