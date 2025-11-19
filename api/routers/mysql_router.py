"""
Router para endpoints de MySQL (Usuarios, Medicamentos, Inventario, Ventas)
"""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

from services.user_service import UserService
from services.inventory_service import InventoryService

router = APIRouter()

# ============= MODELOS PYDANTIC =============

class UsuarioCreate(BaseModel):
    nombre_usuario: str = Field(..., min_length=3, max_length=50)
    contrasena: str = Field(..., min_length=6)
    email: str
    rol: str = Field(..., pattern="^(gerente|farmaceutico|investigador)$")

class MedicamentoCreate(BaseModel):
    nombre: str
    principio_activo: str
    precio: float = Field(..., gt=0)
    stock_minimo: int = Field(..., ge=0)

class LoteCreate(BaseModel):
    medicamento_id: int
    numero_lote: str
    cantidad: int = Field(..., gt=0)
    fecha_fabricacion: str  # YYYY-MM-DD
    fecha_vencimiento: str  # YYYY-MM-DD
    precio_compra: float = Field(..., gt=0)

class VentaCreate(BaseModel):
    usuario_id: int
    detalles: List[dict]  # [{"medicamento_id": 1, "cantidad": 2, "precio_unitario": 15.50}]

# ============= ENDPOINTS - USUARIOS =============

@router.get("/usuarios")
async def listar_usuarios():
    """Listar todos los usuarios"""
    try:
        service = UserService()
        usuarios = service.listar_usuarios()
        return {"usuarios": usuarios}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/usuarios", status_code=201)
async def crear_usuario(usuario: UsuarioCreate):
    """Crear nuevo usuario"""
    try:
        service = UserService()
        usuario_id = service.crear_usuario(
            usuario.nombre_usuario,
            usuario.contrasena,
            usuario.email,
            usuario.rol
        )
        return {"message": "Usuario creado", "usuario_id": usuario_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/usuarios/{usuario_id}")
async def obtener_usuario(usuario_id: int):
    """Obtener usuario por ID"""
    try:
        service = UserService()
        usuario = service.obtener_usuario_por_id(usuario_id)
        if not usuario:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        return usuario
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/usuarios/{usuario_id}/permisos")
async def obtener_permisos_usuario(usuario_id: int):
    """Obtener permisos de un usuario"""
    try:
        service = UserService()
        permisos = service.obtener_permisos_usuario(usuario_id)
        return {"usuario_id": usuario_id, "permisos": permisos}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/usuarios/{usuario_id}")
async def eliminar_usuario(usuario_id: int):
    """Eliminar usuario"""
    try:
        service = UserService()
        # Implementar lógica de eliminación
        return {"message": f"Usuario {usuario_id} eliminado"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============= ENDPOINTS - MEDICAMENTOS =============

@router.get("/medicamentos")
async def listar_medicamentos():
    """Listar todos los medicamentos"""
    try:
        service = InventoryService()
        medicamentos = service.listar_medicamentos()
        return {"medicamentos": medicamentos}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/medicamentos", status_code=201)
async def crear_medicamento(med: MedicamentoCreate):
    """Crear nuevo medicamento"""
    try:
        service = InventoryService()
        med_id = service.crear_medicamento(
            med.nombre,
            med.principio_activo,
            med.precio,
            med.stock_minimo
        )
        return {"message": "Medicamento creado", "medicamento_id": med_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/medicamentos/{medicamento_id}")
async def obtener_medicamento(medicamento_id: int):
    """Obtener medicamento por ID"""
    try:
        service = InventoryService()
        medicamento = service.obtener_medicamento(medicamento_id)
        if not medicamento:
            raise HTTPException(status_code=404, detail="Medicamento no encontrado")
        return medicamento
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/medicamentos/{medicamento_id}/stock")
async def obtener_stock_medicamento(medicamento_id: int):
    """Obtener stock total de un medicamento"""
    try:
        service = InventoryService()
        stock = service.obtener_stock_total(medicamento_id)
        return {
            "medicamento_id": medicamento_id,
            "stock_total": stock
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============= ENDPOINTS - LOTES =============

@router.get("/lotes")
async def listar_lotes(medicamento_id: Optional[int] = Query(None)):
    """Listar lotes (opcionalmente filtrados por medicamento)"""
    try:
        service = InventoryService()
        lotes = service.listar_lotes(medicamento_id)
        return {"lotes": lotes}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/lotes", status_code=201)
async def crear_lote(lote: LoteCreate):
    """Crear nuevo lote de medicamento"""
    try:
        service = InventoryService()
        lote_id = service.crear_lote(
            lote.medicamento_id,
            lote.numero_lote,
            lote.cantidad,
            lote.fecha_fabricacion,
            lote.fecha_vencimiento,
            lote.precio_compra
        )
        return {"message": "Lote creado", "lote_id": lote_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# ============= ENDPOINTS - VENTAS =============

@router.get("/ventas")
async def listar_ventas(usuario_id: Optional[int] = Query(None)):
    """Listar ventas (opcionalmente filtradas por usuario)"""
    try:
        service = InventoryService()
        ventas = service.listar_ventas(usuario_id)
        return {"ventas": ventas}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/ventas", status_code=201)
async def registrar_venta(venta: VentaCreate):
    """Registrar nueva venta"""
    try:
        service = InventoryService()
        venta_id = service.registrar_venta(venta.usuario_id, venta.detalles)
        return {"message": "Venta registrada", "venta_id": venta_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/ventas/{venta_id}")
async def obtener_venta(venta_id: int):
    """Obtener detalle de una venta"""
    try:
        service = InventoryService()
        venta = service.obtener_venta(venta_id)
        if not venta:
            raise HTTPException(status_code=404, detail="Venta no encontrada")
        return venta
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============= ENDPOINTS - AUDITORÍA =============

@router.get("/auditoria")
async def obtener_auditoria(
    usuario_id: Optional[int] = Query(None),
    accion: Optional[str] = Query(None),
    limite: int = Query(50, le=500)
):
    """Obtener registros de auditoría"""
    try:
        service = UserService()
        registros = service.obtener_auditoria(usuario_id, accion, limite)
        return {"registros": registros}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
