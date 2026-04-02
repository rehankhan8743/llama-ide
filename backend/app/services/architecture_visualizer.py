import ast
import json
import logging
from typing import Dict, List, Any, Optional, Set, Tuple
from pydantic import BaseModel
from collections import defaultdict
from pathlib import Path

logger = logging.getLogger(__name__)

# Optional networkx import
try:
    import networkx as nx
    NETWORKX_AVAILABLE = True
except ImportError:
    NETWORKX_AVAILABLE = False
    logger.warning("networkx not available, graph functionality limited")


class CodebaseStructure(BaseModel):
    files: List[str]
    classes: Dict[str, List[str]]  # class_name: methods
    functions: List[str]
    dependencies: Dict[str, List[str]]  # file: dependencies
    entry_points: List[str]
    errors: List[str] = []  # Track analysis errors


class ArchitectureComponent(BaseModel):
    name: str
    type: str  # class, function, module
    dependencies: List[str]
    methods: List[str]
    properties: List[str]
    file_path: str
    line_number: int = 0
    complexity_score: float = 0.0


class ArchitectureDiagram(BaseModel):
    components: List[ArchitectureComponent]
    relationships: List[Dict[str, str]]  # source, target, type
    layers: List[str]
    entry_points: List[str]
    metrics: Dict[str, Any] = {}


