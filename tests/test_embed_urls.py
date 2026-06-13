import json

import pytest

from embed_urls import build_ui_prefill_url, generate_embed_urls


def test_build_ui_prefill_url_for_movie():
    assert (
        build_ui_prefill_url("movie", "550", ui_base_url="http://localhost:8689/")
        == "http://localhost:8689/?mediaType=movie&tmdbId=550"
    )


def test_generate_embed_urls_uses_root_providers(monkeypatch, tmp_path):
    providers_path = tmp_path / "providers.json"
    providers_path.write_text(
        json.dumps({
            "providers": [
                {
                    "name": "Example",
                    "movie": "https://example.test/movie/{id}",
                    "tv": "https://example.test/tv/{id}/{season}/{episode}",
                }
            ]
        }),
        encoding="utf-8",
    )
    monkeypatch.setenv("TMDB_PROVIDERS_PATH", str(providers_path))

    result = generate_embed_urls(
        media_type="tv",
        tmdb_id="1396",
        season="2",
        episode="3",
        ui_base_url="http://localhost:8689",
    )

    assert result["ui_url"] == "http://localhost:8689/?mediaType=tv&tmdbId=1396&season=2&episode=3"
    assert result["results"] == [
        {"provider": "Example", "url": "https://example.test/tv/1396/2/3"}
    ]


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({"media_type": "person", "tmdb_id": "550"}, 'media_type must be "movie" or "tv"'),
        ({"media_type": "movie", "tmdb_id": ""}, "tmdb_id is required"),
        ({"media_type": "movie", "tmdb_id": "abc"}, "tmdb_id must be a positive integer"),
        ({"media_type": "tv", "tmdb_id": "1396", "season": "0"}, "season must be a positive integer"),
        ({"media_type": "tv", "tmdb_id": "1396", "episode": "-1"}, "episode must be a positive integer"),
    ],
)
def test_generate_embed_urls_validates_ids(kwargs, message):
    with pytest.raises(ValueError, match=message):
        generate_embed_urls(**kwargs)
