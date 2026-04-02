from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from pathlib import Path
import zipfile
import shutil
import logging
from ..plugins.plugin_marketplace import (
    plugin_registry,
    compatibility_checker,
    plugin_analytics,
    MarketplacePlugin
)

router = APIRouter(prefix="/marketplace")
logger = logging.getLogger(__name__)


class SearchQuery(BaseModel):
    query: str = ""
    category: str = "all"
    sort_by: str = Field(default="rating", regex="^(rating|downloads|featured|name|newest)$")
    limit: int = Field(default=20, ge=1, le=100)


class CompatibilityCheckRequest(BaseModel):
    plugin_id: str
    ide_version: str
    system_info: Dict[str, str] = {}


class PluginInstallRequest(BaseModel):
    plugin_id: str
    version: str = "latest"
    user_id: str = "current_user"


class PluginUninstallRequest(BaseModel):
    plugin_id: str
    user_id: str = "current_user"


class PluginRateRequest(BaseModel):
    plugin_id: str
    user_id: str
    rating: int = Field(..., ge=1, le=5)
    review: str = ""


class PluginSubmitResponse(BaseModel):
    status: str
    message: str
    plugin_id: Optional[str] = None


class CompatibilityReport(BaseModel):
    compatible: bool
    issues: List[str]
    warnings: List[str]
    details: Dict[str, str]


class PopularPlugin(BaseModel):
    plugin_id: str
    score: float
    installs: int
    usage_count: int
    active_users: int


# Response model for plugin list (using dict since MarketplacePlugin might not serialize directly)
class PluginListResponse(BaseModel):
    plugins: List[Dict[str, Any]]
    total: int


@router.post("/search")
async def search_plugins(query: SearchQuery):
    """Search for plugins in the marketplace"""
    try:
        plugins = await plugin_registry.search_plugins(
            query=query.query,
            category=query.category,
            sort_by=query.sort_by,
            limit=query.limit
        )
        return {
            "plugins": [p.model_dump() for p in plugins],
            "total": len(plugins)
        }
    except Exception as e:
        logger.exception("Error searching plugins")
        raise HTTPException(status_code=500, detail="Failed to search plugins")


@router.get("/plugin/{plugin_id}")
async def get_plugin_details(plugin_id: str):
    """Get detailed information about a specific plugin"""
    try:
        plugin = await plugin_registry.get_plugin_details(plugin_id)
        if plugin:
            return plugin.model_dump()
        raise HTTPException(status_code=404, detail="Plugin not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error getting plugin details for {plugin_id}")
        raise HTTPException(status_code=500, detail="Failed to get plugin details")


