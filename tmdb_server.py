#!/usr/bin/env python3
"""
Simple TMDB MCP Server - Provides read-only access to The Movie Database API
"""
import os
import sys
import logging
import json
import httpx
from mcp.server.fastmcp import FastMCP
from tmdb_formatting import (
    error_text,
    format_candidate_list,
    format_genres,
    format_media_details,
    format_movie_credits,
    normalize_media_type,
    normalize_page,
    normalize_time_window,
    parse_json_object,
    require_tmdb_id,
)

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
async def make_tmdb_json(endpoint: str, params: dict = None) -> dict:
    """Make a request to TMDB API and return a JSON-compatible dict."""
    if not API_KEY:
        return {"error": "TMDB_API_KEY not set"}
    
    url = f"{BASE_URL}{endpoint}"
    params = params or {}
    params["api_key"] = API_KEY
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            return {"error": f"API error: {e.response.status_code}"}
        except Exception as e:
            return {"error": str(e)}


async def make_tmdb_request(endpoint: str, params: dict = None) -> str:
    """Make a request to TMDB API and return raw JSON response."""
    return json.dumps(await make_tmdb_json(endpoint, params), indent=2)


def _clean(value: str) -> str:
    return str(value).strip()


def _discover_params(
    media_type: str,
    page: str,
    sort_by: str,
    with_genres: str,
    year: str,
    first_air_date_year: str,
    vote_average_gte: str,
    vote_count_gte: str,
    filters_json: str,
) -> dict:
    params = parse_json_object(filters_json, "filters_json")
    params["page"] = normalize_page(page)

    if _clean(sort_by):
        params["sort_by"] = _clean(sort_by)
    if _clean(with_genres):
        params["with_genres"] = _clean(with_genres)
    if media_type == "movie" and _clean(year):
        params["year"] = _clean(year)
    if media_type == "tv" and _clean(first_air_date_year):
        params["first_air_date_year"] = _clean(first_air_date_year)
    if _clean(vote_average_gte):
        params["vote_average.gte"] = _clean(vote_average_gte)
    if _clean(vote_count_gte):
        params["vote_count.gte"] = _clean(vote_count_gte)
    return params

# === MCP TOOLS ===

# Focused assistant-friendly tools
@mcp.tool()
async def find_media(query: str = "", media_type: str = "all", page: str = "1") -> str:
    """Search movies, TV, or both by title and return compact candidate choices."""
    logger.info("Finding media: %s (%s)", query, media_type)

    if not query.strip():
        return error_text("query is required")

    try:
        normalized_media_type = normalize_media_type(media_type, allow_all=True)
        normalized_page = normalize_page(page)
    except ValueError as e:
        return error_text(str(e))

    endpoint_by_type = {
        "movie": "/search/movie",
        "tv": "/search/tv",
        "all": "/search/multi",
    }
    payload = await make_tmdb_json(
        endpoint_by_type[normalized_media_type],
        {"query": query.strip(), "page": normalized_page},
    )
    fallback = None if normalized_media_type == "all" else normalized_media_type
    return format_candidate_list(
        payload,
        heading=f"Matches for {query.strip()}",
        fallback_media_type=fallback,
    )


@mcp.tool()
async def discover_media(
    media_type: str = "movie",
    page: str = "1",
    sort_by: str = "popularity.desc",
    with_genres: str = "",
    year: str = "",
    first_air_date_year: str = "",
    vote_average_gte: str = "",
    vote_count_gte: str = "",
    filters_json: str = "{}",
) -> str:
    """Discover movies or TV shows with common filters and compact results."""
    logger.info("Discovering focused media: %s", media_type)

    try:
        normalized_media_type = normalize_media_type(media_type)
        params = _discover_params(
            normalized_media_type,
            page,
            sort_by,
            with_genres,
            year,
            first_air_date_year,
            vote_average_gte,
            vote_count_gte,
            filters_json,
        )
    except ValueError as e:
        return error_text(str(e))

    payload = await make_tmdb_json(f"/discover/{normalized_media_type}", params)
    return format_candidate_list(
        payload,
        heading=f"Discovered {normalized_media_type} results",
        fallback_media_type=normalized_media_type,
    )


