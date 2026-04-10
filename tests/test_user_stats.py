"""
Tests for GET /api/user/stats endpoint.

Verifies that authenticated users receive accurate personal upload statistics
including totals, sentiment breakdown, voice note count, and daily trend.
"""

from datetime import datetime, timedelta, timezone

import bcrypt
import pytest
from bson import ObjectId

#---- Helpers ----

USER_ID = str(ObjectId())
OTHER_USER_ID = str(ObjectId())


def _make_token(app, user_id=USER_ID, role="user"):
    with app.app_context():
        from utils.jwt_auth import create_access_token

        return create_access_token(user_id, role)


def _get(client, token=None):
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    return client.get("/api/user/stats", headers=headers)


def _insert_user(mock_db, user_id=USER_ID):
    mock_db.users.insert_one(
        {
            "_id": ObjectId(user_id),
            "username": "testuser",
            "email": "test@example.com",
            "role": "user",
            "password": bcrypt.hashpw(b"password123", bcrypt.gensalt()),
            "created_at": datetime.now(timezone.utc),
        }
    )


def _insert_image(mock_db, user_id=USER_ID, sentiment=None, audio=None, days_ago=0):
    created = datetime.utcnow() - timedelta(days=days_ago)
    mock_db.images.insert_one(
        {
            "_id": ObjectId(),
            "user_id": ObjectId(user_id),
            "filename": f"file_{ObjectId()}.jpg",
            "title": "Test",
            "description": "desc",
            "sentiment": sentiment,
            "audio_filename": audio,
            "created_at": created,
        }
    )


#---- Auth guard tests ----


def test_stats_no_token(client):
    resp = _get(client)
    assert resp.status_code == 401


def test_stats_invalid_token(client):
    resp = _get(client, token="bad.token.here")
    assert resp.status_code == 401


#---- Stats correctness tests ----


def test_stats_empty_for_new_user(client, app, mock_db):
    """A user with no uploads gets zeroed-out stats."""
    _insert_user(mock_db)
    token = _make_token(app)
    resp = _get(client, token)
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["total_uploads"] == 0
    assert data["voice_notes"] == 0
    assert data["sentiments"] == {"positive": 0, "negative": 0, "neutral": 0}
    assert data["last_upload_at"] is None


def test_stats_counts_only_own_uploads(client, app, mock_db):
    """Stats must not include uploads from other users."""
    _insert_user(mock_db)
    _insert_image(mock_db, user_id=USER_ID, sentiment="positive")
    _insert_image(mock_db, user_id=OTHER_USER_ID, sentiment="positive")

    token = _make_token(app)
    resp = _get(client, token)
    assert resp.get_json()["total_uploads"] == 1


def test_stats_total_uploads(client, app, mock_db):
    _insert_user(mock_db)
    for _ in range(4):
        _insert_image(mock_db)

    token = _make_token(app)
    data = _get(client, token).get_json()
    assert data["total_uploads"] == 4


def test_stats_voice_notes(client, app, mock_db):
    _insert_user(mock_db)
    _insert_image(mock_db, audio="note1.mp3")
    _insert_image(mock_db, audio="note2.mp3")
    _insert_image(mock_db)  # no audio

    token = _make_token(app)
    data = _get(client, token).get_json()
    assert data["voice_notes"] == 2


def test_stats_sentiment_breakdown(client, app, mock_db):
    _insert_user(mock_db)
    _insert_image(mock_db, sentiment="positive")
    _insert_image(mock_db, sentiment="positive")
    _insert_image(mock_db, sentiment="negative")
    _insert_image(mock_db, sentiment="neutral")

    token = _make_token(app)
    data = _get(client, token).get_json()
    assert data["sentiments"]["positive"] == 2
    assert data["sentiments"]["negative"] == 1
    assert data["sentiments"]["neutral"] == 1


def test_stats_daily_trend_length(client, app, mock_db):
    """daily_trend must always contain exactly 7 entries."""
    _insert_user(mock_db)
    token = _make_token(app)
    data = _get(client, token).get_json()
    assert len(data["daily_trend"]) == 7


def test_stats_daily_trend_counts_recent(client, app, mock_db):
    """Uploads from the last 7 days appear in the trend."""
    _insert_user(mock_db)
    _insert_image(mock_db, days_ago=0)
    _insert_image(mock_db, days_ago=1)
    _insert_image(mock_db, days_ago=20)  # outside the window

    token = _make_token(app)
    data = _get(client, token).get_json()
    total_in_trend = sum(d["count"] for d in data["daily_trend"])
    assert total_in_trend == 2


def test_stats_last_upload_at_present(client, app, mock_db):
    """last_upload_at is set when the user has at least one upload."""
    _insert_user(mock_db)
    _insert_image(mock_db)
    token = _make_token(app)
    data = _get(client, token).get_json()
    assert data["last_upload_at"] is not None
