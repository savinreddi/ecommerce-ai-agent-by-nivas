"""
Database service for handling SQL operations
"""
import sqlite3
import pandas as pd
import logging
from typing import List, Dict, Any, Union
from pathlib import Path

from config.settings import settings

logger = logging.getLogger(__name__)

class DatabaseService:
    """Service for database operations"""
    
    def __init__(self, db_path: str = None):
        """Initialize database service"""
        self.db_path = db_path or settings.DB_PATH
        self._ensure_db_exists()
    
    def _ensure_db_exists(self) -> None:
        """Ensure database file exists"""
        db_file = Path(self.db_path)
        if not db_file.exists():
            logger.warning(f"Database file not found at {self.db_path}")
            # Create empty database
            self._create_empty_database()
    
    def _create_empty_database(self) -> None:
        """Create an empty database file"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.close()
            logger.info(f"Created empty database at {self.db_path}")
        except Exception as e:
            logger.error(f"Failed to create database: {e}")
            raise
    
    def execute_query(self, query: str) -> Union[List[Dict[str, Any]], str]:
        """
        Execute SQL query and return results
        
        Args:
            query: SQL query string
            
        Returns:
            Query results as list of dictionaries or error message
        """
        try:
            logger.info(f"Executing query: {query}")
            
            with sqlite3.connect(self.db_path) as conn:
                df = pd.read_sql_query(query, conn)
                results = df.to_dict(orient="records")
                
            logger.info(f"Query executed successfully, returned {len(results)} rows")
            return results
            
        except Exception as e:
            error_msg = f"SQL Execution Error: {e}"
            logger.error(error_msg)
            return error_msg
    
    def get_table_names(self) -> List[str]:
        """Get list of table names in the database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = [row[0] for row in cursor.fetchall()]
            return tables
        except Exception as e:
            logger.error(f"Failed to get table names: {e}")
            return []
    
    def get_table_schema(self, table_name: str) -> List[Dict[str, Any]]:
        """Get schema information for a table"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(f"PRAGMA table_info({table_name});")
                columns = cursor.fetchall()
                
                schema = []
                for col in columns:
                    schema.append({
                        "column_id": col[0],
                        "name": col[1],
                        "type": col[2],
                        "not_null": bool(col[3]),
                        "default_value": col[4],
                        "primary_key": bool(col[5])
                    })
                return schema
        except Exception as e:
            logger.error(f"Failed to get schema for table {table_name}: {e}")
            return []
    
    def get_sample_data(self, table_name: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Get sample data from a table"""
        try:
            query = f"SELECT * FROM {table_name} LIMIT {limit}"
            return self.execute_query(query)
        except Exception as e:
            logger.error(f"Failed to get sample data from {table_name}: {e}")
            return []
    
    def validate_query(self, query: str) -> bool:
        """Validate if a query is safe to execute"""
        # Basic validation - could be expanded
        dangerous_keywords = ['DROP', 'DELETE', 'INSERT', 'UPDATE', 'ALTER', 'CREATE']
        query_upper = query.upper()
        
        for keyword in dangerous_keywords:
            if keyword in query_upper:
                logger.warning(f"Potentially dangerous keyword '{keyword}' found in query")
                return False
        
        return True
    
    def get_database_info(self) -> Dict[str, Any]:
        """Get general information about the database"""
        try:
            tables = self.get_table_names()
            table_info = {}
            
            for table in tables:
                schema = self.get_table_schema(table)
                sample = self.get_sample_data(table, 3)
                table_info[table] = {
                    "schema": schema,
                    "sample_data": sample,
                    "column_count": len(schema)
                }
            
            return {
                "database_path": self.db_path,
                "table_count": len(tables),
                "tables": table_info
            }
        except Exception as e:
            logger.error(f"Failed to get database info: {e}")
            return {"error": str(e)}

# Global database service instance
db_service = DatabaseService()
