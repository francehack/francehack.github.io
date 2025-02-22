import openai
import os
import requests
from bs4 import BeautifulSoup
import time
import logging
import datetime

# 🔑 Charger la clé API OpenAI depuis une variable d'environnement
API_KEY = os.getenv("OPENAI_API_KEY")

# 📌 Modèle OpenAI à utiliser
GPT_MODEL = "gpt-4-turbo"

# ✅ Initialisation du client OpenAI
client = openai.OpenAI(api_key=API_KEY)

# 📂 Configuration du fichier de log
logging.basicConfig(filename="log.txt", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# 📡 🔍 SOURCES OFFICIELLES À SCRAPER
SOURCES = {
    "01Net": "https://www.01net.com/actualites/cyberattaques-france-dernieres-fuites-donnees-entreprises-touchees.html",
    "LeMagIT": "https://www.lemagit.fr/actualites/Cybersecurite",
    "ZDNet": "https://www.zdnet.fr/actualites/cybersecurite-4000080368q.htm"
}

# 📌 Instructions pour OpenAI
INSTRUCTIONS_SYSTEME = """
Tu es un expert en cybersécurité. Ta mission est de répertorier les cyberattaques survenues en France en 2025.
Tu dois respecter les règles suivantes :
1️⃣ Scanner toutes les sources avant de répondre.
2️⃣ Générer un tableau en Markdown avec les colonnes suivantes :
   | Date       | Société | Secteur | Incident | Technique | Impact | Description | Source |
3️⃣ Classer les cyberattaques par ordre chronologique inversé (les plus récentes en premier).
4️⃣ Mentionner la source de chaque cyberattaque avec un lien.
5️⃣ Ne générer un tableau que si au moins 10 cyberattaques sont trouvées.
6️⃣ Si une source est inaccessible, afficher un message d’alerte et continuer avec les autres.
7️⃣ Formater la réponse uniquement en Markdown.
"""

# 📌 Fonction pour scraper les cyberattaques depuis les sources officielles
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
                link = article.find("a")["href"] if article.find("a") else url
                all_articles.append({"source": source, "titre": title, "lien": link})

        except requests.RequestException as e:
            print(f"❌ Erreur lors du scraping de {source}: {e}")
            logging.error(f"❌ Erreur scraping {source}: {e}")

    return all_articles

# 📌 Fonction pour générer le tableau Markdown avec OpenAI
def generate_cyberattack_table(articles):
    # 📌 Construire une requête OpenAI avec les cyberattaques trouvées
    articles_text = "\n".join([f"- {article['source']} : {article['titre']} ({article['lien']})" for article in articles])

    prompt = f"""
    Voici une liste d'articles sur les cyberattaques en France en 2025 :
    {articles_text}

    Analyse ces articles et génère un tableau Markdown formaté en respectant ces règles :
    {INSTRUCTIONS_SYSTEME}
    """

    try:
        response = client.chat.completions.create(
            model=GPT_MODEL,
            messages=[
                {"role": "system", "content": INSTRUCTIONS_SYSTEME},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        return response.choices[0].message.content
    except openai.OpenAIError as e:
        logging.error(f"❌ Erreur OpenAI : {e}")
        return None

# 📌 Exécuter le scraping, analyser et sauvegarder les résultats
if __name__ == "__main__":
    print("🚀 Scraping des sources...")
    articles = fetch_cyberattacks()

    if len(articles) == 0:
        print("❌ Aucune cyberattaque trouvée, vérifie les sources.")
        exit(1)

    print("🚀 Génération du tableau avec OpenAI...")
    markdown_table = generate_cyberattack_table(articles)

    if markdown_table:
        with open("cyberattaques_2025.md", "w", encoding="utf-8") as f:
            f.write(markdown_table)

        logging.info("✅ Fichier 'cyberattaques_2025.md' mis à jour avec succès !")
        print("✅ Le tableau des cyberattaques a été généré.")
    else:
        print("❌ Erreur lors de la génération du tableau, consulte log.txt.")
