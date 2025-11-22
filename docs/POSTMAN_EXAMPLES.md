# 🧪 Ejemplos Prácticos de Postman - PharmaFlow API

## 📋 Requisitos Previos

1. **Iniciar la API:**
```powershell
python run_api.py
```

2. **Verificar que está corriendo:**
```
GET http://localhost:8000/health
```
Respuesta esperada:
```json
{
  "status": "healthy",
  "timestamp": "2025-11-21T..."
}
```

---

## 🔵 MYSQL - Base de Datos Relacional

### 1. Listar Usuarios
```http
GET http://localhost:8000/api/mysql/usuarios
```

**Respuesta esperada:**
```json
{
  "usuarios": [
    {
      "id": 1,
      "username": "admin",
      "nombre": "Administrador",
      "rol": "gerente",
      "activo": 1
    },
    {
      "id": 2,
      "username": "farmaceutico1",
      "nombre": "Juan Pérez",
      "rol": "farmaceutico",
      "activo": 1
    }
  ]
}
```

### 2. Crear Usuario
```http
POST http://localhost:8000/api/mysql/usuarios
Content-Type: application/json

{
  "nombre_usuario": "maria_garcia",
  "contrasena": "Secure123!",
  "email": "maria.garcia@pharmaflow.com",
  "rol": "farmaceutico"
}
```

**Respuesta esperada:**
```json
{
  "message": "Usuario creado",
  "usuario_id": 5
}
```

### 3. Obtener Usuario por ID
```http
GET http://localhost:8000/api/mysql/usuarios/1
```

**Respuesta esperada:**
```json
{
  "id": 1,
  "username": "admin",
  "nombre": "Administrador",
  "email": "admin@pharmaflow.com",
  "rol": "gerente",
  "activo": 1,
  "fecha_creacion": "2024-11-15T10:30:00"
}
```

### 4. Obtener Permisos de Usuario
```http
GET http://localhost:8000/api/mysql/usuarios/1/permisos
```

**Respuesta esperada:**
```json
{
  "usuario_id": 1,
  "permisos": [
    "inventario_ver",
    "inventario_crear",
    "inventario_actualizar",
    "inventario_eliminar",
    "ventas_ver",
    "ventas_crear",
    "usuarios_ver",
    "usuarios_crear",
    "usuarios_actualizar",
    "usuarios_eliminar",
    "ensayos_ver",
    "ensayos_crear",
    "ensayos_actualizar",
    "reportes_generar",
    "reportes_exportar",
    "auditoria_ver"
  ]
}
```

### 5. Listar Medicamentos
```http
GET http://localhost:8000/api/mysql/medicamentos
```

**Respuesta esperada:**
```json
{
  "medicamentos": [
    {
      "id": 1,
      "nombre": "Paracetamol",
      "principio_activo": "Acetaminofén",
      "precio": 12.50,
      "stock_minimo": 100
    },
    {
      "id": 2,
      "nombre": "Ibuprofeno",
      "principio_activo": "Ibuprofeno",
      "precio": 18.75,
      "stock_minimo": 80
    }
  ]
}
```

### 6. Crear Medicamento
```http
POST http://localhost:8000/api/mysql/medicamentos
Content-Type: application/json

{
  "nombre": "Amoxicilina 500mg",
  "principio_activo": "Amoxicilina",
  "precio": 25.00,
  "stock_minimo": 50
}
```

**Respuesta esperada:**
```json
{
  "message": "Medicamento creado",
  "medicamento_id": 6
}
```

### 7. Obtener Stock de Medicamento
```http
GET http://localhost:8000/api/mysql/medicamentos/1/stock
```

**Respuesta esperada:**
```json
{
  "medicamento_id": 1,
  "stock_total": 450
}
```

### 8. Listar Lotes
```http
GET http://localhost:8000/api/mysql/lotes
```

**Con filtro por medicamento:**
```http
GET http://localhost:8000/api/mysql/lotes?medicamento_id=1
```

