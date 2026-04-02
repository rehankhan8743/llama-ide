import time
import asyncio
import logging
from typing import Dict, Any, List, Callable, Optional, Union
from functools import wraps
from dataclasses import dataclass, field
from collections import deque
import gc

logger = logging.getLogger(__name__)

# Optional psutil import with fallback
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    logger.warning("psutil not available, system metrics will be limited")


@dataclass
class FunctionMetric:
    """Stores metrics for a single function"""
    name: str
    times: deque = field(default_factory=lambda: deque(maxlen=1000))
    call_count: int = 0
    errors: int = 0

    def record(self, duration: float, error: bool = False):
        """Record a function execution"""
        self.times.append(duration)
        self.call_count += 1
        if error:
            self.errors += 1

    @property
    def average_time(self) -> float:
        """Calculate average execution time"""
        if self.times:
            return sum(self.times) / len(self.times)
        return 0.0

    @property
    def min_time(self) -> float:
        """Get minimum execution time"""
        return min(self.times) if self.times else 0.0

    @property
    def max_time(self) -> float:
        """Get maximum execution time"""
        return max(self.times) if self.times else 0.0

    @property
    def p95_time(self) -> float:
        """Get 95th percentile execution time"""
        if len(self.times) >= 20:
            sorted_times = sorted(self.times)
            idx = int(len(sorted_times) * 0.95)
            return sorted_times[min(idx, len(sorted_times) - 1)]
        return self.average_time

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "call_count": self.call_count,
            "average_time": round(self.average_time, 4),
            "min_time": round(self.min_time, 4),
            "max_time": round(self.max_time, 4),
            "p95_time": round(self.p95_time, 4),
            "total_time": round(sum(self.times), 4),
            "errors": self.errors,
            "error_rate": round(self.errors / self.call_count * 100, 2) if self.call_count > 0 else 0
        }


class PerformanceMetrics:
    """Collects and stores performance metrics"""

    def __init__(self, max_history: int = 1000):
        self._metrics: Dict[str, FunctionMetric] = {}
        self._lock = asyncio.Lock()
        self._max_history = max_history

    async def record(self, function_name: str, duration: float, error: bool = False):
        """Record execution time for a function"""
        async with self._lock:
            if function_name not in self._metrics:
                self._metrics[function_name] = FunctionMetric(name=function_name)
            self._metrics[function_name].record(duration, error)

    def get_metric(self, function_name: str) -> Optional[FunctionMetric]:
        """Get metrics for a specific function"""
        return self._metrics.get(function_name)

    def get_all_metrics(self) -> Dict[str, Dict[str, Any]]:
        """Get all function metrics"""
        return {name: metric.to_dict() for name, metric in self._metrics.items()}

    def clear(self):
        """Clear all metrics"""
        self._metrics.clear()

    def get_slow_functions(self, threshold: float = 1.0) -> List[str]:
        """Get list of functions exceeding time threshold"""
        return [
            name for name, metric in self._metrics.items()
            if metric.average_time > threshold
        ]

    @staticmethod
    def get_system_metrics() -> Dict[str, Any]:
        """Get current system resource usage"""
        metrics = {}

        if PSUTIL_AVAILABLE:
            try:
                metrics["cpu_percent"] = psutil.cpu_percent(interval=0.1)
                memory = psutil.virtual_memory()
                metrics["memory_percent"] = memory.percent
                metrics["memory_used_gb"] = round(memory.used / (1024**3), 2)
                metrics["memory_available_gb"] = round(memory.available / (1024**3), 2)
                metrics["disk_usage"] = psutil.disk_usage("/").percent

                # Network I/O (cumulative since boot)
                net_io = psutil.net_io_counters()
                metrics["network_io"] = {
                    "bytes_sent": net_io.bytes_sent,
                    "bytes_recv": net_io.bytes_recv,
                    "packets_sent": net_io.packets_sent,
                    "packets_recv": net_io.packets_recv
                }
            except Exception as e:
                logger.warning(f"Error getting system metrics: {e}")
        else:
            metrics["note"] = "psutil not available"

        # Python-specific metrics
        metrics["gc_objects"] = len(gc.get_objects())
        metrics["gc_generations"] = gc.get_count()

        return metrics


