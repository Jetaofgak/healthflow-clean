import streamlit as st
import requests
import os
import pandas as pd

API_URL = os.getenv("API_URL", "http://127.0.0.1:8085")

st.set_page_config(page_title="HealthFlow AI Dashboard", layout="wide")

# ----------------- SIDEBAR LOGIN -----------------

st.sidebar.title("🔐 Connexion Médecin")
username = st.sidebar.text_input("Username", "docteur")
password = st.sidebar.text_input("Password", type="password")

if "token" not in st.session_state:
    st.session_state["token"] = None

if st.sidebar.button("Se connecter"):
    try:
        resp = requests.post(
            f"{API_URL}/token",
            data={"username": username, "password": password},
            timeout=15,
        )
        if resp.status_code == 200:
            st.session_state["token"] = resp.json()["access_token"]
            st.sidebar.success("Connecté !")
        else:
            st.sidebar.error(f"Erreur auth: {resp.status_code}")
    except Exception as e:
        st.sidebar.error(f"API hors ligne: {e}")

# ----------------- MAIN -----------------

st.title("🏥 HealthFlow: Prédiction de Réadmission")

if not st.session_state["token"]:
    st.warning("Veuillez vous connecter dans le menu latéral.")
    st.stop()

headers = {"Authorization": f"Bearer {st.session_state['token']}"}

# --------- SECTION 1 : Pipeline complète depuis un ID FHIR ---------

st.subheader("1️⃣ Créer une prédiction à partir d'un ID FHIR")

fhir_id = st.text_input("FHIR Patient ID (ex: 1285444)", "")

if st.button("Lancer la pipeline complète"):
    if not fhir_id:
        st.error("Veuillez entrer un ID FHIR.")
    else:
        try:
            resp = requests.post(f"{API_URL}/pipeline/run/{fhir_id}",
                                 headers=headers,
                                 timeout=60)
            if resp.status_code == 200:
                data = resp.json()
                pseudo = data["pseudo_id"]
                st.success(f"Pipeline OK ! Nouveau pseudo_id : {pseudo}")
                st.write("Score brut :", data["prediction"]["risk_score"])
                st.session_state["last_pseudo_id"] = pseudo
            else:
                st.error(f"Erreur pipeline: {resp.status_code} - {resp.text}")
        except Exception as e:
            st.error(f"Erreur de connexion à l'API: {e}")

# --------- SECTION 2 : Analyse par pseudo_id ---------

st.subheader("2️⃣ Consulter un patient par pseudo_id")

default_pseudo = st.session_state.get("last_pseudo_id", "6fe631e8ce4e")
pseudo_id = st.text_input("Pseudo-ID Patient", default_pseudo)

if st.button("Analyser ce patient"):
    try:
        resp = requests.get(f"{API_URL}/api/v1/score/{pseudo_id}",
                            headers=headers,
                            timeout=30)
        if resp.status_code == 200:
            data = resp.json()

            col1, col2, col3 = st.columns(3)
            col1.metric("Niveau de Risque", data["risk_level"])
            col2.metric("Score Probabilité", f"{data['risk_score']:.2%}")
            col3.info(f"Consulté par : {data['consulted_by']}")

            st.write("Date d'analyse :", data["analysis_date"])

            st.subheader("🔍 Explication (SHAP)")
            shap_data = data["details"]
            df_shap = pd.DataFrame(list(shap_data.items()),
                                   columns=["Facteur", "Impact"])
            df_shap = df_shap.sort_values("Impact", ascending=False)
            st.bar_chart(df_shap.set_index("Facteur"))
        else:
            st.error(f"Erreur score: {resp.status_code} - {resp.text}")
    except Exception as e:
        st.error(f"Erreur de connexion à l'API: {e}")
