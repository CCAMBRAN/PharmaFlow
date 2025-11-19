"""
Schema de validacion para la coleccion de ensayos clinicos en MongoDB.
Define la estructura y reglas de validacion de documentos.
"""

# JSON Schema para validacion de ensayos clinicos
ENSAYO_CLINICO_SCHEMA = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["codigo_ensayo", "titulo", "medicamento", "fase", "estado"],
        "properties": {
            "codigo_ensayo": {
                "bsonType": "string",
                "description": "Codigo unico del ensayo - requerido",
                "pattern": "^[A-Z0-9-]+$"
            },
            "titulo": {
                "bsonType": "string",
                "description": "Titulo del ensayo clinico - requerido",
                "minLength": 10,
                "maxLength": 500
            },
            "medicamento": {
                "bsonType": "string",
                "description": "Medicamento estudiado - requerido",
                "minLength": 3
            },
            "fase": {
                "enum": ["I", "II", "III", "IV", "Preclinica"],
                "description": "Fase del ensayo clinico - requerido"
            },
            "estado": {
                "enum": ["planificado", "reclutando", "en_progreso", "completado", 
                        "suspendido", "cancelado"],
                "description": "Estado actual del ensayo - requerido"
            },
            "investigador_principal": {
                "bsonType": "string",
                "description": "Nombre del investigador principal"
            },
            "fecha_inicio": {
                "bsonType": "date",
                "description": "Fecha de inicio del ensayo"
            },
            "fecha_fin_estimada": {
                "bsonType": "date",
                "description": "Fecha estimada de finalizacion"
            },
            "participantes": {
                "bsonType": "object",
                "description": "Informacion de participantes",
                "properties": {
                    "objetivo": {
                        "bsonType": "int",
                        "minimum": 0,
                        "description": "Numero objetivo de participantes"
                    },
                    "reclutados": {
                        "bsonType": "int",
                        "minimum": 0,
                        "description": "Participantes reclutados"
                    },
                    "completados": {
                        "bsonType": "int",
                        "minimum": 0,
                        "description": "Participantes que completaron el ensayo"
                    }
                }
            },
            "observaciones": {
                "bsonType": "array",
                "description": "Array de observaciones del ensayo",
                "items": {
                    "bsonType": "object",
                    "required": ["fecha", "descripcion"],
                    "properties": {
                        "fecha": {
                            "bsonType": "date",
                            "description": "Fecha de la observacion"
                        },
                        "descripcion": {
                            "bsonType": "string",
                            "minLength": 1,
                            "description": "Descripcion de la observacion"
                        },
                        "tipo": {
                            "enum": ["eficacia", "efecto_secundario", "administrativo", "general"],
                            "description": "Tipo de observacion"
                        },
                        "investigador": {
                            "bsonType": "string",
                            "description": "Investigador que registro la observacion"
                        },
                        "gravedad": {
                            "enum": ["critico", "grave", "moderado", "leve", "normal", "positivo"],
                            "description": "Nivel de gravedad o importancia"
                        }
                    }
                }
            },
            "resultados": {
                "bsonType": "object",
                "description": "Resultados del ensayo (estructura flexible)"
            },
            "metadata": {
                "bsonType": "object",
                "description": "Metadata del documento",
                "properties": {
                    "fecha_creacion": {
                        "bsonType": "date",
                        "description": "Fecha de creacion del documento"
                    },
                    "fecha_modificacion": {
                        "bsonType": "date",
                        "description": "Fecha de ultima modificacion"
                    },
                    "creado_por": {
                        "bsonType": "string",
                        "description": "Usuario que creo el documento"
                    },
                    "version": {
                        "bsonType": "int",
                        "minimum": 1,
                        "description": "Version del documento"
                    }
                }
            }
        }
    }
}


def aplicar_validacion_schema(db):
    """
    Aplicar schema de validacion a la coleccion ensayos_clinicos.
    Si la coleccion existe, actualiza las reglas de validacion.
    Si no existe, la crea con validacion.
    """
    try:
        # Verificar si la coleccion existe
        if 'ensayos_clinicos' in db.list_collection_names():
            # Actualizar validacion en coleccion existente
            db.command({
                'collMod': 'ensayos_clinicos',
                'validator': ENSAYO_CLINICO_SCHEMA,
                'validationLevel': 'moderate',  # moderate o strict
                'validationAction': 'warn'  # warn o error
            })
            return True, "Validacion actualizada en coleccion existente"
        else:
            # Crear coleccion con validacion
            db.create_collection(
                'ensayos_clinicos',
                validator=ENSAYO_CLINICO_SCHEMA,
                validationLevel='moderate',
                validationAction='warn'
            )
            return True, "Coleccion creada con validacion"
    
    except Exception as e:
        return False, f"Error aplicando validacion: {e}"


def obtener_info_validacion(db):
    """
    Obtener informacion sobre las reglas de validacion de la coleccion.
    """
    try:
        info = db.command({'listCollections': 1, 'filter': {'name': 'ensayos_clinicos'}})
        
        if info['cursor']['firstBatch']:
            collection_info = info['cursor']['firstBatch'][0]
            options = collection_info.get('options', {})
            
            return {
                'tiene_validacion': 'validator' in options,
                'validation_level': options.get('validationLevel', 'N/A'),
                'validation_action': options.get('validationAction', 'N/A'),
                'validator': options.get('validator', {})
            }
        else:
            return {'tiene_validacion': False}
    
    except Exception as e:
        print(f"Error obteniendo info de validacion: {e}")
        return {}


def crear_indices_optimizados(db):
    """
    Crear indices para mejorar rendimiento de consultas.
    """
    try:
        collection = db['ensayos_clinicos']
        
        # Indice unico en codigo_ensayo
        collection.create_index([('codigo_ensayo', 1)], unique=True, name='idx_codigo_ensayo')
        
        # Indice compuesto para busquedas frecuentes
        collection.create_index([('fase', 1), ('estado', 1)], name='idx_fase_estado')
        
        # Indice de texto para busquedas en medicamento y titulo
        collection.create_index([
            ('medicamento', 'text'),
            ('titulo', 'text')
        ], default_language='spanish', name='idx_text_search')
        
        # Indice para ordenar por fecha
        collection.create_index([('metadata.fecha_creacion', -1)], name='idx_fecha_creacion')
        
        # Indice para busquedas por investigador
        collection.create_index([('investigador_principal', 1)], name='idx_investigador')
        
        # Indice para busquedas por numero de participantes
        collection.create_index([('participantes.reclutados', -1)], name='idx_participantes')
        
        return True, "Indices creados exitosamente"
    
    except Exception as e:
        return False, f"Error creando indices: {e}"


def listar_indices(db):
    """
    Listar todos los indices de la coleccion.
    """
    try:
        collection = db['ensayos_clinicos']
        indices = collection.list_indexes()
        return list(indices)
    except Exception as e:
        print(f"Error listando indices: {e}")
        return []
