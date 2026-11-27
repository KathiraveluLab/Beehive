import base64

import pytest


@pytest.mark.parametrize(
    "mime",
    [
        "audio/webm",
        "audio/webm;codecs=opus",
        "audio/ogg;codecs=opus",
        "AUDIO/WEBM;codecs=opus",
    ],
)
def test_decode_audio_data_accepts_mime_parameters(app, mime):
    """Browsers label MediaRecorder blobs like 'audio/webm;codecs=opus'."""
    from app import _decode_audio_data

    payload = b"fake-audio-bytes"
    data_url = f"data:{mime};base64,{base64.b64encode(payload).decode()}"

    with app.test_request_context():
        audio, base_mime = _decode_audio_data(data_url)

    assert audio == payload
    assert base_mime == mime.lower().split(";")[0]


def test_decode_audio_data_still_rejects_disallowed_mime_with_parameters(app):
    from app import _decode_audio_data

    data_url = "data:text/html;charset=utf-8;base64," + base64.b64encode(b"x").decode()

    with app.test_request_context():
        audio, response = _decode_audio_data(data_url)

    assert audio is None
    assert response[1] == 400
    assert response[0].get_json()["error"] == "Unsupported audio MIME type"
