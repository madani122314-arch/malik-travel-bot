import json
import os
import logging
import urllib.request
import urllib.error
from http.server import BaseHTTPRequestHandler

logging.basicConfig(level=logging.INFO)
LOG = logging.getLogger("malik_travel")

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
WEBHOOK_SECRET = os.environ.get("TELEGRAM_WEBHOOK_SECRET", "").strip()
WHATSAPP_URL = "https://wa.me/213779749129"

WELCOME = """✈️ <b>مرحبا بكم في MALIK TRAVEL</b> 🌍

يسعدنا استقبالكم ومرافقتكم في رحلتكم، من أول خطوة حتى تحقيق مشروع سفركم.

نضع تحت تصرّفكم خدماتنا في مجال التأشيرات، المواعيد، وحجوزات السفر، مع الحرص على مرافقتكم وتقديم المعلومات اللازمة.

<b>MALIK TRAVEL — وجهتكم نحو العالم.</b> 🌐"""

COUNTRIES = [
    ("🇪🇸 Espagne — إسبانيا", "country_es"),
    ("🇪🇪 Estonie — إستونيا", "country_other"),
    ("🇬🇧 UK — المملكة المتحدة", "country_other"),
    ("🇺🇸 USA — الولايات المتحدة", "country_other"),
    ("🇨🇦 Canada — كندا", "country_other"),
    ("🇫🇷 France — فرنسا", "country_other"),
    ("🇮🇹 Italie — إيطاليا", "country_other"),
    ("🇩🇪 Allemagne — ألمانيا", "country_other"),
    ("🇳🇴 Norvège — النرويج", "country_other"),
    ("🇲🇹 Malte — مالطا", "country_other"),
    ("🇧🇪 Belgique — بلجيكا", "country_other"),
    ("🇳🇱 Hollande — هولندا", "country_other"),
    ("🇵🇹 Portugal — البرتغال", "country_other"),
    ("🇹🇷 Turquie — تركيا", "country_other"),
    ("🌍 Autre pays", "country_other"),
]

PROFESSIONS = [
    ("Salarié", "job_salarie"),
    ("Commerçant", "job_commercant"),
    ("Professions libérales / Hirafi", "job_liberal"),
    ("Agriculteur", "job_agriculteur"),
    ("Retraité", "job_retraite"),
    ("Fonctionnaire", "job_fonctionnaire"),
    ("Étudiant", "job_etudiant"),
    ("Sans emploi", "job_sans_emploi"),
]

COMMON_PROFESSION_DOCS = [
    "Formulaire uniforme de demande de visa dûment rempli et signé, avec une photo couleur récente de face sur fond blanc.",
    "Passeport valide au moins 3 mois après l’expiration du visa demandé et comportant au moins 2 pages vierges.",
    "Photocopies de toutes les pages du passeport actuel. Le passeport doit avoir été délivré depuis moins de 10 ans.",
    "Assurance voyage couvrant la durée du premier séjour, valable dans tout l’espace Schengen, avec une couverture médicale et de rapatriement d’au moins 30 000 €.",
    "Justificatifs de moyens financiers : autres justificatifs de ressources, si disponibles.",
    "Relevés de compte bancaire en dinars des 6 derniers mois.",
    "Attestation de solde bancaire d’un montant minimum de 2 500 €.",
]

PROFESSION_DOCS = {
    "job_salarie": [
        "Attestation d’emploi ou contrat de travail récent.",
        "Bulletins de salaire des 3 derniers mois.",
        "Attestation d’affiliation à la CNAS.",
        "À défaut, lettre explicative de l’employeur accompagnée du titre de congé.",
    ],
    "job_commercant": [
        "Justificatif d’inscription au registre du commerce.",
        "Attestation d’affiliation à la CASNOS.",
        "Extrait de rôle.",
        "Formulaire C20 mentionnant le chiffre d’affaires et le bilan.",
        "Relevés bancaires des 3 derniers mois.",
    ],
    "job_liberal": [
        "Décision d’installation ou carte professionnelle.",
        "Dernière déclaration du revenu annuel.",
    ],
    "job_agriculteur": [
        "Attestation d’exploitant agricole.",
        "Carte d’agriculteur.",
        "Dernière déclaration du revenu annuel.",
    ],
    "job_retraite": ["Attestation de perception d’une pension de retraite."],
    "job_fonctionnaire": [
        "Arrêté de nomination ou attestation de fonction.",
        "Dernier bulletin de salaire.",
    ],
    "job_etudiant": [
        "Certificat de scolarité.",
        "Carte d’étudiant.",
        "Justificatifs de la situation socioprofessionnelle des parents.",
    ],
    "job_sans_emploi": [
        "Justificatifs d’une situation socioéconomique adéquate, par exemple certificat de mariage, livret de famille ou documents prouvant la propriété d’un bien."
    ],
}

