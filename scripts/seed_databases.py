"""
Script para poblar datos de muestra en todas las bases de datos del proyecto PharmaFlow.
Incluye: MySQL (inventario), MongoDB (ensayos), Redis (sesiones/precios), Neo4j (relaciones).
"""
import os
import sys
from datetime import datetime, timedelta
from dotenv import load_dotenv
load_dotenv()

# Imports para cada BD
import mysql.connector
from pymongo import MongoClient
import redis
from neo4j import GraphDatabase

def poblar_mysql():
    """Poblar datos de muestra en MySQL - Inventario y Transacciones"""
    print("\n=== Poblando MySQL ===")
    try:
        conn = mysql.connector.connect(
            host=os.getenv('MYSQL_HOST', 'localhost'),
            user=os.getenv('MYSQL_USER', 'root'),
            password=os.getenv('MYSQL_PASSWORD', 'black0204'),
            database=os.getenv('MYSQL_DATABASE', 'pharmaflow'),
            port=int(os.getenv('MYSQL_PORT', 3307))
        )
        cursor = conn.cursor()
        
        # Limpiar datos existentes
        cursor.execute("DELETE FROM detalle_venta")
        cursor.execute("DELETE FROM ventas")
        cursor.execute("DELETE FROM lotes")
        cursor.execute("DELETE FROM medicamentos")
        cursor.execute("DELETE FROM usuarios")
        
        # Insertar usuarios
        usuarios = [
            ('carlos_garcia', 'hashed_pass_1', 'Carlos García', 'gerente'),
            ('ana_martinez', 'hashed_pass_2', 'Ana Martínez', 'farmaceutico'),
            ('luis_rodriguez', 'hashed_pass_3', 'Luis Rodríguez', 'investigador'),
            ('maria_lopez', 'hashed_pass_4', 'María López', 'farmaceutico')
        ]
        cursor.executemany(
            "INSERT INTO usuarios (username, password_hash, nombre, rol) VALUES (%s, %s, %s, %s)",
            usuarios
        )
        
        # Insertar medicamentos
        medicamentos = [
            ('Paracetamol 500mg', 'Paracetamol', 'Analgésico y antipirético', 5.50, False),
            ('Ibuprofeno 400mg', 'Ibuprofeno', 'Antiinflamatorio no esteroideo', 8.75, False),
            ('Amoxicilina 500mg', 'Amoxicilina', 'Antibiótico de amplio espectro', 15.00, True),
            ('Omeprazol 20mg', 'Omeprazol', 'Inhibidor de bomba de protones', 12.50, False),
            ('Loratadina 10mg', 'Loratadina', 'Antihistamínico', 6.25, False)
        ]
        cursor.executemany(
            "INSERT INTO medicamentos (nombre, principio_activo, descripcion, precio, requiere_receta) VALUES (%s, %s, %s, %s, %s)",
            medicamentos
        )
        
        # Insertar lotes
        lotes = [
            (1, 'LOTE-2024-001', 500, 0, '2026-01-15', 4.50, 'Farmacéutica ABC'),
            (1, 'LOTE-2024-002', 300, 0, '2026-06-01', 4.50, 'Farmacéutica ABC'),
            (2, 'LOTE-2024-003', 400, 0, '2026-02-20', 7.00, 'Laboratorios XYZ'),
            (3, 'LOTE-2024-004', 200, 0, '2025-09-10', 12.00, 'BioPharm Inc'),
            (4, 'LOTE-2024-005', 350, 0, '2026-04-05', 10.00, 'Genéricos SA'),
            (5, 'LOTE-2024-006', 250, 0, '2026-05-12', 5.00, 'FarmaPlus')
        ]
        cursor.executemany(
            "INSERT INTO lotes (medicamento_id, numero_lote, cantidad, cantidad_reservada, fecha_caducidad, precio_compra, proveedor) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            lotes
        )
        
        # Insertar ventas de muestra
        ventas = [
            (1, 55.00, 'completada'),
            (2, 87.50, 'completada'),
            (1, 150.00, 'completada')
        ]
        cursor.executemany(
            "INSERT INTO ventas (usuario_id, total, estado) VALUES (%s, %s, %s)",
            ventas
        )
        
        # Insertar detalles de venta
        detalles = [
            (1, 1, 10, 5.50),
            (2, 3, 10, 8.75),
            (3, 4, 10, 15.00)
        ]
        cursor.executemany(
            "INSERT INTO detalle_venta (venta_id, lote_id, cantidad, precio_unitario) VALUES (%s, %s, %s, %s)",
            detalles
        )
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("✅ MySQL poblado exitosamente")
        print(f"   - {len(usuarios)} usuarios")
        print(f"   - {len(medicamentos)} medicamentos")
        print(f"   - {len(lotes)} lotes")
        print(f"   - {len(ventas)} ventas")
        return True
    except Exception as e:
        print(f"❌ Error poblando MySQL: {e}")
        return False

