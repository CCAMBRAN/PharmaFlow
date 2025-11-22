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
    def listar_medicamentos(self):
        """Listar todos los medicamentos"""
        connection = self.db_connector.connect_mysql()
        if not connection:
            return []
        
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT id, nombre, principio_activo, precio, stock_minimo
                FROM medicamentos
                ORDER BY nombre
            """)
            return cursor.fetchall()
        except Error as e:
            print(f"Error listando medicamentos: {e}")
            return []
        finally:
            cursor.close()
    
    def obtener_medicamento(self, medicamento_id):
        """Obtener medicamento por ID"""
        connection = self.db_connector.connect_mysql()
        if not connection:
            return None
        
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT id, nombre, principio_activo, precio, stock_minimo
                FROM medicamentos
                WHERE id = %s
            """, (medicamento_id,))
            return cursor.fetchone()
        except Error as e:
            print(f"Error obteniendo medicamento: {e}")
            return None
        finally:
            cursor.close()
    
    def crear_medicamento(self, nombre, principio_activo, precio, stock_minimo):
        """Crear nuevo medicamento"""
        connection = self.db_connector.connect_mysql()
        if not connection:
            return None
        
        try:
            cursor = connection.cursor()
            cursor.execute("""
                INSERT INTO medicamentos (nombre, principio_activo, precio, stock_minimo)
                VALUES (%s, %s, %s, %s)
            """, (nombre, principio_activo, precio, stock_minimo))
            connection.commit()
            return cursor.lastrowid
        except Error as e:
            connection.rollback()
            print(f"Error creando medicamento: {e}")
            return None
        finally:
            cursor.close()
    
    def obtener_stock_total(self, medicamento_id):
        """Obtener stock total de un medicamento"""
        connection = self.db_connector.connect_mysql()
        if not connection:
            return 0
        
        try:
            cursor = connection.cursor()
            cursor.execute("""
                SELECT COALESCE(SUM(cantidad), 0) as total
                FROM lotes
                WHERE medicamento_id = %s
            """, (medicamento_id,))
            result = cursor.fetchone()
            return result[0] if result else 0
        except Error as e:
            print(f"Error obteniendo stock: {e}")
            return 0
        finally:
            cursor.close()
    
    def listar_lotes(self, medicamento_id=None):
        """Listar lotes"""
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
                    WHERE l.medicamento_id = %s
                    ORDER BY l.fecha_vencimiento
                """, (medicamento_id,))
            else:
                cursor.execute("""
                    SELECT l.*, m.nombre as medicamento_nombre
                    FROM lotes l
                    JOIN medicamentos m ON l.medicamento_id = m.id
                    ORDER BY l.fecha_vencimiento
                """)
            return cursor.fetchall()
        except Error as e:
            print(f"Error listando lotes: {e}")
            return []
        finally:
            cursor.close()
    
    def crear_lote(self, medicamento_id, numero_lote, cantidad, fecha_fabricacion, fecha_vencimiento, precio_compra):
        """Crear nuevo lote"""
        connection = self.db_connector.connect_mysql()
        if not connection:
            return None
        
        try:
            cursor = connection.cursor()
            cursor.execute("""
                INSERT INTO lotes (medicamento_id, numero_lote, cantidad, fecha_fabricacion, fecha_vencimiento, precio_compra)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (medicamento_id, numero_lote, cantidad, fecha_fabricacion, fecha_vencimiento, precio_compra))
            connection.commit()
            return cursor.lastrowid
        except Error as e:
            connection.rollback()
            print(f"Error creando lote: {e}")
            return None
        finally:
            cursor.close()
    
    def listar_ventas(self, usuario_id=None):
        """Listar ventas"""
        connection = self.db_connector.connect_mysql()
        if not connection:
            return []
        
        try:
            cursor = connection.cursor(dictionary=True)
            if usuario_id:
                cursor.execute("""
                    SELECT v.*, u.nombre as usuario_nombre
                    FROM ventas v
                    JOIN usuarios u ON v.usuario_id = u.id
                    WHERE v.usuario_id = %s
                    ORDER BY v.fecha DESC
                """, (usuario_id,))
            else:
                cursor.execute("""
                    SELECT v.*, u.nombre as usuario_nombre
                    FROM ventas v
                    JOIN usuarios u ON v.usuario_id = u.id
                    ORDER BY v.fecha DESC
                """)
            return cursor.fetchall()
        except Error as e:
            print(f"Error listando ventas: {e}")
            return []
        finally:
            cursor.close()
    
    def registrar_venta(self, usuario_id, detalles):
        """Registrar nueva venta con detalles"""
        connection = self.db_connector.connect_mysql()
        if not connection:
            return None
        
        try:
            cursor = connection.cursor()
            connection.start_transaction()
            
            # Calcular total
            total = sum(d["cantidad"] * d["precio_unitario"] for d in detalles)
            
            # Insertar venta
            cursor.execute("""
                INSERT INTO ventas (usuario_id, total)
                VALUES (%s, %s)
            """, (usuario_id, total))
            venta_id = cursor.lastrowid
            
            # Insertar detalles
            for detalle in detalles:
                cursor.execute("""
                    INSERT INTO detalle_venta (venta_id, medicamento_id, cantidad, precio_unitario)
                    VALUES (%s, %s, %s, %s)
                """, (venta_id, detalle["medicamento_id"], detalle["cantidad"], detalle["precio_unitario"]))
            
            connection.commit()
            return venta_id
        except Error as e:
            connection.rollback()
            print(f"Error registrando venta: {e}")
            return None
        finally:
            cursor.close()
    
    def obtener_venta(self, venta_id):
        """Obtener detalle de una venta"""
        connection = self.db_connector.connect_mysql()
        if not connection:
            return None
        
        try:
            cursor = connection.cursor(dictionary=True)
            
            # Obtener venta
            cursor.execute("""
                SELECT v.*, u.nombre as usuario_nombre
                FROM ventas v
                JOIN usuarios u ON v.usuario_id = u.id
                WHERE v.id = %s
            """, (venta_id,))
            venta = cursor.fetchone()
            
            if not venta:
                return None
            
            # Obtener detalles
            cursor.execute("""
                SELECT dv.*, m.nombre as medicamento_nombre
                FROM detalle_venta dv
                JOIN medicamentos m ON dv.medicamento_id = m.id
                WHERE dv.venta_id = %s
            """, (venta_id,))
            venta["detalles"] = cursor.fetchall()
            
            return venta
        except Error as e:
            print(f"Error obteniendo venta: {e}")
            return None
        finally:
            cursor.close()