class CodeAnalyzer:
    """Analyze Python source code for architectural patterns"""

    def __init__(self):
        self.structure = CodebaseStructure(
            files=[],
            classes={},
            functions=[],
            dependencies={},
            entry_points=[],
            errors=[]
        )

    def _is_entry_point(self, node: ast.If) -> bool:
        """Check if node is if __name__ == '__main__' pattern"""
        try:
            if not isinstance(node.test, ast.Compare):
                return False

            # Check left side is __name__
            left = node.test.left
            if not isinstance(left, ast.Name) or left.id != "__name__":
                return False

            # Check comparison is == "__main__"
            if len(node.test.comparators) != 1:
                return False

            comparator = node.test.comparators[0]
            if isinstance(comparator, ast.Constant) and comparator.value == "__main__":
                return True
            if isinstance(comparator, ast.Str) and comparator.s == "__main__":  # Python < 3.8
                return True

            return False
        except Exception:
            return False

    def analyze_file(self, file_path: str, content: str) -> Dict[str, Any]:
        """Analyze a single Python file"""
        file_analysis = {
            "classes": [],
            "functions": [],
            "imports": [],
            "entry_points": [],
            "complexity": 0
        }

        try:
            tree = ast.parse(content)

            # Calculate cyclomatic complexity approximation
            complexity = 1
            for node in ast.walk(tree):
                if isinstance(node, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                    complexity += 1
                elif isinstance(node, ast.FunctionDef):
                    file_analysis["functions"].append({
                        "name": node.name,
                        "line_number": node.lineno,
                        "is_async": isinstance(node, ast.AsyncFunctionDef),
                        "args": len(node.args.args)
                    })
                elif isinstance(node, ast.ClassDef):
                    methods = []
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            methods.append(item.name)
                            complexity += 1
                        elif isinstance(item, ast.AsyncFunctionDef):
                            methods.append(item.name)
                            complexity += 1

                    file_analysis["classes"].append({
                        "name": node.name,
                        "methods": methods,
                        "line_number": node.lineno,
                        "bases": [base.id if isinstance(base, ast.Name) else str(base) for base in node.bases]
                    })
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            file_analysis["imports"].append(alias.name)
                    else:  # ImportFrom
                        module = node.module or ""
                        for alias in node.names:
                            full_name = f"{module}.{alias.name}" if module else alias.name
                            file_analysis["imports"].append(full_name)
                elif isinstance(node, ast.If) and self._is_entry_point(node):
                    file_analysis["entry_points"].append({
                        "type": "main_guard",
                        "line_number": node.lineno
                    })

            file_analysis["complexity"] = complexity
            return file_analysis

        except SyntaxError as e:
            logger.warning(f"Syntax error in {file_path}: {e}")
            return {"error": f"Syntax error: {str(e)}"}
        except Exception as e:
            logger.error(f"Error analyzing {file_path}: {e}")
            return {"error": f"Analysis error: {str(e)}"}

    def analyze_codebase(self, files: Dict[str, str]) -> CodebaseStructure:
        """Analyze entire codebase"""
        all_classes = {}
        all_functions = []
        all_dependencies = {}
        all_entry_points = []
        errors = []

        for file_path, content in files.items():
            analysis = self.analyze_file(file_path, content)

            if "error" in analysis:
                errors.append(f"{file_path}: {analysis['error']}")
                continue

            # Collect classes
            for cls in analysis["classes"]:
                all_classes[f"{file_path}:{cls['name']}"] = cls["methods"]

            # Collect functions
            for func in analysis["functions"]:
                all_functions.append(f"{file_path}:{func['name']}")

            # Collect dependencies
            all_dependencies[file_path] = analysis["imports"]

            # Collect entry points
            for ep in analysis["entry_points"]:
                all_entry_points.append(f"{file_path}:{ep['type']}")

        return CodebaseStructure(
            files=list(files.keys()),
            classes=all_classes,
            functions=all_functions,
            dependencies=all_dependencies,
            entry_points=all_entry_points,
            errors=errors
        )


class ArchitectureVisualizer:
    """Visualize codebase architecture as diagrams"""

    def __init__(self):
        self.analyzer = CodeAnalyzer()
        self.graph = nx.DiGraph() if NETWORKX_AVAILABLE else None

    def generate_diagram(self, codebase_structure: CodebaseStructure) -> ArchitectureDiagram:
        """Generate architecture diagram from codebase structure"""
        components = []
        relationships = []

        if self.graph is not None:
            self.graph.clear()

        # Create components for files
        for file_path in codebase_structure.files:
            deps = codebase_structure.dependencies.get(file_path, [])
            component = ArchitectureComponent(
                name=Path(file_path).name,
                type="module",
                dependencies=deps,
                methods=[],
                properties=[],
                file_path=file_path
            )
            components.append(component)

            if self.graph is not None:
                self.graph.add_node(file_path, type="module")

        # Create components for classes
        for class_full_name, methods in codebase_structure.classes.items():
            if ":" in class_full_name:
                file_path, class_short_name = class_full_name.rsplit(":", 1)
            else:
                file_path, class_short_name = "", class_full_name

            component = ArchitectureComponent(
                name=class_short_name,
                type="class",
                dependencies=[],
                methods=methods,
                properties=[],
                file_path=file_path
            )
            components.append(component)

            if self.graph is not None:
                self.graph.add_node(class_short_name, type="class")
                if file_path:
                    self.graph.add_edge(file_path, class_short_name, relation="contains")
                    relationships.append({
                        "source": file_path,
                        "target": class_short_name,
                        "type": "contains"
                    })

        # Create relationships based on dependencies
        for file_path, deps in codebase_structure.dependencies.items():
            for dep in deps:
                # Simplify dependency name
                dep_simple = dep.split(".")[-1] if "." in dep else dep
                relationships.append({
                    "source": file_path,
                    "target": dep_simple,
                    "type": "imports"
                })

                if self.graph is not None:
                    self.graph.add_edge(file_path, dep_simple, relation="imports")

        # Determine layers
        layers = self._determine_layers(components)

        # Calculate metrics
        metrics = self.get_complexity_metrics() if self.graph else {}

        return ArchitectureDiagram(
            components=components,
            relationships=relationships,
            layers=layers,
            entry_points=codebase_structure.entry_points,
            metrics=metrics
        )

    def _determine_layers(self, components: List[ArchitectureComponent]) -> List[str]:
        """Determine architectural layers based on dependencies"""
        layers = set()

        for comp in components:
            path_lower = comp.file_path.lower()

            # Simple layer detection based on path/name conventions
            if any(x in path_lower for x in ["api", "routes", "views", "endpoints"]):
                layers.add("api/presentation")
            elif any(x in path_lower for x in ["service", "business", "logic"]):
                layers.add("business_logic")
            elif any(x in path_lower for x in ["model", "data", "db", "repository"]):
                layers.add("data_access")
            elif any(x in path_lower for x in ["util", "helper", "common", "shared"]):
                layers.add("utilities")
            elif "test" in path_lower:
                layers.add("tests")
            else:
                layers.add("application")

        return sorted(list(layers))

    def highlight_dependencies(self, component_name: str) -> Dict[str, List[str]]:
        """Highlight dependencies of a component"""
        if self.graph is None:
            return {"incoming": [], "outgoing": []}

        if component_name in self.graph:
            predecessors = list(self.graph.predecessors(component_name))
            successors = list(self.graph.successors(component_name))
            return {
                "incoming": predecessors,
                "outgoing": successors
            }
        return {"incoming": [], "outgoing": []}

    def find_cycles(self) -> List[List[str]]:
        """Find circular dependencies in the codebase"""
        if self.graph is None:
            return []

        try:
            cycles = list(nx.simple_cycles(self.graph))
            return cycles
        except Exception as e:
            logger.error(f"Error finding cycles: {e}")
            return []

    def find_orphan_components(self) -> List[str]:
        """Find components with no connections"""
        if self.graph is None:
            return []

        orphans = []
        for node in self.graph.nodes():
            if self.graph.degree(node) == 0:
                orphans.append(node)
        return orphans

    def export_as_image(self, format: str = "png") -> bytes:
        """Export diagram as image"""
        if not NETWORKX_AVAILABLE:
            raise ImportError("networkx required for image export")

        try:
            import matplotlib.pyplot as plt

            if self.graph is None or len(self.graph.nodes()) == 0:
                raise ValueError("No graph to export")

            # Create layout
            pos = nx.spring_layout(self.graph, k=2, iterations=50)

            # Separate nodes by type
            modules = [n for n, attrs in self.graph.nodes(data=True) if attrs.get("type") == "module"]
            classes = [n for n, attrs in self.graph.nodes(data=True) if attrs.get("type") == "class"]

            plt.figure(figsize=(12, 8))

            # Draw nodes
            if modules:
                nx.draw_networkx_nodes(self.graph, pos, nodelist=modules,
                                       node_color='lightblue', node_size=800, label="Modules")
            if classes:
                nx.draw_networkx_nodes(self.graph, pos, nodelist=classes,
                                       node_color='lightgreen', node_size=600, label="Classes")

            nx.draw_networkx_labels(self.graph, pos, font_size=8)

            # Draw edges with different styles
            edges = self.graph.edges(data=True)
            contains_edges = [(u, v) for u, v, d in edges if d.get("relation") == "contains"]
            import_edges = [(u, v) for u, v, d in edges if d.get("relation") == "imports"]

            if contains_edges:
                nx.draw_networkx_edges(self.graph, pos, edgelist=contains_edges,
                                       edge_color='blue', style='dashed', arrows=True)
            if import_edges:
                nx.draw_networkx_edges(self.graph, pos, edgelist=import_edges,
                                       edge_color='gray', arrows=True)

            plt.legend()
            plt.axis('off')

            # Save to bytes
            import io
            buf = io.BytesIO()
            plt.savefig(buf, format=format, bbox_inches='tight', dpi=150)
            buf.seek(0)
            plt.close()
            return buf.getvalue()

        except ImportError:
            raise ImportError("matplotlib required for image export")
        except Exception as e:
            logger.error(f"Error exporting image: {e}")
            raise Exception(f"Error exporting image: {str(e)}")

    def export_as_json(self) -> str:
        """Export diagram as JSON"""
        if self.graph is None:
            return json.dumps({"nodes": [], "edges": []})

        nodes = []
        for node, attrs in self.graph.nodes(data=True):
            nodes.append({
                "id": node,
                "attributes": attrs
            })

        edges = []
        for source, target, attrs in self.graph.edges(data=True):
            edges.append({
                "source": source,
                "target": target,
                "attributes": attrs
            })

        return json.dumps({
            "nodes": nodes,
            "edges": edges,
            "metrics": self.get_complexity_metrics()
        }, indent=2)

    def export_as_dot(self) -> str:
        """Export diagram as Graphviz DOT format"""
        if self.graph is None:
            return "digraph G {}"

        lines = ["digraph G {"]

        # Add nodes
        for node, attrs in self.graph.nodes(data=True):
            node_type = attrs.get("type", "unknown")
            color = "lightblue" if node_type == "module" else "lightgreen"
            lines.append(f'    "{node}" [style=filled, fillcolor={color}, label="{node}"];')

        # Add edges
        for source, target, attrs in self.graph.edges(data=True):
            relation = attrs.get("relation", "")
            style = "dashed" if relation == "contains" else "solid"
            lines.append(f'    "{source}" -> "{target}" [style={style}];')

        lines.append("}")
        return "\n".join(lines)

    def get_complexity_metrics(self) -> Dict[str, Any]:
        """Calculate complexity metrics"""
        if self.graph is None:
            return {"error": "networkx not available"}

        try:
            metrics = {
                "node_count": self.graph.number_of_nodes(),
                "edge_count": self.graph.number_of_edges(),
                "density": nx.density(self.graph),
            }

            # Cyclomatic complexity approximation
            undirected = self.graph.to_undirected()
            try:
                components = nx.number_connected_components(undirected)
                cyclomatic = self.graph.number_of_edges() - self.graph.number_of_nodes() + components
                metrics["cyclomatic_complexity"] = max(1, cyclomatic)
            except Exception:
                metrics["cyclomatic_complexity"] = 1

            # Centralization
            metrics["centralization"] = self._calculate_centralization()

            # Find most connected nodes
            if metrics["node_count"] > 0:
                degrees = dict(self.graph.degree())
                sorted_nodes = sorted(degrees.items(), key=lambda x: x[1], reverse=True)
                metrics["most_connected"] = sorted_nodes[:5]

            return metrics

        except Exception as e:
            logger.error(f"Error calculating metrics: {e}")
            return {"error": str(e)}

    def _calculate_centralization(self) -> float:
        """Calculate graph centralization"""
        if self.graph is None or len(self.graph.nodes()) == 0:
            return 0.0

        try:
            degrees = [d for n, d in self.graph.degree()]
            if not degrees or len(degrees) < 2:
                return 0.0

            max_degree = max(degrees)
            if max_degree == 0:
                return 0.0

            centralization = sum(max_degree - d for d in degrees) / (len(degrees) * (len(degrees) - 1))
            return round(centralization, 4)
        except Exception:
            return 0.0

    def generate_summary(self, codebase_structure: CodebaseStructure) -> Dict[str, Any]:
        """Generate a summary report of the codebase"""
        total_classes = len(codebase_structure.classes)
        total_functions = len(codebase_structure.functions)
        total_files = len(codebase_structure.files)

        # Count imports
        total_imports = sum(len(deps) for deps in codebase_structure.dependencies.values())

        # Calculate average dependencies per file
        avg_deps = total_imports / total_files if total_files > 0 else 0

        # Find most dependent file
        most_dependent = max(
            codebase_structure.dependencies.items(),
            key=lambda x: len(x[1]),
            default=("", [])
        )

        return {
            "summary": {
                "total_files": total_files,
                "total_classes": total_classes,
                "total_functions": total_functions,
                "total_imports": total_imports,
                "avg_dependencies_per_file": round(avg_deps, 2),
                "most_dependent_file": most_dependent[0] if most_dependent[0] else None,
                "most_dependent_count": len(most_dependent[1]),
                "entry_points": len(codebase_structure.entry_points),
                "analysis_errors": len(codebase_structure.errors)
            },
            "files_analyzed": codebase_structure.files,
            "errors": codebase_structure.errors
        }


# Initialize visualizer
architecture_visualizer = ArchitectureVisualizer()
