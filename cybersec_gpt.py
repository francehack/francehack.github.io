import openai
import os

# 🔑 Charger la clé API depuis les variables d'environnement GitHub
API_KEY = os.getenv("OPENAI_API_KEY")

# 📌 ID du GPT personnalisé (ex : g-abc123xyz456)
GPT_ID = "g-67b9896d3d3881918073bac8dc5faa91"  # Remplace par l'ID exact de ton GPT

def get_cyberattacks():
    response = openai.ChatCompletion.create(
        model=GPT_ID,  # Spécifier ton GPT personnalisé
        messages=[
            {"role": "system", "content": "Tu es un expert en cybersécurité qui génère des tableaux de cyberattaques."},
            {"role": "user", "content": "Génère le tableau des cyberattaques de 2025 en Markdown."}
        ],
        temperature=0.7
    )
    return response["choices"][0]["message"]["content"]

if __name__ == "__main__":
    result = get_cyberattacks()

    with open("cyberattaques_2025.md", "w", encoding="utf-8") as f:
        f.write(result)

    print("📂 Fichier 'cyberattaques_2025.md' mis à jour avec ton GPT personnalisé !")
