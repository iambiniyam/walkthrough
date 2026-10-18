# Comparison

## Similar tools

- [Scribe](https://scribehow.com/), [Tango](https://www.tango.us/), [Guidde](https://www.guidde.com/), and Iorad capture a workflow and turn it into a guide.
- They are cloud-first and usually capture from a browser extension.

## What walkthrough does differently

- Works from screenshots you already have, with no recorder and no account.
- Qwen writes the steps, RapidOCR supplies exact labels, and the callout box is drawn locally.
- The guide is editable, re-renderable from JSON, orderable from OCR action words, and masks common PII before export.
- It exports Markdown, standalone HTML, JSON, and a ZIP.
- The npm renderer turns the same JSON into a page without Python.

## Tradeoff

Scribe and Tango also capture the clicks and host the guide. walkthrough covers the writing, annotation, review, and export, and leaves capture and hosting to the user.
