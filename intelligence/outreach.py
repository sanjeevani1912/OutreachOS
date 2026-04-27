import json, time
from google import genai
from config import GEMINI_API_KEY, BRAND_CONTEXT

class OutreachGenerator:
    def __init__(self, brand_name=None, tone="Professional", industry=None, brand_brief=None):
        self.brand_name = brand_name or BRAND_CONTEXT['name']
        self.tone = tone
        self.industry = industry or "General"
        self.brand_brief = brand_brief or "No brief provided."
        self.client = None
        if GEMINI_API_KEY:
            try:
                self.client = genai.Client(api_key=GEMINI_API_KEY)
            except Exception as e:
                print(f"[!] Failed to initialize Gemini for Outreach: {e}")

    def _extract_json(self, text):
        try:
            start = text.find('{')
            end = text.rfind('}') + 1
            if start != -1 and end != -1:
                return json.loads(text[start:end])
            return None
        except:
            return None

    def generate(self, enriched_influencer):
        if not self.client:
            enriched_influencer['outreach'] = {"email": "Mock", "dm": "Mock"}
            return enriched_influencer

        models_to_try = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-flash-latest"]
        prompt = f"""
        Generate personalized outreach messages from our brand to this creator.
        BRAND NAME: {self.brand_name}
        INDUSTRY: {self.industry}
        BRAND BRIEF: {self.brand_brief}
        
        IMPORTANT: Do not assume {self.brand_name} is a pre-existing famous brand. Do not hallucinate product names. Treat it as a generic brand operating within the '{self.industry}' industry unless detailed in the BRAND BRIEF.
        
        CREATOR: {enriched_influencer['name']}
        THEMES: {', '.join(enriched_influencer.get('content_themes', []))}
        RECENT SIGNALS: {', '.join(enriched_influencer.get('recent_signals', ['their content format']))}
        
        Return ONLY a JSON object with TWO distinct tones. Keys MUST be exactly: 'professional', 'friendly'.
        Each key must contain a nested object with keys: 'email' (60-90 words) and 'dm' (15-30 words).
        
        CRITICAL FORMATTING RULES:
        1. Every email MUST start with a proper salutation (e.g., "Hi [Name]," or "Dear [Name],").
        2. Every email MUST end with a professional closing (e.g., "Best regards," or "Cheers,").
        3. You MUST show that you actually watched their content. Reference one of their 'RECENT SIGNALS' or 'THEMES' in the first paragraph. 
        
        CRITICAL RULE for TONE:
        Ensure the generated messages strictly follow the requested BRAND TONE ({self.tone}). Adjust vocabulary, formality, and structure accordingly.
        """

        time.sleep(4) # Strict 15 RPM throttle for free tier limit
        for model_name in models_to_try:
            try:
                response = self.client.models.generate_content(
                    model=model_name,
                    contents=prompt
                )
                outreach = self._extract_json(response.text)
                if outreach:
                    enriched_influencer['outreach'] = outreach
                    return enriched_influencer
                time.sleep(2) # Backoff if JSON parsing failed
            except Exception as e:
                if any(code in str(e) for code in ["404", "429", "503", "500"]):
                    time.sleep(2) # Backoff before trying next model
                    continue
                print(f"[!] Outreach error with {model_name}: {e}")
                break

        base_email = f"Hi {enriched_influencer['name']},\n\nWe love your content in the {enriched_influencer.get('niche', 'General')} space! We think you'd be a great fit for a {self.brand_name} collaboration.\n\nLet us know if you're open to discussing a partnership!\n\nBest,\n{self.brand_name} Team"
        base_dm = f"Hey {enriched_influencer['name']}, love your recent posts! We're from {self.brand_name} and would love to partner with you. Let's chat!"

        enriched_influencer['outreach'] = {
            "professional": {"email": base_email, "dm": base_dm},
            "friendly": {"email": base_email.replace("Hi", "Hey").replace("Best,", "Cheers,"), "dm": base_dm}
        }
        return enriched_influencer
