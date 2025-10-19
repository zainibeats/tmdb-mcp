# TMDB MCP Server - Implementation Guide for Claude

## Overview

This MCP server provides raw JSON responses from The Movie Database (TMDB) API. All tools return unmodified JSON directly from TMDB endpoints.

## Key Implementation Details

### Authentication
- Uses TMDB API v3 with API key authentication
- API key stored in Docker secrets as `TMDB_API_KEY`
- All requests include the API key as a query parameter

### Response Format
All tools return raw JSON from TMDB. The structure typically includes:
- `results` array for search/list endpoints
- `page`, `total_pages`, `total_results` for paginated responses
- Detailed object for individual item endpoints

### Tool Categories

#### Search Tools
- Accept `query` and optional `page` parameters
- Return paginated results with movie/TV/person objects
- Multi-search returns mixed media types

#### Detail Tools
- Require specific ID (movie_id or tv_id)
- Support `append_to_response` for additional data (credits, videos, etc.)
- Return comprehensive object with all available information

#### List Tools (Popular/Top Rated)
- Optional `page` parameter for pagination
- Return standard paginated response format
- Sorted by TMDB's internal algorithms

#### Discover Tools
- Accept complex filter parameters as JSON string
- Support filters like: `with_genres`, `primary_release_year`, `vote_average.gte`
- Most powerful for advanced queries

### Pagination

All paginated endpoints support:
- Default page 1 if not specified
- Maximum 500 pages (TMDB limitation)
- 20 results per page (TMDB default)

### Error Handling

The server returns JSON error objects for:
- Missing required parameters
- Invalid API key
- TMDB API errors
- Network/timeout issues

Format: `{"error": "Description of error"}`

## Usage Patterns

### Finding TMDB IDs
When users ask for a TMDB ID:
1. Use appropriate search tool (search_movies, search_tv, search_multi)
2. Extract the `id` field from results
3. ID can then be used with detail/similar/credits tools

### Getting Detailed Information
For comprehensive data about a movie/TV show:
1. Get the ID first (via search if needed)
2. Use get_movie_details or get_tv_details
3. Optionally use append_to_response for credits, videos, images

### Discovering Content
For filtered searches:
1. Use discover_movies or discover_tv
2. Build filter JSON with parameters like:
   - `"with_genres": "28,12"` (Action & Adventure)
   - `"primary_release_year": "2023"`
   - `"vote_average.gte": "7.0"`
   - `"sort_by": "popularity.desc"`

### Handling Pagination
When users want more results:
1. Initial request returns page 1
2. Check `total_pages` in response
3. Make additional requests with incremented page numbers
4. Compile results as needed

## Common TMDB Response Fields

### Movie Object
- `id`: Unique identifier
- `title`: Movie title
- `overview`: Plot summary
- `release_date`: Release date
- `vote_average`: Rating (0-10)
- `poster_path`: Poster image path
- `backdrop_path`: Background image path
- `genre_ids`: Array of genre IDs

### TV Show Object
- `id`: Unique identifier
- `name`: Show name
- `overview`: Plot summary
- `first_air_date`: First episode date
- `vote_average`: Rating (0-10)
- `poster_path`: Poster image path
- `backdrop_path`: Background image path
- `genre_ids`: Array of genre IDs

### Image URLs
To construct full image URLs:
- Base URL: `https://image.tmdb.org/t/p/`
- Size: `w500` (common size)
- Path: Value from `poster_path` or `backdrop_path`
- Example: `https://image.tmdb.org/t/p/w500/path.jpg`

## Genre IDs Reference

Common movie genre IDs:
- 28: Action
- 12: Adventure
- 16: Animation
- 35: Comedy
- 80: Crime
- 18: Drama
- 27: Horror
- 878: Science Fiction

TV genre IDs differ slightly - use get_genres tool for complete list.

## Best Practices

1. **Always validate required parameters** before making API calls
2. **Return raw JSON** without modification
3. **Handle pagination** when users need comprehensive results
4. **Use appropriate search** based on user intent (movie vs TV vs multi)
5. **Cache nothing** - always fetch fresh data
6. **Respect rate limits** - 40 requests per 10 seconds

## Limitations

- No write operations (no ratings, watchlists, favorites)
- No user authentication or account features
- TV episode-level details require additional endpoints (not implemented)
- Person details and credits not fully implemented
- No image or video file retrieval (only metadata)

## Tips for Natural Language Processing

When users ask questions like:
- "What's that movie about dreams?" → search_movies with query "dreams"
- "Top sci-fi movies" → discover_movies with genre filter
- "Is The Office worth watching?" → get_tv_details for ratings/overview
- "Movies like Inception" → get_similar_movies with Inception's ID
- "What's trending?" → get_trending with media_type "all"