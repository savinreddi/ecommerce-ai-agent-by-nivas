import asyncio
import json
from typing import AsyncGenerator, Dict, Any, List
from datetime import datetime
import uuid

class StreamingService:
    """Handles event streaming for real-time interaction simulation"""
    
    def __init__(self):
        self.active_connections = {}
    
    async def simulate_processing_steps(self, question: str, session_id: str) -> AsyncGenerator[Dict[str, Any], None]:
        """Simulate real-time processing steps for a question"""
        
        # Step 1: Question received
        yield {
            "event": "question_received",
            "session_id": session_id,
            "timestamp": datetime.utcnow().isoformat(),
            "data": {
                "question": question,
                "status": "processing"
            }
        }
        
        await asyncio.sleep(0.5)  # Simulate processing time
        
        # Step 2: Analyzing question
        yield {
            "event": "analyzing_question",
            "session_id": session_id,
            "timestamp": datetime.utcnow().isoformat(),
            "data": {
                "message": "Analyzing your question...",
                "progress": 25
            }
        }
        
        await asyncio.sleep(0.8)
        
        # Step 3: Generating SQL
        yield {
            "event": "generating_sql",
            "session_id": session_id,
            "timestamp": datetime.utcnow().isoformat(),
            "data": {
                "message": "Converting to SQL query...",
                "progress": 50
            }
        }
        
        await asyncio.sleep(0.6)
        
        # Step 4: Executing query
        yield {
            "event": "executing_query",
            "session_id": session_id,
            "timestamp": datetime.utcnow().isoformat(),
            "data": {
                "message": "Executing database query...",
                "progress": 75
            }
        }
        
        await asyncio.sleep(0.4)
        
        # Step 5: Generating visualization
        yield {
            "event": "generating_visualization",
            "session_id": session_id,
            "timestamp": datetime.utcnow().isoformat(),
            "data": {
                "message": "Creating visualization...",
                "progress": 90
            }
        }
        
        await asyncio.sleep(0.3)
    
    async def stream_response_chunks(self, response_data: Dict[str, Any], session_id: str) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream response data in chunks for realistic typing effect"""
        
        # Stream the SQL query
        sql_query = response_data.get("sql_query", "")
        if sql_query:
            for i in range(0, len(sql_query), 10):  # 10 characters at a time
                chunk = sql_query[i:i+10]
                yield {
                    "event": "sql_chunk",
                    "session_id": session_id,
                    "timestamp": datetime.utcnow().isoformat(),
                    "data": {
                        "chunk": chunk,
                        "complete": i + 10 >= len(sql_query)
                    }
                }
                await asyncio.sleep(0.1)
        
        # Stream the answer if it's text
        answer = response_data.get("answer", "")
        if isinstance(answer, str) and answer:
            for i in range(0, len(answer), 20):  # 20 characters at a time
                chunk = answer[i:i+20]
                yield {
                    "event": "answer_chunk",
                    "session_id": session_id,
                    "timestamp": datetime.utcnow().isoformat(),
                    "data": {
                        "chunk": chunk,
                        "complete": i + 20 >= len(answer)
                    }
                }
                await asyncio.sleep(0.05)
    
    async def stream_complete_response(self, question: str) -> AsyncGenerator[Dict[str, Any], None]:
        """Complete streaming response simulation"""
        session_id = str(uuid.uuid4())
        
        # Simulate processing steps
        async for step_event in self.simulate_processing_steps(question, session_id):
            yield step_event
        
        # Import here to avoid circular imports
        from app.llm_interface import ask_llm
        from app.db import execute_sql_query
        from app.visualization import visualizer
        
        try:
            # Get LLM response
            raw_sql = ask_llm(question)
            sql_query = raw_sql.replace("```sql", "").replace("```", "").strip()
            
            # Execute query
            query_result = execute_sql_query(sql_query)
            
            # Generate visualization if data is suitable
            visualization = None
            if isinstance(query_result, list) and len(query_result) > 0:
                visualization = visualizer.generate_visualization(query_result, question)
            
            # Final response
            final_response = {
                "question": question,
                "sql_query": sql_query,
                "answer": query_result,
                "visualization": visualization
            }
            
            # Stream the final response
            yield {
                "event": "response_complete",
                "session_id": session_id,
                "timestamp": datetime.utcnow().isoformat(),
                "data": final_response
            }
            
            # Stream response chunks for typing effect
            async for chunk_event in self.stream_response_chunks(final_response, session_id):
                yield chunk_event
                
        except Exception as e:
            yield {
                "event": "error",
                "session_id": session_id,
                "timestamp": datetime.utcnow().isoformat(),
                "data": {
                    "error": str(e),
                    "message": "An error occurred while processing your request"
                }
            }
    
    def add_connection(self, connection_id: str, websocket):
        """Add a WebSocket connection"""
        self.active_connections[connection_id] = websocket
    
    def remove_connection(self, connection_id: str):
        """Remove a WebSocket connection"""
        if connection_id in self.active_connections:
            del self.active_connections[connection_id]
    
    async def broadcast_to_all(self, message: Dict[str, Any]):
        """Broadcast a message to all connected clients"""
        if self.active_connections:
            disconnected = []
            for connection_id, websocket in self.active_connections.items():
                try:
                    await websocket.send_text(json.dumps(message))
                except:
                    disconnected.append(connection_id)
            
            # Clean up disconnected clients
            for conn_id in disconnected:
                self.remove_connection(conn_id)

# Global streaming service instance
streaming_service = StreamingService()
