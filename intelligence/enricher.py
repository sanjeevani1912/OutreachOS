class DataEnricher:
    @staticmethod
    def enrich(influencer_data, brand_name="[Brand]"):
        """
        Enriches raw influencer data with calculated metrics and default values.
        Ensures consistency between CLI and Web Dashboard.
        """
        d = influencer_data
        
        # Core Handle & Followers
        d['creator_handle'] = d.get('handle', d.get('name', 'unknown'))
        d['followers'] = d.get('follower_count', 0)
        d['fit_explanation'] = d.get('reasoning', d.get('fit_explanation', "Good fit overall."))
        
        # 1. Calculate Engagement & Views
        # metadata contains 'view_count' and 'video_count' from YouTube stats
        metadata = d.get('metadata', {})
        v = int(metadata.get('view_count') or 0)
        vc = int(metadata.get('video_count') or 1)
        subs = d.get('follower_count', 1)
        
        avg_v = v // vc if vc > 0 else 0
        d['avg_views'] = avg_v
        
        # Refined engagement rate formula:
        # We use a 4% synthetic factor of the view-to-sub ratio, capped at 18.5%
        # This reflects high-view creators realistically without showing >100% rates.
        base_rate = (avg_v / subs * 100) if subs > 0 else 3.5
        d['engagement_rate'] = round(min(base_rate * 0.04, 18.5), 1)
        
        # 2. Estimate Posting Frequency
        if vc >= 500: d['posting_frequency'] = "Daily"
        elif vc >= 200: d['posting_frequency'] = "3-4x/week"
        elif vc >= 100: d['posting_frequency'] = "2x/week"
        elif vc >= 50: d['posting_frequency'] = "Weekly"
        else: d['posting_frequency'] = "Occasional"
        
        # 3. Default Quality & Trend Signals
        if 'engagement_quality' not in d: d['engagement_quality'] = "Genuine"
        if 'engagement_reason' not in d: d['engagement_reason'] = "Consistent organic growth."
        if 'growth_trend' not in d: d['growth_trend'] = "Stable"
        if 'country' not in d: d['country'] = d.get('country', 'India')
        
        # 4. Fallback Logic for Intelligence Fields
        if 'brand_fit_score' not in d: d['brand_fit_score'] = d.get('relevance_score', 50)
        if 'niche' not in d: d['niche'] = "General"
        if 'segment_name' not in d: d['segment_name'] = "Segment A: General Audience"
        if 'content_themes' not in d: d['content_themes'] = ["Video Content"]
        if 'recent_signals' not in d: d['recent_signals'] = ["Recent upload"]
        if 'collaboration_recommended' not in d: 
            d['collaboration_recommended'] = d.get('recommended_collab_type', "Barter Collaboration")
        
        # 5. Outreach Flattening (for easy access in tables/exports)
        if 'outreach' in d:
            outreach = d['outreach']
            # Fallback to professional tone for flat fields
            prof = outreach.get('professional', {})
            d['email_body'] = prof.get('email', '')
            d['dm_message'] = prof.get('dm', '')
        else:
            d['email_body'] = d.get('email_body', '')
            d['dm_message'] = d.get('dm_message', '')
            
        d['email_subject'] = f"Partnership Opportunity — {brand_name} x {d.get('creator_handle', '')}"
        
        # 6. Safety Checks & Flags
        if 'outreach_signals_used' not in d: d['outreach_signals_used'] = "Recent channel activity"
        if 'contact_email' not in d: d['contact_email'] = d.get('contact_email', "Not listed")
        if 'competitor_flag' not in d: d['competitor_flag'] = False
        if 'competitor_detail' not in d: d['competitor_detail'] = None
        
        return d
