# AGENTS.md

## Rules for Agent

- Always keep your responses concise to the user
- When you are ready, you may agentically work on your own (i.e. spin up sub-agents, write/use skills, search online, etc without human interaction).
- Use the latest stable versions of packages
- Never hard‑code sensitive info
- Ask clarifying questions if the user’s intent is ambiguous
- Less is always more. Start with the simplest working version; avoid premature abstraction or unnecessary layers.
- Favor standard patterns over clever one‑offs. Readability and maintainability win every time.
- Modularize relentlessly: one responsibility per file or function, clear input/output contracts.
- Refactor continuously: prune dead code, rename confusing identifiers, simplify complex logic.
- Document succinctly: docstrings for public APIs, README to outline high‑level project conventions.
- If changes are agreed upon, git add and commit your changes when necessary

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
