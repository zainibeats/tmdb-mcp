"""Formatting and validation helpers for assistant-friendly TMDB responses."""
from __future__ import annotations

import json
from typing import Any


MEDIA_TYPES = {"movie", "tv"}


def normalize_media_type(value: str, *, allow_all: bool = False) -> str:
    """Return a supported TMDB media type."""
    normalized = value.strip().lower()
    valid_types = MEDIA_TYPES | ({"all"} if allow_all else set())
    if normalized not in valid_types:
        expected = ", ".join(sorted(valid_types))
        raise ValueError(f"media_type must be one of: {expected}")
    return normalized


def normalize_time_window(value: str) -> str:
    """Return a supported TMDB trending time window."""
    normalized = value.strip().lower()
    if normalized not in {"day", "week"}:
        raise ValueError("time_window must be day or week")
    return normalized


def normalize_page(value: str) -> str:
    """Return a TMDB page number string."""
    try:
        page = int(str(value).strip() or "1")
    except ValueError as exc:
        raise ValueError("page must be a positive integer") from exc
    if page < 1 or page > 500:
        raise ValueError("page must be an integer from 1 to 500")
    return str(page)


def require_tmdb_id(value: str, label: str = "tmdb_id") -> str:
    """Return a non-empty numeric TMDB ID string."""
    tmdb_id = str(value).strip()
    if not tmdb_id:
        raise ValueError(f"{label} is required")
    if not tmdb_id.isdigit() or int(tmdb_id) < 1:
        raise ValueError(f"{label} must be a positive integer")
    return tmdb_id


def parse_json_object(value: str, label: str) -> dict[str, Any]:
    """Parse a JSON object from a string."""
    if not str(value).strip():
        return {}
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError as exc:
        raise ValueError(f"{label} must be valid JSON") from exc
    if not isinstance(parsed, dict):
        raise ValueError(f"{label} must be a JSON object")
    return parsed


def error_text(message: str) -> str:
    """Format an error for MCP clients."""
    return f"Error: {message}"


def tmdb_error_text(payload: dict[str, Any]) -> str | None:
    """Return a readable error if the TMDB payload represents one."""
    if "error" not in payload:
        return None
    return error_text(str(payload["error"]))


def format_candidate_list(
    payload: dict[str, Any],
    *,
    heading: str,
    fallback_media_type: str | None = None,
    limit: int = 8,
) -> str:
    """Format TMDB list/search results as compact candidate choices."""
    if error := tmdb_error_text(payload):
        return error

    results = [
        item
        for item in payload.get("results", [])
        if _item_media_type(item, fallback_media_type) in MEDIA_TYPES
    ][:limit]

    page = payload.get("page")
    total_results = payload.get("total_results")
    parts = [heading]
    if page is not None and total_results is not None:
        parts[0] = f"{heading} (page {page}, {total_results} total)"

    if not results:
        parts.append("No movie or TV results found.")
        return "\n".join(parts)

    for index, item in enumerate(results, start=1):
        parts.append(_format_candidate(index, item, fallback_media_type))
    return "\n\n".join(parts)


def format_media_details(
    payload: dict[str, Any],
    *,
    media_type: str,
) -> str:
    """Format TMDB movie or TV details for assistant use."""
    if error := tmdb_error_text(payload):
        return error

    title = _title(payload)
    date = payload.get("release_date") or payload.get("first_air_date") or "unknown date"
    runtime = _runtime_or_seasons(payload, media_type)
    genres = ", ".join(
        str(genre.get("name", "")).strip()
        for genre in payload.get("genres", [])
        if str(genre.get("name", "")).strip()
    ) or "unknown genres"
    rating = _rating(payload)
    overview = _overview(payload)

    return "\n".join([
        f"{title}",
        f"TMDB ID: {payload.get('id', 'unknown')} | Media type: {media_type}",
        f"Date: {date} | {runtime}",
        f"Genres: {genres}",
        f"Rating: {rating}",
        f"Overview: {overview}",
    ])


def format_genres(payload: dict[str, Any], *, media_type: str) -> str:
    """Format TMDB genres as ID/name pairs."""
    if error := tmdb_error_text(payload):
        return error

    genres = payload.get("genres", [])
    if not genres:
        return f"No {media_type} genres found."
    lines = [f"{media_type.title()} genres:"]
    lines.extend(
        f"- {genre.get('name', 'Unknown')} ({genre.get('id', 'unknown')})"
        for genre in genres
    )
    return "\n".join(lines)


def format_movie_credits(payload: dict[str, Any], *, cast_limit: int = 10, crew_limit: int = 8) -> str:
    """Format core movie cast and crew."""
    if error := tmdb_error_text(payload):
        return error

    cast = [
        f"{person.get('name', 'Unknown')} as {person.get('character', 'Unknown')}"
        for person in payload.get("cast", [])[:cast_limit]
    ]
    crew = [
        f"{person.get('name', 'Unknown')} - {person.get('job', 'Unknown')}"
        for person in payload.get("crew", [])
        if person.get("job") in {"Director", "Writer", "Screenplay", "Producer"}
    ][:crew_limit]

    lines = [f"Movie credits for TMDB ID {payload.get('id', 'unknown')}"]
    lines.append("Cast: " + ("; ".join(cast) if cast else "unknown"))
    lines.append("Key crew: " + ("; ".join(crew) if crew else "unknown"))
    return "\n".join(lines)


def _format_candidate(index: int, item: dict[str, Any], fallback_media_type: str | None) -> str:
    media_type = _item_media_type(item, fallback_media_type)
    year = _year(item)
    rating = _rating(item)
    overview = _overview(item)
    return "\n".join([
        f"{index}. {_title(item)} ({year})",
        f"TMDB ID: {item.get('id', 'unknown')} | Media type: {media_type} | Rating: {rating}",
        f"Overview: {overview}",
    ])


def _item_media_type(item: dict[str, Any], fallback_media_type: str | None) -> str:
    return str(item.get("media_type") or fallback_media_type or "").strip().lower()


def _title(item: dict[str, Any]) -> str:
    return str(item.get("title") or item.get("name") or "Untitled").strip()


def _year(item: dict[str, Any]) -> str:
    date = str(item.get("release_date") or item.get("first_air_date") or "").strip()
    return date[:4] if len(date) >= 4 else "unknown year"


def _rating(item: dict[str, Any]) -> str:
    vote_average = item.get("vote_average")
    vote_count = item.get("vote_count")
    if vote_average in {None, ""}:
        return "unrated"
    try:
        rating = f"{float(vote_average):.1f}/10"
    except (TypeError, ValueError):
        rating = f"{vote_average}/10"
    if vote_count not in {None, ""}:
        rating = f"{rating} from {vote_count} votes"
    return rating


def _overview(item: dict[str, Any], limit: int = 260) -> str:
    overview = " ".join(str(item.get("overview") or "No overview available.").split())
    if len(overview) <= limit:
        return overview
    return f"{overview[: limit - 3].rstrip()}..."


def _runtime_or_seasons(item: dict[str, Any], media_type: str) -> str:
    if media_type == "movie":
        runtime = item.get("runtime")
        return f"Runtime: {runtime} minutes" if runtime else "Runtime: unknown"
    seasons = item.get("number_of_seasons")
    return f"Seasons: {seasons}" if seasons else "Seasons: unknown"
