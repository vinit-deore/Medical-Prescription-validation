import os
import pandas as pd

def find_column(df, candidates):
    """Utility to flexibly match column names regardless of capitalization or slight variations."""
    if df is None or df.empty:
        return None
    cols_lower = {col.lower().strip().replace(" ", "_"): col for col in df.columns}
    for cand in candidates:
        cand_clean = cand.lower().strip().replace(" ", "_")
        if cand_clean in cols_lower:
            return cols_lower[cand_clean]
    return None

def get_default_drugs_df():
    data = [
        {"drug_name": "Warfarin", "category": "Anticoagulant"},
        {"drug_name": "Aspirin", "category": "Antiplatelet / Analgesic"},
        {"drug_name": "Ibuprofen", "category": "NSAID Analgesic"},
        {"drug_name": "Simvastatin", "category": "Statin / Lipid Lowering"},
        {"drug_name": "Clarithromycin", "category": "Macrolide Antibiotic"},
        {"drug_name": "Sertraline", "category": "SSRI Antidepressant"},
        {"drug_name": "Tramadol", "category": "Opioid Analgesic"},
        {"drug_name": "Clopidogrel", "category": "Antiplatelet Agent"},
        {"drug_name": "Omeprazole", "category": "Proton Pump Inhibitor"},
        {"drug_name": "Digoxin", "category": "Cardiac Glycoside"},
        {"drug_name": "Verapamil", "category": "Calcium Channel Blocker"},
        {"drug_name": "Lithium", "category": "Mood Stabilizer"},
        {"drug_name": "Codeine", "category": "Opioid Analgesic"},
        {"drug_name": "Paroxetine", "category": "SSRI Antidepressant"},
        {"drug_name": "Theophylline", "category": "Bronchodilator"},
        {"drug_name": "Ciprofloxacin", "category": "Fluoroquinolone Antibiotic"},
        {"drug_name": "Rifampin", "category": "Rifamycin Antibiotic"},
        {"drug_name": "Sildenafil", "category": "PDE5 Inhibitor"},
        {"drug_name": "Nitroglycerin", "category": "Nitrate Vasodilator"},
        {"drug_name": "Valproic Acid", "category": "Anticonvulsant"},
        {"drug_name": "Lamotrigine", "category": "Anticonvulsant"},
        {"drug_name": "Fluconazole", "category": "Antifungal"},
        {"drug_name": "Metformin", "category": "Biguanide Antidiabetic"},
        {"drug_name": "Glipizide", "category": "Sulfonylurea Antidiabetic"},
        {"drug_name": "Metoprolol", "category": "Beta-1 Blocker"},
        {"drug_name": "Amlodipine", "category": "Calcium Channel Blocker"},
        {"drug_name": "Lisinopril", "category": "ACE Inhibitor"},
        {"drug_name": "Paracetamol", "category": "Analgesic / Antipyretic"},
        {"drug_name": "Penicillin", "category": "Beta-Lactam Antibiotic"},
        {"drug_name": "Amoxicillin", "category": "Aminopenicillin Antibiotic"},
        {"drug_name": "Azithromycin", "category": "Macrolide Antibiotic"},
        {"drug_name": "Bupropion", "category": "NDRI Antidepressant"},
        {"drug_name": "Escitalopram", "category": "SSRI Antidepressant"},
        {"drug_name": "Insulin Glargine", "category": "Long-Acting Insulin"},
        {"drug_name": "Losartan", "category": "Angiotensin II Receptor Blocker"},
        {"drug_name": "Hydrochlorothiazide", "category": "Thiazide Diuretic"}
    ]
    return pd.DataFrame(data)