class PerformanceOptimizer:
    """Main performance optimization service"""

    def __init__(self):
        self.metrics = PerformanceMetrics()
        self._optimization_rules = self._load_optimization_rules()

    def _load_optimization_rules(self) -> Dict[str, Callable]:
        """Load available optimization rules"""
        return {
            "batch_operations": self._optimize_batch_operations,
            "memory_cleanup": self._trigger_garbage_collection,
            "parallel_processing": self._enable_parallel_processing,
            "clear_metrics": self._clear_metrics
        }

    @property
    def optimization_rules(self) -> Dict[str, Callable]:
        """Get available optimization rules"""
        return self._optimization_rules

    def monitor_performance(self, func: Callable) -> Callable:
        """Decorator to monitor function performance"""
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.perf_counter()
            error = False
            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                error = True
                raise e
            finally:
                duration = time.perf_counter() - start_time
                asyncio.create_task(self.metrics.record(func.__name__, duration, error))

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.perf_counter()
            error = False
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                error = True
                raise e
            finally:
                duration = time.perf_counter() - start_time
                # Fire and forget for sync functions
                asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: asyncio.run(self.metrics.record(func.__name__, duration, error))
                )

        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper

    async def _optimize_batch_operations(self, operations: List[Callable], batch_size: int = 50) -> List[Any]:
        """Optimize batch operations by grouping and processing in batches"""
        if not operations:
            return []

        results = []

        # Group operations by type
        grouped_ops: Dict[str, List[Callable]] = {}
        for op in operations:
            op_type = type(op).__name__
            if op_type not in grouped_ops:
                grouped_ops[op_type] = []
            grouped_ops[op_type].append(op)

        # Process each group
        for op_type, ops in grouped_ops.items():
            if len(ops) > 10:  # Batch threshold
                batch_results = await self._process_batch_concurrent(ops, batch_size)
                results.extend(batch_results)
            else:
                # Process individually
                for op in ops:
                    if asyncio.iscoroutinefunction(op):
                        results.append(await op())
                    else:
                        results.append(op())

        return results

    async def _process_batch_concurrent(self, operations: List[Callable], batch_size: int) -> List[Any]:
        """Process operations in concurrent batches"""
        results = []

        for i in range(0, len(operations), batch_size):
            batch = operations[i:i + batch_size]

            # Run batch concurrently
            async def run_op(op):
                try:
                    if asyncio.iscoroutinefunction(op):
                        return await op()
                    return op()
                except Exception as e:
                    return {"error": str(e), "type": type(e).__name__}

            batch_tasks = [run_op(op) for op in batch]
            batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
            results.extend(batch_results)

        return results

    def _trigger_garbage_collection(self) -> Dict[str, Any]:
        """Trigger garbage collection if memory usage is high"""
        gc.collect()

        if PSUTIL_AVAILABLE:
            memory_percent = psutil.virtual_memory().percent
            triggered = memory_percent > 80
        else:
            memory_percent = None
            triggered = True

        return {
            "gc_generations": gc.get_count(),
            "gc_objects": len(gc.get_objects()),
            "memory_percent": memory_percent,
            "triggered": triggered
        }

    async def _enable_parallel_processing(self, tasks: List[Callable]) -> List[Any]:
        """Execute tasks in parallel using asyncio"""
        if not tasks:
            return []

        if len(tasks) == 1:
            task = tasks[0]
            if asyncio.iscoroutinefunction(task):
                return [await task()]
            return [task()]

        async def run_task(task):
            try:
                if asyncio.iscoroutinefunction(task):
                    return await task()
                return task()
            except Exception as e:
                return {"error": str(e), "type": type(e).__name__}

        return await asyncio.gather(*[run_task(t) for t in tasks], return_exceptions=True)

    def _clear_metrics(self) -> Dict[str, Any]:
        """Clear performance metrics"""
        previous_count = len(self.metrics._metrics)
        self.metrics.clear()
        return {"cleared": True, "previous_metric_count": previous_count}

    def get_performance_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        report = {
            "function_metrics": self.metrics.get_all_metrics(),
            "system_metrics": self.metrics.get_system_metrics(),
            "optimization_suggestions": []
        }

        # Analyze slow functions
        slow_functions = self.metrics.get_slow_functions(threshold=1.0)
        if slow_functions:
            report["optimization_suggestions"].append({
                "type": "slow_functions",
                "severity": "medium",
                "functions": slow_functions,
                "suggestion": "Consider optimizing these functions or implementing caching"
            })

        # Check memory usage
        if PSUTIL_AVAILABLE:
            memory_percent = psutil.virtual_memory().percent
            if memory_percent > 75:
                report["optimization_suggestions"].append({
                    "type": "memory_usage",
                    "severity": "high" if memory_percent > 90 else "medium",
                    "current_usage": memory_percent,
                    "suggestion": "High memory usage detected. Consider triggering garbage collection or optimizing data structures"
                })

            cpu_percent = psutil.cpu_percent(interval=0.1)
            if cpu_percent > 80:
                report["optimization_suggestions"].append({
                    "type": "cpu_usage",
                    "severity": "high" if cpu_percent > 95 else "medium",
                    "current_usage": cpu_percent,
                    "suggestion": "High CPU usage detected. Consider optimizing CPU-intensive operations"
                })

        return report


# Global performance optimizer instance
performance_optimizer = PerformanceOptimizer()


def performance_monitor(func: Callable) -> Callable:
    """Decorator to monitor function performance"""
    return performance_optimizer.monitor_performance(func)
