const escapeHtml = (value) =>
  String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");

const imagePath = (step, imageDir) =>
  `${imageDir}/step-${Number(step.number)}.png`;

export function renderMarkdown(guide, options = {}) {
  const imageDir = options.imageDir || "images";
  const lines = [`# ${guide.title || "Step-by-step guide"}`, ""];
  if (guide.summary) lines.push(guide.summary, "");
  for (const step of guide.steps || []) {
    lines.push(`## ${step.number}. ${step.title || "Step"}`);
    lines.push("");
    lines.push(`![Step ${step.number}: ${step.title || "Step"}](${imagePath(step, imageDir)})`);
    lines.push("");
    if (step.body) lines.push(step.body, "");
    if (step.callout) lines.push(`**Select:** \`${step.callout}\``, "");
  }
  return lines.join("\n");
}

export function renderHtml(guide, options = {}) {
  const imageDir = options.imageDir || "images";
  const cards = (guide.steps || [])
    .map((step) => {
      const callout = step.callout
        ? `<p class="callout"><strong>Select:</strong> <code>${escapeHtml(step.callout)}</code></p>`
        : "";
      return `<section class="step"><div class="number">${Number(step.number)}</div><div>
        <h2>${escapeHtml(step.title || "Step")}</h2>
        <img src="${escapeHtml(imagePath(step, imageDir))}" alt="Step ${Number(step.number)}: ${escapeHtml(step.title || "Step")}">
        <p>${escapeHtml(step.body || "")}</p>${callout}
      </div></section>`;
    })
    .join("");
  return `<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>${escapeHtml(guide.title || "Step-by-step guide")}</title>
<style>
:root{color-scheme:light dark;--ink:#17211b;--muted:#5d6a61;--line:#ddd7c6;--paper:#f7f5ef;--accent:#2f5d8a}
@media (prefers-color-scheme:dark){:root{--ink:#edf2ee;--muted:#a7b5ac;--line:#2d3a33;--paper:#101613;--accent:#8ab4f8}}
*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font-family:ui-sans-serif,system-ui,-apple-system,sans-serif;line-height:1.6}
main{width:min(880px,100% - 32px);margin:0 auto;padding:48px 0}h1{font-size:2rem;letter-spacing:-.02em;margin:0 0 4px}
.summary{color:var(--muted);margin:0 0 32px}.step{display:grid;grid-template-columns:40px minmax(0,1fr);gap:16px;padding:20px 0;border-top:1px solid var(--line)}
.number{display:grid;place-items:center;width:32px;height:32px;border-radius:50%;background:var(--accent);color:#fff;font-weight:700}
h2{font-size:1.125rem;margin:0 0 8px}img{display:block;max-width:100%;height:auto;border:1px solid var(--line);border-radius:12px;margin:8px 0 12px}
.callout{background:#e8f0f7;color:#17324d;border-radius:8px;padding:8px 12px;display:inline-block}
@media (prefers-color-scheme:dark){.callout{background:#1c2c3e;color:#d9e8f7}}code{font-family:ui-monospace,Menlo,monospace}
</style></head><body><main><h1>${escapeHtml(guide.title || "Step-by-step guide")}</h1>
<p class="summary">${escapeHtml(guide.summary || "")}</p>${cards}</main></body></html>`;
}
