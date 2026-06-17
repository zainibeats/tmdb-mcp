# Open WebUI Integration

This guide exposes the TMDB MCP server to Open WebUI through `mcpo`, an MCP-to-OpenAPI bridge. Open WebUI remains the end-user chat interface; this project only provides the movie and TV discovery tools.

## Architecture

```text
Browser
  -> Open WebUI
      -> Ollama or OpenAI-compatible model backend
      -> User-added OpenAPI tool server
          -> mcpo
              -> tmdb_server.py
                  -> TMDB API
```

Use Open WebUI user tool servers for opt-in access. User tool server requests are made from the user's browser, so `localhost` can point at the user's own machine. Global tool servers are admin-managed and called from the Open WebUI backend, so only use them when the backend can reach the tool URL.

## Prerequisites

- Open WebUI v0.6 or newer.
- Python 3.11+.
- A TMDB API key configured by the server admin.
- A model backend connected to Open WebUI:
  - Ollama, or
  - LM Studio's OpenAI-compatible server, usually `http://localhost:1234/v1`.
- `uv` for running `mcpo` with `uvx`, or install `mcpo` with `pip`.

## 1. Install the TMDB Server

```bash
git clone https://github.com/zainibeats/tmdb-mcp.git
cd tmdb-mcp
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```

## 2. Start mcpo

Run this from the repository root:

```bash
TMDB_API_KEY="your-tmdb-api-key" \
  uvx mcpo --host 0.0.0.0 --port 8000 -- .venv/bin/python tmdb_server.py
```

If you use `pip` instead of `uvx`:

```bash
. .venv/bin/activate
pip install mcpo
TMDB_API_KEY="your-tmdb-api-key" \
  mcpo --host 0.0.0.0 --port 8000 -- .venv/bin/python tmdb_server.py
```

Confirm the OpenAPI docs are available:

```bash
curl http://localhost:8000/docs
```

## 3. Add the Tool in Open WebUI

1. Open Open WebUI in your browser.
2. Open Settings.
3. Open Tools.
4. Add `http://localhost:8000`.
5. Save.

The tool should appear in the chat input tool picker for that user. Enable it only in chats where movie and TV recommendations should use TMDB.

If `mcpo` is running on a different server, use that server URL instead of `localhost`, and make sure the user's browser can reach it.

## 4. Model Backends

### Ollama

Connect Open WebUI to Ollama using the normal Open WebUI model settings. No TMDB-specific configuration is needed in Ollama.

### LM Studio

Start LM Studio's local server and configure Open WebUI with its OpenAI-compatible base URL:

```text
http://localhost:1234/v1
```

If Open WebUI is running in Docker, `localhost` inside the container is not the host machine. Use a reachable host address, such as `host.docker.internal` where supported, or run LM Studio and Open WebUI on the same network.

## Suggested Prompts

- "Recommend five thoughtful sci-fi movies from the 1990s."
- "Find recent highly rated horror movies and explain why each fits."
- "What are some TV shows similar to The Office?"
- "Show me trending movies this week."
- "Find Christopher Nolan and show his notable credits."
- "Find movies like Arrival, but slower and more emotional."

## Troubleshooting

- `TMDB_API_KEY not set`: restart `mcpo` with the key in the environment.
- Open WebUI cannot connect: confirm the browser can open `http://localhost:8000/docs`.
- Tool calls do not happen: enable the tool in the chat and use a model that follows tool-use instructions reliably.
- Docker networking fails: remember that `localhost` depends on where the request originates.
