import os
import re

import requests

import config


def send_message(to, text):
    print("sending message")
    url = f"{config.OPENWA_API_URL}/{config.SESSION_NAME}/send-message"

    payload = {
        "phone": to,
        "isGroup": False if to.endswith("@c.us") else True,
        "isNewsletter": False,
        "isLid": False,
        "message": text
    }
    print(payload)

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.getenv('OPENWA_API_TOKEN')}"
    }

    try:
        requests.post(url, json=payload, headers=headers)
        return

    except requests.exceptions.RequestException as e:
        print(f"❌ Ошибка запроса: {e}")
        return


def process_message_sending(sender, message_data):
    message_text = message_data.get("body") or message_data.get("content")
    quotedMsg = message_data.get("quotedMsg").get("body") if message_data.get("quotedMsg") else None
    if not sender_is_operator(sender):
        send_message(
            config.ROOT_OPERATORS_GROUP,
            f"{sender}\n"
            f"{f'\nОтветил на сообщение: {quotedMsg}\n\n' if quotedMsg else ''}"
            f"{message_text}"
        )
    else:
        customer_number = process_operator_answer(message_data.get("quotedMsg").get("body"))
        send_message(customer_number, message_text)


def sender_is_operator(sender) -> bool:
    return sender == config.ROOT_OPERATORS_GROUP


def process_operator_answer(text):
    pattern = r"(\b\d+@(?:c|g)\.us\b)"
    match = re.search(pattern, text)

    if match:
        extracted_object = match.group(0)
        return extracted_object

    return None