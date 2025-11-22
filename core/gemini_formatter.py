import google.generativeai as genai
from config import config

class GeminiFormatter:
    def __init__(self):
        self.configured = False

    def configure(self):
        if not config.gemini_api_key:
            # Silent fail if key is missing, user might not want AI features
            return False
        
        try:
            genai.configure(api_key=config.gemini_api_key)
            self.configured = True
            return True
        except Exception as e:
            # Only log real errors
            print(f"Error configuring Gemini: {e}")
            return False

    def format_text(self, raw_text):
        if not raw_text or not raw_text.strip():
            return raw_text

        if not self.configured:
            if not self.configure():
                return raw_text # Fallback

        # print(f"Formatting text with Gemini ({config.gemini_model})...")
        
        try:
            model = genai.GenerativeModel(config.gemini_model)
            
            system_prompt = (
                "You are a precise text correction and formatting engine. Your task is to fix grammar, punctuation, "
                "and capitalization errors in the provided text. You should also format the text for readability.\n"
                "RULES:\n"
                "1. Do NOT change the meaning or remove content.\n"
                "2. Do NOT add conversational filler (like 'Here is the text').\n"
                "3. USE bullet points ( - ) and newlines where appropriate to structure lists or distinct thoughts.\n"
                "4. Output ONLY the formatted text."
            )
            
            response = model.generate_content(f"{system_prompt}\n\nText to correct:\n{raw_text}")
            
            formatted_text = response.text.strip()
            print(f"Formatted: {formatted_text[:50]}...")
            return formatted_text
            
        except Exception as e:
            print(f"Error calling Gemini API: {e}")
            return raw_text

gemini_formatter = GeminiFormatter()
