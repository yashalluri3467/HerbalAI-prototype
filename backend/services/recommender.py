from database.knowledge_base import get_recommendations_for_disease, get_herb_by_name

class RecommenderService:
    @staticmethod
    def recommend(detected_disease, disease_confidence, classified_herb=None, herb_confidence=0.0):
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
            
            # Calculate calibrated expected effectiveness
            # We scale the efficacy slightly based on how confident the skin condition detection was.
            calibrated_efficacy = int(base_efficacy * (0.9 + 0.1 * disease_confidence))
            
            # Recommendation confidence integrates the database suitability weight
            # and the disease classifier confidence.
            recommendation_confidence = int(100 * (disease_confidence * base_weight))
            
            # Bound values between 5% and 99%
            calibrated_efficacy = min(max(calibrated_efficacy, 10), 99)
            recommendation_confidence = min(max(recommendation_confidence, 10), 99)
            
            recommendations.append({
                "name": herb_name,
                "botanical_name": rec["botanical_name"],
                "efficacy_score": calibrated_efficacy,
                "recommendation_confidence": recommendation_confidence,
                "evidence_level": rec["evidence_level"],
                "benefits": rec["benefits"]
            })
            
        # If the user uploaded a leaf image, compute the specific compatibility metrics for it
        leaf_evaluation = None
        if classified_herb:
            herb_data = get_herb_by_name(classified_herb)
            if herb_data:
                is_compatible = detected_disease in herb_data["disease_mapping"]
                
                if is_compatible:
                    mapping = herb_data["disease_mapping"][detected_disease]
                    base_efficacy = mapping["efficacy"]
                    base_weight = mapping["weight"]
                    
                    calibrated_efficacy = int(base_efficacy * (0.9 + 0.1 * disease_confidence))
                    # Combined confidence includes the leaf classifier confidence and skin disease confidence
                    joint_confidence = int(100 * (disease_confidence * herb_confidence * base_weight))
                    
                    calibrated_efficacy = min(max(calibrated_efficacy, 10), 99)
                    joint_confidence = min(max(joint_confidence, 10), 99)
                else:
                    calibrated_efficacy = 0
                    joint_confidence = int(100 * (disease_confidence * herb_confidence * 0.1)) # Very low
                    joint_confidence = min(max(joint_confidence, 5), 30)
                    
                leaf_evaluation = {
                    "name": classified_herb,
                    "botanical_name": herb_data["botanical_name"],
                    "is_compatible": is_compatible,
                    "efficacy_score": calibrated_efficacy,
                    "joint_confidence": joint_confidence,
                    "evidence_level": herb_data["evidence_level"],
                    "benefits": herb_data["benefits"]
                }
                
        # Sort recommendations by recommendation confidence desc
        recommendations = sorted(recommendations, key=lambda x: x["recommendation_confidence"], reverse=True)
        
        # Take Top 3 recommendations
        top_3 = recommendations[:3]
        
        return {
            "top_recommendations": top_3,
            "leaf_evaluation": leaf_evaluation
        }
