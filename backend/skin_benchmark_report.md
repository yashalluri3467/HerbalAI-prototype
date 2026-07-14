# Skin model (`skin_disease`) — backbone selection

Selected backbone: **efficientnetb0** (best validation macro-F1).

| Backbone | Accuracy | Macro-F1 | Weighted-F1 | Params | Device |
| --- | ---: | ---: | ---: | ---: | --- |
| mobilenetv2 | 0.4787 | 0.4736 | 0.4832 | 2,286,166 | CPU |
| efficientnetb0 | 0.4835 | 0.4764 | 0.4871 | 4,077,753 | CPU |

The winner was copied to `models/skin_disease/` and is served by `POST /api/predict/skin`.
