from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional
import json
import logging
from ..services.architecture_visualizer import (
    architecture_visualizer,
    CodebaseStructure,
    ArchitectureDiagram
)

router = APIRouter(prefix="/visualization")
logger = logging.getLogger(__name__)


class AnalyzeCodebaseRequest(BaseModel):
    files: Dict[str, str]  # file_path: content


class HighlightDependenciesRequest(BaseModel):
    component_name: str


class ExportDiagramRequest(BaseModel):
    format: str = Field(default="json", regex="^(json|png|svg|dot)$")


class CompareVersionsRequest(BaseModel):
    versions: Dict[str, AnalyzeCodebaseRequest]


@router.post("/analyze")
async def analyze_codebase(request: AnalyzeCodebaseRequest):
    """Analyze codebase structure"""
    try:
        structure = architecture_visualizer.analyzer.analyze_codebase(request.files)
        return structure.model_dump()
    except Exception as e:
        logger.exception("Error analyzing codebase")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/diagram")
async def generate_diagram(request: AnalyzeCodebaseRequest):
    """Generate architecture diagram"""
    try:
        structure = architecture_visualizer.analyzer.analyze_codebase(request.files)
        diagram = architecture_visualizer.generate_diagram(structure)
        return diagram.model_dump()
    except Exception as e:
        logger.exception("Error generating diagram")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/highlight-dependencies")
async def highlight_dependencies(request: HighlightDependenciesRequest):
    """Highlight dependencies of a component"""
    try:
        dependencies = architecture_visualizer.highlight_dependencies(request.component_name)
        return dependencies
    except Exception as e:
        logger.exception("Error highlighting dependencies")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/export")
async def export_diagram(request: AnalyzeCodebaseRequest, format: str = "json"):
    """Export diagram in specified format (json, png, svg, dot)"""
    try:
        # Analyze and generate diagram first
        structure = architecture_visualizer.analyzer.analyze_codebase(request.files)
        architecture_visualizer.generate_diagram(structure)

        if format == "json":
            json_data = architecture_visualizer.export_as_json()
            return Response(content=json_data, media_type="application/json")

        elif format == "png":
            image_data = architecture_visualizer.export_as_image(format="png")
            return Response(content=image_data, media_type="image/png")

        elif format == "svg":
            try:
                image_data = architecture_visualizer.export_as_image(format="svg")
                return Response(content=image_data, media_type="image/svg+xml")
            except Exception:
                raise HTTPException(status_code=400, detail="SVG export requires additional dependencies")

        elif format == "dot":
            dot_data = architecture_visualizer.export_as_dot()
            return Response(content=dot_data, media_type="text/plain")

        else:
            raise HTTPException(status_code=400, detail=f"Unsupported format: {format}")

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error exporting diagram")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/metrics")
async def get_complexity_metrics(request: AnalyzeCodebaseRequest):
    """Get complexity metrics for the codebase"""
    try:
        # Analyze and generate diagram first
        structure = architecture_visualizer.analyzer.analyze_codebase(request.files)
        architecture_visualizer.generate_diagram(structure)

        metrics = architecture_visualizer.get_complexity_metrics()
        return metrics
    except Exception as e:
        logger.exception("Error calculating metrics")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/summary")
async def get_codebase_summary(request: AnalyzeCodebaseRequest):
    """Get a summary report of the codebase"""
    try:
        structure = architecture_visualizer.analyzer.analyze_codebase(request.files)
        summary = architecture_visualizer.generate_summary(structure)
        return summary
    except Exception as e:
        logger.exception("Error generating summary")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cycles")
async def find_circular_dependencies(request: AnalyzeCodebaseRequest):
    """Find circular dependencies in the codebase"""
    try:
        # Analyze and generate diagram first
        structure = architecture_visualizer.analyzer.analyze_codebase(request.files)
        architecture_visualizer.generate_diagram(structure)

        cycles = architecture_visualizer.find_cycles()
        return {
            "cycles": cycles,
            "cycle_count": len(cycles),
            "has_cycles": len(cycles) > 0
        }
    except Exception as e:
        logger.exception("Error finding cycles")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/orphans")
async def find_orphan_components(request: AnalyzeCodebaseRequest):
    """Find components with no connections (orphans)"""
    try:
        # Analyze and generate diagram first
        structure = architecture_visualizer.analyzer.analyze_codebase(request.files)
        architecture_visualizer.generate_diagram(structure)

        orphans = architecture_visualizer.find_orphan_components()
        return {
            "orphans": orphans,
            "orphan_count": len(orphans)
        }
    except Exception as e:
        logger.exception("Error finding orphans")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/compare")
async def compare_architectures(request: CompareVersionsRequest):
    """Compare different versions of architecture"""
    try:
        comparisons = {}

        for version_name, version_request in request.versions.items():
            structure = architecture_visualizer.analyzer.analyze_codebase(version_request.files)
            diagram = architecture_visualizer.generate_diagram(structure)
            metrics = architecture_visualizer.get_complexity_metrics()

            comparisons[version_name] = {
                "component_count": len(diagram.components),
                "relationship_count": len(diagram.relationships),
                "layers": diagram.layers,
                "metrics": metrics,
                "entry_points": len(diagram.entry_points)
            }

        # Compare versions
        comparison_result = {
            "versions": comparisons,
            "improvements": [],
            "regressions": []
        }

        version_names = list(comparisons.keys())
        if len(version_names) >= 2:
            current = comparisons[version_names[-1]]
            previous = comparisons[version_names[-2]]

            # Check for improvements
            if current["component_count"] < previous["component_count"]:
                comparison_result["improvements"].append("Reduced component count")
            if current["metrics"].get("cyclomatic_complexity", 0) < previous["metrics"].get("cyclomatic_complexity", 0):
                comparison_result["improvements"].append("Lower cyclomatic complexity")
            if current["metrics"].get("density", 0) < previous["metrics"].get("density", 0):
                comparison_result["improvements"].append("Reduced coupling (lower density)")

            # Check for regressions
            if current["component_count"] > previous["component_count"]:
                comparison_result["regressions"].append("Increased component count")
            if current["metrics"].get("cyclomatic_complexity", 0) > previous["metrics"].get("cyclomatic_complexity", 0):
                comparison_result["regressions"].append("Higher cyclomatic complexity")

        return comparison_result
    except Exception as e:
        logger.exception("Error comparing architectures")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/formats")
async def get_export_formats():
    """Get list of available export formats"""
    return {
        "formats": [
            {"id": "json", "name": "JSON", "description": "Raw graph data as JSON", "content_type": "application/json"},
            {"id": "png", "name": "PNG Image", "description": "Visual diagram as PNG image", "content_type": "image/png"},
            {"id": "svg", "name": "SVG Image", "description": "Scalable vector graphic", "content_type": "image/svg+xml"},
            {"id": "dot", "name": "Graphviz DOT", "description": "Graphviz DOT format for custom rendering", "content_type": "text/plain"}
        ]
    }
