import os
import pandas as pd

def find_column(df, candidates):
    """Utility to flexibly match column names regardless of capitalization or slight variations."""
    cols_lower = {col.lower().strip().replace(" ", "_"): col for col in df.columns}
    for cand in candidates:
        cand_clean = cand.lower().strip().replace(" ", "_")
        if cand_clean in cols_lower:
            return cols_lower[cand_clean]
    return None

def load_data(data_dir=None):
    """
    Loads drugs.csv, interactions.csv, and side_effects.csv.
    Adapts gracefully to different column names or missing files.
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

    if os.path.exists(drugs_path):
        drugs_df = pd.read_csv(drugs_path)
    if os.path.exists(interactions_path):
        interactions_df = pd.read_csv(interactions_path)
    if os.path.exists(side_effects_path):
        side_effects_df = pd.read_csv(side_effects_path)

    return drugs_df, interactions_df, side_effects_df

def check_interactions(medicines, interactions_df=None):
    """
    Compares every pair of medicines in the prescription against interactions.csv.
    Returns a tuple: (found_interactions, pairs_without_interaction)
    """
    if interactions_df is None or interactions_df.empty:
        return [], []

    # Identify relevant columns adaptively
    col_a = find_column(interactions_df, ['drug_a', 'drug1', 'drug_1', 'drug_a_name'])
    col_b = find_column(interactions_df, ['drug_b', 'drug2', 'drug_2', 'drug_b_name'])
    col_sev = find_column(interactions_df, ['severity', 'risk_level', 'level'])
    col_eff = find_column(interactions_df, ['effect', 'mechanism', 'description', 'side_effect'])
    col_alt = find_column(interactions_df, ['safer_alternative', 'alternative', 'safer_alt'])
    col_rat = find_column(interactions_df, ['rationale', 'reason', 'explanation'])

    if not col_a or not col_b:
        return [], []

    # Standardize dataframe for fast comparison
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

            # Bidirectional matching
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

                    # Normalize severity labels
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
    """
    Checks if any prescribed medicine matches the patient's recorded allergies.
    Returns a list of allergy warnings with HIGH severity.
    """
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
    """
    Retrieves recorded side effects for each medicine in the prescription.
    Returns a dict: {medicine_name: [list_of_side_effects]}
    """
    results = {}
    clean_meds = [m.strip() for m in medicines if m and m.strip()]
    for m in clean_meds:
        results[m] = []

    if side_effects_df is None or side_effects_df.empty:
        return results

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
    """
    Evaluates patient medical condition for clinical risk factors.
    Returns a score from 0 (Normal) to 3 (Severe underlying risk).
    """
    if not medical_condition or not isinstance(medical_condition, str):
        return 0

    cond_lower = medical_condition.lower()
    score = 0

    # High-risk systemic conditions
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
    """
    Calculate rule-based risk level:
    - IF allergy conflict exists -> HIGH
    - ELSE IF HIGH/MAJOR interaction exists -> HIGH
    - ELSE IF MODERATE interaction exists -> MODERATE
    - ELSE -> LOW
    """
    if allergy_conflicts:
        return 'HIGH'

    has_high = any(item['severity'] == 'HIGH' for item in interaction_results)
    if has_high:
        return 'HIGH'

    has_mod = any(item['severity'] == 'MODERATE' for item in interaction_results)
    if has_mod:
        return 'MODERATE'

    return 'LOW'
