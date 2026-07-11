# Skin model (`skin_disease`) — backbone selection

Selected backbone: **efficientnetb0** (best validation macro-F1).

| Backbone | Accuracy | Macro-F1 | Weighted-F1 | Params | Device |
| --- | ---: | ---: | ---: | ---: | --- |
| mobilenetv2 | 0.4458 | 0.4376 | 0.4493 | 2,286,166 | CPU |
| efficientnetb0 | 0.4658 | 0.4549 | 0.4649 | 4,077,753 | CPU |

The winner was copied to `models/skin_disease/` and is served by `POST /api/predict/skin`.
