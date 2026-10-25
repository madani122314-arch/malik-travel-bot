
import json
import os
import urllib.request
import urllib.parse
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

GENERAL_DOCS = """📄 DOSSIER À FOURNIR — DOCUMENTS GÉNÉRAUX

1. Formulaire uniforme de demande de visa, rempli et signé, avec une photo récente en couleur, de face, sur fond blanc.

2. Passeport valide au moins 3 mois après l'expiration du visa demandé et comportant au moins 2 pages libres.

3. Photocopies de toutes les pages du passeport actuel. Le passeport doit avoir été délivré depuis moins de 10 ans.

4. Assurance voyage couvrant toute la durée du premier séjour, valable dans l'espace Schengen, avec une couverture médicale et rapatriement d'au moins 30 000 €.

5. Justificatifs de moyens de subsistance : relevés bancaires des 6 derniers mois ou autres justificatifs de ressources.

6. Pour les mineurs ne voyageant pas avec les deux parents : autorisation parentale et extrait de naissance. Si le tuteur n'est pas le parent, fournir l'autorisation du tuteur et un justificatif de tutelle.

7. Si le demandeur dépose son dossier seul avec les documents d'un proche : prise en charge légalisée par le conjoint, les parents, frères/sœurs ou enfants, ou attestation de l'employeur selon le cas.

8. Pour les demandeurs non algériens : titre de séjour légal en Algérie, valable au moins 3 mois après l'expiration du visa. Si renouvellement en cours, joindre le justificatif correspondant.

9. Réservation d'hôtel confirmée en Espagne.

10. Réservation du billet d'avion aller-retour avec itinéraire.

11. Pour les femmes enceintes : rapport médical détaillé.

12. Pour les personnes mariées : fiche familiale.

13. Certificat de résidence si demandé, notamment selon le lieu de délivrance du passeport ou la région de dépôt.

14. Préparer les originaux et une copie complète de chaque dossier.

⚠️ La liste peut varier selon la situation personnelle. Vérifiez les exigences actuelles auprès du centre de visa compétent."""

