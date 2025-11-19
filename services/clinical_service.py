from datetime import datetime
from bson import ObjectId
from pymongo import ASCENDING, DESCENDING

class ClinicalService:
    def __init__(self, db_connector):
        self.db_connector = db_connector
        self.mongo_db = self.db_connector.connect_mongodb()
        self.collection = self.mongo_db['ensayos_clinicos'] if self.mongo_db is not None else None
    
    def almacenar_reporte_ensayo(self, reporte_data):
        if self.collection is None:
            return False, "Conexión a MongoDB no disponible"
        
        try:
            # Estructura flexible para documentos
            documento = {
                "metadata": {
                    "fecha_creacion": datetime.now(),
                    "version": reporte_data.get('version', '1.0'),
                    "estado": reporte_data.get('estado', 'borrador')
                },
                "estudio": {
                    "titulo": reporte_data.get('titulo'),
                    "fase": reporte_data.get('fase'),
                    "codigo_ensayo": reporte_data.get('codigo_ensayo'),
                    "fecha_inicio": reporte_data.get('fecha_inicio'),
                    "fecha_fin": reporte_data.get('fecha_fin'),
                    "medicamento_estudiado": reporte_data.get('medicamento_estudiado'),
                    "principio_activo": reporte_data.get('principio_activo')
                },
                "participantes": reporte_data.get('participantes', {}),
                "resultados": reporte_data.get('resultados', {}),
                "efectos_secundarios": reporte_data.get('efectos_secundarios', []),
                "conclusiones": reporte_data.get('conclusiones', {}),
                "datos_adicionales": reporte_data.get('datos_adicionales', {})  # Campo flexible
            }
            
            result = self.collection.insert_one(documento)
            return True, f"Reporte almacenado con ID: {result.inserted_id}"
            
        except Exception as e:
            return False, f"Error almacenando reporte: {e}"
    
    def buscar_ensayos_por_medicamento(self, medicamento):
        if self.collection is None:
            return []
        
        try:
            query = {"estudio.medicamento_estudiado": {"$regex": medicamento, "$options": "i"}}
            resultados = self.collection.find(query)
            return list(resultados)
        except Exception as e:
            print(f"Error buscando ensayos: {e}")
            return []
    
    def buscar_ensayos_por_efecto(self, efecto_secundario):
        if self.collection is None:
            return []
        
        try:
            query = {"efectos_secundarios": {"$elemMatch": {"$regex": efecto_secundario, "$options": "i"}}}
            resultados = self.collection.find(query)
            return list(resultados)
        except Exception as e:
            print(f"Error buscando por efecto: {e}")
            return []
    
    # ============= OPERACIONES CRUD COMPLETAS =============
    
    def crear_ensayo(self, datos_ensayo):
        """
        Crear un nuevo ensayo clínico con validación.
        """
        if self.collection is None:
            return False, "Conexión a MongoDB no disponible"
        
        try:
            # Validar campos requeridos
            campos_requeridos = ['codigo_ensayo', 'titulo', 'medicamento', 'fase']
            for campo in campos_requeridos:
                if campo not in datos_ensayo:
                    return False, f"Campo requerido faltante: {campo}"
            
            # Verificar que no exista el código de ensayo
            if self.collection.find_one({"codigo_ensayo": datos_ensayo['codigo_ensayo']}):
                return False, f"Ya existe un ensayo con código: {datos_ensayo['codigo_ensayo']}"
            
            # Estructura del documento
            documento = {
                "codigo_ensayo": datos_ensayo['codigo_ensayo'],
                "titulo": datos_ensayo['titulo'],
                "medicamento": datos_ensayo['medicamento'],
                "fase": datos_ensayo['fase'],
                "estado": datos_ensayo.get('estado', 'planificado'),
                "investigador_principal": datos_ensayo.get('investigador_principal', ''),
                "fecha_inicio": datos_ensayo.get('fecha_inicio'),
                "fecha_fin_estimada": datos_ensayo.get('fecha_fin_estimada'),
                "participantes": {
                    "objetivo": datos_ensayo.get('participantes_objetivo', 0),
                    "reclutados": datos_ensayo.get('participantes_reclutados', 0),
                    "completados": 0
                },
                "observaciones": [],
                "resultados": {},
                "metadata": {
                    "fecha_creacion": datetime.now(),
                    "fecha_modificacion": datetime.now(),
                    "creado_por": datos_ensayo.get('creado_por', 'sistema'),
                    "version": 1
                }
            }
            
            result = self.collection.insert_one(documento)
            return True, f"Ensayo creado con ID: {result.inserted_id}"
            
        except Exception as e:
            return False, f"Error creando ensayo: {e}"
    
    def obtener_ensayo(self, codigo_ensayo=None, ensayo_id=None):
        """
        Obtener un ensayo por código o por ID de MongoDB.
        """
        if self.collection is None:
            return None
        
        try:
            if codigo_ensayo:
                return self.collection.find_one({"codigo_ensayo": codigo_ensayo})
            elif ensayo_id:
                return self.collection.find_one({"_id": ObjectId(ensayo_id)})
            else:
                return None
        except Exception as e:
            print(f"Error obteniendo ensayo: {e}")
            return None
    
    def actualizar_ensayo(self, codigo_ensayo, actualizaciones):
        """
        Actualizar un ensayo existente.
        Permite actualizaciones parciales.
        """
        if self.collection is None:
            return False, "Conexión a MongoDB no disponible"
        
        try:
            # Verificar que el ensayo existe
            ensayo = self.collection.find_one({"codigo_ensayo": codigo_ensayo})
            if not ensayo:
                return False, f"No se encontró ensayo con código: {codigo_ensayo}"
            
            # Preparar actualización
            update_doc = {}
            
            # Campos simples que se pueden actualizar
            campos_actualizables = ['titulo', 'estado', 'investigador_principal', 
                                   'fecha_fin_estimada', 'medicamento', 'fase']
            
            for campo in campos_actualizables:
                if campo in actualizaciones:
                    update_doc[campo] = actualizaciones[campo]
            
            # Actualizar metadata
            update_doc['metadata.fecha_modificacion'] = datetime.now()
            update_doc['metadata.version'] = ensayo['metadata'].get('version', 1) + 1
            
            # Ejecutar actualización
            result = self.collection.update_one(
                {"codigo_ensayo": codigo_ensayo},
                {"$set": update_doc}
            )
            
            if result.modified_count > 0:
                return True, f"Ensayo actualizado: {result.modified_count} campo(s) modificado(s)"
            else:
                return True, "No hubo cambios en el ensayo"
                
        except Exception as e:
            return False, f"Error actualizando ensayo: {e}"
    
    def eliminar_ensayo(self, codigo_ensayo, hard_delete=False):
        """
        Eliminar un ensayo. Por defecto hace soft delete (marca como inactivo).
        """
        if self.collection is None:
            return False, "Conexión a MongoDB no disponible"
        
        try:
            if hard_delete:
                # Eliminación física
                result = self.collection.delete_one({"codigo_ensayo": codigo_ensayo})
                if result.deleted_count > 0:
                    return True, f"Ensayo eliminado permanentemente"
                else:
                    return False, "Ensayo no encontrado"
            else:
                # Soft delete - marcar como inactivo
                result = self.collection.update_one(
                    {"codigo_ensayo": codigo_ensayo},
                    {
                        "$set": {
                            "estado": "cancelado",
                            "metadata.fecha_eliminacion": datetime.now()
                        }
                    }
                )
                if result.modified_count > 0:
                    return True, "Ensayo marcado como cancelado"
                else:
                    return False, "Ensayo no encontrado"
                    
        except Exception as e:
            return False, f"Error eliminando ensayo: {e}"
    
    # ============= OPERACIONES AVANZADAS =============
    
    def agregar_observacion(self, codigo_ensayo, observacion):
        """
        Agregar una observación al array de observaciones del ensayo.
        """
        if self.collection is None:
            return False, "Conexión a MongoDB no disponible"
        
        try:
            nueva_observacion = {
                "fecha": datetime.now(),
                "descripcion": observacion.get('descripcion', ''),
                "tipo": observacion.get('tipo', 'general'),
                "investigador": observacion.get('investigador', ''),
                "gravedad": observacion.get('gravedad', 'normal')
            }
            
            result = self.collection.update_one(
                {"codigo_ensayo": codigo_ensayo},
                {
                    "$push": {"observaciones": nueva_observacion},
                    "$set": {"metadata.fecha_modificacion": datetime.now()}
                }
            )
            
            if result.modified_count > 0:
                return True, "Observación agregada exitosamente"
            else:
                return False, "Ensayo no encontrado"
                
        except Exception as e:
            return False, f"Error agregando observación: {e}"
    
    def actualizar_participantes(self, codigo_ensayo, reclutados=None, completados=None):
        """
        Actualizar contadores de participantes.
        """
        if self.collection is None:
            return False, "Conexión a MongoDB no disponible"
        
        try:
            update_doc = {"metadata.fecha_modificacion": datetime.now()}
            
            if reclutados is not None:
                update_doc["participantes.reclutados"] = reclutados
            
            if completados is not None:
                update_doc["participantes.completados"] = completados
            
            result = self.collection.update_one(
                {"codigo_ensayo": codigo_ensayo},
                {"$set": update_doc}
            )
            
            if result.modified_count > 0:
                return True, "Participantes actualizados"
            else:
                return False, "Ensayo no encontrado"
                
        except Exception as e:
            return False, f"Error actualizando participantes: {e}"
    
    def agregar_resultado(self, codigo_ensayo, categoria, datos_resultado):
        """
        Agregar resultados al ensayo (estructura flexible).
        """
        if self.collection is None:
            return False, "Conexión a MongoDB no disponible"
        
        try:
            result = self.collection.update_one(
                {"codigo_ensayo": codigo_ensayo},
                {
                    "$set": {
                        f"resultados.{categoria}": datos_resultado,
                        "metadata.fecha_modificacion": datetime.now()
                    }
                }
            )
            
            if result.modified_count > 0:
                return True, f"Resultado '{categoria}' agregado exitosamente"
            else:
                return False, "Ensayo no encontrado"
                
        except Exception as e:
            return False, f"Error agregando resultado: {e}"
    
    # ============= BÚSQUEDAS AVANZADAS =============
    
    def buscar_por_criterios(self, filtros=None, ordenar_por=None, limite=100):
        """
        Búsqueda avanzada con múltiples criterios.
        
        filtros: dict con criterios de búsqueda
        ordenar_por: tuple (campo, dirección) ej: ('metadata.fecha_creacion', -1)
        limite: número máximo de resultados
        """
        if self.collection is None:
            return []
        
        try:
            query = {}
            
            if filtros:
                # Fase
                if 'fase' in filtros:
                    query['fase'] = filtros['fase']
                
                # Estado
                if 'estado' in filtros:
                    query['estado'] = filtros['estado']
                
                # Medicamento (búsqueda parcial)
                if 'medicamento' in filtros:
                    query['medicamento'] = {"$regex": filtros['medicamento'], "$options": "i"}
                
                # Investigador
                if 'investigador' in filtros:
                    query['investigador_principal'] = {"$regex": filtros['investigador'], "$options": "i"}
                
                # Rango de fechas
                if 'fecha_inicio_desde' in filtros or 'fecha_inicio_hasta' in filtros:
                    query['fecha_inicio'] = {}
                    if 'fecha_inicio_desde' in filtros:
                        query['fecha_inicio']['$gte'] = filtros['fecha_inicio_desde']
                    if 'fecha_inicio_hasta' in filtros:
                        query['fecha_inicio']['$lte'] = filtros['fecha_inicio_hasta']
                
                # Participantes mínimos
                if 'min_participantes' in filtros:
                    query['participantes.reclutados'] = {"$gte": filtros['min_participantes']}
            
            # Ejecutar búsqueda
            cursor = self.collection.find(query)
            
            # Ordenar
            if ordenar_por:
                campo, direccion = ordenar_por
                cursor = cursor.sort(campo, direccion)
            
            # Limitar
            cursor = cursor.limit(limite)
            
            return list(cursor)
            
        except Exception as e:
            print(f"Error en búsqueda avanzada: {e}")
            return []
    
    def buscar_con_observaciones_recientes(self, dias=7):
        """
        Buscar ensayos con observaciones en los últimos N días.
        """
        if self.collection is None:
            return []
        
        try:
            fecha_limite = datetime.now()
            from datetime import timedelta
            fecha_limite = fecha_limite - timedelta(days=dias)
            
            query = {
                "observaciones": {
                    "$elemMatch": {
                        "fecha": {"$gte": fecha_limite}
                    }
                }
            }
            
            return list(self.collection.find(query))
            
        except Exception as e:
            print(f"Error buscando observaciones recientes: {e}")
            return []
    
    def estadisticas_por_fase(self):
        """
        Obtener estadísticas agrupadas por fase.
        Usa agregación de MongoDB.
        """
        if self.collection is None:
            return []
        
        try:
            pipeline = [
                {
                    "$group": {
                        "_id": "$fase",
                        "total_ensayos": {"$sum": 1},
                        "participantes_totales": {"$sum": "$participantes.reclutados"},
                        "promedio_participantes": {"$avg": "$participantes.reclutados"},
                        "ensayos_activos": {
                            "$sum": {
                                "$cond": [{"$eq": ["$estado", "en_progreso"]}, 1, 0]
                            }
                        }
                    }
                },
                {
                    "$sort": {"_id": 1}
                }
            ]
            
            return list(self.collection.aggregate(pipeline))
            
        except Exception as e:
            print(f"Error calculando estadísticas: {e}")
            return []
    
    def listar_ensayos_activos(self):
        """
        Listar todos los ensayos activos (en progreso o planificados).
        """
        if self.collection is None:
            return []
        
        try:
            query = {
                "estado": {"$in": ["planificado", "en_progreso", "reclutando"]}
            }
            
            return list(self.collection.find(query).sort("metadata.fecha_creacion", DESCENDING))
            
        except Exception as e:
            print(f"Error listando ensayos activos: {e}")
            return []
