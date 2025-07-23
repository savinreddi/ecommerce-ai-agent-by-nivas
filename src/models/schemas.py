"""
Pydantic models and schemas for the Ecommerce AI Agent
"""
from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field
from enum import Enum

class ChartType(str, Enum):
    """Supported chart types"""
    LINE = "line"
    BAR = "bar"
    PIE = "pie"
    SCATTER = "scatter"
    TABLE = "table"

class QuestionRequest(BaseModel):
    """Request model for asking questions"""
    question: str = Field(..., min_length=1, description="The question to ask")
    chart_type: Optional[ChartType] = Field(None, description="Preferred chart type")
    include_visualization: bool = Field(True, description="Whether to include visualization")

class VisualizationFormat(str, Enum):
    """Supported visualization formats"""
    HTML = "html"
    BASE64 = "base64"
    JSON = "json"

class Visualization(BaseModel):
    """Visualization response model"""
    type: str = Field(..., description="Type of visualization")
    content: Union[str, List[Dict[str, Any]]] = Field(..., description="Visualization content")
    format: VisualizationFormat = Field(..., description="Format of the visualization")
    error: Optional[str] = Field(None, description="Error message if visualization failed")

class QuestionResponse(BaseModel):
    """Response model for question answers"""
    question: str = Field(..., description="The original question")
    sql_query: str = Field(..., description="Generated SQL query")
    answer: Union[List[Dict[str, Any]], str] = Field(..., description="Query results")
    visualization: Optional[Visualization] = Field(None, description="Optional visualization")

class HealthResponse(BaseModel):
    """Health check response model"""
    status: str = Field(..., description="Health status")
    timestamp: str = Field(..., description="Current timestamp")
    version: str = Field(..., description="API version")

class ErrorResponse(BaseModel):
    """Error response model"""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
    code: Optional[int] = Field(None, description="Error code")

class StreamingEvent(BaseModel):
    """Streaming event model"""
    event: str = Field(..., description="Event type")
    data: Dict[str, Any] = Field(..., description="Event data")
    timestamp: Optional[str] = Field(None, description="Event timestamp")

class DatabaseConfig(BaseModel):
    """Database configuration model"""
    path: str = Field(..., description="Database file path")
    tables: List[str] = Field(default_factory=list, description="Available tables")

class LLMConfig(BaseModel):
    """LLM configuration model"""
    api_key: str = Field(..., description="API key for LLM service")
    model_url: str = Field(..., description="LLM API endpoint")
    max_tokens: int = Field(default=2048, description="Maximum tokens per request")
    temperature: float = Field(default=0.1, description="LLM temperature setting")
