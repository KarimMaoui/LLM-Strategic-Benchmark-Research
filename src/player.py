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
                    temperature=0.4 # Température basse pour être chirurgical et éviter le bavardage
                )
                return json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"⚠️ Erreur {self.name}: {e}")
            return {"context_analysis": "Erreur", "message": "Bug", "vote": "Personne"}

    def speak(self, conversation_history, round_num):
        # Détection : Suis-je le premier à parler ce tour-ci ?
        is_first = len(conversation_history.strip()) < 5 and round_num == 1
        
        role_instruction = ""
        
        if is_first:
            # STRATÉGIE JOUEUR 1 : AMBIVALENCE CALCULÉE
            role_instruction = (
                "SITUATION : Tu es le PREMIER à parler. C'est dangereux.\n"
                "RISQUE : Si tu es trop précis, l'Imposteur te reconnaîtra. Si tu es trop vague, on te suspectera.\n"
                "ACTION : Imagine 3 mots alternatifs que l'Imposteur pourrait avoir (le 'Preshot'). \n"
                "Choisis un mot 'Carrefour' qui marche pour ton mot ET pour les mots adverses probables."
            )
        else:
            # STRATÉGIE SUIVEUR : ANALYSE DIFFÉRENTIELLE STRICTE
            role_instruction = (
                "SITUATION : D'autres ont parlé avant toi.\n"
                "MISSION CRITIQUE : Ne cherche pas le point commun ! Cherche la DIFFÉRENCE FATALE.\n"
                "Exemple : Si ton mot est 'Piscine' et qu'ils disent 'Sable', ce n'est PAS 'compatible vacances', c'est 'INCOMPATIBLE sol'.\n"
                "Si tu détectes une nuance qui ne colle pas à 100% avec ton mot : TU ES L'IMPOSTEUR. MENS et aligne-toi sur eux."
            )

        sys_prompt = (
            f"Tu es {self.name}. Tu joues à 'Undercover' (Mode Expert).\n"
            f"TON MOT SECRET : '{self.word}'.\n\n"
            
            f"{role_instruction}\n\n"
            
            "CONTRAINTES DE RÉPONSE (Vitales) :\n"
            "1. UN SEUL MOT UNIQUE. Interdiction absolue de faire une phrase ou de mettre deux mots.\n"
            "2. Pas de ponctuation, pas d'article (pas de 'le', 'un', 'c'est'). Juste le mot.\n"
            "3. Pas de nom propre trop évident.\n\n"
            
            "Format JSON attendu :\n"
            "{\n"
            "  \"context_analysis\": \"(Pensée privée) 1. Quels sont les mots adverses possibles ? 2. Ce qui a été dit colle-t-il EXACTEMENT à mon mot ou juste 'à peu près' ?\",\n"
            "  \"strategy\": \"(Pensée privée) Je vise l'ambiguïté ou la précision ?\",\n"
            "  \"message\": \"TON_MOT_UNIQUE\"\n"
            "}"
        )
        
        context = f"Round {round_num}.\nHistorique :\n{conversation_history if conversation_history else '(Aucun historique - Tu ouvres le bal)'}"
        
        return self._generate(sys_prompt, context)

    def vote(self, conversation_history, alive_players_names):
        sys_prompt = (
            f"Tu es {self.name}. Ton mot était '{self.word}'.\n"
            "Phase de VOTE.\n"
            "Disqualification immédiate si :\n"
            "- Un joueur a donné un mot 'Techniquement vrai' mais avec la mauvaise nuance (ex: 'Chaud' pour 'Soleil' alors que le mot était 'Lampe').\n"
            "- Un joueur a répété un synonyme trop proche des autres.\n"
            f"Suspects : {alive_players_names}\n"
            "Réponds JSON: {\"thought\": \"Analyse des nuances...\", \"vote_for\": \"NomExact\"}"
        )
        return self._generate(sys_prompt, conversation_history)
