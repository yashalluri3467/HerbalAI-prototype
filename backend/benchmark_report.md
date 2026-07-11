# HerbalAI Inference Efficiency Benchmark Report
Date: 2026-07-07 18:45:30
Environment: CUDA Inference, Batch Size: 1, Image Shape: (1, 3, 224, 224)

## Skin Classifier (Classes: 8)
| Model Format | File Size (MB) | Load Time (ms) | Avg Latency (ms) | P95 Latency (ms) | Throughput (FPS) | Speedup vs. Standard |
|---|---|---|---|---|---|---|
| **STANDARD** | 15.32 MB | 175.6 ms | 5.06 ms | 5.51 ms | 197.7 FPS | 1.00x |
| **TORCHSCRIPT** | 15.65 MB | 106.4 ms | 9.74 ms | 3.84 ms | 102.7 FPS | 0.52x |
| **FP16** | 7.71 MB | 117.0 ms | 6.04 ms | 6.32 ms | 165.6 FPS | 0.84x |
| **TORCHSCRIPT_FP16** | 8.05 MB | 96.2 ms | 10.33 ms | 4.81 ms | 96.8 FPS | 0.49x |


## Herb Classifier (Classes: 18)
| Model Format | File Size (MB) | Load Time (ms) | Avg Latency (ms) | P95 Latency (ms) | Throughput (FPS) | Speedup vs. Standard |
|---|---|---|---|---|---|---|
| **STANDARD** | 15.36 MB | 101.4 ms | 4.96 ms | 5.22 ms | 201.5 FPS | 1.00x |
| **TORCHSCRIPT** | 15.69 MB | 97.8 ms | 11.03 ms | 6.52 ms | 90.6 FPS | 0.45x |
| **FP16** | 7.73 MB | 108.6 ms | 6.74 ms | 7.92 ms | 148.4 FPS | 0.74x |
| **TORCHSCRIPT_FP16** | 8.08 MB | 98.5 ms | 11.07 ms | 4.96 ms | 90.3 FPS | 0.45x |

