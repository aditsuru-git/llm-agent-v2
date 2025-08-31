from datetime import datetime
import httpx
from langchain_core.tools import tool

@tool
def current_time() -> str:
    """Returns the current UTC time in ISO format."""
    return datetime.now().isoformat()

@tool
def calculate(expression: str) -> str:
    """
    Safely evaluates a mathematical expression and returns the result as a string.
    Example: '2 + 2 * 10' -> '22'
    """
    try:
        result = eval(expression, {"__builtins__": {}})
        return str(result)
    except Exception as e:
        return f"Error: Invalid expression. {e}"

@tool
def fetch_url(url: str) -> str:
    """Fetches the first 4000 characters of raw text/HTML from a URL."""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
        }
        with httpx.Client(headers=headers, follow_redirects=True) as client:
            r = client.get(url, timeout=10)
            r.raise_for_status()
            return r.text[:4000]
    except httpx.RequestError as e:
        return f"Error fetching URL: {e}"
    except Exception as e:
        return f"An unexpected error occurred: {e}"