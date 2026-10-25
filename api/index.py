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
    "job_retraite": [
        "Attestation de perception d’une pension de retraite."
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
        "Justificatifs d’une situation socioéconomique adéquate, par exemple certificat de mariage, livret de famille ou documents prouvant la propriété d’un bien."
    ],
}GENERAL_DOCS = [
    "Formulaire de demande de visa signé avec photo récente en couleur.",
    "Passeport valide au moins 3 mois après l’expiration du visa demandé, avec 2 pages libres.",
    "Photocopies de toutes les pages du passeport.",
    "Assurance voyage Schengen couvrant au minimum 30 000 €.",
    "Relevés bancaires des 6 derniers mois et justificatifs de ressources.",
    "Pour les mineurs : autorisation parentale et documents nécessaires selon la situation.",
    "Prise en charge légalisée si les frais sont payés par un tiers.",
    "Pour les demandeurs non algériens : titre de séjour valide en Algérie.",
    "Réservation d’hôtel en Espagne.",
    "Réservation ou billet d’avion aller-retour.",
    "Pour les femmes enceintes : rapport médical si nécessaire.",
    "Fiche familiale pour les demandeurs mariés.",
    "Certificat de résidence si demandé par le centre.",
    "Présenter les originaux et les photocopies nécessaires.",
]

CENTERS = {
    "alger": [
        ("À domicile Alger", "home_alger"),
        ("ALG 1", "alg1"),
        ("ALG 2", "alg2"),
        ("ALG 3", "alg3"),
    ],
    "oran": [
        ("À domicile Oran", "home_oran"),
        ("Oran 1", "oran1"),
        ("Oran 2", "oran2"),
        ("Oran 3", "oran3"),
    ],
}

REGULAR_CENTER_DOCS = [
    "Passeport",
    "Dernier visa Espagne",
    "Carte magnétique : 10 000 DA",
    "Photo selfie",
]

HOME_CENTER_DOCS = [
    "Passeport",
    "Fiche familiale en France",
    "Numéro de téléphone",
    "Adresse du domicile",
    "Email",
]

CENTER_LABELS = {
    "alg1": "ALG 1",
    "alg2": "ALG 2",
    "alg3": "ALG 3",
    "oran1": "Oran 1",
    "oran2": "Oran 2",
    "oran3": "Oran 3",
    "home_alger": "À domicile Alger",
    "home_oran": "À domicile Oran",
}


def button(text, data):
    return {"text": text, "callback_data": data}


def keyboard(rows):
    return {"inline_keyboard": rows}


def numbered(items):
    return "\n".join(
        f"{i}. {item}" for i, item in enumerate(items, 1)
    )


