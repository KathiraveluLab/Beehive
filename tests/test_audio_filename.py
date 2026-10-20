import base64
import io

import pytest
from bson import ObjectId

from utils.jwt_auth import create_access_token

PNG = b"\x89PNG\r\n\x1a\n" + b"0" * 100
WAV = b"RIFF" + b"\x00" * 4 + b"WAVE" + b"1" * 200


class FakeMagic:
    """Stands in for libmagic, which is not always installed where the tests run."""

    def from_buffer(self, header):
        return (
            "image/png" if header.startswith(b"\x89PNG") else "application/octet-stream"
        )


@pytest.fixture
def uploaded(client, app, mock_db, tmp_path, monkeypatch):
    """Upload an image with a voice note whose title has capital letters."""
    # Import here: another test reloads the app module, so a module-level import can go stale.
    import app as app_module

    monkeypatch.setattr(app_module, "MAGIC", FakeMagic())
    monkeypatch.setitem(app.config, "UPLOAD_FOLDER", str(tmp_path))
    with app.app_context():
        token = create_access_token(user_id=str(ObjectId()), role="user")
    headers = {"Authorization": f"Bearer {token}"}
    audio_url = "data:audio/wav;base64," + base64.b64encode(WAV).decode()

    response = client.post(
        "/api/user/upload",
        data={
            "title": "My Day",
            "description": "Description",
            "sentiment": "neutral",
            "files": [(io.BytesIO(PNG), "photo.png")],
            "audioData": audio_url,
        },
        headers=headers,
        content_type="multipart/form-data",
    )
    assert response.status_code == 200
    return headers, mock_db.images.find_one({}), tmp_path


def test_the_audio_file_on_disk_matches_the_stored_name(uploaded):
    _, record, tmp_path = uploaded

    assert (tmp_path / record["audio_filename"]).read_bytes() == WAV


def test_the_voice_note_can_be_served(client, uploaded):
    headers, record, _ = uploaded

    response = client.get(f"/api/audio/{record['audio_filename']}", headers=headers)

    assert response.status_code == 200
    assert response.data == WAV


def test_deleting_the_image_removes_its_voice_note(client, uploaded, mock_db):
    headers, record, tmp_path = uploaded

    response = client.delete(f"/delete/{record['_id']}", headers=headers)

    assert response.status_code == 200
    assert not (tmp_path / record["audio_filename"]).exists()
    assert list(tmp_path.iterdir()) == []
