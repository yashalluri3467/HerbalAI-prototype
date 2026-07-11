# Training benchmark — `skin_disease_mobilenetv2`

- Dataset: `skin_disease`
- Backbone: `mobilenetv2` (input 160x160)
- Device: CPU
- Accuracy: **0.4458**
- Macro-F1: **0.4376**
- Weighted-F1: 0.4493

## Per-class metrics

| Class | Precision | Recall | F1 | Support |
| --- | ---: | ---: | ---: | ---: |
| acne | 0.587 | 0.534 | 0.559 | 133 |
| actinic_keratosis | 0.562 | 0.423 | 0.483 | 149 |
| benign_tumors | 0.523 | 0.432 | 0.473 | 132 |
| bullous | 0.542 | 0.286 | 0.374 | 91 |
| candidiasis | 0.407 | 0.565 | 0.473 | 62 |
| drugeruption | 0.517 | 0.377 | 0.436 | 122 |
| eczema | 0.173 | 0.238 | 0.201 | 130 |
| infestations_bites | 0.295 | 0.226 | 0.256 | 115 |
| lichen | 0.456 | 0.293 | 0.356 | 123 |
| lupus | 0.189 | 0.362 | 0.249 | 69 |
| moles | 0.276 | 0.519 | 0.360 | 77 |
| psoriasis | 0.286 | 0.609 | 0.389 | 138 |
| rosacea | 0.759 | 0.638 | 0.693 | 138 |
| seborrh_keratoses | 0.516 | 0.457 | 0.485 | 140 |
| skincancer | 0.590 | 0.374 | 0.458 | 131 |
| sun_sunlight_damage | 0.491 | 0.197 | 0.281 | 137 |
| tinea | 0.459 | 0.324 | 0.380 | 139 |
| unknown_normal | 0.679 | 0.921 | 0.782 | 140 |
| vascular_tumors | 0.500 | 0.366 | 0.423 | 172 |
| vasculitis | 0.259 | 0.472 | 0.335 | 89 |
| vitiligo | 0.832 | 0.618 | 0.709 | 144 |
| warts | 0.431 | 0.523 | 0.473 | 132 |

## Confusion matrix

![confusion matrix](skin_disease_mobilenetv2/confusion_matrix.png)

 | acne | actinic_keratosis | benign_tumors | bullous | candidiasis | drugeruption | eczema | infestations_bites | lichen | lupus | moles | psoriasis | rosacea | seborrh_keratoses | skincancer | sun_sunlight_damage | tinea | unknown_normal | vascular_tumors | vasculitis | vitiligo | warts | 
 | acne | 71 | 2 | 1 | 0 | 0 | 3 | 7 | 1 | 0 | 7 | 1 | 1 | 12 | 2 | 1 | 4 | 3 | 0 | 3 | 0 | 2 | 0 | 
 | actinic_keratosis | 2 | 63 | 3 | 3 | 1 | 3 | 0 | 2 | 4 | 6 | 0 | 1 | 8 | 2 | 0 | 4 | 1 | 1 | 4 | 0 | 1 | 3 | 
 | benign_tumors | 2 | 0 | 57 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 3 | 1 | 1 | 16 | 24 | 1 | 0 | 0 | 2 | 0 | 0 | 1 | 
 | bullous | 3 | 2 | 1 | 26 | 1 | 5 | 1 | 1 | 2 | 1 | 0 | 0 | 0 | 0 | 0 | 2 | 1 | 1 | 0 | 0 | 1 | 0 | 
 | candidiasis | 1 | 3 | 0 | 3 | 35 | 3 | 3 | 2 | 7 | 1 | 0 | 6 | 0 | 1 | 1 | 1 | 8 | 0 | 1 | 3 | 0 | 7 | 
 | drugeruption | 6 | 4 | 0 | 7 | 2 | 46 | 1 | 4 | 2 | 2 | 0 | 1 | 1 | 1 | 0 | 4 | 3 | 1 | 1 | 1 | 2 | 0 | 
 | eczema | 6 | 3 | 0 | 4 | 2 | 7 | 31 | 14 | 17 | 5 | 2 | 10 | 1 | 1 | 3 | 17 | 16 | 0 | 14 | 13 | 3 | 10 | 
 | infestations_bites | 1 | 2 | 2 | 7 | 3 | 3 | 10 | 26 | 7 | 0 | 1 | 2 | 0 | 1 | 1 | 2 | 4 | 1 | 6 | 3 | 2 | 4 | 
 | lichen | 1 | 3 | 2 | 2 | 2 | 1 | 2 | 2 | 36 | 0 | 0 | 2 | 2 | 1 | 1 | 3 | 7 | 0 | 2 | 3 | 0 | 7 | 
 | lupus | 4 | 13 | 2 | 3 | 3 | 5 | 8 | 1 | 4 | 25 | 0 | 6 | 17 | 5 | 2 | 10 | 4 | 1 | 8 | 4 | 6 | 1 | 
 | moles | 2 | 3 | 13 | 0 | 0 | 2 | 3 | 8 | 6 | 1 | 40 | 3 | 0 | 18 | 7 | 9 | 1 | 0 | 19 | 1 | 2 | 7 | 
 | psoriasis | 12 | 15 | 2 | 8 | 8 | 19 | 29 | 12 | 11 | 8 | 6 | 84 | 5 | 3 | 5 | 14 | 17 | 0 | 14 | 12 | 0 | 10 | 
 | rosacea | 2 | 12 | 0 | 0 | 0 | 0 | 3 | 0 | 0 | 6 | 0 | 0 | 88 | 0 | 1 | 1 | 2 | 0 | 1 | 0 | 0 | 0 | 
 | seborrh_keratoses | 0 | 1 | 18 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 6 | 0 | 0 | 64 | 21 | 2 | 0 | 0 | 8 | 1 | 0 | 2 | 
 | skincancer | 0 | 2 | 12 | 0 | 0 | 0 | 0 | 2 | 1 | 0 | 2 | 0 | 0 | 11 | 49 | 0 | 0 | 0 | 4 | 0 | 0 | 0 | 
 | sun_sunlight_damage | 2 | 1 | 2 | 0 | 0 | 2 | 3 | 3 | 1 | 0 | 2 | 1 | 0 | 2 | 0 | 27 | 1 | 0 | 2 | 1 | 5 | 0 | 
 | tinea | 4 | 5 | 3 | 3 | 0 | 7 | 3 | 4 | 3 | 0 | 0 | 1 | 1 | 2 | 2 | 6 | 45 | 2 | 0 | 0 | 6 | 1 | 
 | unknown_normal | 2 | 1 | 2 | 3 | 0 | 3 | 3 | 6 | 3 | 3 | 1 | 1 | 0 | 1 | 1 | 4 | 6 | 129 | 2 | 0 | 19 | 0 | 
 | vascular_tumors | 6 | 6 | 1 | 5 | 1 | 2 | 4 | 7 | 2 | 0 | 3 | 1 | 2 | 5 | 3 | 2 | 0 | 0 | 63 | 4 | 2 | 7 | 
 | vasculitis | 4 | 4 | 2 | 13 | 1 | 9 | 8 | 16 | 13 | 3 | 3 | 7 | 0 | 2 | 4 | 13 | 5 | 1 | 6 | 42 | 3 | 3 | 
 | vitiligo | 0 | 1 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 8 | 5 | 3 | 0 | 0 | 89 | 0 | 
 | warts | 2 | 3 | 9 | 4 | 3 | 1 | 11 | 2 | 4 | 1 | 7 | 10 | 0 | 2 | 5 | 3 | 10 | 0 | 12 | 1 | 1 | 69 | 
