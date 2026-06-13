import pytest

from tmdb_formatting import (
    format_candidate_list,
    format_media_details,
    normalize_media_type,
    normalize_page,
    require_tmdb_id,
)


def test_format_candidate_list_includes_choice_fields():
    payload = {
        "page": 1,
        "total_results": 1,
        "results": [
            {
                "id": 550,
                "title": "Fight Club",
                "release_date": "1999-10-15",
                "vote_average": 8.4,
                "vote_count": 29000,
                "overview": "A ticking-time-bomb insomniac meets a soap maker.",
            }
        ],
    }

    formatted = format_candidate_list(
        payload,
        heading="Matches for fight club",
        fallback_media_type="movie",
    )

    assert "Matches for fight club (page 1, 1 total)" in formatted
    assert "Fight Club (1999)" in formatted
    assert "TMDB ID: 550 | Media type: movie | Rating: 8.4/10 from 29000 votes" in formatted
    assert "A ticking-time-bomb insomniac" in formatted


def test_format_candidate_list_filters_people_from_multi_search():
    payload = {
        "results": [
            {"id": 1, "name": "A Person", "media_type": "person"},
            {"id": 2, "name": "A Show", "media_type": "tv", "first_air_date": "2020-01-01"},
        ],
    }

    formatted = format_candidate_list(payload, heading="Matches")

    assert "A Person" not in formatted
    assert "A Show (2020)" in formatted


def test_format_media_details_handles_tv_shape():
    payload = {
        "id": 1396,
        "name": "Breaking Bad",
        "first_air_date": "2008-01-20",
        "number_of_seasons": 5,
        "genres": [{"id": 18, "name": "Drama"}],
        "vote_average": 8.9,
        "vote_count": 15000,
        "overview": "A chemistry teacher turns to crime.",
    }

    formatted = format_media_details(payload, media_type="tv")

    assert "Breaking Bad" in formatted
    assert "TMDB ID: 1396 | Media type: tv" in formatted
    assert "Seasons: 5" in formatted
    assert "Genres: Drama" in formatted


@pytest.mark.parametrize("value", ["", "person", "both"])
def test_normalize_media_type_rejects_invalid_values(value):
    with pytest.raises(ValueError):
        normalize_media_type(value)


@pytest.mark.parametrize("value", ["0", "-1", "501", "abc"])
def test_page_validation_rejects_bad_values(value):
    with pytest.raises(ValueError):
        normalize_page(value)


@pytest.mark.parametrize("value", ["0", "-1", "abc"])
def test_tmdb_id_validation_rejects_bad_values(value):
    with pytest.raises(ValueError):
        require_tmdb_id(value)