def get_default_interactions_df():
    data = [
        {"drug_a": "Warfarin", "drug_b": "Aspirin", "severity": "High", "effect": "Increased bleeding risk", "safer_alternative": "Acetaminophen (Paracetamol)", "rationale": "No antiplatelet effect; safer for bleeding risk."},
        {"drug_a": "Warfarin", "drug_b": "Ibuprofen", "severity": "High", "effect": "Increased bleeding risk (GI irritation)", "safer_alternative": "Acetaminophen (Paracetamol)", "rationale": "No antiplatelet effect; safer for bleeding risk."},
        {"drug_a": "Simvastatin", "drug_b": "Clarithromycin", "severity": "High", "effect": "Risk of severe muscle toxicity (rhabdomyolysis)", "safer_alternative": "Azithromycin or Amoxicillin", "rationale": "Weaker CYP3A4 inhibition; different antibiotic class."},
        {"drug_a": "Sertraline", "drug_b": "Tramadol", "severity": "High", "effect": "Increased risk of serotonin syndrome", "safer_alternative": "Morphine or Oxycodone (with caution)", "rationale": "Lower serotonergic activity."},
        {"drug_a": "Clopidogrel", "drug_b": "Omeprazole", "severity": "High", "effect": "Reduced antiplatelet effect and increased thrombosis risk", "safer_alternative": "Pantoprazole or Famotidine", "rationale": "Less potent CYP2C19 inhibition."},
        {"drug_a": "Digoxin", "drug_b": "Verapamil", "severity": "High", "effect": "Increased risk of digoxin toxicity", "safer_alternative": "Amlodipine", "rationale": "No significant effect on P-gp."},
        {"drug_a": "Lithium", "drug_b": "Ibuprofen", "severity": "High", "effect": "Increased risk of lithium toxicity", "safer_alternative": "Acetaminophen (Paracetamol)", "rationale": "Does not affect lithium clearance."},
        {"drug_a": "Codeine", "drug_b": "Paroxetine", "severity": "High", "effect": "Lack of analgesic efficacy due to metabolic block", "safer_alternative": "Morphine", "rationale": "Bypasses metabolic conversion."},
        {"drug_a": "Ciprofloxacin", "drug_b": "Theophylline", "severity": "High", "effect": "Increased risk of theophylline toxicity", "safer_alternative": "Levofloxacin or Cefuroxime", "rationale": "Lower interaction potential."},
        {"drug_a": "Sildenafil", "drug_b": "Nitroglycerin", "severity": "High", "effect": "Severe hypotension and syncope risk", "safer_alternative": "Alternative angina treatment", "rationale": "Contraindicated combination."},
        {"drug_a": "Valproic Acid", "drug_b": "Lamotrigine", "severity": "High", "effect": "Increased risk of serious rash (Stevens-Johnson syndrome)", "safer_alternative": "Slow lamotrigine titration", "rationale": "Requires very slow dose escalation."},
        {"drug_a": "Warfarin", "drug_b": "Fluconazole", "severity": "High", "effect": "Increased bleeding risk due to CYP2C9 inhibition", "safer_alternative": "Terbinafine", "rationale": "Does not significantly inhibit CYP2C9."},
        {"drug_a": "Lisinopril", "drug_b": "Hydrochlorothiazide", "severity": "Low", "effect": "Enhanced blood pressure reduction (monitored combination)", "safer_alternative": "None needed", "rationale": "Standard synergistic combination."},
        {"drug_a": "Ciprofloxacin", "drug_b": "Metformin", "severity": "Moderate", "effect": "Altered blood glucose levels", "safer_alternative": "Amoxicillin", "rationale": "Does not interfere with glycemic control."},
        {"drug_a": "Paracetamol", "drug_b": "Warfarin", "severity": "Moderate", "effect": "Increased bleeding risk with high chronic paracetamol doses", "safer_alternative": "Limit paracetamol to <2g/day", "rationale": "Low doses have minimal interaction."},
        {"drug_a": "Ibuprofen", "drug_b": "Aspirin", "severity": "Moderate", "effect": "Reduced antiplatelet effect of aspirin", "safer_alternative": "Take aspirin 30 mins before ibuprofen", "rationale": "Separating dose times minimizes interaction."},
        {"drug_a": "Metoprolol", "drug_b": "Fluoxetine", "severity": "Moderate", "effect": "Increased metoprolol concentration causing slow heart rate", "safer_alternative": "Atenolol", "rationale": "Less dependent on CYP2D6 metabolism."},
        {"drug_a": "Amlodipine", "drug_b": "Simvastatin", "severity": "Moderate", "effect": "Increased statin exposure and risk of muscle soreness", "safer_alternative": "Pravastatin or Rosuvastatin", "rationale": "Lower interaction potential with calcium channel blockers."},
        {"drug_a": "Lisinopril", "drug_b": "Ibuprofen", "severity": "Moderate", "effect": "Decreased blood pressure control and potential kidney stress", "safer_alternative": "Paracetamol", "rationale": "Does not inhibit renal prostaglandins."},
        {"drug_a": "Metformin", "drug_b": "Contrast Dye", "severity": "High", "effect": "Increased risk of lactic acidosis", "safer_alternative": "Temporarily withhold metformin", "rationale": "Prevents renal contrast interaction."},
        {"drug_a": "Azithromycin", "drug_b": "Amiodarone", "severity": "High", "effect": "Increased risk of irregular heart rhythm", "safer_alternative": "Amoxicillin", "rationale": "No QT prolongation effect."}
    ]
    return pd.DataFrame(data)

