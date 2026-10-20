import datetime

from bson import ObjectId

from utils.jwt_auth import create_access_token


def _auth_headers(app, user_id, role="user"):
    with app.app_context():
        token = create_access_token(user_id=user_id, role=role)
    return {"Authorization": f"Bearer {token}"}


def _insert_image(mock_db, user_id, sentiment="positive"):
    return mock_db.images.insert_one(
        {
            "user_id": ObjectId(user_id),
            "filename": "photo.png",
            "title": "Old title",
            "description": "Old description",
            "sentiment": sentiment,
            "created_at": datetime.datetime(2026, 1, 1),
        }
    ).inserted_id


def test_edit_without_sentiment_keeps_the_stored_sentiment(client, app, mock_db):
    user_id = str(ObjectId())
    image_id = _insert_image(mock_db, user_id, sentiment="positive")

    response = client.patch(
        f"/edit/{image_id}",
        data={"title": "New title", "description": "New description"},
        headers=_auth_headers(app, user_id),
    )

    assert response.status_code == 200
    image = mock_db.images.find_one({"_id": image_id})
    assert image["title"] == "New title"
    assert image["description"] == "New description"
    assert image["sentiment"] == "positive"


def test_edit_with_sentiment_updates_it(client, app, mock_db):
    user_id = str(ObjectId())
    image_id = _insert_image(mock_db, user_id, sentiment="positive")

    response = client.patch(
        f"/edit/{image_id}",
        data={"title": "T", "description": "D", "sentiment": "negative"},
        headers=_auth_headers(app, user_id),
    )

    assert response.status_code == 200
    assert mock_db.images.find_one({"_id": image_id})["sentiment"] == "negative"


def test_edit_requires_title_and_description(client, app, mock_db):
    user_id = str(ObjectId())
    image_id = _insert_image(mock_db, user_id)

    response = client.patch(
        f"/edit/{image_id}",
        data={"title": "Only a title"},
        headers=_auth_headers(app, user_id),
    )

    assert response.status_code == 400
    assert mock_db.images.find_one({"_id": image_id})["title"] == "Old title"


def test_edit_of_another_users_image_is_forbidden(client, app, mock_db):
    owner_id = str(ObjectId())
    image_id = _insert_image(mock_db, owner_id)

    response = client.patch(
        f"/edit/{image_id}",
        data={"title": "Hijacked", "description": "Hijacked"},
        headers=_auth_headers(app, str(ObjectId())),
    )

    assert response.status_code == 403
    assert mock_db.images.find_one({"_id": image_id})["title"] == "Old title"
