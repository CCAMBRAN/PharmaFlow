"""
Router para endpoints de Neo4j (Grafos de Medicamentos e Interacciones)
"""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

from services.graph_service import GraphService
from api.dependencies import get_db_connector

router = APIRouter()

# Obtener conector de BD
db_connector = get_db_connector()

# ============= MODELOS PYDANTIC =============

class MedicamentoNodo(BaseModel):
    nombre: str
    descripcion: Optional[str] = None

class CompuestoNodo(BaseModel):
    nombre: str
    formula: Optional[str] = None

class InteraccionCreate(BaseModel):
    medicamento1: str
    medicamento2: str
    severidad: str
    descripcion: str

# ============= ENDPOINTS - CONSULTAS =============

@router.get("/medicamentos")
async def listar_medicamentos():
    """Listar todos los medicamentos en el grafo"""
    try:
        service = GraphService(db_connector)
        medicamentos = service.listar_todos_medicamentos()
        return {
            "total": len(medicamentos),
            "medicamentos": medicamentos
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/medicamentos/{nombre}/compuestos")
async def obtener_compuestos_medicamento(nombre: str):
    """Obtener todos los compuestos de un medicamento"""
    try:
        service = GraphService(db_connector)
        compuestos = service.obtener_compuestos_medicamento(nombre)
        return {
            "medicamento": nombre,
            "total_compuestos": len(compuestos),
            "compuestos": compuestos
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/medicamentos/{nombre}/interacciones")
async def obtener_interacciones(nombre: str):
    """Obtener interacciones medicamentosas"""
    try:
        service = GraphService(db_connector)
        interacciones = service.obtener_interacciones_medicamento(nombre)
        return {
            "medicamento": nombre,
            "total_interacciones": len(interacciones),
            "interacciones": interacciones
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/interacciones/detectar")
async def detectar_interacciones(medicamentos: str = Query(..., description="Lista separada por comas")):
    """Detectar interacciones entre múltiples medicamentos"""
    try:
        service = GraphService(db_connector)
        lista_meds = [m.strip() for m in medicamentos.split(',')]
        
        if len(lista_meds) < 2:
            raise HTTPException(status_code=400, detail="Se requieren al menos 2 medicamentos")
        
        interacciones = service.detectar_interacciones_multiples(lista_meds)
        return {
            "medicamentos_consultados": lista_meds,
            "total_interacciones": len(interacciones),
            "interacciones": interacciones
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/camino-mas-corto")
async def camino_mas_corto(origen: str = Query(...), destino: str = Query(...)):
    """Encontrar camino más corto entre dos nodos"""
    try:
        service = GraphService(db_connector)
        camino = service.encontrar_camino_mas_corto(origen, destino)
        
        if not camino:
            return {
                "origen": origen,
                "destino": destino,
                "camino_encontrado": False,
                "mensaje": "No existe camino entre los nodos"
            }
        
        return {
            "origen": origen,
            "destino": destino,
            "camino_encontrado": True,
            "longitud": len(camino['nodos']) - 1,
            "camino": camino
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/alternativas/{medicamento}")
async def sugerir_alternativas(medicamento: str):
    """Sugerir medicamentos alternativos basados en compuestos similares"""
    try:
        service = GraphService(db_connector)
        alternativas = service.sugerir_medicamentos_alternativos(medicamento)
        return {
            "medicamento_original": medicamento,
            "total_alternativas": len(alternativas),
            "alternativas": alternativas
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============= ENDPOINTS - ESTADÍSTICAS =============

@router.get("/stats")
async def obtener_estadisticas_grafo():
    """Obtener estadísticas del grafo"""
    try:
        service = GraphService(db_connector)
        stats = service.obtener_estadisticas_grafo()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============= ENDPOINTS - CREACIÓN (OPCIONAL) =============

@router.post("/medicamentos", status_code=201)
async def crear_medicamento(medicamento: MedicamentoNodo):
    """Crear nodo de medicamento"""
    try:
        service = GraphService(db_connector)
        service.crear_nodo_medicamento(medicamento.nombre, medicamento.descripcion)
        return {"message": f"Medicamento '{medicamento.nombre}' creado"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/compuestos", status_code=201)
async def crear_compuesto(compuesto: CompuestoNodo):
    """Crear nodo de compuesto"""
    try:
        service = GraphService(db_connector)
        service.crear_nodo_compuesto(compuesto.nombre, compuesto.formula)
        return {"message": f"Compuesto '{compuesto.nombre}' creado"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/interacciones", status_code=201)
async def crear_interaccion(interaccion: InteraccionCreate):
    """Crear relación de interacción entre medicamentos"""
    try:
        service = GraphService(db_connector)
        service.crear_interaccion(
            interaccion.medicamento1,
            interaccion.medicamento2,
            interaccion.severidad,
            interaccion.descripcion
        )
        return {"message": "Interacción creada"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
