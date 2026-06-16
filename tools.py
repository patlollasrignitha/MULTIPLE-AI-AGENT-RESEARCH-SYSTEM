from langchain.tools import tool 
import requests
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS
import os 
from dotenv import load_dotenv
from rich import print
load_dotenv(override=True)

@tool
def web_search(query : str) -> str:
    """Search the web for recent and reliable information on a topic . Returns Titles , URLs and snippets."""
    # Try Tavily Search first if API key is configured
    tavily_key = os.getenv("TAVILY_API_KEY")
    if tavily_key and tavily_key.strip() and tavily_key != "your_tavily_api_key_here":
        try:
            from tavily import TavilyClient
            tavily = TavilyClient(api_key=tavily_key)
            response = tavily.search(query=query, max_results=5)
            out = []
            for r in response.get("results", []):
                out.append(
                    f"Title: {r.get('title')}\nURL: {r.get('url')}\nSnippet: {r.get('content')[:300]}\n"
                )
            if out:
                return "\n----\n".join(out)
        except Exception:
            pass

    # DuckDuckGo fallback
    try:
        with DDGS() as ddgs:
            results = []
            # Try multiple backends because the default 'auto' can return empty or block
            for backend in ["html", "lite", "auto"]:
                try:
                    res = list(ddgs.text(query, backend=backend, max_results=5))
                    if res:
                        results = res
                        break
                except Exception:
                    continue
            
            if not results:
                return "No search results found."
                
            out = []
            for r in results:
                out.append(
                    f"Title: {r.get('title')}\nURL: {r.get('href')}\nSnippet: {r.get('body')[:300]}\n"
                )
            return "\n----\n".join(out)
    except Exception as e:
        return f"DuckDuckGo search error: {str(e)}"

@tool
def scrape_url(url: str) -> str:
    """Scrape and return clean text content from a given URL for deeper reading."""
    try:
        resp = requests.get(url, timeout=8, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(resp.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer"]):
            tag.decompose()
        return soup.get_text(separator=" ", strip=True)[:3000]
    except Exception as e:
        return f"Could not scrape URL: {str(e)}"

