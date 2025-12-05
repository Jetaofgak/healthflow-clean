from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import models, database, anonymizer

# Créer les tables manquantes (deid_patients)
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

@app.post("/deid/process/{patient_id}")
def process_patient(patient_id: str, db: Session = Depends(database.get_db)):
    # 1. Récupérer les données brutes (depuis la table Java)
    bundle = db.query(models.FhirBundle).filter(models.FhirBundle.patient_id == patient_id).first()
    
    if not bundle:
        raise HTTPException(status_code=404, detail="Données patient introuvables (lancez ProxyFHIR d'abord)")

    # 2. Générer un pseudo ID
    pseudo_id = anonymizer.generate_pseudo_id(patient_id)

    # 3. Vérifier si déjà traité
    existing = db.query(models.DeidPatient).filter(models.DeidPatient.original_patient_id == patient_id).first()
    if existing:
        return {"message": "Patient déjà anonymisé", "pseudo_id": existing.pseudo_id}

    # 4. Anonymiser le JSON
    clean_json = anonymizer.anonymize_bundle(bundle.raw_json)

    # 5. Sauvegarder
    new_record = models.DeidPatient(
        original_patient_id=patient_id,
        pseudo_id=pseudo_id,
        anonymized_data=clean_json
    )
    db.add(new_record)
    db.commit()

    return {
        "status": "success", 
        "original_id": patient_id, 
        "pseudo_id": pseudo_id,
        "message": "Données anonymisées et sauvegardées."
    }
