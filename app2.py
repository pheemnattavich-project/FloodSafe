from flask import Flask, request
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from linebot.exceptions import InvalidSignatureError
import os

# ====== Load ENV ======
CHANNEL_ACCESS_TOKEN = os.getenv("CHANNEL_ACCESS_TOKEN")
CHANNEL_SECRET = os.getenv("CHANNEL_SECRET")

if not CHANNEL_ACCESS_TOKEN or not CHANNEL_SECRET:
    raise RuntimeError("Missing env vars: CHANNEL_ACCESS_TOKEN / CHANNEL_SECRET")

app = Flask(__name__)

line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)


# Simple health check
@app.route("/", methods=["GET"])
def home():
    return "Server is running", 200


# LINE webhook endpoint
@app.route("/callback", methods=["GET", "POST"])
def callback():

    # Allow browser test
    if request.method == "GET":
        return "Callback endpoint ready", 200

    signature = request.headers.get("X-Line-Signature")
    body = request.get_data(as_text=True)

    print("===== WEBHOOK RECEIVED =====")
    print("Signature:", signature)
    print("Body:", body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature")
        return "Invalid signature", 400
    except Exception as e:
        print("Error:", e)
        return "Error", 500

    return "OK", 200


# When user sends ANY text message
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    print("User said:", event.message.text)

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text="Hello :wave: I received your message!")
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)