def poblar_mongodb():
    """Poblar datos de muestra en MongoDB - Ensayos Clínicos"""
    print("\n=== Poblando MongoDB ===")
    try:
        uri = os.getenv('MONGODB_URI')
        client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        db = client[os.getenv('MONGODB_DATABASE', 'pharmaflow')]
        
        # Limpiar colección
        db.ensayos_clinicos.drop()
        
        # Insertar ensayos clínicos de muestra
        ensayos = [
            {
                "codigo_ensayo": "EC-2024-001",
                "medicamento": "Amoxicilina 500mg",
                "fase": "Fase III",
                "fecha_inicio": datetime(2024, 1, 15),
                "fecha_fin": datetime(2024, 12, 15),
                "investigador_principal": "Dr. Luis Rodríguez",
                "estado": "En progreso",
                "participantes": 150,
                "resultados": {
                    "efectividad": 0.87,
                    "efectos_secundarios": ["Náuseas leves", "Dolor de cabeza"],
                    "notas": "Resultados preliminares positivos"
                },
                "observaciones": [
                    {
                        "fecha": datetime(2024, 3, 1),
                        "descripcion": "Primer seguimiento - 85% adherencia al tratamiento"
                    },
                    {
                        "fecha": datetime(2024, 6, 1),
                        "descripcion": "Seguimiento intermedio - Efectividad confirmada"
                    }
                ]
            },
            {
                "codigo_ensayo": "EC-2024-002",
                "medicamento": "Ibuprofeno 400mg",
                "fase": "Fase II",
                "fecha_inicio": datetime(2024, 3, 1),
                "fecha_fin": datetime(2025, 3, 1),
                "investigador_principal": "Dra. María López",
                "estado": "En progreso",
                "participantes": 80,
                "resultados": {
                    "efectividad": 0.92,
                    "efectos_secundarios": ["Irritación gástrica leve"],
                    "notas": "Excelente tolerabilidad"
                },
                "observaciones": [
                    {
                        "fecha": datetime(2024, 5, 15),
                        "descripcion": "Primer corte - Sin eventos adversos graves"
                    }
                ]
            },
            {
                "codigo_ensayo": "EC-2023-015",
                "medicamento": "Omeprazol 20mg",
                "fase": "Fase IV",
                "fecha_inicio": datetime(2023, 6, 1),
                "fecha_fin": datetime(2024, 6, 1),
                "investigador_principal": "Dr. Carlos García",
                "estado": "Completado",
                "participantes": 200,
                "resultados": {
                    "efectividad": 0.95,
                    "efectos_secundarios": ["Diarrea ocasional", "Dolor abdominal"],
                    "notas": "Estudio completado exitosamente. Medicamento aprobado."
                },
                "observaciones": [
                    {
                        "fecha": datetime(2023, 9, 1),
                        "descripcion": "Seguimiento a 3 meses - Resultados excelentes"
                    },
                    {
                        "fecha": datetime(2024, 1, 1),
                        "descripcion": "Seguimiento a 6 meses - Confirma eficacia a largo plazo"
                    },
                    {
                        "fecha": datetime(2024, 6, 1),
                        "descripcion": "Estudio finalizado - Documentación completa"
                    }
                ]
            }
        ]
        
        result = db.ensayos_clinicos.insert_many(ensayos)
        
        # Crear índices
        db.ensayos_clinicos.create_index("codigo_ensayo", unique=True)
        db.ensayos_clinicos.create_index("medicamento")
        db.ensayos_clinicos.create_index("estado")
        
        client.close()
        
        print("✅ MongoDB poblado exitosamente")
        print(f"   - {len(ensayos)} ensayos clínicos")
        print(f"   - Índices creados en: codigo_ensayo, medicamento, estado")
        return True
    except Exception as e:
        print(f"❌ Error poblando MongoDB: {e}")
        return False

