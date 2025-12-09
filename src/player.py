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
        try:
            time.sleep(1.5) 
            
            if self.provider == "gemini":
                chat = self.model.start_chat(history=[])
                response = chat.send_message(f"{system_prompt}\n\nCONTEXTE ACTUEL:\n{user_context}")
                return json.loads(response.text)
            else:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"CONTEXTE ACTUEL:\n{user_context}"}
                    ],
                    response_format={"type": "json_object"},
                    temperature=0.5
                )
                return json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"⚠️ Erreur {self.name}: {e}")
            return {"context_analysis": "Erreur", "message": "Passe", "vote_for": "Personne"}

    def speak(self, conversation_history, round_num):
        # Détection : Est-ce le tout début du jeu ?
        is_first_speaker = len(conversation_history.strip()) < 5 and round_num == 1
        
        if is_first_speaker:
            # --- RÈGLES DU PREMIER JOUEUR ---
            strategy_instruction = (
                "SITUATION : Tu es le PREMIER à parler.\n"
                "OBJECTIF : Ne pas te faire repérer par l'Imposteur, mais être reconnu par les Civils.\n"
                "CONTRAINTE LONGUEUR : 1 SEUL MOT UNIQUE (Strict).\n"
                "STRATÉGIE : Trouve un 'Mot Carrefour' (un mot qui a un double sens ou qui est assez large)."
            )
        else:
            # --- RÈGLES DES SUIVANTS ---
            strategy_instruction = (
                "SITUATION : D'autres ont parlé avant toi.\n"
                "OBJECTIF : Confirmer ton camp en donnant une nuance précise.\n"
                "CONTRAINTE LONGUEUR : 1 ou 2 Mots MAX.\n"
                "ANTI-RÉPÉTITION : Interdiction formelle de répéter un mot DEJA DIT dans l'historique.\n"
                "STRATÉGIE : Si tu as un doute sur un joueur précédent, teste-le avec un mot qui lève l'ambiguïté."
            )

        sys_prompt = (
            f"Tu es {self.name}. Tu joues à 'Undercover' (Mode Expert).\n"
            f"TON MOT SECRET : '{self.word}'.\n\n"
            
            f"{strategy_instruction}\n\n"
            
            "RÈGLES DE SÉCURITÉ :\n"
            "1. Ne jamais utiliser la racine du mot secret (ex: interdit de dire 'Vol' pour 'Avion').\n"
            "2. Vérifie l'historique : Ton mot doit être différent de ceux déjà dits.\n"
            "3. Pas de phrases, pas d'articles.\n\n"
            
            "Format JSON :\n"
            "{\n"
            "  \"context_analysis\": \"(Privé) Analyse des mots précédents. Sont-ils trop proches du mien ?\",\n"
            "  \"message\": \"TON_MOT\"\n"
            "}"
        )
        
        context = f"Round {round_num}.\nHistorique :\n{conversation_history if conversation_history else '(Tu commences)'}"
        
        return self._generate(sys_prompt, context)

    def vote(self, conversation_history, alive_players_names):
        # Ajout de l'option "Personne"
        options = alive_players_names + ["Personne"]
        
        sys_prompt = (
            f"Tu es {self.name}. Ton mot était '{self.word}'.\n"
            "Phase de VOTE.\n"
            "Analyse les indices. Y a-t-il un intrus ?\n"
            "- Si un mot t'a semblé hors sujet ou techniquement faux : Vote contre le joueur.\n"
            "- Si tu penses que tout le monde a le même mot (ou que c'est trop dur à dire) : Vote 'Personne'.\n\n"
            f"Choix possibles : {options}\n"
            "Réponds JSON: {\"thought\": \"Raisonnement...\", \"vote_for\": \"Nom_Ou_Personne\"}"
        )
        return self._generate(sys_prompt, conversation_history)
