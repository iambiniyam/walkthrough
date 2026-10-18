"""Browser-level accessibility checks for walkthrough."""

from __future__ import annotations

import socket
import threading
import time
from pathlib import Path

import pytest
import uvicorn
from PIL import Image

pytest.importorskip("playwright.sync_api")
from playwright.sync_api import sync_playwright

from walkthrough.server import app

AXE = Path(__file__).with_name("axe.min.js")


def free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


@pytest.fixture(scope="module")
def live_server(tmp_path_factory):
    old = None
    import os

    old = os.environ.get("WALKTHROUGH_OUTPUT")
    os.environ["WALKTHROUGH_OUTPUT"] = str(tmp_path_factory.mktemp("walkthrough-out"))
    port = free_port()
    config = uvicorn.Config(app, host="127.0.0.1", port=port, log_level="error")
    server = uvicorn.Server(config)
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    deadline = time.time() + 10
    while time.time() < deadline:
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=0.2):
                break
        except OSError:
            time.sleep(0.1)
    yield f"http://127.0.0.1:{port}"
    server.should_exit = True
    thread.join(timeout=5)
    if old is None:
        os.environ.pop("WALKTHROUGH_OUTPUT", None)
    else:
        os.environ["WALKTHROUGH_OUTPUT"] = old


def axe_violations(page) -> list[dict]:
    page.add_script_tag(path=str(AXE))
    report = page.evaluate(
        """async () => await axe.run(document, {
          runOnly: { type: "tag", values: ["wcag2a", "wcag2aa", "wcag21aa"] }
        })"""
    )
    return [item for item in report["violations"] if item["impact"] in {"serious", "critical"}]


def test_initial_and_result_states(live_server, tmp_path):
    shot = tmp_path / "shot.png"
    image = Image.new("RGB", (600, 300), "white")
    from PIL import ImageDraw

    ImageDraw.Draw(image).text((40, 80), "Export report", fill="black")
    image.save(shot)

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        tab = browser.new_page(viewport={"width": 1182, "height": 900})
        tab.goto(live_server, wait_until="networkidle")
        assert axe_violations(tab) == []

        tab.set_input_files("#files", str(shot))
        tab.click("#go")
        tab.wait_for_selector("#result:not([hidden])", timeout=180000)
        assert axe_violations(tab) == []
        browser.close()