def poblar_redis():
    """Poblar datos de muestra en Redis - Tokens y Precios"""
    print("\n=== Poblando Redis ===")
    try:
        r = redis.Redis(
            host=os.getenv('REDIS_HOST', 'localhost'),
            port=int(os.getenv('REDIS_PORT', 6379)),
            password=os.getenv('REDIS_PASSWORD', None),
            db=int(os.getenv('REDIS_DB', 0)),
            decode_responses=True
        )
        
        # Limpiar datos de prueba anteriores
        r.flushdb()
        
        # Tokens de sesión (con expiración de 1 hora)
        sesiones = [
            ('session:token_abc123', {'user_id': '1', 'username': 'carlos@pharmaflow.com', 'role': 'Gerente', 'login_time': datetime.now().isoformat()}),
            ('session:token_def456', {'user_id': '2', 'username': 'ana@pharmaflow.com', 'role': 'Farmacéutico', 'login_time': datetime.now().isoformat()}),
            ('session:token_ghi789', {'user_id': '3', 'username': 'luis@pharmaflow.com', 'role': 'Investigador', 'login_time': datetime.now().isoformat()})
        ]
        
        for key, data in sesiones:
            r.hset(key, mapping=data)
            r.expire(key, 3600)  # 1 hora
        
        # Precios en cache (para cálculos rápidos de importación)
        precios = {
            'price:medicamento:1': '5.50',
            'price:medicamento:2': '8.75',
            'price:medicamento:3': '15.00',
            'price:medicamento:4': '12.50',
            'price:medicamento:5': '6.25'
        }
        
        for key, value in precios.items():
            r.set(key, value)
            r.expire(key, 86400)  # 24 horas
        
        # Lista de actividad reciente
        r.lpush('recent_activities', 
                'Usuario carlos@pharmaflow.com inició sesión',
                'Venta #001 procesada - Total: $55.00',
                'Usuario ana@pharmaflow.com registró venta #002',
                'Nuevo lote LOTE-2024-007 agregado al inventario',
                'Usuario luis@pharmaflow.com consultó ensayo EC-2024-001')
        
        # Contador de ventas del día
        r.set('sales:count:today', 15)
        r.set('sales:total:today', 1250.75)
        
        print("✅ Redis poblado exitosamente")
        print(f"   - {len(sesiones)} sesiones activas (expire: 1h)")
        print(f"   - {len(precios)} precios en cache (expire: 24h)")
        print(f"   - Actividad reciente y contadores configurados")
        return True
    except Exception as e:
        print(f"❌ Error poblando Redis: {e}")
        return False

