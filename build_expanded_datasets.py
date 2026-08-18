import os
import json
import pandas as pd

def build_expanded_datasets():
    print("=" * 60)
    print("BUILDING EXPANDED MEDICAL DATASETS FROM LOCAL RAW DATA")
    print("=" * 60)

    curr_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(curr_dir)
    data_dir = os.path.join(curr_dir, 'data')
    os.makedirs(data_dir, exist_ok=True)

    json_path = os.path.join(parent_dir, 'DDI Database.json')
    real_csv_path = os.path.join(parent_dir, 'real_drug_dataset.csv')
    df_csv_path = os.path.join(parent_dir, 'drug_df.csv')

    drugs_dict = {}  # {drug_name: category}
    interactions_list = []  # list of dicts
    side_effects_dict = {}  # {drug_name: set of side effects}

    # 1. Parse DDI Database.json
    if os.path.exists(json_path):
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                ddi_data = json.load(f)
            
            # Navigate drug_interactions
            di = ddi_data.get('drug_interactions', {})
            for category_key in di:
                items = di[category_key]
                if isinstance(items, list):
                    for item in items:
                        d_a = str(item.get('drug_a', '')).strip()
                        d_b = str(item.get('drug_b', '')).strip()
                        sev = str(item.get('severity', category_key)).strip()
                        eff = str(item.get('effect', item.get('mechanism', 'Interaction alert'))).strip()
                        alt = str(item.get('Safer_alternative', item.get('safer_alternative', 'Clinical review required'))).strip()
                        rat = str(item.get('rationale', 'Monitor patient closely')).strip()

                        if d_a and d_b:
                            interactions_list.append({
                                'drug_a': d_a,
                                'drug_b': d_b,
                                'severity': sev.title(),
                                'effect': eff,
                                'safer_alternative': alt,
                                'rationale': rat
                            })
                            # Add default category if unknown
                            if d_a not in drugs_dict:
                                drugs_dict[d_a] = "Prescription Medication"
                            if d_b not in drugs_dict:
                                drugs_dict[d_b] = "Prescription Medication"
        except Exception as e:
            print(f"Error reading DDI Database.json: {e}")

    # 2. Parse real_drug_dataset.csv
    if os.path.exists(real_csv_path):
        try:
            r_df = pd.read_csv(real_csv_path)
            for _, row in r_df.iterrows():
                d_name = str(row.get('Drug_Name', '')).strip()
                se = str(row.get('Side_Effects', '')).strip()
                cond = str(row.get('Condition', '')).strip()

                if d_name:
                    if d_name not in drugs_dict or drugs_dict[d_name] == "Prescription Medication":
                        if cond:
                            drugs_dict[d_name] = f"Treatment for {cond}"
                        else:
                            drugs_dict[d_name] = "Therapeutic Drug"

                    if se and se.lower() != 'none' and se.lower() != 'nan':
                        if d_name not in side_effects_dict:
                            side_effects_dict[d_name] = set()
                        side_effects_dict[d_name].add(se)
        except Exception as e:
            print(f"Error reading real_drug_dataset.csv: {e}")

    # 3. Parse drug_df.csv for additional side effects
    if os.path.exists(df_csv_path):
        try:
            d_df = pd.read_csv(df_csv_path)
            for _, row in d_df.iterrows():
                d_name = str(row.get('drugname', '')).strip().title()
                pt_se = str(row.get('pt', '')).strip()

                if d_name and pt_se and pt_se.lower() != 'nan':
                    if d_name not in side_effects_dict:
                        side_effects_dict[d_name] = set()
                    if len(side_effects_dict[d_name]) < 8:  # cap per drug
                        side_effects_dict[d_name].add(pt_se)
        except Exception as e:
            print(f"Error reading drug_df.csv: {e}")

    # Default category mapping polish
    category_map = {
        'Warfarin': 'Anticoagulant',
        'Aspirin': 'Antiplatelet / Analgesic',
        'Ibuprofen': 'NSAID Analgesic',
        'Simvastatin': 'Statin / Lipid Lowering',
        'Clarithromycin': 'Macrolide Antibiotic',
        'Sertraline': 'SSRI Antidepressant',
        'Tramadol': 'Opioid Analgesic',
        'Clopidogrel': 'Antiplatelet Agent',
        'Omeprazole': 'Proton Pump Inhibitor',
        'Digoxin': 'Cardiac Glycoside',
        'Verapamil': 'Calcium Channel Blocker',
        'Lithium': 'Mood Stabilizer',
        'Codeine': 'Opioid Analgesic',
        'Paroxetine': 'SSRI Antidepressant',
        'Theophylline': 'Bronchodilator',
        'Ciprofloxacin': 'Fluoroquinolone Antibiotic',
        'Rifampin': 'Rifamycin Antibiotic',
        'Sildenafil': 'PDE5 Inhibitor',
        'Nitroglycerin': 'Nitrate Vasodilator',
        'Valproic Acid': 'Anticonvulsant',
        'Lamotrigine': 'Anticonvulsant',
        'Fluconazole': 'Antifungal',
        'Metformin': 'Biguanide Antidiabetic',
        'Glipizide': 'Sulfonylurea Antidiabetic',
        'Metoprolol': 'Beta-1 Blocker',
        'Amlodipine': 'Calcium Channel Blocker',
        'Lisinopril': 'ACE Inhibitor',
        'Paracetamol': 'Analgesic / Antipyretic',
        'Penicillin': 'Beta-Lactam Antibiotic',
        'Amoxicillin': 'Aminopenicillin Antibiotic',
        'Azithromycin': 'Macrolide Antibiotic',
        'Bupropion': 'NDRI Antidepressant',
        'Escitalopram': 'SSRI Antidepressant',
        'Insulin Glargine': 'Long-Acting Insulin',
        'Losartan': 'Angiotensin II Receptor Blocker',
        'Hydrochlorothiazide': 'Thiazide Diuretic'
    }

    for d_name, cat in category_map.items():
        drugs_dict[d_name] = cat

    # Default side effects fallback polish
    default_side_effects = {
        'Aspirin': ['Stomach irritation', 'Nausea', 'Heartburn', 'GI discomfort'],
        'Warfarin': ['Bleeding risk', 'Bruising', 'Haematoma'],
        'Ibuprofen': ['Stomach irritation', 'Nausea', 'Dizziness', 'Heartburn'],
        'Simvastatin': ['Muscle pain', 'Headache', 'Elevated liver enzymes'],
        'Clarithromycin': ['Nausea', 'Diarrhea', 'Taste alteration'],
        'Sertraline': ['Insomnia', 'Dry mouth', 'Dizziness', 'Nausea'],
        'Tramadol': ['Dizziness', 'Nausea', 'Drowsiness', 'Constipation'],
        'Clopidogrel': ['Bleeding risk', 'Bruising', 'Abdominal pain'],
        'Omeprazole': ['Headache', 'Abdominal pain', 'Flatulence'],
        'Digoxin': ['Nausea', 'Visual disturbances', 'Arrhythmia'],
        'Verapamil': ['Constipation', 'Dizziness', 'Low blood pressure'],
        'Lithium': ['Tremors', 'Increased thirst', 'Frequent urination'],
        'Codeine': ['Drowsiness', 'Constipation', 'Nausea'],
        'Ciprofloxacin': ['Nausea', 'Dizziness', 'Diarrhea', 'Tendonitis risk'],
        'Paracetamol': ['Nausea', 'Liver stress (at high chronic doses)'],
        'Metformin': ['Nausea', 'Diarrhea', 'Abdominal discomfort'],
        'Glipizide': ['Low blood sugar', 'Skin rash', 'Dizziness'],
        'Metoprolol': ['Tiredness', 'Slow heart rate', 'Dizziness'],
        'Amlodipine': ['Dizziness', 'Ankle swelling', 'Flushing'],
        'Lisinopril': ['Dry cough', 'Dizziness', 'Hyperkalemia'],
        'Penicillin': ['Nausea', 'Diarrhea', 'Hypersensitivity rash'],
        'Amoxicillin': ['Diarrhea', 'Rash', 'Nausea'],
        'Azithromycin': ['Abdominal pain', 'Nausea', 'Diarrhea'],
        'Bupropion': ['Dry mouth', 'Anxiety', 'Headache', 'Insomnia'],
        'Escitalopram': ['Nausea', 'Drowsiness', 'Sweating'],
        'Losartan': ['Back pain', 'Dizziness', 'Hyperkalemia']
    }

    for d_name, se_list in default_side_effects.items():
        if d_name not in side_effects_dict:
            side_effects_dict[d_name] = set()
        for se in se_list:
            side_effects_dict[d_name].add(se)

    # Convert to DataFrames and Save
    drugs_list = [{'drug_name': d, 'category': cat} for d, cat in sorted(drugs_dict.items())]
    drugs_df_out = pd.DataFrame(drugs_list)
    drugs_df_out.to_csv(os.path.join(data_dir, 'drugs.csv'), index=False)

    interactions_df_out = pd.DataFrame(interactions_list).drop_duplicates(subset=['drug_a', 'drug_b'])
    interactions_df_out.to_csv(os.path.join(data_dir, 'interactions.csv'), index=False)

    se_rows = []
    for d_name, se_set in sorted(side_effects_dict.items()):
        for se in sorted(se_set):
            se_rows.append({'drug_name': d_name, 'side_effect': se})
    side_effects_df_out = pd.DataFrame(se_rows)
    side_effects_df_out.to_csv(os.path.join(data_dir, 'side_effects.csv'), index=False)

    # Expanded Patients dataset
    expanded_patients = [
        {"patient_id": "P001", "name": "John Doe", "age": 68, "gender": "Male", "allergies": "Penicillin", "condition": "Atrial Fibrillation & Hypertension", "blood_group": "O+", "bp": "138/88 mmHg", "heart_rate": "74 bpm"},
        {"patient_id": "P002", "name": "Emily Watson", "age": 35, "gender": "Female", "allergies": "Penicillin", "condition": "Bacterial Infection", "blood_group": "A+", "bp": "120/80 mmHg", "heart_rate": "70 bpm"},
        {"patient_id": "P003", "name": "Robert Chen", "age": 42, "gender": "Male", "allergies": "None", "condition": "Major Depression & Chronic Pain", "blood_group": "B+", "bp": "128/82 mmHg", "heart_rate": "76 bpm"},
        {"patient_id": "P004", "name": "Maria Garcia", "age": 58, "gender": "Female", "allergies": "Aspirin", "condition": "Type 2 Diabetes & Hyperlipidemia", "blood_group": "AB+", "bp": "132/84 mmHg", "heart_rate": "72 bpm"},
        {"patient_id": "P005", "name": "David Miller", "age": 74, "gender": "Male", "allergies": "Sulfa Drugs", "condition": "Heart Failure & Osteoarthritis", "blood_group": "O-", "bp": "142/90 mmHg", "heart_rate": "68 bpm"},
        {"patient_id": "P006", "name": "Sophia Martinez", "age": 29, "gender": "Female", "allergies": "None", "condition": "Asthma & Allergic Rhinitis", "blood_group": "A-", "bp": "118/76 mmHg", "heart_rate": "72 bpm"},
        {"patient_id": "P007", "name": "James Wilson", "age": 63, "gender": "Male", "allergies": "Ibuprofen", "condition": "Coronary Artery Disease", "blood_group": "B-", "bp": "135/85 mmHg", "heart_rate": "78 bpm"},
        {"patient_id": "P008", "name": "Olivia Taylor", "age": 51, "gender": "Female", "allergies": "Codeine", "condition": "Rheumatoid Arthritis", "blood_group": "O+", "bp": "126/80 mmHg", "heart_rate": "74 bpm"},
        {"patient_id": "P009", "name": "Alexander Wright", "age": 81, "gender": "Male", "allergies": "Penicillin, Ciprofloxacin", "condition": "Chronic Kidney Disease & Gout", "blood_group": "A+", "bp": "145/92 mmHg", "heart_rate": "66 bpm"},
        {"patient_id": "P010", "name": "Emma Brown", "age": 24, "gender": "Female", "allergies": "None", "condition": "Migraine Prevention", "blood_group": "AB-", "bp": "115/74 mmHg", "heart_rate": "70 bpm"}
    ]
    patients_df_out = pd.DataFrame(expanded_patients)
    patients_df_out.to_csv(os.path.join(data_dir, 'patients.csv'), index=False)

    print(f"✅ Drugs Saved        : {len(drugs_df_out)} items -> {os.path.join(data_dir, 'drugs.csv')}")
    print(f"✅ Interactions Saved : {len(interactions_df_out)} pairs -> {os.path.join(data_dir, 'interactions.csv')}")
    print(f"✅ Side Effects Saved : {len(side_effects_df_out)} items -> {os.path.join(data_dir, 'side_effects.csv')}")
    print(f"✅ Patients Saved     : {len(patients_df_out)} records -> {os.path.join(data_dir, 'patients.csv')}")
    print("=" * 60)

if __name__ == '__main__':
    build_expanded_datasets()
