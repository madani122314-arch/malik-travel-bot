
import json
import os
import urllib.request
import urllib.error
from http.server import BaseHTTPRequestHandler

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
WEBHOOK_SECRET = os.environ.get("TELEGRAM_WEBHOOK_SECRET", "")
WHATSAPP_URL = "https://wa.me/213779749129"

API_URL = f"https://api.telegram.org/bot{TOKEN}/"


# =========================
# TELEGRAM API
# =========================

def telegram(method, payload=None):
    if not TOKEN:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is missing")

    data = json.dumps(payload or {}).encode("utf-8")
    request = urllib.request.Request(
        API_URL + method,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urllib.request.urlopen(request, timeout=15) as response:
        result = json.loads(response.read().decode("utf-8"))

    if not result.get("ok"):
        raise RuntimeError(result.get("description", "Telegram API error"))

    return result.get("result")


def send(chat_id, text, keyboard=None):
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }

    if keyboard is not None:
        payload["reply_markup"] = keyboard

    return telegram("sendMessage", payload)


def answer_callback(callback_id):
    try:
        telegram("answerCallbackQuery", {"callback_query_id": callback_id})
    except Exception:
        pass


def edit_message(chat_id, message_id, text, keyboard=None):
    payload = {
        "chat_id": chat_id,
        "message_id": message_id,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }

    if keyboard is not None:
        payload["reply_markup"] = keyboard

    try:
        return telegram("editMessageText", payload)
    except Exception:
        # If the message has not changed, send a new one instead.
        return send(chat_id, text, keyboard)


def button(text, callback):
    return {"text": text, "callback_data": callback}


def home_button():
    return [[button("🏠 Menu principal", "home")]]


def whatsapp_button():
    return [[{"text": "📱 Contact WhatsApp", "url": WHATSAPP_URL}]]


def navigation_keyboard(rows=None):
    keyboard = list(rows or [])
    keyboard.append([button("🏠 Menu principal", "home")])
    return {"inline_keyboard": keyboard}


def send_page(chat_id, text, rows=None):
    return send(chat_id, text, navigation_keyboard(rows))


# =========================
# WELCOME & COUNTRIES
# =========================

WELCOME = (
    "✈️ <b>مرحبا بكم في MALIK TRAVEL</b> 🌍\n\n"
    "يسعدنا استقبالكم ومرافقتكم في رحلتكم، من أول خطوة حتى تحقيق مشروع سفركم.\n\n"
    "نضع تحت تصرّفكم خدماتنا في مجال التأشيرات، المواعيد، وحجوزات السفر، "
    "مع الحرص على مرافقتكم وتقديم المعلومات اللازمة.\n\n"
    "<b>MALIK TRAVEL — وجهتكم نحو العالم.</b> 🌐"
)

COUNTRIES = [
    ("🇪🇸 Espagne — إسبانيا", "country_es"),
    ("🇪🇪 Estonie — إستونيا", "country_ee"),
    ("🇬🇧 UK — المملكة المتحدة", "country_uk"),
    ("🇺🇸 USA — الولايات المتحدة", "country_us"),
    ("🇨🇦 Canada — كندا", "country_ca"),
    ("🇫🇷 France — فرنسا", "country_fr"),
    ("🇮🇹 Italie — إيطاليا", "country_it"),
    ("🇩🇪 Allemagne — ألمانيا", "country_de"),
    ("🇳🇴 Norvège — النرويج", "country_no"),
    ("🇲🇹 Malte — مالطا", "country_mt"),
    ("🇧🇪 Belgique — بلجيكا", "country_be"),
    ("🇳🇱 Hollande — هولندا", "country_nl"),
    ("🇵🇹 Portugal — البرتغال", "country_pt"),
    ("🇹🇷 Turquie — تركيا", "country_tr"),
    ("🌍 Autre pays", "country_other"),
]


def country_keyboard():
    rows = []
    for i in range(0, len(COUNTRIES), 2):
        row = [button(label, callback) for label, callback in COUNTRIES[i:i + 2]]
        rows.append(row)
    return {"inline_keyboard": rows}


def show_home(chat_id, message_id=None):
    text = WELCOME + "\n\n<b>Choisissez votre destination :</b>"
    keyboard = country_keyboard()

    if message_id:
        return edit_message(chat_id, message_id, text, keyboard)

    return send(chat_id, text, keyboard)


# =========================
# SPAIN MENU
# =========================

