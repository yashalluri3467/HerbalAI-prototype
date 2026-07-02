HERB_DATABASE = {
    "Neem": {
        "name": "Neem",
        "botanical_name": "Azadirachta indica",
        "family": "Meliaceae",
        "active_compounds": ["Nimbin", "Azadirachtin", "Nimbidin", "Gedunin", "Quercetin"],
        "phytochemicals": ["Limonoids", "Flavonoids", "Triterpenoids", "Beta-sitosterol"],
        "benefits": ["Antibacterial", "Anti-inflammatory", "Controls excess oil", "Reduces acne-causing bacteria", "Promotes skin healing"],
        "side_effects": ["May cause mild dryness or irritation on extremely sensitive skin if used undiluted"],
        "contraindications": ["Extremely dry skin conditions (use with a hydrating carrier)"],
        "evidence_level": "High (Multiple Clinical Trials)",
        "research_papers": [
            "Alzohairy MA. Therapeutics Role of Azadirachta indica (Neem) and Their Active Constituents in Diseases Prevention and Treatment. Evid Based Complement Alternat Med. 2016.",
            "Kumar VS, Navaratnam V. Neem (Azadirachta indica): Prehistory to contemporary medicinal uses to humankind. Asian Pac J Trop Biomed. 2013."
        ],
        "preparation_method": "Grind fresh neem leaves with water to form a paste and apply to affected areas, or dilute neem oil (2-3 drops) in coconut oil.",
        "skin_types": ["Oily", "Acne-prone", "Combination"],
        "disease_mapping": {
            "Acne": {"efficacy": 96, "weight": 0.98},
            "Dermatitis": {"efficacy": 85, "weight": 0.88},
            "Psoriasis": {"efficacy": 80, "weight": 0.82},
            "Fungal Infection": {"efficacy": 90, "weight": 0.92}
        }
    },
    "Aloe Vera": {
        "name": "Aloe Vera",
        "botanical_name": "Aloe barbadensis Miller",
        "family": "Asphodelaceae",
        "active_compounds": ["Aloin", "Aloesin", "Al浸-emodin", "Acemannan", "Salicylic Acid"],
        "phytochemicals": ["Anthraquinones", "Polysaccharides", "Sterols", "Saponins"],
        "benefits": ["Dry skin relief", "Soothes sunburn", "Speeds up wound healing", "Skin hydration", "Anti-inflammatory"],
        "side_effects": ["Rare allergic contact dermatitis in sensitive individuals"],
        "contraindications": ["Open deep surgical wounds"],
        "evidence_level": "High (Widely Researched)",
        "research_papers": [
            "Surjushe A, Vasani R, Saple DG. Aloe vera: a short review. Indian J Dermatol. 2008.",
            "Hekmatpou D, et al. Effect of Aloe Vera Clinical Trials on Skin Prevention and Healing: A Systematic Review. Iran J Med Sci. 2019."
        ],
        "preparation_method": "Extract fresh gel from an Aloe leaf and apply directly to the skin. No dilution required.",
        "skin_types": ["Dry", "Sensitive", "All", "Sunburnt"],
        "disease_mapping": {
            "Dry Skin": {"efficacy": 98, "weight": 0.99},
            "Eczema": {"efficacy": 88, "weight": 0.90},
            "Dermatitis": {"efficacy": 85, "weight": 0.87},
            "Healthy Skin": {"efficacy": 95, "weight": 0.96}
        }
    },
    "Turmeric": {
        "name": "Turmeric",
        "botanical_name": "Curcuma longa",
        "family": "Zingiberaceae",
        "active_compounds": ["Curcumin", "Demethoxycurcumin", "Bisdemethoxycurcumin", "Turmerone"],
        "phytochemicals": ["Diarylheptanoids", "Sesquiterpenes", "Curcuminoids"],
        "benefits": ["Reduces pigmentation", "Fades acne scars", "Skin brightening", "Anti-inflammatory", "Antioxidant protection"],
        "side_effects": ["Temporary yellow skin staining", "Mild contact dermatitis in rare cases"],
        "contraindications": ["None major, but avoid applying to fresh open bleeding wounds"],
        "evidence_level": "High (Strong Evidence)",
        "research_papers": [
            "Vaughn AR, Branum A, Sivamani RK. Effects of Turmeric (Curcuma longa) on Skin Health: A Systematic Review of the Clinical Evidence. Phytother Res. 2016."
        ],
        "preparation_method": "Mix 1/2 teaspoon of turmeric powder with yogurt or honey to form a paste. Apply for 10-15 minutes and rinse.",
        "skin_types": ["Combination", "Pigmented", "Dull"],
        "disease_mapping": {
            "Pigmentation": {"efficacy": 94, "weight": 0.96},
            "Acne": {"efficacy": 88, "weight": 0.90},
            "Melasma": {"efficacy": 92, "weight": 0.95},
            "Vitiligo": {"efficacy": 75, "weight": 0.78}
        }
    },
    "Tulsi": {
        "name": "Tulsi",
        "botanical_name": "Ocimum tenuiflorum",
        "family": "Lamiaceae",
        "active_compounds": ["Eugenol", "Ursolic Acid", "Carvacrol", "Linalool"],
        "phytochemicals": ["Tannins", "Flavonoids", "Terpenoids"],
        "benefits": ["Clears acne", "Anti-microbial skin protection", "Soothes skin infections", "Balances oily skin"],
        "side_effects": ["Generally very safe; mild warming sensation on application"],
        "contraindications": ["None reported for topical applications"],
        "evidence_level": "Medium-High",
        "research_papers": [
            "Cohen MM. Tulsi - Ocimum sanctum: A herb for all reasons. J Ayurveda Integr Med. 2014."
        ],
        "preparation_method": "Crush tulsi leaves and extract the juice. Apply this juice directly using a cotton ball to acne lesions.",
        "skin_types": ["Oily", "Acne-prone"],
        "disease_mapping": {
            "Acne": {"efficacy": 92, "weight": 0.95},
            "Fungal Infection": {"efficacy": 80, "weight": 0.85},
            "Healthy Skin": {"efficacy": 85, "weight": 0.88}
        }
    },
    "Amla": {
        "name": "Amla",
        "botanical_name": "Phyllanthus emblica",
        "family": "Phyllanthaceae",
        "active_compounds": ["Vitamin C (Ascorbic Acid)", "Ellagic Acid", "Gallic Acid", "Emblicanin"],
        "phytochemicals": ["Tannins", "Polyphenols", "Flavonoids"],
        "benefits": ["Anti-aging", "Promotes skin glow", "Supports collagen production", "Fights oxidative stress"],
        "side_effects": ["Highly acidic; might cause mild tingling on sensitive skin"],
        "contraindications": ["Extremely sensitive or peeled skin"],
        "evidence_level": "Medium (Strong Antioxidant Action)",
        "research_papers": [
            "Fujii T, et al. Amla (Emblica officinalis Gaertn.) extract promotes procollagen production and inhibits matrix metalloproteinase-1 in human skin fibroblasts. J Ethnopharmacol. 2008."
        ],
        "preparation_method": "Mix amla powder with raw honey or rose water, apply as a mask for 10 minutes, then wash off.",
        "skin_types": ["Aging", "Dull", "Normal"],
        "disease_mapping": {
            "Wrinkles": {"efficacy": 91, "weight": 0.93},
            "Pigmentation": {"efficacy": 82, "weight": 0.85},
            "Healthy Skin": {"efficacy": 90, "weight": 0.92}
        }
    },
    "Harra": {
        "name": "Harra",
        "botanical_name": "Terminalia chebula",
        "family": "Combretaceae",
        "active_compounds": ["Chebulinic Acid", "Chebulagic Acid", "Corilagin", "Gallic Acid"],
        "phytochemicals": ["Hydrolyzable Tannins", "Polyphenols"],
        "benefits": ["Wound healing", "Soothes skin infections", "Antioxidant activity", "Astringent properties"],
        "side_effects": ["Can cause dryness due to high tannin content"],
        "contraindications": ["Extremely dry skin (always combine with a lipid carrier)"],
        "evidence_level": "Medium",
        "research_papers": [
            "Bag A, et al. The development of Terminalia chebula Retz. (Combretaceae) in clinical research. Asian Pac J Trop Biomed. 2013."
        ],
        "preparation_method": "Make a fine paste of Harra powder with water and apply as a spot treatment on minor wounds or rashes.",
        "skin_types": ["Oily", "Infected", "Normal"],
        "disease_mapping": {
            "Dermatitis": {"efficacy": 80, "weight": 0.82},
            "Eczema": {"efficacy": 75, "weight": 0.78},
            "Fungal Infection": {"efficacy": 82, "weight": 0.84}
        }
    },
    "Bahera": {
        "name": "Bahera",
        "botanical_name": "Terminalia bellirica",
        "family": "Combretaceae",
        "active_compounds": ["Bellericanin", "Gallic Acid", "Ellagic Acid", "Chebulinic Acid"],
        "phytochemicals": ["Tannins", "Saponins", "Cardiac Glycosides"],
        "benefits": ["Skin detoxification", "Antioxidant protection", "Reduces swelling and redness"],
        "side_effects": ["Mild drying effect"],
        "contraindications": ["None reported for external use"],
        "evidence_level": "Medium",
        "research_papers": [
            "Saraswathi V, et al. Antioxidant and anti-inflammatory activity of Terminalia bellirica. Journal of Pharmacy Research. 2012."
        ],
        "preparation_method": "Mix Bahera powder with warm water, apply as a paste on inflamed or swollen skin patches.",
        "skin_types": ["Normal", "Congested"],
        "disease_mapping": {
            "Dermatitis": {"efficacy": 78, "weight": 0.80},
            "Eczema": {"efficacy": 76, "weight": 0.79}
        }
    },
    "Giloy": {
        "name": "Giloy",
        "botanical_name": "Tinospora cordifolia",
        "family": "Menispermaceae",
        "active_compounds": ["Tinosporide", "Cordifolide", "Berberine", "Gilonin"],
        "phytochemicals": ["Alkaloids", "Diterpenoid Lactones", "Glycosides", "Steroids"],
        "benefits": ["Soothes skin allergies", "Anti-inflammatory", "Manages autoimmune skin disorders", "Purifies blood topically"],
        "side_effects": ["Generally extremely safe; no significant topical side effects"],
        "contraindications": ["None major for topical application"],
        "evidence_level": "Medium-High",
        "research_papers": [
            "Saha S, Ghosh S. Tinospora cordifolia: One plant, many roles. Anc Sci Life. 2012."
        ],
        "preparation_method": "Boil Giloy stems in water to prepare a decoction, let it cool, and wash the affected skin areas.",
        "skin_types": ["Sensitive", "Allergy-prone"],
        "disease_mapping": {
            "Eczema": {"efficacy": 86, "weight": 0.89},
            "Psoriasis": {"efficacy": 88, "weight": 0.90},
            "Dermatitis": {"efficacy": 84, "weight": 0.86}
        }
    },
    "Mahua": {
        "name": "Mahua",
        "botanical_name": "Madhuca longifolia",
        "family": "Sapotaceae",
        "active_compounds": ["Mahuasin", "Mowrin", "Oleic Acid", "Linoleic Acid"],
        "phytochemicals": ["Saponins", "Triterpenoids", "Fatty Acids"],
        "benefits": ["Deeply moisturizes dry skin", "Soothes skin irritation", "Promotes wound healing"],
        "side_effects": ["Can feel heavy or greasy; may clog pores on oily skin"],
        "contraindications": ["Active acne-prone skin (due to high lipid content)"],
        "evidence_level": "Medium-Low (Traditional Usage)",
        "research_papers": [
            "Ramadan MF, et al. Bioactive lipids and phytochemicals of Madhuca longifolia seed oil. Food Chemistry. 2006."
        ],
        "preparation_method": "Apply cold-pressed Mahua seed oil directly onto patches of dry skin, or mix with beeswax to form a salve.",
        "skin_types": ["Dry", "Very Dry", "Chapped"],
        "disease_mapping": {
            "Dry Skin": {"efficacy": 95, "weight": 0.94},
            "Eczema": {"efficacy": 80, "weight": 0.82}
        }
    },
    "Karanj": {
        "name": "Karanj",
        "botanical_name": "Pongamia pinnata",
        "family": "Fabaceae",
        "active_compounds": ["Karanjin", "Pongamol", "Kanjone", "Pongapin"],
        "phytochemicals": ["Furanoflavonoids", "Chalcones", "Flavones"],
        "benefits": ["Eczema relief", "Psoriasis management", "Antifungal activity", "Heals chronic skin diseases"],
        "side_effects": ["Strong smell; may cause warmth or mild burning sensation initially"],
        "contraindications": ["Do not apply to open bleeding lesions"],
        "evidence_level": "Medium-High",
        "research_papers": [
            "Ramesh M, et al. Antifungal and antibacterial activity of Pongamia pinnata (Karanj) seed oil. Fitoterapia. 2002."
        ],
        "preparation_method": "Dilute Karanj oil with neem oil or coconut oil in a 1:5 ratio and apply to affected patches.",
        "skin_types": ["Dry", "Scaly", "Infected"],
        "disease_mapping": {
            "Eczema": {"efficacy": 92, "weight": 0.94},
            "Psoriasis": {"efficacy": 90, "weight": 0.92},
            "Fungal Infection": {"efficacy": 94, "weight": 0.95}
        }
    },
    "Palash": {
        "name": "Palash",
        "botanical_name": "Butea monosperma",
        "family": "Fabaceae",
        "active_compounds": ["Butin", "Butrin", "Isobutrin", "Palasitrin"],
        "phytochemicals": ["Flavonoids", "Glucosides", "Alkaloids"],
        "benefits": ["Treats skin infections", "Promotes wound healing", "Anti-inflammatory"],
        "side_effects": ["Palash flower extract may dye the skin temporarily orange"],
        "contraindications": ["None reported"],
        "evidence_level": "Medium-Low",
        "research_papers": [
            "Mishra M, et al. Butea monosperma (Palash): A review on its phytochemical and pharmacological profile. Int J Phytomed. 2011."
        ],
        "preparation_method": "Infuse Palash flowers in hot water to create a soothing rinse, or crush flowers into a paste.",
        "skin_types": ["Normal", "Sensitive", "Infected"],
        "disease_mapping": {
            "Dermatitis": {"efficacy": 82, "weight": 0.83},
            "Eczema": {"efficacy": 80, "weight": 0.80}
        }
    },
    "Moringa": {
        "name": "Moringa",
        "botanical_name": "Moringa oleifera",
        "family": "Moringaceae",
        "active_compounds": ["Zeatin", "Quercetin", "Kaempferol", "Moringine", "Isothiocyanates"],
        "phytochemicals": ["Glucosinolates", "Polyphenols", "Vitamins A, C, and E"],
        "benefits": ["Skin nourishment", "Deeply hydrates dry skin", "Antioxidant protection", "Anti-aging properties"],
        "side_effects": ["Very well tolerated; extremely low incidence of reactions"],
        "contraindications": ["None"],
        "evidence_level": "High",
        "research_papers": [
            "Ali A, et al. Enhancement of human skin facial revitalization by moringa leaf extract cream. Postepy Dermatol Alergol. 2014."
        ],
        "preparation_method": "Apply cold-pressed Moringa seed oil as a moisturizer or face oil, or make a leaf powder paste.",
        "skin_types": ["Dry", "Aging", "Normal"],
        "disease_mapping": {
            "Dry Skin": {"efficacy": 94, "weight": 0.95},
            "Wrinkles": {"efficacy": 88, "weight": 0.90},
            "Healthy Skin": {"efficacy": 92, "weight": 0.93}
        }
    },
    "Hibiscus": {
        "name": "Hibiscus",
        "botanical_name": "Hibiscus rosa-sinensis",
        "family": "Malvaceae",
        "active_compounds": ["Anthocyanins", "Citric Acid", "Malic Acid", "Mucilage"],
        "phytochemicals": ["Alpha-hydroxy acids (AHAs)", "Flavonoids", "Organic Acids"],
        "benefits": ["Anti-aging (natural botox effect)", "Improves skin elasticity", "Exfoliates gently to reduce wrinkles"],
        "side_effects": ["Mild tingling due to natural fruit acids"],
        "contraindications": ["Raw applying on sunburns or fresh peeling skin"],
        "evidence_level": "Medium",
        "research_papers": [
            "Nanda A, et al. Evaluation of cosmetic potential of Hibiscus rosa-sinensis petals. Journal of Cosmetic Dermatology. 2019."
        ],
        "preparation_method": "Crush fresh hibiscus petals with a little yogurt, apply to face for 15 minutes, then rinse with warm water.",
        "skin_types": ["Aging", "Normal", "Dull"],
        "disease_mapping": {
            "Wrinkles": {"efficacy": 93, "weight": 0.95},
            "Pigmentation": {"efficacy": 84, "weight": 0.86},
            "Healthy Skin": {"efficacy": 90, "weight": 0.91}
        }
    },
    "Ashwagandha": {
        "name": "Ashwagandha",
        "botanical_name": "Withania somnifera",
        "family": "Solanaceae",
        "active_compounds": ["Withaferin A", "Withanolides", "Sitoindosides", "Somniferine"],
        "phytochemicals": ["Alkaloids", "Steroidal Lactones"],
        "benefits": ["Skin rejuvenation", "Fades wrinkles", "Stimulates collagen", "Calms skin stress & cortisol impact"],
        "side_effects": ["Very rare contact allergy"],
        "contraindications": ["None reported for topical use"],
        "evidence_level": "Medium-High",
        "research_papers": [
            "Sikandar M, et al. Ashwagandha (Withania somnifera) in skincare: Clinical studies and phytochemical insights. Phytotherapy Letters. 2021."
        ],
        "preparation_method": "Mix Ashwagandha root powder with ghee or honey and apply to areas showing fine lines or fatigue.",
        "skin_types": ["Aging", "Stressed", "All"],
        "disease_mapping": {
            "Wrinkles": {"efficacy": 90, "weight": 0.92},
            "Dry Skin": {"efficacy": 84, "weight": 0.85},
            "Healthy Skin": {"efficacy": 88, "weight": 0.90}
        }
    },
    "Bael": {
        "name": "Bael",
        "botanical_name": "Aegle marmelos",
        "family": "Rutaceae",
        "active_compounds": ["Marmelosin", "Limonene", "Luvangetin", "Aegeline"],
        "phytochemicals": ["Coumarins", "Alkaloids", "Tannins"],
        "benefits": ["Soothes skin irritation", "Speeds up wound healing", "Anti-inflammatory relief"],
        "side_effects": ["May cause slight dryness if used excessively"],
        "contraindications": ["Very dry skin without mixing with oils"],
        "evidence_level": "Medium-Low",
        "research_papers": [
            "Bhalodia NR, Shukla VJ. Antibacterial and wound healing properties of Aegle marmelos fruit extracts. J Adv Pharm Technol Res. 2011."
        ],
        "preparation_method": "Mash the pulp of ripe Bael fruit, apply to irritated skin patch, let sit for 15 minutes, wash off.",
        "skin_types": ["Normal", "Irritated"],
        "disease_mapping": {
            "Dermatitis": {"efficacy": 83, "weight": 0.85},
            "Eczema": {"efficacy": 78, "weight": 0.80}
        }
    },
    "Arjun": {
        "name": "Arjun",
        "botanical_name": "Terminalia arjuna",
        "family": "Combretaceae",
        "active_compounds": ["Arjunic Acid", "Arjunetin", "Arjunolone", "Beta-sitosterol"],
        "phytochemicals": ["Triterpenoid Saponins", "Flavonoids", "Tannins"],
        "benefits": ["Skin barrier repair", "Antioxidant protection", "Improves skin microcirculation", "Tightens sagging skin"],
        "side_effects": ["Mild astringent drying effect"],
        "contraindications": ["None reported"],
        "evidence_level": "Medium",
        "research_papers": [
            "Chaudhari M, et al. Terminalia arjuna bark extract: barrier repair and microcirculation benefits in skin care. Journal of Ethnopharmacology. 2014."
        ],
        "preparation_method": "Mix Arjun bark powder with honey and milk to make a skin paste. Apply twice a week.",
        "skin_types": ["Aging", "Damaged", "Normal"],
        "disease_mapping": {
            "Wrinkles": {"efficacy": 86, "weight": 0.88},
            "Dry Skin": {"efficacy": 80, "weight": 0.82},
            "Healthy Skin": {"efficacy": 85, "weight": 0.86}
        }
    },
    "Chironji": {
        "name": "Chironji",
        "botanical_name": "Buchanania lanzan",
        "family": "Anacardiaceae",
        "active_compounds": ["Oleic Acid", "Linoleic Acid", "Myristic Acid", "Gallic Acid"],
        "phytochemicals": ["Fatty Acids", "Tannins", "Flavonoids"],
        "benefits": ["Deep skin nourishment", "Softens and moisturizes skin", "Reduces blemishes and spots"],
        "side_effects": ["Comedogenic risk for highly oily acne-prone skin"],
        "contraindications": ["Oily acne-prone skin types"],
        "evidence_level": "Medium-Low",
        "research_papers": [
            "Siddiqui AA, et al. Phytochemical and therapeutic potential of Buchanania lanzan (Chironji) seeds. Journal of Natural Remedies. 2015."
        ],
        "preparation_method": "Grind Chironji seeds with milk to make a paste, apply on skin for soft texture and fading of dry patches.",
        "skin_types": ["Dry", "Flaky", "Normal"],
        "disease_mapping": {
            "Dry Skin": {"efficacy": 92, "weight": 0.93},
            "Pigmentation": {"efficacy": 78, "weight": 0.80}
        }
    },
    "Bhringraj": {
        "name": "Bhringraj",
        "botanical_name": "Eclipta prostrata",
        "family": "Asteraceae",
        "active_compounds": ["Wedelolactone", "Demethylwedelolactone", "Ecliptine", "Stigmasterol"],
        "phytochemicals": ["Coumestans", "Alkaloids", "Thiophenes"],
        "benefits": ["Skin regeneration and repair", "Soothes skin inflammation", "Heals minor wounds and burns", "Antiallergic action"],
        "side_effects": ["Very high tolerance rate; no common side effects reported"],
        "contraindications": ["None reported"],
        "evidence_level": "Medium-High",
        "research_papers": [
            "Tewtrakul S, et al. Anti-inflammatory and wound healing activities of Eclipta prostrata. Journal of Ethnopharmacology. 2011."
        ],
        "preparation_method": "Extract juice from crushed fresh Bhringraj leaves and apply to wounds, or apply Bhringraj leaf powder paste.",
        "skin_types": ["Normal", "Sensitive", "Damaged"],
        "disease_mapping": {
            "Dermatitis": {"efficacy": 88, "weight": 0.90},
            "Eczema": {"efficacy": 84, "weight": 0.85},
            "Healthy Skin": {"efficacy": 85, "weight": 0.87}
        }
    }
}

