"""
Script comparativo de control de concurrencia.
Compara rendimiento y comportamiento de metodos optimista vs pesimista.
"""
import os
import sys
import threading
import time
from dotenv import load_dotenv
load_dotenv()

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from utils.database_connector import DatabaseConnector
from services.inventory_service import InventoryService

def preparar_lote(lote_id, cantidad_inicial):
    """Preparar lote con stock inicial"""
    connector = DatabaseConnector()
    conn = connector.connect_mysql()
    cursor = conn.cursor()
    cursor.execute("UPDATE lotes SET cantidad = %s, version = 1 WHERE id = %s", 
                  (cantidad_inicial, lote_id))
    conn.commit()
    cursor.close()
    connector.close_all_connections()

def obtener_stock(lote_id):
    connector = DatabaseConnector()
    conn = connector.connect_mysql()
    cursor = conn.cursor()
    cursor.execute("SELECT cantidad, version FROM lotes WHERE id = %s", (lote_id,))
    result = cursor.fetchone()
    cursor.close()
    connector.close_all_connections()
    return result

def benchmark_optimista(lote_id, num_usuarios, cantidad_por_usuario):
    """Benchmark del metodo optimista"""
    resultados = []
    lock = threading.Lock()
    
    def venta_optimista(usuario_id):
        connector = DatabaseConnector()
        service = InventoryService(connector)
        
        # Obtener version actual
        _, version = obtener_stock(lote_id)
        
        inicio = time.time()
        exito, msg = service.vender_medicamento_optimista(lote_id, cantidad_por_usuario, usuario_id, version)
        fin = time.time()
        
        with lock:
            resultados.append({
                'usuario_id': usuario_id,
                'exito': exito,
                'tiempo': fin - inicio
            })
        
        connector.close_all_connections()
    
    # Ejecutar
    hilos = []
    inicio_total = time.time()
    
    for i in range(num_usuarios):
        t = threading.Thread(target=venta_optimista, args=(i+1,))
        hilos.append(t)
        t.start()
    
    for t in hilos:
        t.join()
    
    fin_total = time.time()
    
    exitosos = sum(1 for r in resultados if r['exito'])
    tiempos = [r['tiempo'] for r in resultados]
    
    return {
        'exitosos': exitosos,
        'fallidos': num_usuarios - exitosos,
        'tiempo_total': fin_total - inicio_total,
        'tiempo_promedio': sum(tiempos) / len(tiempos),
        'tiempo_min': min(tiempos),
        'tiempo_max': max(tiempos)
    }

def benchmark_pesimista(lote_id, num_usuarios, cantidad_por_usuario):
    """Benchmark del metodo pesimista"""
    resultados = []
    lock = threading.Lock()
    
    def venta_pesimista(usuario_id):
        connector = DatabaseConnector()
        service = InventoryService(connector)
        
        inicio = time.time()
        exito, msg = service.vender_medicamento_pesimista(lote_id, cantidad_por_usuario, usuario_id)
        fin = time.time()
        
        with lock:
            resultados.append({
                'usuario_id': usuario_id,
                'exito': exito,
                'tiempo': fin - inicio
            })
        
        connector.close_all_connections()
    
    # Ejecutar
    hilos = []
    inicio_total = time.time()
    
    for i in range(num_usuarios):
        t = threading.Thread(target=venta_pesimista, args=(i+1,))
        hilos.append(t)
        t.start()
    
    for t in hilos:
        t.join()
    
    fin_total = time.time()
    
    exitosos = sum(1 for r in resultados if r['exito'])
    tiempos = [r['tiempo'] for r in resultados]
    
    return {
        'exitosos': exitosos,
        'fallidos': num_usuarios - exitosos,
        'tiempo_total': fin_total - inicio_total,
        'tiempo_promedio': sum(tiempos) / len(tiempos),
        'tiempo_min': min(tiempos),
        'tiempo_max': max(tiempos)
    }

