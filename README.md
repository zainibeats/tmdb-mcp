# TMDB MCP Server

> **Note**: This project contains AI-generated code.

A local Model Context Protocol (MCP) toolchain for media discovery and TMDB-based provider URL resolution.

## Purpose

The main TMDB MCP server provides a read-only interface for AI assistants (eg. Claude Desktop, LM Studio, Claude Code etc.) to query movie and TV show data from TMDB, including searching, retrieving details, discovering content, and getting recommendations.

The separate embed resolver MCP server turns a confirmed TMDB ID into provider URLs and a local UI prefill URL. This keeps discovery and URL resolution as separate local services.

## Features

### MCP Tools
- **`find_media`** - Search movies, TV, or both by title/query
- **`discover_media`** - Discover movies or TV shows with common filters
- **`get_media_details`** - Get compact details for a confirmed movie or TV ID
- **`get_similar_media`** - Find related titles from a confirmed movie or TV ID
- **`get_trending_media`** - Get trending movies, TV, or both
- **`get_popular_media`** - Get currently popular movies or TV shows
- **`get_top_rated_media`** - Get top-rated movies or TV shows
- **`get_genres`** - Get TMDB genre IDs for movie or TV discovery
- **`get_movie_credits`** - Get core cast/crew for a movie
- **`list_embed_providers`** - List configured provider names
- **`generate_embed_urls_for_tmdb`** - Generate provider URLs and a helper UI URL after user selection

The Python TMDB server still includes lower-level raw TMDB helpers for direct local development, but the recommended client configuration exposes the focused assistant-friendly tools by default.

## Recommended Runtime

Linux users should run the Python MCP servers directly over stdio. This does not require Docker MCP Gateway or Docker Desktop.

Docker MCP Gateway is also supported for users who already have Docker Desktop with MCP Toolkit.

The Docker MCP setup uses three images:

- `zainibeats/tmdb-mcp:latest` - TMDB discovery MCP server
- `zainibeats/tmdb-embed-resolver:latest` - MCP server that returns provider URLs and a clickable local UI link
- `zainibeats/tmdb-embed-ui:latest` - companion UI served at `http://localhost:8689`

Keeping discovery and provider-link generation as separate MCP servers makes tool choice easier for local models: first discover and compare titles, then call the resolver only after the user chooses a specific TMDB ID.

## Prerequisites

- Python 3.11+
- TMDB API Key (free from https://www.themoviedb.org/settings/api)
- LM Studio 0.4.0+, Claude Desktop, Claude Code, or another stdio MCP client
- Optional: Docker Engine for the companion UI container
- Optional: Docker Desktop with MCP Toolkit for Docker MCP Gateway

## Installation

- Linux/native stdio: [Linux install guide](./docs/LINUX.md)
- Docker MCP Gateway: [Docker MCP install guide](./docs/INSTALL.md)

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
       stdio MCP processes
          |          |
   TMDB MCP      Embed Resolver MCP
      |               |
   TMDB API      Provider templates
```

Docker MCP Gateway can replace the direct stdio processes when using the optional Docker MCP setup.

Expected flow:

1. The user asks for recommendations or a known title.
2. The assistant uses the TMDB MCP server to search, discover, and present options.
3. After the user commits to a movie or TV show, the assistant calls the embed resolver with `media_type` and `tmdb_id`.
4. The resolver returns provider URLs plus a clickable `ui_url` such as `http://localhost:8689/?mediaType=movie&tmdbId=550`.
5. Opening the `ui_url` pre-fills the UI and generates provider links locally.

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
