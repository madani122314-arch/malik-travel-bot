
import json
import os
import urllib.request
from http.server import BaseHTTPRequestHandler

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
WEBHOOK_SECRET = os.environ.get("TELEGRAM_WEBHOOK_SECRET", "")
WHATSAPP_URL = os.environ.get("WHATSAPP_URL", "")

API = f"https://api.telegram.org/bot{TOKEN}"

COUNTRIES = [
    ("🇪🇸 Espagne — إسبانيا", "espagne"),
    ("🇪🇪 Estonie — إستونيا", "estonie"),
    ("🇬🇧 UK — المملكة المتحدة", "uk"),
    ("🇺🇸 USA — الولايات المتحدة", "usa"),
    ("🇨🇦 Canada — كندا", "canada"),
    ("🇫🇷 France — فرنسا", "france"),
    ("🇮🇹 Italie — إيطاليا", "italie"),
    ("🇩🇪 Allemagne — ألمانيا", "allemagne"),
    ("🇳🇴 Norvège — النرويج", "norvege"),
    ("🇲🇹 Malte — مالطا", "malte"),
    ("🇧🇪 Belgique — بلجيكا", "belgique"),
    ("🇳🇱 Hollande — هولندا", "hollande"),
    ("🇵🇹 Portugal — البرتغال", "portugal"),
    ("🇹🇷 Turquie — تركيا", "turquie"),
    ("🌍 Autre pays", "autre"),
]

PROFESSIONS = [
    ("Salarié", "salarie"),
    ("Commerçant", "commercant"),
    ("Professions libérales / Hirafi", "liberal"),
    ("Agriculteur", "agriculteur"),
    ("Retraité", "retraite"),
    ("Fonctionnaire", "fonctionnaire"),
    ("Étudiant", "etudiant"),
    ("Sans emploi", "sans_emploi"),
]

DOCS = {
    "salarie": """📂 DOSSIER SALARIÉ

1. Attestation de travail
2. Les 3 dernières fiches de paie
3. CNAS
4. Titre de congé
5. Relevés de compte bancaire en dinars des 6 derniers mois
6. Attestation de solde en euros : minimum 2 500 €
7. Acte de naissance en France
8. Fiche familiale en France
9. Acte de mariage en France
10. Passeport
11. Deux photos d'identité""",

    "commercant": """📂 DOSSIER COMMERÇANT

1. Registre de commerce avec traduction française
2. C20
3. Existence
4. Extrait de rôle
5. CASNOS
6. Relevés de compte bancaire en dinars des 6 derniers mois
7. Attestation de solde en euros : minimum 2 500 €
8. Acte de naissance en France
9. Fiche familiale en France
10. Acte de mariage en France
11. Passeport
12. Deux photos""",

    "liberal": """📂 DOSSIER PROFESSIONS LIBÉRALES / HIRAFI

1. Carte professionnelle
2. C20
3. Existence
4. Extrait de rôle
5. Attestation CASNOS
6. Relevés de compte bancaire en dinars des 6 derniers mois
7. Attestation de solde en euros : minimum 2 500 €
8. Acte de naissance en France
9. Fiche familiale en France
10. Acte de mariage en France
11. Passeport
12. Deux photos d'identité""",

    "etudiant": """📂 DOSSIER ÉTUDIANT

1. Carte de scolarité
2. Relevés de compte bancaire en dinars des 6 derniers mois
3. Attestation de solde en euros : minimum 2 500 €
4. Acte de naissance en France
5. Prise en charge
6. Passeport
7. Deux photos d'identité
8. Autorisation parentale pour les mineurs
9. Dossier du garant qui prend en charge le voyage"""
}

GENERAL_DOCS = """📄 DOSSIER À FOURNIR — DOCUMENTS GÉNÉRAUX

1. Formulaire de demande de visa rempli et signé, avec photo récente en couleur sur fond blanc.
2. Passeport valide au moins 3 mois après l'expiration du visa et comportant au moins 2 pages libres.
3. Photocopies de toutes les pages du passeport actuel, délivré depuis moins de 10 ans.
4. Assurance voyage valable dans l'espace Schengen, couvrant les frais médicaux et le rapatriement, minimum 30 000 €.
5. Justificatifs de moyens de subsistance : relevés bancaires des 6 derniers mois ou autres justificatifs de ressources.
6. Pour les mineurs ne voyageant pas avec les deux parents : autorisation parentale et extrait de naissance. Si le tuteur n'est pas le parent, justificatif de tutelle.
7. Si le demandeur dépose son dossier seul avec les documents d'un proche : prise en charge légalisée ou attestation de l'employeur selon le cas.
8. Pour les demandeurs non algériens : titre de séjour légal en Algérie, valable au moins 3 mois après l'expiration du visa.
9. Réservation d'hôtel en Espagne.
10. Réservation du billet d'avion aller-retour avec itinéraire.
11. Pour les femmes enceintes : rapport médical détaillé.
12. Fiche familiale pour les personnes mariées.
13. Certificat de résidence si demandé selon le lieu de dépôt ou de délivrance du passeport.
14. Originaux et photocopies complètes du dossier.

⚠️ Vérifiez toujours la liste officielle actuelle du centre de visa avant le dépôt."""


