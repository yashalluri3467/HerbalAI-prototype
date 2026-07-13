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
| leaf | 0.993 | 0.995 | 0.994 | 437 |
| other | 0.998 | 1.000 | 0.999 | 630 |
| skin | 0.996 | 0.992 | 0.994 | 496 |

## Confusion matrix

![confusion matrix](domain_gate/confusion_matrix.png)

 | leaf | other | skin | 
 | leaf | 435 | 0 | 3 | 
 | other | 0 | 630 | 1 | 
 | skin | 2 | 0 | 492 | 