GENERAL_DOCS = [
    "Formulaire uniforme de demande de visa dûment rempli et signé, avec une photo couleur récente de face sur fond blanc.",
    "Passeport valide jusqu’à au moins 3 mois après l’expiration du visa demandé et comportant au moins 2 pages vierges.",
    "Photocopies de toutes les pages du passeport actuel. Le passeport doit avoir été délivré depuis moins de 10 ans.",
    "Assurance voyage couvrant la durée du premier séjour, valable dans tout l’espace Schengen, avec une couverture médicale et de rapatriement d’au moins 30 000 €.",
    "Justificatifs de moyens financiers : relevés bancaires des 6 derniers mois ou autres justificatifs de ressources.",
    "Pour les mineurs ne voyageant pas avec leurs deux parents : autorisation parentale et extrait de naissance. Si le tuteur n’est pas un parent, joindre le justificatif de tutelle (acte de décès ou jugement, selon le cas).",
    "Si le demandeur dépose seul le dossier et présente des documents d’un conjoint, parent, frère, sœur, enfant ou employeur : prise en charge légalisée par la personne concernée, ou lettre de l’employeur.",
    "Pour les demandeurs non algériens : titre de séjour en Algérie valide au moins 3 mois après l’expiration du visa. Si le renouvellement est en cours, joindre une preuve de la demande de renouvellement.",
    "Réservation d’hôtel confirmée en Espagne.",
    "Réservation ou billet d’avion aller-retour indiquant l’itinéraire.",
    "Pour les femmes enceintes : rapport médical détaillé relatif à la grossesse.",
    "Fiche familiale pour les demandeurs mariés.",
    "Certificat de résidence si exigé par le centre concerné, notamment selon le lieu de résidence ou de délivrance du passeport.",
    "Présenter les originaux et un jeu complet de photocopies pour chaque dossier.",
]

CENTERS = {
    "alger": [("À domicile Alger", "home_alger"), ("ALG 1", "alg1"), ("ALG 2", "alg2"), ("ALG 3", "alg3")],
    "oran": [("À domicile Oran", "home_oran"), ("Oran 1", "oran1"), ("Oran 2", "oran2"), ("Oran 3", "oran3")],
}
REGULAR_CENTER_DOCS = ["Passeport", "Dernier visa Espagne", "Carte magnétique : 10 000 DA", "Photo selfie"]
HOME_CENTER_DOCS = ["Passeport", "Fiche familiale en France", "Numéro de téléphone", "Adresse du domicile", "Email"]
CENTER_LABELS = {
    "alg1": "ALG 1", "alg2": "ALG 2", "alg3": "ALG 3",
    "oran1": "Oran 1", "oran2": "Oran 2", "oran3": "Oran 3",
    "home_alger": "À domicile Alger", "home_oran": "À domicile Oran",
}


def button(text, data):
    return {"text": text, "callback_data": data}


def keyboard(rows):
    return {"inline_keyboard": rows}


def numbered(items):
    return "\n".join(f"{i}. {item}" for i, item in enumerate(items, 1))


def telegram(method, payload):
    if not BOT_TOKEN:
        raise RuntimeError("La variable TELEGRAM_BOT_TOKEN est absente.")
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/{method}"
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json; charset=utf-8"}, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            result = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Telegram {method} HTTP {exc.code}: {detail}") from exc
    if not result.get("ok"):
        raise RuntimeError(f"Telegram {method} API error: {result}")
    return result.get("result")


def send(chat_id, text, reply_markup=None):
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML", "disable_web_page_preview": True}
    if reply_markup:
        payload["reply_markup"] = reply_markup
    return telegram("sendMessage", payload)


def answer_callback(callback_id):
    if callback_id:
        try:
            telegram("answerCallbackQuery", {"callback_query_id": callback_id})
        except Exception:
            LOG.exception("Failed to answer callback query")


def edit_or_send(chat_id, message_id, text, reply_markup=None):
    if not message_id:
        return send(chat_id, text, reply_markup)
    payload = {"chat_id": chat_id, "message_id": message_id, "text": text, "parse_mode": "HTML", "disable_web_page_preview": True}
    if reply_markup:
        payload["reply_markup"] = reply_markup
    try:
        return telegram("editMessageText", payload)
    except Exception as exc:
        if "message is not modified" in str(exc).lower():
            return None
        LOG.warning("Edit failed; trying sendMessage instead: %s", exc)
        return send(chat_id, text, reply_markup)


def country_keyboard():
    rows = []
    for i in range(0, len(COUNTRIES), 2):
        rows.append([button(label, data) for label, data in COUNTRIES[i:i + 2]])
    return keyboard(rows)