### 9. Crear Lote
```http
POST http://localhost:8000/api/mysql/lotes
Content-Type: application/json

{
  "medicamento_id": 1,
  "numero_lote": "LOT-2025-001",
  "cantidad": 500,
  "fecha_fabricacion": "2025-01-15",
  "fecha_vencimiento": "2027-01-15",
  "precio_compra": 8.50
}
```

### 10. Registrar Venta
```http
POST http://localhost:8000/api/mysql/ventas
Content-Type: application/json

{
  "usuario_id": 2,
  "detalles": [
    {
      "medicamento_id": 1,
      "cantidad": 5,
      "precio_unitario": 12.50
    },
    {
      "medicamento_id": 2,
      "cantidad": 3,
      "precio_unitario": 18.75
    }
  ]
}
```

**Respuesta esperada:**
```json
{
  "message": "Venta registrada",
  "venta_id": 4
}
```

### 11. Listar Ventas
```http
GET http://localhost:8000/api/mysql/ventas
```

**Filtrar por usuario:**
```http
GET http://localhost:8000/api/mysql/ventas?usuario_id=2
```

### 12. Obtener Auditoría
```http
GET http://localhost:8000/api/mysql/auditoria
```

**Con filtros:**
```http
GET http://localhost:8000/api/mysql/auditoria?usuario_id=1&accion=inventario_crear&limite=20
```

---

## 🟢 MONGODB - Documentos NoSQL

### 13. Listar Todos los Ensayos
```http
GET http://localhost:8000/api/mongodb/ensayos
```

**Respuesta esperada:**
```json
{
  "total": 3,
  "ensayos": [
    {
      "_id": "673e5a1b2c3d4e5f6a7b8c9d",
      "codigo_ensayo": "EC-2024-001",
      "titulo": "Eficacia de Ibuprofeno en dolor crónico",
      "medicamento": "Ibuprofeno 600mg",
      "fase": "III",
      "estado": "en_progreso",
      "investigador_principal": "Dr. Carlos Martínez",
      "participantes": {
        "objetivo": 200,
        "reclutados": 75,
        "activos": 70,
        "completados": 0,
        "retirados": 5
      }
    }
  ]
}
```

### 14. Listar Solo Ensayos Activos
```http
GET http://localhost:8000/api/mongodb/ensayos?solo_activos=true
```

### 15. Filtrar por Fase
```http
GET http://localhost:8000/api/mongodb/ensayos?fase=III
```

### 16. Filtrar por Estado
```http
GET http://localhost:8000/api/mongodb/ensayos?estado=en_progreso
```

### 17. Filtrar por Medicamento
```http
GET http://localhost:8000/api/mongodb/ensayos?medicamento=Ibuprofeno
```

### 18. Crear Ensayo Clínico
```http
POST http://localhost:8000/api/mongodb/ensayos
Content-Type: application/json

{
  "codigo_ensayo": "EC-2025-100",
  "titulo": "Eficacia de Aspirina en prevención cardiovascular",
  "medicamento": "Aspirina 100mg",
  "fase": "III",
  "estado": "reclutando",
  "investigador_principal": "Dra. Ana López",
  "institucion": "Hospital Universitario Central",
  "objetivo": "Evaluar la eficacia de Aspirina en dosis bajas para prevención de eventos cardiovasculares en pacientes de alto riesgo",
  "criterios_inclusion": [
    "Edad entre 50-75 años",
    "Historia de hipertensión arterial",
    "Diabetes tipo 2 controlada",
    "Consentimiento informado firmado"
  ],
  "criterios_exclusion": [
    "Alergia conocida a AAS",
    "Úlcera péptica activa",
    "Trastornos de coagulación",
    "Embarazo o lactancia"
  ],
  "participantes_objetivo": 500
}
```

**Respuesta esperada:**
```json
{
  "message": "Ensayo clínico creado",
  "ensayo_id": "673e5f2a3b4c5d6e7f8a9b0c"
}
```

