import random
import time
import sys
import os
from dotenv import load_dotenv
from colorama import init, Fore, Style

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.player import Player
from src.words import WORD_PAIRS

load_dotenv()
init(autoreset=True)

NB_GAMES = 10
NB_ROUNDS = 3

# Initialisation des Agents
AGENTS = [
    Player("Mistral", "mistral"),
    Player("DeepSeek", "deepseek"),
    Player("Gemini", "gemini")
]

def run_simulation():
    print(f"{Fore.CYAN}=== 🕵️  BENCHMARK UNDERCOVER : EXPERT MODE ==={Style.RESET_ALL}\n")

    # Structure de données enrichie pour les KPIs
    stats = {
        agent.name: {
            "games_played": 0,
            "civil_role_count": 0,
            "impostor_role_count": 0,
            "civil_wins": 0,
            "impostor_wins": 0,
            "votes_cast_against_civil": 0,    # Pour mesurer la confusion
            "votes_cast_against_impostor": 0, # Pour mesurer la précision
            "impostor_survival_rounds": 0,    # Pour mesurer le caméléon
            "manipulation_score": 0           # Votes reçus par d'autres quand on est imposteur
        } 
        for agent in AGENTS
    }

    for game_id in range(1, NB_GAMES + 1):
        # --- SETUP ---
        pair = random.choice(WORD_PAIRS)
        words = [pair[0], pair[1]]
        random.shuffle(words)
        civil_word, impostor_word = words[0], words[1]
        
        impostor = random.choice(AGENTS)
        
        # Ordre aléatoire
        current_players = AGENTS.copy()
        random.shuffle(current_players)

        print(f"{Fore.YELLOW}--- PARTIE {game_id} : {civil_word} (Majorité) vs {impostor_word} (Imposteur) ---{Style.RESET_ALL}")
        
        for p in current_players:
            p.set_word(impostor_word if p == impostor else civil_word)

        history = "" 

        # --- GAME LOOP (3 ROUNDS) ---
        for round_num in range(1, NB_ROUNDS + 1):
            print(f"\n{Style.BRIGHT}🔁 Round {round_num}{Style.RESET_ALL}")
            
            for p in current_players:
                # L'IA reçoit l'historique à jour
                res = p.speak(history, round_num)
                
                msg = res.get('message', '...')
                analysis = res.get('context_analysis', 'Ras')
                
                # Couleurs pour le debug visuel
                role_color = Fore.RED if p == impostor else Fore.GREEN
                print(f"{role_color}{p.name:<10}{Style.RESET_ALL} : {Style.BRIGHT}\"{msg}\"{Style.RESET_ALL}")
                print(f"{Style.DIM}   └─ 🧠 {analysis}{Style.RESET_ALL}")
                
                # Ajout à l'historique
                history += f"- {p.name} : \"{msg}\"\n"

        # --- VOTES ---
        print(f"\n{Fore.MAGENTA}🗳️  VOTE{Style.RESET_ALL}")
        votes = {}
        for p in current_players:
            others = [a.name for a in AGENTS if a.name != p.name]
            v_res = p.vote(history, others)
            target = v_res.get('vote_for')
            votes[p.name] = target
            print(f"   {p.name} suspecte -> {Fore.RED}{target}{Style.RESET_ALL} ({v_res.get('thought')})")

        # --- RÉSULTAT ---
        vote_counts = {}
        for t in votes.values():
            vote_counts[t] = vote_counts.get(t, 0) + 1
        
        # Gestion des égalités (si égalité, personne ne meurt ou random, ici on prend le premier max)
        eliminated = max(vote_counts, key=vote_counts.get) if vote_counts else "Personne"
        
        print(f"\n💀 Éliminé : {eliminated}")

        if eliminated == impostor.name:
            print(f"{Fore.GREEN}✅ VICTOIRE DES CIVILS !{Style.RESET_ALL}")
            for p in AGENTS:
                if p != impostor: 
                    stats[p.name]['score'] += 1
                    stats[p.name]['civil_wins'] += 1
        else:
            print(f"{Fore.RED}❌ VICTOIRE DE L'IMPOSTEUR ({impostor.name}) !{Style.RESET_ALL}")
            stats[impostor.name]['score'] += 3 # Bonus x3 pour victoire Imposteur
            stats[impostor.name]['impostor_wins'] += 1
        
        print("_"*40 + "\n")
        time.sleep(2)

    # --- CLASSEMENT FINAL ---
    print(f"\n{Fore.CYAN}=== 🏆 CLASSEMENT FINAL ({NB_GAMES} PARTIES) ==={Style.RESET_ALL}")
    print(f"{'JOUEUR':<12} | {'SCORE':<6} | {'IMP. WIN':<10} | {'CIV. WIN':<10}")
    print("-" * 50)
    for name, s in sorted(stats.items(), key=lambda x: x[1]['score'], reverse=True):
        print(f"{name:<12} | {s['score']:<6} | {s['impostor_wins']:<10} | {s['civil_wins']:<10}")

if __name__ == "__main__":
    run_simulation()
