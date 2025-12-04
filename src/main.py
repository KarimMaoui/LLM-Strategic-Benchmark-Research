import os
import sys
from dotenv import load_dotenv
from colorama import init, Fore, Style

# Ajout du chemin pour trouver player.py
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.player import Player

load_dotenv()
init(autoreset=True)

# --- CONFIGURATION DE LA PARTIE ---
SECRET_WORD = "Croissant"

# On crée 3 joueurs DeepSeek
PLAYERS_SETUP = [
    {"name": "DeepSeek-Alpha", "role": "Civil"},
    {"name": "DeepSeek-Beta",  "role": "Imposteur"},
    {"name": "DeepSeek-Gamma", "role": "Civil"}
]

def run_game():
    print(f"{Fore.CYAN}=== 🕵️  DEEPSEEK SELF-PLAY ARENA ==={Style.RESET_ALL}")
    print(f"Mot secret : {SECRET_WORD}\n")

    # 1. Création des joueurs
    players = []
    for setup in PLAYERS_SETUP:
        # Si c'est un civil, il reçoit le mot. Si imposteur, il reçoit "???"
        word = SECRET_WORD if setup["role"] == "Civil" else "???"
        players.append(Player(setup["name"], setup["role"], word))

    # 2. Tour de table
    history = ""
    for p in players:
        print(f"🤔 {p.name} ({p.role}) réfléchit...")
        
        response = p.speak(history)
        
        # Affichage
        if p.role == "Imposteur":
            color = Fore.RED
        else:
            color = Fore.GREEN
            
        print(f"{Style.DIM}   (Pensée : {response.get('thought')}){Style.RESET_ALL}")
        print(f"{color}🗣️  {p.name} : \"{response.get('message')}\"{Style.RESET_ALL}\n")
        
        history += f"{p.name}: {response.get('message')}\n"

if __name__ == "__main__":
    run_game()
