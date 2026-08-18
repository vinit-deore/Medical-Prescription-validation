import os
import pandas as pd

def get_patients_file_path(data_dir=None):
    if data_dir is None:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        data_dir = os.path.join(base_dir, 'data')
    return os.path.join(data_dir, 'patients.csv')

def load_patients(data_dir=None):
    """Loads patients DataFrame from data/patients.csv."""
    path = get_patients_file_path(data_dir)
    if os.path.exists(path):
        try:
            df = pd.read_csv(path)
            return df
        except Exception:
            pass
    # Fallback default dataframe
    default_data = [
        {"patient_id": "P001", "name": "John Doe", "age": 68, "gender": "Male", "allergies": "Penicillin", "condition": "Atrial Fibrillation & Hypertension", "blood_group": "O+", "bp": "138/88 mmHg", "heart_rate": "74 bpm"},
        {"patient_id": "P002", "name": "Emily Watson", "age": 35, "gender": "Female", "allergies": "Penicillin", "condition": "Bacterial Infection", "blood_group": "A+", "bp": "120/80 mmHg", "heart_rate": "70 bpm"},
        {"patient_id": "P003", "name": "Robert Chen", "age": 42, "gender": "Male", "allergies": "None", "condition": "Major Depression & Chronic Pain", "blood_group": "B+", "bp": "128/82 mmHg", "heart_rate": "76 bpm"}
    ]
    return pd.DataFrame(default_data)

def save_patient(patient_dict, data_dir=None):
    """Appends a new patient record to patients.csv."""
    path = get_patients_file_path(data_dir)
    df = load_patients(data_dir)

    new_df = pd.concat([df, pd.DataFrame([patient_dict])], ignore_index=True)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    new_df.to_csv(path, index=False)
    return new_df
