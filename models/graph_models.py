class GraphModels:
	"""
	Lightweight Neo4j model helpers. Expects a `neo4j.Driver` instance.

	These helpers create nodes and relationships for chemical compounds,
	active principles and medications. They are deliberately small and
	focused to be used by higher-level services.
	"""

	def __init__(self, driver):
		self.driver = driver

	def create_compound(self, compuesto):
		"""Create or update a compound node.

		compuesto: dict with keys `nombre`, `formula`, `propiedades`, `usos`, `efectos`
		"""
		with self.driver.session() as session:
			session.run(
				"""
				MERGE (c:Compuesto {nombre: $nombre})
				SET c.formula = $formula, c.propiedades = $propiedades, c.usos = $usos, c.efectos = $efectos
				RETURN c
				""",
				compuesto
			)

	def relate_compound_to_principio(self, compuesto_nombre, principio_nombre, relacion_data=None):
		relacion_data = relacion_data or {}
		with self.driver.session() as session:
			session.run(
				"""
				MATCH (c:Compuesto {nombre: $compuesto_nombre})
				MERGE (p:PrincipioActivo {nombre: $principio_nombre})
				MERGE (c)-[r:DERIVA_EN]->(p)
				SET r += $props
				RETURN r
				""",
				{'compuesto_nombre': compuesto_nombre, 'principio_nombre': principio_nombre, 'props': relacion_data}
			)

	def relate_principio_to_medicamento(self, principio_nombre, medicamento_nombre, relacion_data=None):
		relacion_data = relacion_data or {}
		with self.driver.session() as session:
			session.run(
				"""
				MATCH (p:PrincipioActivo {nombre: $principio_nombre})
				MERGE (m:Medicamento {nombre: $medicamento_nombre})
				MERGE (p)-[r:COMPONE]->(m)
				SET r += $props
				RETURN r
				""",
				{'principio_nombre': principio_nombre, 'medicamento_nombre': medicamento_nombre, 'props': relacion_data}
			)

	def create_interaction(self, med1, med2, interaccion_data=None):
		interaccion_data = interaccion_data or {}
		with self.driver.session() as session:
			session.run(
				"""
				MATCH (m1:Medicamento {nombre: $med1}), (m2:Medicamento {nombre: $med2})
				MERGE (m1)-[r:INTERACCIONA_CON]->(m2)
				SET r += $props
				RETURN r
				""",
				{'med1': med1, 'med2': med2, 'props': interaccion_data}
			)

