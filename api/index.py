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
}
