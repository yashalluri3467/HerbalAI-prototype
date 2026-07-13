from database.knowledge_base import get_recommendations_for_disease, get_herb_by_name


class RecommenderService:
    @staticmethod
    def recommend(
        detected_disease, disease_confidence, classified_herb=None, herb_confidence=0.0
    ):
        """
        Calculates recommendation rankings, confidence, and efficacy scores.
        Arguments:
            detected_disease (str): The classified skin condition.
            disease_confidence (float): Confidence score of the skin condition model (0.0 to 1.0).
            classified_herb (str, optional): The herb classified from the leaf image, if uploaded.
            herb_confidence (float, optional): Confidence score of the leaf classifier model.
        Returns:
            dict containing recommendations list, direct match details, etc.
        """
        # Get matching herbs from knowledge base
        kb_recs = get_recommendations_for_disease(detected_disease)

        recommendations = []
        for rec in kb_recs:
            herb_name = rec["name"]
            base_efficacy = rec["efficacy"]
            base_weight = rec["weight"]

            recommendations.append(
                {
                    "name": herb_name,
                    "botanical_name": rec["botanical_name"],
                    "efficacy_score": base_efficacy,
                    "recommendation_confidence": round(disease_confidence * 100, 2),
                    "knowledge_base_weight": base_weight,
                    "evidence_level": rec["evidence_level"],
                    "benefits": rec["benefits"],
                }
            )

        # If the user uploaded a leaf image, compute the specific compatibility metrics for it
        leaf_evaluation = None
        if classified_herb:
            herb_data = get_herb_by_name(classified_herb)
            if herb_data:
                normalized_disease = detected_disease.replace("_", " ").casefold()
                mapping_key = next(
                    (
                        label
                        for label in herb_data["disease_mapping"]
                        if label.casefold() == normalized_disease
                    ),
                    None,
                )
                is_compatible = mapping_key is not None

                if is_compatible:
                    mapping = herb_data["disease_mapping"][mapping_key]
                    base_efficacy = mapping["efficacy"]
                    base_weight = mapping["weight"]
                    calibrated_efficacy = base_efficacy
                    joint_confidence = round(
                        min(disease_confidence, herb_confidence) * 100, 2
                    )
                else:
                    calibrated_efficacy = 0
                    joint_confidence = round(
                        min(disease_confidence, herb_confidence) * 100, 2
                    )

                leaf_evaluation = {
                    "name": classified_herb,
                    "botanical_name": herb_data["botanical_name"],
                    "is_compatible": is_compatible,
                    "efficacy_score": calibrated_efficacy,
                    "joint_confidence": joint_confidence,
                    "knowledge_base_weight": base_weight if is_compatible else None,
                    "evidence_level": herb_data["evidence_level"],
                    "benefits": herb_data["benefits"],
                }

        # Sort recommendations by recommendation confidence desc
        recommendations = sorted(
            recommendations, key=lambda x: x["recommendation_confidence"], reverse=True
        )

        # Take Top 3 recommendations
        top_3 = recommendations[:3]

        return {"top_recommendations": top_3, "leaf_evaluation": leaf_evaluation}
