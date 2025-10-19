#!/usr/bin/env python3
"""
Simple TMDB MCP Server - Provides read-only access to The Movie Database API
"""
import os
import sys
import logging
import json
from datetime import datetime, timezone
import httpx
from mcp.server.fastmcp import FastMCP

# Configure logging to stderr
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger("tmdb-server")

# Initialize MCP server - NO PROMPT PARAMETER!
mcp = FastMCP("tmdb")

# Configuration
API_KEY = os.environ.get("TMDB_API_KEY", "")
BASE_URL = "https://api.themoviedb.org/3"

# === UTILITY FUNCTIONS ===
async def make_tmdb_request(endpoint: str, params: dict = None) -> str:
    """Make a request to TMDB API and return raw JSON response."""
    if not API_KEY:
        return '{"error": "TMDB_API_KEY not set"}'
    
    url = f"{BASE_URL}{endpoint}"
    params = params or {}
    params["api_key"] = API_KEY
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, params=params, timeout=10)
            response.raise_for_status()
            return json.dumps(response.json(), indent=2)
        except httpx.HTTPStatusError as e:
            return json.dumps({"error": f"API error: {e.response.status_code}"})
        except Exception as e:
            return json.dumps({"error": str(e)})

# === MCP TOOLS ===

# Search Tools
@mcp.tool()
async def search_movies(query: str = "", page: str = "1") -> str:
    """Search for movies by title - returns raw JSON from TMDB /search/movie endpoint."""
    logger.info(f"Searching movies: {query}")
    
    if not query.strip():
        return '{"error": "Query parameter is required"}'
    
    params = {"query": query.strip()}
    if page.strip():
        params["page"] = page.strip()
    
    result = await make_tmdb_request("/search/movie", params)
    return result

@mcp.tool()
async def search_tv(query: str = "", page: str = "1") -> str:
    """Search for TV shows by title - returns raw JSON from TMDB /search/tv endpoint."""
    logger.info(f"Searching TV shows: {query}")
    
    if not query.strip():
        return '{"error": "Query parameter is required"}'
    
    params = {"query": query.strip()}
    if page.strip():
        params["page"] = page.strip()
    
    result = await make_tmdb_request("/search/tv", params)
    return result

@mcp.tool()
async def search_multi(query: str = "", page: str = "1") -> str:
    """Search across movies, TV shows, and people - returns raw JSON from TMDB /search/multi endpoint."""
    logger.info(f"Multi-search: {query}")
    
    if not query.strip():
        return '{"error": "Query parameter is required"}'
    
    params = {"query": query.strip()}
    if page.strip():
        params["page"] = page.strip()
    
    result = await make_tmdb_request("/search/multi", params)
    return result

# Details Tools
@mcp.tool()
async def get_movie_details(movie_id: str = "", append_to_response: str = "") -> str:
    """Get detailed information about a specific movie - returns raw JSON from TMDB /movie/{id} endpoint."""
    logger.info(f"Getting movie details for ID: {movie_id}")
    
    if not movie_id.strip():
        return '{"error": "Movie ID is required"}'
    
    params = {}
    if append_to_response.strip():
        params["append_to_response"] = append_to_response.strip()
    
    result = await make_tmdb_request(f"/movie/{movie_id.strip()}", params)
    return result

@mcp.tool()
async def get_tv_details(tv_id: str = "", append_to_response: str = "") -> str:
    """Get detailed information about a specific TV show - returns raw JSON from TMDB /tv/{id} endpoint."""
    logger.info(f"Getting TV show details for ID: {tv_id}")
    
    if not tv_id.strip():
        return '{"error": "TV ID is required"}'
    
    params = {}
    if append_to_response.strip():
        params["append_to_response"] = append_to_response.strip()
    
    result = await make_tmdb_request(f"/tv/{tv_id.strip()}", params)
    return result

# Top Rated / Popular Tools
@mcp.tool()
async def get_top_rated_movies(page: str = "1") -> str:
    """Get top rated movies - returns raw JSON from TMDB /movie/top_rated endpoint."""
    logger.info(f"Getting top rated movies, page: {page}")
    
    params = {}
    if page.strip():
        params["page"] = page.strip()
    
    result = await make_tmdb_request("/movie/top_rated", params)
    return result

@mcp.tool()
async def get_top_rated_tv(page: str = "1") -> str:
    """Get top rated TV shows - returns raw JSON from TMDB /tv/top_rated endpoint."""
    logger.info(f"Getting top rated TV shows, page: {page}")
    
    params = {}
    if page.strip():
        params["page"] = page.strip()
    
    result = await make_tmdb_request("/tv/top_rated", params)
    return result

@mcp.tool()
async def get_popular_movies(page: str = "1") -> str:
    """Get popular movies - returns raw JSON from TMDB /movie/popular endpoint."""
    logger.info(f"Getting popular movies, page: {page}")
    
    params = {}
    if page.strip():
        params["page"] = page.strip()
    
    result = await make_tmdb_request("/movie/popular", params)
    return result

