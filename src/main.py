import os
import sys
from dotenv import load_dotenv
from colorama import init, Fore, Style

# Pour trouver le fichier player.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.player import Player

load_dotenv()
init(autoreset=True)

# CONFIGURATION
SECRET_WORD = "Tournesol"

# Le Casting : 1 Français, 1 Chinois, 1 Américain
PLAYERS_SETUP = [
    {"name": "Mistral-Large", "role": "Civil",     "provider": "mistral"},
    {"name": "DeepSeek-V3",   "role": "Imposteur", "provider": "deepseek"},
    {"name": "Gemini-Flash",  "role": "Civil",     "provider": "gemini"}
]

def run_game():
    print(f"{Fore.CYAN}=== 🌍 WORLD WAR AI : MISTRAL vs DEEPSEEK vs GEMINI ==={Style.RESET_ALL}")
    print(f"Mot secret : {SECRET_WORD}\n")
    
    # 1. Création des joueurs
    players = []
    for setup in PLAYERS_SETUP:
        word = SECRET_WORD if setup["role"] == "Civil" else "???"
        players.append(Player(setup["name"], setup["role"], word, setup["provider"]))

    # 2. La Discussion
    history = ""
    for p in players:
        print(f"🤔 {p.name} ({p.role}) réfléchit sur {p.provider}...")
        
        res = p.speak(history)
        
        # Gestion des couleurs pour l'affichage
        if p.role == "Imposteur":
            color = Fore.RED
        elif p.provider == "mistral":
            color = Fore.BLUE
        elif p.provider == "gemini":
            color = Fore.YELLOW
        else:
            color = Fore.GREEN # DeepSeek en civil (si applicable)
            
        print(f"{Style.DIM}   (Pensée: {res.get('thought')}){Style.RESET_ALL}")
        print(f"{color}🗣️  {p.name}: \"{res.get('message')}\"{Style.RESET_ALL}\n")
        
        history += f"{p.name}: {res.get('message')}\n"

if __name__ == "__main__":
    run_game()
