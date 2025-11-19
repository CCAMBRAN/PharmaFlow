"""
Script para configurar validacion de schema e indices en MongoDB.
"""
import os
import sys
from dotenv import load_dotenv
load_dotenv()

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from utils.database_connector import DatabaseConnector
from models.mongodb_schema import (
    aplicar_validacion_schema,
    obtener_info_validacion,
    crear_indices_optimizados,
    listar_indices
)

def main():
    print("=" * 70)
    print("CONFIGURACION DE SCHEMA E INDICES - MONGODB")
    print("=" * 70)
    
    connector = DatabaseConnector()
    db = connector.connect_mongodb()
    
    if db is None:
        print("\n[ERROR] No se pudo conectar a MongoDB")
        return
    
    # 1. Aplicar validacion de schema
    print("\n>> Aplicando validacion de schema...")
    exito, msg = aplicar_validacion_schema(db)
    if exito:
        print(f"   [OK] {msg}")
    else:
        print(f"   [ERROR] {msg}")
    
    # 2. Mostrar informacion de validacion
    print("\n>> Informacion de validacion:")
    info = obtener_info_validacion(db)
    if info.get('tiene_validacion'):
        print(f"   Nivel de validacion: {info.get('validation_level')}")
        print(f"   Accion al fallar: {info.get('validation_action')}")
        print(f"   [OK] Validacion activa")
    else:
        print("   [ADVERTENCIA] No hay validacion configurada")
    
    # 3. Crear indices
    print("\n>> Creando indices optimizados...")
    exito, msg = crear_indices_optimizados(db)
    if exito:
        print(f"   [OK] {msg}")
    else:
        print(f"   [ERROR] {msg}")
    
    # 4. Listar indices
    print("\n>> Indices configurados:")
    indices = listar_indices(db)
    for idx in indices:
        nombre = idx.get('name')
        keys = idx.get('key', {})
        unique = idx.get('unique', False)
        
        keys_str = ', '.join([f"{k}:{v}" for k, v in keys.items()])
        unique_str = " (UNIQUE)" if unique else ""
        
        print(f"   - {nombre}: {keys_str}{unique_str}")
    
    print("\n>> Reglas de validacion aplicadas:")
    print("   - codigo_ensayo: requerido, patron [A-Z0-9-]+")
    print("   - titulo: requerido, 10-500 caracteres")
    print("   - medicamento: requerido, min 3 caracteres")
    print("   - fase: requerido, valores: I, II, III, IV, Preclinica")
    print("   - estado: requerido, valores especificos")
    print("   - participantes: validacion de estructura y tipos")
    print("   - observaciones: array con estructura validada")
    
    print("\n" + "=" * 70)
    print("[OK] CONFIGURACION COMPLETADA")
    print("=" * 70)
    
    print("\n>> Notas:")
    print("   - Nivel 'moderate': valida inserts y updates completos")
    print("   - Accion 'warn': registra advertencias pero permite el documento")
    print("   - Para validacion estricta, cambiar a 'strict' y 'error'")
    
    connector.close_all_connections()

if __name__ == '__main__':
    main()
