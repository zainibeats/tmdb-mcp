# Linux Installation

This path runs the TMDB MCP server directly over stdio. It works without Docker.

## Prerequisites

- Python 3.11+
- TMDB API key from `https://www.themoviedb.org/settings/api`
- LM Studio 0.4.0+ as the recommended Linux MCP client

For Open WebUI with Ollama or LM Studio, use the [Open WebUI guide](./OPENWEBUI.md).

## 1. Install the Python Server

```bash
git clone https://github.com/zainibeats/tmdb-mcp.git
cd tmdb-mcp
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
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
    }
  }
}
```

Restart LM Studio after changing `mcp.json`.

## Usage Notes

- Use the `tmdb` server to search, discover, compare, and inspect TMDB movie and TV results.
- The server needs `TMDB_API_KEY`.
- The TMDB API key should be configured by the server admin, not entered by end users.

## Troubleshooting

- `TMDB_API_KEY not set`: add the key to the `env` block for the `tmdb` server.
- Client cannot start the server: confirm the `command` and `args` paths are absolute and executable.