def test_comparativo_baja_contension():
    """
    Escenario 1: Baja contencion
    Pocos usuarios, stock suficiente
    """
    print("\n" + "=" * 70)
    print("ESCENARIO 1: BAJA CONTENCION (3 usuarios, stock suficiente)")
    print("=" * 70)
    
    lote_opt = 1
    lote_pes = 2
    num_usuarios = 3
    cantidad = 5
    stock_inicial = 100
    
    # Preparar lotes
    preparar_lote(lote_opt, stock_inicial)
    preparar_lote(lote_pes, stock_inicial)
    
    print(f"\nConfiguracion: {num_usuarios} usuarios, {cantidad} unidades c/u, stock: {stock_inicial}")
    
    # Test optimista
    print("\n>> Ejecutando metodo OPTIMISTA...")
    res_opt = benchmark_optimista(lote_opt, num_usuarios, cantidad)
    
    # Test pesimista
    print(">> Ejecutando metodo PESIMISTA...")
    res_pes = benchmark_pesimista(lote_pes, num_usuarios, cantidad)
    
    # Comparar
    print("\n" + "-" * 70)
    print("RESULTADOS:")
    print("-" * 70)
    print(f"{'Metrica':<30} {'Optimista':>15} {'Pesimista':>15} {'Ganador':>10}")
    print("-" * 70)
    
    print(f"{'Ventas exitosas':<30} {res_opt['exitosos']:>15} {res_pes['exitosos']:>15} ", end="")
    if res_opt['exitosos'] > res_pes['exitosos']:
        print("OPT")
    elif res_pes['exitosos'] > res_opt['exitosos']:
        print("PES")
    else:
        print("EMPATE")
    
    print(f"{'Ventas fallidas':<30} {res_opt['fallidos']:>15} {res_pes['fallidos']:>15} ", end="")
    if res_opt['fallidos'] < res_pes['fallidos']:
        print("OPT")
    elif res_pes['fallidos'] < res_opt['fallidos']:
        print("PES")
    else:
        print("EMPATE")
    
    print(f"{'Tiempo total (s)':<30} {res_opt['tiempo_total']:>15.4f} {res_pes['tiempo_total']:>15.4f} ", end="")
    if res_opt['tiempo_total'] < res_pes['tiempo_total']:
        print("OPT")
    else:
        print("PES")
    
    print(f"{'Tiempo promedio (s)':<30} {res_opt['tiempo_promedio']:>15.4f} {res_pes['tiempo_promedio']:>15.4f} ", end="")
    if res_opt['tiempo_promedio'] < res_pes['tiempo_promedio']:
        print("OPT")
    else:
        print("PES")
    
    print(f"{'Tiempo max (s)':<30} {res_opt['tiempo_max']:>15.4f} {res_pes['tiempo_max']:>15.4f} ", end="")
    if res_opt['tiempo_max'] < res_pes['tiempo_max']:
        print("OPT")
    else:
        print("PES")

