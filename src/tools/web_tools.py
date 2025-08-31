import requests
from bs4 import BeautifulSoup
from langchain_tavily import TavilySearch
from langchain_core.tools import tool

# --- Tool 1: The Intelligent Web Searcher ---
# This allows the agent to search the web to find information and URLs on its own.
web_search = TavilySearch(max_results=3)
web_search.name = "web_search"
web_search.description = (
    "Searches the web for information, news, or to find specific URLs. "
    "Input should be a search query."
)


# --- Tool 2: The Intelligent Web Scraper ---
# This replaces the old `fetch_url` tool. It returns clean, readable text.
@tool
def scrape_webpage(url: str) -> str:
    """
    Fetches the content of a URL and returns the clean, parsed text content.
    Use this to read the content of a specific webpage after finding its URL.
    """
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        for script_or_style in soup(["script", "style"]):
            script_or_style.decompose()

        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        clean_text = "\n".join(chunk for chunk in chunks if chunk)

        if not clean_text:
            return "Error: The webpage is empty or contains no readable text."

        return clean_text

    except requests.RequestException as e:
        return f"Error: Failed to fetch the URL. Reason: {e}"
    except Exception as e:
        return f"Error: An unexpected error occurred during scraping. Reason: {e}"