def show_home(chat_id, message_id=None):
    text = WELCOME + "\n\n<b>Choisissez votre destination :</b>"
    return edit_or_send(chat_id, message_id, text, country_keyboard())


def show_spain_menu(chat_id, message_id=None):
    rows = [
        [button("📅 RDV", "es_rdv")],
        [button("📂 Traitement du dossier", "es_general_docs")],
        [button("📄 Dossier à fournir", "es_professions")],
        [button("⬅️ Menu principal", "home")],
    ]
    return edit_or_send(chat_id, message_id, "🇪🇸 <b>ESPAGNE</b>\n\nChoisissez le service souhaité :", keyboard(rows))


def show_general_docs(chat_id, message_id=None):
    text = """📂 <b>TRAITEMENT DU DOSSIER — ESPAGNE</b>
<b>خدمات معالجة ملف التأشيرة — إسبانيا</b>

━━━━━━━━━━━━━━━━━━
📝 <b>1. FORMULAIRE VISA SCHENGEN</b>
<b>استمارة تأشيرة شنغن</b>
• Saisie complète et fiable
• Vérification des données
• Conforme aux exigences des consulats

• تعبئة كاملة ودقيقة للاستمارة
• مراجعة المعلومات
• احترام متطلبات القنصليات

━━━━━━━━━━━━━━━━━━
🏨 <b>2. RÉSERVATION HÔTEL CONFIRMÉE</b>
<b>حجز فندقي مؤكد</b>
• Hôtels partenaires fiables
• Confirmation selon disponibilité
• Justificatif adapté aux exigences du dossier

• فنادق موثوقة
• تأكيد الحجز حسب التوفر
• وثيقة مناسبة لمتطلبات الملف

━━━━━━━━━━━━━━━━━━
✈️ <b>3. TELEX / RÉSERVATION BILLET D’AVION</b>
<b>تيليكس / حجز تذكرة الطيران</b>
• Air Algérie, Vueling et autres compagnies
• Réservation vérifiable selon le service proposé
• Tarifs compétitifs et traitement rapide

• الخطوط الجوية الجزائرية وVueling وشركات أخرى
• حجز قابل للتحقق حسب الخدمة المتاحة
• أسعار تنافسية وخدمة سريعة

━━━━━━━━━━━━━━━━━━
🗺️ <b>4. PLAN DE VOYAGE</b>
<b>خطة السفر</b>
• Itinéraire détaillé jour par jour
• Hébergements et déplacements
• Présentation claire du programme

• برنامج سفر مفصل يومًا بيوم
• الإقامة والتنقلات
• تنظيم واضح لبرنامج الرحلة

━━━━━━━━━━━━━━━━━━
✍️ <b>5. LETTRE DE MOTIVATION</b>
<b>رسالة تحفيزية لطلب التأشيرة</b>
• Rédaction personnalisée
• Adaptée à votre profil
• Présentation claire de votre projet de voyage

• كتابة مخصصة حسب الحالة
• مناسبة للملف الشخصي
• توضيح هدف ومشروع السفر

━━━━━━━━━━━━━━━━━━
📁 <b>6. PRÉPARATION DU DOSSIER SELON L’ACTIVITÉ</b>
<b>تحضير الملف حسب النشاط المهني</b>
• Salarié · Commerçant · Agriculteur
• Retraité · Étudiant · Autres situations
• Analyse de la situation et liste des documents nécessaires
• Conseils personnalisés pour préparer le dossier

• أجير · تاجر · فلاح
• متقاعد · طالب · حالات أخرى
• دراسة الوضعية وتحديد الوثائق المطلوبة
• إرشادات مخصصة لتحضير الملف

━━━━━━━━━━━━━━━━━━
📩 <b>Contactez-nous pour les informations et les tarifs.</b>
<b>تواصلوا معنا لمعرفة التفاصيل والأسعار.</b>"""
    rows = [
        [{"text": "📱 Contact WhatsApp", "url": WHATSAPP_URL}],
        [button("🏠 Menu principal", "home")],
    ]
    return edit_or_send(chat_id, message_id, text, keyboard(rows))


def show_professions(chat_id, message_id=None):
    rows = [[button(label, data)] for label, data in PROFESSIONS]
    rows += [[button("⬅️ Retour Espagne", "country_es")], [button("🏠 Menu principal", "home")]]
    return edit_or_send(chat_id, message_id, "📄 <b>DOSSIER À FOURNIR — ESPAGNE</b>\n\nChoisissez votre profession :", keyboard(rows))


def show_profession_docs(chat_id, callback_data, message_id=None):
    names = {callback_data: label for label, callback_data in PROFESSIONS}
    name = names.get(callback_data)
    specific_docs = PROFESSION_DOCS.get(callback_data)
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
