
import json
import os
import urllib.request
from http.server import BaseHTTPRequestHandler

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
WEBHOOK_SECRET = os.environ.get("TELEGRAM_WEBHOOK_SECRET")


def telegram(method, data):
    url = f"https://api.telegram.org/bot{TOKEN}/{method}"
    request = urllib.request.Request(
        url,
        data=json.dumps(data).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=8) as response:
        return json.loads(response.read().decode("utf-8"))


def main_menu():
    return {
        "inline_keyboard": [
            [{"text": "🛂 طلبات الفيزا", "callback_data": "visa"}],
            [{"text": "📅 مواعيد BLS / VFS", "callback_data": "appointments"}],
            [{"text": "📄 الوثائق المطلوبة", "callback_data": "documents"}],
            [{"text": "💶 الأسعار والرسوم", "callback_data": "prices"}],
            [{"text": "✈️ الطيران والفنادق", "callback_data": "travel"}],
            [{"text": "👨‍💼 التواصل مع الوكالة", "callback_data": "contact"}],
        ]
    }


def back_button():
    return {
        "inline_keyboard": [
            [{"text": "⬅️ القائمة الرئيسية", "callback_data": "menu"}]
        ]
    }


def send(chat_id, text, keyboard=None):
    data = {"chat_id": chat_id, "text": text}
    if keyboard:
        data["reply_markup"] = keyboard
    telegram("sendMessage", data)


def show_menu(chat_id):
    send(
        chat_id,
        "✈️ مرحباً بك في MALIK TRAVEL!\n\n"
        "اختار الخدمة اللي تحتاجها من الأزرار:",
        main_menu(),
    )


def handle_update(update):
    if "callback_query" in update:
        query = update["callback_query"]
        chat_id = query["message"]["chat"]["id"]
        choice = query.get("data", "")

        telegram("answerCallbackQuery", {"callback_query_id": query["id"]})

        if choice == "menu":
            show_menu(chat_id)

        elif choice == "visa":
            keyboard = {
                "inline_keyboard": [
                    [{"text": "🇫🇷 فرنسا", "callback_data": "country_fr"}],
                    [{"text": "🇪🇸 إسبانيا", "callback_data": "country_es"}],
                    [{"text": "🇮🇹 إيطاليا", "callback_data": "country_it"}],
                    [{"text": "🇨🇦 كندا", "callback_data": "country_ca"}],
                    [{"text": "🌍 دولة أخرى", "callback_data": "country_other"}],
                    [{"text": "⬅️ رجوع", "callback_data": "menu"}],
                ]
            }
            send(chat_id, "🌍 اختار الدولة اللي حاب تسافر ليها:", keyboard)

        elif choice.startswith("country_"):
            send(
                chat_id,
                "🛂 معلومات الفيزا\n\n"
                "الوثائق والشروط تختلف حسب جنسيتك، ونوع الفيزا وبلد الوجهة.\n"
                "تحقق من الموقع الرسمي للقنصلية قبل تقديم الملف. "
                "هذه القائمة لا تتحقق من الشروط أو المواعيد مباشرة.",
                back_button(),
            )

        elif choice == "appointments":
            send(
                chat_id,
                "📅 مواعيد BLS / VFS\n\n"
                "المواعيد المتاحة تتغير باستمرار. تحقق من الموقع الرسمي "
                "لمركز التأشيرات المعني. البوت لا يعرض المواعيد المباشرة.",
                back_button(),
            )

        elif choice == "documents":
            send(
                chat_id,
                "📄 الوثائق المطلوبة\n\n"
                "اختار الدولة من قسم «طلبات الفيزا» لمعرفة معلومات عامة. "
                "القائمة الرسمية تختلف حسب نوع التأشيرة ووضعية كل شخص.",
                back_button(),
            )

        elif choice == "prices":
            send(
                chat_id,
                "💶 الأسعار والرسوم\n\n"
                "رسوم التأشيرة والخدمات قابلة للتغيير. تحقق من الأسعار "
                "الرسمية قبل الدفع. لم تُضف أسعار الوكالة إلى البوت بعد.",
                back_button(),
            )

        elif choice == "travel":
            send(
                chat_id,
                "✈️ الطيران والفنادق\n\n"
                "معلومات الأسعار والتوفر تحتاج إلى تحقق مباشر. "
                "لم تتم إضافة نظام حجز إلى هذا البوت بعد.",
                back_button(),
            )

        elif choice == "contact":
            send(
                chat_id,
                "👨‍💼 التواصل مع MALIK TRAVEL\n\n"
                "أضفنا زر التواصل، لكن يلزم إدخال رقم الهاتف أو رابط "
                "الصفحة الرسمية للوكالة حتى يستطيع الزبون الوصول إليكم.",
                back_button(),
            )

        return

    message = update.get("message", {})
    chat_id = message.get("chat", {}).get("id")
    text = message.get("text", "")

    if not chat_id:
        return

    if text.startswith("/start") or text.startswith("/help"):
        show_menu(chat_id)
    else:
        send(
            chat_id,
            "من فضلك استعمل الأزرار لاختيار الخدمة المطلوبة 👇",
            main_menu(),
        )


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(b"MALIK TRAVEL bot is ready.")

    def do_POST(self):
        if WEBHOOK_SECRET:
            supplied = self.headers.get(
                "X-Telegram-Bot-Api-Secret-Token", ""
            )
            if supplied != WEBHOOK_SECRET:
                self.send_response(403)
                self.end_headers()
                return

        try:
            length = int(self.headers.get("Content-Length", "0"))
            update = json.loads(self.rfile.read(length).decode("utf-8"))

            if not TOKEN:
                raise RuntimeError("Missing TELEGRAM_BOT_TOKEN")

            handle_update(update)

            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"OK")

        except Exception:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(b"Error")
