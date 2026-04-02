import ast
import sys
import traceback
from typing import Dict, List, Any, Optional, Callable
from pydantic import BaseModel
import time
import threading
from collections import defaultdict

class DebugPoint(BaseModel):
    file_path: str
    line_number: int
    condition: Optional[str] = None
    hit_count: int = 0
    enabled: bool = True

class VariableState(BaseModel):
    name: str
    value: Any
    type_name: str
    size: Optional[int] = None

class CallStackFrame(BaseModel):
    function_name: str
    file_path: str
    line_number: int
    variables: List[VariableState]
    locals: Dict[str, Any]

class DebugSession(BaseModel):
    id: str
    name: str
    breakpoints: List[DebugPoint]
    watch_expressions: List[str]
    call_stack: List[CallStackFrame]
    current_line: Optional[int] = None
    current_file: Optional[str] = None
    is_paused: bool = False
    variables: Dict[str, Any] = {}

class PerformanceReport(BaseModel):
    function_name: str
    execution_time: float
    call_count: int
    memory_usage: int  # bytes
    cpu_time: float

class AdvancedDebugger:
    def __init__(self):
        self.sessions: Dict[str, DebugSession] = {}
        self.global_breakpoints: Dict[str, List[DebugPoint]] = defaultdict(list)
        self.performance_data: Dict[str, List[PerformanceReport]] = defaultdict(list)
        self.trace_functions = {}

    def create_session(self, session_name: str) -> str:
        """Create a new debugging session"""
        import uuid
        session_id = str(uuid.uuid4())

        session = DebugSession(
            id=session_id,
            name=session_name,
            breakpoints=[],
            watch_expressions=[],
            call_stack=[],
            is_paused=False,
            variables={}
        )

        self.sessions[session_id] = session
        return session_id

    def add_breakpoint(self, session_id: str, file_path: str, line_number: int,
                      condition: Optional[str] = None) -> bool:
        """Add breakpoint to session"""
        if session_id in self.sessions:
            breakpoint = DebugPoint(
                file_path=file_path,
                line_number=line_number,
                condition=condition
            )
            self.sessions[session_id].breakpoints.append(breakpoint)
            return True
        return False

    def remove_breakpoint(self, session_id: str, file_path: str, line_number: int) -> bool:
        """Remove breakpoint from session"""
        if session_id in self.sessions:
            session = self.sessions[session_id]
            session.breakpoints = [
                bp for bp in session.breakpoints
                if not (bp.file_path == file_path and bp.line_number == line_number)
            ]
            return True
        return False

    def set_watch_expression(self, session_id: str, expression: str) -> bool:
        """Add watch expression to session"""
        if session_id in self.sessions:
            session = self.sessions[session_id]
            if expression not in session.watch_expressions:
                session.watch_expressions.append(expression)
            return True
        return False

    def evaluate_watch_expressions(self, session_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate all watch expressions in context"""
        if session_id not in self.sessions:
            return {}

        results = {}
        session = self.sessions[session_id]

        for expr in session.watch_expressions:
            try:
                # Evaluate expression in context
                result = eval(expr, context)
                results[expr] = {
                    "value": result,
                    "type": type(result).__name__,
                    "success": True
                }
            except Exception as e:
                results[expr] = {
                    "error": str(e),
                    "success": False
                }

        return results

    def step_through_execution(self, code: str, inputs: Dict[str, Any] = None) -> Dict[str, Any]:
        """Step through code execution with visualization"""
        try:
            # Parse code to AST
            tree = ast.parse(code)

            # Track execution steps
            execution_steps = []
            variables = inputs or {}

            # Custom visitor to trace execution
            class TraceVisitor(ast.NodeVisitor):
                def __init__(self, debugger):
                    self.debugger = debugger
                    self.step_count = 0

                def visit(self, node):
                    if isinstance(node, (ast.Assign, ast.Expr, ast.Call, ast.If, ast.For, ast.While)):
                        # Record step
                        step_info = {
                            "step": self.step_count,
                            "line": getattr(node, 'lineno', 0),
                            "type": type(node).__name__,
                            "variables": variables.copy()
                        }
                        execution_steps.append(step_info)
                        self.step_count += 1

                    # Continue visiting child nodes
                    super().visit(node)

            # Execute code with tracing
            visitor = TraceVisitor(self)
            visitor.visit(tree)

            # Execute code to get final result
            local_vars = variables.copy()
            exec(code, globals(), local_vars)

            return {
                "steps": execution_steps,
                "final_variables": local_vars,
                "success": True
            }
        except Exception as e:
            return {
                "error": str(e),
                "traceback": traceback.format_exc(),
                "success": False
            }

    def analyze_performance(self, code: str, iterations: int = 100) -> List[PerformanceReport]:
        """Analyze code performance bottlenecks"""
        performance_reports = []

        try:
            # Parse code to find functions
            tree = ast.parse(code)
            functions = [node for node in tree.body if isinstance(node, ast.FunctionDef)]

            for func in functions:
                # Create test code that calls the function
                test_code = f"""
import time
import sys
{code}

# Test function
start_time = time.perf_counter()
for _ in range({iterations}):
    result = {func.name}()
end_time = time.perf_counter()

execution_time = (end_time - start_time) / {iterations}
                """

                # Measure execution time
                start_perf = time.perf_counter()
                try:
                    local_vars = {}
                    exec(test_code, globals(), local_vars)
                    execution_time = local_vars.get('execution_time', 0)

                    # Estimate memory usage
                    memory_usage = sys.getsizeof(local_vars.get('result', None)) if 'result' in local_vars else 0

                    report = PerformanceReport(
                        function_name=func.name,
                        execution_time=execution_time,
                        call_count=iterations,
                        memory_usage=memory_usage,
                        cpu_time=time.perf_counter() - start_perf
                    )
                    performance_reports.append(report)

                except Exception as e:
                    report = PerformanceReport(
                        function_name=func.name,
                        execution_time=0,
                        call_count=0,
                        memory_usage=0,
                        cpu_time=0
                    )
                    performance_reports.append(report)

        except Exception as e:
            print(f"Performance analysis error: {e}")

        return performance_reports

    def get_session(self, session_id: str) -> Optional[DebugSession]:
        """Get debug session by ID"""
        return self.sessions.get(session_id)

    def pause_session(self, session_id: str) -> bool:
        """Pause debug session"""
        if session_id in self.sessions:
            self.sessions[session_id].is_paused = True
            return True
        return False

    def resume_session(self, session_id: str) -> bool:
        """Resume debug session"""
        if session_id in self.sessions:
            self.sessions[session_id].is_paused = False
            return True
        return False

    def get_variable_state(self, session_id: str, variable_name: str) -> Optional[VariableState]:
        """Get current state of a variable"""
        if session_id in self.sessions:
            session = self.sessions[session_id]
            if variable_name in session.variables:
                value = session.variables[variable_name]
                return VariableState(
                    name=variable_name,
                    value=value,
                    type_name=type(value).__name__,
                    size=sys.getsizeof(value) if hasattr(value, '__sizeof__') else None
                )
        return None

    def set_variable(self, session_id: str, variable_name: str, value: Any) -> bool:
        """Set variable value in debug session"""
        if session_id in self.sessions:
            self.sessions[session_id].variables[variable_name] = value
            return True
        return False

# Initialize advanced debugger
advanced_debugger = AdvancedDebugger()
