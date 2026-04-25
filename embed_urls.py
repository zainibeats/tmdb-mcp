"""Provider URL generation for TMDB-based movie and TV embeds."""
import json
import os
from pathlib import Path
from typing import Any


DEFAULT_UI_BASE_URL = "http://localhost:8689"


def _candidate_provider_paths() -> list[Path]:
    configured_path = os.environ.get("TMDB_PROVIDERS_PATH", "").strip()
    paths = []
    if configured_path:
        paths.append(Path(configured_path))

    here = Path(__file__).resolve().parent
    paths.extend([
        here / "providers.json",
        here / "ui" / "src" / "providers.json",
    ])
    return paths


def load_providers() -> list[dict[str, Any]]:
    """Load provider templates from JSON config."""
    for provider_path in _candidate_provider_paths():
        if provider_path.exists():
            with provider_path.open("r", encoding="utf-8") as provider_file:
                config = json.load(provider_file)
            providers = config.get("providers", [])
            if isinstance(providers, list):
                return providers
            raise ValueError(f"Invalid providers config in {provider_path}")

    searched_paths = ", ".join(str(path) for path in _candidate_provider_paths())
    raise FileNotFoundError(f"No providers.json found. Searched: {searched_paths}")


def _normalize_provider_filter(provider_names: list[str] | None) -> set[str]:
    return {
        provider_name.strip().casefold()
        for provider_name in provider_names or []
        if provider_name.strip()
    }


def generate_embed_urls(
    media_type: str,
    tmdb_id: str,
    season: str = "1",
    episode: str = "1",
    provider_names: list[str] | None = None,
    ui_base_url: str = DEFAULT_UI_BASE_URL,
) -> dict[str, Any]:
    """Generate provider URLs and a local UI prefill URL for a TMDB item."""
    normalized_media_type = media_type.strip().lower()
    normalized_tmdb_id = tmdb_id.strip()
    normalized_season = str(season).strip() or "1"
    normalized_episode = str(episode).strip() or "1"

    if normalized_media_type not in {"movie", "tv"}:
        raise ValueError('media_type must be "movie" or "tv"')
    if not normalized_tmdb_id:
        raise ValueError("tmdb_id is required")

    requested_providers = _normalize_provider_filter(provider_names)
    results = []

    for provider in load_providers():
        provider_name = str(provider.get("name", "")).strip()
        if not provider_name:
            continue
        if requested_providers and provider_name.casefold() not in requested_providers:
            continue

        template = provider.get(normalized_media_type)
        if not template:
            continue

        url = str(template).replace("{id}", normalized_tmdb_id)
        if normalized_media_type == "tv":
            url = url.replace("{season}", normalized_season)
            url = url.replace("{episode}", normalized_episode)

        results.append({
            "provider": provider_name,
            "url": url,
        })

    ui_url = build_ui_prefill_url(
        media_type=normalized_media_type,
        tmdb_id=normalized_tmdb_id,
        season=normalized_season,
        episode=normalized_episode,
        ui_base_url=ui_base_url,
    )

    return {
        "media_type": normalized_media_type,
        "tmdb_id": normalized_tmdb_id,
        "season": normalized_season if normalized_media_type == "tv" else None,
        "episode": normalized_episode if normalized_media_type == "tv" else None,
        "ui_url": ui_url,
        "results": results,
    }


def build_ui_prefill_url(
    media_type: str,
    tmdb_id: str,
    season: str = "1",
    episode: str = "1",
    ui_base_url: str = DEFAULT_UI_BASE_URL,
) -> str:
    """Build a local UI URL that pre-fills the embed form."""
    base_url = ui_base_url.rstrip("/")
    query = f"mediaType={media_type}&tmdbId={tmdb_id}"
    if media_type == "tv":
        query = f"{query}&season={season}&episode={episode}"
    return f"{base_url}/?{query}"