@mcp.tool()
async def get_media_details(media_type: str = "movie", tmdb_id: str = "") -> str:
    """Get compact details for a confirmed movie or TV ID."""
    logger.info("Getting %s details for ID: %s", media_type, tmdb_id)

    try:
        normalized_media_type = normalize_media_type(media_type)
        normalized_id = require_tmdb_id(tmdb_id)
    except ValueError as e:
        return error_text(str(e))

    payload = await make_tmdb_json(f"/{normalized_media_type}/{normalized_id}")
    return format_media_details(payload, media_type=normalized_media_type)


@mcp.tool()
async def get_similar_media(media_type: str = "movie", tmdb_id: str = "", page: str = "1") -> str:
    """Find related titles from a confirmed movie or TV ID."""
    logger.info("Getting similar %s for ID: %s", media_type, tmdb_id)

    try:
        normalized_media_type = normalize_media_type(media_type)
        normalized_id = require_tmdb_id(tmdb_id)
        normalized_page = normalize_page(page)
    except ValueError as e:
        return error_text(str(e))

    payload = await make_tmdb_json(
        f"/{normalized_media_type}/{normalized_id}/similar",
        {"page": normalized_page},
    )
    return format_candidate_list(
        payload,
        heading=f"Similar {normalized_media_type} results for TMDB ID {normalized_id}",
        fallback_media_type=normalized_media_type,
    )


@mcp.tool()
async def get_trending_media(media_type: str = "all", time_window: str = "day", page: str = "1") -> str:
    """Get trending movies, TV, or both."""
    logger.info("Getting focused trending %s for %s", media_type, time_window)

    try:
        normalized_media_type = normalize_media_type(media_type, allow_all=True)
        normalized_time_window = normalize_time_window(time_window)
        normalized_page = normalize_page(page)
    except ValueError as e:
        return error_text(str(e))

    payload = await make_tmdb_json(
        f"/trending/{normalized_media_type}/{normalized_time_window}",
        {"page": normalized_page},
    )
    fallback = None if normalized_media_type == "all" else normalized_media_type
    return format_candidate_list(
        payload,
        heading=f"Trending {normalized_media_type} for {normalized_time_window}",
        fallback_media_type=fallback,
    )


@mcp.tool()
async def get_popular_media(media_type: str = "movie", page: str = "1") -> str:
    """Get currently popular movies or TV shows."""
    logger.info("Getting focused popular %s", media_type)

    try:
        normalized_media_type = normalize_media_type(media_type)
        normalized_page = normalize_page(page)
    except ValueError as e:
        return error_text(str(e))

    payload = await make_tmdb_json(
        f"/{normalized_media_type}/popular",
        {"page": normalized_page},
    )
    return format_candidate_list(
        payload,
        heading=f"Popular {normalized_media_type} results",
        fallback_media_type=normalized_media_type,
    )


@mcp.tool()
async def get_top_rated_media(media_type: str = "movie", page: str = "1") -> str:
    """Get top-rated movies or TV shows."""
    logger.info("Getting focused top-rated %s", media_type)

    try:
        normalized_media_type = normalize_media_type(media_type)
        normalized_page = normalize_page(page)
    except ValueError as e:
        return error_text(str(e))

    payload = await make_tmdb_json(
        f"/{normalized_media_type}/top_rated",
        {"page": normalized_page},
    )
    return format_candidate_list(
        payload,
        heading=f"Top-rated {normalized_media_type} results",
        fallback_media_type=normalized_media_type,
    )

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
    """Get TMDB genre IDs for movie or TV discovery."""
    logger.info(f"Getting {media_type} genres")
    
    try:
        normalized_media_type = normalize_media_type(media_type)
    except ValueError as e:
        return error_text(str(e))
    
    payload = await make_tmdb_json(f"/genre/{normalized_media_type}/list")
    return format_genres(payload, media_type=normalized_media_type)

# Credits and Reviews Tools
@mcp.tool()
async def get_movie_credits(movie_id: str = "") -> str:
    """Get core cast and crew for a movie."""
    logger.info(f"Getting movie credits for ID: {movie_id}")
    
    try:
        normalized_id = require_tmdb_id(movie_id, "movie_id")
    except ValueError as e:
        return error_text(str(e))
    
    payload = await make_tmdb_json(f"/movie/{normalized_id}/credits")
    payload.setdefault("id", normalized_id)
    return format_movie_credits(payload)

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
