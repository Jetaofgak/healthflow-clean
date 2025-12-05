from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import Float, String, Text
import models, database, predictor
import json

# Création tables
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

@app.post("/predict/risk/{pseudo_id}")
def predict_patient_risk(pseudo_id: str, db: Session = Depends(database.get_db)):
    # 1. Récupérer les features du patient
    feat_record = db.query(models.PatientFeatures).filter(models.PatientFeatures.pseudo_id == pseudo_id).first()
    
    if not feat_record:
        raise HTTPException(status_code=404, detail="Features introuvables. Lancez le Featurizer d'abord.")

    # 2. Parser le JSON des features
    features_dict = json.loads(feat_record.feature_vector_json)

    # 3. Appeler l'IA (XGBoost + SHAP)
    risk_score, shap_explanations = predictor.predict_risk(features_dict)
    
    # Déterminer le niveau
    level = "Low"
    if risk_score > 0.7: level = "High"
    elif risk_score > 0.4: level = "Medium"

    # 4. Sauvegarder la prédiction
    pred = models.RiskPrediction(
        pseudo_id=pseudo_id,
        risk_score=risk_score,
        risk_level=level,
        shap_values_json=json.dumps(shap_explanations)
    )
    db.add(pred)
    db.commit()

    return {
        "status": "success",
        "pseudo_id": pseudo_id,
        "risk_score": round(risk_score, 4),
        "risk_level": level,
        "explanations": shap_explanations
    }
