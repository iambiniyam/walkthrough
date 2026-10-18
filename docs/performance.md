# Guide-building performance

Measured on an Apple Silicon Mac with 8 GB RAM using the three `examples/` screenshots and `benchmarks/bench_pipeline.py`.

| Writer | Steps | Time | Per step |
|---|---:|---:|---:|
| Heuristic (OCR only) | 3 | 2.08 s | 693 ms |
| Qwen3-VL-2B 4-bit MLX | 3 | about 64.5 s | about 21.5 s |

The heuristic row isolates OCR and guide assembly. The Qwen row includes model load and step generation; it is not an OCR-only benchmark.

The OCR engine is created once per process. The model is loaded once per process by the web server and reused across requests.
