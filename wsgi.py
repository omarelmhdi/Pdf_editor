from flask import Flask, send_from_directory
from bot import create_bot
import threading
import os

app = Flask(__name__)

@app.route('/')
def home():
    return 'Bot is running! 🚀'

@app.route('/<path:path>')
def catch_all(path):
    return 'Bot is running! 🚀'

def run_bot():
    bot = create_bot()
    bot.start_polling()

# تشغيل البوت في thread منفصل
bot_thread = threading.Thread(target=run_bot)
bot_thread.start()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
