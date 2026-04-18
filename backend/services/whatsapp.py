"""WhatsApp Cloud API helper."""
import logging
import requests

logger = logging.getLogger(__name__)


def send_whatsapp_text(to: str, text: str, token: str, phone_id: str) -> bool:
    url = f"https://graph.facebook.com/v18.0/{phone_id}/messages"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    try:
        r = requests.post(url, headers=headers, json={
            "messaging_product": "whatsapp", "to": to, "type": "text",
            "text": {"body": text}
        }, timeout=15)
        if r.status_code != 200:
            logger.error(f"WhatsApp send failed: {r.status_code} {r.text[:200]}")
        return r.status_code == 200
    except Exception as e:
        logger.error(f"WhatsApp send error: {e}")
        return False


def mark_as_read(message_id: str, token: str, phone_id: str):
    url = f"https://graph.facebook.com/v18.0/{phone_id}/messages"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    try:
        requests.post(url, headers=headers, json={
            "messaging_product": "whatsapp", "status": "read", "message_id": message_id
        }, timeout=5)
    except:
        pass
