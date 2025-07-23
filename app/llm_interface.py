import os
import requests
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

HEADERS = {
    "Content-Type": "application/json"
}

def ask_llm(question: str) -> str:
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY not set in environment variables")

    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": f"""
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

Question: {question}
"""

                    }
                ]
            }
        ]
    }

    response = requests.post(f"{GEMINI_URL}?key={GEMINI_API_KEY}", headers=HEADERS, json=payload)
    data = response.json()

    try:
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        return f"Error from LLM: {data}"  # Better visibility into LLM errors
