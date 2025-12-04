import json
from openai import OpenAI
from colorama import Fore, Style

class Player:
    def __init__(self, name, role, secret_word, client):
        self.name = name
        self.role = role  # "Civil" ou "Imposteur"
        self.secret_word = secret_word
        self.client = client
        self.memory = [] # Pour retenir ce qui s'est dit

    def speak(self, conversation_history):
        """
        Demande au LLM de générer une pensée et une phrase publique.
        """
        # 1. Construction du System Prompt selon le rôle
        if self.role == "Civil":
            system_prompt = (
                f"Tu es {self.name}, un CIVIL dans le jeu de l'Imposteur.\n"
                f"Le mot secret est : '{self.secret_word}'.\n"
                "Objectif : Donne un indice subtil sur le mot pour prouver que tu le connais, "
                "mais ne sois pas trop évident pour que l'Imposteur ne devine pas."
            )
        else:
            system_prompt = (
                f"Tu es {self.name}, l'IMPOSTEUR.\n"
                "Tu ne connais PAS le mot secret.\n"
                "Objectif : Lis la conversation, déduis le contexte, et dis quelque chose "
                "de vague mais crédible pour te fondre dans la masse."
            )

        system_prompt += (
            "\nFormat de réponse JSON attendu :\n"
            "{\n"
            '  "thought": "Ta réflexion stratégique interne",\n'
            '  "message": "Ta phrase publique"\n'
            "}"
        )

        # 2. Appel API
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Historique de la conversation :\n{conversation_history}\n\nÀ toi de parler."}
                ]
            )
            content = response.choices[0].message.content
            return json.loads(content)
        except Exception as e:
            return {"thought": "Erreur", "message": "Je ne sais pas quoi dire..."}
