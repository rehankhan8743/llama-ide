from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
import json
from ..services.advanced_debugger import (
    advanced_debugger,
    DebugSession,
    DebugPoint,
    PerformanceReport
)

router = APIRouter(prefix="/debug")

class CreateSessionRequest(BaseModel):
    name: str

class AddBreakpointRequest(BaseModel):
    file_path: str
    line_number: int
    condition: Optional[str] = None

class WatchExpressionRequest(BaseModel):
    expression: str

class StepExecutionRequest(BaseModel):
    code: str
    inputs: Optional[Dict[str, Any]] = None

class PerformanceAnalysisRequest(BaseModel):
    code: str
    iterations: int = 100

class VariableStateRequest(BaseModel):
    variable_name: str
    value: Any

@router.post("/sessions")
async def create_debug_session(request: CreateSessionRequest):
    """Create a new debugging session"""
    try:
        session_id = advanced_debugger.create_session(request.name)
        return {"session_id": session_id, "message": "Debug session created successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sessions/{session_id}")
async def get_debug_session(session_id: str):
    """Get debug session information"""
    try:
        session = advanced_debugger.get_session(session_id)
        if session:
            return session
        else:
            raise HTTPException(status_code=404, detail="Debug session not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sessions/{session_id}/breakpoints")
async def add_breakpoint(session_id: str, request: AddBreakpointRequest):
    """Add breakpoint to debug session"""
    try:
        success = advanced_debugger.add_breakpoint(
            session_id,
            request.file_path,
            request.line_number,
            request.condition
        )
        if success:
            return {"message": "Breakpoint added successfully"}
        else:
            raise HTTPException(status_code=404, detail="Debug session not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/sessions/{session_id}/breakpoints")
async def remove_breakpoint(session_id: str, file_path: str, line_number: int):
    """Remove breakpoint from debug session"""
    try:
        success = advanced_debugger.remove_breakpoint(session_id, file_path, line_number)
        if success:
            return {"message": "Breakpoint removed successfully"}
        else:
            raise HTTPException(status_code=404, detail="Debug session or breakpoint not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sessions/{session_id}/watch")
async def set_watch_expression(session_id: str, request: WatchExpressionRequest):
    """Add watch expression to debug session"""
    try:
        success = advanced_debugger.set_watch_expression(session_id, request.expression)
        if success:
            return {"message": "Watch expression added successfully"}
        else:
            raise HTTPException(status_code=404, detail="Debug session not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sessions/{session_id}/evaluate")
async def evaluate_watch_expressions(session_id: str):
    """Evaluate all watch expressions in current context"""
    try:
        # In a real implementation, this would get the current execution context
        context = {}  # This would be populated with actual variables
        results = advanced_debugger.evaluate_watch_expressions(session_id, context)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/step-through", response_model=Dict[str, Any])
async def step_through_execution(request: StepExecutionRequest):
    """Step through code execution with visualization"""
    try:
        result = advanced_debugger.step_through_execution(request.code, request.inputs)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/performance", response_model=List[PerformanceReport])
async def analyze_performance(request: PerformanceAnalysisRequest):
    """Analyze code performance bottlenecks"""
    try:
        reports = advanced_debugger.analyze_performance(request.code, request.iterations)
        return reports
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sessions/{session_id}/pause")
async def pause_session(session_id: str):
    """Pause debug session"""
    try:
        success = advanced_debugger.pause_session(session_id)
        if success:
            return {"message": "Session paused successfully"}
        else:
            raise HTTPException(status_code=404, detail="Debug session not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sessions/{session_id}/resume")
async def resume_session(session_id: str):
    """Resume debug session"""
    try:
        success = advanced_debugger.resume_session(session_id)
        if success:
            return {"message": "Session resumed successfully"}
        else:
            raise HTTPException(status_code=404, detail="Debug session not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sessions/{session_id}/variables/{variable_name}")
async def get_variable_state(session_id: str, variable_name: str):
    """Get current state of a variable"""
    try:
        variable_state = advanced_debugger.get_variable_state(session_id, variable_name)
        if variable_state:
            return variable_state
        else:
            raise HTTPException(status_code=404, detail="Variable not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sessions/{session_id}/variables/{variable_name}")
async def set_variable(session_id: str, variable_name: str, request: VariableStateRequest):
    """Set variable value in debug session"""
    try:
        success = advanced_debugger.set_variable(session_id, variable_name, request.value)
        if success:
            return {"message": "Variable set successfully"}
        else:
            raise HTTPException(status_code=404, detail="Debug session not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sessions/{session_id}/stack")
async def get_call_stack(session_id: str):
    """Get current call stack"""
    try:
        session = advanced_debugger.get_session(session_id)
        if session:
            return {"call_stack": session.call_stack}
        else:
            raise HTTPException(status_code=404, detail="Debug session not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
