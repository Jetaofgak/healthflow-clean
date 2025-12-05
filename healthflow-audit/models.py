from sqlalchemy import Column, Integer, String, Text, DateTime, func, Float
from database import Base

# 1. Table source (celle créée par Java)
# On la déclare juste pour pouvoir la lire, on ne la crée pas ici.
class FhirBundle(Base):
    __tablename__ = "fhir_bundles"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(String)
    raw_json = Column(Text)
    sync_date = Column(DateTime)

# 2. Table destination (Anonymisée)
class DeidPatient(Base):
    __tablename__ = "deid_patients"

    id = Column(Integer, primary_key=True, index=True)
    original_patient_id = Column(String, unique=True) # Pour garder le lien (mapping)
    pseudo_id = Column(String, unique=True, index=True) # Le nouvel ID anonyme
    anonymized_data = Column(Text) # JSON nettoyé
    created_at = Column(DateTime, default=func.now())
# 3. Table des Features (prêtes pour l'IA)
class PatientFeatures(Base):
    __tablename__ = "patient_features"

    id = Column(Integer, primary_key=True, index=True)
    pseudo_id = Column(String, unique=True) # Lien avec DeID
    
    # Voici les variables (features) qu'on va extraire
    age = Column(Integer)
    gender_code = Column(Integer) # 0=F, 1=M
    encounter_count = Column(Integer) # Nombre de visites passées
    condition_count = Column(Integer) # Nombre de diagnostics
    has_diabetes = Column(Integer) # 0 ou 1
    has_hypertension = Column(Integer) # 0 ou 1
    
    # Pour stocker le vecteur complet (utile pour le modèle)
    feature_vector_json = Column(Text) 
    
    created_at = Column(DateTime, default=func.now())
# 4. Table des Prédictions
class RiskPrediction(Base):
    __tablename__ = "risk_predictions"

    id = Column(Integer, primary_key=True, index=True)
    pseudo_id = Column(String)
    
    risk_score = Column(Float) # Probabilité (0.0 - 1.0)
    risk_level = Column(String) # "Low", "Medium", "High"
    
    shap_values_json = Column(Text) # Explications locales
    model_version = Column(String, default="v1.0")
    
    created_at = Column(DateTime, default=func.now())