def telegram(method, data):
    if not TOKEN:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is missing")

    request = urllib.request.Request(
        f"{API}/{method}",
        data=json.dumps(data).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=15) as response:
        result = json.loads(response.read().decode("utf-8"))

    if not result.get("ok"):
        raise RuntimeError("Telegram API request failed")
    return result


def send(chat_id, text, keyboard=None):
    data = {"chat_id": chat_id, "text": text}
    if keyboard:
        data["reply_markup"] = {"inline_keyboard": keyboard}
    return telegram("sendMessage", data)


def make_rows(buttons, width=2):
    return [
        [
            {"text": label, "callback_data": value}
            for label, value in buttons[i:i + width]
        ]
        for i in range(0, len(buttons), width)
    ]


def home_button():
    return [[{"text": "🏠 Menu principal", "callback_data": "menu"}]]


def whatsapp_button():
    if WHATSAPP_URL:
        return [[{"text": "📲 Contact WhatsApp", "url": WHATSAPP_URL}]]
    return []


def start_menu(chat_id):
    text = (
        "✈️ مرحبا بكم في MALIK TRAVEL 🌍\n\n"
        "يسعدنا استقبالكم ومرافقتكم في رحلتكم، من أول خطوة حتى "
        "تحقيق مشروع سفركم.\n\n"
        "نضع تحت تصرّفكم خدماتنا في مجال التأشيرات، المواعيد، "
        "وحجوزات السفر، مع الحرص على مرافقتكم وتقديم المعلومات اللازمة.\n\n"
        "MALIK TRAVEL — وجهتكم نحو العالم. 🌐\n\n"
        "🌍 اختار البلد:"
    )
    buttons = [(label, "country_" + code) for label, code in COUNTRIES]
    send(chat_id, text, make_rows(buttons, 2))


def show_country(chat_id, country):
    names = dict((code, label) for label, code in COUNTRIES)
    if country == "autre":
        send(
            chat_id,
            "🌍 Autre pays\n\nللاستفسار عن بلد آخر، تواصل معنا.",
            whatsapp_button() + home_button(),
        )
        return

    if country == "espagne":
        send(
            chat_id,
            "🇪🇸 Espagne — إسبانيا\n\nاختار الخدمة:",
            [
                [{"text": "📅 RDV", "callback_data": "sp_rdv"}],
                [{"text": "📂 Traitement du dossier",
                  "callback_data": "sp_traitement"}],
                [{"text": "📄 Dossier à fournir",
                  "callback_data": "general_docs"}],
            ] + home_button(),
        )
        return

    send(
        chat_id,
        f"{names.get(country, country)}\n\n"
        "للحصول على معلومات حول التأشيرة والوثائق والمواعيد، تواصل معنا.",
        whatsapp_button() + home_button(),
    )


def show_regions(chat_id):
    send(
        chat_id,
        "📅 RDV Espagne\n\nاختار المركز:",
        [
            [{"text": "🇩🇿 Alger", "callback_data": "sp_alger"}],
            [{"text": "🇩🇿 Oran", "callback_data": "sp_oran"}],
        ] + home_button(),
    )


def show_centers(chat_id, city):
    if city == "alger":
        title = "📍 مواعيد الجزائر"
        buttons = [
            ("À domicile Alger", "home_alger"),
            ("ALG 1", "alg1"),
            ("ALG 2", "alg2"),
            ("ALG 3", "alg3"),
        ]
    else:
        title = "📍 مواعيد وهران"
        buttons = [
            ("À domicile Oran", "home_oran"),
            ("Oran 1", "oran1"),
            ("Oran 2", "oran2"),
            ("Oran 3", "oran3"),
        ]

    send(chat_id, title + "\n\nاختار نوع الموعد:", 
         make_rows(buttons, 2) + home_button())


