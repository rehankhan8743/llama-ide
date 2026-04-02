from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from ..services.performance_optimizer import performance_optimizer

router = APIRouter(prefix="/performance")


class PerformanceReport(BaseModel):
    function_metrics: Dict[str, Dict[str, Any]]
    system_metrics: Dict[str, Any]
    optimization_suggestions: List[Dict[str, Any]]


class OptimizeRequest(BaseModel):
    operation_type: str = Field(..., description="Type of optimization to apply")
    parameters: Optional[Dict[str, Any]] = Field(default={}, description="Optimization parameters")


class BatchOptimizeRequest(BaseModel):
    operations: List[Dict[str, Any]] = Field(..., description="List of operations to batch")
    batch_size: int = Field(default=50, ge=1, le=1000)


class ParallelProcessRequest(BaseModel):
    tasks: List[Dict[str, Any]] = Field(..., description="List of tasks to run in parallel")


class ClearMetricsResponse(BaseModel):
    cleared: bool
    previous_metric_count: int


class MemoryCleanupResponse(BaseModel):
    gc_generations: List[int]
    gc_objects: int
    memory_percent: Optional[float]
    triggered: bool


@router.get("/metrics", response_model=PerformanceReport)
async def get_performance_metrics():
    """Get current performance metrics and system resource usage"""
    try:
        report = performance_optimizer.get_performance_report()
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get metrics: {str(e)}")


@router.post("/optimize")
async def optimize_operation(request: OptimizeRequest):
    """Apply an optimization rule"""
    try:
        if request.operation_type not in performance_optimizer.optimization_rules:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown optimization type: {request.operation_type}. "
                       f"Available: {list(performance_optimizer.optimization_rules.keys())}"
            )

        optimization_func = performance_optimizer.optimization_rules[request.operation_type]

        # Handle async vs sync functions
        if request.operation_type == "batch_operations":
            operations = request.parameters.get("operations", [])
            batch_size = request.parameters.get("batch_size", 50)
            # Note: actual callables would need to be passed, not just dicts
            result = {"note": "Batch operations require actual callable functions"}
        elif request.operation_type == "parallel_processing":
            tasks = request.parameters.get("tasks", [])
            result = {"note": "Parallel processing requires actual callable functions"}
        else:
            result = optimization_func(**request.parameters)

        return {
            "status": "optimized",
            "operation_type": request.operation_type,
            "result": result
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Optimization failed: {str(e)}")


@router.post("/memory-cleanup", response_model=MemoryCleanupResponse)
async def trigger_memory_cleanup():
    """Trigger garbage collection and return memory status"""
    try:
        result = performance_optimizer._trigger_garbage_collection()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Memory cleanup failed: {str(e)}")


@router.post("/clear-metrics", response_model=ClearMetricsResponse)
async def clear_performance_metrics():
    """Clear all performance monitoring metrics"""
    try:
        result = performance_optimizer._clear_metrics()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clear metrics: {str(e)}")


@router.get("/recommendations")
async def get_optimization_recommendations():
    """Get optimization recommendations based on current metrics"""
    try:
        report = performance_optimizer.get_performance_report()
        return {
            "recommendations": report["optimization_suggestions"],
            "slow_functions": performance_optimizer.metrics.get_slow_functions(threshold=1.0),
            "function_count": len(report["function_metrics"])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get recommendations: {str(e)}")


@router.get("/function/{function_name}")
async def get_function_metrics(function_name: str):
    """Get detailed metrics for a specific function"""
    try:
        metric = performance_optimizer.metrics.get_metric(function_name)
        if metric:
            return metric.to_dict()
        raise HTTPException(status_code=404, detail=f"No metrics found for function: {function_name}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get function metrics: {str(e)}")


@router.get("/system")
async def get_system_metrics():
    """Get current system resource usage"""
    try:
        from ..services.performance_optimizer import PerformanceMetrics
        metrics = PerformanceMetrics.get_system_metrics()
        return metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get system metrics: {str(e)}")


@router.get("/rules")
async def get_optimization_rules():
    """Get list of available optimization rules"""
    return {
        "available_rules": list(performance_optimizer.optimization_rules.keys()),
        "descriptions": {
            "batch_operations": "Group and process similar operations in batches",
            "memory_cleanup": "Trigger garbage collection when memory is high",
            "parallel_processing": "Execute independent tasks concurrently",
            "clear_metrics": "Clear all performance metrics"
        }
    }
