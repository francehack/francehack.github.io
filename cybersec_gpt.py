import openai
import os

# 🔑 Charger la clé API OpenAI depuis les variables d'environnement
API_KEY = os.getenv("OPENAI_API_KEY")

# 📌 Modèle OpenAI à utiliser
GPT_MODEL = "gpt-4-turbo"

# ✅ Initialisation du client OpenAI
client = openai.OpenAI(api_key=API_KEY)

# 🎯 Instructions simplifiées pour OpenAI
INSTRUCTIONS_SYSTEME = """
Tu es un expert en cybersécurité. Génère un tableau des cyberattaques ayant eu lieu en France en 2025.

📌 **Format du tableau en Markdown** :
| Date       | Société | Secteur | Incident | Technique | Impact | Description | Source |
|------------|---------|---------|------------|------------|------------|------------|------------|
| 21/02/2025 | Entreprise X | Informatique | **Fuite massive de données** | Hameçonnage | 500 000 utilisateurs touchés | Détails... | Source officielle |

✅ **Règles strictes** :
- Afficher uniquement les cyberattaques confirmées en 2025.
- Classer les attaques par **ordre chronologique inversé** (les plus récentes en premier).
- Si l'impact est inconnu, écrire **"Impact inconnu"**.
- Ne pas inventer d'informations.
- Toujours structurer la réponse en **Markdown**.

🚀 Maintenant, génère le tableau des cyberattaques en respectant ces consignes.
"""

# 📌 Fonction pour interroger OpenAI
def get_cyberattacks():
    response = client.chat.completions.create(
        model=GPT_MODEL,
        messages=[
            {"role": "system", "content": "Tu es un assistant expert en cybersécurité."},
            {"role": "user", "content": INSTRUCTIONS_SYSTEME}
        ],
        temperature=0.7
    )
    return response.choices[0].message.content

# 📌 Exécuter la requête et sauvegarder le résultat
if __name__ == "__main__":
    print("🚀 Interrogation de l'API OpenAI...")
    result = get_cyberattacks()

    if result:
        with open("cyberattaques_2025.md", "w", encoding="utf-8") as f:
            f.write(result)

        print("✅ Le tableau des cyberattaques a été généré avec succès !")
    else:
        print("❌ Erreur lors de la récupération des cyberattaques.")
