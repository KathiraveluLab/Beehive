def test_admin_users_empty(client, mock_db, admin_token):
    """GET /api/admin/users - No users in database"""

    response = client.get(
        "/api/admin/users", headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data["users"] == []
    assert data["totalCount"] == 0


def test_admin_users_with_data(client, mock_db, admin_token):
    """GET /api/admin/users - With users in database"""

    mock_db.users.insert_many(
        [
            {
                "username": "user1",
                "email": "user1@example.com",
                "role": "user",
                "status": "active",
            },
            {
                "username": "admin1",
                "email": "admin@example.com",
                "role": "admin",
                "status": "active",
            },
        ]
    )

    response = client.get(
        "/api/admin/users", headers={"Authorization": f"Bearer {admin_token}"}
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data["totalCount"] == 2
    assert len(data["users"]) == 2
    users_sorted = sorted(data["users"], key=lambda u: u["name"])
    assert users_sorted[0]["name"] == "admin1"
    assert users_sorted[1]["name"] == "user1"
