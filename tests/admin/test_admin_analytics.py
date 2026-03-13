from unittest.mock import patch


def test_admin_analytics_success(client, admin_token):
    """
    GET /api/admin/analytics - Success
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
                "custom": 0,
            },
        },
        "trend": [
            {"date": "2026-03-01", "uploads": {"total": 5, "increase": 0.0}},
            {"date": "2026-03-02", "uploads": {"total": 10, "increase": 100.0}},
        ],
    }

    with patch(
        "routes.adminroutes.get_upload_analytics", return_value=mock_analytics_data
    ):
        response = client.get(
            "/api/admin/analytics?days=7",
            headers={"Authorization": f"Bearer {admin_token}"},
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
            "/api/admin/analytics", headers={"Authorization": f"Bearer {admin_token}"}
        )

    assert response.status_code == 500
    data = response.get_json()
    assert data["error"] == "Failed to retrieve analytics data"
