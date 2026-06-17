# TMDB MCP Server

> **Note**: This project contains AI-generated code.

A local Model Context Protocol (MCP) server for movie and TV discovery through TMDB.

## Purpose

The TMDB MCP server provides a read-only interface for AI assistants and MCP clients. It can query movie and TV show data from TMDB, including searching, retrieving details, discovering content, and getting recommendations.

The preferred end-user experience is to connect this server to an existing chat UI, such as Open WebUI, through an MCP-to-OpenAPI bridge. This keeps the project modular and avoids shipping a standalone recommendation app.

## Features

### MCP Tools
- **`find_media`** - Search movies, TV, or both by title/query
- **`discover_media`** - Discover movies or TV shows with common filters
- **`get_media_details`** - Get compact details for a confirmed movie or TV ID
- **`get_similar_media`** - Find related titles from a confirmed movie or TV ID
- **`get_recommended_media`** - Get TMDB recommendations from a confirmed movie or TV ID
- **`get_trending_media`** - Get trending movies, TV, or both
- **`get_popular_media`** - Get currently popular movies or TV shows
- **`get_top_rated_media`** - Get top-rated movies or TV shows
- **`get_genres`** - Get TMDB genre IDs for movie or TV discovery
- **`get_movie_credits`** - Get core cast/crew for a movie
- **`get_tv_credits`** - Get core cast/crew for a TV show
- **`search_person`** - Search TMDB people by name
- **`get_person_details`** - Get compact details for a confirmed person ID
- **`get_person_credits`** - Get a person's combined movie and TV credits

The Python TMDB server still includes lower-level raw TMDB helpers for direct local development, but the recommended client configuration exposes the focused assistant-friendly tools by default.

## Recommended Runtime

Linux users can run the Python MCP server directly over stdio for clients such as LM Studio, Claude Code, and Claude Desktop.

Open WebUI users should expose this MCP server through `mcpo`, then add the generated OpenAPI tool server in Open WebUI as a user opt-in tool. This works with Ollama or any OpenAI-compatible model backend, including LM Studio at `http://localhost:1234/v1`.

Docker MCP Gateway is also supported for users who already have Docker Desktop with MCP Toolkit.

The default Docker image is `skimming124/tmdb-mcp:latest`.

## Prerequisites

- Python 3.11+
- TMDB API Key (free from https://www.themoviedb.org/settings/api)
- Open WebUI, LM Studio, Claude Code, or another MCP/OpenAPI-capable client
- Optional: `mcpo` for Open WebUI integration
- Optional: Docker Desktop with MCP Toolkit for Docker MCP Gateway

## Installation

- Linux/native stdio: [Linux install guide](./docs/LINUX.md)
- Open WebUI with Ollama or LM Studio: [Open WebUI guide](./docs/OPENWEBUI.md)
- Example Docker Compose stack for Ollama, Open WebUI, and this project: [`compose.example.yml`](./compose.example.yml)
- Docker MCP Gateway: [Docker MCP install guide](./docs/INSTALL.md)

## Usage Examples

In your MCP client, you can ask:
- "Find the TMDB ID for Breaking Bad"
- "Search for movies with 'inception' in the title"
- "Show me the top rated sci-fi movies"
- "Get details about movie ID 550"
- "Find TV shows similar to The Office"
- "Recommend movies based on Arrival"
- "What movies are trending this week?"
- "Show me popular TV shows page 2"
- "Get the cast of The Dark Knight"
- "Find Christopher Nolan and show his most notable credits"
- "Find horror movies from 2023 with rating above 7"
- "Search for content related to Christopher Nolan"

## Architecture
```
Open WebUI / LM Studio / Claude Code / other client
              |
       mcpo or stdio MCP
              |
          TMDB MCP
              |
          TMDB API
```

Docker MCP Gateway can replace the direct stdio processes when using the optional Docker MCP setup.

Expected flow:

1. The user asks for recommendations, trends, similar titles, or a known title.
2. The assistant uses the TMDB MCP server to search, discover, and compare options.
3. The assistant presents a short, human-readable answer with TMDB-backed details.

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

### Adding TMDB Tools

1. Add the function to `tmdb_server.py`
2. Decorate with `@mcp.tool()`
3. Update the catalog entry with the new tool name
4. Rebuild the Docker image

## API Rate Limits

TMDB API has the following rate limits:
- 40 requests per 10 seconds
- No daily limit for free tier

## License

MIT License
