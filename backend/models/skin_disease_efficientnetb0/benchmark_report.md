# Training benchmark — `skin_disease_efficientnetb0`

- Dataset: `skin_disease`
- Backbone: `efficientnetb0` (input 160x160)
- Device: CPU
- Accuracy: **0.4835**
- Macro-F1: **0.4764**
- Weighted-F1: 0.4871

## Per-class metrics

| Class | Precision | Recall | F1 | Support |
| --- | ---: | ---: | ---: | ---: |
| acne | 0.612 | 0.594 | 0.603 | 133 |
| actinic_keratosis | 0.566 | 0.376 | 0.452 | 149 |
| benign_tumors | 0.611 | 0.439 | 0.511 | 132 |
| bullous | 0.500 | 0.462 | 0.480 | 91 |
| candidiasis | 0.372 | 0.613 | 0.463 | 62 |
| drugeruption | 0.516 | 0.271 | 0.355 | 122 |
| eczema | 0.220 | 0.269 | 0.242 | 130 |
| infestations_bites | 0.333 | 0.313 | 0.323 | 115 |
| lichen | 0.574 | 0.285 | 0.380 | 123 |
| lupus | 0.299 | 0.420 | 0.349 | 69 |
| moles | 0.309 | 0.558 | 0.398 | 77 |
| psoriasis | 0.412 | 0.478 | 0.443 | 138 |
| rosacea | 0.748 | 0.688 | 0.717 | 138 |
| seborrh_keratoses | 0.574 | 0.557 | 0.565 | 140 |
| skincancer | 0.639 | 0.473 | 0.544 | 131 |
| sun_sunlight_damage | 0.402 | 0.329 | 0.361 | 137 |
| tinea | 0.558 | 0.345 | 0.427 | 139 |
| unknown_normal | 0.842 | 0.800 | 0.821 | 140 |
| vascular_tumors | 0.500 | 0.471 | 0.485 | 172 |
| vasculitis | 0.336 | 0.449 | 0.385 | 89 |
| vitiligo | 0.797 | 0.681 | 0.734 | 144 |
| warts | 0.315 | 0.742 | 0.442 | 132 |

## Confusion matrix

