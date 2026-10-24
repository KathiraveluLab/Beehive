"""Uploads over the request size cap must be answered with 413, and the per-type limits shown to
users must fit inside that cap."""
import io
from unittest.mock import patch

from bson import ObjectId

MB = 1024 * 1024


def _auth(app, user_id):
    with app.app_context():
        from utils.jwt_auth import create_access_token

        return {"Authorization": f"Bearer {create_access_token(user_id, 'user')}"}


def _upload(client, headers, payload, filename):
    return client.post(
        "/api/user/upload",
        data={
            "title": "Scan",
            "description": "A document",
            "files": (io.BytesIO(payload), filename),
        },
        content_type="multipart/form-data",
        headers=headers,
    )


def test_request_cap_covers_the_largest_per_type_limit(app):
    import app as app_module

    largest = max(app_module.MIME_SIZE_LIMITS.values())

    assert app.config["MAX_CONTENT_LENGTH"] > largest + app_module.MAX_AUDIO_FILE_SIZE


def test_body_over_the_cap_gets_413_json_not_500(client, app):
    headers = _auth(app, str(ObjectId()))
    payload = b"%PDF-1.4\n" + b"0" * app.config["MAX_CONTENT_LENGTH"]

    response = _upload(client, headers, payload, "huge.pdf")

    assert response.status_code == 413
    assert "too large" in response.get_json()["error"].lower()


def test_pdf_of_the_advertised_maximum_is_accepted(client, app):
    """The upload page tells users a PDF can be up to 25 MB."""
    user_id = str(ObjectId())
    headers = _auth(app, user_id)
    import app as app_module

    payload = b"%PDF-1.4\n" + b"0" * (app_module.MIME_SIZE_LIMITS["application/pdf"] - MB)

    with patch("app.get_user_by_id", return_value={"username": "u"}), patch(
        "app.MAGIC"
    ) as magic, patch("app.save_image") as save_image, patch("app.save_notification"), patch(
        "app.generate_pdf_thumbnail"
    ), patch("app.os.makedirs"), patch("werkzeug.datastructures.FileStorage.save"):
        magic.from_buffer.return_value = "application/pdf"
        response = _upload(client, headers, payload, "report.pdf")

    assert response.status_code == 200
    assert save_image.call_count == 1


def test_file_over_its_own_type_limit_still_gets_413(client, app):
    headers = _auth(app, str(ObjectId()))
    import app as app_module

    jpeg_limit = app_module.MIME_SIZE_LIMITS["image/jpeg"]
    payload = b"\xff\xd8\xff" + b"0" * (jpeg_limit + MB)

    with patch("app.get_user_by_id", return_value={"username": "u"}), patch("app.MAGIC") as magic:
        magic.from_buffer.return_value = "image/jpeg"
        response = _upload(client, headers, payload, "photo.jpg")

    assert response.status_code == 413
    assert f"{jpeg_limit // MB}MB" in response.get_json()["error"]


def test_oversized_analyze_media_request_gets_json_413(client, app):
    headers = _auth(app, str(ObjectId()))
    payload = b"0" * app.config["MAX_CONTENT_LENGTH"]

    response = client.post(
        "/api/analyze-media",
        data={"image": (io.BytesIO(payload), "big.jpg")},
        content_type="multipart/form-data",
        headers=headers,
    )

    assert response.status_code == 413
    assert response.get_json()["error"]