@mcp.tool()
async def get_popular_tv(page: str = "1") -> str:
    """Get popular TV shows - returns raw JSON from TMDB /tv/popular endpoint."""
    logger.info(f"Getting popular TV shows, page: {page}")
    
    params = {}
    if page.strip():
        params["page"] = page.strip()
    
    result = await make_tmdb_request("/tv/popular", params)
    return result

# Trending Tool
@mcp.tool()
async def get_trending(media_type: str = "all", time_window: str = "day", page: str = "1") -> str:
    """Get trending items - returns raw JSON from TMDB /trending/{media_type}/{time_window} endpoint."""
    logger.info(f"Getting trending {media_type} for {time_window}")
    
    # Validate media_type
    valid_media_types = ["movie", "tv", "all", "person"]
    if not media_type.strip() or media_type.strip() not in valid_media_types:
        media_type = "all"
    
    # Validate time_window
    valid_time_windows = ["day", "week"]
    if not time_window.strip() or time_window.strip() not in valid_time_windows:
        time_window = "day"
    
    params = {}
    if page.strip():
        params["page"] = page.strip()
    
    result = await make_tmdb_request(f"/trending/{media_type.strip()}/{time_window.strip()}", params)
    return result

# Similar / Recommendations Tools
@mcp.tool()
async def get_similar_movies(movie_id: str = "", page: str = "1") -> str:
    """Get movies similar to a specific movie - returns raw JSON from TMDB /movie/{id}/similar endpoint."""
    logger.info(f"Getting similar movies for ID: {movie_id}")
    
    if not movie_id.strip():
        return '{"error": "Movie ID is required"}'
    
    params = {}
    if page.strip():
        params["page"] = page.strip()
    
    result = await make_tmdb_request(f"/movie/{movie_id.strip()}/similar", params)
    return result

@mcp.tool()
async def get_similar_tv(tv_id: str = "", page: str = "1") -> str:
    """Get TV shows similar to a specific TV show - returns raw JSON from TMDB /tv/{id}/similar endpoint."""
    logger.info(f"Getting similar TV shows for ID: {tv_id}")
    
    if not tv_id.strip():
        return '{"error": "TV ID is required"}'
    
    params = {}
    if page.strip():
        params["page"] = page.strip()
    
    result = await make_tmdb_request(f"/tv/{tv_id.strip()}/similar", params)
    return result

# Genres Tool
@mcp.tool()
async def get_genres(media_type: str = "movie") -> str:
    """Get list of genres - returns raw JSON from TMDB /genre/{media_type}/list endpoint."""
    logger.info(f"Getting {media_type} genres")
    
    # Validate media_type
    valid_types = ["movie", "tv"]
    if not media_type.strip() or media_type.strip() not in valid_types:
        media_type = "movie"
    
    result = await make_tmdb_request(f"/genre/{media_type.strip()}/list")
    return result

# Credits and Reviews Tools
@mcp.tool()
async def get_movie_credits(movie_id: str = "") -> str:
    """Get cast and crew for a movie - returns raw JSON from TMDB /movie/{id}/credits endpoint."""
    logger.info(f"Getting movie credits for ID: {movie_id}")
    
    if not movie_id.strip():
        return '{"error": "Movie ID is required"}'
    
    result = await make_tmdb_request(f"/movie/{movie_id.strip()}/credits")
    return result

@mcp.tool()
async def get_movie_reviews(movie_id: str = "", page: str = "1") -> str:
    """Get reviews for a movie - returns raw JSON from TMDB /movie/{id}/reviews endpoint."""
    logger.info(f"Getting movie reviews for ID: {movie_id}")
    
    if not movie_id.strip():
        return '{"error": "Movie ID is required"}'
    
    params = {}
    if page.strip():
        params["page"] = page.strip()
    
    result = await make_tmdb_request(f"/movie/{movie_id.strip()}/reviews", params)
    return result

# Discover / Filter Tools
@mcp.tool()
async def discover_movies(params_json: str = "{}") -> str:
    """Discover movies with filters - returns raw JSON from TMDB /discover/movie endpoint. Pass filters as JSON string."""
    logger.info(f"Discovering movies with params: {params_json}")
    
    try:
        params = json.loads(params_json) if params_json.strip() else {}
    except json.JSONDecodeError:
        return '{"error": "Invalid JSON parameters"}'
    
    result = await make_tmdb_request("/discover/movie", params)
    return result

@mcp.tool()
async def discover_tv(params_json: str = "{}") -> str:
    """Discover TV shows with filters - returns raw JSON from TMDB /discover/tv endpoint. Pass filters as JSON string."""
    logger.info(f"Discovering TV shows with params: {params_json}")
    
    try:
        params = json.loads(params_json) if params_json.strip() else {}
    except json.JSONDecodeError:
        return '{"error": "Invalid JSON parameters"}'
    
    result = await make_tmdb_request("/discover/tv", params)
    return result

# === SERVER STARTUP ===
if __name__ == "__main__":
    logger.info("Starting TMDB MCP server...")
    
    # Add startup check
    if not API_KEY:
        logger.warning("TMDB_API_KEY not set - server will return errors for all requests")
    
    try:
        mcp.run(transport='stdio')
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        sys.exit(1)