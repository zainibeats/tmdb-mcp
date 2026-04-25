#!/usr/bin/env python3
"""MCP server for generating provider URLs from TMDB IDs."""
import json
import logging
import os
import sys
from pathlib import Path

from mcp.server.fastmcp import FastMCP

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from embed_urls import generate_embed_urls, load_providers


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger("embed-resolver")

mcp = FastMCP("tmdb-embed-resolver")

UI_BASE_URL = os.environ.get("TMDB_EMBED_UI_BASE_URL", "http://localhost:8689")


@mcp.tool()
async def list_embed_providers() -> str:
    """List configured provider names supported by the resolver."""
    try:
        provider_names = [
            str(provider.get("name", "")).strip()
            for provider in load_providers()
            if str(provider.get("name", "")).strip()
        ]
        return json.dumps({"providers": provider_names}, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})


@mcp.tool()
async def generate_embed_urls_for_tmdb(
    media_type: str = "movie",
    tmdb_id: str = "",
    season: str = "1",
    episode: str = "1",
    providers_json: str = "[]",
) -> str:
    """Generate provider URLs and a local UI prefill URL for a TMDB movie or TV show ID."""
    logger.info("Generating embed URLs for %s ID: %s", media_type, tmdb_id)

    try:
        provider_names = json.loads(providers_json) if providers_json.strip() else []
        if not isinstance(provider_names, list):
            return '{"error": "providers_json must be a JSON array of provider names"}'
    except json.JSONDecodeError:
        return '{"error": "Invalid providers_json"}'

    try:
        result = generate_embed_urls(
            media_type=media_type,
            tmdb_id=tmdb_id,
            season=season,
            episode=episode,
            provider_names=[str(provider) for provider in provider_names],
            ui_base_url=UI_BASE_URL,
        )
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})


if __name__ == "__main__":
    logger.info("Starting TMDB embed resolver MCP server...")
    try:
        mcp.run(transport="stdio")
    except Exception as e:
        logger.error("Server error: %s", e, exc_info=True)
        sys.exit(1)
