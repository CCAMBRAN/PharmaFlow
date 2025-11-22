import hashlib
import secrets
from functools import wraps
from mysql.connector import Error
from datetime import datetime

class UserService:
    def __init__(self, db_connector):
        self.db_connector = db_connector
    
    def _hash_password(self, password):
        """Hash seguro de contraseña"""
        salt = secrets.token_hex(16)
        hash_obj = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return f"{salt}${hash_obj.hex()}"
    
    def _verify_password(self, password, hashed_password):
        """Verificar contraseña"""
        try:
            salt, stored_hash = hashed_password.split('$')
            new_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000).hex()
            return secrets.compare_digest(new_hash, stored_hash)
        except:
            return False
    
    def crear_usuario(self, username, password, nombre, rol):
        connection = self.db_connector.connect_mysql()
        if not connection:
            return False, "Error de conexión"
        
        try:
            cursor = connection.cursor()
            
            # Verificar si el usuario ya existe
            cursor.execute("SELECT id FROM usuarios WHERE username = %s", (username,))
            if cursor.fetchone():
                return False, "El usuario ya existe"
            
            # Crear usuario
            password_hash = self._hash_password(password)
            cursor.execute("""
                INSERT INTO usuarios (username, password_hash, nombre, rol)
                VALUES (%s, %s, %s, %s)
            """, (username, password_hash, nombre, rol))
            
            connection.commit()
            return True, "Usuario creado exitosamente"
            
        except Error as e:
            connection.rollback()
            return False, f"Error creando usuario: {e}"
        finally:
            cursor.close()
    
    def autenticar_usuario(self, username, password):
        connection = self.db_connector.connect_mysql()
        if not connection:
            return None
        
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT id, username, password_hash, nombre, rol 
                FROM usuarios 
                WHERE username = %s AND activo = TRUE
            """, (username,))
            
            usuario = cursor.fetchone()
            if usuario and self._verify_password(password, usuario['password_hash']):
                return usuario
            return None
            
        except Error as e:
            print(f"Error autenticando usuario: {e}")
            return None
        finally:
            cursor.close()
    
    def verificar_permiso(self, usuario_id, permiso_nombre):
        """Verificar si un usuario tiene un permiso específico basado en su rol"""
        connection = self.db_connector.connect_mysql()
        if not connection:
            return False
        
        try:
            cursor = connection.cursor()
            
            # Obtener rol del usuario
            cursor.execute("SELECT rol FROM usuarios WHERE id = %s AND activo = TRUE", (usuario_id,))
            result = cursor.fetchone()
            
            if not result:
                return False
            
            rol = result[0]
            
            # Verificar si el rol tiene el permiso
            cursor.execute("""
                SELECT COUNT(*) FROM rol_permiso rp
                JOIN permisos p ON rp.permiso_id = p.id
                WHERE rp.rol = %s AND p.nombre = %s
            """, (rol, permiso_nombre))
            
            count = cursor.fetchone()[0]
            return count > 0
            
        except Error as e:
            print(f"Error verificando permiso: {e}")
            return False
        finally:
            cursor.close()
    
    def obtener_permisos_usuario(self, usuario_id):
        """Obtener lista de todos los permisos de un usuario"""
        connection = self.db_connector.connect_mysql()
        if not connection:
            return []
        
        try:
            cursor = connection.cursor(dictionary=True)
            
            cursor.execute("""
                SELECT p.nombre, p.descripcion, p.recurso, p.accion
                FROM usuarios u
                JOIN rol_permiso rp ON u.rol = rp.rol
                JOIN permisos p ON rp.permiso_id = p.id
                WHERE u.id = %s AND u.activo = TRUE
            """, (usuario_id,))
            
            return cursor.fetchall()
            
        except Error as e:
            print(f"Error obteniendo permisos: {e}")
            return []
        finally:
            cursor.close()
    
    def registrar_accion(self, usuario_id, accion, recurso=None, detalles=None):
        """Registrar acción en auditoría"""
        connection = self.db_connector.connect_mysql()
        if not connection:
            return False
        
        try:
            cursor = connection.cursor()
            cursor.execute("""
                INSERT INTO auditoria (usuario_id, accion, recurso, detalles)
                VALUES (%s, %s, %s, %s)
            """, (usuario_id, accion, recurso, detalles))
            
            connection.commit()
            return True
            
        except Error as e:
            print(f"Error registrando auditoría: {e}")
            return False
        finally:
            cursor.close()
    
    def obtener_auditoria(self, usuario_id=None, limit=50):
        """Obtener registros de auditoría"""
        connection = self.db_connector.connect_mysql()
        if not connection:
            return []
        
        try:
            cursor = connection.cursor(dictionary=True)
            
            if usuario_id:
                cursor.execute("""
                    SELECT a.*, u.username, u.nombre
                    FROM auditoria a
                    JOIN usuarios u ON a.usuario_id = u.id
                    WHERE a.usuario_id = %s
                    ORDER BY a.fecha DESC
                    LIMIT %s
                """, (usuario_id, limit))
            else:
                cursor.execute("""
                    SELECT a.*, u.username, u.nombre
                    FROM auditoria a
                    JOIN usuarios u ON a.usuario_id = u.id
                    ORDER BY a.fecha DESC
                    LIMIT %s
                """, (limit,))
            
            return cursor.fetchall()
            
        except Error as e:
            print(f"Error obteniendo auditoría: {e}")
            return []
        finally:
            cursor.close()
    
    def listar_usuarios(self):
        """Listar todos los usuarios activos"""
        connection = self.db_connector.connect_mysql()
        if not connection:
            return []
        
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT id, username, nombre, email, rol, activo, fecha_creacion
                FROM usuarios
                ORDER BY id
            """)
            return cursor.fetchall()
        except Error as e:
            print(f"Error listando usuarios: {e}")
            return []
        finally:
            cursor.close()
    
    def obtener_usuario_por_id(self, usuario_id):
        """Obtener usuario por ID"""
        connection = self.db_connector.connect_mysql()
        if not connection:
            return None
        
        try:
            cursor = connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT id, username, nombre, email, rol, activo, fecha_creacion
                FROM usuarios
                WHERE id = %s
            """, (usuario_id,))
            return cursor.fetchone()
        except Error as e:
            print(f"Error obteniendo usuario: {e}")
            return None
        finally:
            cursor.close()


def require_permission(permiso_nombre):
    """Decorador para requerir un permiso específico antes de ejecutar una función"""
    def decorator(func):
        @wraps(func)
        def wrapper(self, usuario_id, *args, **kwargs):
            # Verificar permiso
            if hasattr(self, 'db_connector'):
                user_service = UserService(self.db_connector)
                if not user_service.verificar_permiso(usuario_id, permiso_nombre):
                    raise PermissionError(f"Usuario no tiene permiso: {permiso_nombre}")
                
                # Registrar acción en auditoría
                user_service.registrar_accion(
                    usuario_id,
                    f"{func.__name__}",
                    permiso_nombre.split('_')[0],
                    f"Ejecutó {func.__name__} con args: {args[:2] if args else 'sin args'}"
                )
            
            return func(self, usuario_id, *args, **kwargs)
        return wrapper
    return decorator