def test_comparativo_alta_contension():
    """
    Escenario 2: Alta contencion
    Muchos usuarios compitiendo por el mismo recurso
    """
    print("\n" + "=" * 70)
    print("ESCENARIO 2: ALTA CONTENCION (10 usuarios, mismo lote)")
    print("=" * 70)
    
    lote_opt = 3
    lote_pes = 4
    num_usuarios = 10
    cantidad = 2
    stock_inicial = 50
    
    # Preparar lotes
    preparar_lote(lote_opt, stock_inicial)
    preparar_lote(lote_pes, stock_inicial)
    
    print(f"\nConfiguracion: {num_usuarios} usuarios, {cantidad} unidades c/u, stock: {stock_inicial}")
    
    # Test optimista
    print("\n>> Ejecutando metodo OPTIMISTA...")
    res_opt = benchmark_optimista(lote_opt, num_usuarios, cantidad)
    
    # Test pesimista
    print(">> Ejecutando metodo PESIMISTA...")
    res_pes = benchmark_pesimista(lote_pes, num_usuarios, cantidad)
    
    # Comparar
    print("\n" + "-" * 70)
    print("RESULTADOS:")
    print("-" * 70)
    print(f"{'Metrica':<30} {'Optimista':>15} {'Pesimista':>15} {'Ganador':>10}")
    print("-" * 70)
    
    print(f"{'Ventas exitosas':<30} {res_opt['exitosos']:>15} {res_pes['exitosos']:>15} ", end="")
    if res_opt['exitosos'] > res_pes['exitosos']:
        print("OPT")
    elif res_pes['exitosos'] > res_opt['exitosos']:
        print("PES")
    else:
        print("EMPATE")
    
    print(f"{'Tiempo total (s)':<30} {res_opt['tiempo_total']:>15.4f} {res_pes['tiempo_total']:>15.4f} ", end="")
    if res_opt['tiempo_total'] < res_pes['tiempo_total']:
        print("OPT")
    else:
        print("PES")
    
    print(f"{'Latencia max (s)':<30} {res_opt['tiempo_max']:>15.4f} {res_pes['tiempo_max']:>15.4f} ", end="")
    if res_opt['tiempo_max'] < res_pes['tiempo_max']:
        print("OPT")
    else:
        print("PES")
    
    variacion_opt = res_opt['tiempo_max'] - res_opt['tiempo_min']
    variacion_pes = res_pes['tiempo_max'] - res_pes['tiempo_min']
    
    print(f"{'Variacion tiempo (s)':<30} {variacion_opt:>15.4f} {variacion_pes:>15.4f} ", end="")
    if variacion_opt < variacion_pes:
        print("OPT")
    else:
        print("PES")

def test_comparativo_stock_limitado():
    """
    Escenario 3: Stock limitado
    Mas demanda que oferta
    """
    print("\n" + "=" * 70)
    print("ESCENARIO 3: STOCK LIMITADO (15 usuarios, stock para 5)")
    print("=" * 70)
    
    lote_opt = 5
    lote_pes = 6
    num_usuarios = 15
    cantidad = 3
    stock_inicial = 15  # Solo alcanza para 5 ventas
    
    # Preparar lotes
    preparar_lote(lote_opt, stock_inicial)
    preparar_lote(lote_pes, stock_inicial)
    
    print(f"\nConfiguracion: {num_usuarios} usuarios, {cantidad} unidades c/u")
    print(f"Stock: {stock_inicial} (solo alcanza para {stock_inicial // cantidad} ventas)")
    
    # Test optimista
    print("\n>> Ejecutando metodo OPTIMISTA...")
    res_opt = benchmark_optimista(lote_opt, num_usuarios, cantidad)
    
    # Test pesimista
    print(">> Ejecutando metodo PESIMISTA...")
    res_pes = benchmark_pesimista(lote_pes, num_usuarios, cantidad)
    
    # Verificar consistencia
    stock_opt_final, _ = obtener_stock(lote_opt)
    stock_pes_final, _ = obtener_stock(lote_pes)
    
    print("\n" + "-" * 70)
    print("RESULTADOS:")
    print("-" * 70)
    print(f"{'Metrica':<30} {'Optimista':>15} {'Pesimista':>15}")
    print("-" * 70)
    print(f"{'Ventas exitosas':<30} {res_opt['exitosos']:>15} {res_pes['exitosos']:>15}")
    print(f"{'Ventas rechazadas':<30} {res_opt['fallidos']:>15} {res_pes['fallidos']:>15}")
    print(f"{'Stock final':<30} {stock_opt_final:>15} {stock_pes_final:>15}")
    print(f"{'Tiempo total (s)':<30} {res_opt['tiempo_total']:>15.4f} {res_pes['tiempo_total']:>15.4f}")
    
    # Verificar que no hubo overselling
    vendido_opt = stock_inicial - stock_opt_final
    vendido_pes = stock_inicial - stock_pes_final
    
    print(f"{'Unidades vendidas':<30} {vendido_opt:>15} {vendido_pes:>15}")
    
    print("\n>> Verificacion de integridad:")
    if vendido_opt == res_opt['exitosos'] * cantidad:
        print("   [OK] Optimista: Stock consistente con ventas")
    else:
        print("   [ERROR] Optimista: Inconsistencia detectada!")
    
    if vendido_pes == res_pes['exitosos'] * cantidad:
        print("   [OK] Pesimista: Stock consistente con ventas")
    else:
        print("   [ERROR] Pesimista: Inconsistencia detectada!")

