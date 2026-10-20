import datetime

from bson import ObjectId

from utils.jwt_auth import create_access_token


def _auth_headers(app, user_id):
    with app.app_context():
        token = create_access_token(user_id=user_id, role="user")
    return {"Authorization": f"Bearer {token}"}


def _insert_image(mock_db, user_id, created_at):
    mock_db.images.insert_one(
        {
            "user_id": ObjectId(user_id),
            "filename": f"{created_at:%Y%m%d}.png",
            "title": f"Image {created_at:%Y-%m-%d}",
            "description": "A description",
            "sentiment": "neutral",
            "created_at": created_at,
        }
    )


def test_invalid_from_date_is_a_bad_request(client, app, mock_db):
    user_id = str(ObjectId())
    _insert_image(mock_db, user_id, datetime.datetime(2026, 1, 1))

    response = client.get(
        "/api/user/user_uploads?from=notadate", headers=_auth_headers(app, user_id)
    )

    assert response.status_code == 400
    assert "'from'" in response.get_json()["error"]


def test_invalid_to_date_is_a_bad_request(client, app, mock_db):
    user_id = str(ObjectId())

    response = client.get(
        "/api/user/user_uploads?to=2026-13-45", headers=_auth_headers(app, user_id)
    )

    assert response.status_code == 400
    assert "'to'" in response.get_json()["error"]


def test_date_range_filters_the_uploads(client, app, mock_db):
    user_id = str(ObjectId())
    _insert_image(mock_db, user_id, datetime.datetime(2026, 1, 1))
    _insert_image(mock_db, user_id, datetime.datetime(2026, 2, 1))
    _insert_image(mock_db, user_id, datetime.datetime(2026, 3, 1))

    response = client.get(
        "/api/user/user_uploads?from=2026-01-15&to=2026-02-15T23:59:59",
        headers=_auth_headers(app, user_id),
    )

    assert response.status_code == 200
    body = response.get_json()
    assert body["total"] == 1
    assert body["images"][0]["title"] == "Image 2026-02-01"
