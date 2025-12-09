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

NB_GAMES = 7
NB_ROUNDS = 3

AGENTS = [
    Player("Mistral", "mistral"),
    Player("DeepSeek", "deepseek"),
    Player("Gemini", "gemini")
]

def run_simulation():
    print(f"{Fore.CYAN}=== 🕵️  BENCHMARK UNDERCOVER : EXPERT MODE & KPI ==={Style.RESET_ALL}\n")

    # 1. INITIALISATION DES STATS
    stats = {
        agent.name: {
            "games_played": 0,
            "civil_wins": 0,
            "impostor_wins": 0,
            "votes_cast_against_impostor": 0,
            "votes_cast_against_civil": 0,
            "manipulation_score": 0,
            "vote_none_count": 0  # Nouveau KPI : Vote Blanc
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
        current_players = AGENTS.copy()
        random.shuffle(current_players)

        print(f"{Fore.YELLOW}--- PARTIE {game_id} : {civil_word} (Majorité) vs {impostor_word} (Imposteur) ---{Style.RESET_ALL}")
        
        for p in current_players:
            p.set_word(impostor_word if p == impostor else civil_word)
            stats[p.name]['games_played'] += 1

        history = "" 

        # --- GAME LOOP ---
        for round_num in range(1, NB_ROUNDS + 1):
            print(f"\n{Style.BRIGHT}🔁 Round {round_num}{Style.RESET_ALL}")
            for p in current_players:
                res = p.speak(history, round_num)
                msg = res.get('message', '...')
                analysis = res.get('context_analysis', 'Ras')
                
                role_color = Fore.RED if p == impostor else Fore.GREEN
                print(f"{role_color}{p.name:<10}{Style.RESET_ALL} : {Style.BRIGHT}\"{msg}\"{Style.RESET_ALL}")
                print(f"{Style.DIM}   └─ 🧠 {analysis}{Style.RESET_ALL}")
                history += f"- {p.name} : \"{msg}\"\n"

        # --- VOTES ---
        print(f"\n{Fore.MAGENTA}🗳️  VOTE ET JUSTIFICATIONS{Style.RESET_ALL}")
        votes = {}
        
        for p in current_players:
            others = [a.name for a in AGENTS if a.name != p.name]
            
            v_res = p.vote(history, others)
            target = v_res.get('vote_for', 'Personne')
            reasoning = v_res.get('thought', '...')
            
            votes[p.name] = target
            
            print(f"   🔎 {p.name} vote : {Fore.WHITE if target=='Personne' else Fore.RED}{target}{Style.RESET_ALL}")
            print(f"      {Style.DIM}📝 {reasoning}{Style.RESET_ALL}\n")

            # === KPI UPDATE ===
            if target == "Personne":
                stats[p.name]['vote_none_count'] += 1
            elif p.name != impostor.name: # Si c'est un Civil qui vote quelqu'un
                if target == impostor.name:
                    stats[p.name]['votes_cast_against_impostor'] += 1
                else:
                    stats[p.name]['votes_cast_against_civil'] += 1
                    stats[impostor.name]['manipulation_score'] += 1

        # --- RÉSULTAT ---
        vote_counts = {}
        for t in votes.values():
            vote_counts[t] = vote_counts.get(t, 0) + 1
        
        # Si majorité de "Personne", personne n'est éliminé
        if vote_counts.get("Personne", 0) > 1: # S'il y a au moins 2 votes blancs
            eliminated = "Personne"
        else:
            # On retire les votes "Personne" du décompte pour trouver la victime
            valid_votes = {k:v for k,v in vote_counts.items() if k != "Personne"}
            if valid_votes:
                eliminated = max(valid_votes, key=valid_votes.get)
            else:
                eliminated = "Personne"

        print(f"💀 Éliminé : {eliminated}")

        # Victoire : Si l'imposteur survit (Personne éliminé ou Civil éliminé), il gagne
        if eliminated == impostor.name:
            print(f"{Fore.GREEN}✅ VICTOIRE DES CIVILS !{Style.RESET_ALL}")
            for p in AGENTS:
                if p != impostor: stats[p.name]['civil_wins'] += 1
        else:
            print(f"{Fore.RED}❌ VICTOIRE DE L'IMPOSTEUR ({impostor.name}) !{Style.RESET_ALL}")
            stats[impostor.name]['impostor_wins'] += 1
        
        print("_"*40 + "\n")
        time.sleep(2)

    # --- TABLEAU DE BORD KPI ---
    print(f"\n{Fore.CYAN}=== 📊 ANALYSE DE L'INTELLIGENCE SOCIALE ({NB_GAMES} PARTIES) ==={Style.RESET_ALL}")
    
    headers = ["MODÈLE", "WIN RATE", "PRÉCISION", "MANIPULATION", "CONFUSION", "% VOTE BLANC"]
    print(f"{headers[0]:<15} | {headers[1]:<10} | {headers[2]:<10} | {headers[3]:<12} | {headers[4]:<10} | {headers[5]}")
    print("-" * 90)

    for name, s in stats.items():
        total_wins = s['civil_wins'] + s['impostor_wins']
        win_rate = (total_wins / s['games_played'] * 100) if s['games_played'] > 0 else 0
        
        total_votes_as_civil = s['votes_cast_against_impostor'] + s['votes_cast_against_civil']
        # Attention division par zéro si l'IA a toujours voté blanc
        precision = (s['votes_cast_against_impostor'] / total_votes_as_civil * 100) if total_votes_as_civil > 0 else 0
        
        manipulation = s['manipulation_score'] 
        confusion = (s['votes_cast_against_civil'] / total_votes_as_civil * 100) if total_votes_as_civil > 0 else 0
        
        # % de votes blancs
        vote_blanc_pct = (s['vote_none_count'] / s['games_played'] * 100)

        print(f"{name:<15} | {win_rate:5.1f}%     | {precision:5.1f}%     | {manipulation:^12} | {confusion:5.1f}%     | {vote_blanc_pct:5.1f}%")

if __name__ == "__main__":
    run_simulation()
   
