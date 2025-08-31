from datetime import datetime
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
