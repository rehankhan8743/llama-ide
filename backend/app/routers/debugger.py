from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from ..services.advanced_debugger import (
    advanced_debugger,
    DebugPoint,
    PerformanceReport,
    ExecutionTrace
)

router = APIRouter(prefix="/debugger")


class CreateSessionRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)


class AddBreakpointRequest(BaseModel):
    session_id: str
    file_path: str
    line_number: int = Field(..., ge=1)
    condition: Optional[str] = None


class RemoveBreakpointRequest(BaseModel):
    session_id: str
    breakpoint_id: str


class WatchExpressionRequest(BaseModel):
    session_id: str
    expression: str


class StepExecutionRequest(BaseModel):
    code: str
    inputs: Optional[Dict[str, Any]] = None


class PerformanceAnalysisRequest(BaseModel):
    code: str
    iterations: int = Field(default=100, ge=1, le=10000)


class VariableRequest(BaseModel):
    session_id: str
    variable_name: str
    value: Optional[Any] = None


class EvaluateExpressionsRequest(BaseModel):
    session_id: str
    context: Dict[str, Any]


@router.post("/sessions")
async def create_session(request: CreateSessionRequest):
    """Create a new debugging session"""
    try:
        session_id = advanced_debugger.create_session(request.name)
        return {"session_id": session_id, "name": request.name}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create session: {str(e)}")


