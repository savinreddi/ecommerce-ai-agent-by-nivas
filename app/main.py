from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from app.llm_interface import ask_llm
from app.db import execute_sql_query
from app.visualization import visualizer
from app.streaming_service import streaming_service
import json
import uuid
from typing import Optional

app = FastAPI(title="Ecommerce AI Agent", description="AI-powered ecommerce analytics with visualizations and real-time streaming")

class QuestionRequest(BaseModel):
    question: str
    chart_type: Optional[str] = None
    include_visualization: bool = True

@app.post("/ask")
def ask_question(request: QuestionRequest):
    """Standard synchronous endpoint for asking questions"""
    question = request.question
    raw_sql = ask_llm(question)

    # ✅ Clean SQL from markdown formatting (e.g., ```sql ... ```)
    sql_query = raw_sql.replace("```sql", "").replace("```", "").strip()

    try:
        answer = execute_sql_query(sql_query)
        
        # Generate visualization if requested and data is suitable
        visualization = None
        if request.include_visualization and isinstance(answer, list) and len(answer) > 0:
            visualization = visualizer.generate_visualization(answer, question, request.chart_type)
            
    except Exception as e:
        answer = f"SQL Execution Error: {e}"
        visualization = None

    return {
        "question": question,
        "sql_query": sql_query,
        "answer": answer,
        "visualization": visualization
    }

@app.post("/ask-stream")
async def ask_question_stream(request: QuestionRequest):
    """Streaming endpoint that simulates real-time processing"""
    async def generate_stream():
        async for event in streaming_service.stream_complete_response(request.question):
            yield f"data: {json.dumps(event)}\n\n"
    
    return StreamingResponse(generate_stream(), media_type="text/plain")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time communication"""
    await websocket.accept()
    connection_id = str(uuid.uuid4())
    streaming_service.add_connection(connection_id, websocket)
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("type") == "question":
                question = message.get("question", "")
                
                # Stream the response
                async for event in streaming_service.stream_complete_response(question):
                    await websocket.send_text(json.dumps(event))
            
            elif message.get("type") == "ping":
                await websocket.send_text(json.dumps({"type": "pong", "timestamp": "now"}))
                
    except WebSocketDisconnect:
        streaming_service.remove_connection(connection_id)
    except Exception as e:
        await websocket.send_text(json.dumps({
            "event": "error",
            "data": {"error": str(e)}
        }))
        streaming_service.remove_connection(connection_id)

@app.get("/visualize/{chart_type}")
def get_visualization(chart_type: str, question: str):
    """Endpoint to get specific visualization types"""
    try:
        raw_sql = ask_llm(question)
        sql_query = raw_sql.replace("```sql", "").replace("```", "").strip()
        answer = execute_sql_query(sql_query)
        
        if not isinstance(answer, list) or len(answer) == 0:
            raise HTTPException(status_code=400, detail="No data available for visualization")
        
        visualization = visualizer.generate_visualization(answer, question, chart_type)
        
        return {
            "question": question,
            "sql_query": sql_query,
            "data": answer,
            "visualization": visualization
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/demo")
def get_demo():
    """Serve the demo HTML file"""
    return FileResponse("demo.html")

@app.get("/")
def read_root():
    """Root endpoint with basic info"""
    return {
        "message": "Ecommerce AI Agent API",
        "endpoints": {
            "/ask": "POST - Ask questions (synchronous)",
            "/ask-stream": "POST - Ask questions (streaming)",
            "/ws": "WebSocket - Real-time communication",
            "/visualize/{chart_type}": "GET - Get specific visualizations",
            "/demo": "GET - Demo frontend",
            "/health": "GET - Health check"
        },
        "chart_types": ["line", "bar", "pie", "scatter", "table"]
    }

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": "2025-01-23T15:06:38Z"}
