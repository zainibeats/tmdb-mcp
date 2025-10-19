# INSTALLATION INSTRUCTIONS

## Step 1: Clone Repository

```bash
# Create project directory
git clone https://github.com/zainibeats/tmdb-mcp
cd tmdb-mcp

# Save all 5 files in this directory:
# - Dockerfile
# - requirements.txt
# - tmdb_server.py
# - readme.md
# - CLAUDE.md
```

## Step 2: Build Docker Image

```bash
docker build -t tmdb-mcp .
```

## Step 3: Set Up Secrets

```bash
# Get your free API key from https://www.themoviedb.org/settings/api
# Then set it as a Docker secret
docker mcp secret set TMDB_API_KEY="your-tmdb-api-key-here"

# Verify the secret was saved
docker mcp secret list
```

## Step 4: Create Custom Catalog

```bash
# Create catalogs directory if it doesn't exist
mkdir -p ~/.docker/mcp/catalogs

# Create or edit custom.yaml
nano ~/.docker/mcp/catalogs/custom.yaml
```

Add this entry to custom.yaml:

```yaml
version: 2
name: custom
displayName: Custom MCP Servers
registry:
  tmdb:
    description: "Read-only access to The Movie Database API for movie and TV information"
    title: "TMDB"
    type: server
    dateAdded: "2025-01-09T00:00:00Z"
    image: skimming124/tmdb-mcp:latest
    ref: ""
    readme: ""
    toolsUrl: ""
    source: ""
    upstream: ""
    icon: ""
    tools:
      - name: search_movies
      - name: search_tv
      - name: search_multi
      - name: get_movie_details
      - name: get_tv_details
      - name: get_top_rated_movies
      - name: get_top_rated_tv
      - name: get_popular_movies
      - name: get_popular_tv
      - name: get_trending
      - name: get_similar_movies
      - name: get_similar_tv
      - name: get_genres
      - name: get_movie_credits
      - name: get_movie_reviews
      - name: discover_movies
      - name: discover_tv
    secrets:
      - name: TMDB_API_KEY
        env: TMDB_API_KEY
        example: "abc123def456ghi789"
    metadata:
      category: integration
      tags:
        - movies
        - tv
        - entertainment
        - media
        - tmdb
      license: MIT
      owner: local
```

## Step 5: Update Registry

```bash
# Edit registry file
nano ~/.docker/mcp/registry.yaml
```

Add this entry under the existing `registry:` key:

```yaml
registry:
  # ... existing servers ...
  tmdb:
    ref: ""
```

**IMPORTANT**: The entry must be under the `registry:` key, not at the root level.

## Step 6: Configure Claude Desktop

Find your Claude Desktop config file:
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

Edit the file and add your custom catalog to the args array:

```json
{
  "mcpServers": {
    "mcp-toolkit-gateway": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "-v", "/var/run/docker.sock:/var/run/docker.sock",
        "-v", "[YOUR_HOME]/.docker/mcp:/mcp",
        "docker/mcp-gateway",
        "--catalog=/mcp/catalogs/docker-mcp.yaml",
        "--catalog=/mcp/catalogs/custom.yaml",
        "--config=/mcp/config.yaml",
        "--registry=/mcp/registry.yaml",
        "--tools-config=/mcp/tools.yaml",
        "--transport=stdio"
      ]
    }
  }
}
```

Replace `[YOUR_HOME]` with:
- **macOS**: `/Users/your_username`
- **Windows**: `C:\\Users\\your_username` (use double backslashes)
- **Linux**: `/home/your_username`

## Step 7: Restart Claude Desktop

1. Quit Claude Desktop completely
2. Start Claude Desktop again
3. Your TMDB tools should now appear!

## Step 8: Test Your Server

```bash
# Verify it appears in the list
docker mcp server list

# If you don't see your server, check logs:
docker logs tmdb-mcp

# Test a tool in Claude Desktop by asking:
# "Search for movies about space"
# "What's the TMDB ID for Breaking Bad?"
# "Show me trending movies this week"
```

## Troubleshooting Tips

If the tools don't appear:
1. Check that the Docker image built successfully: `docker images | grep tmdb`
2. Verify your API key is set: `docker mcp secret list`
3. Ensure the catalog file has correct YAML syntax
4. Check Claude Desktop logs for any errors
5. Make sure you restarted Claude Desktop after configuration changes
6. Verify all 5 files were saved correctly, especially the `requirements.txt` file

Your TMDB MCP server is now ready to use! You can ask Claude to search for movies, get details about shows, find similar content, and much more using the TMDB database.
