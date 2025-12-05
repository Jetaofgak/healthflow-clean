from fastapi import FastAPI, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
import pandas as pd
import models, database # Réutilise tes modèles existants
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset, DataQualityPreset, TargetDriftPreset

app = FastAPI()

@app.get("/audit/report", response_class=HTMLResponse)
def get_audit_report(db: Session = Depends(database.get_db)):
    # 1. Récupérer les données (Features + Prédictions)
    # On fait une jointure SQL propre ou on charge tout en pandas (bourrin mais simple pour démo)
    query = db.query(
        models.RiskPrediction.risk_score,
        models.PatientFeatures.age,
        models.PatientFeatures.gender_code,
        models.PatientFeatures.encounter_count
    ).join(models.PatientFeatures, models.RiskPrediction.pseudo_id == models.PatientFeatures.pseudo_id)
    
    # Convertir en DataFrame
    df = pd.read_sql(query.statement, db.bind)
    
    if df.empty:
        return "<h1>Pas assez de données pour l'audit</h1>"

    # 2. Créer le rapport Evidently
    # Pour la démo, on compare la première moitié des données (ref) avec la seconde (curr)
    # Ou on simule si on a peu de données
    report = Report(metrics=[
        DataQualityPreset(),
        DataDriftPreset(), 
        TargetDriftPreset()
    ])
    
    report.run(reference_data=df, current_data=df) # Auto-comparaison pour l'exemple
    
    # 3. Renvoyer le HTML
    return report.get_html()
