def filter_by_followers(influencers, min_f, max_f):
    return [i for i in influencers if min_f <= i.get('follower_count', 0) <= max_f]

def filter_by_engagement(influencers, min_engagement):
    # Stub for future engagement rate filtering
    return influencers
