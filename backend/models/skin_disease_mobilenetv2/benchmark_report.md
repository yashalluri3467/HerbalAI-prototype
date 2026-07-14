# Training benchmark — `skin_disease_mobilenetv2`

- Dataset: `skin_disease`
- Backbone: `mobilenetv2` (input 160x160)
- Device: CPU
- Accuracy: **0.4787**
- Macro-F1: **0.4736**
- Weighted-F1: 0.4832

## Per-class metrics

| Class | Precision | Recall | F1 | Support |
| --- | ---: | ---: | ---: | ---: |
| acne | 0.575 | 0.549 | 0.561 | 133 |
| actinic_keratosis | 0.646 | 0.416 | 0.506 | 149 |
| benign_tumors | 0.583 | 0.424 | 0.491 | 132 |
| bullous | 0.533 | 0.352 | 0.424 | 91 |
| candidiasis | 0.506 | 0.661 | 0.573 | 62 |
| drugeruption | 0.500 | 0.434 | 0.465 | 122 |
| eczema | 0.174 | 0.223 | 0.195 | 130 |
| infestations_bites | 0.439 | 0.374 | 0.404 | 115 |
| lichen | 0.612 | 0.333 | 0.432 | 123 |
| lupus | 0.286 | 0.319 | 0.301 | 69 |
| moles | 0.275 | 0.571 | 0.371 | 77 |
| psoriasis | 0.314 | 0.652 | 0.423 | 138 |
| rosacea | 0.806 | 0.573 | 0.669 | 138 |
| seborrh_keratoses | 0.571 | 0.457 | 0.508 | 140 |
| skincancer | 0.631 | 0.405 | 0.493 | 131 |
| sun_sunlight_damage | 0.525 | 0.226 | 0.316 | 137 |
| tinea | 0.421 | 0.324 | 0.366 | 139 |
| unknown_normal | 0.815 | 0.914 | 0.862 | 140 |
| vascular_tumors | 0.442 | 0.512 | 0.474 | 172 |
| vasculitis | 0.265 | 0.483 | 0.343 | 89 |
| vitiligo | 0.795 | 0.674 | 0.729 | 144 |
| warts | 0.442 | 0.606 | 0.511 | 132 |

## Confusion matrix

