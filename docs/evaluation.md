# Walkthrough model evaluation

This is a small engineering check on three generated interface screenshots. It is not a public benchmark.

## Setup

- Qwen3-VL-2B-Instruct 4-bit MLX, 1.7 GB.
- RapidOCR for labels and callout boxes.
- Apple Silicon Mac with 8 GB RAM.
- Three screenshots: Reports, Export report, Report ready.

## Method

1. OCR each screenshot.
2. Ask the model for one JSON step per screenshot, using the OCR labels.
3. Match the requested callout to an OCR box.
4. Record latency, callout match, and a human review of the step.

## Results

| Step | Title | Callout | Latency |
|---|---|---|---|
| 1 | Review monthly reports | Export report | about 21 s |
| 2 | Choose export format | Format | about 21 s |
| 3 | Download your report | Download | about 21 s |

Total for three steps including model load: 64.5 seconds. All three callouts matched an OCR box. The model did not invent a control.

## What worked

- Correct callouts for all three screens.
- Useful step titles and descriptions.
- The JSON shape held.
- The OCR box made the highlight land on the right control.

## What needs review

- Step 1 says clicking Export will "view this month's numbers." It opens the export dialog instead. A human should fix that.
- The model describes what it sees. It does not know the destination of a click.
- Small or low-contrast labels can be missed by OCR.
- The three screenshots are clean and synthetic. Real screenshots have more text.

## Decision

Ship Qwen3-VL 4-bit MLX with a review-first UI. Keep the heuristic writer for tests. Do not auto-publish a guide without review.
