
import streamlit as st
import requests
import random
import string
from datetime import datetime

st.set_page_config(page_title="Test: Neurodiversität", layout="centered")
st.title("Selbsteinschätzung: Testversion")

antwortoptionen = ["Trifft gar nicht zu", "Trifft wenig zu", "Teils/teils", "Trifft zu", "Trifft völlig zu"]
wertung = {"Trifft gar nicht zu": 1, "Trifft wenig zu": 2, "Teils/teils": 3, "Trifft zu": 4, "Trifft völlig zu": 5}

# Strukturierte Abschnitte
abschnitte = {
    "Soziale Kommunikation": [
        "Ich finde es anstrengend, Gespräche in Gruppen zu führen.",
        "Ich habe Mühe, Gesichtsausdrücke richtig zu interpretieren.",
        "Ich beobachte andere, um zu wissen, wie ich mich verhalten soll.",
        "Ich ziehe Gespräche zu zweit größeren Gruppen vor."
    ],
    "Selbstregulation & Struktur": [
        "Ich spüre eine innere Unruhe, besonders in ruhigen Momenten.",
        "Ich verliere oft den Faden beim Reden.",
        "Ich funktioniere im Alltag meist durch äußere Struktur.",
        "Ich finde es schwer, meine eigenen Bedürfnisse zu spüren."
    ],
    "Sensorische Empfindlichkeit": [
        "Ich bin sehr empfindlich gegenüber Geräuschen oder Licht.",
        "Ich ziehe mich nach sozialen Kontakten zurück, um mich zu erholen."
    ]
}

antworten = []
abschnittsscores = {}
frage_nummer = 1

for abschnitt, fragen in abschnitte.items():
    st.header(abschnitt)
    score = 0
    for frage in fragen:
        antwort = st.radio(f"{frage_nummer}. {frage}", antwortoptionen, key=frage_nummer)
        antworten.append({
            "abschnitt": abschnitt,
            "nummer": frage_nummer,
            "frage": frage,
            "antwort": antwort,
            "score": wertung[antwort]
        })
        score += wertung[antwort]
        frage_nummer += 1
    abschnittsscores[abschnitt] = (score, len(fragen) * 5)

if st.button("Abschicken & Auswerten"):
    datum = datetime.today().strftime("%Y-%m-%d")
    code = "SATT-" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    st.success(f"Testcode: {code} – Danke fürs Ausfüllen!")

    webhook_url = "https://script.google.com/macros/library/d/1UAWELk9XSOHdqsDco6tPzm8klNle0ifM47IVVoHmIZJ2mLX9Nl9k7MQp/1"

    # Einzelantworten senden
    for eintrag in antworten:
        payload = {
            "datum": datum,
            "testcode": code,
            "abschnitt": eintrag["abschnitt"],
            "fragenummer": eintrag["nummer"],
            "frage": eintrag["frage"],
            "antwort": eintrag["antwort"],
            "score": eintrag["score"],
            "typ": "antwort"
        }
        try:
            requests.post(webhook_url, json=payload)
        except:
            st.warning("Fehler beim Senden einer Antwort an Google Sheet.")

    # Abschnittsauswertung senden
    for abschnitt, (score, maxscore) in abschnittsscores.items():
        prozent = (score / maxscore) * 100
        if prozent >= 80:
            einstufung = "🔴 Deutlich auffällig"
        elif prozent >= 60:
            einstufung = "🟡 Leicht auffällig"
        else:
            einstufung = "🟢 Unauffällig"

        summary_payload = {
            "datum": datum,
            "testcode": code,
            "abschnitt": abschnitt,
            "score": score,
            "maxscore": maxscore,
            "prozent": round(prozent, 2),
            "einstufung": einstufung,
            "typ": "abschnitt"
        }
        try:
            requests.post(webhook_url, json=summary_payload)
        except:
            st.warning(f"Fehler beim Senden der Auswertung zu {abschnitt}.")

    st.balloons()