@router.get("/sessions")
async def list_sessions():
    """List all active debugging sessions"""
    try:
        sessions = advanced_debugger.list_sessions()
        return {"sessions": [s.model_dump() for s in sessions]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list sessions: {str(e)}")


@router.get("/sessions/{session_id}")
async def get_session(session_id: str):
    """Get debug session details"""
    try:
        session = advanced_debugger.get_session(session_id)
        if session:
            return session.model_dump()
        raise HTTPException(status_code=404, detail="Session not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get session: {str(e)}")


@router.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    """Delete a debugging session"""
    try:
        success = advanced_debugger.delete_session(session_id)
        if success:
            return {"status": "success", "message": "Session deleted"}
        raise HTTPException(status_code=404, detail="Session not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete session: {str(e)}")


@router.post("/breakpoints")
async def add_breakpoint(request: AddBreakpointRequest):
    """Add a breakpoint to a session"""
    try:
        breakpoint = advanced_debugger.add_breakpoint(
            session_id=request.session_id,
            file_path=request.file_path,
            line_number=request.line_number,
            condition=request.condition
        )
        if breakpoint:
            return {"status": "success", "breakpoint": breakpoint.model_dump()}
        raise HTTPException(status_code=404, detail="Session not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add breakpoint: {str(e)}")


@router.delete("/breakpoints")
async def remove_breakpoint(request: RemoveBreakpointRequest):
    """Remove a breakpoint from a session"""
    try:
        success = advanced_debugger.remove_breakpoint(
            request.session_id,
            request.breakpoint_id
        )
        if success:
            return {"status": "success", "message": "Breakpoint removed"}
        raise HTTPException(status_code=404, detail="Session or breakpoint not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to remove breakpoint: {str(e)}")


@router.post("/breakpoints/{breakpoint_id}/toggle")
async def toggle_breakpoint(session_id: str, breakpoint_id: str):
    """Toggle breakpoint enabled state"""
    try:
        success = advanced_debugger.toggle_breakpoint(session_id, breakpoint_id)
        if success:
            return {"status": "success", "message": "Breakpoint toggled"}
        raise HTTPException(status_code=404, detail="Session or breakpoint not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to toggle breakpoint: {str(e)}")


@router.post("/watch-expressions")
async def add_watch_expression(request: WatchExpressionRequest):
    """Add a watch expression to a session"""
    try:
        success = advanced_debugger.set_watch_expression(
            request.session_id,
            request.expression
        )
        if success:
            return {"status": "success", "message": "Watch expression added"}
        raise HTTPException(status_code=404, detail="Session not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add watch expression: {str(e)}")


@router.delete("/watch-expressions")
async def remove_watch_expression(request: WatchExpressionRequest):
    """Remove a watch expression from a session"""
    try:
        success = advanced_debugger.remove_watch_expression(
            request.session_id,
            request.expression
        )
        if success:
            return {"status": "success", "message": "Watch expression removed"}
        raise HTTPException(status_code=404, detail="Session or expression not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to remove watch expression: {str(e)}")


@router.post("/watch-expressions/evaluate")
async def evaluate_watch_expressions(request: EvaluateExpressionsRequest):
    """Evaluate all watch expressions in a session"""
    try:
        results = advanced_debugger.evaluate_watch_expressions(
            request.session_id,
            request.context
        )
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to evaluate expressions: {str(e)}")


@router.post("/step-execution")
async def step_through_execution(request: StepExecutionRequest):
    """Step through code execution with visualization"""
    try:
        trace = advanced_debugger.step_through_execution(
            code=request.code,
            inputs=request.inputs
        )
        return trace.model_dump()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to execute code: {str(e)}")


@router.post("/performance-analysis")
async def analyze_performance(request: PerformanceAnalysisRequest):
    """Analyze code performance"""
    try:
        reports = advanced_debugger.analyze_performance(
            code=request.code,
            iterations=request.iterations
        )
        return {
            "reports": [r.model_dump() for r in reports],
            "function_count": len(reports)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to analyze performance: {str(e)}")


@router.get("/performance-history/{function_name}")
async def get_performance_history(function_name: str):
    """Get historical performance data for a function"""
    try:
        history = advanced_debugger.get_performance_history(function_name)
        return {
            "function_name": function_name,
            "history": [h.model_dump() for h in history]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get performance history: {str(e)}")


@router.post("/sessions/{session_id}/pause")
async def pause_session(session_id: str):
    """Pause a debugging session"""
    try:
        success = advanced_debugger.pause_session(session_id)
        if success:
            return {"status": "success", "message": "Session paused"}
        raise HTTPException(status_code=404, detail="Session not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to pause session: {str(e)}")


@router.post("/sessions/{session_id}/resume")
async def resume_session(session_id: str):
    """Resume a debugging session"""
    try:
        success = advanced_debugger.resume_session(session_id)
        if success:
            return {"status": "success", "message": "Session resumed"}
        raise HTTPException(status_code=404, detail="Session not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to resume session: {str(e)}")


@router.post("/sessions/{session_id}/stop")
async def stop_session(session_id: str):
    """Stop a debugging session"""
    try:
        success = advanced_debugger.stop_session(session_id)
        if success:
            return {"status": "success", "message": "Session stopped"}
        raise HTTPException(status_code=404, detail="Session not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to stop session: {str(e)}")


@router.get("/sessions/{session_id}/variables/{variable_name}")
async def get_variable(session_id: str, variable_name: str):
    """Get variable state in a session"""
    try:
        state = advanced_debugger.get_variable_state(session_id, variable_name)
        if state:
            return state.model_dump()
        raise HTTPException(status_code=404, detail="Variable not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get variable: {str(e)}")


@router.post("/sessions/{session_id}/variables/{variable_name}")
async def set_variable(session_id: str, variable_name: str, request: Dict[str, Any]):
    """Set variable value in a session"""
    try:
        value = request.get("value")
        success = advanced_debugger.set_variable(session_id, variable_name, value)
        if success:
            return {"status": "success", "message": "Variable set"}
        raise HTTPException(status_code=404, detail="Session not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to set variable: {str(e)}")


@router.get("/sessions/{session_id}/call-stack")
async def get_call_stack(session_id: str):
    """Get call stack for a session"""
    try:
        stack = advanced_debugger.get_call_stack(session_id)
        return {"call_stack": [f.model_dump() for f in stack]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get call stack: {str(e)}")


@router.delete("/sessions")
async def clear_all_sessions():
    """Clear all debugging sessions"""
    try:
        count = advanced_debugger.clear_all_sessions()
        return {"status": "success", "cleared_count": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clear sessions: {str(e)}")
