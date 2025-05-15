
import streamlit as st
import requests
import random
import string
from datetime import datetime

st.set_page_config(page_title="Test: Neurodiversität", layout="centered")
st.title("Selbsteinschätzung: Testversion")

antwortoptionen = ["Trifft gar nicht zu", "Trifft wenig zu", "Teils/teils", "Trifft zu", "Trifft völlig zu"]
wertung = {"Trifft gar nicht zu": 1, "Trifft wenig zu": 2, "Teils/teils": 3, "Trifft zu": 4, "Trifft völlig zu": 5}

fragen = [
    "Ich finde es anstrengend, Gespräche in Gruppen zu führen.",
    "Ich spüre eine innere Unruhe, besonders in ruhigen Momenten.",
    "Ich ziehe mich nach sozialen Kontakten zurück, um mich zu erholen.",
    "Ich verliere oft den Faden beim Reden.",
    "Ich habe Mühe, Gesichtsausdrücke richtig zu interpretieren.",
    "Ich funktioniere im Alltag meist durch äußere Struktur.",
    "Ich bin sehr empfindlich gegenüber Geräuschen oder Licht.",
    "Ich finde es schwer, meine eigenen Bedürfnisse zu spüren.",
    "Ich beobachte andere, um zu wissen, wie ich mich verhalten soll.",
    "Ich ziehe Gespräche zu zweit größeren Gruppen vor."
]

antworten = []
for i, frage in enumerate(fragen, 1):
    antwort = st.radio(f"{i}. {frage}", antwortoptionen, key=i)
    antworten.append((frage, antwort, wertung[antwort]))

if st.button("Abschicken & Auswerten"):
    datum = datetime.today().strftime("%Y-%m-%d")
    code = "SATT-" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    st.success(f"Testcode: {code} – Danke fürs Ausfüllen!")

    # Webhook (anpassen auf deinen echten Zapier-Link!)
    zapier_url = "https://hooks.zapier.com/hooks/catch/7436424/27unfyd/"

    for nr, (frage, antwort, score) in enumerate(antworten, 1):
        payload = {
            "datum": datum,
            "testcode": code,
            "fragenummer": nr,
            "frage": frage,
            "antwort": antwort,
            "score": score
        }
        try:
            requests.post(zapier_url, json=payload)
        except:
            st.warning("Fehler beim Senden an Zapier.")

    st.balloons()
