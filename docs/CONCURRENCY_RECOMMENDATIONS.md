# Recomendaciones de Control de Concurrencia


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
