const fileInput = document.getElementById("files");
const drop = document.getElementById("drop");
const fileList = document.getElementById("file-list");
const titleInput = document.getElementById("title");
const redactInput = document.getElementById("redact");
const autoOrderInput = document.getElementById("auto-order");
const go = document.getElementById("go");
const statusLine = document.getElementById("status");
const result = document.getElementById("result");
const resultTitle = document.getElementById("result-title");
const summary = document.getElementById("summary");
const stepsBox = document.getElementById("steps");
const bundle = document.getElementById("bundle");
const htmlLink = document.getElementById("html");
const printLink = document.getElementById("print");
const markdownLink = document.getElementById("markdown");
const jsonLink = document.getElementById("json");

const MAX_BYTES = 12 * 1024 * 1024;
const MAX_FILES = 20;
const state = { files: [], guide: null };

function escapeHtml(value) {
  return String(value == null ? "" : value)
    .replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;").replaceAll("'", "&#39;");
}

function setStatus(message, isError = false) {
  statusLine.textContent = message;
  statusLine.classList.toggle("is-error", isError);
}

function addFiles(files) {
  for (const file of files) {
    if (!file.type.startsWith("image/")) continue;
    if (file.size > MAX_BYTES) { setStatus(`${file.name} is larger than 12 MB.`, true); continue; }
    if (state.files.length >= MAX_FILES) { setStatus(`Only ${MAX_FILES} screenshots fit.`, true); break; }
    if (!state.files.some((item) => item.name === file.name && item.size === file.size)) state.files.push(file);
  }
  renderFiles();
}

function renderFiles() {
  fileList.innerHTML = state.files.map((file, index) => `<li class="file-item">
    <span class="file-name">${index + 1}. ${escapeHtml(file.name)}</span>
    <span class="row-actions">
      <button type="button" data-action="up" data-index="${index}" ${index === 0 ? "disabled" : ""}>Up</button>
      <button type="button" data-action="down" data-index="${index}" ${index === state.files.length - 1 ? "disabled" : ""}>Down</button>
      <button type="button" data-action="remove" data-index="${index}">Remove</button>
    </span>
  </li>`).join("");
  if (state.files.length) setStatus(`${state.files.length} screenshot${state.files.length === 1 ? "" : "s"} ready.`);
}

fileInput.addEventListener("change", () => { addFiles(fileInput.files); fileInput.value = ""; });
fileList.addEventListener("click", (event) => {
  const button = event.target.closest("button[data-action]");
  if (!button) return;
  const index = Number(button.dataset.index);
  const action = button.dataset.action;
  if (action === "remove") state.files.splice(index, 1);
  if (action === "up" && index > 0) [state.files[index - 1], state.files[index]] = [state.files[index], state.files[index - 1]];
  if (action === "down" && index < state.files.length - 1) [state.files[index + 1], state.files[index]] = [state.files[index], state.files[index + 1]];
  renderFiles();
});

["dragenter", "dragover"].forEach((name) => drop.addEventListener(name, (event) => {
  event.preventDefault(); drop.classList.add("is-over");
}));
["dragleave", "drop"].forEach((name) => drop.addEventListener(name, (event) => {
  event.preventDefault(); drop.classList.remove("is-over");
}));
drop.addEventListener("drop", (event) => addFiles(event.dataTransfer.files));

document.addEventListener("paste", (event) => {
  const files = [];
  for (const item of event.clipboardData ? event.clipboardData.items : []) {
    if (item.type.startsWith("image/")) {
      const file = item.getAsFile();
      if (file) files.push(file);
    }
  }
  if (files.length) { addFiles(files); setStatus("Pasted screenshot added."); }
});

function overlay(step) {
  if (!step.bbox || !step.image_size) return "";
  const [x0, y0, x1, y1] = step.bbox;
  const [width, height] = step.image_size;
  const left = (x0 / width) * 100;
  const top = (y0 / height) * 100;
  const boxWidth = ((x1 - x0) / width) * 100;
  const boxHeight = ((y1 - y0) / height) * 100;
  return `<span class="box" style="left:${left}%;top:${top}%;width:${boxWidth}%;height:${boxHeight}%"></span>`;
}

function renderStep(step) {
  return `<article class="step" data-number="${step.number}">
    <div>
      <div class="number">${step.number}</div>
      <div class="shot"><img src="${step.image_url}" alt="Screenshot for step ${step.number}">${overlay(step)}</div>
    </div>
    <div>
      <p class="conf">${Math.round((Number(step.confidence) || 0) * 100)}% confidence</p>
      <div class="field"><label for="title-${step.number}">Step title</label><input id="title-${step.number}" type="text" data-field="title" value="${escapeHtml(step.title)}"></div>
      <div class="field"><label for="body-${step.number}">Description</label><textarea id="body-${step.number}" data-field="body">${escapeHtml(step.body)}</textarea></div>
      <div class="field"><label for="callout-${step.number}">Highlighted label</label><input id="callout-${step.number}" type="text" data-field="callout" value="${escapeHtml(step.callout)}"></div>
    </div>
  </article>`;
}

function render(data) {
  state.guide = data.guide;
  result.hidden = false;
  summary.textContent = `${data.guide.steps.length} steps · ${data.writer}`;
  stepsBox.innerHTML = data.guide.steps.map(renderStep).join("");
  bundle.href = data.downloads.bundle;
  htmlLink.href = data.downloads.html;
  printLink.href = data.downloads.html;
  markdownLink.href = data.downloads.markdown;
  jsonLink.href = data.downloads.json;
  resultTitle.textContent = data.guide.title || "Review the guide";
  resultTitle.focus();
}

async function build() {
  if (!state.files.length) { setStatus("Add at least one screenshot first.", true); return; }
  go.disabled = true;
  go.textContent = "Writing...";
  setStatus("Reading screenshots locally. The first run loads the model.");
  result.hidden = true;
  document.querySelector("main").setAttribute("aria-busy", "true");
  const body = new FormData();
  for (const file of state.files) body.append("files", file);
  body.append("title", titleInput.value.trim() || "Step-by-step guide");
  body.append("redact", redactInput.checked ? "true" : "false");
  body.append("auto_order", autoOrderInput.checked ? "true" : "false");
  try {
    const response = await fetch("/api/build", { method: "POST", body });
    if (!response.ok) {
      const payload = await response.json().catch(() => ({}));
      throw new Error(payload.detail || `Server returned ${response.status}`);
    }
    render(await response.json());
    setStatus("Done. Review each step before publishing.");
  } catch (error) {
    setStatus(error.message, true);
  } finally {
    go.disabled = false;
    go.textContent = "Build guide";
    document.querySelector("main").setAttribute("aria-busy", "false");
  }
}

go.addEventListener("click", build);
document.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && (event.metaKey || event.ctrlKey)) { event.preventDefault(); build(); }
});
