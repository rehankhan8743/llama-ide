from typing import Dict, List, Any, Optional, Callable
from pydantic import BaseModel, Field
import json
import logging
from pathlib import Path
from datetime import datetime
from enum import Enum
import uuid

logger = logging.getLogger(__name__)


class WidgetType(str, Enum):
    """Available widget types"""
    CHART = "chart"
    TABLE = "table"
    TEXT = "text"
    CODE = "code"
    METRIC = "metric"
    PROGRESS = "progress"
    LIST = "list"
    GRAPH = "graph"


class ChartType(str, Enum):
    """Available chart types"""
    LINE = "line"
    BAR = "bar"
    PIE = "pie"
    AREA = "area"
    SCATTER = "scatter"


class DashboardWidget(BaseModel):
    """Individual dashboard widget configuration"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    type: WidgetType
    component: str  # React component name
    position: Dict[str, int] = Field(default_factory=lambda: {"x": 0, "y": 0, "w": 6, "h": 4})
    settings: Dict[str, Any] = Field(default_factory=dict)
    data_source: Optional[str] = None
    refresh_interval: Optional[int] = Field(default=None, ge=5)  # seconds, min 5s
    chart_type: Optional[ChartType] = None  # For chart widgets
    query: Optional[str] = None  # Query for data source


class DashboardLayout(BaseModel):
    """Dashboard layout configuration"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    widgets: List[DashboardWidget] = Field(default_factory=list)
    user_id: str
    is_public: bool = False
    tags: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    theme: str = "default"  # default, dark, light
    layout_type: str = "grid"  # grid, freeform


class WidgetData(BaseModel):
    """Widget data response"""
    widget_id: str
    data: Any
    timestamp: datetime = Field(default_factory=datetime.now)
    refresh_interval: Optional[int] = None


class DashboardTemplate(BaseModel):
    """Pre-defined dashboard template"""
    id: str
    name: str
    description: str
    category: str
    widgets: List[DashboardWidget]
    thumbnail: Optional[str] = None