def get_default_side_effects_df():
    data = [
        {"drug_name": "Aspirin", "side_effect": "Stomach irritation"},
        {"drug_name": "Aspirin", "side_effect": "Nausea"},
        {"drug_name": "Aspirin", "side_effect": "Heartburn"},
        {"drug_name": "Warfarin", "side_effect": "Bleeding risk"},
        {"drug_name": "Warfarin", "side_effect": "Bruising"},
        {"drug_name": "Ibuprofen", "side_effect": "Stomach irritation"},
        {"drug_name": "Ibuprofen", "side_effect": "Nausea"},
        {"drug_name": "Ibuprofen", "side_effect": "Dizziness"},
        {"drug_name": "Simvastatin", "side_effect": "Muscle pain"},
        {"drug_name": "Simvastatin", "side_effect": "Headache"},
        {"drug_name": "Clarithromycin", "side_effect": "Nausea"},
        {"drug_name": "Clarithromycin", "side_effect": "Diarrhea"},
        {"drug_name": "Sertraline", "side_effect": "Insomnia"},
        {"drug_name": "Sertraline", "side_effect": "Dry mouth"},
        {"drug_name": "Sertraline", "side_effect": "Dizziness"},
        {"drug_name": "Tramadol", "side_effect": "Dizziness"},
        {"drug_name": "Tramadol", "side_effect": "Nausea"},
        {"drug_name": "Tramadol", "side_effect": "Drowsiness"},
        {"drug_name": "Clopidogrel", "side_effect": "Bleeding risk"},
        {"drug_name": "Omeprazole", "side_effect": "Headache"},
        {"drug_name": "Digoxin", "side_effect": "Nausea"},
        {"drug_name": "Verapamil", "side_effect": "Constipation"},
        {"drug_name": "Lithium", "side_effect": "Tremors"},
        {"drug_name": "Codeine", "side_effect": "Drowsiness"},
        {"drug_name": "Ciprofloxacin", "side_effect": "Nausea"},
        {"drug_name": "Ciprofloxacin", "side_effect": "Dizziness"},
        {"drug_name": "Paracetamol", "side_effect": "Nausea"},
        {"drug_name": "Metformin", "side_effect": "Nausea"},
        {"drug_name": "Metformin", "side_effect": "Diarrhea"},
        {"drug_name": "Glipizide", "side_effect": "Low blood sugar"},
        {"drug_name": "Metoprolol", "side_effect": "Tiredness"},
        {"drug_name": "Amlodipine", "side_effect": "Dizziness"},
        {"drug_name": "Lisinopril", "side_effect": "Dry cough"},
        {"drug_name": "Penicillin", "side_effect": "Nausea"},
        {"drug_name": "Amoxicillin", "side_effect": "Diarrhea"},
        {"drug_name": "Azithromycin", "side_effect": "Abdominal pain"},
        {"drug_name": "Bupropion", "side_effect": "Dry mouth"},
        {"drug_name": "Escitalopram", "side_effect": "Nausea"},
        {"drug_name": "Losartan", "side_effect": "Back pain"}
    ]
    return pd.DataFrame(data)

