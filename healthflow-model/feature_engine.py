import json
import spacy
from transformers import pipeline
from datetime import datetime

# 1. Chargement du modèle NLP (une seule fois au démarrage)
print("Chargement des modèles NLP...")
nlp = spacy.load("en_core_web_sm")
# Pipeline BioBERT pour la reconnaissance d'entités nommées (NER)
# On utilise un petit modèle biomédical rapide pour la démo
ner_pipeline = pipeline("ner", model="d4data/biomedical-ner-all", tokenizer="d4data/biomedical-ner-all", aggregation_strategy="simple")
print("Modèles chargés !")

def calculate_age(birth_date_str):
    if not birth_date_str: return 0
    try:
        birth = datetime.strptime(birth_date_str, "%Y-%m-%d")
        return datetime.now().year - birth.year
    except: return 0

def extract_features(anonymized_json_str: str):
    data = json.loads(anonymized_json_str)
    
    features = {
        "age": 0,
        "gender_code": 0,
        "encounter_count": 0,
        "condition_count": 0,
        "has_diabetes": 0,
        "has_hypertension": 0,
        "nlp_symptoms_count": 0,  # Nouvelle feature NLP
        "nlp_medications_count": 0 # Nouvelle feature NLP
    }

    # Récupération de tous les textes libres (notes, descriptions)
    clinical_texts = []

    if 'entry' in data:
        for entry in data['entry']:
            res = entry.get('resource', {})
            rtype = res.get('resourceType')

            # --- Extraction Structurelle ---
            if rtype == 'Patient':
                features['age'] = calculate_age(res.get('birthDate'))
                features['gender_code'] = 1 if res.get('gender') == 'male' else 0
            
            if rtype == 'Condition':
                features['condition_count'] += 1
                # On récupère aussi le texte du diagnostic pour le NLP
                if 'code' in res and 'text' in res['code']:
                    clinical_texts.append(res['code']['text'])

            # --- Récupération Textes ---
            # Souvent dans FHIR, les notes sont dans "DocumentReference" ou "Observation" (component text)
            if rtype == 'Observation' and 'valueString' in res:
                clinical_texts.append(res['valueString'])

    # --- Extraction NLP Avancée (BioBERT) ---
    full_text = " ".join(clinical_texts)
    if full_text:
        # Analyse NER avec BioBERT
        entities = ner_pipeline(full_text)
        
        for entity in entities:
            label = entity['entity_group']
            # Comptage basé sur les entités détectées
            if label in ['Sign_symptom', 'Diagnostic_procedure']:
                features['nlp_symptoms_count'] += 1
            elif label in ['Medication', 'Biological_structure']:
                features['nlp_medications_count'] += 1

    return features
