
from flask import Flask
from bot import create_bot
import threading

app = Flask(__name__)

@app.route('/')
def home():
    return 'Bot is running!'

def run_bot():
    bot = create_bot()

# تشغيل البوت في thread منفصل
bot_thread = threading.Thread(target=run_bot)
bot_thread.start()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
