import io

import pytest
from bson import ObjectId

from utils.jwt_auth import create_access_token

PNG = b"\x89PNG\r\n\x1a\n" + b"0" * 100
WAV = b"RIFF" + b"\x00" * 4 + b"WAVE" + b"1" * 200


class FakeMagic:
    """Stands in for libmagic, which is not always installed where the tests run."""

    def from_buffer(self, header):
        if header.startswith(b"\x89PNG"):
            return "image/png"
        if header.startswith(b"RIFF"):
            return "audio/wav"
        return "application/x-dosexec"


@pytest.fixture
def upload(client, app, mock_db, tmp_path, monkeypatch):
    # Import here: another test reloads the app module, so a module-level import can go stale.
    import app as app_module

    monkeypatch.setattr(app_module, "MAGIC", FakeMagic())
    monkeypatch.setitem(app.config, "UPLOAD_FOLDER", str(tmp_path))
    user_id = str(ObjectId())
    with app.app_context():
        token = create_access_token(user_id=user_id, role="user")

    def post(files, **fields):
        data = {"title": "Title", "description": "Description", "sentiment": "neutral"}
        data.update(fields)
        data["files"] = [(io.BytesIO(content), name) for name, content in files]
        if "audio" in data:
            data["audio"] = (io.BytesIO(data["audio"]), "note.wav")
        return client.post(
            "/api/user/upload",
            data=data,
            headers={"Authorization": f"Bearer {token}"},
            content_type="multipart/form-data",
        )

    return post


def _saved_files(tmp_path):
    return [p for p in tmp_path.iterdir() if p.is_file()]


def test_upload_of_two_images_saves_both(upload, mock_db, tmp_path):
    response = upload([("one.png", PNG), ("two.png", PNG)])

    assert response.status_code == 200
    assert mock_db.images.count_documents({}) == 2
    assert mock_db.notifications.count_documents({}) == 2
    assert len(_saved_files(tmp_path)) == 2


def test_a_bad_file_later_in_the_batch_saves_nothing(upload, mock_db, tmp_path):
    response = upload([("ok.png", PNG), ("bad.png", b"MZ" + b"0" * 100)])

    assert response.status_code == 400
    assert mock_db.images.count_documents({}) == 0
    assert mock_db.notifications.count_documents({}) == 0
    assert _saved_files(tmp_path) == []


def test_an_extension_that_is_not_allowed_saves_nothing(upload, mock_db, tmp_path):
    response = upload([("ok.png", PNG), ("script.exe", PNG)])

    assert response.status_code == 400
    assert mock_db.images.count_documents({}) == 0
    assert _saved_files(tmp_path) == []


def test_invalid_audio_data_saves_nothing(upload, mock_db, tmp_path):
    response = upload([("ok.png", PNG)], audioData="not a data url")

    assert response.status_code == 400
    assert mock_db.images.count_documents({}) == 0
    assert _saved_files(tmp_path) == []


def test_every_image_gets_its_own_complete_audio_file(upload, mock_db, tmp_path):
    response = upload([("one.png", PNG), ("two.png", PNG)], audio=WAV, title="note")

    assert response.status_code == 200
    records = list(mock_db.images.find({}))
    assert len(records) == 2
    audio_names = {record["audio_filename"] for record in records}
    assert len(audio_names) == 2
    for name in audio_names:
        assert (tmp_path / name).read_bytes() == WAV