class DashboardManager:
    """Manage dashboard layouts and widgets"""

    def __init__(self, dashboards_dir: str = "./dashboards"):
        self.dashboards_dir = Path(dashboards_dir)
        self.dashboards_dir.mkdir(parents=True, exist_ok=True)
        self._dashboards: Dict[str, DashboardLayout] = {}
        self._data_providers: Dict[str, Callable] = {}
        self._load_dashboards()
        self._register_default_data_providers()

    def _load_dashboards(self) -> None:
        """Load dashboards from storage"""
        for file_path in self.dashboards_dir.glob("*.json"):
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    # Parse datetime strings back to datetime objects
                    if isinstance(data.get("created_at"), str):
                        data["created_at"] = datetime.fromisoformat(data["created_at"])
                    if isinstance(data.get("updated_at"), str):
                        data["updated_at"] = datetime.fromisoformat(data["updated_at"])
                    dashboard = DashboardLayout(**data)
                    self._dashboards[dashboard.id] = dashboard
            except Exception as e:
                logger.error(f"Error loading dashboard {file_path}: {e}")

    def _register_default_data_providers(self) -> None:
        """Register default data source providers"""
        self._data_providers["performance"] = self._get_performance_data
        self._data_providers["code_review"] = self._get_code_review_data
        self._data_providers["git"] = self._get_git_data
        self._data_providers["learning"] = self._get_learning_data
        self._data_providers["collaboration"] = self._get_collaboration_data

    def _get_performance_data(self, query: Optional[str] = None) -> Dict[str, Any]:
        """Get performance metrics data"""
        try:
            from ..services.performance_optimizer import performance_optimizer
            metrics = performance_optimizer.metrics.get_system_metrics()
            return {
                "cpu": metrics.get("cpu_percent", 0),
                "memory": metrics.get("memory_percent", 0),
                "disk": metrics.get("disk_usage", 0),
                "gc_objects": metrics.get("gc_objects", 0)
            }
        except Exception as e:
            logger.warning(f"Error getting performance data: {e}")
            return {"cpu": 0, "memory": 0, "disk": 0, "error": str(e)}

    def _get_code_review_data(self, query: Optional[str] = None) -> Dict[str, Any]:
        """Get code review statistics"""
        return {
            "issues": 0,
            "complexity": 0.0,
            "rating": 0.0,
            "last_review": None
        }

    def _get_git_data(self, query: Optional[str] = None) -> Dict[str, Any]:
        """Get git repository statistics"""
        return {
            "commits": 0,
            "branches": 0,
            "contributors": 0,
            "last_commit": None
        }

    def _get_learning_data(self, query: Optional[str] = None) -> Dict[str, Any]:
        """Get learning progress data"""
        return {
            "completed_topics": 0,
            "progress_percentage": 0.0,
            "streak_days": 0
        }

    def _get_collaboration_data(self, query: Optional[str] = None) -> Dict[str, Any]:
        """Get collaboration session data"""
        return {
            "active_sessions": 0,
            "online_users": 0,
            "recent_messages": []
        }

    def create_dashboard(self, user_id: str, name: str, description: Optional[str] = None) -> DashboardLayout:
        """Create a new dashboard"""
        dashboard = DashboardLayout(
            name=name,
            description=description,
            user_id=user_id
        )
        self._dashboards[dashboard.id] = dashboard
        self._save_dashboard(dashboard)
        logger.info(f"Created dashboard {dashboard.id} for user {user_id}")
        return dashboard

    def get_dashboard(self, dashboard_id: str) -> Optional[DashboardLayout]:
        """Get dashboard by ID"""
        return self._dashboards.get(dashboard_id)

    def get_user_dashboards(self, user_id: str) -> List[DashboardLayout]:
        """Get all dashboards for a user"""
        return [
            dashboard for dashboard in self._dashboards.values()
            if dashboard.user_id == user_id
        ]

    def update_dashboard(self, dashboard_id: str, updates: Dict[str, Any]) -> Optional[DashboardLayout]:
        """Update dashboard"""
        if dashboard_id not in self._dashboards:
            return None

        dashboard = self._dashboards[dashboard_id]

        # Update allowed fields
        allowed_fields = ["name", "description", "is_public", "tags", "theme", "layout_type"]
        for key, value in updates.items():
            if key in allowed_fields and hasattr(dashboard, key):
                setattr(dashboard, key, value)

        dashboard.updated_at = datetime.now()
        self._save_dashboard(dashboard)
        return dashboard

    def delete_dashboard(self, dashboard_id: str) -> bool:
        """Delete dashboard"""
        if dashboard_id not in self._dashboards:
            return False

        del self._dashboards[dashboard_id]

        # Delete file
        dashboard_file = self.dashboards_dir / f"{dashboard_id}.json"
        try:
            dashboard_file.unlink(missing_ok=True)
            logger.info(f"Deleted dashboard {dashboard_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting dashboard file {dashboard_id}: {e}")
            return False

    def add_widget(self, dashboard_id: str, widget: DashboardWidget) -> Optional[DashboardWidget]:
        """Add widget to dashboard"""
        if dashboard_id not in self._dashboards:
            return None

        dashboard = self._dashboards[dashboard_id]
        dashboard.widgets.append(widget)
        dashboard.updated_at = datetime.now()
        self._save_dashboard(dashboard)
        logger.info(f"Added widget {widget.id} to dashboard {dashboard_id}")
        return widget

    def update_widget(self, dashboard_id: str, widget_id: str, updates: Dict[str, Any]) -> Optional[DashboardWidget]:
        """Update widget in dashboard"""
        if dashboard_id not in self._dashboards:
            return None

        dashboard = self._dashboards[dashboard_id]

        for widget in dashboard.widgets:
            if widget.id == widget_id:
                allowed_fields = ["title", "position", "settings", "data_source", "refresh_interval", "chart_type", "query"]
                for key, value in updates.items():
                    if key in allowed_fields and hasattr(widget, key):
                        setattr(widget, key, value)

                dashboard.updated_at = datetime.now()
                self._save_dashboard(dashboard)
                return widget

        return None

    def remove_widget(self, dashboard_id: str, widget_id: str) -> bool:
        """Remove widget from dashboard"""
        if dashboard_id not in self._dashboards:
            return False

        dashboard = self._dashboards[dashboard_id]
        original_count = len(dashboard.widgets)
        dashboard.widgets = [w for w in dashboard.widgets if w.id != widget_id]

        if len(dashboard.widgets) < original_count:
            dashboard.updated_at = datetime.now()
            self._save_dashboard(dashboard)
            logger.info(f"Removed widget {widget_id} from dashboard {dashboard_id}")
            return True

        return False

    def reorder_widgets(self, dashboard_id: str, widget_order: List[str]) -> bool:
        """Reorder widgets in dashboard"""
        if dashboard_id not in self._dashboards:
            return False

        dashboard = self._dashboards[dashboard_id]
        widget_map = {w.id: w for w in dashboard.widgets}

        new_widgets = []
        for widget_id in widget_order:
            if widget_id in widget_map:
                new_widgets.append(widget_map[widget_id])

        # Add any widgets not in the order list
        for widget in dashboard.widgets:
            if widget.id not in widget_order:
                new_widgets.append(widget)

        dashboard.widgets = new_widgets
        dashboard.updated_at = datetime.now()
        self._save_dashboard(dashboard)
        return True

    def get_widget_data(self, widget: DashboardWidget) -> WidgetData:
        """Get data for a widget"""
        if not widget.data_source:
            return WidgetData(widget_id=widget.id, data={"message": "No data source configured"})

        provider = self._data_providers.get(widget.data_source)
        if provider:
            data = provider(widget.query)
            return WidgetData(
                widget_id=widget.id,
                data=data,
                refresh_interval=widget.refresh_interval
            )

        return WidgetData(
            widget_id=widget.id,
            data={"message": f"Unknown data source: {widget.data_source}"}
        )

    def register_data_provider(self, name: str, provider: Callable) -> None:
        """Register a custom data provider"""
        self._data_providers[name] = provider
        logger.info(f"Registered data provider: {name}")

    def get_templates(self) -> List[DashboardTemplate]:
        """Get available dashboard templates"""
        return [
            DashboardTemplate(
                id="developer",
                name="Developer Dashboard",
                description="Essential widgets for developers",
                category="default",
                widgets=[
                    DashboardWidget(
                        title="Performance Metrics",
                        type=WidgetType.METRIC,
                        component="MetricCard",
                        data_source="performance",
                        position={"x": 0, "y": 0, "w": 6, "h": 2}
                    ),
                    DashboardWidget(
                        title="Code Review Stats",
                        type=WidgetType.TABLE,
                        component="DataTable",
                        data_source="code_review",
                        position={"x": 6, "y": 0, "w": 6, "h": 4}
                    ),
                    DashboardWidget(
                        title="Git Activity",
                        type=WidgetType.CHART,
                        component="LineChart",
                        chart_type=ChartType.LINE,
                        data_source="git",
                        position={"x": 0, "y": 2, "w": 6, "h": 4}
                    )
                ]
            ),
            DashboardTemplate(
                id="learning",
                name="Learning Dashboard",
                description="Track your learning progress",
                category="education",
                widgets=[
                    DashboardWidget(
                        title="Progress Overview",
                        type=WidgetType.PROGRESS,
                        component="ProgressBar",
                        data_source="learning",
                        position={"x": 0, "y": 0, "w": 12, "h": 2}
                    ),
                    DashboardWidget(
                        title="Completed Topics",
                        type=WidgetType.LIST,
                        component="TopicList",
                        data_source="learning",
                        position={"x": 0, "y": 2, "w": 6, "h": 4}
                    )
                ]
            ),
            DashboardTemplate(
                id="collaboration",
                name="Team Collaboration",
                description="Monitor team activity",
                category="team",
                widgets=[
                    DashboardWidget(
                        title="Active Sessions",
                        type=WidgetType.METRIC,
                        component="MetricCard",
                        data_source="collaboration",
                        position={"x": 0, "y": 0, "w": 4, "h": 2}
                    ),
                    DashboardWidget(
                        title="Online Users",
                        type=WidgetType.METRIC,
                        component="MetricCard",
                        data_source="collaboration",
                        position={"x": 4, "y": 0, "w": 4, "h": 2}
                    )
                ]
            )
        ]

    def create_from_template(self, template_id: str, user_id: str, name: Optional[str] = None) -> Optional[DashboardLayout]:
        """Create dashboard from template"""
        templates = {t.id: t for t in self.get_templates()}

        if template_id not in templates:
            return None

        template = templates[template_id]
        dashboard = self.create_dashboard(
            user_id=user_id,
            name=name or template.name,
            description=template.description
        )

        # Copy widgets from template
        for widget_template in template.widgets:
            widget_copy = DashboardWidget(
                title=widget_template.title,
                type=widget_template.type,
                component=widget_template.component,
                position=widget_template.position.copy(),
                settings=widget_template.settings.copy(),
                data_source=widget_template.data_source,
                refresh_interval=widget_template.refresh_interval,
                chart_type=widget_template.chart_type
            )
            dashboard.widgets.append(widget_copy)

        self._save_dashboard(dashboard)
        return dashboard

    def _save_dashboard(self, dashboard: DashboardLayout) -> None:
        """Save dashboard to file"""
        try:
            dashboard_file = self.dashboards_dir / f"{dashboard.id}.json"
            dashboard_dict = dashboard.model_dump()

            # Convert datetime objects to ISO format strings
            dashboard_dict["created_at"] = dashboard.created_at.isoformat()
            dashboard_dict["updated_at"] = dashboard.updated_at.isoformat()

            with open(dashboard_file, 'w') as f:
                json.dump(dashboard_dict, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving dashboard {dashboard.id}: {e}")


# Initialize dashboard manager
dashboard_manager = DashboardManager()
