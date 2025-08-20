#!/usr/bin/env python3
"""
Metrics collector for MCP Server
"""

import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from collections import defaultdict, deque
from dataclasses import dataclass, field

@dataclass
class MetricsCollector:
    """Metrics collector for MCP Server."""
    
    requests: deque = field(default_factory=lambda: deque(maxlen=10000))
    errors: deque = field(default_factory=lambda: deque(maxlen=1000))
    tool_usage: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    response_times: Dict[str, List[float]] = field(default_factory=lambda: defaultdict(list))
    start_time: datetime = field(default_factory=datetime.now)
    
    def record_request(self, request_type: str, tool_name: Optional[str] = None):
        """Record a request."""
        timestamp = datetime.now()
        self.requests.append({
            "type": request_type,
            "tool": tool_name,
            "timestamp": timestamp.isoformat()
        })
        
        if tool_name:
            self.tool_usage[tool_name] += 1
    
    def record_success(self, request_type: str, tool_name: Optional[str] = None, execution_time: float = 0.0):
        """Record a successful request."""
        if tool_name:
            self.response_times[tool_name].append(execution_time)
            # Keep only last 1000 response times per tool
            if len(self.response_times[tool_name]) > 1000:
                self.response_times[tool_name] = self.response_times[tool_name][-1000:]
    
    def record_error(self, request_type: str, tool_name: Optional[str] = None, error_message: str = "", execution_time: float = 0.0):
        """Record an error."""
        timestamp = datetime.now()
        self.errors.append({
            "type": request_type,
            "tool": tool_name,
            "error": error_message,
            "execution_time": execution_time,
            "timestamp": timestamp.isoformat()
        })
    
    def get_metrics(self, hours: int = 24) -> Dict[str, Any]:
        """Get metrics for the last N hours."""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        # Filter requests
        recent_requests = [
            req for req in self.requests
            if datetime.fromisoformat(req["timestamp"]) > cutoff_time
        ]
        
        # Filter errors
        recent_errors = [
            err for err in self.errors
            if datetime.fromisoformat(err["timestamp"]) > cutoff_time
        ]
        
        # Calculate metrics
        total_requests = len(recent_requests)
        total_errors = len(recent_errors)
        success_rate = ((total_requests - total_errors) / total_requests * 100) if total_requests > 0 else 0
        
        # Tool usage
        tool_usage = {}
        for req in recent_requests:
            if req.get("tool"):
                tool_usage[req["tool"]] = tool_usage.get(req["tool"], 0) + 1
        
        # Average response times
        avg_response_times = {}
        for tool, times in self.response_times.items():
            if times:
                avg_response_times[tool] = sum(times) / len(times)
        
        # Error breakdown
        error_breakdown = defaultdict(int)
        for error in recent_errors:
            error_breakdown[error.get("tool", "unknown")] += 1
        
        return {
            "period_hours": hours,
            "total_requests": total_requests,
            "total_errors": total_errors,
            "success_rate": round(success_rate, 2),
            "tool_usage": dict(tool_usage),
            "avg_response_times": avg_response_times,
            "error_breakdown": dict(error_breakdown),
            "uptime_seconds": (datetime.now() - self.start_time).total_seconds()
        }
    
    def get_recent_errors(self, count: int = 10) -> List[Dict[str, Any]]:
        """Get recent errors."""
        return list(self.errors)[-count:]
    
    def get_tool_performance(self, tool_name: str) -> Dict[str, Any]:
        """Get performance metrics for a specific tool."""
        times = self.response_times.get(tool_name, [])
        if not times:
            return {
                "tool": tool_name,
                "total_calls": 0,
                "avg_response_time": 0,
                "min_response_time": 0,
                "max_response_time": 0
            }
        
        return {
            "tool": tool_name,
            "total_calls": len(times),
            "avg_response_time": sum(times) / len(times),
            "min_response_time": min(times),
            "max_response_time": max(times)
        }
    
    def save_metrics(self, filepath: str):
        """Save metrics to file."""
        metrics_data = {
            "start_time": self.start_time.isoformat(),
            "current_time": datetime.now().isoformat(),
            "metrics": self.get_metrics(),
            "tool_usage": dict(self.tool_usage),
            "recent_errors": self.get_recent_errors(50)
        }
        
        with open(filepath, 'w') as f:
            json.dump(metrics_data, f, indent=2)
    
    def load_metrics(self, filepath: str):
        """Load metrics from file."""
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            # Load tool usage
            self.tool_usage.update(data.get("tool_usage", {}))
            
            # Load start time
            if "start_time" in data:
                self.start_time = datetime.fromisoformat(data["start_time"])
                
        except Exception as e:
            print(f"Error loading metrics: {e}")
    
    def reset_metrics(self):
        """Reset all metrics."""
        self.requests.clear()
        self.errors.clear()
        self.tool_usage.clear()
        self.response_times.clear()
        self.start_time = datetime.now()