DOCS = {
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
12. Deux photos d'identité""",

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
9. Dossier du garant qui prend en charge le voyage

📌 Les documents détaillés du garant restent à confirmer selon sa situation."""
}


def telegram(method, data):
    if not TOKEN:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is missing")

    body = json.dumps(data).encode("utf-8")
    req = urllib.request.Request(
        f"{API}/{method}",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=15) as response:
        return json.loads(response.read().decode("utf-8"))


def send(chat_id, text, keyboard=None):
    data = {
        "chat_id": chat_id,
        "text": text,
    }
    if keyboard:
        data["reply_markup"] = {"inline_keyboard": keyboard}
    return telegram("sendMessage", data)


def rows(buttons, width=2):
    result = []
    for i in range(0, len(buttons), width):
        result.append([
            {"text": label, "callback_data": value}
            for label, value in buttons[i:i + width]
        ])
    return result


def footer():
    return [[{"text": "🏠 Menu principal", "callback_data": "menu"}]]


def show_menu(chat_id):
    text = (
        "✈️ مرحبا بكم في MALIK TRAVEL 🌍\n\n"
        "يسعدنا استقبالكم ومرافقتكم في رحلتكم، من أول خطوة حتى "
        "تحقيق مشروع سفركم.\n\n"
        "نضع تحت تصرّفكم خدماتنا في مجال التأشيرات، المواعيد، "
        "وحجوزات السفر، مع الحرص على مرافقتكم وتقديم المعلومات اللازمة.\n\n"
        "MALIK TRAVEL — وجهتكم نحو العالم. 🌐\n\n"
        "اختار الخدمة اللي تحتاجها:"
    )
    keyboard = [
        [{"text": "🌍 التأشيرات حسب البلد", "callback_data": "visa"}],
        [{"text": "📅 مواعيد BLS / VFS", "callback_data": "appointments"}],
        [{"text": "📂 معالجة الملف حسب المهنة", "callback_data": "documents"}],
        [{"text": "📄 الوثائق العامة لإسبانيا", "callback_data": "general_docs"}],
        [{"text": "💰 الأسعار", "callback_data": "prices"}],
        [{"text": "✈️ السفر والحجوزات", "callback_data": "travel"}],
        [{"text": "📞 التواصل", "callback_data": "contact"}],
    ]
    send(chat_id, text, keyboard)


def show_countries(chat_id):
    buttons = [(label, "country_" + code) for label, code in COUNTRIES]
    send(
        chat_id,
        "🌍 اختار البلد اللي حاب تسافر ليه:",
        rows(buttons, 2) + footer()
    )


def show_country_options(chat_id, country):
    name = dict((code, label) for label, code in COUNTRIES).get(country, country)
    if country == "espagne":
        text = f"🇪🇸 {name}\n\nاختار الخدمة اللي تحتاجها:"
        keyboard = [
            [{"text": "📅 RDV — موعد", "callback_data": "sp_rdv"}],
            [{"text": "📂 Traitement du dossier", "callback_data": "sp_traitement"}],
            [{"text": "📄 Dossier à fournir", "callback_data": "general_docs"}],
        ] + footer()
    else:
        text = (
            f"🌍 {name}\n\n"
            "للحصول على معلومات حول التأشيرة والوثائق والمواعيد "
            "الخاصة بهذا البلد، تواصل مع MALIK TRAVEL."
        )
        keyboard = [
            [{"text": "📞 التواصل", "callback_data": "contact"}],
        ] + footer()
    send(chat_id, text, keyboard)


def show_spain_regions(chat_id):
    send(
        chat_id,
        "🇪🇸 RDV Espagne\n\nاختار المركز:",
        [
            [{"text": "🇩🇿 Alger", "callback_data": "sp_alger"}],
            [{"text": "🇩🇿 Oran", "callback_data": "sp_oran"}],
        ] + footer()
    )


def show_spain_center(chat_id, center):
    if center == "alger":
        buttons = [
            ("🏠 À domicile Alger", "sp_home_alger"),
            ("ALG 1", "sp_alg1"),
            ("ALG 2", "sp_alg2"),
            ("ALG 3", "sp_alg3"),
        ]
        title = "🇩🇿 مواعيد الجزائر — Alger"
    else:
        buttons = [
            ("🏠 À domicile Oran", "sp_home_oran"),
            ("Oran 1", "sp_oran1"),
            ("Oran 2", "sp_oran2"),
            ("Oran 3", "sp_oran3"),
        ]
        title = "🇩🇿 مواعيد وهران — Oran"

    send(chat_id, title + "\n\nاختار نوع الموعد:", rows(buttons, 2) + footer())


def show_appointment_requirements(chat_id, choice):
    home = choice in ("sp_home_alger", "sp_home_oran")
    first = choice in ("sp_alg1", "sp_oran1")
    place = "Alger" if "alger" in choice or "alg" in choice else "Oran"

    if home:
        text = (
            f"🏠 RDV À DOMICILE — {place}\n\n"
            "📋 الوثائق والمعلومات المطلوبة:\n\n"
            "1. Passeport\n"
            "2. Fiche familiale en France\n"
            "3. Numéro de téléphone\n"
            "4. Adresse du domicile\n"
            "5. Email\n\n"
            "لإكمال الطلب، تواصل معنا عبر WhatsApp."
        )
    elif first:
        text = (
            f"📅 RDV {choice.replace('sp_', '').upper()}\n\n"
            "📋 الوثائق المطلوبة:\n\n"
            "1. Passeport\n"
            "2. Carte magnétique فيها 10 000 DA\n"
            "3. Photo selfie\n\n"
            "لإكمال الطلب، تواصل معنا عبر WhatsApp."
        )
    else:
        text = (
            f"📅 RDV {choice.replace('sp_', '').upper()}\n\n"
            "📋 الوثائق المطلوبة:\n\n"
            "1. Passeport\n"
            "2. Dernier visa Espagne\n"
            "3. Carte magnétique فيها 1 000 000 DA\n"
            "4. Photo selfie\n\n"
            "لإكمال الطلب، تواصل معنا عبر WhatsApp."
        )

    keyboard = []
    if WHATSAPP_URL:
        keyboard.append([{
            "text": "📲 Contact WhatsApp",
            "url": WHATSAPP_URL
        }])
    else:
        text += "\n\n📲 رابط WhatsApp سيتم إضافته بعد تزويدنا به."

    keyboard += footer()
    send(chat_id, text, keyboard)


def show_professions(chat_id):
    send(
        chat_id,
        "📂 Traitement du dossier Espagne\n\nاختار مهنتك:",
        rows(PROFESSIONS, 2) + footer()
    )


def show_profession_docs(chat_id, profession):
    if profession in DOCS:
        text = DOCS[profession]
    else:
        labels = dict(PROFESSIONS)
        text = (
            f"📂 DOSSIER — {labels.get(profession, profession)}\n\n"
            "قائمة الوثائق الخاصة بهذه المهنة لم تتم إضافتها بعد.\n"
            "تواصل معنا للحصول على القائمة المناسبة لحالتك."
        )

    keyboard = []
    if WHATSAPP_URL:
        keyboard.append([{
            "text": "📲 Contact WhatsApp",
            "url": WHATSAPP_URL
        }])
    else:
        text += "\n\n📲 رابط WhatsApp سيتم إضافته بعد تزويدنا به."

    keyboard += footer()
    send(chat_id, text, keyboard)


def show_contact(chat_id):
    text = (
        "📞 MALIK TRAVEL\n\n"
        "للاستفسار حول التأشيرات والمواعيد والوثائق، تواصل معنا."
    )
    keyboard = []
    if WHATSAPP_URL:
        keyboard.append([{
            "text": "📲 Contact WhatsApp",
            "url": WHATSAPP_URL
        }])
    else:
        text += "\n\nرابط WhatsApp لم يُضف بعد."
    keyboard += footer()
    send(chat_id, text, keyboard)


def handle_update(update):
    if "message" in update:
        message = update["message"]
        chat_id = message["chat"]["id"]
        text = message.get("text", "").strip()

        if text in ("/start", "/help"):
            show_menu(chat_id)
        else:
            send(
                chat_id,
                "اختار خدمة من القائمة باش نقدر نعاونك.",
                footer()
            )
        return

    callback = update.get("callback_query")
    if not callback:
        return

    data = callback.get("data", "")
    chat_id = callback["message"]["chat"]["id"]

    try:
        telegram("answerCallbackQuery", {
            "callback_query_id": callback["id"]
        })
    except Exception:
        pass

    if data == "menu":
        show_menu(chat_id)
    elif data == "visa":
        show_countries(chat_id)
    elif data.startswith("country_"):
        show_country_options(chat_id, data.replace("country_", "", 1))
    elif data == "sp_rdv":
        show_spain_regions(chat_id)
    elif data == "sp_alger":
        show_spain_center(chat_id, "alger")
    elif data == "sp_oran":
        show_spain_center(chat_id, "oran")
    elif data in (
        "sp_home_alger", "sp_home_oran",
        "sp_alg1", "sp_alg2", "sp_alg3",
        "sp_oran1", "sp_oran2", "sp_oran3"
    ):
        show_appointment_requirements(chat_id, data)
    elif data == "sp_traitement":
        show_professions(chat_id)
    elif data.startswith("salarie") or data in dict(PROFESSIONS).values():
        show_profession_docs(chat_id, data)
    elif data == "general_docs":
        send(chat_id, GENERAL_DOCS, footer())
    elif data == "appointments":
        send(
            chat_id,
            "📅 المواعيد\n\nاختار إسبانيا من قائمة البلدان للوصول إلى خيارات RDV الجزائر ووهران.",
            [
                [{"text": "🇪🇸 Espagne", "callback_data": "country_espagne"}],
            ] + footer()
        )
    elif data == "documents":
        show_professions(chat_id)
    elif data == "prices":
        send(
            chat_id,
            "💰 الأسعار تختلف حسب نوع الخدمة والملف.\n\n"
            "تواصل معنا للحصول على التفاصيل.",
            footer()
        )
    elif data == "travel":
        send(
            chat_id,
            "✈️ MALIK TRAVEL تساعدك في معلومات السفر والحجوزات.\n\n"
            "تواصل معنا لمعرفة التفاصيل.",
            footer()
        )
    elif data == "contact":
        show_contact(chat_id)


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"MALIK TRAVEL bot is running")

    def do_POST(self):
        if WEBHOOK_SECRET:
            received_secret = self.headers.get(
                "X-Telegram-Bot-Api-Secret-Token", ""
            )
            if received_secret != WEBHOOK_SECRET:
                self.send_response(403)
                self.end_headers()
                self.wfile.write(b"Forbidden")
                return

        try:
            length = int(self.headers.get("Content-Length", 0))
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