### 19. Obtener Ensayo por Código
```http
GET http://localhost:8000/api/mongodb/ensayos/EC-2025-100
```

### 20. Actualizar Ensayo
```http
PUT http://localhost:8000/api/mongodb/ensayos/EC-2025-100
Content-Type: application/json

{
  "estado": "en_progreso",
  "investigador_principal": "Dra. Ana López Martínez"
}
```

**Respuesta esperada:**
```json
{
  "message": "Ensayo actualizado",
  "campos_modificados": 2
}
```

### 21. Agregar Observación
```http
POST http://localhost:8000/api/mongodb/ensayos/EC-2025-100/observaciones
Content-Type: application/json

{
  "tipo": "eficacia",
  "descripcion": "Paciente 045 reporta mejoría significativa del dolor tras 2 semanas de tratamiento. Escala EVA disminuyó de 8 a 3.",
  "severidad": "leve"
}
```

**Respuesta esperada:**
```json
{
  "message": "Observación agregada exitosamente"
}
```

### 22. Actualizar Participantes
```http
PUT http://localhost:8000/api/mongodb/ensayos/EC-2025-100/participantes
Content-Type: application/json

{
  "reclutados": 125,
  "activos": 120,
  "completados": 0,
  "retirados": 5
}
```

### 23. Agregar Resultados
```http
POST http://localhost:8000/api/mongodb/ensayos/EC-2025-100/resultados
Content-Type: application/json

{
  "categoria": "eficacia",
  "datos": {
    "reduccion_dolor_promedio": 65.5,
    "pacientes_con_mejoria": 95,
    "pacientes_sin_cambio": 20,
    "pacientes_con_empeoramiento": 5,
    "escala_EVA_inicial": 7.8,
    "escala_EVA_final": 3.2,
    "tiempo_promedio_mejoria_dias": 14
  }
}
```

**Otro ejemplo - Resultados de Seguridad:**
```http
POST http://localhost:8000/api/mongodb/ensayos/EC-2025-100/resultados
Content-Type: application/json

{
  "categoria": "seguridad",
  "datos": {
    "eventos_adversos_totales": 12,
    "eventos_adversos_graves": 0,
    "eventos_adversos_leves": 12,
    "tasa_abandono": 4.0,
    "principales_efectos": ["nausea", "cefalea", "mareo"],
    "hospitalizaciones": 0
  }
}
```

### 24. Búsqueda Avanzada
```http
GET http://localhost:8000/api/mongodb/ensayos/busqueda/avanzada?fase=III&estado=en_progreso&min_participantes=100
```

**Con más filtros:**
```http
GET http://localhost:8000/api/mongodb/ensayos/busqueda/avanzada?medicamento=Ibuprofeno&investigador=Martinez&fecha_inicio_desde=2024-01-01
```

### 25. Estadísticas por Fase
```http
GET http://localhost:8000/api/mongodb/estadisticas/por-fase
```

**Respuesta esperada:**
```json
{
  "total_fases": 4,
  "estadisticas": [
    {
      "fase": "I",
      "total_ensayos": 2,
      "participantes_totales": 80,
      "promedio_participantes": 40.0,
      "ensayos_activos": 1
    },
    {
      "fase": "II",
      "total_ensayos": 5,
      "participantes_totales": 450,
      "promedio_participantes": 90.0,
      "ensayos_activos": 3
    },
    {
      "fase": "III",
      "total_ensayos": 8,
      "participantes_totales": 2400,
      "promedio_participantes": 300.0,
      "ensayos_activos": 5
    }
  ]
}
```

### 26. Eliminar Ensayo (Soft Delete)
```http
DELETE http://localhost:8000/api/mongodb/ensayos/EC-2025-100
```

**Hard Delete (permanente):**
```http
DELETE http://localhost:8000/api/mongodb/ensayos/EC-2025-100?hard_delete=true
```

---

## 🔴 REDIS - Clave-Valor

