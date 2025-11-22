"""
Router para endpoints de Redis (Sesiones, Caché, Contadores)
"""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

from services.keyvalue_service import KeyValueService
from api.dependencies import get_db_connector

router = APIRouter()

# Obtener conector de BD
db_connector = get_db_connector()

# ============= MODELOS PYDANTIC =============

class SesionCreate(BaseModel):
    usuario_id: int
    nombre_usuario: str
    rol: str
    expiracion_minutos: int = Field(default=30, gt=0, le=1440)

class CachePrecio(BaseModel):
    medicamento_id: int
    precio: float
    expiracion_segundos: int = Field(default=300, gt=0)

# ============= ENDPOINTS - SESIONES =============

@router.post("/sesiones", status_code=201)
async def crear_sesion(sesion: SesionCreate):
    """Crear nueva sesión de usuario"""
    try:
        service = KeyValueService(db_connector)
        session_id = service.crear_sesion(
            sesion.usuario_id,
            sesion.nombre_usuario,
            sesion.rol,
            sesion.expiracion_minutos
        )
        return {
            "message": "Sesión creada",
            "session_id": session_id,
            "expira_en_minutos": sesion.expiracion_minutos
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sesiones/{session_id}")
async def obtener_sesion(session_id: str):
    """Obtener datos de sesión"""
    try:
        service = KeyValueService(db_connector)
        datos = service.obtener_sesion(session_id)
        if not datos:
            raise HTTPException(status_code=404, detail="Sesión no encontrada o expirada")
        return datos
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/sesiones/{session_id}")
async def cerrar_sesion(session_id: str):
    """Cerrar sesión (logout)"""
    try:
        service = KeyValueService(db_connector)
        service.cerrar_sesion(session_id)
        return {"message": "Sesión cerrada"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sesiones")
async def listar_sesiones_activas():
    """Listar todas las sesiones activas"""
    try:
        service = KeyValueService(db_connector)
        sesiones = service.listar_sesiones_activas()
        return {
            "total": len(sesiones),
            "sesiones": sesiones
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============= ENDPOINTS - CACHÉ DE PRECIOS =============

@router.post("/cache/precios", status_code=201)
async def cachear_precio(cache: CachePrecio):
    """Cachear precio de medicamento"""
    try:
        service = KeyValueService(db_connector)
        service.cachear_precio(
            cache.medicamento_id,
            cache.precio,
            cache.expiracion_segundos
        )
        return {
            "message": "Precio cacheado",
            "medicamento_id": cache.medicamento_id,
            "expira_en_segundos": cache.expiracion_segundos
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/cache/precios/{medicamento_id}")
async def obtener_precio_cache(medicamento_id: int):
    """Obtener precio desde caché"""
    try:
        service = KeyValueService(db_connector)
        precio = service.obtener_precio_cache(medicamento_id)
        if precio is None:
            raise HTTPException(status_code=404, detail="Precio no encontrado en caché")
        return {
            "medicamento_id": medicamento_id,
            "precio": precio
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/cache/precios/{medicamento_id}")
async def invalidar_precio_cache(medicamento_id: int):
    """Invalidar precio en caché"""
    try:
        service = KeyValueService(db_connector)
        service.invalidar_precio_cache(medicamento_id)
        return {"message": "Precio invalidado"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============= ENDPOINTS - CONTADORES =============

@router.post("/contadores/{nombre}/incrementar")
async def incrementar_contador(nombre: str, cantidad: int = Query(1, ge=1)):
    """Incrementar contador"""
    try:
        service = KeyValueService(db_connector)
        nuevo_valor = service.incrementar_contador(nombre, cantidad)
        return {
            "contador": nombre,
            "nuevo_valor": nuevo_valor
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/contadores/{nombre}")
async def obtener_contador(nombre: str):
    """Obtener valor de contador"""
    try:
        service = KeyValueService(db_connector)
        valor = service.obtener_contador(nombre)
        return {
            "contador": nombre,
            "valor": valor
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/contadores/{nombre}")
async def resetear_contador(nombre: str):
    """Resetear contador a 0"""
    try:
        service = KeyValueService(db_connector)
        service.resetear_contador(nombre)
        return {"message": f"Contador '{nombre}' reseteado"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============= ENDPOINTS - ACTIVIDAD RECIENTE =============

@router.post("/actividad/{usuario_id}")
async def registrar_actividad(usuario_id: int, actividad: Dict[str, Any]):
    """Registrar actividad de usuario"""
    try:
        service = KeyValueService(db_connector)
        service.registrar_actividad_usuario(usuario_id, actividad)
        return {"message": "Actividad registrada"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/actividad/{usuario_id}")
async def obtener_actividad(usuario_id: int, limite: int = Query(10, le=100)):
    """Obtener actividad reciente de usuario"""
    try:
        service = KeyValueService(db_connector)
        actividades = service.obtener_actividad_reciente(usuario_id, limite)
        return {
            "usuario_id": usuario_id,
            "total": len(actividades),
            "actividades": actividades
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============= ENDPOINTS - UTILIDADES =============

@router.get("/stats")
async def obtener_estadisticas_redis():
    """Obtener estadísticas de Redis"""
    try:
        service = KeyValueService(db_connector)
        info = service.redis.info()
        return {
            "servidor": {
                "version": info.get('redis_version'),
                "uptime_dias": info.get('uptime_in_days'),
                "modo": info.get('redis_mode')
            },
            "clientes": {
                "conectados": info.get('connected_clients'),
                "bloqueados": info.get('blocked_clients')
            },
            "memoria": {
                "usada_mb": round(info.get('used_memory', 0) / 1024 / 1024, 2),
                "pico_mb": round(info.get('used_memory_peak', 0) / 1024 / 1024, 2)
            },
            "estadisticas": {
                "comandos_totales": info.get('total_commands_processed'),
                "keys_totales": service.redis.dbsize()
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/flush")
async def limpiar_redis(confirmar: bool = Query(False)):
    """Limpiar toda la base de datos Redis (PELIGROSO)"""
    if not confirmar:
        raise HTTPException(
            status_code=400,
            detail="Debe confirmar la operación con ?confirmar=true"
        )
    try:
        service = KeyValueService(db_connector)
        service.redis.flushdb()
        return {"message": "Base de datos Redis limpiada"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
