def test_admin_user_uploads_empty(client, mock_db, admin_token):
    """GET /api/admin/user_uploads/<user_id> - No uploads"""
    response = client.get(
        "/api/admin/user_uploads/some_user_id",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data["images"] == []
    assert data["total_count"] == 0
    assert data["page"] == 1


def test_admin_user_uploads_with_data_and_pagination(client, mock_db, admin_token):
    """GET /api/admin/user_uploads/<user_id> - With uploads and pagination"""
    user_id = "test_user_123"

    mock_db.images.insert_many(
        [
            {"user_id": user_id, "title": "Image 1", "created_at": 3},
            {"user_id": user_id, "title": "Image 2", "created_at": 2},
            {"user_id": user_id, "title": "Image 3", "created_at": 1},
        ]
    )

    mock_db.images.insert_one({"user_id": "other_user", "title": "Other Image", "created_at": 0})

    response = client.get(
        f"/api/admin/user_uploads/{user_id}?page=1&page_size=2",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 200
    data = response.get_json()

    assert data["total_count"] == 3  # Total for this user
    assert len(data["images"]) == 2  # Only 2 returned because of page_size=2
    assert data["totalPages"] == 2
    assert data["images"][0]["title"] == "Image 1"


def test_admin_user_uploads_with_filters(client, mock_db, admin_token):
    """GET /api/admin/user_uploads/<user_id> - Testing filters"""
    user_id = "test_user_456"

    mock_db.images.insert_many(
        [
            {"user_id": user_id, "title": "Happy Dog", "sentiment": "happy", "created_at": 3},
            {"user_id": user_id, "title": "Happy Cat", "sentiment": "happy", "created_at": 2},
            {"user_id": user_id, "title": "Sad Dog", "sentiment": "sad", "created_at": 1},
        ]
    )

    response = client.get(
        f"/api/admin/user_uploads/{user_id}?sentiment=happy&q=Dog",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 200
    data = response.get_json()

    assert data["total_count"] == 1
    assert len(data["images"]) == 1
    assert data["images"][0]["title"] == "Happy Dog"
