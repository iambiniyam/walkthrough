import test from "node:test";
import assert from "node:assert/strict";
import { renderHtml, renderMarkdown } from "../src/index.js";

const guide = {
  title: "Export a report",
  summary: "A one-step guide.",
  steps: [
    { number: 1, title: "Open <Export>", body: "Select Export.", callout: "Export" }
  ]
};

test("markdown includes steps and images", () => {
  const text = renderMarkdown(guide);
  assert.match(text, /## 1\. Open <Export>/);
  assert.match(text, /images\/step-1\.png/);
  assert.match(text, /\*\*Select:\*\* `Export`/);
});

test("html escapes content and is standalone", () => {
  const page = renderHtml(guide);
  assert.match(page, /<!doctype html>/);
  assert.match(page, /Open &lt;Export&gt;/);
  assert.doesNotMatch(page, /Open <Export>/);
});

test("image directory can be changed", () => {
  assert.match(renderMarkdown(guide, { imageDir: "assets" }), /assets\/step-1\.png/);
});
