import telebot
import requests

# ===== CONFIGURATION =====
import os

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
MAMOUTH_API_KEY = os.environ.get("MAMOUTH_API_KEY")
MAMOUTH_API_URL = "https://api.mammouth.ai/v1/chat/completions"

bot = telebot.TeleBot(TELEGRAM_TOKEN)

# ===== CONFIGURATION DEEPSEEK =====
MODEL_NAME = "deepseek-v3.2"
TIMEOUT = 90

# ===== PREPROMPT SYSTÈME =====
SYSTEM_PROMPT = """Tu es un assistant IA accessible via un bot Telegram connecté à Deepseek-v3.2 via l'API Mammouth. Tu es le bot du Caveau, disponible pour répondre aux membres du canal. Tu t'appelles Mnemosyne en référence à la Titanide mythologique grecque.

RÈGLES STRICTES :
- Réponds de manière CONCISE et EXHAUSTIVE
- Réponds TOUJOURS en français
- Tu ne lis PAS la discussion dans le canal du Caveau, sauf si ta commande d'appel est effectuée
- Tu ne peux PAS générer d'images
- Tu ne peux PAS naviguer sur des sites web
- Si on te demande une image ou de la navigation, explique poliment tes limites
- Reste factuel et précis
- Tu t'exprimes correctement
- Tu utilises les smileys de façon pertinente et sans excès"""

# ===== FONCTION APPEL MAMOUTH =====
def ask_mamouth(question):
    try:
        headers = {
            "Authorization": f"Bearer {MAMOUTH_API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": MODEL_NAME,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": question}
            ]
        }

        response = requests.post(
            MAMOUTH_API_URL,
            headers=headers,
            json=payload,
            timeout=TIMEOUT
        )
        response.raise_for_status()

        data = response.json()
        return data['choices'][0]['message']['content']

    except requests.exceptions.Timeout:
        return f"⏱️ Délai d'attente dépassé ({TIMEOUT}s). Veuillez réessayer."
    except requests.exceptions.RequestException as e:
        return f"❌ Erreur API Mamouth : {str(e)}"
    except Exception as e:
        return f"❌ Erreur inattendue : {str(e)}"

# ===== COMMANDE /llm =====
@bot.message_handler(commands=['llm'])
def handle_llm(message):
    try:
        args = message.text.split(maxsplit=1)

        if len(args) < 2:
            bot.reply_to(
                message,
                "❌ Usage : /llm [votre question]\n💡 Exemple : /llm Quel est l'homme le plus fort du monde ?"
            )
            return

        question = args[1]

        # Appel API direct
        answer = ask_mamouth(question)

        # Réponse
        bot.reply_to(message, answer)

    except Exception as e:
        bot.reply_to(message, f"❌ Erreur : {str(e)}")

# ===== COMMANDE /start =====
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    welcome_text = """👋 Bienvenue sur Mnemosyne, le bot du Caveau !

🤖 Je suis alimentée par Deepseek-v3.2 via l'API Mammouth.

📝 Utilisation :
/llm [votre question]

💡 Exemple :
/llm Quel est l'homme le plus fort du monde ?

Je suis là pour répondre à vos questions de manière concise et précise ! 🧠"""

    bot.reply_to(message, welcome_text)

# ===== DÉMARRAGE =====
print("🚀 Mnemosyne (Bot Deepseek) démarré !")
print(f"🤖 Modèle : {MODEL_NAME}")
bot.infinity_polling()
