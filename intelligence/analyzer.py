import json, time
from google import genai
from config import GEMINI_API_KEY, BRAND_CONTEXT

class ContentAnalyzer:
    def __init__(self, brand_name=None, industry=None, brand_brief=None):
        self.brand_name = brand_name or BRAND_CONTEXT['name']
        self.industry = industry or "General"
        self.brand_brief = brand_brief or "No brief provided."
        self.client = None
        if GEMINI_API_KEY:
            try:
                self.client = genai.Client(api_key=GEMINI_API_KEY)
            except Exception as e:
                print(f"[!] Failed to initialize Gemini: {e}")

    def _extract_json(self, text):
        try:
            start = text.find('{')
            end = text.rfind('}') + 1
            if start != -1 and end != -1:
                return json.loads(text[start:end])
            return None
        except:
            return None

    def analyze(self, influencer_data):
        if not self.client:
            return self._mock_analysis(influencer_data)

        models_to_try = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-flash-latest"]
        prompt = f"""
        Analyze this micro-influencer for our brand:
        BRAND NAME: {self.brand_name}
        INDUSTRY: {self.industry}
        BRAND BRIEF: {self.brand_brief}
        
        IMPORTANT: Do not assume {self.brand_name} is a pre-existing famous brand. Treat it as a generic brand operating within the '{self.industry}' industry unless explicitly detailed in the BRAND BRIEF.
        
        CREATOR: {influencer_data['name']}
        BIO: {influencer_data['description']}
        RECENT UPLOAD: {influencer_data.get('recent_video', 'Unknown')}
        
        CRITICAL: You MUST classify this creator primarily based on their 'RECENT UPLOAD' content context, NOT just their follower bio assumptions.
        
        Return ONLY a JSON object with:
        niche, segment_name (String. Must be formatted exactly as "Segment [A/B/C]: [Logical Cluster Name]". Group the creator into one of 3 logical segments based on their content, e.g., "Segment A: Skincare Educators" or "Segment B: Workout Routines"), content_themes (list), recent_signals (list of specific topics/keywords mentioned), relevance_score (0-100), reasoning, recommended_collab_type (MUST be one of: "paid sponsorship", "affiliate programs", "barter collaborations", "UGC partnerships", "product trials", "ambassador programs")
        """

        time.sleep(4) # Strict 15 RPM throttle for free tier limit
        for model_name in models_to_try:
            try:
                response = self.client.models.generate_content(
                    model=model_name,
                    contents=prompt
                )
                analysis = self._extract_json(response.text)
                if analysis:
                    influencer_data.update(analysis)
                    return influencer_data
                time.sleep(2) # Backoff if JSON parsing failed
            except Exception as e:
                if any(code in str(e) for code in ["404", "429", "503", "500"]):
                    time.sleep(2) # Backoff before trying next model
                    continue
                print(f"[!] Detailed Gemini Error: {e}")
                break

        return self._mock_analysis(influencer_data)

    def _mock_analysis(self, data):
        data.update({
            "niche": "General Content", "segment": "Segment B",
            "content_themes": ["Education"], "recent_signals": ["general topics"], "relevance_score": 50,
            "reasoning": "Fallback analysis.", "recommended_collab_type": "Barter"
        })
        return data
