    if name is None or specific_docs is None:
        LOG.error("Unknown profession callback: %r", callback_data)
        return edit_or_send(chat_id, message_id, "Profession non reconnue. Veuillez choisir à nouveau.", keyboard([[button("⬅️ Retour aux professions", "es_professions")], [button("🏠 Menu principal", "home")]]))
    text = f"📄 <b>{name.upper()} — ESPAGNE</b>\n\n<b>Documents à fournir :</b>\n\n" + numbered(COMMON_PROFESSION_DOCS + specific_docs)
    rows = [[button("⬅️ Retour aux professions", "es_professions")], [{"text": "📱 Contact WhatsApp", "url": WHATSAPP_URL}], [button("🏠 Menu principal", "home")]]
    return edit_or_send(chat_id, message_id, text, keyboard(rows))


def show_cities(chat_id, message_id=None):
    rows = [[button("🇩🇿 Alger", "city_alger")], [button("🇩🇿 Oran", "city_oran")], [button("⬅️ Retour Espagne", "country_es")], [button("🏠 Menu principal", "home")]]
    return edit_or_send(chat_id, message_id, "📅 <b>RDV ESPAGNE</b>\n\nChoisissez la ville :", keyboard(rows))


def show_centers(chat_id, city, message_id=None):
    if city not in CENTERS:
        return show_cities(chat_id, message_id)
    rows = [[button(label, "center_" + key)] for label, key in CENTERS[city]]
    rows += [[button("⬅️ Retour aux villes", "es_rdv")], [button("🏠 Menu principal", "home")]]
    city_name = "Alger" if city == "alger" else "Oran"
    return edit_or_send(chat_id, message_id, f"📅 <b>Centres de rendez-vous — {city_name}</b>\n\nChoisissez un centre :", keyboard(rows))


def show_center_docs(chat_id, center_key, message_id=None):
    label = CENTER_LABELS.get(center_key)
    if not label:
        return show_cities(chat_id, message_id)
    is_home = center_key.startswith("home_")
    docs = HOME_CENTER_DOCS if is_home else REGULAR_CENTER_DOCS
    text = f"📅 <b>{label}</b>\n\n<b>Documents à préparer :</b>\n\n" + numbered(docs)
    city = "oran" if center_key.startswith("oran") or center_key == "home_oran" else "alger"
    rows = [[{"text": "📱 Contact WhatsApp", "url": WHATSAPP_URL}], [button("⬅️ Retour aux centres", "back_centers_" + city)], [button("🏠 Menu principal", "home")]]
    return edit_or_send(chat_id, message_id, text, keyboard(rows))


def show_other_country(chat_id, message_id=None):
    rows = [[{"text": "📱 Contact WhatsApp", "url": WHATSAPP_URL}], [button("🏠 Menu principal", "home")]]
    return edit_or_send(chat_id, message_id, "🌍 <b>Autres destinations</b>\n\nPour toute demande concernant les autres pays, contactez-nous sur WhatsApp.", keyboard(rows))


def handle_callback(callback):
    answer_callback(callback.get("id"))
    message = callback.get("message") or {}
    chat_id = (message.get("chat") or {}).get("id")
    message_id = message.get("message_id")
    data = callback.get("data", "")
    if not chat_id:
        LOG.warning("Callback without chat_id: %r", callback)
        return
    if data == "home": return show_home(chat_id, message_id)
    if data == "country_es": return show_spain_menu(chat_id, message_id)
    if data == "country_other": return show_other_country(chat_id, message_id)
    if data == "es_general_docs": return show_general_docs(chat_id, message_id)
    if data == "es_professions": return show_professions(chat_id, message_id)
    if data.startswith("job_"): return show_profession_docs(chat_id, data, message_id)
    if data == "es_rdv": return show_cities(chat_id, message_id)
    if data == "city_alger": return show_centers(chat_id, "alger", message_id)
    if data == "city_oran": return show_centers(chat_id, "oran", message_id)
    if data.startswith("center_"): return show_center_docs(chat_id, data[len("center_"):], message_id)
    if data.startswith("back_centers_"): return show_centers(chat_id, data[len("back_centers_"):], message_id)
    if data == "contact_whatsapp":
        return edit_or_send(chat_id, message_id, "📱 <b>Contactez MALIK TRAVEL sur WhatsApp :</b>", keyboard([[{"text": "Ouvrir WhatsApp", "url": WHATSAPP_URL}], [button("🏠 Menu principal", "home")]]))
    LOG.warning("Unknown callback: %r", data)
    return send(chat_id, "Choix non reconnu. Revenez au menu principal.", keyboard([[button("🏠 Menu principal", "home")]]))


class handler(BaseHTTPRequestHandler):
    def reply(self, status, body):
        data = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        self.reply(200, "MALIK TRAVEL bot is running.")

    def do_POST(self):
        try:
            if WEBHOOK_SECRET:
                secret = self.headers.get("X-Telegram-Bot-Api-Secret-Token", "")
                if secret != WEBHOOK_SECRET:
                    LOG.warning("Rejected webhook: invalid secret token")
                    self.reply(403, "Forbidden")
                    return
            length = int(self.headers.get("Content-Length", "0"))
            if length <= 0:
                self.reply(400, "Missing request body")
                return
            update = json.loads(self.rfile.read(length).decode("utf-8"))
            if "message" in update:
                msg = update["message"]
                chat_id = (msg.get("chat") or {}).get("id")
                text = (msg.get("text") or "").strip()
                if chat_id and text.startswith("/start"):
                    show_home(chat_id)
                elif chat_id and text.startswith("/menu"):
                    show_home(chat_id)
            elif "callback_query" in update:
                handle_callback(update["callback_query"])
            self.reply(200, "OK")
        except Exception:
            LOG.exception("Webhook processing failed")
            # Log the real exception so it is visible in Vercel Runtime Logs.
            try:
                self.reply(200, "OK")
            except Exception:
                pass
