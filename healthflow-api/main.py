from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import os
import json
import requests

import models
import database
import auth

app = FastAPI(title="HealthFlow API")

# ----------------- CONFIG SERVICES -----------------

PROXY_URL = os.getenv("PROXY_URL", "http://127.0.0.1:8081")
DEID_URL = os.getenv("DEID_URL", "http://127.0.0.1:8082")
FEAT_URL = os.getenv("FEAT_URL", "http://127.0.0.1:8083")
MODEL_URL = os.getenv("MODEL_URL", "http://127.0.0.1:8084")

# ----------------- DB DEPENDENCY -----------------

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ----------------- STARTUP: USER TEST -----------------

@app.on_event("startup")
def create_test_user():
    db = database.SessionLocal()
    try:
        user = db.query(models.User).filter(models.User.username == "docteur").first()
        if not user:
            print("Création de l'utilisateur 'docteur'...")
            user = models.User(
                username="docteur",
                hashed_password=auth.get_password_hash("password123"),
                role="doctor"
            )
            db.add(user)
            db.commit()
    finally:
        db.close()

# ----------------- AUTH TOKEN -----------------

@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends(),
          db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = auth.create_access_token(data={"sub": user.username, "role": user.role})
    return {"access_token": access_token, "token_type": "bearer"}

# ----------------- SECURED SCORE ENDPOINT -----------------

@app.get("/api/v1/score/{pseudo_id}")
def get_patient_score(
    pseudo_id: str,
    current_user: str = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    pred = (db.query(models.RiskPrediction)
              .filter(models.RiskPrediction.pseudo_id == pseudo_id)
              .order_by(models.RiskPrediction.created_at.desc())
              .first())

    if not pred:
        raise HTTPException(status_code=404, detail="Aucun score disponible pour ce patient")

    return {
        "patient_id": pseudo_id,
        "risk_score": pred.risk_score,
        "risk_level": pred.risk_level,
        "analysis_date": pred.created_at,
        "details": json.loads(pred.shap_values_json),
        "consulted_by": current_user
    }

# ----------------- PIPELINE COMPLETE -----------------

@app.post("/pipeline/run/{patient_id}")
def run_full_pipeline(patient_id: str,
                      current_user: str = Depends(auth.get_current_user)):
    """
    1) ProxyFHIR: sync FHIR bundle pour ce patient_id
    2) DeID: anonymiser et obtenir pseudo_id
    3) Featurizer: extraire les features
    4) Model: prédire le risque
    """
    # 1. SYNC FHIR
    try:
        r1 = requests.post(f"{PROXY_URL}/api/proxy/sync/{patient_id}", timeout=30)
        if r1.status_code != 200:
            raise Exception(f"ProxyFHIR error: {r1.status_code} {r1.text}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # 2. DEID
    try:
        r2 = requests.post(f"{DEID_URL}/deid/process/{patient_id}", timeout=30)
        if r2.status_code != 200:
            raise Exception(f"DeID error: {r2.status_code} {r2.text}")
        pseudo_id = r2.json()["pseudo_id"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # 3. FEATURIZER
    try:
        r3 = requests.post(f"{FEAT_URL}/features/extract/{pseudo_id}", timeout=30)
        if r3.status_code != 200:
            raise Exception(f"Featurizer error: {r3.status_code} {r3.text}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # 4. MODEL
    try:
        r4 = requests.post(f"{MODEL_URL}/predict/risk/{pseudo_id}", timeout=30)
        if r4.status_code != 200:
            raise Exception(f"Model error: {r4.status_code} {r4.text}")
        prediction = r4.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {
        "status": "success",
        "requested_by": current_user,
        "patient_id": patient_id,
        "pseudo_id": pseudo_id,
        "prediction": prediction
    }
