from datetime import datetime


class DocumentModels:


	@staticmethod
	def ensure_indexes(db):
		"""Create commonly used indexes for collections."""
		# Ensure clinical reports collection exists and add indexes
		coll = db.get_collection('ensayos_clinicos')
		# index on estudio.codigo_ensayo for fast lookup
		coll.create_index([('estudio.codigo_ensayo', 1)], unique=False)
		# index on medicamento studied for searches
		coll.create_index([('estudio.medicamento_estudiado', 'text')], default_language='spanish')
		# index on metadata.fecha_creacion
		coll.create_index([('metadata.fecha_creacion', -1)])

	@staticmethod
	def insert_clinical_report(db, documento):
		"""Insert a clinical report document, attaching creation metadata."""
		coll = db.get_collection('ensayos_clinicos')
		documento.setdefault('metadata', {})
		documento['metadata'].setdefault('fecha_creacion', datetime.utcnow())
		result = coll.insert_one(documento)
		return result.inserted_id

	@staticmethod
	def find_reports_by_medicine(db, medicine_name, limit=50):
		coll = db.get_collection('ensayos_clinicos')
		query = {"estudio.medicamento_estudiado": {"$regex": medicine_name, "$options": "i"}}
		return list(coll.find(query).limit(limit))