def show_spain_menu(chat_id, message_id=None):
    text = (
        "🇪🇸 <b>ESPAGNE — إسبانيا</b>\n\n"
        "Choisissez le service souhaité :"
    )

    keyboard = {
        "inline_keyboard": [
            [button("📅 RDV", "es_rdv")],
            [button("📂 Traitement du dossier", "es_general")],
            [button("📄 Dossier à fournir", "es_professions")],
            [button("🏠 Menu principal", "home")],
        ]
    }

    if message_id:
        return edit_message(chat_id, message_id, text, keyboard)

    return send(chat_id, text, keyboard)


# =========================
# GENERAL DOCUMENT CHECKLIST
# Traitement du dossier
# =========================

GENERAL_DOCS = [
    "Formulaire uniforme de demande de visa, dûment rempli et signé, "
    "avec une photo récente en couleur, de face et sur fond blanc.",

    "Passeport valide jusqu’à 3 mois après l’expiration du visa, "
    "avec au moins 2 pages libres.",

    "Photocopies de toutes les pages du passeport actuel. "
    "Le passeport doit avoir été délivré depuis moins de 10 ans.",

    "Assurance de voyage couvrant les jours du séjour prévu, valable "
    "dans tous les pays de l’espace Schengen, couvrant les frais médicaux "
    "et de rapatriement, avec une couverture minimale de 30 000 €.",

    "Justificatifs des moyens de subsistance pendant le séjour : "
    "historique bancaire des 6 derniers mois ou autres justificatifs "
    "de ressources financières disponibles pendant le séjour.",

    "Pour les mineurs ne voyageant pas avec leurs deux parents : "
    "autorisation parentale et extrait de naissance. Si l’accompagnateur "
    "est un tuteur, justificatifs de tutelle et autorisation nécessaires.",

    "Si le demandeur présente les documents financiers d’un conjoint, "
    "parent, frère, sœur, enfant ou employeur : justificatif de prise en "
    "charge légalisé ou lettre de l’employeur, selon le cas.",

    "Pour les demandeurs non algériens : titre de séjour algérien valide "
    "au moins 3 mois après l’expiration du visa. Si le titre est expiré, "
    "justificatif de renouvellement en cours, selon le cas.",

    "Réservation d’hôtel confirmée en Espagne.",

    "Réservation ou billet d’avion aller-retour indiquant l’itinéraire.",

    "Pour les femmes enceintes : rapport détaillé de grossesse.",

    "Fiche familiale pour les demandeurs mariés.",

    "Certificat de résidence si exigé pour le lieu de résidence du "
    "demandeur ou si le passeport a été délivré hors de la région Ouest.",

    "Présenter les originaux et un jeu complet de photocopies du dossier.",
]


def numbered(items):
    return "\n\n".join(
        f"{i}. {item}" for i, item in enumerate(items, 1)
    )


def show_general_docs(chat_id, message_id=None):
    text = (
        "📂 <b>TRAITEMENT DU DOSSIER — ESPAGNE</b>\n\n"
        "<b>Documents généraux à fournir :</b>\n\n"
        + numbered(GENERAL_DOCS)
    )

    keyboard = navigation_keyboard()

    if message_id:
        return edit_message(chat_id, message_id, text, keyboard)

    return send(chat_id, text, keyboard)


# =========================
# SPAIN RDV
# =========================

def show_regions(chat_id, message_id=None):
    text = "📅 <b>RDV ESPAGNE</b>\n\nChoisissez votre ville :"

    keyboard = {
        "inline_keyboard": [
            [button("🇩🇿 Alger", "region_alger")],
            [button("🇩🇿 Oran", "region_oran")],
            [button("🏠 Menu principal", "home")],
        ]
    }

    if message_id:
        return edit_message(chat_id, message_id, text, keyboard)

    return send(chat_id, text, keyboard)


def show_centers(chat_id, region, message_id=None):
    if region == "alger":
        title = "Alger"
        centers = [
            ("🏠 À domicile Alger", "center_home_alger"),
            ("ALG 1", "center_alg1"),
            ("ALG 2", "center_alg2"),
            ("ALG 3", "center_alg3"),
        ]
    else:
        title = "Oran"
        centers = [
            ("🏠 À domicile Oran", "center_home_oran"),
            ("Oran 1", "center_oran1"),
            ("Oran 2", "center_oran2"),
            ("Oran 3", "center_oran3"),
        ]

    rows = [[button(label, callback)] for label, callback in centers]
    rows.append([button("⬅️ Retour aux villes", "es_rdv")])
    rows.append([button("🏠 Menu principal", "home")])

    text = f"📅 <b>RDV ESPAGNE — {title}</b>\n\nChoisissez votre centre :"
    keyboard = {"inline_keyboard": rows}

    if message_id:
        return edit_message(chat_id, message_id, text, keyboard)

    return send(chat_id, text, keyboard)


