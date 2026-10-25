
import json
import os
import logging
from urllib.request import Request, urlopen

from http.server import BaseHTTPRequestHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
WEBHOOK_SECRET = os.environ.get("TELEGRAM_WEBHOOK_SECRET", "")
WHATSAPP_URL = "https://wa.me/213779749129"

TELEGRAM_API = f"https://api.telegram.org/bot{TOKEN}/"


def telegram(method, payload=None):
    if not TOKEN:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is missing")

    request = Request(
        TELEGRAM_API + method,
        data=json.dumps(payload or {}).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urlopen(request, timeout=15) as response:
        result = json.loads(response.read().decode("utf-8"))

    if not result.get("ok"):
        raise RuntimeError(str(result))

    return result.get("result")


def send(chat_id, text, keyboard=None):
    payload = {"chat_id": chat_id, "text": text}
    if keyboard is not None:
        payload["reply_markup"] = {"inline_keyboard": keyboard}
    return telegram("sendMessage", payload)


def home_button():
    return [[{"text": "🏠 Menu principal", "callback_data": "home"}]]


def whatsapp_button():
    return [[{"text": "📱 Contact WhatsApp", "url": WHATSAPP_URL}]]


def with_home(rows):
    return rows + home_button()


WELCOME = (
    "✈️ مرحبا بكم في MALIK TRAVEL 🌍\n\n"
    "يسعدنا استقبالكم ومرافقتكم في رحلتكم، من أول خطوة حتى تحقيق مشروع سفركم.\n\n"
    "نضع تحت تصرّفكم خدماتنا في مجال التأشيرات، المواعيد، وحجوزات السفر، "
    "مع الحرص على مرافقتكم وتقديم المعلومات اللازمة.\n\n"
    "MALIK TRAVEL — وجهتكم نحو العالم. 🌐"
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


def start_menu(chat_id):
    rows = []
    for i in range(0, len(COUNTRIES), 2):
        row = [{
            "text": COUNTRIES[i][0],
            "callback_data": COUNTRIES[i][1],
        }]
        if i + 1 < len(COUNTRIES):
            row.append({
                "text": COUNTRIES[i + 1][0],
                "callback_data": COUNTRIES[i + 1][1],
            })
        rows.append(row)

    send(chat_id, WELCOME + "\n\nChoisissez votre destination :", rows)


def show_spain_menu(chat_id):
    rows = [
        [{"text": "📅 RDV", "callback_data": "sp_rdv"}],
        [{"text": "📂 Traitement du dossier", "callback_data": "general_docs"}],
        [{"text": "📄 Dossier à fournir", "callback_data": "sp_traitement"}],
    ]
    send(chat_id, "🇪🇸 Espagne\n\nChoisissez le service souhaité :", with_home(rows))


def show_regions(chat_id):
    rows = [[
        {"text": "🇩🇿 Alger", "callback_data": "region_alger"},
        {"text": "🇩🇿 Oran", "callback_data": "region_oran"},
    ]]
    send(chat_id, "Choisissez votre ville :", with_home(rows))


def show_centers(chat_id, region):
    if region == "alger":
        centers = [
            ("À domicile Alger", "center_home_alger"),
            ("ALG 1", "center_alg1"),
            ("ALG 2", "center_alg2"),
            ("ALG 3", "center_alg3"),
        ]
    else:
        centers = [
            ("À domicile Oran", "center_home_oran"),
            ("Oran 1", "center_oran1"),
            ("Oran 2", "center_oran2"),
            ("Oran 3", "center_oran3"),
        ]

    rows = [[{"text": label, "callback_data": callback}]
            for label, callback in centers]
    send(chat_id, "Choisissez le centre :", with_home(rows))


def show_appointment_docs(chat_id, center):
    paid_centers = {
        "center_alg1", "center_alg2", "center_alg3",
        "center_oran1", "center_oran2", "center_oran3",
    }

    if center in paid_centers:
        text = (
            "Documents requis :\n\n"
            "1. Passeport\n"
            "2. Dernier visa Espagne\n"
            "3. Carte magnétique : 10 000 DA\n"
            "4. Photo selfie\n"
            "5. Contact WhatsApp"
        )

    elif center in ("center_home_alger", "center_home_oran"):
        text = (
            "Documents requis pour le rendez-vous à domicile :\n\n"
            "1. Passeport\n"
            "2. Fiche familiale en France\n"
            "3. Numéro de téléphone\n"
            "4. Adresse du domicile\n"
            "5. Email\n"
            "6. Contact WhatsApp"
        )
    else:
        show_contact(chat_id)
        return

    send(chat_id, text, whatsapp_button() + home_button())


GENERAL_DOCS = (
    "📄 Documents généraux — Visa Espagne\n\n"
    "1. Formulaire uniforme de demande de visa dûment rempli et signé, "
    "avec une photo récente en couleur, de face, sur fond blanc.\n\n"
    "2. Passeport valable au moins trois mois après l'expiration du visa "
    "et comportant au minimum deux pages vierges.\n\n"
    "3. Photocopies de toutes les pages du passeport actuel, délivré depuis "
    "moins de dix ans.\n\n"
    "4. Assurance voyage valable dans tout l'espace Schengen, couvrant "
    "les frais médicaux et de rapatriement à hauteur d'au moins 30 000 €.\n\n"
    "5. Justificatifs de moyens de subsistance : relevés bancaires des "
    "six derniers mois ou autres justificatifs de ressources.\n\n"
    "6. Pour les mineurs ne voyageant pas avec leurs deux parents : "
    "autorisation parentale et extrait de naissance. En cas de tutelle, "
    "joindre les justificatifs correspondants.\n\n"
    "7. Si le demandeur présente les documents financiers d'un proche ou "
    "d'un employeur : prise en charge légalisée ou attestation de l'employeur.\n\n"
    "8. Pour les demandeurs non algériens : titre de séjour en Algérie "
    "valable au moins trois mois après l'expiration du visa, ou justificatif "
    "de renouvellement si applicable.\n\n"
    "9. Réservation d'hôtel confirmée en Espagne.\n\n"
    "10. Réservation de billet d'avion aller-retour avec itinéraire.\n\n"
    "11. Pour les femmes enceintes : rapport médical détaillé.\n\n"
    "12. Fiche familiale pour les demandeurs mariés.\n\n"
    "13. Certificat de résidence lorsque requis selon le lieu de dépôt "
    "ou le lieu de délivrance du passeport.\n\n"
    "14. Présenter les originaux ainsi qu'un jeu complet de photocopies."
)


def show_general_docs(chat_id):
    send(chat_id, GENERAL_DOCS, home_button())


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


def show_professions(chat_id):
    rows = [[{"text": label, "callback_data": callback}]
            for label, callback in PROFESSIONS]
    send(chat_id, "Choisissez votre profession :", with_home(rows))


PROFESSION_DOCS = {
    "job_commercant": (
        "Documents — Commerçant\n\n"
        "1. Registre de commerce avec traduction française\n"
        "2. C20\n"
        "3. Existence\n"
        "4. Extrait de rôle\n"
        "5. CASNOS\n"
        "6. Relevés bancaires en dinars des six derniers mois\n"
        "7. Attestation de solde en euros : minimum 2 500 €\n"
        "8. Acte de naissance en France\n"
        "9. Fiche familiale en France\n"
        "10. Acte de mariage en France\n"
        "11. Passeport\n"
        "12. Deux photos d'identité"
    ),
    "job_salarie": (
        "Documents — Salarié\n\n"
        "1. Attestation de travail\n"
        "2. Les trois dernières fiches de paie\n"
        "3. CNAS\n"
        "4. Titre de congé\n"
        "5. Relevés bancaires en dinars des six derniers mois\n"
        "6. Attestation de solde en euros : minimum 2 500 €\n"
        "7. Acte de naissance en France\n"
        "8. Fiche familiale en France\n"
        "9. Acte de mariage en France\n"
        "10. Passeport\n"
        "11. Deux photos d'identité"
    ),
    "job_liberal": (
        "Documents — Professions libérales / Hirafi\n\n"
        "1. Carte professionnelle\n"
        "2. C20\n"
        "3. Existence\n"
        "4. Extrait de rôle\n"
        "5. Attestation CASNOS\n"
        "6. Relevés bancaires en dinars des six derniers mois\n"
        "7. Attestation de solde en euros : minimum 2 500 €\n"
        "8. Acte de naissance en France\n"
        "9. Fiche familiale en France\n"
        "10. Acte de mariage en France\n"
        "11. Passeport\n"
        "12. Deux photos d'identité"
    ),
    "job_etudiant": (
        "Documents — Étudiant\n\n"
        "1. Carte de scolarité\n"
        "2. Relevés bancaires en dinars des six derniers mois\n"
        "3. Attestation de solde en euros : minimum 2 500 €\n"
        "4. Acte de naissance en France\n"
        "5. Prise en charge\n"
        "6. Passeport\n"
        "7. Deux photos d'identité\n"
        "8. Autorisation parentale pour les mineurs\n"
        "9. Dossier du garant : documents de la personne qui finance le voyage"
    ),
}


def show_profession_docs(chat_id, callback):
    text = PROFESSION_DOCS.get(callback)
    if text:
        send(chat_id, text, home_button())
    else:
        send(
            chat_id,
            "La liste des documents pour cette profession doit être confirmée. "
            "Veuillez nous contacter pour obtenir les informations.",
            whatsapp_button() + home_button(),
        )


def show_contact(chat_id):
    send(
        chat_id,
        "Pour plus d'informations, veuillez nous contacter sur WhatsApp.",
        whatsapp_button() + home_button(),
    )


def handle_callback(callback):
    callback_id = callback.get("id")
    data = callback.get("data", "")
    message = callback.get("message") or {}
    chat = message.get("chat") or {}
    chat_id = chat.get("id")

    if callback_id:
        try:
            telegram("answerCallbackQuery", {"callback_query_id": callback_id})
        except Exception:
            logger.exception("Could not answer callback")

    if not chat_id:
        return

    if data == "home":
        start_menu(chat_id)
    elif data == "country_es":
        show_spain_menu(chat_id)
    elif data == "sp_rdv":
        show_regions(chat_id)
    elif data == "region_alger":
        show_centers(chat_id, "alger")
    elif data == "region_oran":
        show_centers(chat_id, "oran")
    elif data.startswith("center_"):
        show_appointment_docs(chat_id, data)
    elif data == "general_docs":
        show_general_docs(chat_id)
    elif data == "sp_traitement":
        show_professions(chat_id)
    elif data.startswith("job_"):
        show_profession_docs(chat_id, data)
    elif data.startswith("country_"):
        show_contact(chat_id)
    else:
        show_contact(chat_id)


class handler(BaseHTTPRequestHandler):

    def _send_response(self, status, body):
        encoded = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def do_GET(self):
        self._send_response(200, "MALIK TRAVEL bot is ready.")

    def do_POST(self):
        if WEBHOOK_SECRET:
            received = self.headers.get(
                "X-Telegram-Bot-Api-Secret-Token", ""
            )
            if received != WEBHOOK_SECRET:
                self._send_response(403, "Forbidden")
                return

        try:
            length = int(self.headers.get("Content-Length", "0"))
            update = json.loads(self.rfile.read(length).decode("utf-8"))

            callback = update.get("callback_query")
            if callback:
                handle_callback(callback)
            else:
                message = update.get("message") or {}
                chat = message.get("chat") or {}
                chat_id = chat.get("id")
                text = (message.get("text") or "").strip()

                if chat_id and (
                    text == "/start"
                    or text.startswith("/start ")
                    or text in ("/menu", "Menu principal")
                ):
                    start_menu(chat_id)

        except Exception:
            logger.exception("Error handling Telegram webhook")

        self._send_response(200, "OK")