def load_data(data_dir=None):
    """
    Loads drugs.csv, interactions.csv, and side_effects.csv.
    Safely handles empty CSV files, missing files, or parse errors by using fallbacks.
    """
    if data_dir is None:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        data_dir = os.path.join(base_dir, 'data')

    drugs_path = os.path.join(data_dir, 'drugs.csv')
    interactions_path = os.path.join(data_dir, 'interactions.csv')
    side_effects_path = os.path.join(data_dir, 'side_effects.csv')

    drugs_df = pd.DataFrame()
    interactions_df = pd.DataFrame()
    side_effects_df = pd.DataFrame()

    # Load drugs_df
    if os.path.exists(drugs_path) and os.path.getsize(drugs_path) > 0:
        try:
            drugs_df = pd.read_csv(drugs_path)
        except Exception:
            drugs_df = get_default_drugs_df()
    else:
        drugs_df = get_default_drugs_df()

    # Load interactions_df
    if os.path.exists(interactions_path) and os.path.getsize(interactions_path) > 0:
        try:
            interactions_df = pd.read_csv(interactions_path)
        except Exception:
            interactions_df = get_default_interactions_df()
    else:
        interactions_df = get_default_interactions_df()

    # Load side_effects_df
    if os.path.exists(side_effects_path) and os.path.getsize(side_effects_path) > 0:
        try:
            side_effects_df = pd.read_csv(side_effects_path)
        except Exception:
            side_effects_df = get_default_side_effects_df()
    else:
        side_effects_df = get_default_side_effects_df()

    if drugs_df.empty:
        drugs_df = get_default_drugs_df()
    if interactions_df.empty:
        interactions_df = get_default_interactions_df()
    if side_effects_df.empty:
        side_effects_df = get_default_side_effects_df()

    return drugs_df, interactions_df, side_effects_df

def check_interactions(medicines, interactions_df=None):
    """
    Compares every pair of medicines in the prescription against interactions.csv.
    Returns a tuple: (found_interactions, pairs_without_interaction)
    """
    if interactions_df is None or interactions_df.empty:
        interactions_df = get_default_interactions_df()

    col_a = find_column(interactions_df, ['drug_a', 'drug1', 'drug_1', 'drug_a_name'])
    col_b = find_column(interactions_df, ['drug_b', 'drug2', 'drug_2', 'drug_b_name'])
    col_sev = find_column(interactions_df, ['severity', 'risk_level', 'level'])
    col_eff = find_column(interactions_df, ['effect', 'mechanism', 'description', 'side_effect'])
    col_alt = find_column(interactions_df, ['safer_alternative', 'alternative', 'safer_alt'])
    col_rat = find_column(interactions_df, ['rationale', 'reason', 'explanation'])

    if not col_a or not col_b:
        return [], []

    df_clean = interactions_df.copy()
    df_clean['drug_a_clean'] = df_clean[col_a].astype(str).str.strip().str.lower()
    df_clean['drug_b_clean'] = df_clean[col_b].astype(str).str.strip().str.lower()

    found_interactions = []
    pairs_without_interaction = []

    clean_meds = [m.strip() for m in medicines if m and m.strip()]
    num_meds = len(clean_meds)

    for i in range(num_meds):
        for j in range(i + 1, num_meds):
            m1 = clean_meds[i].lower()
            m2 = clean_meds[j].lower()

            match = df_clean[
                ((df_clean['drug_a_clean'] == m1) & (df_clean['drug_b_clean'] == m2)) |
                ((df_clean['drug_a_clean'] == m2) & (df_clean['drug_b_clean'] == m1))
            ]

            if not match.empty:
                for _, row in match.iterrows():
                    sev_val = str(row[col_sev]).strip() if col_sev and pd.notna(row[col_sev]) else "UNKNOWN"
                    eff_val = str(row[col_eff]).strip() if col_eff and pd.notna(row[col_eff]) else "Known interaction recorded."
                    alt_val = str(row[col_alt]).strip() if col_alt and pd.notna(row[col_alt]) else "Clinical consultation required."
                    rat_val = str(row[col_rat]).strip() if col_rat and pd.notna(row[col_rat]) else "Monitor patient response closely."

                    sev_upper = sev_val.upper()
                    if 'HIGH' in sev_upper or 'MAJOR' in sev_upper:
                        norm_sev = 'HIGH'
                    elif 'MODERATE' in sev_upper or 'MEDIUM' in sev_upper:
                        norm_sev = 'MODERATE'
                    elif 'LOW' in sev_upper or 'MINOR' in sev_upper:
                        norm_sev = 'LOW'
                    else:
                        norm_sev = 'UNKNOWN'

                    found_interactions.append({
                        'drug_a': clean_meds[i],
                        'drug_b': clean_meds[j],
                        'severity': norm_sev,
                        'raw_severity': sev_val,
                        'effect': eff_val,
                        'safer_alternative': alt_val,
                        'rationale': rat_val
                    })
            else:
                pairs_without_interaction.append((clean_meds[i], clean_meds[j]))

    return found_interactions, pairs_without_interaction

