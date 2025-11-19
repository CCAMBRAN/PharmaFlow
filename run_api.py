"""
Script para iniciar la API de PharmaFlow Solutions
"""
import uvicorn

if __name__ == "__main__":
    print("=" * 70)
    print("🚀 INICIANDO API DE PHARMAFLOW SOLUTIONS")
    print("=" * 70)
    print()
    print("📖 Documentación Swagger: http://localhost:8000/docs")
    print("📖 Documentación ReDoc:   http://localhost:8000/redoc")
    print("🔍 Health Check:          http://localhost:8000/health")
    print()
    print("Endpoints disponibles:")
    print("  🔵 MySQL:   http://localhost:8000/api/mysql")
    print("  🟢 MongoDB: http://localhost:8000/api/mongodb")
    print("  🔴 Redis:   http://localhost:8000/api/redis")
    print("  🟡 Neo4j:   http://localhost:8000/api/neo4j")
    print()
    print("Presiona CTRL+C para detener el servidor")
    print("=" * 70)
    print()
    
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