![confusion matrix](skin_disease_mobilenetv2/confusion_matrix.png)

 | acne | actinic_keratosis | benign_tumors | bullous | candidiasis | drugeruption | eczema | infestations_bites | lichen | lupus | moles | psoriasis | rosacea | seborrh_keratoses | skincancer | sun_sunlight_damage | tinea | unknown_normal | vascular_tumors | vasculitis | vitiligo | warts | 
 | acne | 73 | 5 | 1 | 0 | 1 | 3 | 7 | 2 | 0 | 4 | 1 | 0 | 14 | 3 | 1 | 3 | 2 | 1 | 3 | 0 | 3 | 0 | 
 | actinic_keratosis | 1 | 62 | 0 | 1 | 1 | 2 | 0 | 2 | 2 | 6 | 0 | 1 | 6 | 2 | 0 | 4 | 2 | 0 | 1 | 1 | 0 | 2 | 
 | benign_tumors | 1 | 0 | 56 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 3 | 0 | 1 | 16 | 18 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 
 | bullous | 4 | 4 | 0 | 32 | 1 | 7 | 0 | 0 | 2 | 3 | 0 | 1 | 0 | 0 | 0 | 2 | 2 | 0 | 0 | 1 | 0 | 1 | 
 | candidiasis | 1 | 1 | 0 | 2 | 41 | 2 | 2 | 1 | 6 | 1 | 0 | 6 | 0 | 1 | 1 | 0 | 6 | 0 | 3 | 2 | 0 | 5 | 
 | drugeruption | 6 | 6 | 0 | 10 | 2 | 53 | 4 | 4 | 2 | 1 | 0 | 1 | 1 | 1 | 0 | 3 | 6 | 2 | 2 | 0 | 2 | 0 | 
 | eczema | 5 | 4 | 0 | 6 | 0 | 8 | 29 | 14 | 11 | 3 | 1 | 10 | 1 | 2 | 4 | 13 | 19 | 0 | 9 | 17 | 2 | 9 | 
 | infestations_bites | 0 | 1 | 3 | 6 | 0 | 3 | 9 | 43 | 5 | 0 | 1 | 1 | 0 | 1 | 3 | 6 | 3 | 0 | 5 | 2 | 2 | 4 | 
 | lichen | 1 | 2 | 1 | 0 | 2 | 0 | 3 | 0 | 41 | 0 | 1 | 1 | 2 | 0 | 0 | 2 | 4 | 0 | 0 | 2 | 2 | 3 | 
 | lupus | 2 | 5 | 2 | 1 | 0 | 3 | 3 | 1 | 2 | 22 | 1 | 4 | 15 | 1 | 0 | 5 | 2 | 0 | 2 | 2 | 3 | 1 | 
 | moles | 4 | 6 | 10 | 1 | 0 | 3 | 1 | 5 | 10 | 2 | 44 | 3 | 0 | 19 | 6 | 13 | 4 | 0 | 16 | 2 | 4 | 7 | 
 | psoriasis | 11 | 18 | 2 | 7 | 6 | 13 | 31 | 11 | 14 | 9 | 3 | 90 | 8 | 4 | 5 | 12 | 13 | 1 | 11 | 9 | 1 | 8 | 
 | rosacea | 3 | 8 | 1 | 0 | 0 | 0 | 1 | 0 | 1 | 3 | 0 | 0 | 79 | 0 | 0 | 1 | 0 | 0 | 1 | 0 | 0 | 0 | 
 | seborrh_keratoses | 0 | 1 | 14 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 4 | 0 | 0 | 64 | 20 | 1 | 1 | 0 | 5 | 0 | 0 | 1 | 
 | skincancer | 0 | 1 | 15 | 0 | 0 | 0 | 0 | 1 | 1 | 0 | 0 | 0 | 0 | 11 | 53 | 0 | 0 | 0 | 1 | 0 | 1 | 0 | 
 | sun_sunlight_damage | 1 | 2 | 1 | 0 | 0 | 1 | 3 | 1 | 0 | 3 | 3 | 2 | 1 | 1 | 0 | 31 | 1 | 0 | 2 | 1 | 5 | 0 | 
 | tinea | 3 | 4 | 2 | 3 | 1 | 5 | 5 | 3 | 7 | 2 | 1 | 4 | 3 | 0 | 0 | 7 | 45 | 2 | 3 | 1 | 3 | 3 | 
 | unknown_normal | 1 | 0 | 1 | 1 | 0 | 2 | 1 | 3 | 1 | 0 | 1 | 0 | 0 | 1 | 1 | 1 | 1 | 128 | 1 | 0 | 13 | 0 | 
 | vascular_tumors | 8 | 7 | 11 | 7 | 3 | 6 | 7 | 6 | 2 | 4 | 6 | 2 | 5 | 5 | 8 | 5 | 2 | 2 | 88 | 6 | 3 | 6 | 
 | vasculitis | 3 | 5 | 4 | 9 | 1 | 9 | 13 | 10 | 14 | 4 | 2 | 3 | 1 | 4 | 3 | 13 | 9 | 1 | 7 | 43 | 2 | 2 | 
 | vitiligo | 1 | 1 | 0 | 0 | 0 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 1 | 9 | 7 | 3 | 0 | 0 | 97 | 0 | 
 | warts | 4 | 6 | 8 | 5 | 3 | 1 | 10 | 7 | 2 | 2 | 5 | 9 | 0 | 4 | 7 | 6 | 10 | 0 | 11 | 0 | 1 | 80 | 
