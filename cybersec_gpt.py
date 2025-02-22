import openai
import os

# 🔑 Charger la clé API OpenAI depuis les variables d'environnement GitHub
API_KEY = os.getenv("OPENAI_API_KEY")

# 📌 ID du GPT personnalisé (à récupérer sur OpenAI)
GPT_ID = "g-67b9896d3d3881918073bac8dc5faa91"  # Remplace par ton ID exact

# ✅ Initialiser le client OpenAI
client = openai.OpenAI(api_key=API_KEY)

# 📌 Fonction pour récupérer les cyberattaques depuis ton GPT personnalisé
def get_cyberattacks():
    response = client.chat.completions.create(
        model=GPT_ID,  # Utilisation du GPT personnalisé
        messages=[
            {"role": "system", "content": "Tu es un expert en cybersécurité qui génère des tableaux de cyberattaques."},
            {"role": "user", "content": "Génère le tableau des cyberattaques de 2025 en Markdown."}
        ],
        temperature=0.7
    )
    return response.choices[0].message.content

# 📌 Exécuter la requête et sauvegarder le résultat
if __name__ == "__main__":
    try:
        result = get_cyberattacks()

        with open("cyberattaques_2025.md", "w", encoding="utf-8") as f:
            f.write(result)

        print("✅ Fichier 'cyberattaques_2025.md' mis à jour avec succès !")
    except Exception as e:
        print(f"❌ Erreur lors de l'exécution du script : {e}")

