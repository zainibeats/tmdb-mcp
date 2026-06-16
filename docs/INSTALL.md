# Installation

This guide sets up the TMDB MCP server through Docker MCP Gateway. On Linux, the simpler recommended path is direct stdio; see [Linux installation](./LINUX.md). For Open WebUI, see [Open WebUI integration](./OPENWEBUI.md).

## Architecture

Expose the TMDB MCP server through one Docker MCP Gateway profile.

```text
LM Studio / Claude Desktop
          |
 docker mcp gateway run --profile tmdb-media
          |
       TMDB MCP
          |
       TMDB API
```

The recommended runtime image is:

- `skimming124/tmdb-mcp:latest`

## Prerequisites

- Docker Desktop with MCP Toolkit enabled
- Docker MCP CLI plugin available as `docker mcp`
- TMDB API key from `https://www.themoviedb.org/settings/api`
- LM Studio 0.4.0+ or Claude Desktop

Check Docker MCP:

```bash
docker mcp version
```

If that command is missing, update Docker Desktop and enable MCP Toolkit before continuing.

## 1. Store the TMDB API Key

```bash
docker mcp secret set TMDB_API_KEY="your-tmdb-api-key"
docker mcp secret list
```

The server admin configures this once. End users should not need their own TMDB API key.

## 2. Create a Docker MCP Profile

Create a focused profile for this project:

```bash
docker mcp profile create --name tmdb-media
```

If `docker mcp profile` is unavailable, enable the profiles feature with `docker mcp feature enable profiles`, then retry.

Add the local server definition from this repository:

```bash
docker mcp profile server add tmdb-media \
  --server file://$(pwd)/docker-mcp/tmdb.yaml
```

Confirm the profile:

```bash
docker mcp profile server ls --filter profile=tmdb-media
docker mcp profile config tmdb-media --get-all
```

## 3. Test the Gateway

List available tools:

```bash
docker mcp tools list --gateway-arg="--profile=tmdb-media"
```

Call a simple TMDB discovery tool:

```bash
docker mcp tools call find_media \
  --gateway-arg="--profile=tmdb-media" \
  query=inception \
  media_type=movie \
  page=1
```

## 4. Connect LM Studio

LM Studio uses `mcp.json` for frequently used local MCP servers. Add Docker MCP Gateway as the server command:

```json
{
  "mcpServers": {
    "tmdb-media": {
      "command": "docker",
      "args": ["mcp", "gateway", "run", "--profile", "tmdb-media"]
    }
  }
}
```

In LM Studio Server Settings, enable **Allow calling servers from mcp.json**.

When using the LM Studio API, include the plugin ID for the configured MCP server in the request integrations. LM Studio's exact plugin ID display can vary by version, so confirm it in the LM Studio MCP configuration screen after saving `mcp.json`.

## 5. Connect Claude Desktop

Add the same gateway command to Claude Desktop:

```json
{
  "mcpServers": {
    "tmdb-media": {
      "command": "docker",
      "args": ["mcp", "gateway", "run", "--profile", "tmdb-media"]
    }
  }
}
```

Claude Desktop config paths:

- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

Restart Claude Desktop after editing the file.

## Recommended Prompts

Use prompts that let the model search, discover, and compare TMDB results:

- "Show me comedy movies with a rating above 6 from before 2003."
- "Find highly rated sci-fi movies from the 1990s and give me five options."
- "Search for TV shows similar to The Office."
- "I liked Arrival. Find slower, emotional science fiction movies with strong reviews."

For advanced discovery, the model should use `get_genres` first if it does not know the genre ID, then call `discover_media`.

Example TMDB discover parameters for "comedy movies rated above 6 before 2003":

```json
{
  "media_type": "movie",
  "with_genres": "35",
  "vote_average_gte": "6",
  "sort_by": "vote_average.desc"
}
```

For less common TMDB discover filters, pass them through `filters_json` as a JSON object.

## Local Development Builds

Use these commands only when testing changes locally:

```bash
docker build -t tmdb-mcp .
```

Then edit `docker-mcp/tmdb.yaml` to point at the local image name.

## Troubleshooting

- `docker: unknown command: docker mcp`: update Docker Desktop and enable MCP Toolkit.
- Tools are missing in the client: confirm `docker mcp gateway run --profile tmdb-media` starts without errors.
- TMDB tools return `{"error": "TMDB_API_KEY not set"}`: re-run `docker mcp secret set TMDB_API_KEY=...`.
- Local models choose the wrong tool: tell the model to use TMDB discovery tools for search, recommendations, details, and similar-title requests.
