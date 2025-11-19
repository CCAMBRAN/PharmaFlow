"""
Script para configurar el sistema de roles y permisos en MySQL.
Crea las tablas necesarias, puebla permisos y asigna permisos a roles.
"""
import os
import sys
from dotenv import load_dotenv
load_dotenv()

# Agregar ruta del proyecto
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from utils.database_connector import DatabaseConnector
from models.relational_models import RelationalModels

def main():
    print("=" * 60)
    print("CONFIGURACI\u00d3N DE SISTEMA DE ROLES Y PERMISOS")
    print("=" * 60)
    
    connector = DatabaseConnector()
    conn = connector.connect_mysql()
    
    if not conn:
        print("\u274c Error: No se pudo conectar a MySQL")
        return 1
    
    try:
        print("\n1\ufe0f\u20e3  Creando tablas de roles y permisos...")
        RelationalModels.create_tables(conn)
        
        print("\n2\ufe0f\u20e3  Poblando permisos del sistema...")
        RelationalModels.seed_permisos(conn)
        
        print("\n3\ufe0f\u20e3  Asignando permisos a roles...")
        RelationalModels.asignar_permisos_roles(conn)
        
        # Mostrar resumen de configuraci\u00f3n
        print("\n" + "=" * 60)
        print("RESUMEN DE CONFIGURACION")
        print("=" * 60)
        
        cursor = conn.cursor()
        
        # Contar permisos por rol
        print("\n>> Permisos por Rol:")
        for rol in ['gerente', 'farmaceutico', 'investigador']:
            cursor.execute("""
                SELECT COUNT(*) FROM rol_permiso WHERE rol = %s
            """, (rol,))
            count = cursor.fetchone()[0]
            
            cursor.execute("""
                SELECT p.nombre FROM rol_permiso rp
                JOIN permisos p ON rp.permiso_id = p.id
                WHERE rp.rol = %s
                ORDER BY p.nombre
            """, (rol,))
            permisos = [row[0] for row in cursor.fetchall()]
            
            print(f"\n  {rol.upper()}: {count} permisos")
            for permiso in permisos:
                print(f"    \u2713 {permiso}")
        
        # Mostrar usuarios con sus roles
        print("\n>> Usuarios Configurados:")
        cursor.execute("""
            SELECT id, username, nombre, rol 
            FROM usuarios 
            WHERE activo = TRUE
            ORDER BY rol, username
        """)
        usuarios = cursor.fetchall()
        
        for id, username, nombre, rol in usuarios:
            print(f"  [{id}] {nombre} (@{username}) - Rol: {rol}")
        
        cursor.close()
        
        print("\n" + "=" * 60)
        print("\u2705 Sistema de roles y permisos configurado exitosamente!")
        print("=" * 60)
        
        return 0
        
    except Exception as e:
        print(f"\n\u274c Error durante la configuraci\u00f3n: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        connector.close_all_connections()

if __name__ == '__main__':
    sys.exit(main())
