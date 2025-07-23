import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import seaborn as sns
import io
import base64
from typing import List, Dict, Any, Optional
from datetime import datetime
import json

# Set matplotlib backend for server environments
plt.switch_backend('Agg')

class VisualizationGenerator:
    """Handles generation of various types of visualizations for ecommerce data"""
    
    def __init__(self):
        # Set seaborn style for better-looking plots
        sns.set_style("whitegrid")
        plt.style.use('seaborn-v0_8')
    
    def determine_chart_type(self, data: List[Dict], query: str) -> str:
        """Intelligently determine the best chart type based on data and query"""
        query_lower = query.lower()
        
        if not data or len(data) == 0:
            return "none"
        
        # Analyze data structure
        columns = list(data[0].keys())
        has_date = any('date' in col.lower() for col in columns)
        has_numeric = any(isinstance(data[0].get(col), (int, float)) for col in columns)
        
        # Chart type logic
        if 'trend' in query_lower or 'over time' in query_lower or has_date:
            return "line"
        elif 'compare' in query_lower or 'comparison' in query_lower:
            return "bar"
        elif 'distribution' in query_lower or 'breakdown' in query_lower:
            return "pie"
        elif 'correlation' in query_lower or 'relationship' in query_lower:
            return "scatter"
        elif len(data) > 1 and has_numeric:
            return "bar"
        else:
            return "table"
    
    def generate_line_chart(self, data: List[Dict], title: str = "Line Chart") -> str:
        """Generate a line chart for time series data"""
        df = pd.DataFrame(data)
        
        fig = go.Figure()
        
        # Find date and numeric columns
        date_col = next((col for col in df.columns if 'date' in col.lower()), df.columns[0])
        numeric_cols = df.select_dtypes(include=['number']).columns
        
        for col in numeric_cols:
            fig.add_trace(go.Scatter(
                x=df[date_col],
                y=df[col],
                mode='lines+markers',
                name=col.replace('_', ' ').title(),
                line=dict(width=2)
            ))
        
        fig.update_layout(
            title=title,
            xaxis_title=date_col.replace('_', ' ').title(),
            yaxis_title="Value",
            hovermode='x unified',
            template='plotly_white'
        )
        
        return fig.to_html(include_plotlyjs='cdn')
    
    def generate_bar_chart(self, data: List[Dict], title: str = "Bar Chart") -> str:
        """Generate a bar chart for categorical data"""
        df = pd.DataFrame(data)
        
        # Find categorical and numeric columns
        categorical_col = df.select_dtypes(include=['object']).columns[0] if len(df.select_dtypes(include=['object']).columns) > 0 else df.columns[0]
        numeric_col = df.select_dtypes(include=['number']).columns[0] if len(df.select_dtypes(include=['number']).columns) > 0 else df.columns[-1]
        
        fig = px.bar(
            df, 
            x=categorical_col, 
            y=numeric_col,
            title=title,
            color=numeric_col,
            color_continuous_scale='viridis'
        )
        
        fig.update_layout(template='plotly_white')
        return fig.to_html(include_plotlyjs='cdn')
    
    def generate_pie_chart(self, data: List[Dict], title: str = "Pie Chart") -> str:
        """Generate a pie chart for distribution data"""
        df = pd.DataFrame(data)
        
        # Find categorical and numeric columns
        categorical_col = df.select_dtypes(include=['object']).columns[0] if len(df.select_dtypes(include=['object']).columns) > 0 else df.columns[0]
        numeric_col = df.select_dtypes(include=['number']).columns[0] if len(df.select_dtypes(include=['number']).columns) > 0 else df.columns[-1]
        
        fig = px.pie(
            df, 
            values=numeric_col, 
            names=categorical_col,
            title=title
        )
        
        fig.update_layout(template='plotly_white')
        return fig.to_html(include_plotlyjs='cdn')
    
    def generate_scatter_plot(self, data: List[Dict], title: str = "Scatter Plot") -> str:
        """Generate a scatter plot for correlation analysis"""
        df = pd.DataFrame(data)
        numeric_cols = df.select_dtypes(include=['number']).columns
        
        if len(numeric_cols) >= 2:
            fig = px.scatter(
                df, 
                x=numeric_cols[0], 
                y=numeric_cols[1],
                title=title,
                trendline="ols"
            )
        else:
            # Fallback to simple scatter
            fig = px.scatter(
                df, 
                x=df.columns[0], 
                y=df.columns[1] if len(df.columns) > 1 else df.columns[0],
                title=title
            )
        
        fig.update_layout(template='plotly_white')
        return fig.to_html(include_plotlyjs='cdn')
    
    def generate_matplotlib_chart(self, data: List[Dict], chart_type: str = "bar") -> str:
        """Generate matplotlib chart and return as base64 encoded image"""
        df = pd.DataFrame(data)
        
        plt.figure(figsize=(10, 6))
        
        if chart_type == "bar":
            if len(df.columns) >= 2:
                plt.bar(df.iloc[:, 0], df.iloc[:, 1])
                plt.xlabel(df.columns[0])
                plt.ylabel(df.columns[1])
        elif chart_type == "line":
            if len(df.columns) >= 2:
                plt.plot(df.iloc[:, 0], df.iloc[:, 1], marker='o')
                plt.xlabel(df.columns[0])
                plt.ylabel(df.columns[1])
        
        plt.title("Data Visualization")
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        # Save to base64
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
        plt.close()
        
        buf.seek(0)
        image_base64 = base64.b64encode(buf.read()).decode('utf-8')
        return f"data:image/png;base64,{image_base64}"
    
    def generate_visualization(self, data: List[Dict], query: str, chart_type: Optional[str] = None) -> Dict[str, Any]:
        """Main method to generate appropriate visualization"""
        if not data:
            return {"type": "none", "content": "No data to visualize", "message": "No results found"}
        
        # Determine chart type
        determined_type = chart_type or self.determine_chart_type(data, query)
        
        try:
            if determined_type == "line":
                html_content = self.generate_line_chart(data, f"Analysis: {query}")
                return {"type": "line", "content": html_content, "format": "html"}
            elif determined_type == "bar":
                html_content = self.generate_bar_chart(data, f"Analysis: {query}")
                return {"type": "bar", "content": html_content, "format": "html"}
            elif determined_type == "pie":
                html_content = self.generate_pie_chart(data, f"Distribution: {query}")
                return {"type": "pie", "content": html_content, "format": "html"}
            elif determined_type == "scatter":
                html_content = self.generate_scatter_plot(data, f"Correlation: {query}")
                return {"type": "scatter", "content": html_content, "format": "html"}
            else:
                # Return table format
                return {"type": "table", "content": data, "format": "json"}
        except Exception as e:
            # Fallback to matplotlib
            try:
                image_b64 = self.generate_matplotlib_chart(data, "bar")
                return {"type": "image", "content": image_b64, "format": "base64"}
            except:
                return {"type": "table", "content": data, "format": "json", "error": str(e)}

# Global instance
visualizer = VisualizationGenerator()
