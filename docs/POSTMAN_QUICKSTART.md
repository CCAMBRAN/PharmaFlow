# 🚀 Guía Rápida: Usar Postman con PharmaFlow API

## Paso 1: Iniciar la API

```powershell
python run_api.py
```

La API estará en: **http://localhost:8000**

## Paso 2: Abrir Postman

1. Abre Postman Desktop o Web
2. Crea una nueva **Collection** llamada "PharmaFlow Solutions"
3. Dentro de la collection, crea folders para cada BD:
   - MySQL - Relacional
   - MongoDB - Documentos
   - Redis - Clave-Valor
   - Neo4j - Grafos

## Paso 3: Primeros Requests

### ✅ Health Check
```
GET http://localhost:8000/health
```
Debería devolver: `{"status": "healthy", "timestamp": "..."}`

### 📖 Ver Documentación Interactiva
Abre en tu navegador: **http://localhost:8000/docs**

Aquí puedes ver TODOS los endpoints disponibles y probarlos directamente.

## Ejemplos Rápidos

### 1️⃣ Listar Usuarios (MySQL)
```http
GET http://localhost:8000/api/mysql/usuarios
```

### 2️⃣ Listar Ensayos Clínicos (MongoDB)
```http
GET http://localhost:8000/api/mongodb/ensayos
```

### 3️⃣ Ver Sesiones Activas (Redis)
```http
GET http://localhost:8000/api/redis/sesiones
```

### 4️⃣ Listar Medicamentos (Neo4j)
```http
GET http://localhost:8000/api/neo4j/medicamentos
```

### 5️⃣ Crear Usuario (MySQL)
```http
POST http://localhost:8000/api/mysql/usuarios
Content-Type: application/json

{
  "nombre_usuario": "maria_garcia",
  "contrasena": "password123",
  "email": "maria@pharmaflow.com",
  "rol": "farmaceutico"
}
```

### 6️⃣ Buscar Ensayos por Fase (MongoDB)
```http
GET http://localhost:8000/api/mongodb/ensayos?fase=III&solo_activos=true
```

### 7️⃣ Crear Sesión (Redis)
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

### 8️⃣ Detectar Interacciones (Neo4j)
```http
GET http://localhost:8000/api/neo4j/interacciones/detectar?medicamentos=Ibuprofeno,Aspirina
```

## Configurar Variables en Postman

1. Click en tu Collection → Variables
2. Agrega estas variables:

| Variable | Value |
|----------|-------|
| baseUrl | http://localhost:8000 |
| apiVersion | v1 |

3. Ahora puedes usar: `{{baseUrl}}/api/mysql/usuarios`

## Guardar Respuestas

Postman automáticamente guarda:
- ✅ Historial de requests
- ✅ Respuestas recibidas
- ✅ Headers y body

## Exportar Collection

1. Click derecho en tu Collection
2. **Export**
3. Guardar como `PharmaFlow_Collection.json`
4. Compartir con tu equipo o guardar en Git

## Ventajas sobre Scripts

| Aspecto | Scripts Python | API + Postman |
|---------|---------------|---------------|
| Modificar datos | Editar código | Cambiar JSON en UI |
| Ejecutar | Correr archivo completo | Click en request |
| Ver resultados | Terminal | JSON formateado + colores |
| Guardar pruebas | Versionar código | Exportar collection |
| Compartir | Enviar archivo .py | Enviar archivo .json |
| Documentación | Comentarios en código | Auto-generada en /docs |

## Tips Avanzados

### Pre-request Scripts
Ejecutar código antes del request (ej: generar timestamps)

### Tests
Validar respuestas automáticamente:
```javascript
pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});

pm.test("Response has usuarios", function () {
    pm.expect(pm.response.json()).to.have.property("usuarios");
});
```

### Environments
Crear ambientes (Development, Production) con URLs diferentes

### Runner
Ejecutar toda la collection de una vez (testing automatizado)

---

**¡Ahora puedes probar todas tus bases de datos desde Postman sin escribir código!** 🎉
