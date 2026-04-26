class BrandFitScorer:
    def __init__(self):
        pass

    def calculate_score(self, influencer_data):
        """
        Takes the base AI relevance score and applies programmatic weights based on rules.
        """
        base_score = influencer_data.get('relevance_score', 50)
        followers = influencer_data.get('follower_count', 0)
        
        # Algorithmic bump for the 'sweet spot' of micro-influencers
        if 10000 <= followers <= 50000:
            adjusted_score = min(100, base_score + 5)
        else:
            adjusted_score = base_score
            
        influencer_data['adjusted_brand_fit_score'] = adjusted_score
        # For compatibility with UI, copy adjusted to main score
        influencer_data['brand_fit_score'] = adjusted_score
        
        return influencer_data
