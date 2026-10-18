from pathlib import Path

from fastapi.testclient import TestClient

from walkthrough.server import app


def test_invalid_upload_cleans_job_folder(tmp_path, monkeypatch):
    monkeypatch.setenv("WALKTHROUGH_OUTPUT", str(tmp_path))
    client = TestClient(app)
    response = client.post(
        "/api/build",
        files={"files": ("bad.png", b"not an image", "image/png")},
        data={"title": "Bad", "redact": "true"},
    )
    assert response.status_code == 400
    assert list(Path(tmp_path).iterdir()) == []