### 27. Crear Sesión
```http
POST http://localhost:8000/api/redis/sesiones
Content-Type: application/json

{
  "usuario_id": 1,
  "nombre_usuario": "admin",
  "rol": "gerente",
  "expiracion_minutos": 60
}
```

**Respuesta esperada:**
```json
{
  "message": "Sesión creada",
  "session_id": "session:abc123def456",
  "expira_en_minutos": 60
}
```

### 28. Obtener Sesión
```http
GET http://localhost:8000/api/redis/sesiones/session:abc123def456
```

**Respuesta esperada:**
```json
{
  "usuario_id": 1,
  "nombre_usuario": "admin",
  "rol": "gerente",
  "timestamp": "2025-11-21T10:30:00"
}
```

### 29. Listar Sesiones Activas
```http
GET http://localhost:8000/api/redis/sesiones
```

**Respuesta esperada:**
```json
{
  "total": 3,
  "sesiones": [
    {
      "session_id": "session:abc123",
      "usuario_id": 1,
      "nombre_usuario": "admin",
      "rol": "gerente"
    },
    {
      "session_id": "session:def456",
      "usuario_id": 2,
      "nombre_usuario": "farmaceutico1",
      "rol": "farmaceutico"
    }
  ]
}
```

### 30. Cerrar Sesión
```http
DELETE http://localhost:8000/api/redis/sesiones/session:abc123def456
```

### 31. Cachear Precio
```http
POST http://localhost:8000/api/redis/cache/precios
Content-Type: application/json

{
  "medicamento_id": 1,
  "precio": 12.50,
  "expiracion_segundos": 300
}
```

### 32. Obtener Precio del Caché
```http
GET http://localhost:8000/api/redis/cache/precios/1
```

**Respuesta esperada:**
```json
{
  "medicamento_id": 1,
  "precio": 12.5
}
```

### 33. Invalidar Caché de Precio
```http
DELETE http://localhost:8000/api/redis/cache/precios/1
```

### 34. Incrementar Contador
```http
POST http://localhost:8000/api/redis/contadores/ventas_diarias/incrementar
```

**Con cantidad específica:**
```http
POST http://localhost:8000/api/redis/contadores/ventas_diarias/incrementar?cantidad=5
```

**Respuesta esperada:**
```json
{
  "contador": "ventas_diarias",
  "nuevo_valor": 45
}
```

### 35. Obtener Contador
```http
GET http://localhost:8000/api/redis/contadores/ventas_diarias
```

### 36. Resetear Contador
```http
DELETE http://localhost:8000/api/redis/contadores/ventas_diarias
```

### 37. Registrar Actividad
```http
POST http://localhost:8000/api/redis/actividad/1
Content-Type: application/json

{
  "accion": "venta_realizada",
  "detalles": "Venta #45 - Total: $125.50",
  "timestamp": "2025-11-21T15:30:00"
}
```

### 38. Obtener Actividad Reciente
```http
GET http://localhost:8000/api/redis/actividad/1
```

**Con límite:**
```http
GET http://localhost:8000/api/redis/actividad/1?limite=20
```

### 39. Estadísticas de Redis
```http
GET http://localhost:8000/api/redis/stats
```

**Respuesta esperada:**
```json
{
  "servidor": {
    "version": "7.2.0",
    "uptime_dias": 5,
    "modo": "standalone"
  },
  "clientes": {
    "conectados": 2,
    "bloqueados": 0
  },
  "memoria": {
    "usada_mb": 1.25,
    "pico_mb": 2.10
  },
  "estadisticas": {
    "comandos_totales": 15847,
    "keys_totales": 42
  }
}
```

---

## 🟡 NEO4J - Grafos

### 40. Listar Medicamentos
```http
GET http://localhost:8000/api/neo4j/medicamentos
```

**Respuesta esperada:**
```json
{
  "total": 5,
  "medicamentos": [
    {
      "nombre": "Ibuprofeno",
      "descripcion": "Antiinflamatorio no esteroideo"
    },
    {
      "nombre": "Aspirina",
      "descripcion": "Analgésico y antiagregante plaquetario"
    }
  ]
}
```