def show_center_docs(chat_id, center, message_id=None):
    home_centers = {
        "center_home_alger": "À domicile Alger",
        "center_home_oran": "À domicile Oran",
    }

    regular_centers = {
        "center_alg1": "ALG 1",
        "center_alg2": "ALG 2",
        "center_alg3": "ALG 3",
        "center_oran1": "Oran 1",
        "center_oran2": "Oran 2",
        "center_oran3": "Oran 3",
    }

    if center in home_centers:
        title = home_centers[center]
        items = [
            "Passeport",
            "Fiche familiale en France",
            "Numéro de téléphone",
            "Adresse du domicile",
            "Email",
        ]
    elif center in regular_centers:
        title = regular_centers[center]
        items = [
            "Passeport",
            "Dernier visa Espagne",
            "Carte magnétique : 10 000 DA",
            "Photo selfie",
        ]
    else:
        return

    text = (
        f"📋 <b>{title} — Documents nécessaires</b>\n\n"
        + numbered(items)
    )

    keyboard = {
        "inline_keyboard": [
            [{"text": "📱 Contact WhatsApp", "url": WHATSAPP_URL}],
            [button("⬅️ Retour aux centres", "back_centers")],
            [button("🏠 Menu principal", "home")],
        ]
    }

    if message_id:
        return edit_message(chat_id, message_id, text, keyboard)

    return send(chat_id, text, keyboard)


# =========================
# PROFESSION-SPECIFIC FILES
# Dossier à fournir
# =========================

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
    "Formulaire uniforme de demande de visa, dûment rempli et signé, "
    "avec une photo récente en couleur, de face et sur fond blanc.",

    "Passeport valide jusqu’à 3 mois après l’expiration du visa, "
    "avec au moins 2 pages libres.",

    "Photocopies de toutes les pages du passeport actuel. "
    "Le passeport doit avoir été délivré depuis moins de 10 ans.",

    "Assurance de voyage valable dans tous les pays de l’espace Schengen, "
    "couvrant les frais médicaux et de rapatriement, avec une couverture "
    "minimale de 30 000 €.",

    "Justificatifs des moyens de subsistance : historique bancaire des "
    "6 derniers mois ou autres justificatifs de ressources financières.",
]


PROFESSION_DOCS = {
    "job_salarie": [
        "Attestation d’emploi ou contrat de travail récent.",
        "Bulletins de salaire des 3 derniers mois.",
        "Attestation d’affiliation à la CNAS.",
        "Titre de congé.",
        "Si les justificatifs professionnels habituels ne sont pas "
        "disponibles : lettre explicative de l’employeur, selon le cas.",
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

    "job_retraite": [
        "Attestation de perception d’une pension de retraite.",
    ],

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
        "Preuves d’une situation socioéconomique adéquate, par exemple : "
        "certificat de mariage, livret de famille ou documents confirmant "
        "la propriété d’un bien immobilier.",
    ],
}


def show_professions(chat_id, message_id=None):
    rows = []
    for label, callback in PROFESSIONS:
        rows.append([button(label, callback)])

    rows.append([button("🏠 Menu principal", "home")])

    text = (
        "📄 <b>DOSSIER À FOURNIR — ESPAGNE</b>\n\n"
        "Choisissez votre situation professionnelle :"
    )

    keyboard = {"inline_keyboard": rows}

    if message_id:
        return edit_message(chat_id, message_id, text, keyboard)

    return send(chat_id, text, keyboard)


def show_profession_docs(chat_id, profession, message_id=None):
    profession_names = dict(PROFESSIONS)
    name = profession_names.get(profession)

    if not name or profession not in PROFESSION_DOCS:
        return

    items = COMMON_PROFESSION_DOCS + PROFESSION_DOCS[profession]

    text = (
        f"📄 <b>{name.upper()} — ESPAGNE</b>\n\n"
        "<b>Documents à fournir :</b>\n\n"
        + numbered(items)
    )

    keyboard = {
        "inline_keyboard": [
            [button("⬅️ Retour aux professions", "es_professions")],
            [{"text": "📱 Contact WhatsApp", "url": WHATSAPP_URL}],
            [button("🏠 Menu principal", "home")],
        ]
    }

    if message_id:
        return edit_message(chat_id, message_id, text, keyboard)

    return send(chat_id, text, keyboard)


