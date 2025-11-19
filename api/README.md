# 🚀 PharmaFlow Solutions - API REST

API completa para interactuar con todas las bases de datos del proyecto desde Postman.

## 📋 Instalación

```powershell
# 1. Instalar dependencias (incluye FastAPI y Uvicorn)
pip install -r requierments.txt

# 2. Asegurarse de que el archivo .env está configurado
```

## ▶️ Ejecutar la API

```powershell
# Opción 1: Directamente con Python
python api/main.py

# Opción 2: Con Uvicorn (recomendado para desarrollo)
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

La API estará disponible en: **http://localhost:8000**

## 📖 Documentación Interactiva

Una vez iniciada la API, accede a:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

Estas interfaces permiten probar todos los endpoints directamente desde el navegador.

## 🗂️ Estructura de Endpoints

### 🔵 MySQL - Relacional (`/api/mysql`)

#### Usuarios
- `GET /api/mysql/usuarios` - Listar usuarios
- `POST /api/mysql/usuarios` - Crear usuario
- `GET /api/mysql/usuarios/{id}` - Obtener usuario
- `GET /api/mysql/usuarios/{id}/permisos` - Permisos del usuario
- `DELETE /api/mysql/usuarios/{id}` - Eliminar usuario

#### Medicamentos
- `GET /api/mysql/medicamentos` - Listar medicamentos
- `POST /api/mysql/medicamentos` - Crear medicamento
- `GET /api/mysql/medicamentos/{id}` - Obtener medicamento
- `GET /api/mysql/medicamentos/{id}/stock` - Stock del medicamento

#### Lotes
- `GET /api/mysql/lotes` - Listar lotes
- `POST /api/mysql/lotes` - Crear lote

#### Ventas
- `GET /api/mysql/ventas` - Listar ventas
- `POST /api/mysql/ventas` - Registrar venta
- `GET /api/mysql/ventas/{id}` - Detalle de venta

#### Auditoría
- `GET /api/mysql/auditoria` - Registros de auditoría

### 🟢 MongoDB - Documentos (`/api/mongodb`)

#### Ensayos Clínicos
- `GET /api/mongodb/ensayos` - Listar ensayos (con filtros)
- `POST /api/mongodb/ensayos` - Crear ensayo
- `GET /api/mongodb/ensayos/{codigo}` - Obtener ensayo
- `PUT /api/mongodb/ensayos/{codigo}` - Actualizar ensayo
- `DELETE /api/mongodb/ensayos/{codigo}` - Eliminar ensayo

#### Operaciones Especiales
- `POST /api/mongodb/ensayos/{codigo}/observaciones` - Agregar observación
- `PUT /api/mongodb/ensayos/{codigo}/participantes` - Actualizar participantes
- `POST /api/mongodb/ensayos/{codigo}/resultados` - Agregar resultados

#### Búsquedas y Estadísticas
- `GET /api/mongodb/ensayos/busqueda/avanzada` - Búsqueda con múltiples filtros
- `GET /api/mongodb/estadisticas/por-fase` - Agregaciones por fase

### 🔴 Redis - Clave-Valor (`/api/redis`)

#### Sesiones
- `POST /api/redis/sesiones` - Crear sesión
- `GET /api/redis/sesiones/{id}` - Obtener sesión
- `DELETE /api/redis/sesiones/{id}` - Cerrar sesión
- `GET /api/redis/sesiones` - Listar sesiones activas

#### Caché de Precios
- `POST /api/redis/cache/precios` - Cachear precio
- `GET /api/redis/cache/precios/{id}` - Obtener precio
- `DELETE /api/redis/cache/precios/{id}` - Invalidar caché

#### Contadores
- `POST /api/redis/contadores/{nombre}/incrementar` - Incrementar
- `GET /api/redis/contadores/{nombre}` - Obtener valor
- `DELETE /api/redis/contadores/{nombre}` - Resetear

#### Actividad
- `POST /api/redis/actividad/{usuario_id}` - Registrar actividad
- `GET /api/redis/actividad/{usuario_id}` - Obtener actividad

#### Utilidades
- `GET /api/redis/stats` - Estadísticas de Redis
- `DELETE /api/redis/flush` - Limpiar BD (requiere confirmación)

### 🟡 Neo4j - Grafos (`/api/neo4j`)

#### Consultas
- `GET /api/neo4j/medicamentos` - Listar medicamentos
- `GET /api/neo4j/medicamentos/{nombre}/compuestos` - Compuestos de un medicamento
- `GET /api/neo4j/medicamentos/{nombre}/interacciones` - Interacciones
- `GET /api/neo4j/interacciones/detectar?medicamentos=Med1,Med2` - Detectar múltiples
- `GET /api/neo4j/camino-mas-corto?origen=A&destino=B` - Camino más corto
- `GET /api/neo4j/alternativas/{medicamento}` - Sugerir alternativas

#### Estadísticas
- `GET /api/neo4j/stats` - Estadísticas del grafo

#### Creación (Opcional)
- `POST /api/neo4j/medicamentos` - Crear medicamento
- `POST /api/neo4j/compuestos` - Crear compuesto
- `POST /api/neo4j/interacciones` - Crear interacción

## 📝 Ejemplos de Uso en Postman

### 1. Crear Usuario (MySQL)
```http
POST http://localhost:8000/api/mysql/usuarios
Content-Type: application/json