def telegram(method, payload):
    if not BOT_TOKEN:
        raise RuntimeError(
            "La variable TELEGRAM_BOT_TOKEN est absente."
        )

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/{method}"
    body = json.dumps(
        payload, ensure_ascii=False
    ).encode("utf-8")

    request = urllib.request.Request(
        url,
        data=body,
        headers={
            "Content-Type": "application/json; charset=utf-8"
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            result = json.loads(
                response.read().decode("utf-8")
            )
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode(
            "utf-8", errors="replace"
        )
        raise RuntimeError(
            f"Telegram {method} HTTP {exc.code}: {detail}"
        ) from exc

    if not result.get("ok"):
        raise RuntimeError(
            f"Telegram {method} API error: {result}"
        )

    return result.get("result")


def send(chat_id, text, reply_markup=None):
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }

    if reply_markup:
        payload["reply_markup"] = reply_markup

    return telegram("sendMessage", payload)


def answer_callback(callback_id):
    if callback_id:
        try:
            telegram(
                "answerCallbackQuery",
                {"callback_query_id": callback_id},
            )
        except Exception:
            LOG.exception(
                "Failed to answer callback query"
            )


def edit_or_send(
    chat_id, message_id, text, reply_markup=None
):
    if not message_id:
        return send(chat_id, text, reply_markup)

    payload = {
        "chat_id": chat_id,
        "message_id": message_id,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }

    if reply_markup:
        payload["reply_markup"] = reply_markup

    try:
        return telegram("editMessageText", payload)
    except Exception as exc:
        if "message is not modified" in str(exc).lower():
            return None

        LOG.warning(
            "Edit failed; trying sendMessage instead: %s",
            exc,
        )
        return send(chat_id, text, reply_markup)


def country_keyboard():
    rows = []

    for i in range(0, len(COUNTRIES), 2):
        rows.append([
            button(label, data)
            for label, data in COUNTRIES[i:i + 2]
        ])

    return keyboard(rows)


def show_home(chat_id, message_id=None):
    text = (
        WELCOME
        + "\n\n<b>Choisissez votre destination :</b>"
    )
    return edit_or_send(
        chat_id,
        message_id,
        text,
        country_keyboard(),
    )


def show_spain_menu(chat_id, message_id=None):
    rows = [
        [button("📅 RDV", "es_rdv")],
        [button("📂 Traitement du dossier", "es_general_docs")],
        [button("📄 Dossier à fournir", "es_professions")],
        [button("⬅️ Menu principal", "home")],
    ]

    return edit_or_send(
        chat_id,
        message_id,
        "🇪🇸 <b>ESPAGNE</b>\n\nChoisissez le service souhaité :",
        keyboard(rows),
    )


def show_general_docs(chat_id, message_id=None):
    text = """📂 <b>TRAITEMENT DU DOSSIER</b>

📝 <b>1. FORMULAIRE VISA SCHENGEN</b>
Saisie et vérification des informations.

🏨 <b>2. RÉSERVATION HÔTEL</b>
Réservation et confirmation selon disponibilité.

✈️ <b>3. BILLET D’AVION / TELEX</b>
Réservation selon la destination et le service disponible.

🗺️ <b>4. PLAN DE VOYAGE</b>
Itinéraire, hébergement et déplacements.

📨 <b>5. LETTRE DE MOTIVATION</b>
Rédaction personnalisée selon votre profil.

📩 <b>Contactez-nous pour les informations et les tarifs.</b>"""

    rows = [
        [{"text": "📱 WhatsApp", "url": WHATSAPP_URL}],
        [button("🏠 Menu principal", "home")],
    ]

    return edit_or_send(
        chat_id,
        message_id,
        text,
        keyboard(rows),
    )


def show_professions(chat_id, message_id=None):
    rows = [
        [button(label, data)]
        for label, data in PROFESSIONS
    ]

    rows += [
        [button("⬅️ Retour Espagne", "country_es")],
        [button("🏠 Menu principal", "home")],
    ]

    return edit_or_send(
        chat_id,
        message_id,
        "📄 <b>DOSSIER À FOURNIR — ESPAGNE</b>\n\nChoisissez votre profession :",
        keyboard(rows),
    )


def show_profession_docs(
    chat_id, callback_data, message_id=None
):
    names = {
        data: label
        for label, data in PROFESSIONS
    }

    name = names.get(callback_data)
    specific_docs = PROFESSION_DOCS.get(callback_data)

    if name is None or specific_docs is None:
        LOG.error(
            "Unknown profession callback: %r",
            callback_data,
        )
        return edit_or_send(
            chat_id,
            message_id,
            "Profession non reconnue. Veuillez choisir à nouveau.",
            keyboard([
                [button("⬅️ Retour aux professions", "es_professions")],
                [button("🏠 Menu principal", "home")],
            ]),
        )

    docs = COMMON_PROFESSION_DOCS + specific_docs

    text = (
        f"📄 <b>{name.upper()} — ESPAGNE</b>\n\n"
        f"<b>Documents à fournir :</b>\n\n"
        + numbered(docs)
    )

    rows = [
        [button("⬅️ Retour aux professions", "es_professions")],
        [{"text": "📱 Contact WhatsApp", "url": WHATSAPP_URL}],
        [button("🏠 Menu principal", "home")],
    ]

    return edit_or_send(
        chat_id,
        message_id,
        text,
        keyboard(rows),
    )


def show_cities(chat_id, message_id=None):
    rows = [
        [button("🇩🇿 Alger", "city_alger")],
        [button("🇩🇿 Oran", "city_oran")],
        [button("⬅️ Retour Espagne", "country_es")],
        [button("🏠 Menu principal", "home")],
    ]

    return edit_or_send(
        chat_id,
        message_id,
        "📅 <b>RDV ESPAGNE</b>\n\nChoisissez la ville :",
        keyboard(rows),
    )


def show_centers(chat_id, city, message_id=None):
    if city not in CENTERS:
        return show_cities(chat_id, message_id)

    rows = [
        [button(label, data)]
        for label, data in CENTERS[city]
    ]

    back_callback = (
        "city_alger" if city == "alger" else "city_oran"
    )

    rows += [
        [button("⬅️ Retour aux villes", "es_rdv")],
        [button("🏠 Menu principal", "home")],
    ]

    return edit_or_send(
        chat_id,
        message_id,
        f"📅 <b>RDV ESPAGNE — {city.upper()}</b>\n\nChoisissez le centre :",
        keyboard(rows),
    )


def show_center_docs(
    chat_id, center_code, message_id=None
):
    center_name = CENTER_LABELS.get(center_code)

    if not center_name:
        return show_cities(chat_id, message_id)

    if center_code.startswith("home_"):
        docs = HOME_CENTER_DOCS
    else:
        docs = REGULAR_CENTER_DOCS

    text = (
        f"📅 <b>{center_name.upper()}</b>\n\n"
        "<b>Informations à préparer :</b>\n\n"
        + numbered(docs)
    )

    rows = [
        [{"text": "📱 WhatsApp", "url": WHATSAPP_URL}],
        [button("🏠 Menu principal", "home")],
    ]

    return edit_or_send(
        chat_id,
        message_id,
        text,
        keyboard(rows),
    )
