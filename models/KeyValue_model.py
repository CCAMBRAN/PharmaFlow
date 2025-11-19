import json
from datetime import timedelta


class KeyValueModel:


	def __init__(self, redis_client):
		self.redis = redis_client

	def store_session_token(self, usuario_id, token_data, hours=24):
		key = f"session:{usuario_id}"
		self.redis.setex(key, timedelta(hours=hours), json.dumps(token_data))

	def get_session_token(self, usuario_id):
		key = f"session:{usuario_id}"
		data = self.redis.get(key)
		return json.loads(data) if data else None

	def store_price_dollar(self, precio, hours=1):
		key = "precio:dolar:actual"
		self.redis.setex(key, timedelta(hours=hours), str(precio))

	def get_price_dollar(self):
		key = "precio:dolar:actual"
		val = self.redis.get(key)
		return float(val) if val else None

	def cache_query(self, key, data, minutes=30):
		self.redis.setex(key, timedelta(minutes=minutes), json.dumps(data))

	def get_cached_query(self, key):
		val = self.redis.get(key)
		return json.loads(val) if val else None

