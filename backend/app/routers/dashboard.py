from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from ..services.dashboard import (
    dashboard_manager,
    DashboardWidget,
    WidgetType,
    ChartType
)

router = APIRouter(prefix="/dashboard")


class CreateDashboardRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    user_id: str
    description: Optional[str] = None


class CreateFromTemplateRequest(BaseModel):
    user_id: str
    name: Optional[str] = None


class UpdateDashboardRequest(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    description: Optional[str] = None
    is_public: Optional[bool] = None
    tags: Optional[List[str]] = None
    theme: Optional[str] = None


class AddWidgetRequest(BaseModel):
    title: str
    type: WidgetType
    component: str
    position: Dict[str, int] = Field(default_factory=lambda: {"x": 0, "y": 0, "w": 6, "h": 4})
    settings: Optional[Dict[str, Any]] = None
    data_source: Optional[str] = None
    refresh_interval: Optional[int] = Field(default=None, ge=5)
    chart_type: Optional[ChartType] = None
    query: Optional[str] = None


class UpdateWidgetRequest(BaseModel):
    title: Optional[str] = None
    position: Optional[Dict[str, int]] = None
    settings: Optional[Dict[str, Any]] = None
    data_source: Optional[str] = None
    refresh_interval: Optional[int] = Field(default=None, ge=5)
    chart_type: Optional[ChartType] = None
    query: Optional[str] = None


class ReorderWidgetsRequest(BaseModel):
    widget_order: List[str]


class WidgetDataResponse(BaseModel):
    widget_id: str
    data: Any
    timestamp: str
    refresh_interval: Optional[int] = None


@router.post("/")
async def create_dashboard(request: CreateDashboardRequest):
    """Create a new dashboard"""
    try:
        dashboard = dashboard_manager.create_dashboard(
            user_id=request.user_id,
            name=request.name,
            description=request.description
        )
        return dashboard.model_dump()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to create dashboard")


@router.post("/from-template/{template_id}")
async def create_from_template(template_id: str, request: CreateFromTemplateRequest):
    """Create dashboard from a template"""
    try:
        dashboard = dashboard_manager.create_from_template(
            template_id=template_id,
            user_id=request.user_id,
            name=request.name
        )
        if dashboard:
            return dashboard.model_dump()
        raise HTTPException(status_code=404, detail="Template not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to create dashboard from template")


@router.get("/{dashboard_id}")
async def get_dashboard(dashboard_id: str):
    """Get dashboard by ID"""
    try:
        dashboard = dashboard_manager.get_dashboard(dashboard_id)
        if dashboard:
            return dashboard.model_dump()
        raise HTTPException(status_code=404, detail="Dashboard not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to get dashboard")


@router.get("/user/{user_id}")
async def get_user_dashboards(user_id: str):
    """Get all dashboards for a user"""
    try:
        dashboards = dashboard_manager.get_user_dashboards(user_id)
        return [d.model_dump() for d in dashboards]
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to get user dashboards")


@router.put("/{dashboard_id}")
async def update_dashboard(dashboard_id: str, request: UpdateDashboardRequest):
    """Update dashboard"""
    try:
        updates = request.model_dump(exclude_none=True)
        if not updates:
            raise HTTPException(status_code=400, detail="No fields to update")

        dashboard = dashboard_manager.update_dashboard(dashboard_id, updates)
        if dashboard:
            return dashboard.model_dump()
        raise HTTPException(status_code=404, detail="Dashboard not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to update dashboard")


@router.delete("/{dashboard_id}")
async def delete_dashboard(dashboard_id: str):
    """Delete dashboard"""
    try:
        success = dashboard_manager.delete_dashboard(dashboard_id)
        if success:
            return {"status": "success", "message": "Dashboard deleted successfully"}
        raise HTTPException(status_code=404, detail="Dashboard not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to delete dashboard")


@router.post("/{dashboard_id}/widgets")
async def add_widget(dashboard_id: str, request: AddWidgetRequest):
    """Add widget to dashboard"""
    try:
        widget = DashboardWidget(
            title=request.title,
            type=request.type,
            component=request.component,
            position=request.position,
            settings=request.settings or {},
            data_source=request.data_source,
            refresh_interval=request.refresh_interval,
            chart_type=request.chart_type,
            query=request.query
        )

        result = dashboard_manager.add_widget(dashboard_id, widget)
        if result:
            return {"status": "success", "widget": result.model_dump()}
        raise HTTPException(status_code=404, detail="Dashboard not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to add widget")


@router.put("/{dashboard_id}/widgets/{widget_id}")
async def update_widget(dashboard_id: str, widget_id: str, request: UpdateWidgetRequest):
    """Update widget in dashboard"""
    try:
        updates = request.model_dump(exclude_none=True)
        if not updates:
            raise HTTPException(status_code=400, detail="No fields to update")

        widget = dashboard_manager.update_widget(dashboard_id, widget_id, updates)
        if widget:
            return {"status": "success", "widget": widget.model_dump()}
        raise HTTPException(status_code=404, detail="Dashboard or widget not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to update widget")


@router.delete("/{dashboard_id}/widgets/{widget_id}")
async def remove_widget(dashboard_id: str, widget_id: str):
    """Remove widget from dashboard"""
    try:
        success = dashboard_manager.remove_widget(dashboard_id, widget_id)
        if success:
            return {"status": "success", "message": "Widget removed successfully"}
        raise HTTPException(status_code=404, detail="Dashboard or widget not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to remove widget")


@router.post("/{dashboard_id}/widgets/reorder")
async def reorder_widgets(dashboard_id: str, request: ReorderWidgetsRequest):
    """Reorder widgets in dashboard"""
    try:
        success = dashboard_manager.reorder_widgets(dashboard_id, request.widget_order)
        if success:
            return {"status": "success", "message": "Widgets reordered successfully"}
        raise HTTPException(status_code=404, detail="Dashboard not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to reorder widgets")


@router.get("/{dashboard_id}/widgets/{widget_id}/data")
async def get_widget_data(dashboard_id: str, widget_id: str):
    """Get data for a widget"""
    try:
        dashboard = dashboard_manager.get_dashboard(dashboard_id)
        if not dashboard:
            raise HTTPException(status_code=404, detail="Dashboard not found")

        widget = None
        for w in dashboard.widgets:
            if w.id == widget_id:
                widget = w
                break

        if not widget:
            raise HTTPException(status_code=404, detail="Widget not found")

        data = dashboard_manager.get_widget_data(widget)
        return {
            "widget_id": data.widget_id,
            "data": data.data,
            "timestamp": data.timestamp.isoformat(),
            "refresh_interval": data.refresh_interval
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to get widget data")


@router.get("/{dashboard_id}/export")
async def export_dashboard(dashboard_id: str):
    """Export dashboard configuration"""
    try:
        dashboard = dashboard_manager.get_dashboard(dashboard_id)
        if dashboard:
            return {
                "status": "success",
                "dashboard": dashboard.model_dump(),
                "export_timestamp": datetime.now().isoformat()
            }
        raise HTTPException(status_code=404, detail="Dashboard not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to export dashboard")


@router.get("/templates/available")
async def get_templates():
    """Get available dashboard templates"""
    try:
        templates = dashboard_manager.get_templates()
        return {"templates": [t.model_dump() for t in templates]}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to get templates")


@router.get("/data-sources/list")
async def get_data_sources():
    """Get available data source providers"""
    try:
        sources = list(dashboard_manager._data_providers.keys())
        return {
            "data_sources": sources,
            "descriptions": {
                "performance": "System performance metrics (CPU, memory, disk)",
                "code_review": "Code review statistics and ratings",
                "git": "Git repository statistics",
                "learning": "Learning progress tracking",
                "collaboration": "Team collaboration metrics"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to get data sources")


@router.get("/widget-types/list")
async def get_widget_types():
    """Get available widget types"""
    return {
        "widget_types": [
            {"id": "chart", "name": "Chart", "description": "Data visualization charts"},
            {"id": "table", "name": "Table", "description": "Data tables"},
            {"id": "text", "name": "Text", "description": "Text content"},
            {"id": "code", "name": "Code", "description": "Code snippets"},
            {"id": "metric", "name": "Metric", "description": "Single value metrics"},
            {"id": "progress", "name": "Progress", "description": "Progress bars"},
            {"id": "list", "name": "List", "description": "Item lists"},
            {"id": "graph", "name": "Graph", "description": "Network graphs"}
        ],
        "chart_types": [
            {"id": "line", "name": "Line Chart"},
            {"id": "bar", "name": "Bar Chart"},
            {"id": "pie", "name": "Pie Chart"},
            {"id": "area", "name": "Area Chart"},
            {"id": "scatter", "name": "Scatter Plot"}
        ]
    }
