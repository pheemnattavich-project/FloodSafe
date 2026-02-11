from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.models import (
    MessageEvent, TextMessage, FlexSendMessage
)
from linebot.exceptions import InvalidSignatureError
import json
import os
from linebot.models import TextSendMessage
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, FlexSendMessage
)


# ================= CONFIG =================
CHANNEL_ACCESS_TOKEN = "alXFltNUebrHE+nzSRJ34cJ0ZyvTz7/4cBOlak3Mn1hrzP+37GluOIYLrORuIhwTfYa27g0OyEj4mEbNxnnDlJdaEaDpLLuDiUVLG/rPhSA+l/apPzBUWHQSRgj+McJBLxRlL8mjc4+46ZJ097dbcwdB04t89/1O/w1cDnyilFU="
CHANNEL_SECRET = "28c6ad714dedf449f3c2e8187ad27caa"

DATA_FILE = "thaiwater_wl.json"
# =========================================

app = Flask(__name__)

line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)


def load_station_data():
    if not os.path.exists(DATA_FILE):
        return None
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def search_station(keyword):
    data = load_station_data()
    if not data:
        return None

    keyword = keyword.strip()

    for item in data:
        if keyword in item["location"] or keyword in item["station_name"]:
            return item

    return None

def build_station_flex(data):
    status_color = {
        "น้อย": "#43A047",
        "ปกติ": "#1E88E5",
        "มาก": "#FB8C00",
        "ล้นตลิ่ง": "#E53935"
    }.get(data["status"], "#757575")

    trend_icon = {
        "UP": "⬆️",
        "DOWN": "⬇️",
        "STABLE": "➡️"
    }.get(data["trend"], "")

    return {
        "type": "bubble",
        "size": "kilo",
        "body": {
            "type": "box",
            "layout": "vertical",
            "spacing": "md",
            "contents": [
                {
                    "type": "text",
                    "text": "สถานการณ์ล่าสุด",
                    "weight": "bold",
                    "color": "#2E7D32",
                    "size": "sm"
                },
                {
                    "type": "text",
                    "text": f"อัปเดต {data['update_time']}",
                    "size": "xs",
                    "color": "#9E9E9E"
                },
                {
                    "type": "separator"
                },
                {
                    "type": "text",
                    "text": data["station_name"],
                    "weight": "bold",
                    "size": "lg",
                    "wrap": True
                },
                {
                    "type": "text",
                    "text": data["location"],
                    "size": "sm",
                    "color": "#616161",
                    "wrap": True
                },
                {
                    "type": "box",
                    "layout": "horizontal",
                    "margin": "lg",
                    "contents": [
                        {
                            "type": "text",
                            "text": "สถานะน้ำ",
                            "size": "sm",
                            "color": "#555555",
                            "flex": 2
                        },
                        {
                            "type": "text",
                            "text": data["status"],
                            "size": "sm",
                            "weight": "bold",
                            "color": status_color,
                            "flex": 2
                        }
                    ]
                },
                {
                    "type": "box",
                    "layout": "horizontal",
                    "contents": [
                        {
                            "type": "text",
                            "text": "แนวโน้ม",
                            "size": "sm",
                            "color": "#555555",
                            "flex": 2
                        },
                        {
                            "type": "text",
                            "text": f"{trend_icon} {data['trend']}",
                            "size": "sm",
                            "weight": "bold",
                            "flex": 2
                        }
                    ]
                }
            ]
        }
    }


@app.route("/callback", methods=["POST"])
def callback():
    # 1. ดึง signature (อาจไม่มีตอน verify)
    signature = request.headers.get("X-Line-Signature", "")

    # 2. ดึง body
    body = request.get_data(as_text=True)

    # 🔴 สำคัญมาก: ตอน VERIFY body อาจว่าง
    if not body:
        return "OK", 200

    # 3. พยายาม handle event
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        # ❌ อย่า abort ตอน verify
        return "OK", 200
    except Exception as e:
        print("ERROR:", e)
        return "OK", 200

    return "OK", 200


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_text = event.message.text.strip()

    result = search_station(user_text)

    if not result:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="❌ ไม่พบสถานีที่ค้นหา กรุณาพิมพ์ชื่อจังหวัด / อำเภอ / ตำบล")
        )
        return

    flex = build_station_flex(result)

    line_bot_api.reply_message(
        event.reply_token,
        FlexSendMessage(
            alt_text="สถานการณ์น้ำล่าสุด",
            contents=flex
        )
    )



if __name__ == "__main__":
    app.run(port=4040, debug=True)
