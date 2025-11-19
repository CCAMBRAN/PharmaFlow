import mysql.connector
from mysql.connector import Error

class InventoryService:
    def __init__(self, db_connector):
        self.db_connector = db_connector
    
    # Control de concurrencia PESIMISTA (con LOCK)
    def vender_medicamento_pesimista(self, lote_id, cantidad, usuario_id):
        connection = self.db_connector.connect_mysql()
        if not connection:
            return False, "Error de conexión"
        
        try:
            cursor = connection.cursor()
            
            # Iniciar transacción
            connection.start_transaction()
            
            # Bloquear el registro para escritura (LOCK PESIMISTA)
            cursor.execute("""
                SELECT cantidad, version FROM lotes 
                WHERE id = %s FOR UPDATE
            """, (lote_id,))
            
            result = cursor.fetchone()
            if not result:
                connection.rollback()
                return False, "Lote no encontrado"
            
            stock_actual, version = result
            
            if stock_actual < cantidad:
                connection.rollback()
                return False, "Stock insuficiente"
            
            # Actualizar stock
            nuevo_stock = stock_actual - cantidad
            cursor.execute("""
                UPDATE lotes 
                SET cantidad = %s 
                WHERE id = %s
            """, (nuevo_stock, lote_id))
            
            # Registrar venta
            cursor.execute("""
                INSERT INTO ventas (usuario_id, total) 
                VALUES (%s, 0)
            """, (usuario_id,))
            venta_id = cursor.lastrowid
            
            # Obtener precio del medicamento
            cursor.execute("""
                SELECT m.precio FROM lotes l
                JOIN medicamentos m ON l.medicamento_id = m.id
                WHERE l.id = %s
            """, (lote_id,))
            precio = cursor.fetchone()[0]
            
            # Registrar detalle de venta
            cursor.execute("""
                INSERT INTO detalle_venta (venta_id, lote_id, cantidad, precio_unitario)
                VALUES (%s, %s, %s, %s)
            """, (venta_id, lote_id, cantidad, precio))
            
            # Actualizar total de venta
            total_venta = cantidad * precio
            cursor.execute("""
                UPDATE ventas SET total = %s WHERE id = %s
            """, (total_venta, venta_id))
            
            connection.commit()
            return True, f"Venta registrada. Total: ${total_venta}"
            
        except Error as e:
            connection.rollback()
            return False, f"Error en transacción: {e}"
        finally:
            cursor.close()
    
    # Control de concurrencia OPTIMISTA
    def vender_medicamento_optimista(self, lote_id, cantidad, usuario_id, version_actual):
        connection = self.db_connector.connect_mysql()
        if not connection:
            return False, "Error de conexión"
        
        try:
            cursor = connection.cursor()
            
            # Iniciar transacción
            connection.start_transaction()
            
            # Verificar versión sin bloquear
            cursor.execute("""
                SELECT cantidad, version FROM lotes 
                WHERE id = %s
            """, (lote_id,))
            
            result = cursor.fetchone()
            if not result:
                connection.rollback()
                return False, "Lote no encontrado"
            
            stock_actual, version_bd = result
            
            if version_bd != version_actual:
                connection.rollback()
                return False, "El registro ha sido modificado por otro usuario"
            
            if stock_actual < cantidad:
                connection.rollback()
                return False, "Stock insuficiente"
            
            # Actualizar stock con verificación de versión
            nuevo_stock = stock_actual - cantidad
            cursor.execute("""
                UPDATE lotes 
                SET cantidad = %s, version = version + 1 
                WHERE id = %s AND version = %s
            """, (nuevo_stock, lote_id, version_actual))
            
            if cursor.rowcount == 0:
                connection.rollback()
                return False, "Conflicto de concurrencia - versión modificada"
            
            # Registrar venta (similar al método anterior)
            cursor.execute("""
                INSERT INTO ventas (usuario_id, total) 
                VALUES (%s, 0)
            """, (usuario_id,))
            venta_id = cursor.lastrowid
            
            cursor.execute("""
                SELECT m.precio FROM lotes l
                JOIN medicamentos m ON l.medicamento_id = m.id
                WHERE l.id = %s
            """, (lote_id,))
            precio = cursor.fetchone()[0]
            
            cursor.execute("""
                INSERT INTO detalle_venta (venta_id, lote_id, cantidad, precio_unitario)
                VALUES (%s, %s, %s, %s)
            """, (venta_id, lote_id, cantidad, precio))
            
            total_venta = cantidad * precio
            cursor.execute("""
                UPDATE ventas SET total = %s WHERE id = %s
            """, (total_venta, venta_id))
            
            connection.commit()
            return True, f"Venta registrada. Total: ${total_venta}"
            
        except Error as e:
            connection.rollback()
            return False, f"Error en transacción: {e}"
        finally:
            cursor.close()
    
    def consultar_stock(self, medicamento_id=None):
        connection = self.db_connector.connect_mysql()
        if not connection:
            return []
        
        try:
            cursor = connection.cursor(dictionary=True)
            
            if medicamento_id:
                cursor.execute("""
                    SELECT l.*, m.nombre as medicamento_nombre 
                    FROM lotes l 
                    JOIN medicamentos m ON l.medicamento_id = m.id 
                    WHERE m.id = %s
                """, (medicamento_id,))
            else:
                cursor.execute("""
                    SELECT l.*, m.nombre as medicamento_nombre 
                    FROM lotes l 
                    JOIN medicamentos m ON l.medicamento_id = m.id
                """)
            
            return cursor.fetchall()
        except Error as e:
            print(f"Error consultando stock: {e}")
            return []
        finally:
            cursor.close()