
import streamlit as st
import requests
import random
import string
from datetime import datetime

st.set_page_config(page_title="Test: Neurodiversität", layout="centered")

# Zentriertes Logo
st.markdown(
    "<div style='text-align: center;'><img src='Logo Vector_01.png' width='200'></div>",
    unsafe_allow_html=True
)
st.title("Selbsteinschätzung: Testversion")

antwortoptionen = ["Trifft gar nicht zu", "Trifft wenig zu", "Teils/teils", "Trifft zu", "Trifft völlig zu"]
wertung = {"Trifft gar nicht zu": 1, "Trifft wenig zu": 2, "Teils/teils": 3, "Trifft zu": 4, "Trifft völlig zu": 5}

# Abschnittsdaten importieren aus externer Datei (Platzhalter: hier würden alle 90 Fragen stehen)
from abschnitte_data import abschnitte

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

    webhook_url = "https://script.google.com/macros/s/AKfycbxTwgNRJLpNPkgrc9lkeQnGo65fbyVBMKs-O3FNZjjf3FKQKWNliN-V7eMBQ-TN6ck58g/exec"

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

    for abschnitt, (score, maxscore) in abschnittsscores.items():
        prozent = (score / maxscore) * 100
        if prozent >= 80:
            einstufung = "Deutlich auffällig"
        elif prozent >= 60:
            einstufung = "Leicht auffällig"
        else:
            einstufung = "Unauffällig"

        payload = {
            "datum": datum,
            "testcode": code,
            "abschnitt": abschnitt,
            "score": score,
            "maxscore": maxscore,
            "prozent": prozent,
            "bewertung": einstufung,
            "typ": "abschnitt"
        }
        try:
            requests.post(webhook_url, json=payload)
        except Exception as e:
            st.error(f"Fehler beim Senden der Abschnittsdaten: {e}")

    st.success("Die Daten wurden erfolgreich übermittelt. Bitte merke dir die Testnummer.")
    st.info(f"Dein persönlicher Testcode: **{code}**")
    st.balloons()

    st.subheader("Ergebnisse pro Abschnitt")
    for abschnitt, (score, maxscore) in abschnittsscores.items():
        prozent = (score / maxscore) * 100
        if prozent >= 80:
            einstufung = "🔴 Deutlich auffällig"
        elif prozent >= 60:
            einstufung = "🟡 Leicht auffällig"
        else:
            einstufung = "🟢 Unauffällig"
        st.write(f"**{abschnitt}**: {score} von {maxscore} Punkten → {einstufung}")
