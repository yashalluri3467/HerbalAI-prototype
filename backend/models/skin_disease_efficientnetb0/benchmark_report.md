# Training benchmark — `skin_disease_efficientnetb0`

- Dataset: `skin_disease`
- Backbone: `efficientnetb0` (input 160x160)
- Device: CPU
- Accuracy: **0.4658**
- Macro-F1: **0.4549**
- Weighted-F1: 0.4649

## Per-class metrics

| Class | Precision | Recall | F1 | Support |
| --- | ---: | ---: | ---: | ---: |
| acne | 0.506 | 0.669 | 0.576 | 133 |
| actinic_keratosis | 0.583 | 0.403 | 0.476 | 149 |
| benign_tumors | 0.504 | 0.432 | 0.465 | 132 |
| bullous | 0.477 | 0.451 | 0.463 | 91 |
| candidiasis | 0.429 | 0.581 | 0.493 | 62 |
| drugeruption | 0.575 | 0.221 | 0.320 | 122 |
| eczema | 0.260 | 0.192 | 0.221 | 130 |
| infestations_bites | 0.379 | 0.217 | 0.276 | 115 |
| lichen | 0.486 | 0.285 | 0.359 | 123 |
| lupus | 0.299 | 0.377 | 0.333 | 69 |
| moles | 0.264 | 0.571 | 0.361 | 77 |
| psoriasis | 0.301 | 0.536 | 0.385 | 138 |
| rosacea | 0.714 | 0.652 | 0.682 | 138 |
| seborrh_keratoses | 0.535 | 0.543 | 0.539 | 140 |
| skincancer | 0.615 | 0.366 | 0.459 | 131 |
| sun_sunlight_damage | 0.493 | 0.256 | 0.337 | 137 |
| tinea | 0.486 | 0.374 | 0.423 | 139 |
| unknown_normal | 0.888 | 0.793 | 0.838 | 140 |
| vascular_tumors | 0.440 | 0.424 | 0.432 | 172 |
| vasculitis | 0.249 | 0.573 | 0.347 | 89 |
| vitiligo | 0.779 | 0.688 | 0.731 | 144 |
| warts | 0.399 | 0.644 | 0.493 | 132 |

## Confusion matrix

