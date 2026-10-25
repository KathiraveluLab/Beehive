"""
Tests for sanitize_text: HTML is stripped, but ordinary punctuation such as
"&", "<" and ">" is kept as plain text instead of being stored HTML-escaped.
"""

import pytest
from bson import ObjectId

from utils.jwt_auth import create_access_token
from utils.sanitize import sanitize_text


@pytest.mark.parametrize(
    "text",
    ["Tom & Jerry", "I <3 you", "5 > 3 and 2 < 4", "Fish & Chips <3"],
)
def test_plain_punctuation_is_not_escaped(text):
    assert sanitize_text(text) == text


@pytest.mark.parametrize(
    "text, expected",
    [
        ("<b>bold</b> & more", "bold & more"),
        ("<img src=x onerror=alert(1)>hi", "hi"),
    ],
)
def test_html_tags_are_stripped(text, expected):
    assert sanitize_text(text) == expected


@pytest.mark.parametrize(
    "text",
    [
        "<<script>script>alert(1)<</script>/script>",
        "<<b>b>x<</b>/b>",
    ],
)
def test_unescaping_does_not_rebuild_tags(text):
    result = sanitize_text(text)
    assert "<script" not in result.lower()
    assert "<b>" not in result.lower()


def test_empty_values():
    assert sanitize_text(None) == ""
    assert sanitize_text("") == ""
    assert sanitize_text("   ") == ""


def test_edit_stores_punctuation_unescaped(client, app, mock_db):
    user_id = ObjectId()
    image_id = mock_db.images.insert_one(
        {"user_id": user_id, "filename": "a.jpg", "title": "old", "description": "old"}
    ).inserted_id
    with app.app_context():
        token = create_access_token(user_id=str(user_id), role="user")

    response = client.patch(
        f"/edit/{image_id}",
        data={"title": "Tom & Jerry", "description": "I <3 you, 5 > 3"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    stored = mock_db.images.find_one({"_id": image_id})
    assert stored["title"] == "Tom & Jerry"
    assert stored["description"] == "I <3 you, 5 > 3"