### 41. Obtener Compuestos de un Medicamento
```http
GET http://localhost:8000/api/neo4j/medicamentos/Ibuprofeno/compuestos
```

**Respuesta esperada:**
```json
{
  "medicamento": "Ibuprofeno",
  "total_compuestos": 2,
  "compuestos": [
    {
      "compuesto": "Ácido propiónico",
      "principio_activo": "Ibuprofeno base",
      "propiedades": ["antiinflamatorio", "analgésico"],
      "efectos": ["reducción inflamación", "alivio dolor"]
    }
  ]
}
```

### 42. Obtener Interacciones de un Medicamento
```http
GET http://localhost:8000/api/neo4j/medicamentos/Ibuprofeno/interacciones
```

**Respuesta esperada:**
```json
{
  "medicamento": "Ibuprofeno",
  "total_interacciones": 3,
  "interacciones": [
    {
      "medicamento": "Aspirina",
      "severidad": "moderada",
      "tipo": "farmacodinámica",
      "efecto": "Aumento riesgo de sangrado",
      "recomendacion": "Evitar uso concomitante"
    },
    {
      "medicamento": "Warfarina",
      "severidad": "grave",
      "tipo": "farmacodinámica",
      "efecto": "Riesgo significativo de hemorragia",
      "recomendacion": "Contraindicado - buscar alternativa"
    }
  ]
}
```

### 43. Detectar Interacciones Múltiples
```http
GET http://localhost:8000/api/neo4j/interacciones/detectar?medicamentos=Ibuprofeno,Aspirina,Warfarina
```

**Respuesta esperada:**
```json
{
  "medicamentos_consultados": ["Ibuprofeno", "Aspirina", "Warfarina"],
  "total_interacciones": 3,
  "interacciones": [
    {
      "medicamento1": "Ibuprofeno",
      "medicamento2": "Aspirina",
      "severidad": "moderada",
      "descripcion": "Aumento del riesgo de sangrado gastrointestinal"
    },
    {
      "medicamento1": "Ibuprofeno",
      "medicamento2": "Warfarina",
      "severidad": "grave",
      "descripcion": "Riesgo significativo de hemorragia"
    },
    {
      "medicamento1": "Aspirina",
      "medicamento2": "Warfarina",
      "severidad": "grave",
      "descripcion": "Efecto anticoagulante potenciado"
    }
  ]
}
```

### 44. Camino Más Corto
```http
GET http://localhost:8000/api/neo4j/camino-mas-corto?origen=Ibuprofeno&destino=Warfarina
```

**Respuesta esperada:**
```json
{
  "origen": "Ibuprofeno",
  "destino": "Warfarina",
  "camino_encontrado": true,
  "longitud": 1,
  "camino": {
    "nodos": ["Ibuprofeno", "Warfarina"],
    "relaciones": ["INTERACTUA_CON"]
  }
}
```

### 45. Sugerir Medicamentos Alternativos
```http
GET http://localhost:8000/api/neo4j/alternativas/Ibuprofeno
```

**Respuesta esperada:**
```json
{
  "medicamento_original": "Ibuprofeno",
  "total_alternativas": 2,
  "alternativas": [
    {
      "medicamento": "Naproxeno",
      "compuestos_comunes": ["Ácido propiónico"],
      "similitud": "alta",
      "razon": "Mismo mecanismo de acción"
    },
    {
      "medicamento": "Diclofenaco",
      "compuestos_comunes": ["Base AINE"],
      "similitud": "moderada",
      "razon": "Familia de antiinflamatorios"
    }
  ]
}
```

### 46. Estadísticas del Grafo
```http
GET http://localhost:8000/api/neo4j/stats
```

**Respuesta esperada:**
```json
{
  "total_nodos": 15,
  "total_relaciones": 22,
  "medicamentos": 5,
  "principios_activos": 5,
  "compuestos": 5,
  "interacciones": 7
}
```

---

