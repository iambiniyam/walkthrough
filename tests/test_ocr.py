from walkthrough.ocr import TextLine, find_callout


def test_find_callout_exact_and_partial():
    lines = [
        TextLine("Export report", (10, 10, 120, 40), 0.9),
        TextLine("Cancel", (10, 50, 80, 80), 0.9),
    ]
    match = find_callout(lines, "export report")
    assert match is not None
    assert match.text == "Export report"
    assert find_callout(lines, "Report") is not None
    assert find_callout(lines, "Delete") is None