![confusion matrix](skin_disease_efficientnetb0/confusion_matrix.png)

 | acne | actinic_keratosis | benign_tumors | bullous | candidiasis | drugeruption | eczema | infestations_bites | lichen | lupus | moles | psoriasis | rosacea | seborrh_keratoses | skincancer | sun_sunlight_damage | tinea | unknown_normal | vascular_tumors | vasculitis | vitiligo | warts | 
 | acne | 79 | 2 | 1 | 1 | 0 | 5 | 3 | 1 | 0 | 6 | 0 | 1 | 11 | 1 | 1 | 7 | 2 | 2 | 1 | 1 | 4 | 0 | 
 | actinic_keratosis | 1 | 56 | 1 | 1 | 1 | 4 | 3 | 1 | 1 | 1 | 1 | 4 | 4 | 3 | 5 | 3 | 1 | 1 | 1 | 1 | 2 | 3 | 
 | benign_tumors | 0 | 0 | 58 | 0 | 0 | 0 | 0 | 3 | 1 | 0 | 3 | 1 | 0 | 12 | 12 | 0 | 0 | 0 | 3 | 0 | 0 | 2 | 
 | bullous | 0 | 10 | 1 | 42 | 1 | 13 | 5 | 2 | 0 | 1 | 0 | 0 | 0 | 0 | 1 | 2 | 1 | 2 | 1 | 0 | 2 | 0 | 
 | candidiasis | 2 | 3 | 0 | 2 | 38 | 5 | 9 | 1 | 8 | 1 | 1 | 9 | 0 | 0 | 3 | 0 | 6 | 0 | 2 | 5 | 0 | 7 | 
 | drugeruption | 3 | 3 | 0 | 3 | 0 | 33 | 2 | 1 | 2 | 4 | 0 | 1 | 0 | 0 | 0 | 5 | 4 | 1 | 0 | 1 | 1 | 0 | 
 | eczema | 2 | 5 | 1 | 5 | 2 | 6 | 35 | 11 | 14 | 3 | 2 | 10 | 1 | 3 | 3 | 13 | 15 | 0 | 5 | 16 | 1 | 6 | 
 | infestations_bites | 2 | 1 | 3 | 4 | 2 | 9 | 4 | 36 | 5 | 3 | 5 | 1 | 0 | 1 | 2 | 3 | 10 | 3 | 6 | 4 | 3 | 1 | 
 | lichen | 0 | 1 | 1 | 0 | 2 | 4 | 0 | 3 | 35 | 1 | 0 | 1 | 1 | 1 | 0 | 4 | 2 | 0 | 0 | 1 | 2 | 2 | 
 | lupus | 2 | 11 | 0 | 3 | 1 | 2 | 3 | 3 | 4 | 29 | 3 | 5 | 13 | 0 | 1 | 5 | 5 | 0 | 1 | 0 | 5 | 1 | 
 | moles | 3 | 3 | 11 | 1 | 1 | 1 | 4 | 4 | 6 | 0 | 43 | 1 | 0 | 9 | 8 | 7 | 3 | 2 | 25 | 2 | 2 | 3 | 
 | psoriasis | 5 | 12 | 2 | 4 | 0 | 9 | 10 | 1 | 10 | 5 | 4 | 66 | 1 | 3 | 1 | 8 | 6 | 1 | 4 | 3 | 2 | 3 | 
 | rosacea | 5 | 10 | 0 | 0 | 1 | 0 | 3 | 0 | 1 | 3 | 0 | 2 | 95 | 0 | 1 | 2 | 0 | 0 | 3 | 1 | 0 | 0 | 
 | seborrh_keratoses | 0 | 1 | 24 | 0 | 0 | 0 | 0 | 3 | 3 | 0 | 4 | 0 | 0 | 78 | 14 | 0 | 0 | 1 | 5 | 2 | 0 | 1 | 
 | skincancer | 1 | 2 | 12 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 16 | 62 | 0 | 0 | 0 | 3 | 0 | 0 | 0 | 
 | sun_sunlight_damage | 3 | 7 | 0 | 2 | 0 | 7 | 5 | 2 | 4 | 2 | 1 | 4 | 0 | 1 | 1 | 45 | 6 | 3 | 3 | 2 | 13 | 1 | 
 | tinea | 3 | 1 | 1 | 3 | 1 | 4 | 4 | 6 | 0 | 1 | 0 | 4 | 1 | 1 | 0 | 3 | 48 | 1 | 1 | 1 | 2 | 0 | 
 | unknown_normal | 1 | 1 | 0 | 0 | 0 | 1 | 2 | 1 | 3 | 0 | 0 | 0 | 0 | 0 | 1 | 1 | 4 | 112 | 0 | 2 | 4 | 0 | 
 | vascular_tumors | 6 | 5 | 4 | 3 | 3 | 2 | 5 | 9 | 2 | 4 | 2 | 4 | 6 | 7 | 9 | 2 | 2 | 0 | 81 | 2 | 0 | 4 | 
 | vasculitis | 2 | 1 | 1 | 3 | 2 | 9 | 11 | 12 | 9 | 3 | 1 | 8 | 1 | 0 | 0 | 8 | 2 | 0 | 5 | 40 | 1 | 0 | 
 | vitiligo | 0 | 2 | 0 | 2 | 0 | 2 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 6 | 3 | 9 | 0 | 0 | 98 | 0 | 
 | warts | 13 | 12 | 11 | 12 | 7 | 6 | 21 | 15 | 15 | 2 | 6 | 16 | 4 | 4 | 6 | 13 | 19 | 2 | 22 | 5 | 2 | 98 | 