## 🎯 Flujos Completos de Prueba

### Flujo 1: Registro Completo de Venta

**Paso 1 - Verificar stock:**
```http
GET http://localhost:8000/api/mysql/medicamentos/1/stock
```

**Paso 2 - Crear sesión de usuario:**
```http
POST http://localhost:8000/api/redis/sesiones
{
  "usuario_id": 2,
  "nombre_usuario": "farmaceutico1",
  "rol": "farmaceutico",
  "expiracion_minutos": 30
}
```

**Paso 3 - Cachear precio:**
```http
POST http://localhost:8000/api/redis/cache/precios
{
  "medicamento_id": 1,
  "precio": 12.50,
  "expiracion_segundos": 300
}
```

**Paso 4 - Registrar venta:**
```http
POST http://localhost:8000/api/mysql/ventas
{
  "usuario_id": 2,
  "detalles": [
    {"medicamento_id": 1, "cantidad": 5, "precio_unitario": 12.50}
  ]
}
```

**Paso 5 - Incrementar contador:**
```http
POST http://localhost:8000/api/redis/contadores/ventas_diarias/incrementar
```

**Paso 6 - Registrar actividad:**
```http
POST http://localhost:8000/api/redis/actividad/2
{
  "accion": "venta_completada",
  "detalles": "Venta #X - Total: $62.50"
}
```

### Flujo 2: Gestión Completa de Ensayo Clínico

**Paso 1 - Crear ensayo:**
```http
POST http://localhost:8000/api/mongodb/ensayos
{...datos del ensayo...}
```

**Paso 2 - Actualizar participantes:**
```http
PUT http://localhost:8000/api/mongodb/ensayos/EC-2025-100/participantes
{
  "reclutados": 50,
  "activos": 48
}
```

**Paso 3 - Agregar observación:**
```http
POST http://localhost:8000/api/mongodb/ensayos/EC-2025-100/observaciones
{
  "tipo": "eficacia",
  "descripcion": "Mejorías observadas..."
}
```

**Paso 4 - Agregar resultados:**
```http
POST http://localhost:8000/api/mongodb/ensayos/EC-2025-100/resultados
{
  "categoria": "eficacia",
  "datos": {...}
}
```

**Paso 5 - Consultar estadísticas:**
```http
GET http://localhost:8000/api/mongodb/estadisticas/por-fase
```

### Flujo 3: Verificación de Interacciones Medicamentosas

**Paso 1 - Listar medicamentos disponibles:**
```http
GET http://localhost:8000/api/neo4j/medicamentos
```

**Paso 2 - Detectar interacciones:**
```http
GET http://localhost:8000/api/neo4j/interacciones/detectar?medicamentos=Ibuprofeno,Aspirina,Warfarina
```

**Paso 3 - Buscar alternativas si hay interacción grave:**
```http
GET http://localhost:8000/api/neo4j/alternativas/Ibuprofeno
```

**Paso 4 - Verificar compuestos del alternativo:**
```http
GET http://localhost:8000/api/neo4j/medicamentos/Naproxeno/compuestos
```

---

## 💡 Tips para Postman

### 1. Variables de Entorno
Crea variables para no repetir la URL base:
- Variable: `baseUrl` = `http://localhost:8000`
- Uso: `{{baseUrl}}/api/mysql/usuarios`

### 2. Tests Automáticos
Agrega en la pestaña "Tests":
```javascript
pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});

pm.test("Response has data", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData).to.not.be.empty;
});
```

### 3. Pre-request Scripts
Para generar datos dinámicos:
```javascript
pm.environment.set("timestamp", new Date().toISOString());
pm.environment.set("random_id", Math.floor(Math.random() * 1000));
```

### 4. Guardar Session ID
En Tests, después de crear sesión:
```javascript
var jsonData = pm.response.json();
pm.environment.set("session_id", jsonData.session_id);
```

Luego usar: `{{session_id}}`

---

**¡Ahora tienes ejemplos completos para probar toda tu API!** 🎉