def generar_recomendaciones():
    """Generar documento de recomendaciones"""
    print("\n" + "=" * 70)
    print("RECOMENDACIONES DE USO")
    print("=" * 70)
    
    recomendaciones = """
CUANDO USAR CONTROL OPTIMISTA:
-------------------------------
✓ Baja probabilidad de conflictos (diferentes recursos)
✓ Operaciones de lectura frecuentes
✓ Transacciones cortas y rapidas
✓ Necesidad de alto throughput
✓ Costo de rollback/reintento es bajo
✓ Aplicaciones web con muchos usuarios simultaneos

Ventajas:
  - Mayor rendimiento en baja contencion
  - No bloquea recursos durante lectura
  - Mejor escalabilidad horizontal
  - Menos deadlocks

Desventajas:
  - Requiere logica de reintento en cliente
  - Puede haber muchos fallos en alta contencion
  - Usuario puede experimentar errores


CUANDO USAR CONTROL PESIMISTA:
-------------------------------
✓ Alta probabilidad de conflictos (mismo recurso)
✓ Transacciones largas o complejas
✓ Costo de rollback/reintento es alto
✓ Garantia de exito es critica
✓ Operaciones de escritura frecuentes
✓ Procesos batch o carga masiva

Ventajas:
  - Garantiza exito de primera transaccion
  - No requiere reintentos
  - Logica mas simple en aplicacion
  - Previsibilidad de resultados

Desventajas:
  - Menor throughput en alta concurrencia
  - Posibles deadlocks
  - Bloqueos pueden causar esperas largas
  - Escalabilidad limitada


RECOMENDACION PARA PHARMAFLOW:
-------------------------------
>> VENTAS (vender_medicamento):
   - Usar PESIMISTA para garantizar integridad de stock
   - Transacciones criticas que no deben fallar
   - Evitar overselling en temporadas altas

>> CONSULTAS (consultar_stock):
   - Sin bloqueos, lectura simple
   - Snapshot del momento de consulta

>> ACTUALIZACIONES DE LOTE (recibir_mercancia):
   - Usar OPTIMISTA si son operaciones espaciadas
   - Usar PESIMISTA si hay multiples almacenistas

>> REPORTES Y ANALYTICS:
   - Lectura sin bloqueos
   - Considerar replicas de lectura para no afectar OLTP


ESTRATEGIA HIBRIDA RECOMENDADA:
-------------------------------
1. Ventas en tiempo real -> PESIMISTA
2. Ajustes de inventario -> OPTIMISTA con reintento
3. Procesos nocturnos -> PESIMISTA
4. APIs publicas -> OPTIMISTA (fallar rapido)
5. Admin interno -> PESIMISTA (garantizar exito)
"""
    
    print(recomendaciones)
    
    # Guardar recomendaciones
    with open('docs/CONCURRENCY_RECOMMENDATIONS.md', 'w', encoding='utf-8') as f:
        f.write("# Recomendaciones de Control de Concurrencia\n\n")
        f.write(recomendaciones)
    
    print("\n>> Recomendaciones guardadas en: docs/CONCURRENCY_RECOMMENDATIONS.md")

def main():
    print("=" * 70)
    print("ANALISIS COMPARATIVO: CONTROL DE CONCURRENCIA")
    print("=" * 70)
    
    try:
        test_comparativo_baja_contension()
        time.sleep(1)
        
        test_comparativo_alta_contension()
        time.sleep(1)
        
        test_comparativo_stock_limitado()
        
        generar_recomendaciones()
        
        print("\n" + "=" * 70)
        print("[OK] ANALISIS COMPLETADO")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
