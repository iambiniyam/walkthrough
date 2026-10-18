# walkthrough-render

Render a walkthrough guide JSON object as Markdown or accessible standalone HTML.

```bash
pnpm add walkthrough-render
```

```js
import { renderMarkdown, renderHtml } from "walkthrough-render";

const markdown = renderMarkdown(guide);
const html = renderHtml(guide, { imageDir: "assets" });
```

The guide shape is the JSON written by `walkthrough`:

```json
{
  "title": "Export a report",
  "summary": "A one-step guide.",
  "steps": [
    { "number": 1, "title": "Open Export", "body": "Select Export.", "callout": "Export" }
  ]
}
```

The renderer does not run a model and does not annotate images. It is a small dependency-free package for docs sites and static generators.

MIT.