{
  "nombre_usuario": "ana_lopez",
  "contrasena": "password123",
  "email": "ana@pharmaflow.com",
  "rol": "farmaceutico"
}
```

### 2. Crear Ensayo Clínico (MongoDB)
```http
POST http://localhost:8000/api/mongodb/ensayos
Content-Type: application/json

{
  "codigo_ensayo": "EC-2025-100",
  "titulo": "Eficacia de Aspirina en prevención cardiovascular",
  "medicamento": "Aspirina 100mg",
  "fase": "III",
  "estado": "reclutando",
  "investigador_principal": "Dr. Juan Pérez",
  "institucion": "Hospital Central",
  "objetivo": "Evaluar eficacia en prevención de eventos cardiovasculares",
  "criterios_inclusion": ["Mayor de 50 años", "Historia de hipertensión"],
  "criterios_exclusion": ["Alergia a AAS", "Úlcera activa"],
  "participantes_objetivo": 500
}
```

### 3. Buscar Ensayos (MongoDB)
```http
GET http://localhost:8000/api/mongodb/ensayos/busqueda/avanzada?fase=III&estado=reclutando&min_participantes=100
```

### 4. Crear Sesión (Redis)
```http
POST http://localhost:8000/api/redis/sesiones
Content-Type: application/json

{
  "usuario_id": 1,
  "nombre_usuario": "ana_lopez",
  "rol": "farmaceutico",
  "expiracion_minutos": 60
}
```

### 5. Detectar Interacciones (Neo4j)
```http
GET http://localhost:8000/api/neo4j/interacciones/detectar?medicamentos=Ibuprofeno,Aspirina,Warfarina
```

### 6. Registrar Venta (MySQL)
```http
POST http://localhost:8000/api/mysql/ventas
Content-Type: application/json

{
  "usuario_id": 1,
  "detalles": [
    {
      "medicamento_id": 1,
      "cantidad": 2,
      "precio_unitario": 15.50
    },
    {
      "medicamento_id": 3,
      "cantidad": 1,
      "precio_unitario": 45.00
    }
  ]
}
```

## 🔧 Características

✅ **Documentación automática** con Swagger UI y ReDoc
✅ **Validación de datos** con Pydantic
✅ **Manejo de errores** con HTTP status codes apropiados
✅ **CORS habilitado** para desarrollo
✅ **Endpoints organizados** por tipo de base de datos
✅ **Filtros y búsquedas avanzadas**
✅ **Operaciones CRUD completas**

## 📦 Exportar/Importar Colección de Postman

Una vez que pruebes los endpoints en Postman, puedes:

1. **Guardar la colección**: Click en los "..." → Export
2. **Compartir**: Guarda el archivo JSON en `docs/postman_collection.json`
3. **Importar**: File → Import → Seleccionar el archivo JSON

## 🎯 Ventajas vs Scripts de Testing

| Scripts Python | API REST + Postman |
|----------------|-------------------|
| ❌ Modificar código para cada prueba | ✅ Cambiar parámetros en la UI |
| ❌ Ejecutar archivo completo | ✅ Ejecutar endpoints individuales |
| ❌ Sin historial de requests | ✅ Historial y colecciones guardadas |
| ❌ Salida solo en terminal | ✅ Respuestas JSON formateadas |
| ❌ Difícil compartir pruebas | ✅ Exportar/importar colecciones |
| ❌ No hay variables de entorno | ✅ Variables y ambientes (dev/prod) |

## 🚨 Notas Importantes

- La API usa los mismos **services** del proyecto, por lo que todas las operaciones afectan las bases de datos reales
- Asegúrate de que todas las bases de datos (MySQL, MongoDB, Redis, Neo4j) estén corriendo
- Para producción, configurar autenticación JWT y HTTPS
- Los endpoints de eliminación (DELETE) son permanentes (excepto MongoDB que usa soft delete por defecto)

## 🐛 Solución de Problemas

**Error de conexión a BD:**
```
Verificar que los contenedores Docker están corriendo:
docker ps
```

**Puerto 8000 ocupado:**
```powershell
# Cambiar puerto
uvicorn api.main:app --port 8001
```

**Módulos no encontrados:**
```powershell
pip install -r requierments.txt
```

---

**¡Ahora puedes usar Postman para todas tus pruebas sin modificar código!** 🎉
