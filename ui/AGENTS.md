# AGENTS.md

## Project Overview

TMDB Embed URL Generator is a web application that generates streaming embed URLs using TMDB (The Movie Database) IDs. It's a simple Express.js server serving a static HTML frontend with Tailwind CSS.

**Educational Purpose Only**: This tool is strictly for educational purposes demonstrating web development and API integration concepts.

## Architecture

### Backend (src/server.js)
- **Express.js server** listening on port 8689 (configurable via PORT env var)
- **Single POST endpoint**: `/api/generate-embeds` - generates embed URLs based on media type, TMDB ID, and selected providers
- **Health check endpoint**: `/health` - returns status and MCP endpoint configuration
- **Provider configuration**: Loaded once at startup from `providers.json` and cached in memory
- **URL generation logic**: Template-based string replacement using provider configurations

### Frontend (src/public/index.html)
- **Single-page application** with inline JavaScript and Tailwind CSS (loaded via CDN)
- **Form inputs**: Media type selector, TMDB ID, season/episode (for TV), provider checkboxes
- **Dynamic UI**: TV fields show/hide based on media type selection
- **Results display**: Generated URLs with one-click copy-to-clipboard functionality
- **Error handling**: User-friendly error messages for API failures

### Configuration (src/providers.json)
- **Provider definitions**: Array of streaming providers with name and URL templates
- **URL templates**: Separate templates for movies and TV shows using placeholders:
  - `{id}` - TMDB ID
  - `{season}` - Season number (TV only)
  - `{episode}` - Episode number (TV only)
- **Currently supports 12 providers**: VidAPI, Cinemaos, Rivestream, Videasy, Superembed, Vidfast, SpenEmbed, Autoembed, 111movies, 2embed, Filmku, VidSrc.to

## Development Commands

### Local Development (Node.js)
```bash
cd src
npm install
npm start
```
Server runs on http://localhost:8689

### Docker Development
```bash
# Build and run with Docker Compose
docker compose up -d

# View logs
docker compose logs -f

# Stop
docker compose down

# Rebuild image
docker compose up -d --build
```

### Testing the Application
1. Access http://localhost:8689
2. Select Movie or TV Show
3. Enter a TMDB ID (e.g., 550 for Fight Club)
4. For TV shows, enter season and episode numbers
5. Select providers and click "Generate Embed URLs"

## Key Implementation Details

### Adding New Providers
To add a new streaming provider, edit `providers.json`:
```json
{
  "name": "ProviderName",
  "movie": "https://example.com/movie/{id}",
  "tv": "https://example.com/tv/{id}/{season}/{episode}"
}
```
The server loads this file at startup, so restart is required after changes.

### Environment Variables
- `PORT` - Server port (default: 8689)
- `MCP_ENDPOINT` - MCP endpoint URL (default: http://localhost:5000, currently unused in URL generation)

### Request/Response Format
POST to `/api/generate-embeds`:
```json
{
  "mediaType": "movie|tv",
  "tmdbId": "550",
  "season": "1",      // required for TV
  "episode": "1",     // required for TV
  "providers": ["VidAPI", "Cinemaos"]  // optional, defaults to all
}
```

Response:
```json
[
  {
    "provider": "VidAPI",
    "url": "https://vidapi.xyz/embed/movie/550"
  }
]
```
