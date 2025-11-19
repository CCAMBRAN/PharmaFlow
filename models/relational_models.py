class RelationalModels:
    @staticmethod
    def create_tables(mysql_conn):
        cursor = mysql_conn.cursor()
        
        # Tabla de usuarios
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                nombre VARCHAR(100) NOT NULL,
                rol ENUM('gerente', 'farmaceutico', 'investigador') NOT NULL,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                activo BOOLEAN DEFAULT TRUE
            )
        """)
        
        # Tabla de medicamentos
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS medicamentos (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nombre VARCHAR(100) NOT NULL,
                principio_activo VARCHAR(100) NOT NULL,
                descripcion TEXT,
                precio DECIMAL(10,2) NOT NULL,
                requiere_receta BOOLEAN DEFAULT FALSE,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tabla de lotes (con control de concurrencia)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS lotes (
                id INT AUTO_INCREMENT PRIMARY KEY,
                medicamento_id INT NOT NULL,
                numero_lote VARCHAR(50) UNIQUE NOT NULL,
                cantidad INT NOT NULL,
                cantidad_reservada INT DEFAULT 0,
                fecha_caducidad DATE NOT NULL,
                precio_compra DECIMAL(10,2) NOT NULL,
                proveedor VARCHAR(100),
                fecha_ingreso TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                version INT DEFAULT 0,  # Para control de concurrencia optimista
                FOREIGN KEY (medicamento_id) REFERENCES medicamentos(id),
                INDEX idx_medicamento (medicamento_id),
                INDEX idx_caducidad (fecha_caducidad)
            )
        """)
        
        # Tabla de ventas
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ventas (
                id INT AUTO_INCREMENT PRIMARY KEY,
                usuario_id INT NOT NULL,
                fecha_venta TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                total DECIMAL(10,2) NOT NULL,
                estado ENUM('pendiente', 'completada', 'cancelada') DEFAULT 'completada',
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
            )
        """)
        
        # Tabla de detalles de venta
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS detalle_venta (
                id INT AUTO_INCREMENT PRIMARY KEY,
                venta_id INT NOT NULL,
                lote_id INT NOT NULL,
                cantidad INT NOT NULL,
                precio_unitario DECIMAL(10,2) NOT NULL,
                FOREIGN KEY (venta_id) REFERENCES ventas(id),
                FOREIGN KEY (lote_id) REFERENCES lotes(id),
                INDEX idx_venta (venta_id),
                INDEX idx_lote (lote_id)
            )
        """)
        
        # Tabla de permisos
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS permisos (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nombre VARCHAR(50) UNIQUE NOT NULL,
                descripcion TEXT,
                recurso VARCHAR(50) NOT NULL,
                accion ENUM('crear', 'leer', 'actualizar', 'eliminar', 'ejecutar') NOT NULL,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_recurso_accion (recurso, accion)
            )
        """)
        
        # Tabla de relación roles-permisos
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rol_permiso (
                id INT AUTO_INCREMENT PRIMARY KEY,
                rol ENUM('gerente', 'farmaceutico', 'investigador') NOT NULL,
                permiso_id INT NOT NULL,
                FOREIGN KEY (permiso_id) REFERENCES permisos(id) ON DELETE CASCADE,
                UNIQUE KEY unique_rol_permiso (rol, permiso_id),
                INDEX idx_rol (rol)
            )
        """)
        
        # Tabla de auditoría de acciones
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS auditoria (
                id INT AUTO_INCREMENT PRIMARY KEY,
                usuario_id INT NOT NULL,
                accion VARCHAR(100) NOT NULL,
                recurso VARCHAR(50),
                detalles TEXT,
                fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
                INDEX idx_usuario (usuario_id),
                INDEX idx_fecha (fecha)
            )
        """)
        
        mysql_conn.commit()
        print("✅ Tablas relacionales creadas/existen")
    
    @staticmethod
    def seed_permisos(mysql_conn):
        """Poblar permisos predefinidos del sistema"""
        cursor = mysql_conn.cursor()
        
        permisos = [
            # Permisos de Inventario
            ('inventario_leer', 'Consultar inventario', 'inventario', 'leer'),
            ('inventario_crear', 'Agregar medicamentos/lotes', 'inventario', 'crear'),
            ('inventario_actualizar', 'Modificar inventario', 'inventario', 'actualizar'),
            ('inventario_eliminar', 'Eliminar del inventario', 'inventario', 'eliminar'),
            
            # Permisos de Ventas
            ('ventas_leer', 'Consultar ventas', 'ventas', 'leer'),
            ('ventas_crear', 'Registrar ventas', 'ventas', 'crear'),
            ('ventas_cancelar', 'Cancelar ventas', 'ventas', 'actualizar'),
            
            # Permisos de Usuarios
            ('usuarios_leer', 'Consultar usuarios', 'usuarios', 'leer'),
            ('usuarios_crear', 'Crear usuarios', 'usuarios', 'crear'),
            ('usuarios_actualizar', 'Modificar usuarios', 'usuarios', 'actualizar'),
            ('usuarios_eliminar', 'Eliminar usuarios', 'usuarios', 'eliminar'),
            
            # Permisos de Ensayos Clínicos
            ('ensayos_leer', 'Consultar ensayos clínicos', 'ensayos', 'leer'),
            ('ensayos_crear', 'Crear ensayos clínicos', 'ensayos', 'crear'),
            ('ensayos_actualizar', 'Actualizar ensayos clínicos', 'ensayos', 'actualizar'),
            
            # Permisos de Consultas Especiales
            ('reportes_generar', 'Generar reportes', 'reportes', 'ejecutar'),
            ('auditoria_leer', 'Ver auditoría', 'auditoria', 'leer'),
        ]
        
        for permiso in permisos:
            cursor.execute("""
                INSERT IGNORE INTO permisos (nombre, descripcion, recurso, accion)
                VALUES (%s, %s, %s, %s)
            """, permiso)
        
        mysql_conn.commit()
        print(f"✅ {len(permisos)} permisos configurados")
    
    @staticmethod
    def asignar_permisos_roles(mysql_conn):
        """Asignar permisos a cada rol según especificaciones del proyecto"""
        cursor = mysql_conn.cursor()
        
        # Limpiar asignaciones anteriores
        cursor.execute("DELETE FROM rol_permiso")
        
        # Obtener IDs de permisos
        cursor.execute("SELECT id, nombre FROM permisos")
        permisos_dict = {nombre: id for id, nombre in cursor.fetchall()}
        
        # Definir permisos por rol según especificaciones
        asignaciones = {
            'gerente': [
                # Gerente: Acceso total a inventario y usuarios
                'inventario_leer', 'inventario_crear', 'inventario_actualizar', 'inventario_eliminar',
                'ventas_leer', 'ventas_crear', 'ventas_cancelar',
                'usuarios_leer', 'usuarios_crear', 'usuarios_actualizar', 'usuarios_eliminar',
                'ensayos_leer', 'ensayos_crear', 'ensayos_actualizar',
                'reportes_generar', 'auditoria_leer'
            ],
            'farmaceutico': [
                # Farmacéutico: Registrar ventas y modificar lotes
                'inventario_leer', 'inventario_actualizar',
                'ventas_leer', 'ventas_crear',
                'ensayos_leer'
            ],
            'investigador': [
                # Investigador: Solo consultar documentos NoSQL y datos relacionales
                'inventario_leer',
                'ventas_leer',
                'ensayos_leer', 'ensayos_crear', 'ensayos_actualizar'
            ]
        }
        
        for rol, permisos in asignaciones.items():
            for permiso_nombre in permisos:
                if permiso_nombre in permisos_dict:
                    cursor.execute("""
                        INSERT INTO rol_permiso (rol, permiso_id)
                        VALUES (%s, %s)
                    """, (rol, permisos_dict[permiso_nombre]))
        
        mysql_conn.commit()
        
        # Mostrar resumen
        for rol in asignaciones:
            cursor.execute("""
                SELECT COUNT(*) FROM rol_permiso WHERE rol = %s
            """, (rol,))
            count = cursor.fetchone()[0]
            print(f"  - {rol}: {count} permisos asignados")
        
        print("✅ Permisos asignados a roles")