@router.post("/install")
async def install_plugin(request: PluginInstallRequest):
    """Install a plugin from the marketplace"""
    try:
        # Check if plugin exists
        plugin = await plugin_registry.get_plugin_details(request.plugin_id)
        if not plugin:
            raise HTTPException(status_code=404, detail="Plugin not found")

        # Download plugin
        plugin_file = await plugin_registry.download_plugin(request.plugin_id, request.version)

        # Extract plugin to plugins directory
        plugins_dir = Path("./plugins") / request.plugin_id
        plugins_dir.mkdir(parents=True, exist_ok=True)

        with zipfile.ZipFile(plugin_file, 'r') as zip_ref:
            zip_ref.extractall(plugins_dir)

        # Record installation analytics
        plugin_analytics.record_plugin_install(request.plugin_id, request.user_id)

        # Clean up downloaded file
        Path(plugin_file).unlink(missing_ok=True)

        return {
            "status": "success",
            "message": f"Plugin '{plugin.name}' installed successfully",
            "plugin_id": request.plugin_id,
            "version": request.version,
            "install_path": str(plugins_dir)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error installing plugin {request.plugin_id}")
        raise HTTPException(status_code=500, detail=f"Failed to install plugin: {str(e)}")


@router.post("/uninstall")
async def uninstall_plugin(request: PluginUninstallRequest):
    """Uninstall a plugin"""
    try:
        plugins_dir = Path("./plugins") / request.plugin_id

        if not plugins_dir.exists():
            raise HTTPException(status_code=404, detail="Plugin not installed")

        # Remove plugin directory
        shutil.rmtree(plugins_dir)

        # Record uninstall analytics
        plugin_analytics.record_plugin_uninstall(request.plugin_id, request.user_id)

        return {
            "status": "success",
            "message": "Plugin uninstalled successfully",
            "plugin_id": request.plugin_id
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error uninstalling plugin {request.plugin_id}")
        raise HTTPException(status_code=500, detail=f"Failed to uninstall plugin: {str(e)}")


@router.post("/check-compatibility")
async def check_compatibility(request: CompatibilityCheckRequest):
    """Check if a plugin is compatible with current environment"""
    try:
        plugin = await plugin_registry.get_plugin_details(request.plugin_id)
        if not plugin:
            raise HTTPException(status_code=404, detail="Plugin not found")

        # Check compatibility
        compatibility_report = compatibility_checker.check_compatibility(
            plugin,
            request.ide_version,
            request.system_info
        )

        # Check dependencies
        installed_plugins = {}  # Would be loaded from actual installed plugins
        dependency_report = compatibility_checker.check_dependencies(plugin, installed_plugins)

        return {
            "compatibility": compatibility_report,
            "dependencies": dependency_report,
            "plugin": plugin.model_dump()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error checking compatibility")
        raise HTTPException(status_code=500, detail="Failed to check compatibility")


@router.get("/categories")
async def get_categories():
    """Get available plugin categories"""
    try:
        categories = await plugin_registry.get_categories()
        return {"categories": categories}
    except Exception as e:
        logger.exception("Error getting categories")
        raise HTTPException(status_code=500, detail="Failed to get categories")


@router.get("/featured")
async def get_featured_plugins():
    """Get featured/trending plugins"""
    try:
        plugins = await plugin_registry.get_featured_plugins()
        return {
            "plugins": [p.model_dump() for p in plugins],
            "total": len(plugins)
        }
    except Exception as e:
        logger.exception("Error getting featured plugins")
        raise HTTPException(status_code=500, detail="Failed to get featured plugins")


@router.get("/popular")
async def get_popular_plugins(limit: int = 10):
    """Get most popular plugins based on analytics"""
    try:
        popular = plugin_analytics.get_popular_plugins(limit=limit)
        return {"plugins": popular}
    except Exception as e:
        logger.exception("Error getting popular plugins")
        raise HTTPException(status_code=500, detail="Failed to get popular plugins")


@router.get("/stats/{plugin_id}")
async def get_plugin_stats(plugin_id: str):
    """Get usage statistics for a specific plugin"""
    try:
        stats = plugin_analytics.get_plugin_stats(plugin_id)
        if stats:
            return stats
        raise HTTPException(status_code=404, detail="Plugin stats not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error getting plugin stats for {plugin_id}")
        raise HTTPException(status_code=500, detail="Failed to get plugin stats")


@router.post("/rate")
async def rate_plugin(request: PluginRateRequest):
    """Rate a plugin"""
    try:
        # In production, would validate API token from auth header
        api_token = ""  # Get from auth

        success = await plugin_registry.rate_plugin(
            request.plugin_id,
            request.user_id,
            request.rating,
            request.review,
            api_token
        )

        if success:
            return {
                "status": "success",
                "message": "Rating submitted successfully"
            }
        raise HTTPException(status_code=500, detail="Failed to submit rating")
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error rating plugin")
        raise HTTPException(status_code=500, detail="Failed to submit rating")


@router.post("/submit", response_model=PluginSubmitResponse)
async def submit_plugin(
    plugin: UploadFile = File(...),
    name: str = Form(...),
    description: str = Form(...),
    version: str = Form(...),
    author: str = Form(...),
    tags: str = Form(""),
    dependencies: str = Form(""),
    license: str = Form("MIT"),
    homepage: Optional[str] = Form(None)
):
    """Submit a new plugin to the marketplace"""
    temp_file = None
    try:
        # Validate file type
        if not plugin.filename.endswith('.zip'):
            raise HTTPException(status_code=400, detail="Plugin must be a zip file")

        # Save uploaded plugin file temporarily
        temp_file = Path(f"./temp_{plugin.filename}")
        with open(temp_file, 'wb') as f:
            content = await plugin.read()
            f.write(content)

        # Prepare plugin data
        plugin_data = {
            "name": name,
            "description": description,
            "version": version,
            "author": author,
            "tags": [t.strip() for t in tags.split(",") if t.strip()],
            "dependencies": [d.strip() for d in dependencies.split(",") if d.strip()],
            "license": license,
            "homepage": homepage
        }

        # In production, would get API token from auth header
        api_token = ""  # Get from auth

        # Submit to registry
        result = await plugin_registry.submit_plugin(plugin_data, str(temp_file), api_token)

        return {
            "status": "success",
            "message": "Plugin submitted successfully",
            "plugin_id": result.get("plugin_id")
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error submitting plugin")
        raise HTTPException(status_code=500, detail=f"Failed to submit plugin: {str(e)}")
    finally:
        # Clean up temp file
        if temp_file and temp_file.exists():
            temp_file.unlink(missing_ok=True)


@router.post("/cache/clear")
async def clear_cache():
    """Clear plugin marketplace cache"""
    try:
        plugin_registry.cache.clear()
        return {"status": "success", "message": "Cache cleared"}
    except Exception as e:
        logger.exception("Error clearing cache")
        raise HTTPException(status_code=500, detail="Failed to clear cache")


@router.on_event("shutdown")
async def shutdown_event():
    """Clean up resources on shutdown"""
    await plugin_registry.close()
