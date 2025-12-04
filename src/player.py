import json
import os
from openai import OpenAI

class Player:
    def __init__(self, name, role, secret_word):
        self.name = name
        self.role = role
        self.secret_word = secret_word
        
        # On initialise DeepSeek via le client OpenAI
        # DeepSeek est "OpenAI Compatible", on change juste l'URL
        self.client = OpenAI(
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url="https://api.deepseek.com"
        )

    def speak(self, conversation_history):
        # 1. Préparation des instructions (System Prompt)
        if self.role == "Civil":
            system_instruction = (
                f"Tu es {self.name}, un CIVIL. Le mot secret est : '{self.secret_word}'.\n"
                "Ton but : Prouver que tu connais le mot sans le dire explicitement. Sois subtil."
            )
        else:
            system_instruction = (
                f"Tu es {self.name}, l'IMPOSTEUR. Tu ne connais PAS le mot secret.\n"
                "Ton but : Lire la conversation, déduire le contexte, et inventer une phrase vague pour te fondre dans la masse."
            )

        system_instruction += "\nRéponds UNIQUEMENT au format JSON : {\"thought\": \"ta pensée stratégique\", \"message\": \"ta phrase publique\"}"

        # 2. Appel à l'API DeepSeek
        try:
            response = self.client.chat.completions.create(
                model="deepseek-chat", # ou "deepseek-reasoner" (R1) pour plus d'intelligence
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": f"Historique de la conversation :\n{conversation_history}\n\nÀ toi de parler."}
                ],
                temperature=0.7
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"Erreur API : {e}")
            return {"thought": "Erreur", "message": "Je suis muet..."}
