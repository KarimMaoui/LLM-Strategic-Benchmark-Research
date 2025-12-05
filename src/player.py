import json
import os
import time
from openai import OpenAI
import google.generativeai as genai

class Player:
    def __init__(self, name, provider):
        self.name = name
        self.provider = provider
        self.word = None
        
        # --- CONFIGURATION CLIENTS ---
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

    def _generate(self, system_prompt, user_context):
        """Gère l'appel API avec une pause de sécurité"""
        try:
            time.sleep(1.5) # Pause pour laisser le temps de 'réfléchir' (et rate limit)
            
            if self.provider == "gemini":
                chat = self.model.start_chat(history=[])
                response = chat.send_message(f"{system_prompt}\n\nSITUATION ACTUELLE:\n{user_context}")
                return json.loads(response.text)
            else:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"SITUATION ACTUELLE:\n{user_context}"}
                    ],
                    response_format={"type": "json_object"},
                    temperature=0.6 # Température basse pour être précis et concis
                )
                return json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"⚠️ Erreur {self.name}: {e}")
            return {"thought": "Erreur", "message": "...", "vote": "Personne"}

    def speak(self, conversation_history, round_num):
        # PROMPT DE HAUT NIVEAU STRATÉGIQUE
        sys_prompt = (
            f"Tu es {self.name}. Tu joues à 'Undercover'.\n"
            f"TON MOT SECRET : '{self.word}'.\n\n"
            
            "RÈGLES ABSOLUES (Mode Expert) :\n"
            "1. LONGUEUR : 1 à 3 mots MAXIMUM. Interdiction de faire des phrases. Pas de verbes.\n"
            "2. ADAPTATION : Lis ce que les autres ont dit AVANT de parler. S'ils disent un truc incompatible avec ton mot, TU ES L'IMPOSTEUR. Dans ce cas, mens et aligne-toi sur eux.\n"
            "3. SUBTILITÉ : Ne sois pas évident. Si ton mot est 'Soleil', ne dis pas 'Jaune' (trop facile), dis 'Astres' ou 'Été'.\n\n"
            
            "Format de réponse JSON attendu :\n"
            "{\n"
            "  \"context_analysis\": \"Analyse CRITIQUE : Qu'ont dit les joueurs précédents ? Est-ce compatible avec mon mot '{self.word}' ? Si non, quel est LEUR mot probable ?\",\n"
            "  \"strategy\": \"Si je suis safe -> indice subtil. Si je suis suspect -> bluff total pour coller aux autres.\",\n"
            "  \"message\": \"Ton mot ou groupe de mots (Max 3 mots)\"\n"
            "}"
        )
        
        context = f"Nous sommes au Round {round_num}.\nHistorique de la conversation :\n{conversation_history if conversation_history else '(Tu es le premier à parler, reste vague !)'}"
        
        return self._generate(sys_prompt, context)

    def vote(self, conversation_history, alive_players_names):
        sys_prompt = (
            f"Tu es {self.name}. Ton mot était '{self.word}'.\n"
            "Phase de VOTE FINAL.\n"
            "Analyse l'historique complet. Qui a donné un indice qui ne collait pas tout à fait ?\n"
            "Qui a semblé hésiter ou copier les autres ?\n"
            f"Joueurs ciblables : {alive_players_names}\n"
            "Réponds JSON: {\"thought\": \"Raisonnement de détective...\", \"vote_for\": \"NomExactDuJoueur\"}"
        )
        return self._generate(sys_prompt, conversation_history)
