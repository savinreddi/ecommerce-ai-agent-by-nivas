"""
LLM service for generating SQL queries from natural language
"""
import requests
import logging
from typing import Optional, Dict, Any

from config.settings import settings

logger = logging.getLogger(__name__)

class LLMService:
    """Service for interacting with Large Language Models"""
    
    def __init__(self, api_key: str = None, model_url: str = None):
        """Initialize LLM service"""
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.model_url = model_url or settings.GEMINI_URL
        self.headers = {"Content-Type": "application/json"}
        
        if not self.api_key:
            raise ValueError("LLM API key is required but not provided")
    
    def _build_sql_prompt(self, question: str) -> str:
        """Build the prompt for SQL generation"""
        return f"""
You are an AI that converts natural language questions into SQL queries.
Only return the SQL query, nothing else.
Use the following available tables:
- ad_sales_metrics (columns: date, item_id, ad_sales, impressions, ad_spend, clicks, units_sold)
- total_sales_metrics (columns: date, item_id, total_sales, total_units_ordered)
- eligibility_table (columns: eligibility_datetime_utc, item_id, eligibility, message)

Important guidelines:
- For questions asking for "total sales" or "total amount", use SUM(total_sales) to get the aggregate total
- For questions asking for individual sales by item/date, use SELECT without SUM
- Use table `total_sales_metrics` for sales-related questions
- Always use proper aggregate functions when asked for totals/sums
- For RoAS calculations, use: ad_sales / ad_spend
- For CPC calculations, use: ad_spend / clicks (where clicks > 0)

Question: {question}
"""
    
    def generate_sql_query(self, question: str) -> str:
        """
        Generate SQL query from natural language question
        
        Args:
            question: Natural language question
            
        Returns:
            Generated SQL query string
        """
        try:
            logger.info(f"Generating SQL for question: {question}")
            
            prompt = self._build_sql_prompt(question)
            
            payload = {
                "contents": [
                    {
                        "parts": [
                            {"text": prompt}
                        ]
                    }
                ]
            }
            
            response = requests.post(
                f"{self.model_url}?key={self.api_key}",
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            response.raise_for_status()
            data = response.json()
            
            # Extract the generated SQL query
            sql_query = data["candidates"][0]["content"]["parts"][0]["text"]
            
            # Clean up the SQL query (remove markdown formatting)
            sql_query = sql_query.replace("```sql", "").replace("```", "").strip()
            
            logger.info(f"Generated SQL query: {sql_query}")
            return sql_query
            
        except requests.exceptions.RequestException as e:
            error_msg = f"LLM API request failed: {e}"
            logger.error(error_msg)
            return error_msg
            
        except KeyError as e:
            error_msg = f"Unexpected LLM response format: {e}"
            logger.error(error_msg)
            return error_msg
            
        except Exception as e:
            error_msg = f"LLM service error: {e}"
            logger.error(error_msg)
            return error_msg
    
    def validate_and_improve_query(self, query: str, question: str) -> str:
        """
        Validate and potentially improve the generated query
        
        Args:
            query: Generated SQL query
            question: Original question
            
        Returns:
            Validated/improved query
        """
        # Basic query validation and improvements
        query = query.strip()
        
        # Remove any remaining markdown
        if query.startswith("```"):
            lines = query.split("\n")
            query = "\n".join(line for line in lines if not line.strip().startswith("```"))
        
        # Ensure query ends with semicolon (optional)
        if not query.endswith(";"):
            query += ";"
        
        return query.strip()
    
    def explain_query(self, query: str) -> str:
        """
        Generate explanation for a SQL query
        
        Args:
            query: SQL query to explain
            
        Returns:
            Human-readable explanation
        """
        try:
            explain_prompt = f"""
Explain this SQL query in simple, human-readable terms:

{query}

Provide a clear, concise explanation of what this query does.
"""
            
            payload = {
                "contents": [
                    {
                        "parts": [
                            {"text": explain_prompt}
                        ]
                    }
                ]
            }
            
            response = requests.post(
                f"{self.model_url}?key={self.api_key}",
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            response.raise_for_status()
            data = response.json()
            
            explanation = data["candidates"][0]["content"]["parts"][0]["text"]
            return explanation.strip()
            
        except Exception as e:
            logger.error(f"Failed to explain query: {e}")
            return f"Unable to explain query: {e}"
    
    def health_check(self) -> Dict[str, Any]:
        """Check if the LLM service is available"""
        try:
            # Simple test query
            test_response = self.generate_sql_query("SELECT 1")
            
            return {
                "status": "healthy",
                "api_key_configured": bool(self.api_key),
                "test_response_length": len(test_response)
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "api_key_configured": bool(self.api_key)
            }

# Global LLM service instance
llm_service = LLMService()
