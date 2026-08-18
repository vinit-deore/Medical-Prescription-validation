import os
import pandas as pd

def get_patients_file_path(data_dir=None):
    if data_dir is None:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        data_dir = os.path.join(base_dir, 'data')
    return os.path.join(data_dir, 'patients.csv')

def get_default_patients():
    return [
        {"patient_id": "P001", "name": "John Doe", "age": 68, "gender": "Male", "allergies": "Penicillin", "condition": "Atrial Fibrillation & Hypertension", "blood_group": "O+", "bp": "138/88 mmHg", "heart_rate": "74 bpm"},
        {"patient_id": "P002", "name": "Emily Watson", "age": 35, "gender": "Female", "allergies": "Penicillin", "condition": "Bacterial Infection", "blood_group": "A+", "bp": "120/80 mmHg", "heart_rate": "70 bpm"},
        {"patient_id": "P003", "name": "Robert Chen", "age": 42, "gender": "Male", "allergies": "None", "condition": "Major Depression & Chronic Pain", "blood_group": "B+", "bp": "128/82 mmHg", "heart_rate": "76 bpm"},
        {"patient_id": "P004", "name": "Maria Garcia", "age": 58, "gender": "Female", "allergies": "Aspirin", "condition": "Type 2 Diabetes & Hyperlipidemia", "blood_group": "AB+", "bp": "132/84 mmHg", "heart_rate": "72 bpm"},
        {"patient_id": "P005", "name": "David Miller", "age": 74, "gender": "Male", "allergies": "Sulfa Drugs", "condition": "Heart Failure & Osteoarthritis", "blood_group": "O-", "bp": "142/90 mmHg", "heart_rate": "68 bpm"}
    ]

def load_patients(data_dir=None):
    """Loads patients DataFrame safely from data/patients.csv."""
    path = get_patients_file_path(data_dir)
    if os.path.exists(path) and os.path.getsize(path) > 0:
        try:
            df = pd.read_csv(path)
            if not df.empty:
                return df
        except Exception:
            pass

    return pd.DataFrame(get_default_patients())

def save_patient(patient_dict, data_dir=None):
    """Appends a new patient record to patients.csv."""
    path = get_patients_file_path(data_dir)
    df = load_patients(data_dir)

    new_df = pd.concat([df, pd.DataFrame([patient_dict])], ignore_index=True)
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        new_df.to_csv(path, index=False)
    except Exception:
        pass
    return new_df
