# TMDB MCP Server

> **Note**: This project contains AI-generated code.

A local Model Context Protocol (MCP) toolchain for media discovery and TMDB-based provider URL resolution.

## Purpose

The main TMDB MCP server provides a read-only interface for AI assistants (eg. Claude Desktop, LM Studio, Claude Code etc.) to query movie and TV show data from TMDB, including searching, retrieving details, discovering content, and getting recommendations.

The separate embed resolver MCP server turns a confirmed TMDB ID into provider URLs and a local UI prefill URL. This keeps discovery and URL resolution as separate local services.

## Features

### Current Implementation
- **`search_movies`** - Search for movies by title with pagination support
- **`search_tv`** - Search for TV shows by title with pagination support
- **`search_multi`** - Search across movies, TV shows, and people
- **`get_movie_details`** - Get comprehensive details about a specific movie
- **`get_tv_details`** - Get comprehensive details about a specific TV show
- **`get_top_rated_movies`** - Retrieve top-rated movies with pagination
- **`get_top_rated_tv`** - Retrieve top-rated TV shows with pagination
- **`get_popular_movies`** - Get currently popular movies with pagination
- **`get_popular_tv`** - Get currently popular TV shows with pagination
- **`get_trending`** - Get trending content (movies/TV/all) for day or week
- **`get_similar_movies`** - Find movies similar to a given movie
- **`get_similar_tv`** - Find TV shows similar to a given TV show
- **`get_genres`** - Get list of available genres for movies or TV
- **`get_movie_credits`** - Get cast and crew information for a movie
- **`get_movie_reviews`** - Get user reviews for a movie with pagination
- **`discover_movies`** - Discover movies with advanced filters (genre, year, rating, etc.)
- **`discover_tv`** - Discover TV shows with advanced filters

## Prerequisites

- Docker Desktop with MCP Toolkit enabled
- Docker MCP CLI plugin (`docker mcp` command)
- TMDB API Key (free from https://www.themoviedb.org/settings/api)

## Installation

Follow the [installation guide](./docs/INSTALL.md) for step-by-step instructions to get the MCP servers running through Docker MCP Gateway.

## Usage Examples

In Claude Desktop, you can ask:
- "Find the TMDB ID for Breaking Bad"
- "Search for movies with 'inception' in the title"
- "Show me the top rated sci-fi movies"
- "Get details about movie ID 550"
- "Find TV shows similar to The Office"
- "What movies are trending this week?"
- "Show me popular TV shows page 2"
- "Get the cast of The Dark Knight"
- "Find horror movies from 2023 with rating above 7"
- "Search for content related to Christopher Nolan"
- "Generate provider URLs for movie TMDB ID 550"
- "Generate provider URLs for TV TMDB ID 1396 season 1 episode 1"

## Architecture
```
Claude Desktop / LM Studio / Claude Code
              |
       Docker MCP Gateway
          |          |
   TMDB MCP      Embed Resolver MCP
      |               |
   TMDB API      Provider templates
```

Expected flow:

1. The user asks for recommendations or a known title.
2. The assistant uses the TMDB MCP server to search, discover, and present options.
3. After the user commits to a movie or TV show, the assistant calls the embed resolver with `media_type` and `tmdb_id`.
4. The resolver returns provider URLs plus a `ui_url` such as `http://localhost:8689/?mediaType=movie&tmdbId=550`.

## Development

### Local Testing
```bash
# Set environment variables for testing
export TMDB_API_KEY="your-api-key"

# Run directly
python tmdb_server.py

# Run the embed resolver directly
python embed-resolver-mcp/server.py

# Test MCP protocol
echo '{"jsonrpc":"2.0","method":"tools/list","id":1}' | python tmdb_server.py
```

### Adding TMDB Tools

1. Add the function to `tmdb_server.py`
2. Decorate with `@mcp.tool()`
3. Update the catalog entry with the new tool name
4. Rebuild the Docker image

### Adding Resolver Tools

1. Add the function to `embed-resolver-mcp/server.py`
2. Decorate with `@mcp.tool()`
3. Update the resolver catalog entry
4. Rebuild the resolver Docker image

## API Rate Limits

TMDB API has the following rate limits:
- 40 requests per 10 seconds
- No daily limit for free tier

## License

MIT License
