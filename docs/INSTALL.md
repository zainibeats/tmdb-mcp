# Installation

This guide sets up the TMDB MCP toolchain through Docker MCP Gateway. On Linux, the simpler recommended path is direct stdio; see [Linux installation](./LINUX.md).

## Architecture

Run the UI as a normal Docker container, then expose both MCP servers through one Docker MCP Gateway profile.

```text
LM Studio / Claude Desktop
          |
 docker mcp gateway run --profile tmdb-media
          |
    +-----+----------------+
    |                      |
 TMDB MCP           TMDB Embed Resolver MCP
    |                      |
 TMDB API           provider templates + UI links
                           |
                 http://localhost:8689
```

The recommended runtime images are:

- `skimming124/tmdb-mcp:latest`
- `skimming124/tmdb-embed-resolver:latest`
- `skimming124/tmdb-embed-ui:latest`

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

## 1. Start the UI

The UI is required for clickable resolver links such as `http://localhost:8689/?mediaType=movie&tmdbId=550`.

```bash
docker run -d \
  --name tmdb-embed-ui \
  --restart unless-stopped \
  -p 8689:8689 \
  skimming124/tmdb-embed-ui:latest
```

Verify it:

```bash
curl http://localhost:8689/health
```

## 2. Store the TMDB API Key

```bash
docker mcp secret set TMDB_API_KEY="your-tmdb-api-key"
docker mcp secret list
```

Only the `tmdb` discovery server needs this secret. The embed resolver does not call TMDB.

## 3. Create a Docker MCP Profile

Create a focused profile for this project:

```bash
docker mcp profile create --name tmdb-media
```

If `docker mcp profile` is unavailable, enable the profiles feature with `docker mcp feature enable profiles`, then retry.

Add the two local server definitions from this repository:

```bash
docker mcp profile server add tmdb-media \
  --server file://$(pwd)/docker-mcp/tmdb.yaml \
  --server file://$(pwd)/docker-mcp/tmdb-embed-resolver.yaml
```

Confirm the profile:

```bash
docker mcp profile server ls --filter profile=tmdb-media
docker mcp profile config tmdb-media --get-all
```

## 4. Test the Gateway

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

Call the resolver:

```bash
docker mcp tools call generate_embed_urls_for_tmdb \
  --gateway-arg="--profile=tmdb-media" \
  media_type=movie \
  tmdb_id=550
```

The resolver response should include a `ui_url`. Opening that link should load the local UI and generate provider links.

## 5. Connect LM Studio

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

## 6. Connect Claude Desktop

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

Use prompts that let the model discover first and resolve only after user confirmation:

- "Show me comedy movies with a rating above 6 from before 2003."
- "Find highly rated sci-fi movies from the 1990s and give me five options."
- "Search for TV shows similar to The Office."
- "I choose movie TMDB ID 550. Give me the local UI link."

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

## Provider Configuration

The project ships with provider templates in `providers.json`, and the UI image ships with `ui/src/providers.json`. Providers change often, so treat these as configurable runtime data.

For the embed resolver, mount a replacement provider file and set `TMDB_PROVIDERS_PATH` in the server definition or catalog entry.

For the UI, rebuild the UI image with an updated `ui/src/providers.json`, or run a custom image that contains your provider list.

## Local Development Builds

Use these commands only when testing changes locally:

```bash
docker build -t tmdb-mcp .
docker build -f embed-resolver-mcp/Dockerfile -t tmdb-embed-resolver .
docker build -f ui/Dockerfile -t tmdb-embed-ui ./ui
```

Then edit `docker-mcp/tmdb.yaml` and `docker-mcp/tmdb-embed-resolver.yaml` to point at the local image names.

## Troubleshooting

- `docker: unknown command: docker mcp`: update Docker Desktop and enable MCP Toolkit.
- Tools are missing in the client: confirm `docker mcp gateway run --profile tmdb-media` starts without errors.
- TMDB tools return `{"error": "TMDB_API_KEY not set"}`: re-run `docker mcp secret set TMDB_API_KEY=...`.
- UI links do not open: confirm `docker ps` shows `tmdb-embed-ui` and `curl http://localhost:8689/health` succeeds.
- Local models choose the wrong tool: tell the model to use TMDB discovery tools first, then call `generate_embed_urls_for_tmdb` only after the user chooses a result.