# =========================
# OTHER COUNTRIES
# =========================

def show_other_country(chat_id, message_id=None):
    text = (
        "🌍 <b>Autre pays</b>\n\n"
        "Pour toute demande concernant une autre destination, "
        "contactez-nous sur WhatsApp."
    )

    keyboard = {
        "inline_keyboard": [
            [{"text": "📱 Contact WhatsApp", "url": WHATSAPP_URL}],
            [button("🏠 Menu principal", "home")],
        ]
    }

    if message_id:
        return edit_message(chat_id, message_id, text, keyboard)

    return send(chat_id, text, keyboard)


def show_country_contact(chat_id, country_label, message_id=None):
    text = (
        f"🌍 <b>{country_label}</b>\n\n"
        "Pour les informations et services concernant cette destination, "
        "contactez-nous sur WhatsApp."
    )

    keyboard = {
        "inline_keyboard": [
            [{"text": "📱 Contact WhatsApp", "url": WHATSAPP_URL}],
            [button("🏠 Menu principal", "home")],
        ]
    }

    if message_id:
        return edit_message(chat_id, message_id, text, keyboard)

    return send(chat_id, text, keyboard)


COUNTRY_LABELS = {
    "country_ee": "Estonie — إستونيا",
    "country_uk": "UK — المملكة المتحدة",
    "country_us": "USA — الولايات المتحدة",
    "country_ca": "Canada — كندا",
    "country_fr": "France — فرنسا",
    "country_it": "Italie — إيطاليا",
    "country_de": "Allemagne — ألمانيا",
    "country_no": "Norvège — النرويج",
    "country_mt": "Malte — مالطا",
    "country_be": "Belgique — بلجيكا",
    "country_nl": "Hollande — هولندا",
    "country_pt": "Portugal — البرتغال",
    "country_tr": "Turquie — تركيا",
}


# =========================
# CALLBACK ROUTER
# =========================

def handle_callback(callback):
    callback_id = callback.get("id")
    answer_callback(callback_id)

    message = callback.get("message", {})
    chat = message.get("chat", {})
    chat_id = chat.get("id")
    message_id = message.get("message_id")
    data = callback.get("data", "")

    if not chat_id:
        return

    if data == "home":
        return show_home(chat_id, message_id)

    if data == "country_es":
        return show_spain_menu(chat_id, message_id)

    if data == "country_other":
        return show_other_country(chat_id, message_id)

    if data in COUNTRY_LABELS:
        return show_country_contact(
            chat_id, COUNTRY_LABELS[data], message_id
        )

    if data == "es_rdv":
        return show_regions(chat_id, message_id)

    if data == "region_alger":
        return show_centers(chat_id, "alger", message_id)

    if data == "region_oran":
        return show_centers(chat_id, "oran", message_id)

    if data.startswith("center_"):
        return show_center_docs(chat_id, data, message_id)

    if data == "back_centers":
        return show_centers(chat_id, "alger", message_id)

    if data == "es_general":
        return show_general_docs(chat_id, message_id)

    if data == "es_professions":
        return show_professions(chat_id, message_id)

    if data.startswith("job_"):
        return show_profession_docs(chat_id, data, message_id)


# =========================
# VERCEL WEBHOOK HANDLER
# =========================

class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        body = b"MALIK TRAVEL bot is ready."
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        if WEBHOOK_SECRET:
            supplied_secret = self.headers.get(
                "X-Telegram-Bot-Api-Secret-Token", ""
            )
            if supplied_secret != WEBHOOK_SECRET:
                self.send_response(403)
                self.end_headers()
                self.wfile.write(b"Forbidden")
                return

        try:
            length = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(length)
            update = json.loads(raw.decode("utf-8"))

            if "callback_query" in update:
                handle_callback(update["callback_query"])

            elif "message" in update:
                message = update["message"]
                chat_id = message.get("chat", {}).get("id")
                text = (message.get("text") or "").strip()

                if chat_id and text.startswith("/start"):
                    show_home(chat_id)

                elif chat_id and text in ("/menu", "Menu principal"):
                    show_home(chat_id)

            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write(b"OK")

        except Exception:
            # Avoid returning internal details to the webhook caller.
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write(b"OK")
