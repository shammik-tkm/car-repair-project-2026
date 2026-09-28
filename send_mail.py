from flask import Flask, request
import requests
import smtplib
from email.mime.text import MIMEText
import os

app = Flask(__name__)

# --- НАСТРОЙКИ ---
BOT_TOKEN = '8776881285:AAFyC5M3EPacriPY6cqGuSyHh9I0T8qmS28'
CHAT_ID   = '6990139455'
MY_EMAIL  = 'dev.shammik.tm@gmail.com'
# -----------------

# Папка, где лежит этот скрипт (там же должен быть index.html)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

@app.route('/')
def index():
    with open(os.path.join(BASE_DIR, 'index.html'), 'r', encoding='utf-8') as f:
        return f.read()

@app.route('/send', methods=['POST'])
def send():
    # 1. Получаем данные
    name    = request.form.get('name', '').strip()
    phone   = request.form.get('phone', '').strip()
    email   = request.form.get('email', '').strip()
    service = request.form.get('service', '').strip() or 'Nicht angegeben'
    message = request.form.get('message', '').strip()

    if not name or not phone or not message:
        return "Bitte füllen Sie alle Pflichtfelder aus.", 400

    # 2. Формируем сообщение для Telegram
    tg_text = (
        "🔔 <b>Neue Anfrage von der Website</b>\n\n"
        f"👤 <b>Name:</b> {name}\n"
        f"📞 <b>Telefon:</b> {phone}\n"
        f"📧 <b>E-Mail:</b> {email or 'Nicht angegeben'}\n"
        f"🛠 <b>Leistung:</b> {service}\n"
        f"📝 <b>Nachricht:</b>\n{message}"
    )

    # 3. Отправка текста в Telegram
    r = requests.post(
        f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage',
        data={'chat_id': CHAT_ID, 'text': tg_text, 'parse_mode': 'HTML'}
    )
    print("Telegram text response:", r.status_code, r.text)

    # 4. Отправка фото (если есть)
    photo = request.files.get('photo')
    if photo and photo.filename:
        r2 = requests.post(
            f'https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto',
            data={'chat_id': CHAT_ID, 'caption': f'📸 Foto zur Anfrage von {name}'},
            files={'photo': (photo.filename, photo.stream, photo.mimetype)}
        )
        print("Telegram photo response:", r2.status_code, r2.text)

    
    try:
        msg = MIMEText(
            f"Name: {name}\nTelefon: {phone}\nEmail: {email}\nLeistung: {service}\n\nNachricht:\n{message}",
            'plain', 'utf-8'
        )
        msg['Subject'] = f'Neue Anfrage von {name}'
        msg['From'] = MY_EMAIL
        msg['To'] = MY_EMAIL
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as s:
            s.login(MY_EMAIL, 'ПАРОЛЬ_ПРИЛОЖЕНИЯ')
            s.send_message(msg)
    except Exception as e:
        print(f"Email error: {e}")

    return "<h2 style='text-align:center;margin-top:50px;font-family:sans-serif;'>Vielen Dank! Ihre Anfrage wurde gesendet.</h2>"

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)