"""
Digital Legacy Vault - Application Launcher
Run this script to start the FastAPI server:
    python run.py
"""
import uvicorn
from app.config import settings

def main():
    print("=" * 65)
    print("  DIGITAL LEGACY VAULT – DA3")
    print("  College DBMS Mini-Project: Neo4j Graph Database System")
    print("=" * 65)
    print(f"Server URL:     http://{settings.APP_HOST}:{settings.APP_PORT}")
    print(f"API Swagger UI: http://{settings.APP_HOST}:{settings.APP_PORT}/docs")
    print(f"Health Check:   http://{settings.APP_HOST}:{settings.APP_PORT}/api/health")
    print(f"Graph Database: {settings.NEO4J_URI} ({settings.NEO4J_DATABASE})")
    print("-" * 65)
    print("Press Ctrl+C to stop the application server.\n")

    uvicorn.run(
        "app.main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=False,
        log_level=settings.LOG_LEVEL
    )

if __name__ == "__main__":
    main()