def show_appointment_docs(chat_id, choice):
    if choice.startswith("home_"):
        city = "Alger" if choice.endswith("alger") else "Oran"
        text = (
            f"🏠 À domicile {city}\n\n"
            "📋 الوثائق والمعلومات المطلوبة:\n\n"
            "1. Passeport\n"
            "2. Fiche familiale en France\n"
            "3. Numéro de téléphone\n"
            "4. Adresse du domicile\n"
            "5. Email"
        )
    elif choice in ("alg1", "oran1"):
        text = (
            f"📅 {choice.upper()}\n\n"
            "📋 الوثائق المطلوبة:\n\n"
            "1. Passeport\n"
            "2. Carte magnétique فيها 10 000 DA\n"
            "3. Photo selfie"
        )
    else:
        text = (
            f"📅 {choice.upper()}\n\n"
            "📋 الوثائق المطلوبة:\n\n"
            "1. Passeport\n"
            "2. Dernier visa Espagne\n"
            "3. Carte magnétique فيها 1 000 000 DA\n"
            "4. Photo selfie"
        )

    send(
        chat_id,
        text,
        whatsapp_button() + home_button(),
    )


def show_professions(chat_id):
    send(
        chat_id,
        "📂 Traitement du dossier Espagne\n\nاختار مهنتك:",
        make_rows(PROFESSIONS, 2) + home_button(),
    )


def show_profession_docs(chat_id, profession):
    labels = dict((key, label) for label, key in PROFESSIONS)

    if profession in DOCS:
        text = DOCS[profession]
    else:
        text = (
            f"📂 {labels.get(profession, profession)}\n\n"
            "قائمة الوثائق الخاصة بهذه المهنة ما زالت تحتاج إلى التفاصيل "
            "اللي تحددها MALIK TRAVEL."
        )

    send(chat_id, text, whatsapp_button() + home_button())


def show_contact(chat_id):
    send(
        chat_id,
        "📞 MALIK TRAVEL\n\nللاستفسار حول التأشيرات والمواعيد والوثائق، تواصل معنا.",
        whatsapp_button() + home_button(),
    )


def handle_update(update):
    message = update.get("message")
    if message:
        chat_id = message["chat"]["id"]
        text = message.get("text", "").strip()

        if text.startswith("/start") or text.startswith("/help"):
            start_menu(chat_id)
        else:
            send(
                chat_id,
                "استعمل الأزرار اللي في القائمة باش تختار الخدمة.",
                home_button(),
            )
        return

    callback = update.get("callback_query")
    if not callback:
        return

    try:
        telegram("answerCallbackQuery", {
            "callback_query_id": callback["id"]
        })
    except Exception:
        pass

    chat_id = callback["message"]["chat"]["id"]
    data = callback.get("data", "")

    if data == "menu":
        start_menu(chat_id)
    elif data.startswith("country_"):
        show_country(chat_id, data[len("country_"):])
    elif data == "sp_rdv":
        show_regions(chat_id)
    elif data == "sp_alger":
        show_centers(chat_id, "alger")
    elif data == "sp_oran":
        show_centers(chat_id, "oran")
    elif data in (
        "home_alger", "home_oran",
        "alg1", "alg2", "alg3",
        "oran1", "oran2", "oran3",
    ):
        show_appointment_docs(chat_id, data)
    elif data == "sp_traitement":
        show_professions(chat_id)
    elif data in dict((key, label) for label, key in PROFESSIONS):
        show_profession_docs(chat_id, data)
    elif data == "general_docs":
        send(chat_id, GENERAL_DOCS, home_button())
    elif data == "appointments":
        show_country(chat_id, "espagne")
    elif data == "documents":
        show_professions(chat_id)
    elif data == "prices":
        send(chat_id, "💰 الأسعار حسب نوع الخدمة. تواصل معنا للتفاصيل.",
             whatsapp_button() + home_button())
    elif data == "travel":
        send(chat_id, "✈️ للاستفسار عن السفر والحجوزات، تواصل معنا.",
             whatsapp_button() + home_button())
    elif data == "contact":
        show_contact(chat_id)


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"MALIK TRAVEL bot is running")

    def do_POST(self):
        if WEBHOOK_SECRET:
            received = self.headers.get(
                "X-Telegram-Bot-Api-Secret-Token", ""
            )
            if received != WEBHOOK_SECRET:
                self.send_response(403)
                self.end_headers()
                self.wfile.write(b"Forbidden")
                return

        try:
            length = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(length)
            update = json.loads(raw.decode("utf-8"))
            handle_update(update)
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"OK")
        except Exception:
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"OK")

    def log_message(self, format, *args):
        return