![confusion matrix](skin_disease_efficientnetb0/confusion_matrix.png)

 | acne | actinic_keratosis | benign_tumors | bullous | candidiasis | drugeruption | eczema | infestations_bites | lichen | lupus | moles | psoriasis | rosacea | seborrh_keratoses | skincancer | sun_sunlight_damage | tinea | unknown_normal | vascular_tumors | vasculitis | vitiligo | warts | 
 | acne | 89 | 7 | 1 | 1 | 2 | 6 | 12 | 4 | 2 | 9 | 1 | 1 | 16 | 1 | 2 | 8 | 5 | 2 | 2 | 1 | 3 | 1 | 
 | actinic_keratosis | 2 | 60 | 3 | 0 | 0 | 4 | 1 | 2 | 5 | 2 | 1 | 2 | 3 | 6 | 3 | 3 | 1 | 1 | 3 | 0 | 1 | 0 | 
 | benign_tumors | 0 | 0 | 57 | 0 | 0 | 1 | 2 | 2 | 1 | 1 | 3 | 4 | 0 | 10 | 26 | 0 | 0 | 0 | 4 | 1 | 0 | 1 | 
 | bullous | 0 | 6 | 2 | 41 | 0 | 13 | 3 | 5 | 3 | 3 | 0 | 0 | 0 | 0 | 0 | 1 | 2 | 1 | 2 | 2 | 2 | 0 | 
 | candidiasis | 0 | 4 | 0 | 1 | 36 | 4 | 7 | 1 | 5 | 0 | 1 | 6 | 0 | 0 | 1 | 1 | 3 | 2 | 2 | 2 | 1 | 7 | 
 | drugeruption | 1 | 2 | 0 | 3 | 0 | 27 | 2 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 5 | 1 | 0 | 1 | 2 | 0 | 
 | eczema | 0 | 3 | 1 | 2 | 1 | 5 | 25 | 10 | 8 | 2 | 0 | 5 | 0 | 2 | 1 | 7 | 9 | 1 | 2 | 6 | 1 | 5 | 
 | infestations_bites | 0 | 2 | 2 | 3 | 1 | 5 | 2 | 25 | 3 | 2 | 2 | 0 | 0 | 0 | 1 | 6 | 2 | 1 | 7 | 1 | 0 | 1 | 
 | lichen | 0 | 1 | 0 | 0 | 3 | 2 | 2 | 5 | 35 | 1 | 0 | 3 | 1 | 2 | 0 | 3 | 6 | 0 | 1 | 3 | 2 | 2 | 
 | lupus | 6 | 8 | 0 | 1 | 0 | 2 | 1 | 0 | 2 | 26 | 3 | 3 | 14 | 1 | 0 | 4 | 6 | 0 | 3 | 2 | 4 | 1 | 
 | moles | 2 | 3 | 18 | 2 | 1 | 1 | 6 | 5 | 8 | 2 | 44 | 4 | 0 | 14 | 13 | 7 | 3 | 0 | 23 | 1 | 3 | 7 | 
 | psoriasis | 7 | 16 | 4 | 6 | 6 | 17 | 22 | 7 | 16 | 4 | 4 | 74 | 4 | 4 | 4 | 11 | 11 | 0 | 15 | 7 | 1 | 6 | 
 | rosacea | 6 | 13 | 0 | 0 | 1 | 0 | 4 | 0 | 0 | 3 | 0 | 3 | 90 | 0 | 0 | 3 | 0 | 0 | 3 | 0 | 0 | 0 | 
 | seborrh_keratoses | 0 | 4 | 21 | 0 | 0 | 0 | 0 | 3 | 0 | 1 | 6 | 1 | 0 | 76 | 16 | 2 | 1 | 2 | 7 | 0 | 0 | 2 | 
 | skincancer | 2 | 1 | 8 | 0 | 0 | 1 | 0 | 1 | 0 | 0 | 0 | 0 | 2 | 13 | 48 | 0 | 0 | 0 | 2 | 0 | 0 | 0 | 
 | sun_sunlight_damage | 0 | 1 | 0 | 2 | 0 | 4 | 3 | 3 | 0 | 2 | 0 | 1 | 0 | 0 | 0 | 35 | 6 | 3 | 1 | 1 | 9 | 0 | 
 | tinea | 4 | 1 | 0 | 4 | 4 | 6 | 5 | 3 | 7 | 2 | 1 | 3 | 2 | 1 | 0 | 4 | 52 | 2 | 1 | 2 | 3 | 0 | 
 | unknown_normal | 0 | 0 | 0 | 1 | 0 | 1 | 0 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 111 | 0 | 0 | 8 | 0 | 
 | vascular_tumors | 7 | 6 | 6 | 9 | 2 | 2 | 7 | 8 | 1 | 2 | 3 | 4 | 3 | 4 | 8 | 3 | 3 | 0 | 73 | 7 | 0 | 8 | 
 | vasculitis | 2 | 1 | 2 | 8 | 2 | 17 | 16 | 18 | 16 | 7 | 2 | 13 | 1 | 3 | 3 | 18 | 8 | 0 | 7 | 51 | 4 | 6 | 
 | vitiligo | 0 | 1 | 0 | 1 | 0 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 12 | 2 | 9 | 0 | 0 | 99 | 0 | 
 | warts | 5 | 9 | 7 | 6 | 3 | 1 | 10 | 12 | 9 | 0 | 6 | 11 | 2 | 3 | 5 | 7 | 12 | 4 | 14 | 1 | 1 | 85 | 
