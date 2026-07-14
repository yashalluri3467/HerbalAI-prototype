# Training benchmark — `domain_gate`

- Dataset: `domain_gate`
- Backbone: `mobilenetv2` (input 160x160)
- Device: CPU
- Accuracy: **0.9962**
- Macro-F1: **0.9958**
- Weighted-F1: 0.9961

## Per-class metrics

| Class | Precision | Recall | F1 | Support |
| --- | ---: | ---: | ---: | ---: |
| leaf | 0.991 | 0.998 | 0.994 | 437 |
| other | 0.998 | 1.000 | 0.999 | 630 |
| skin | 0.998 | 0.990 | 0.994 | 496 |

## Confusion matrix

![confusion matrix](domain_gate/confusion_matrix.png)

 | leaf | other | skin | 
 | leaf | 436 | 0 | 4 | 
 | other | 0 | 630 | 1 | 
 | skin | 1 | 0 | 491 | 
