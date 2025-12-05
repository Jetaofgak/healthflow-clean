import xgboost as xgb
import shap
import numpy as np
import pandas as pd
import json

# Simulation d'un modèle entraîné (normalement on le chargerait depuis un fichier .json/.model)
print("Initialisation du modèle XGBoost...")
# On crée un mini dataset fictif pour initialiser le modèle
X_train = np.random.rand(100, 8) # 8 features
y_train = np.random.randint(0, 2, 100)
model = xgb.XGBClassifier(use_label_encoder=False, eval_metric='logloss')
model.fit(X_train, y_train)

# Initialisation de l'explainer SHAP
explainer = shap.TreeExplainer(model)
print("Modèle IA prêt.")

def predict_risk(features_dict):
    # 1. Convertir le dict en vecteur ordonné (MÊME ORDRE QUE L'ENTRAÎNEMENT)
    # Ordre: age, gender, encounters, conditions, diabetes, hypertension, symptoms, meds
    feature_names = [
        "age", "gender_code", "encounter_count", "condition_count", 
        "has_diabetes", "has_hypertension", "nlp_symptoms_count", "nlp_medications_count"
    ]
    
    vector = [
        features_dict.get(k, 0) for k in feature_names
    ]
    
    # Convertir en format attendu par XGBoost (DataFrame pour garder les noms)
    X = pd.DataFrame([vector], columns=feature_names)
    
    # 2. Prédiction (Probabilité de la classe 1 = Réadmission)
    prob = float(model.predict_proba(X)[0][1])
    
    # 3. Explication SHAP
    shap_values = explainer.shap_values(X)
    
    # Si binaire, shap_values est parfois une liste, on prend l'index 1 (classe positive)
    # Avec XGBClassifier récent, ça peut dépendre, on sécurise :
    if isinstance(shap_values, list):
        sv = shap_values[1][0]
    else:
        sv = shap_values[0]

    # Créer un dictionnaire d'explication trié
    explanations = {}
    for name, val in zip(feature_names, sv):
        explanations[name] = float(val)
        
    return prob, explanations
