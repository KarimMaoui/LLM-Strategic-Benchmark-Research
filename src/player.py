import json
import os
import time
from openai import OpenAI
import google.generativeai as genai

class Player:
    def __init__(self, name, provider):
        self.name = name
        self.provider = provider
        self.word = None  # Sera défini à chaque partie
        self.points = 0   # KPI: Score total
        self.wins = 0     # KPI: Victoires
        
        # Configuration des clients
        if self.provider == "deepseek":
            self.client = OpenAI(api_key=os.getenv("DEEPSEEK_API_KEY"), base_url="https://api.deepseek.com")
            self.model = "deepseek-chat"
        elif self.provider == "mistral":
            self.client = OpenAI(api_key=os.getenv("MISTRAL_API_KEY"), base_url="https://api.mistral.ai/v1")
            self.model = "mistral-large-latest"
        elif self.provider == "gemini":
            genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
            self.model = genai.GenerativeModel("gemini-2.5-flash", generation_config={"response_mime_type": "application/json"})

    def set_word(self, word):
        self.word = word

    def _generate(self, system_prompt, history):
        """Fonction interne pour gérer les appels API"""
        try:
            # Pause pour éviter le Rate Limit des versions gratuites
            time.sleep(1) 
            
            if self.provider == "gemini":
                chat = self.model.start_chat(history=[])
                response = chat.send_message(f"{system_prompt}\n\nContexte:\n{history}\n\nTa réponse:")
                return json.loads(response.text)
            else:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"Contexte:\n{history}\n\nTa réponse:"}
                    ],
                    response_format={"type": "json_object"},
                    temperature=0.7
                )
                return json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"⚠️ Erreur {self.name}: {e}")
            return {"thought": "Erreur", "message": "...", "vote": "Personne"}

    def speak(self, conversation_history, round_num):
        sys_prompt = (
            f"Tu es {self.name}. Tu joues à 'Undercover'.\n"
            f"TON MOT SECRET EST : '{self.word}'.\n"
            "Tu ne sais pas si tu es un Civil (majorité) ou l'Imposteur (minorité).\n"
            "Analyse les descriptions des autres. Si elles ne collent pas à ton mot, tu es peut-être l'Imposteur (dans ce cas, bluffe !).\n"
            f"C'est le Round {round_num}/3. Décris ton mot subtilement."
            "\nRéponds JSON: {\"thought\": \"Analyse stratégique...\", \"message\": \"Ta description courte\"}"
        )
        return self._generate(sys_prompt, conversation_history)

    def vote(self, conversation_history, alive_players_names):
        sys_prompt = (
            f"Tu es {self.name}. Ton mot était '{self.word}'.\n"
            "C'est la phase de VOTE. Qui a un mot différent des autres ?\n"
            f"Joueurs possibles : {alive_players_names}\n"
            "Réponds JSON: {\"thought\": \"Raisonnement...\", \"vote_for\": \"NomExactDuJoueur\"}"
        )
        return self._generate(sys_prompt, conversation_history)
