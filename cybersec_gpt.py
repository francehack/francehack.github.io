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

# 📡 URL de 01Net à scraper
SOURCE_URL = "https://www.01net.com/actualites/cyberattaques-france-dernieres-fuites-donnees-entreprises-touchees.html"

# 📌 Fonction pour scraper les cyberattaques depuis 01Net
def fetch_cyberattacks():
    print(f"🔍 Scraping de {SOURCE_URL}...")
    all_articles = []

    try:
        response = requests.get(SOURCE_URL, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        if response.status_code != 200:
            print(f"⚠️ Erreur {response.status_code} sur 01Net")
            logging.warning(f"⚠️ Impossible d'accéder à 01Net - Code {response.status_code}")
            return []

        soup = BeautifulSoup(response.text, "html.parser")

        # 🔍 Extraction des articles (basé sur la structure HTML de 01Net)
        articles = soup.find_all("article")[:10]  # On limite à 10 articles récents

        for article in articles:
            title = article.find("h2").text.strip() if article.find("h2") else "Titre inconnu"
            summary = article.find("p").text.strip() if article.find("p") else "Résumé non disponible"
            link = article.find("a")["href"] if article.find("a") else SOURCE_URL
            date = article.find("time").text.strip() if article.find("time") else "Date inconnue"

            # Nettoyage et structuration des données
            all_articles.append({
                "date": date,
                "titre": title,
                "resume": summary,
                "lien": f"https://www.01net.com{link}" if not link.startswith("http") else link
            })

    except requests.RequestException as e:
        print(f"❌ Erreur lors du scraping de 01Net: {e}")
        logging.error(f"❌ Erreur scraping 01Net: {e}")

    return all_articles

# 📌 Fonction pour envoyer les données à OpenAI et générer le tableau Markdown
def generate_cyberattack_table(articles):
    if not articles:
        return "❌ Aucune cyberattaque trouvée sur 01Net."

    articles_text = "\n".join([
        f"- **Date** : {article['date']}\n  **Titre** : {article['titre']}\n  **Résumé** : {article['resume']}\n  **Lien** : {article['lien']}"
        for article in articles
    ])

    prompt = f"""
    Voici une liste d'articles récents sur les cyberattaques en France extraits de 01Net :

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
    print("🚀 Scraping de 01Net...")
    articles = fetch_cyberattacks()

    print("🚀 Génération du tableau avec OpenAI...")
    markdown_table = generate_cyberattack_table(articles)

    with open("cyberattaques_2025.md", "w", encoding="utf-8") as f:
        f.write(markdown_table)

    logging.info("✅ Fichier 'cyberattaques_2025.md' mis à jour avec succès !")
    print("✅ Le tableau des cyberattaques a été généré.")
