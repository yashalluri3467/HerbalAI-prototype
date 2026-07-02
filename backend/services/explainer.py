from database.knowledge_base import get_herb_by_name

class ExplainerService:
    @staticmethod
    def generate_explanation(disease, herb_name):
        """
        Generates clinical-grade explainable text for recommending a specific herb for a skin condition.
        """
        herb = get_herb_by_name(herb_name)
        if not herb:
            return "No explanation available."
            
        botanical = herb["botanical_name"]
        compounds = ", ".join(herb["active_compounds"][:3])
        phytochemicals = ", ".join(herb["phytochemicals"][:3])
        
        # Clinical reasoning mapping depending on condition
        reasoning_templates = {
            "Acne": (
                f"{herb_name} contains bioactive compounds such as {compounds}, which have documented "
                f"antibacterial and anti-inflammatory properties. These compounds target Cutibacterium acnes, "
                f"reduce sebum production, and minimize redness. The presence of {phytochemicals} further supports "
                f"pore tightening and helps heal post-inflammatory hyperpigmentation (acne scars)."
            ),
            "Eczema": (
                f"For Eczema, {herb_name} ({botanical}) works as an intense immunomodulator and anti-inflammatory agent. "
                f"Active compounds like {compounds} help restore the damaged skin barrier, lock in moisture, "
                f"and inhibit the cytokine pathways that trigger pruritus (itching) and scaling."
            ),
            "Pigmentation": (
                f"{herb_name} is rich in {compounds}, which act as natural tyrosinase inhibitors. "
                f"By regulating melanin synthesis, it helps fade dark spots, sun spots, and melasma patches. "
                f"The antioxidant properties of {phytochemicals} protect against UV-induced melanogenesis."
            ),
            "Dry Skin": (
                f"Dry skin is characterized by a deficient lipid barrier. {herb_name} provides rich fatty acids and "
                f"phytosterols, particularly {compounds}, that act as natural emollients. It fills the gaps between "
                f"desquamating skin cells, prevents trans-epidermal water loss (TEWL), and restores natural suppleness."
            ),
            "Wrinkles": (
                f"{herb_name} helps minimize wrinkles by stimulating collagen synthesis and inhibiting elastase enzymes. "
                f"Compounds like {compounds} neutralize free radicals that cause cellular aging, while the phytochemical "
                f"profile promotes cellular turnover and skin tightening."
            ),
            "Psoriasis": (
                f"Psoriasis involves rapid keratinocyte hyperproliferation. {herb_name} contains {compounds} which "
                f"possess anti-proliferative and anti-inflammatory activities, helping to slow down skin cell buildup, "
                f"reduce plaque scaling, and soothe underlying immune flares in the skin dermis."
            ),
            "Rosacea": (
                f"{herb_name} is recommended for Rosacea due to its vasoconstrictive and calming properties. "
                f"Compounds like {compounds} reduce vascular dilation (redness) and calm hyper-reactive skin pathways "
                f"without causing irritation or triggering skin flares."
            ),
            "Fungal Infection": (
                f"The active compounds in {herb_name}, particularly {compounds}, demonstrate strong antifungal activity "
                f"against dermatophyte species like Trichophyton. It disrupts the fungal cell wall membrane, preventing "
                f"spore multiplication and soothing localized itching and ringworm patterns."
            ),
            "Dermatitis": (
                f"In cases of Dermatitis, {herb_name} helps calm contact hypersensitivity. The presence of {compounds} "
                f"suppresses histamine release and localized edema, reducing swelling, redness, and vesicular oozing."
            ),
            "Melasma": (
                f"{herb_name} is effective for Melasma by inhibiting the hyperactive melanocytes. Active compounds such as "
                f"{compounds} provide safe depigmentation, fading patches on the cheeks and forehead by gently accelerating "
                f"epidermal renewal."
            ),
            "Vitiligo": (
                f"For Vitiligo, {herb_name} helps support melanogenesis in hypopigmented areas. The active constituents like "
                f"{compounds} stimulate melanocyte activity and migration, encouraging repigmentation under safe clinical parameters."
            ),
            "Healthy Skin": (
                f"For general skincare, {herb_name} maintains skin homeostasis, balances the microbiome, and provides "
                f"a continuous shield of antioxidants to prevent environmental damage and support a natural, healthy glow."
            )
        }
        
        # Fallback explanation if the template is not defined for a condition
        default_reasoning = (
            f"{herb_name} ({botanical}) is recommended because it contains bioactive compounds such as {compounds}, "
            f"which exhibit therapeutic properties suited to restore skin homeostasis. Research indicates that the "
            f"phytochemicals ({phytochemicals}) present in this herb help soothe skin tissue, reduce irritation, "
            f"and support cell regeneration for this type of condition."
        )
        
        reasoning = reasoning_templates.get(disease, default_reasoning)
        
        # Add preparation and evidence level details
        full_explanation = {
            "disease": disease,
            "herb_name": herb_name,
            "botanical_name": botanical,
            "reasoning": reasoning,
            "evidence_level": herb["evidence_level"],
            "contraindications": herb["contraindications"],
            "preparation_method": herb["preparation_method"]
        }
        
        return full_explanation
