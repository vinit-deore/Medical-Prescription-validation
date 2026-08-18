import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from build_expanded_datasets import build_expanded_datasets
from validator import load_data, check_interactions, check_allergies, get_side_effects, calculate_condition_risk, calculate_rule_risk
from train_model import train_and_save_model
from ai_engine import suggest_drug_corrections, calculate_ai_risk_score, generate_ai_clinical_narrative
from auth import login_user, DEMO_USERS
from patient_manager import load_patients

def run_tests():
    print("--- 1. Testing Dataset Expansion ---")
    build_expanded_datasets()
    drugs_df, interactions_df, side_effects_df = load_data()
    patients_df = load_patients()

    print(f"Drugs Count        : {len(drugs_df)}")
    print(f"Interactions Count : {len(interactions_df)}")
    print(f"Side Effects Count : {len(side_effects_df)}")
    print(f"Patients Count     : {len(patients_df)}")

    assert len(drugs_df) >= 30
    assert len(interactions_df) >= 10
    assert len(patients_df) >= 5

    print("\n--- 2. Testing AI Typo Assistant ---")
    match, score = suggest_drug_corrections("warferin", drugs_df['drug_name'].tolist())
    print(f"Typo 'warferin' -> Match: {match} (Confidence: {score}%)")
    assert match == "Warfarin"

    print("\n--- 3. Testing Model Training ---")
    clf = train_and_save_model()
    assert clf is not None

    print("\n✅ ALL EXPANDED GLASSMORPHISM TESTS PASSED SUCCESSFULLY!")

if __name__ == '__main__':
    run_tests()
