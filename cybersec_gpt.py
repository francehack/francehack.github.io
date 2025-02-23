import openai
import os
import requests
from bs4 import BeautifulSoup
import logging

# 🔑 Charger la clé API OpenAI
API_KEY = os.getenv("OPENAI_API_KEY")

# 📌 Modèle OpenAI utilisé
GPT_MODEL = "gpt-4-turbo"

# ✅ Initialisation du client OpenAI
client = openai.Client(api_key=API_KEY)

# 📂 Configuration du log
logging.basicConfig(filename="log.txt", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# 📡 SOURCES FIABLES À SCRAPER
SOURCES = {
    "01Net": "https://www.01net.com/actualites/cyberattaques-france-dernieres-fuites-donnees-entreprises-touchees.html",
    "LeMagIT": "https://www.lemagit.fr/actualites/Cybersecurite",
    "ZDNet": "https://www.zdnet.fr/actualites/cybersecurite-4000080368q.htm"
}

# 📌 Fonction pour scraper les cyberattaques
def fetch_cyberattacks():
    all_articles = []
    for source, url in SOURCES.items():
        print(f"🔍 Scraping {source}...")
        try:
            response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
            if response.status_code != 200:
                print(f"⚠️ Erreur {response.status_code} sur {source}")
                logging.warning(f"⚠️ Impossible d'accéder à {source} - Code {response.status_code}")
                continue

            soup = BeautifulSoup(response.text, "html.parser")
            articles = soup.find_all("article")[:5]  # Récupérer les 5 derniers articles

            for article in articles:
                title = article.find("h2").text.strip() if article.find("h2") else "Titre inconnu"
                summary = article.find("p").text.strip() if article.find("p") else "Résumé non disponible"
                link = article.find("a")["href"] if article.find("a") else url
                all_articles.append({
                    "source": source,
                    "titre": title,
                    "resume": summary,
                    "lien": link
                })

        except requests.RequestException as e:
            print(f"❌ Erreur lors du scraping de {source}: {e}")
            logging.error(f"❌ Erreur scraping {source}: {e}")

    return all_articles

# 📌 Fonction pour envoyer les données à OpenAI et générer le tableau Markdown
def generate_cyberattack_table(articles):
    if not articles:
        return "❌ Aucune cyberattaque trouvée dans les sources disponibles."

    articles_text = "\n".join([
        f"- **Source** : {article['source']}\n  **Titre** : {article['titre']}\n  **Résumé** : {article['resume']}\n  **Lien** : {article['lien']}"
        for article in articles
    ])

    prompt = f"""
    Voici une liste d'articles confirmés sur les cyberattaques en France en 2025 :

    {articles_text}

    🔥 **Objectif** :
    - Analyse ces informations et génère un tableau Markdown.
    - Format attendu :
    | Date       | Société | Secteur | Incident | Technique | Impact | Description | Source |
    - Si une donnée est inconnue, écris "Non mentionné".
    - Utilise les sources mentionnées.

    🚀 Maintenant, génère le tableau en Markdown.
    """

    try:
        response = client.chat.completions.create(
            model=GPT_MODEL,
            messages=[
                {"role": "system", "content": "Tu es un expert en cybersécurité."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        return response.choices[0].message.content
    except openai.OpenAIError as e:
        logging.error(f"❌ Erreur OpenAI : {e}")
        return "❌ Erreur OpenAI lors de la génération du tableau."

# 📌 Exécuter le scraping et générer le fichier
if __name__ == "__main__":
    print("🚀 Scraping des sources...")
    articles = fetch_cyberattacks()

    print("🚀 Génération du tableau avec OpenAI...")
    markdown_table = generate_cyberattack_table(articles)

    with open("cyberattaques_2025.md", "w", encoding="utf-8") as f:
        f.write(markdown_table)

    logging.info("✅ Fichier 'cyberattaques_2025.md' mis à jour avec succès !")
    print("✅ Le tableau des cyberattaques a été généré.")
