# AGENTS.md

## Rules for Agent

- Keep responses concise.
- Use the latest stable versions of packages.
- Never hard-code sensitive info.
- Ask clarifying questions if the user's intent is ambiguous.
- Start with the simplest working version; avoid premature abstraction.
- Favor standard patterns over clever one-offs.
- Document succinctly.

## Project Overview

This project provides a TMDB-only MCP tool service for movie and TV discovery. The recommended end-user interface is an existing chat UI, especially Open WebUI through `mcpo`, not a standalone app in this repository.

## Current Product Direction

- Primary scope: TMDB search, discovery, details, similar titles, trending, popular, top-rated, genres, and useful credits.
- Preferred UI: Open WebUI with a user-added OpenAPI tool server exposed by `mcpo`.
- Model backends: Ollama and LM Studio are both supported through Open WebUI. LM Studio should be treated as an OpenAI-compatible backend, commonly at `http://localhost:1234/v1`.
- Secret ownership: the server admin configures `TMDB_API_KEY`; end users should not need their own key.
- Provider/embed URL generation is not part of the recommended workflow.

## Usage Pattern

1. The user asks for recommendations, trends, details, or similar movies/TV shows.
2. The assistant calls the focused TMDB tools.
3. The assistant returns a short list or answer with enough detail to choose confidently.
4. Follow-up questions should use TMDB IDs from prior results when possible.

## Documentation Expectations

- Keep README and install docs focused on the TMDB MCP server.
- Put Open WebUI setup in `docs/OPENWEBUI.md`.
- Keep Docker MCP Gateway setup in `docs/INSTALL.md`.
- Keep direct stdio setup in `docs/LINUX.md`.
