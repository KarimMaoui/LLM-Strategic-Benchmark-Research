import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

print(f"🔑 Clé testée : {api_key[:10]}...")

try:
    genai.configure(api_key=api_key)
    print("📡 Connexion à Google...")
    
    # On demande à Google : "Qu'est-ce que j'ai le droit d'utiliser ?"
    models = genai.list_models()
    
    print("\n✅ MODÈLES DISPONIBLES POUR TOI :")
    found_flash = False
    for m in models:
        if "generateContent" in m.supported_generation_methods:
            # On affiche le nom technique exact (ex: models/gemini-1.5-flash)
            print(f" - {m.name}")
            if "flash" in m.name:
                found_flash = True

    if not found_flash:
        print("\n❌ Aucun modèle 'flash' trouvé. Essaie 'gemini-pro'.")
    else:
        print("\n🎉 Flash est là ! Copie le nom EXACT ci-dessus (sans 'models/').")

except Exception as e:
    print(f"\n❌ ERREUR CRITIQUE : {e}")
