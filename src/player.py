import json
import os
from openai import OpenAI
import google.generativeai as genai # On importe la librairie Google

class Player:
    def __init__(self, name, role, secret_word, provider):
        self.name = name
        self.role = role
        self.secret_word = secret_word
        self.provider = provider
        
        # --- CONFIGURATION ---
        
        if self.provider == "deepseek":
            self.client = OpenAI(
                api_key=os.getenv("DEEPSEEK_API_KEY"),
                base_url="https://api.deepseek.com"
            )
            self.model = "deepseek-chat"

        elif self.provider == "mistral":
            self.client = OpenAI(
                api_key=os.getenv("MISTRAL_API_KEY"),
                base_url="https://api.mistral.ai/v1"
            )
            self.model = "mistral-large-latest"

        elif self.provider == "gemini":
            # Configuration Spécifique Google Native
            genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
            # On configure le modèle pour qu'il sorte du JSON obligatoirement
            self.model = genai.GenerativeModel(
                "gemini-1.5-flash",
                generation_config={"response_mime_type": "application/json"}
            )

    def speak(self, conversation_history):
        # 1. Préparation du Prompt
        if self.role == "Civil":
            sys_prompt = f"Tu es {self.name} (CIVIL). Mot secret: '{self.secret_word}'. Sois subtil."
        else:
            sys_prompt = f"Tu es {self.name} (IMPOSTEUR). Tu ne connais pas le mot. Reste vague."
        
        sys_prompt += "\nRéponds UNIQUEMENT avec ce format JSON : {\"thought\": \"...\", \"message\": \"...\"}"

        # 2. Appel API (Différent selon le fournisseur)
        try:
            if self.provider == "gemini":
                # --- Méthode Google Native ---
                chat = self.model.start_chat(history=[])
                full_prompt = f"{sys_prompt}\n\nHistorique:\n{conversation_history}\n\nÀ toi."
                response = chat.send_message(full_prompt)
                return json.loads(response.text)
            
            else:
                # --- Méthode OpenAI (DeepSeek / Mistral) ---
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
            print(f"⚠️ Erreur {self.name}: {e}")
            return {"thought": "Bug", "message": "Je ne sais pas quoi dire..."}
