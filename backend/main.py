from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import all routers
from app.routers import (
    chat,
    files,
    settings,
    git,
    providers,
    sessions,
    editor,
    collaboration,
    code_review,
    learning,
    performance,
    marketplace,
    visualization,
    dashboard,
    debug,
    generation,
    extended_providers,
    analytics,
    security
)
from app.routers.plugins import router as plugins_router, set_plugin_manager
from app.plugins.plugin_base import PluginManager, PluginContext

# Plugin directory
PLUGINS_DIR = Path(os.getenv("PLUGINS_DIR", "./plugins"))


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting llama-ide backend with all enhancements...")

    # Initialize plugin system
    if not PLUGINS_DIR.exists():
        PLUGINS_DIR.mkdir(exist_ok=True)
        print(f"Created plugins directory: {PLUGINS_DIR}")

    context = PluginContext(
        app_root=Path("./").resolve(),
        plugins_dir=PLUGINS_DIR,
        settings={}
    )

    plugin_manager = PluginManager(plugins_dir=PLUGINS_DIR, context=context)
    set_plugin_manager(plugin_manager)

    # Discover and auto-load enabled plugins
    await plugin_manager.load_all_plugins()

    yield

    # Shutdown - unload all plugins
    print("Shutting down llama-ide backend...")
    await plugin_manager.unload_all_plugins()


app = FastAPI(
    title="llama-ide API",
    description="Enhanced Backend API for llama-ide with all 12 major features",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all routers
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(files.router, prefix="/api/files", tags=["files"])
app.include_router(settings.router, prefix="/api/settings", tags=["settings"])
app.include_router(git.router, prefix="/api/git", tags=["git"])
app.include_router(providers.router, prefix="/api/providers", tags=["providers"])
app.include_router(sessions.router, prefix="/api/sessions", tags=["sessions"])
app.include_router(editor.router, prefix="/api/editor", tags=["editor"])
app.include_router(plugins_router, prefix="/api/plugins", tags=["plugins"])
app.include_router(collaboration.router, prefix="/api/collaboration", tags=["collaboration"])
app.include_router(code_review.router, prefix="/api/code-review", tags=["code-review"])
app.include_router(learning.router, prefix="/api/learning", tags=["learning"])
app.include_router(performance.router, prefix="/api/performance", tags=["performance"])
app.include_router(marketplace.router, prefix="/api/marketplace", tags=["marketplace"])
app.include_router(visualization.router, prefix="/api/visualization", tags=["visualization"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["dashboard"])
app.include_router(debug.router, prefix="/api/debug", tags=["debug"])
app.include_router(generation.router, prefix="/api/generation", tags=["generation"])
app.include_router(extended_providers.router, prefix="/api/extended-providers", tags=["extended-providers"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])
app.include_router(security.router, prefix="/api/security", tags=["security"])


@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "enhancements": "All 12 major features implemented"}


@app.get("/api/features")
async def list_features():
    """List all implemented features"""
    return {
        "features": [
            "Collaborative Development Features",
            "AI-Powered Code Review System",
            "Integrated Learning Assistant",
            "Performance Optimizations",
            "Advanced Plugin Ecosystem",
            "Enhanced Visualization Tools",
            "Customizable Dashboard",
            "Advanced Debugging Tools",
            "Intelligent Code Generation",
            "Extended Cloud Provider Support",
            "Development Analytics Dashboard",
            "Enterprise Security Features"
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