def get_herb_by_name(name):
    if not name:
        return {
            "name": "Unknown",
            "botanical_name": "Unknown species",
            "family": "Unknown family",
            "active_compounds": ["Natural Phytochemicals"],
            "phytochemicals": ["Bioflavonoids", "Antioxidants"],
            "benefits": ["General skin soothing", "Antioxidant support"],
            "side_effects": ["None reported for general topical use"],
            "contraindications": ["None reported"],
            "evidence_level": "Traditional/General literature",
            "research_papers": [],
            "preparation_method": "Clean the leaf, crush to extract juice or make a paste, and apply topically.",
            "skin_types": ["All"],
            "disease_mapping": {}
        }

    # 1. Direct exact match
    if name in HERB_DATABASE:
        return HERB_DATABASE[name]

    # 2. Case-insensitive and synonym matching
    import re
    def normalize(val):
        return re.sub(r'[^a-zA-Z0-9]', '', val).lower()

    mapping = {
        "neem": "Neem",
        "azadirachtaindica": "Neem",
        "aloevera": "Aloe Vera",
        "aloe": "Aloe Vera",
        "turmeric": "Turmeric",
        "curcumalonga": "Turmeric",
        "tulsi": "Tulsi",
        "ocimumtenuiflorum": "Tulsi",
        "amla": "Amla",
        "phyllanthusemblica": "Amla",
        "harra": "Harra",
        "terminaliachebula": "Harra",
        "bahera": "Bahera",
        "terminaliabellirica": "Bahera",
        "giloy": "Giloy",
        "tinosporacordifolia": "Giloy",
        "mahua": "Mahua",
        "madhucalongifolia": "Mahua",
        "karanj": "Karanj",
        "pongamiapinnata": "Karanj",
        "palash": "Palash",
        "buteamonosperma": "Palash",
        "moringa": "Moringa",
        "moringaoleifera": "Moringa",
        "hibiscus": "Hibiscus",
        "hibiscusrosasinensis": "Hibiscus",
        "ashwagandha": "Ashwagandha",
        "withaniasomnifera": "Ashwagandha",
        "bael": "Bael",
        "aeglemarmelos": "Bael",
        "arjun": "Arjun",
        "terminaliaarjuna": "Arjun",
        "chironji": "Chironji",
        "buchananalanzan": "Chironji",
        "bhringraj": "Bhringraj",
        "bringaraja": "Bhringraj",
        "ecliptaprostrata": "Bhringraj"
    }

    norm_query = normalize(name)
    if norm_query in mapping:
        return HERB_DATABASE[mapping[norm_query]]

    # 3. Substring matching in normalized keys
    for key, data in HERB_DATABASE.items():
        norm_key = normalize(key)
        norm_botanical = normalize(data["botanical_name"])
        if norm_query in norm_key or norm_key in norm_query or norm_query in norm_botanical:
            return data

    # Return a default template to prevent crashes and provide general information for new species
    return {
        "name": name.title(),
        "botanical_name": "Unknown species",
        "family": "Unknown family",
        "active_compounds": ["Natural Phytochemicals"],
        "phytochemicals": ["Bioflavonoids", "Antioxidants"],
        "benefits": ["General skin soothing", "Antioxidant support"],
        "side_effects": ["None reported for general topical use"],
        "contraindications": ["None reported"],
        "evidence_level": "Traditional/General literature",
        "research_papers": [],
        "preparation_method": "Clean the leaf, crush to extract juice or make a paste, and apply topically.",
        "skin_types": ["All"],
        "disease_mapping": {}
    }

def get_recommendations_for_disease(disease, min_efficacy=0):
    recs = []
    for name, data in HERB_DATABASE.items():
        if disease in data["disease_mapping"]:
            mapping = data["disease_mapping"][disease]
            if mapping["efficacy"] >= min_efficacy:
                recs.append({
                    "name": name,
                    "botanical_name": data["botanical_name"],
                    "efficacy": mapping["efficacy"],
                    "weight": mapping["weight"],
                    "benefits": data["benefits"],
                    "evidence_level": data["evidence_level"]
                })
    # Sort by efficacy score desc
    return sorted(recs, key=lambda x: x["efficacy"], reverse=True)

def get_all_herbs():
    return list(HERB_DATABASE.values())
