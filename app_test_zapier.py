import streamlit as st
import requests
import random
import string
from datetime import datetime
import importlib

st.set_page_config(page_title="Test: Neurodiversität", layout="centered")

# Logo einbinden
st.image("Logo Vector_01.png", width=200)
st.title("Selbsteinschätzung: Testversion")

antwortoptionen = ["Trifft gar nicht zu", "Trifft wenig zu", "Teils/teils", "Trifft zu", "Trifft völlig zu"]
wertung = {"Trifft gar nicht zu": 1, "Trifft wenig zu": 2, "Teils/teils": 3, "Trifft zu": 4, "Trifft völlig zu": 5}

# Auswahl der Version
version = st.selectbox("Welche Version möchtest du nutzen?", ["Vollversion", "Testversion (10 Fragen)"])

if version == "Vollversion":
    abschnittsmodul = importlib.import_module("abschnitte_fragen")
else:
    abschnittsmodul = importlib.import_module("abschnitte_fragen_kurz")

abschnitte = abschnittsmodul.abschnitte

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
    with st.spinner("Geschafft! Bitte habe einen Augenblick Geduld. Sobald die Daten übertragen sind, wird hier die Auswertung angezeigt. Bitte Fragebogen nicht verlassen."):
        datum = datetime.today().strftime("%Y-%m-%d")
        code = "SATT-" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        webhook_url = "https://script.google.com/macros/s/AKfycbwzndSMdKyKNt6rp7vGVErQkEzvoxNrDTUSRZZLQL5EJCy1o-h__cNfEUHeXIhEZB6p8Q/exec"

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
            except Exception as e:
                st.error(f"Fehler beim Senden der Antwort: {e}")

        st.success("Die Daten wurden erfolgreich übermittelt. Bitte merke dir die Testnummer.")
        st.info(f"Dein persönlicher Testcode: **{code}**")
        st.balloons()

        # Auswertung anzeigen und Abschnittsbewertungen übertragen
        st.subheader("Ergebnisse pro Abschnitt")
        for abschnitt, (score, maxscore) in abschnittsscores.items():
            prozent = (score / maxscore) * 100
            if prozent >= 80:
                einstufung = "🔴 Deutlich auffällig"
                farbe = "rot"
            elif prozent >= 60:
                einstufung = "🟡 Leicht auffällig"
                farbe = "gelb"
            else:
                einstufung = "🟢 Unauffällig"
                farbe = "grün"

            st.write(f"**{abschnitt}**: {score} von {maxscore} Punkten → {einstufung}")

            auswertung_payload = {
                "datum": datum,
                "testcode": code,
                "abschnitt": abschnitt,
                "score": score,
                "maxscore": maxscore,
                "prozent": round(prozent, 1),
                "bewertung": einstufung,
                "farbe": farbe,
                "typ": "abschnitt"
            }
            try:
                r = requests.post(webhook_url, json=auswertung_payload)
                if r.status_code != 200:
                    st.warning(f"Abschnitt **{abschnitt}** konnte nicht gespeichert werden (Status: {r.status_code})")
            except Exception as e:
                st.error(f"Fehler beim Senden der Abschnittsauswertung: {e}")
