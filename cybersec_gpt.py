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

# 📌 Fonction pour scraper uniquement la section pertinente de 01Net
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

        # 🔍 Trouver la section de l’article à scraper
        sommaire = soup.find("h2", string="Sommaire")  # Trouver l'en-tête Sommaire
        votre_opinion = soup.find("h2", string="Votre opinion")  # Trouver la fin de l'article

        if not sommaire or not votre_opinion:
            print("⚠️ Impossible de trouver les sections 'Sommaire' et 'Votre opinion'.")
            logging.warning("⚠️ Sections Sommaire et Votre opinion non trouvées.")
            return []

        # Extraire uniquement le contenu situé entre ces deux balises
        content_section = []
        for element in sommaire.find_next_siblings():
            if element == votre_opinion:
                break  # Arrêter le scraping à "Votre opinion"
            content_section.append(element.text.strip())

        # 🛠️ Nettoyage du texte
        content_text = "\n".join(content_section).strip()

        # 📌 Séparer chaque cyberattaque en utilisant les titres en gras comme repère
        entries = content_text.split("\n\n")
        for entry in entries:
            lines = entry.split("\n")
            if len(lines) > 1:  # Vérifier qu'il y a bien une structure
                date = lines[0].strip()  # La première ligne est la date
                title = lines[1].strip()  # La deuxième ligne est l’entreprise concernée
                description = " ".join(lines[2:]).strip()  # Le reste est la description de l’attaque

                all_entries.append({
                    "date": date,
                    "titre": title,
                    "resume": description,
                    "lien": SOURCE_URL  # Même lien pour toutes les attaques
                })

    except requests.RequestException as e:
        print(f"❌ Erreur lors du scraping de 01Net: {e}")
        logging.error(f"❌ Erreur scraping 01Net: {e}")

    return all_entries

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
