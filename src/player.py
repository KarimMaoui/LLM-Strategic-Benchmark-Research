import json
import os
from openai import OpenAI

class Player:
    def __init__(self, name, role, secret_word, provider):
        self.name = name
        self.role = role
        self.secret_word = secret_word
        self.provider = provider
        
        # --- CONFIGURATION DES 3 FOURNISSEURS ---
        
        if self.provider == "deepseek":
            # DeepSeek V3
            self.client = OpenAI(
                api_key=os.getenv("DEEPSEEK_API_KEY"),
                base_url="https://api.deepseek.com"
            )
            self.model = "deepseek-chat"

        elif self.provider == "mistral":
            # Mistral AI (France)
            self.client = OpenAI(
                api_key=os.getenv("MISTRAL_API_KEY"),
                base_url="https://api.mistral.ai/v1"
            )
            # 'mistral-large-latest' est le meilleur, 'open-mistral-nemo' est gratuit/moins cher
            self.model = "mistral-large-latest" 

        elif self.provider == "gemini":
            # Google Gemini (via AI Studio)
            # IMPORTANT : On utilise 'v1beta' car la compatibilité OpenAI est meilleure
            self.client = OpenAI(
                api_key=os.getenv("GEMINI_API_KEY"),
                base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
            )
            # On utilise le modèle Flash standard
            self.model = "gemini-1.5-flash"

    def speak(self, conversation_history):
        # 1. System Prompt (Instructions)
        if self.role == "Civil":
            sys_prompt = f"Tu es {self.name} (CIVIL). Mot secret: '{self.secret_word}'. Sois subtil."
        else:
            sys_prompt = f"Tu es {self.name} (IMPOSTEUR). Tu ne connais pas le mot. Reste vague et fonds-toi dans la masse."
        
        sys_prompt += "\nRéponds UNIQUEMENT en JSON: {\"thought\": \"...\", \"message\": \"...\"}"

        # 2. Appel API
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": sys_prompt},
                    {"role": "user", "content": f"Historique:\n{conversation_history}\n\nÀ toi."}
                ],
                response_format={"type": "json_object"},
                temperature=0.7
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            # En cas d'erreur, on renvoie un message par défaut pour ne pas planter le jeu
            print(f"⚠️ Erreur avec {self.name} ({self.provider}): {e}")
            return {"thought": "Erreur technique", "message": "Je réfléchis..."}
