import openai
import os

# 🔑 Charger la clé API OpenAI depuis les variables d'environnement
API_KEY = os.getenv("OPENAI_API_KEY")

# 📌 Modèle OpenAI à utiliser
GPT_MODEL = "gpt-4-turbo"

# ✅ Initialisation du client OpenAI
client = openai.OpenAI(api_key=API_KEY)

# 🎯 Instructions précises pour OpenAI
INSTRUCTIONS_SYSTEME = """
Tu es un expert en cybersécurité. Ta mission est d'analyser toutes les cyberattaques en France en 2025 en utilisant uniquement les sources suivantes :

📡 **SOURCES OFFICIELLES À CONSULTER :**
1️⃣ **01Net** → [https://www.01net.com/actualites/cyberattaques-france-dernieres-fuites-donnees-entreprises-touchees.html](https://www.01net.com/actualites/cyberattaques-france-dernieres-fuites-donnees-entreprises-touchees.html)
2️⃣ **LeMagIT** → [https://www.lemagit.fr/actualites/Cybersecurite](https://www.lemagit.fr/actualites/Cybersecurite)
3️⃣ **ZDNet** → [https://www.zdnet.fr/actualites/cybersecurite-4000080368q.htm](https://www.zdnet.fr/actualites/cybersecurite-4000080368q.htm)

🚨 **Règles strictes :**
- **Ne réponds pas** tant que ces sites n'ont pas été consultés.
- **Ne génère pas de tableau incomplet**.
- **Ne complète que les informations confirmées sur ces sources**.
- **Classe les cyberattaques par ordre chronologique inversé (les plus récentes en premier).**

📊 **Format attendu du tableau Markdown** :
| Date       | Société | Secteur | Incident | Technique | Impact | Description | Source |
|------------|---------|---------|------------|------------|------------|------------|------------|
| 21/02/2025 | Entreprise X | Informatique | **Fuite massive de données** | Hameçonnage | 500 000 utilisateurs touchés | Détails... | [01Net](https://www.01net.com/...) |

✅ **Chaque ligne doit inclure :**
- 📅 **Date exacte de l’attaque**
- 🏢 **Nom de l’organisation ciblée**
- 🔍 **Secteur concerné**
- ⚠️ **Incident détaillé**
- 🎭 **Technique utilisée** (ex: phishing, ransomware, injection SQL…)
- 🎯 **Impact** (nombre de victimes, pertes financières…)
- 📜 **Description courte mais complète**
- 🔗 **Lien vers la source officielle**

🚀 **Maintenant, génère le tableau en Markdown en respectant ces consignes.**
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
