# Project Direction

## Goal

Build a local-first MCP tool service that helps an AI assistant find movies and TV shows through TMDB and present concise candidate choices.

The primary product is the MCP tool service. End users should use it through an existing chat interface such as Open WebUI, LM Studio, Claude Code, or another MCP/OpenAPI-capable client.

## Intended Flow

1. The user asks for a movie, TV show, recommendation, trend, or filtered discovery result.
2. The assistant uses focused TMDB discovery tools.
3. The assistant presents a short, human-readable list of candidates with enough detail to choose confidently.
4. The user can ask follow-up questions, request similar titles, or ask for details on a specific TMDB result.

## Product Boundaries

### In Scope

- Local MCP server for assistant-driven media discovery.
- Assistant-friendly TMDB tools with clear, focused behavior.
- Human-readable tool responses that are easy for local models to summarize.
- Open WebUI integration through `mcpo` without making this project a standalone chat UI.
- Equal support for Ollama and LM Studio as model backends through Open WebUI.
- Server-admin configured TMDB API keys.
- Direct Python local development and Docker-based deployment.

### Out of Scope

- User accounts, watchlists, ratings, or TMDB write operations.
- Making the UI the main product.
- Full TMDB API coverage.
- Hard-coded sensitive values.
- Provider/embed URL generation as part of the recommended workflow.

## MCP Tool Surface

Expose only focused assistant-friendly tools in the Docker MCP catalog. Avoid exposing broad raw TMDB proxy tools by default.

The tool surface should not be too small. It should cover the common assistant workflows without forcing models into generic raw API calls.

Proposed discovery tools:

- `find_media` - Search movies, TV, or both by title/query.
- `discover_media` - Discover movies or TV shows with common filters.
- `get_media_details` - Get compact details for a confirmed movie or TV ID.
- `get_similar_media` - Find related titles from a confirmed movie or TV ID.
- `get_trending_media` - Get trending movies, TV, or both.
- `get_popular_media` - Get currently popular movies or TV shows.
- `get_top_rated_media` - Get top-rated movies or TV shows.
- `get_genres` - Get TMDB genre IDs for movie or TV discovery.
- `get_movie_credits` - Get core cast/crew for a movie when useful for user choice.

## Response Style

Discovery tools should return human-readable text, not raw TMDB JSON dumps.

Candidate lists should include:

- Title or name
- TMDB ID
- Media type
- Release year or first air year
- Rating when available
- Short overview

Details responses should include:

- Title or name
- TMDB ID
- Media type
- Release date or first air date
- Runtime or season count when available
- Genres
- Rating and vote count
- Short overview
- Useful links or image paths only when helpful

Structured JSON can still be used internally and in tests, but the default MCP response should be optimized for an assistant reading and relaying results.

## Cleanup Priorities

1. Add formatting helpers that convert TMDB JSON into compact human-readable responses.
2. Replace the default exposed TMDB catalog with focused assistant-friendly tools.
3. Keep or move raw TMDB helpers as internal implementation details.
4. Tighten parameter validation and normalization for media type, page, IDs, and filters.
5. Add and maintain Open WebUI documentation using `mcpo`.
6. Keep provider/embed resolver code out of the recommended workflow unless that scope is explicitly reintroduced.
7. Update README and install docs to reflect the focused TMDB-only workflow.
8. Add lightweight tests for formatting helpers and validation.

## Development Support

Open WebUI plus `mcpo` is the recommended end-user setup.

Docker MCP Gateway remains supported for MCP clients that use it.

Direct local development remains first-class:

- Root TMDB MCP server should run with Python.
- Docs should clearly show direct MCP, Open WebUI, and Docker commands.

## Open Questions

- Should raw TMDB tools remain callable in direct development but omitted from Docker MCP catalogs, or should they be removed entirely after focused replacements exist?
- Should `get_movie_credits` be generalized to `get_media_credits` with TV support, or kept movie-only until there is a clear need?
- Should `discover_media` expose a simple set of named parameters, accept advanced JSON filters, or support both?
