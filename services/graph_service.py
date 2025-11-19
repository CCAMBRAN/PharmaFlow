class GraphService:
    def __init__(self, db_connector):
        self.db_connector = db_connector
        self.driver = self.db_connector.connect_neo4j()
    
    def crear_estructura_quimica(self, compuesto_data):
        if not self.driver:
            return False, "Conexión a Neo4j no disponible"
        
        try:
            with self.driver.session() as session:
                # Crear compuesto químico
                result = session.run("""
                    MERGE (c:Compuesto {nombre: $nombre, formula: $formula})
                    SET c.propiedades = $propiedades,
                        c.usos = $usos,
                        c.efectos = $efectos
                    RETURN c
                """, compuesto_data)
                
                return True, "Compuesto creado/actualizado"
        except Exception as e:
            return False, f"Error creando compuesto: {e}"
    
    def relacionar_compuesto_principio_activo(self, compuesto_nombre, principio_activo_nombre, relacion_data):
        if not self.driver:
            return False, "Conexión a Neo4j no disponible"
        
        try:
            with self.driver.session() as session:
                result = session.run("""
                    MATCH (c:Compuesto {nombre: $compuesto_nombre})
                    MERGE (p:PrincipioActivo {nombre: $principio_nombre})
                    MERGE (c)-[r:DERIVA_EN]->(p)
                    SET r.proporcion = $proporcion,
                        r.metodo_extraccion = $metodo_extraccion,
                        r.eficacia = $eficacia
                    RETURN c, r, p
                """, {
                    'compuesto_nombre': compuesto_nombre,
                    'principio_nombre': principio_activo_nombre,
                    **relacion_data
                })
                
                return True, "Relación creada/actualizada"
        except Exception as e:
            return False, f"Error creando relación: {e}"
    
    def relacionar_principio_medicamento(self, principio_nombre, medicamento_nombre, relacion_data):
        if not self.driver:
            return False, "Conexión a Neo4j no disponible"
        
        try:
            with self.driver.session() as session:
                result = session.run("""
                    MATCH (p:PrincipioActivo {nombre: $principio_nombre})
                    MERGE (m:Medicamento {nombre: $medicamento_nombre})
                    MERGE (p)-[r:COMPONE]->(m)
                    SET r.concentracion = $concentracion,
                        r.funcion = $funcion,
                        r.importancia = $importancia
                    RETURN p, r, m
                """, {
                    'principio_nombre': principio_nombre,
                    'medicamento_nombre': medicamento_nombre,
                    **relacion_data
                })
                
                return True, "Relación medicamento creada/actualizada"
        except Exception as e:
            return False, f"Error creando relación medicamento: {e}"
    
    def crear_interaccion_medicamentosa(self, medicamento1, medicamento2, interaccion_data):
        if not self.driver:
            return False, "Conexión a Neo4j no disponible"
        
        try:
            with self.driver.session() as session:
                result = session.run("""
                    MATCH (m1:Medicamento {nombre: $med1})
                    MATCH (m2:Medicamento {nombre: $med2})
                    MERGE (m1)-[r:INTERACCIONA_CON]->(m2)
                    SET r.gravedad = $gravedad,
                        r.tipo_interaccion = $tipo,
                        r.efecto = $efecto,
                        r.recomendacion = $recomendacion
                    RETURN m1, r, m2
                """, {
                    'med1': medicamento1,
                    'med2': medicamento2,
                    **interaccion_data
                })
                
                return True, "Interacción creada/actualizada"
        except Exception as e:
            return False, f"Error creando interacción: {e}"
    
    def buscar_interacciones_medicamento(self, medicamento_nombre):
        if not self.driver:
            return []
        
        try:
            with self.driver.session() as session:
                result = session.run("""
                    MATCH (m:Medicamento {nombre: $nombre})-[r:INTERACCIONA_CON]->(otro:Medicamento)
                    RETURN otro.nombre as medicamento, r.gravedad as gravedad, 
                           r.tipo_interaccion as tipo, r.efecto as efecto,
                           r.recomendacion as recomendacion
                    ORDER BY r.gravedad DESC
                """, {'nombre': medicamento_nombre})
                
                return [dict(record) for record in result]
        except Exception as e:
            print(f"Error buscando interacciones: {e}")
            return []
    
    def buscar_compuestos_por_medicamento(self, medicamento_nombre):
        if not self.driver:
            return []
        
        try:
            with self.driver.session() as session:
                result = session.run("""
                    MATCH (c:Compuesto)-[:DERIVA_EN]->(p:PrincipioActivo)-[:COMPONE]->(m:Medicamento {nombre: $nombre})
                    RETURN c.nombre as compuesto, p.nombre as principio_activo, 
                           c.propiedades as propiedades, c.efectos as efectos
                """, {'nombre': medicamento_nombre})
                
                return [dict(record) for record in result]
        except Exception as e:
            print(f"Error buscando compuestos: {e}")
            return []