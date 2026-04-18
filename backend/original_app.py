from flask import Flask, request, jsonify
import os
import logging
import requests
from threading import Thread, Lock
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv(override=True)

from bot import (
    get_response, fetch_all_website_data, refresh_all, cache,
    send_text, mark_as_read, clear_session_state, get_user
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")

user_sessions = {}
processed_messages = set()
phone_lock = Lock()
processing_phones = set()

# Session timeout: 1 hour of inactivity
SESSION_TIMEOUT_MINUTES = 60


def update_cache():
    while True:
        logger.info("Refreshing website data from API...")
        fetch_all_website_data()
        time.sleep(1800)


def get_session(phone, name):
    now = datetime.now()

    if phone not in user_sessions:
        user_sessions[phone] = {
            "name": name,
            "phone": phone,
            "language": "english",
            "last_active": now
        }
    else:
        user_sessions[phone]["name"] = name
        last_active = user_sessions[phone].get("last_active")

        # Check if session has expired (1 hour of inactivity)
        if last_active and (now - last_active) > timedelta(minutes=SESSION_TIMEOUT_MINUTES):
            logger.info(f"Session expired for {phone}, clearing conversation state")
            clear_session_state(phone)
            user_sessions[phone] = {
                "name": name,
                "phone": phone,
                "language": "english",
                "last_active": now
            }
        else:
            user_sessions[phone]["last_active"] = now

    return user_sessions[phone]


def handle_message(from_num, name, text):
    """Process message — all responses are text only."""
    session = get_session(from_num, name)

    if not cache.get("products"):
        logger.info("Fetching website data from API...")
        fetch_all_website_data()

    result = get_response(text, session, cache)
    if not result:
        return

    # Normalize to dict
    if not isinstance(result, dict):
        result = {"type": "text", "text": str(result)}

    # If AI provided an intro, send it first
    ai_intro = result.get("ai_intro")
    if ai_intro:
        send_text(from_num, ai_intro, WHATSAPP_TOKEN, PHONE_NUMBER_ID)

    # All responses are text — including product info, order confirm, etc.
    txt = result.get("text", "")
    if txt:
        send_text(from_num, str(txt), WHATSAPP_TOKEN, PHONE_NUMBER_ID)


@app.route('/webhook', methods=['GET'])
def verify():
    if request.args.get('hub.mode') == 'subscribe' and request.args.get('hub.verify_token') == VERIFY_TOKEN:
        return request.args.get('hub.challenge'), 200
    return 'Forbidden', 403


@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    logger.info("Webhook received")

    if data.get('object') != 'whatsapp_business_account':
        return jsonify({"status": "ok"}), 200

    for entry in data.get('entry', []):
        for change in entry.get('changes', []):
            value = change.get('value', {})
            messages = value.get('messages', [])
            contacts = value.get('contacts', [])

            if not messages:
                continue

            msg = messages[0]
            msg_id = msg.get('id', '')

            if msg.get('type') != 'text':
                logger.info(f"Non-text type: {msg.get('type')}")
                return jsonify({"status": "ok"}), 200

            if msg_id in processed_messages:
                logger.info(f"Duplicate msg_id: {msg_id}")
                return jsonify({"status": "ok"}), 200

            from_num = msg.get('from')

            with phone_lock:
                if from_num in processing_phones:
                    logger.info(f"Phone {from_num} already processing")
                    return jsonify({"status": "ok"}), 200
                processing_phones.add(from_num)
                processed_messages.add(msg_id)
                if len(processed_messages) > 500:
                    processed_messages.clear()

            try:
                name = contacts[0].get('profile', {}).get('name', 'Friend') if contacts else 'Friend'
                text = msg.get('text', {}).get('body', '').strip()
                logger.info(f"{name} ({from_num}): {text}")

                # Mark as read
                mark_as_read(msg_id, WHATSAPP_TOKEN, PHONE_NUMBER_ID)

                handle_message(from_num, name, text)
            finally:
                with phone_lock:
                    processing_phones.discard(from_num)

    return jsonify({"status": "ok"}), 200


@app.route('/status')
def status():
    return jsonify({
        "status": "running",
        "products": len(cache.get('products', [])),
        "categories": len(cache.get('categories', [])),
        "sessions": len(user_sessions)
    })


@app.route('/refresh')
def refresh():
    d = refresh_all()
    return jsonify({"refreshed": True, "products": len(d.get('products', [])), "categories": len(d.get('categories', []))})


if __name__ == '__main__':
    logger.info("Starting bot...")
    fetch_all_website_data()
    logger.info(f"Ready: {len(cache.get('products', []))} products, {len(cache.get('categories', []))} categories")
    Thread(target=update_cache, daemon=True).start()
    app.run(host='0.0.0.0', port=5000, debug=False)
