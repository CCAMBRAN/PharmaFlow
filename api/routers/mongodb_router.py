"""
Router para endpoints de MongoDB (Ensayos Clínicos)
"""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

from services.clinical_service import ClinicalService

router = APIRouter()

# ============= MODELOS PYDANTIC =============

class EnsayoCreate(BaseModel):
    codigo_ensayo: str = Field(..., min_length=5)
    titulo: str
    medicamento: str
    fase: str = Field(..., pattern="^(I|II|III|IV|Fase I|Fase II|Fase III|Fase IV)$")
    estado: str = Field(..., pattern="^(planificado|reclutando|en_progreso|completado|suspendido|cancelado)$")
    investigador_principal: str
    institucion: str
    objetivo: str
    criterios_inclusion: List[str]
    criterios_exclusion: List[str]
    participantes_objetivo: int = Field(..., gt=0)

class EnsayoUpdate(BaseModel):
    titulo: Optional[str] = None
    estado: Optional[str] = None
    investigador_principal: Optional[str] = None
    fase: Optional[str] = None

class ObservacionCreate(BaseModel):
    tipo: str = Field(..., pattern="^(eficacia|seguridad|efecto_secundario|administrativo|otro)$")
    descripcion: str
    severidad: Optional[str] = Field(None, pattern="^(leve|moderada|grave)$")

class ParticipantesUpdate(BaseModel):
    reclutados: Optional[int] = Field(None, ge=0)
    activos: Optional[int] = Field(None, ge=0)
    completados: Optional[int] = Field(None, ge=0)
    retirados: Optional[int] = Field(None, ge=0)

class ResultadoCreate(BaseModel):
    categoria: str  # eficacia, seguridad, farmacocinetica, etc.
    datos: Dict[str, Any]

# ============= ENDPOINTS =============

@router.get("/ensayos")
async def listar_ensayos(
    fase: Optional[str] = Query(None),
    estado: Optional[str] = Query(None),
    medicamento: Optional[str] = Query(None),
    solo_activos: bool = Query(False)
):
    """Listar ensayos clínicos con filtros opcionales"""
    try:
        service = ClinicalService()
        
        if solo_activos:
            ensayos = service.listar_ensayos_activos()
        elif fase or estado or medicamento:
            criterios = {}
            if fase:
                criterios['fase'] = fase
            if estado:
                criterios['estado'] = estado
            if medicamento:
                criterios['medicamento'] = medicamento
            ensayos = service.buscar_por_criterios(**criterios)
        else:
            # Listar todos
            ensayos = list(service.collection.find({}))
        
        # Convertir ObjectId a string
        for ensayo in ensayos:
            ensayo['_id'] = str(ensayo['_id'])
        
        return {
            "total": len(ensayos),
            "ensayos": ensayos
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/ensayos", status_code=201)
async def crear_ensayo(ensayo: EnsayoCreate):
    """Crear nuevo ensayo clínico"""
    try:
        service = ClinicalService()
        ensayo_data = ensayo.model_dump()
        ensayo_id = service.crear_ensayo(ensayo_data)
        return {
            "message": "Ensayo clínico creado",
            "ensayo_id": str(ensayo_id)
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/ensayos/{codigo_ensayo}")
async def obtener_ensayo(codigo_ensayo: str):
    """Obtener ensayo clínico por código"""
    try:
        service = ClinicalService()
        ensayo = service.obtener_ensayo(codigo_ensayo)
        if not ensayo:
            raise HTTPException(status_code=404, detail="Ensayo no encontrado")
        ensayo['_id'] = str(ensayo['_id'])
        return ensayo
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/ensayos/{codigo_ensayo}")
async def actualizar_ensayo(codigo_ensayo: str, updates: EnsayoUpdate):
    """Actualizar ensayo clínico"""
    try:
        service = ClinicalService()
        updates_dict = {k: v for k, v in updates.model_dump().items() if v is not None}
        
        if not updates_dict:
            raise HTTPException(status_code=400, detail="No hay campos para actualizar")
        
        modificados = service.actualizar_ensayo(codigo_ensayo, updates_dict)
        return {
            "message": "Ensayo actualizado",
            "campos_modificados": modificados
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/ensayos/{codigo_ensayo}")
async def eliminar_ensayo(codigo_ensayo: str, hard_delete: bool = Query(False)):
    """Eliminar ensayo clínico (soft delete por defecto)"""
    try:
        service = ClinicalService()
        resultado = service.eliminar_ensayo(codigo_ensayo, hard_delete)
        
        if hard_delete:
            return {"message": "Ensayo eliminado permanentemente"}
        else:
            return {"message": "Ensayo marcado como cancelado"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/ensayos/{codigo_ensayo}/observaciones")
async def agregar_observacion(codigo_ensayo: str, observacion: ObservacionCreate):
    """Agregar observación a un ensayo"""
    try:
        service = ClinicalService()
        obs_data = observacion.model_dump()
        service.agregar_observacion(codigo_ensayo, **obs_data)
        return {"message": "Observación agregada exitosamente"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/ensayos/{codigo_ensayo}/participantes")
async def actualizar_participantes(codigo_ensayo: str, participantes: ParticipantesUpdate):
    """Actualizar contadores de participantes"""
    try:
        service = ClinicalService()
        updates = {k: v for k, v in participantes.model_dump().items() if v is not None}
        
        if not updates:
            raise HTTPException(status_code=400, detail="No hay campos para actualizar")
        
        service.actualizar_participantes(codigo_ensayo, **updates)
        return {"message": "Participantes actualizados"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/ensayos/{codigo_ensayo}/resultados")
async def agregar_resultado(codigo_ensayo: str, resultado: ResultadoCreate):
    """Agregar resultados a un ensayo"""
    try:
        service = ClinicalService()
        service.agregar_resultado(codigo_ensayo, resultado.categoria, resultado.datos)
        return {"message": f"Resultado '{resultado.categoria}' agregado exitosamente"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/ensayos/busqueda/avanzada")
async def busqueda_avanzada(
    fase: Optional[str] = Query(None),
    estado: Optional[str] = Query(None),
    medicamento: Optional[str] = Query(None),
    investigador: Optional[str] = Query(None),
    min_participantes: Optional[int] = Query(None),
    fecha_inicio_desde: Optional[str] = Query(None),
    fecha_inicio_hasta: Optional[str] = Query(None)
):
    """Búsqueda avanzada con múltiples criterios"""
    try:
        service = ClinicalService()
        criterios = {}
        
        if fase:
            criterios['fase'] = fase
        if estado:
            criterios['estado'] = estado
        if medicamento:
            criterios['medicamento'] = medicamento
        if investigador:
            criterios['investigador'] = investigador
        if min_participantes:
            criterios['min_participantes'] = min_participantes
        if fecha_inicio_desde:
            criterios['fecha_inicio_desde'] = fecha_inicio_desde
        if fecha_inicio_hasta:
            criterios['fecha_inicio_hasta'] = fecha_inicio_hasta
        
        ensayos = service.buscar_por_criterios(**criterios)
        
        for ensayo in ensayos:
            ensayo['_id'] = str(ensayo['_id'])
        
        return {
            "total": len(ensayos),
            "criterios": criterios,
            "ensayos": ensayos
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/estadisticas/por-fase")
async def estadisticas_por_fase():
    """Obtener estadísticas agregadas por fase"""
    try:
        service = ClinicalService()
        estadisticas = service.estadisticas_por_fase()
        return {
            "total_fases": len(estadisticas),
            "estadisticas": estadisticas
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
