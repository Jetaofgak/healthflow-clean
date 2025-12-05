from sqlalchemy import Column, Integer, String, Text, DateTime, func
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
