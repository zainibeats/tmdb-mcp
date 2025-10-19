# TMDB MCP Server

A Model Context Protocol (MCP) server that provides read-only access to The Movie Database (TMDB) API for movie and TV show information.

## Purpose

This MCP server provides a secure interface for AI assistants to query movie and TV show data from TMDB, including searching, retrieving details, discovering content, and getting recommendations.

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

Follow the [installation guide](./INSTALL.md) for step-by-step instructions to get the MCP server up and running. The process includes building the Docker image, configuring your TMDB API key, setting up the MCP catalog, and integrating with Claude Desktop.

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

## Architecture
```
Claude Desktop → MCP Gateway → TMDB MCP Server → TMDB API
                      ↓
              Docker Desktop Secrets
                (TMDB_API_KEY)
```

## Development

### Local Testing
```bash
# Set environment variables for testing
export TMDB_API_KEY="your-api-key"

# Run directly
python tmdb_server.py

# Test MCP protocol
echo '{"jsonrpc":"2.0","method":"tools/list","id":1}' | python tmdb_server.py
```

### Adding New Tools

1. Add the function to `tmdb_server.py`
2. Decorate with `@mcp.tool()`
3. Update the catalog entry with the new tool name
4. Rebuild the Docker image

## Troubleshooting

### Tools Not Appearing
- Verify Docker image built successfully
- Check catalog and registry files
- Ensure Claude Desktop config includes custom catalog
- Restart Claude Desktop

### Authentication Errors
- Verify secrets with `docker mcp secret list`
- Ensure TMDB_API_KEY is set correctly
- Check API key validity at TMDB website

### No Results Returned
- Verify TMDB API is accessible
- Check rate limiting (40 requests/10 seconds)
- Ensure search queries are properly formatted

## Security Considerations

- TMDB API key stored in Docker Desktop secrets
- Never hardcode credentials
- Running as non-root user
- Read-only operations only
- No user authentication endpoints accessed

## API Rate Limits

TMDB API has the following rate limits:
- 40 requests per 10 seconds
- No daily limit for free tier

## License

MIT License
