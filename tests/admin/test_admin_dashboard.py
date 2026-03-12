import pytest
import mongomock
from unittest.mock import patch
from utils.jwt_auth import create_access_token

def test_admin_dashboard_empty(client, mock_db, admin_token):
    """GET /api/admin/dashboard - No data"""
    response = client.get(
        "/api/admin/dashboard",
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data["stats"]["totalImages"] == 0
    assert data["stats"]["totalVoiceNotes"] == 0
    assert data["stats"]["totalMedia"] == 0
    assert data["recentUploads"] == []


def test_admin_dashboard_with_data(client, mock_db, admin_token):
    """GET /api/admin/dashboard - With data"""
    import datetime
    from bson.objectid import ObjectId

    user_id = ObjectId()
    mock_db.users.insert_one({
        "_id": user_id,
        "username": "testuser",
        "email": "test@example.com"
    })

    # Prepare some mock image uploads
    mock_db.images.insert_many([
        {
            "user_id": str(user_id),
            "filename": "img1.webp",
            "url": "https://example.com/img1.webp", # Avoid direct images as requested
            "created_at": datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=1)
        },
        {
            "user_id": str(user_id),
            "filename": "img2.webp",
            "url": "https://example.com/img2.webp",
            "audio_filename": "audio1.webm", # This represents a voice note
            "created_at": datetime.datetime.now(datetime.timezone.utc)
        }
    ])

    response = client.get(
        "/api/admin/dashboard",
        headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert response.status_code == 200
    data = response.get_json()
    
    # Assert proper statistics were calculated correctly
    assert data["stats"]["totalImages"] == 2
    assert data["stats"]["totalVoiceNotes"] == 1 
    assert data["stats"]["totalMedia"] == 3

    # Assert recentUploads populate correctly
    recent = data["recentUploads"]
    assert len(recent) == 2
    assert recent[0]["filename"] == "img2.webp" # Usually sorted by newest
    assert recent[1]["filename"] == "img1.webp"


def test_admin_analytics_success(client, admin_token):
    """
    GET /api/admin/analytics - Success
    We mock the underlying handler because mongomock does not cleanly support
    the complex `$facet` aggregation pipelines.
    """
    mock_analytics_data = {
        "summary": {
            "total": 50,
            "voiceNotes": 10,
            "increase": 15.5,
            "timeframe": "This month",
            "sentimentAnalysis": {
                "positive": 30,
                "negative": 5,
                "neutral": 15,
                "custom": 0
            }
        },
        "trend": [
            {"date": "2026-03-01", "uploads": {"total": 5, "increase": 0.0}},
            {"date": "2026-03-02", "uploads": {"total": 10, "increase": 100.0}}
        ]
    }

    with patch("routes.adminroutes.get_upload_analytics", return_value=mock_analytics_data):
        response = client.get(
            "/api/admin/analytics?days=7",
            headers={"Authorization": f"Bearer {admin_token}"}
        )

    assert response.status_code == 200
    data = response.get_json()
    assert "uploads" in data
    assert data["uploads"]["summary"]["total"] == 50
    assert data["uploads"]["summary"]["voiceNotes"] == 10
    assert len(data["uploads"]["trend"]) == 2


def test_admin_analytics_failure(client, admin_token):
    """GET /api/admin/analytics - Handle failures cleanly"""
    with patch("routes.adminroutes.get_upload_analytics", return_value=None):
        response = client.get(
            "/api/admin/analytics",
            headers={"Authorization": f"Bearer {admin_token}"}
        )

    assert response.status_code == 500
    data = response.get_json()
    assert data["error"] == "Failed to retrieve analytics data"