def check_allergies(medicines, patient_allergies):
    conflicts = []
    if not patient_allergies:
        return conflicts

    if isinstance(patient_allergies, str):
        allergies_list = [a.strip().lower() for a in patient_allergies.replace(";", ",").split(",") if a.strip()]
    else:
        allergies_list = [str(a).strip().lower() for a in patient_allergies if str(a).strip()]

    for med in medicines:
        med_clean = med.strip().lower()
        if not med_clean:
            continue
        for allergy in allergies_list:
            if allergy in med_clean or med_clean in allergy:
                conflicts.append({
                    'medicine': med.strip(),
                    'allergy': allergy.title(),
                    'severity': 'HIGH',
                    'message': f"Warning: Patient has a recorded allergy to {allergy.title()} matching prescribed drug '{med.strip()}'."
                })
                break

    return conflicts

def get_side_effects(medicines, side_effects_df=None):
    results = {}
    clean_meds = [m.strip() for m in medicines if m and m.strip()]
    for m in clean_meds:
        results[m] = []

    if side_effects_df is None or side_effects_df.empty:
        side_effects_df = get_default_side_effects_df()

    col_drug = find_column(side_effects_df, ['drug_name', 'drug', 'drugname', 'pt'])
    col_se = find_column(side_effects_df, ['side_effect', 'pt', 'side_effects', 'effect'])

    if not col_drug or not col_se:
        return results

    df_clean = side_effects_df.copy()
    df_clean['drug_clean'] = df_clean[col_drug].astype(str).str.strip().str.lower()

    for m in clean_meds:
        m_clean = m.lower()
        match = df_clean[df_clean['drug_clean'] == m_clean]
        if not match.empty:
            effects = match[col_se].dropna().astype(str).str.strip().unique().tolist()
            results[m] = effects

    return results

def calculate_condition_risk(medical_condition):
    if not medical_condition or not isinstance(medical_condition, str):
        return 0

    cond_lower = medical_condition.lower()
    score = 0

    high_risk_keywords = ['renal', 'kidney', 'liver', 'hepatic', 'heart failure', 'arrhythmia', 'pregnancy', 'stroke']
    moderate_risk_keywords = ['hypertension', 'diabetes', 'asthma', 'copd', 'depression', 'atrial fibrillation']

    for kw in high_risk_keywords:
        if kw in cond_lower:
            score += 2
            break

    for kw in moderate_risk_keywords:
        if kw in cond_lower:
            score += 1
            break

    return min(score, 3)

def calculate_rule_risk(interaction_results, allergy_conflicts):
    if allergy_conflicts:
        return 'HIGH'

    has_high = any(item['severity'] == 'HIGH' for item in interaction_results)
    if has_high:
        return 'HIGH'

    has_mod = any(item['severity'] == 'MODERATE' for item in interaction_results)
    if has_mod:
        return 'MODERATE'

    return 'LOW'