def poblar_neo4j():
    """Poblar datos de muestra en Neo4j - Relaciones entre Componentes"""
    print("\n=== Poblando Neo4j ===")
    try:
        uri = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
        user = os.getenv('NEO4J_USER', 'neo4j')
        password = os.getenv('NEO4J_PASSWORD', 'black0204')
        
        driver = GraphDatabase.driver(uri, auth=(user, password))
        
        with driver.session(database='neo4j') as session:
            # Limpiar base de datos
            session.run("MATCH (n) DETACH DELETE n")
            
            # Crear Compuestos Químicos
            session.run("""
                CREATE (c1:Compuesto {id: 'C001', nombre: 'Ácido acetilsalicílico', formula: 'C9H8O4'})
                CREATE (c2:Compuesto {id: 'C002', nombre: 'Paracetamol base', formula: 'C8H9NO2'})
                CREATE (c3:Compuesto {id: 'C003', nombre: 'Ibuprofeno base', formula: 'C13H18O2'})
                CREATE (c4:Compuesto {id: 'C004', nombre: 'Amoxicilina trihidrato', formula: 'C16H19N3O5S·3H2O'})
                CREATE (c5:Compuesto {id: 'C005', nombre: 'Omeprazol base', formula: 'C17H19N3O3S'})
            """)
            
            # Crear Principios Activos
            session.run("""
                CREATE (p1:PrincipioActivo {id: 'PA001', nombre: 'Paracetamol', tipo: 'Analgésico'})
                CREATE (p2:PrincipioActivo {id: 'PA002', nombre: 'Ibuprofeno', tipo: 'AINE'})
                CREATE (p3:PrincipioActivo {id: 'PA003', nombre: 'Amoxicilina', tipo: 'Antibiótico'})
                CREATE (p4:PrincipioActivo {id: 'PA004', nombre: 'Omeprazol', tipo: 'IBP'})
                CREATE (p5:PrincipioActivo {id: 'PA005', nombre: 'Loratadina', tipo: 'Antihistamínico'})
            """)
            
            # Crear Medicamentos
            session.run("""
                CREATE (m1:Medicamento {id: 'M001', nombre: 'Paracetamol 500mg', dosis: '500mg'})
                CREATE (m2:Medicamento {id: 'M002', nombre: 'Ibuprofeno 400mg', dosis: '400mg'})
                CREATE (m3:Medicamento {id: 'M003', nombre: 'Amoxicilina 500mg', dosis: '500mg'})
                CREATE (m4:Medicamento {id: 'M004', nombre: 'Omeprazol 20mg', dosis: '20mg'})
                CREATE (m5:Medicamento {id: 'M005', nombre: 'Loratadina 10mg', dosis: '10mg'})
            """)
            
            # Relaciones: Compuesto -> PrincipioActivo
            session.run("""
                MATCH (c:Compuesto {id: 'C002'}), (p:PrincipioActivo {id: 'PA001'})
                CREATE (c)-[:ES_BASE_DE]->(p)
            """)
            session.run("""
                MATCH (c:Compuesto {id: 'C003'}), (p:PrincipioActivo {id: 'PA002'})
                CREATE (c)-[:ES_BASE_DE]->(p)
            """)
            session.run("""
                MATCH (c:Compuesto {id: 'C004'}), (p:PrincipioActivo {id: 'PA003'})
                CREATE (c)-[:ES_BASE_DE]->(p)
            """)
            session.run("""
                MATCH (c:Compuesto {id: 'C005'}), (p:PrincipioActivo {id: 'PA004'})
                CREATE (c)-[:ES_BASE_DE]->(p)
            """)
            
            # Relaciones: PrincipioActivo -> Medicamento
            session.run("""
                MATCH (p:PrincipioActivo {id: 'PA001'}), (m:Medicamento {id: 'M001'})
                CREATE (p)-[:CONTIENE {concentracion: '500mg'}]->(m)
            """)
            session.run("""
                MATCH (p:PrincipioActivo {id: 'PA002'}), (m:Medicamento {id: 'M002'})
                CREATE (p)-[:CONTIENE {concentracion: '400mg'}]->(m)
            """)
            session.run("""
                MATCH (p:PrincipioActivo {id: 'PA003'}), (m:Medicamento {id: 'M003'})
                CREATE (p)-[:CONTIENE {concentracion: '500mg'}]->(m)
            """)
            session.run("""
                MATCH (p:PrincipioActivo {id: 'PA004'}), (m:Medicamento {id: 'M004'})
                CREATE (p)-[:CONTIENE {concentracion: '20mg'}]->(m)
            """)
            session.run("""
                MATCH (p:PrincipioActivo {id: 'PA005'}), (m:Medicamento {id: 'M005'})
                CREATE (p)-[:CONTIENE {concentracion: '10mg'}]->(m)
            """)
            
            # Interacciones medicamentosas
            session.run("""
                MATCH (m1:Medicamento {id: 'M002'}), (m2:Medicamento {id: 'M004'})
                CREATE (m1)-[:INTERACTUA_CON {severidad: 'Moderada', descripcion: 'El ibuprofeno puede reducir la eficacia del omeprazol'}]->(m2)
            """)
            session.run("""
                MATCH (m1:Medicamento {id: 'M003'}), (m2:Medicamento {id: 'M005'})
                CREATE (m1)-[:INTERACTUA_CON {severidad: 'Leve', descripcion: 'Posible aumento de efectos secundarios gastrointestinales'}]->(m2)
            """)
            
            # Contar nodos y relaciones
            result = session.run("MATCH (n) RETURN count(n) as count")
            node_count = result.single()["count"]
            
            result = session.run("MATCH ()-[r]->() RETURN count(r) as count")
            rel_count = result.single()["count"]
        
        driver.close()
        
        print("✅ Neo4j poblado exitosamente")
        print(f"   - {node_count} nodos creados (Compuestos, Principios, Medicamentos)")
        print(f"   - {rel_count} relaciones (ES_BASE_DE, CONTIENE, INTERACTUA_CON)")
        return True
    except Exception as e:
        print(f"❌ Error poblando Neo4j: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("=" * 60)
    print("POBLANDO DATOS DE MUESTRA - PHARMAFLOW SOLUTIONS")
    print("=" * 60)
    
    resultados = {
        'MySQL': poblar_mysql(),
        'MongoDB': poblar_mongodb(),
        'Redis': poblar_redis(),
        'Neo4j': poblar_neo4j()
    }
    
    print("\n" + "=" * 60)
    print("RESUMEN")
    print("=" * 60)
    for db, success in resultados.items():
        status = "✅ OK" if success else "❌ FALLÓ"
        print(f"{db}: {status}")
    
    all_success = all(resultados.values())
    if all_success:
        print("\n🎉 Todas las bases de datos fueron pobladas exitosamente!")
    else:
        print("\n⚠️  Algunas bases de datos no pudieron ser pobladas. Revisar errores arriba.")
    
    return 0 if all_success else 1

if __name__ == '__main__':
    sys.exit(main())
