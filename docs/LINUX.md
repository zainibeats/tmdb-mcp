# Linux Installation

This path runs the MCP servers directly over stdio. It works with normal Linux Docker Engine, Podman, or no container runtime at all.

## Prerequisites

- Python 3.11+
- Node.js 18+ if running the optional UI without Docker
- Optional: Docker Engine if running the UI container
- TMDB API key from `https://www.themoviedb.org/settings/api`
- LM Studio 0.4.0+ as the recommended Linux MCP client

Open WebUI with Ollama is a good local chat stack, but this guide uses LM Studio because it can launch stdio MCP servers directly from `mcp.json`.

## 1. Install the Python Servers

```bash
git clone https://github.com/zainibeats/tmdb-mcp.git
cd tmdb-mcp
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
pip install -r embed-resolver-mcp/requirements.txt
```

Test the discovery server:

```bash
TMDB_API_KEY="your-tmdb-api-key" \
  .venv/bin/python tmdb_server.py
```

Press `Ctrl+C` after it starts. MCP clients will launch this process themselves.

## 2. Configure LM Studio

In LM Studio, open the **Program** tab, choose **Install > Edit mcp.json**, and add these servers. Use absolute paths.

```json
{
  "mcpServers": {
    "tmdb": {
      "command": "/absolute/path/to/tmdb-mcp/.venv/bin/python",
      "args": ["/absolute/path/to/tmdb-mcp/tmdb_server.py"],
      "env": {
        "TMDB_API_KEY": "your-tmdb-api-key"
      }
    },
    "tmdb-embed-resolver": {
      "command": "/absolute/path/to/tmdb-mcp/.venv/bin/python",
      "args": ["/absolute/path/to/tmdb-mcp/embed-resolver-mcp/server.py"],
      "env": {
        "TMDB_EMBED_UI_BASE_URL": "http://localhost:8689"
      }
    }
  }
}
```

Restart LM Studio after changing `mcp.json`.

## 3. Start the Optional UI

The resolver works without the UI, but returned `ui_url` links are only clickable if something is listening on `http://localhost:8689`.

With Docker Engine:

```bash
docker run -d \
  --name tmdb-embed-ui \
  --restart unless-stopped \
  -p 8689:8689 \
  skimming124/tmdb-embed-ui:latest
```

Without Docker:

```bash
cd ui/src
npm install
npm start
```

Verify the UI:

```bash
curl http://localhost:8689/health
```

## Usage Notes

- Use the `tmdb` server first to search, discover, and confirm a TMDB ID.
- Use `tmdb-embed-resolver` only after choosing a specific movie or TV show.
- The discovery server needs `TMDB_API_KEY`; the resolver does not.
- Set `TMDB_PROVIDERS_PATH` for the resolver if you want to use a custom provider file.

## Troubleshooting

- `TMDB_API_KEY not set`: add the key to the `env` block for the `tmdb` server.
- Client cannot start the server: confirm the `command` and `args` paths are absolute and executable.
- UI links do not open: start the UI and confirm `curl http://localhost:8689/health` succeeds.
