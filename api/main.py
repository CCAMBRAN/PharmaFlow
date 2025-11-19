"""
API REST para PharmaFlow Solutions
Permite interactuar con todas las bases de datos desde Postman
"""
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List, Dict, Any
from datetime import datetime
import sys
from pathlib import Path

# Agregar el directorio padre al path para imports
sys.path.append(str(Path(__file__).parent.parent))

from api.routers import mysql_router, mongodb_router, redis_router, neo4j_router

# Crear aplicación FastAPI
app = FastAPI(
    title="PharmaFlow Solutions API",
    description="API REST para gestión farmacéutica con múltiples bases de datos",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS para permitir requests desde Postman
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(mysql_router.router, prefix="/api/mysql", tags=["MySQL - Relacional"])
app.include_router(mongodb_router.router, prefix="/api/mongodb", tags=["MongoDB - Documentos"])
app.include_router(redis_router.router, prefix="/api/redis", tags=["Redis - Clave-Valor"])
app.include_router(neo4j_router.router, prefix="/api/neo4j", tags=["Neo4j - Grafos"])

@app.get("/", tags=["General"])
async def root():
    """Endpoint raíz con información de la API"""
    return {
        "message": "PharmaFlow Solutions API",
        "version": "1.0.0",
        "docs": "/docs",
        "databases": {
            "mysql": "/api/mysql",
            "mongodb": "/api/mongodb",
            "redis": "/api/redis",
            "neo4j": "/api/neo4j"
        }
    }

@app.get("/health", tags=["General"])
async def health_check():
    """Verificar estado de salud de la API"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
