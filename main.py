import os
from dotenv import load_dotenv
from openai import OpenAI
from colorama import init, Fore, Style
from player import Player # On importe notre classe Player

# Chargement des variables d'environnement (.env)
load_dotenv()
init(autoreset=True)

# Configuration API
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("Clé API manquante ! Vérifie ton fichier .env")

client = OpenAI(api_key=api_key)

# Paramètres du jeu
SECRET_WORD = "Aéroport"
ROLES_CONFIG = ["Civil", "Imposteur", "Civil"]

def run_game():
    print(f"{Fore.CYAN}=== DÉBUT DU JEU : L'IMPOSTEUR ==={Style.RESET_ALL}")
    print(f"Mot secret (caché à l'imposteur) : {SECRET_WORD}\n")

    # 1. Création des joueurs
    players = []
    for i, role in enumerate(ROLES_CONFIG):
        name = f"Joueur_{i+1}"
        # L'imposteur reçoit "???" au lieu du mot
        word_for_player = SECRET_WORD if role == "Civil" else "???"
        players.append(Player(name, role, word_for_player, client))

    # 2. Boucle de discussion (1 tour pour commencer)
    conversation_log = ""
    
    for p in players:
        print(f"🤔 {p.name} ({p.role}) réfléchit...")
        
        # Le joueur 'p' parle
        result = p.speak(conversation_log)
        
        # Affichage (Pensée cachée en gris, Message public en couleur)
        color = Fore.GREEN if p.role == "Civil" else Fore.RED
        print(f"{Style.DIM}   (Pensée : {result['thought']}){Style.RESET_ALL}")
        print(f"{color}🗣️  {p.name} dit : \"{result['message']}\"{Style.RESET_ALL}\n")
        
        # Mise à jour de l'historique commun
        conversation_log += f"{p.name}: {result['message']}\n"

    print(f"{Fore.CYAN}=== FIN DU PREMIER TOUR ==={Style.RESET_ALL}")
    # Plus tard, on ajoutera le vote ici !

if __name__ == "__main__":
    run_game()
