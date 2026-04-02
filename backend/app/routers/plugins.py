from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from app.plugins.plugin_base import PluginManager, PluginManifest, HookName

router = APIRouter(prefix="/plugins")

# Global plugin manager reference (set during lifespan)
_plugin_manager: Optional[PluginManager] = None


def get_plugin_manager() -> PluginManager:
    """Get the plugin manager instance"""
    if _plugin_manager is None:
        raise HTTPException(status_code=500, detail="Plugin manager not initialized")
    return _plugin_manager


def set_plugin_manager(manager: PluginManager) -> None:
    """Set the global plugin manager instance"""
    global _plugin_manager
    _plugin_manager = manager


class PluginActionRequest(BaseModel):
    """Request model for plugin actions"""
    action: str
    plugin_name: str


class PluginListResponse(BaseModel):
    """Response model for plugin list"""
    plugins: List[Dict[str, Any]]


class HookInvokeRequest(BaseModel):
    """Request model for hook invocation"""
    params: Dict[str, Any] = {}


@router.get("/", response_model=PluginListResponse)
async def list_plugins():
    """List all available plugins with their status"""
    manager = get_plugin_manager()
    return PluginListResponse(plugins=manager.list_plugins())


@router.post("/actions")
async def plugin_action(request: PluginActionRequest):
    """Enable, disable, or reload a plugin"""
    manager = get_plugin_manager()

    if request.action == "enable":
        success = await manager.load_plugin(request.plugin_name)
        if success:
            return {"status": "enabled", "plugin": request.plugin_name}
        raise HTTPException(status_code=400, detail=f"Failed to enable plugin: {request.plugin_name}")

    elif request.action == "disable":
        success = await manager.unload_plugin(request.plugin_name)
        if success:
            return {"status": "disabled", "plugin": request.plugin_name}
        raise HTTPException(status_code=400, detail=f"Failed to disable plugin: {request.plugin_name}")

    elif request.action == "reload":
        success = await manager.reload_plugin(request.plugin_name)
        if success:
            return {"status": "reloaded", "plugin": request.plugin_name}
        raise HTTPException(status_code=400, detail=f"Failed to reload plugin: {request.plugin_name}")

    else:
        raise HTTPException(status_code=400, detail=f"Unknown action: {request.action}")


@router.get("/manifest/{plugin_name}", response_model=PluginManifest)
async def get_plugin_manifest(plugin_name: str):
    """Get manifest for a specific plugin"""
    manager = get_plugin_manager()
    manifest = manager.get_plugin_manifest(plugin_name)
    if manifest is None:
        raise HTTPException(status_code=404, detail=f"Plugin not found: {plugin_name}")
    return manifest


@router.post("/hooks/{hook_name}")
async def invoke_hook(hook_name: str, request: HookInvokeRequest = None):
    """Invoke a plugin hook with parameters"""
    manager = get_plugin_manager()

    try:
        hook = HookName(hook_name)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Unknown hook: {hook_name}")

    params = request.params if request else {}
    results = await manager.invoke_hook(hook, **params)
    return {"hook_name": hook_name, "results": results}


@router.get("/routes")
async def get_plugin_routes():
    """Get all routes registered by plugins"""
    manager = get_plugin_manager()
    return {"routes": manager.get_routes()}


@router.get("/middlewares")
async def get_plugin_middlewares():
    """Get all middlewares registered by plugins"""
    manager = get_plugin_manager()
    return {"middlewares": []}  # Middlewares need special handling in FastAPI
