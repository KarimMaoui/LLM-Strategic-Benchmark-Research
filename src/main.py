import random
import time
import sys
import os
from dotenv import load_dotenv
from colorama import init, Fore, Style

# Imports locaux
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.player import Player
from src.words import WORD_PAIRS

load_dotenv()
init(autoreset=True)

# --- CONFIGURATION ---
NB_GAMES = 10
NB_ROUNDS = 3

# Création des Agents (Persistants pour garder les stats)
AGENTS = [
    Player("Mistral-Large", "mistral"),
    Player("DeepSeek-V3", "deepseek"),
    Player("Gemini-Flash", "gemini")
]

def run_simulation():
    print(f"{Fore.CYAN}=== 🚀 LANCEMENT DU BENCHMARK : {NB_GAMES} PARTIES ==={Style.RESET_ALL}\n")

    global_stats = {agent.name: {"civil_wins": 0, "impostor_wins": 0, "impostor_escapes": 0} for agent in AGENTS}

    for game_id in range(1, NB_GAMES + 1):
        # 1. SETUP DE LA PARTIE
        # Choix aléatoire des mots
        pair = random.choice(WORD_PAIRS)
        civil_word, impostor_word = pair if random.random() > 0.5 else (pair[1], pair[0])
        
        # Désignation aléatoire de l'imposteur
        impostor_agent = random.choice(AGENTS)
        
        # Distribution des mots et mélange de l'ordre de parole
        current_players = AGENTS.copy()
        random.shuffle(current_players) # L'ordre change à chaque partie !

        print(f"{Fore.YELLOW}--- PARTIE {game_id}/{NB_GAMES} ---{Style.RESET_ALL}")
        print(f"Mots en jeu : '{civil_word}' (Majorité) vs '{impostor_word}' (Imposteur)")
        print(f"(Secret: L'Imposteur est {impostor_agent.name})")

        for p in current_players:
            p.set_word(impostor_word if p == impostor_agent else civil_word)

        history = ""

        # 2. BOUCLE DES 3 ROUNDS
        for round_num in range(1, NB_ROUNDS + 1):
            print(f"\n{Style.BRIGHT}Round {round_num}{Style.RESET_ALL}")
            for p in current_players:
                res = p.speak(history, round_num)
                
                # Couleurs
                color = Fore.RED if p == impostor_agent else Fore.BLUE
                print(f"{color}{p.name}: {res.get('message', '...')} {Style.DIM}({res.get('thought', '')}){Style.RESET_ALL}")
                
                history += f"{p.name}: {res.get('message')}\n"

        # 3. PHASE DE VOTE
        print(f"\n{Fore.MAGENTA}🗳️  VOTES FINAUX{Style.RESET_ALL}")
        votes = {}
        for p in current_players:
            # On passe la liste des noms pour qu'ils sachent pour qui voter
            others = [a.name for a in AGENTS if a.name != p.name] 
            v_res = p.vote(history, others)
            
            target = v_res.get('vote_for')
            votes[p.name] = target
            print(f"   - {p.name} vote contre {Fore.RED}{target}{Style.RESET_ALL} ({v_res.get('thought')})")

        # 4. RÉSULTATS
        # Compter les votes
        vote_counts = {}
        for voter, target in votes.items():
            vote_counts[target] = vote_counts.get(target, 0) + 1
        
        # Qui est éliminé ? (Celui qui a le max de votes)
        eliminated = max(vote_counts, key=vote_counts.get)
        
        print(f"\n💀 Joueur éliminé : {eliminated}")

        # KPI LOGIC
        if eliminated == impostor_agent.name:
            print(f"{Fore.GREEN}🏆 LES CIVILS GAGNENT !{Style.RESET_ALL}")
            # Stats update
            for p in AGENTS:
                if p != impostor_agent:
                    global_stats[p.name]["civil_wins"] += 1
        else:
            print(f"{Fore.RED}🏆 L'IMPOSTEUR ({impostor_agent.name}) GAGNE !{Style.RESET_ALL}")
            global_stats[impostor_agent.name]["impostor_wins"] += 1
            global_stats[impostor_agent.name]["impostor_escapes"] += 1

        print("-" * 30 + "\n")
        time.sleep(2) # Petite pause entre les parties

    # 5. TABLEAU DES SCORES FINAL (KPIs)
    print(f"\n{Fore.CYAN}=== 📊 RÉSULTATS DU BENCHMARK ({NB_GAMES} PARTIES) ==={Style.RESET_ALL}")
    print(f"{'MODÈLE':<15} | {'CIVIL WINS':<12} | {'IMP. WINS':<12} | {'TOTAL SCORE'}")
    print("-" * 55)
    
    for name, stats in global_stats.items():
        score = stats['civil_wins'] + (stats['impostor_wins'] * 2) # L'imposteur gagne plus de points car c'est dur
        print(f"{name:<15} | {stats['civil_wins']:<12} | {stats['impostor_wins']:<12} | {score}")

if __name__ == "__main__":
    run_simulation()
