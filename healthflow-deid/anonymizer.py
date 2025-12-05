import json
from faker import Faker
import hashlib

fake = Faker('fr_FR') # Générateur de fausses données françaises

def generate_pseudo_id(real_id: str):
    # Crée un ID stable basé sur le vrai ID (hash)
    return hashlib.sha256(real_id.encode()).hexdigest()[:12]

def anonymize_bundle(raw_json_str: str):
    data = json.loads(raw_json_str)
    
    # Si c'est un Bundle FHIR, on parcourt les entrées
    if 'entry' in data:
        for entry in data['entry']:
            resource = entry.get('resource', {})
            
            # Si c'est le Patient, on change ses infos
            if resource.get('resourceType') == 'Patient':
                # On remplace le nom
                if 'name' in resource:
                    resource['name'] = [{
                        'family': fake.last_name(),
                        'given': [fake.first_name()],
                        'use': 'official'
                    }]
                
                # On remplace l'adresse
                if 'address' in resource:
                    resource['address'] = [{
                        'line': [fake.street_address()],
                        'city': fake.city(),
                        'postalCode': fake.postcode(),
                        'country': 'FR'
                    }]
                    
                # On garde la date de naissance (utile pour l'âge) mais on pourrait la flouter
                # On garde le genre (utile pour la prédiction)

    return json.dumps(data)
