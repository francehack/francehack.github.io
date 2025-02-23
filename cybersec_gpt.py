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

# 📌 Fonction pour scraper la section pertinente de 01Net
def fetch_cyberattacks():
    print(f"🔍 Scraping de {SOURCE_URL}...")
    all_entries = []

    try:
        response = requests.get(SOURCE_URL, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        if response.status_code != 200:
            print(f"⚠️ Erreur {response.status_code} sur 01Net")
            logging.warning(f"⚠️ Impossible d'accéder à 01Net - Code {response.status_code}")
            return []

        soup = BeautifulSoup(response.text, "html.parser")

        # 🔍 Trouver le bloc principal contenant les cyberattaques
        main_content = soup.find("div", class_="article-body")  # Adapter la classe si besoin
        if not main_content:
            print("⚠️ Impossible de trouver la section principale.")
            logging.warning("⚠️ Section principale non trouvée.")
            return []

        # 📌 Extraire les paragraphes contenant les cyberattaques
        paragraphs = main_content.find_all("p")
        current_entry = {}
        for para in paragraphs:
            text = para.text.strip()

            # 🟢 Vérification d'un nouveau bloc de cyberattaque
            if text[:5].isdigit() and "/" in text[:5]:  # Exemple : "14/02"
                if current_entry:
                    all_entries.append(current_entry)  # Ajouter l'entrée précédente avant d'en créer une nouvelle

                current_entry = {
                    "date": text,
                    "titre": "Non mentionné",
                    "resume": "",
                    "lien": SOURCE_URL
                }

            # 🏢 Si une entreprise est mentionnée en début de phrase, on l’ajoute comme titre
            elif len(text.split()) > 1 and text.split()[0][0].isupper():
                current_entry["titre"] = text.split(":")[0]  # Extraire le nom de l'entreprise si c'est structuré

            # 📜 Ajouter le texte à la description
            elif current_entry:
                current_entry["resume"] += " " + text

        if current_entry:
            all_entries.append(current_entry)  # Ajouter la dernière entrée

    except requests.RequestException as e:
        print(f"❌ Erreur lors du scraping de 01Net: {e}")
        logging.error(f"❌ Erreur scraping 01Net: {e}")

    return all_entries

# 📌 Fonction pour envoyer les données à OpenAI et générer le tableau Markdown
def generate_cyberattack_table(articles):
    if not articles:
        return "❌ Aucune cyberattaque trouvée sur 01Net."

    articles_text = "\n".join([
        f"- **Date** : {article['date']}\n  **Société** : {article['titre']}\n  **Résumé** : {article['resume']}\n  **Lien** : {article['lien']}"
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
