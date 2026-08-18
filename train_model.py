import os
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
import joblib

from build_expanded_datasets import build_expanded_datasets

def generate_enhanced_synthetic_data(num_samples=2000, seed=42):
    """
    Generates realistic clinical synthetic data for training the prescription risk model.
    """
    np.random.seed(seed)

    ages = np.random.randint(18, 90, size=num_samples)
    is_elderly = (ages >= 65).astype(int)
    num_meds = np.random.randint(1, 8, size=num_samples)

    total_interactions = np.zeros(num_samples, dtype=int)
    for i in range(num_samples):
        if num_meds[i] > 1:
            total_interactions[i] = np.random.choice([0, 1, 2, 3, 4], p=[0.35, 0.35, 0.20, 0.07, 0.03])

    has_allergy = np.random.choice([0, 1], size=num_samples, p=[0.85, 0.15])

    max_severity = np.zeros(num_samples, dtype=int)
    for i in range(num_samples):
        if total_interactions[i] > 0:
            max_severity[i] = np.random.choice([1, 2, 3], p=[0.2, 0.5, 0.3])

    total_side_effects = np.clip(
        num_meds * np.random.randint(1, 3, size=num_samples) + np.random.randint(0, 3, size=num_samples),
        0, 15
    )

    condition_risk = np.random.choice([0, 1, 2, 3], size=num_samples, p=[0.4, 0.35, 0.18, 0.07])

    targets = np.zeros(num_samples, dtype=int)
    for i in range(num_samples):
        if has_allergy[i] == 1 or max_severity[i] == 3 or (total_interactions[i] >= 2 and max_severity[i] >= 2):
            targets[i] = 2  # High Risk
        elif max_severity[i] == 2 or total_interactions[i] >= 1 or num_meds[i] >= 4 or (is_elderly[i] == 1 and num_meds[i] >= 3) or condition_risk[i] >= 2:
            targets[i] = 1  # Moderate Risk
        else:
            targets[i] = 0  # Low Risk

    df = pd.DataFrame({
        'patient_age': ages,
        'is_elderly': is_elderly,
        'num_medicines': num_meds,
        'has_allergy_conflict': has_allergy,
        'max_interaction_severity': max_severity,
        'total_interaction_count': total_interactions,
        'total_side_effects_count': total_side_effects,
        'condition_risk_factor': condition_risk,
        'risk_level': targets
    })
    return df

def train_and_save_model():
    """Builds expanded datasets and trains the Random Forest model."""
    print("=" * 65)
    print("CHS PRESCRIPTION RISK MODEL TRAINING")
    print("=" * 65)

    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, 'data')

    # Ensure datasets are expanded
    build_expanded_datasets()

    model_dir = os.path.join(base_dir, 'model')
    os.makedirs(model_dir, exist_ok=True)
    model_path = os.path.join(model_dir, 'prescription_risk_model.pkl')

    df = generate_enhanced_synthetic_data(num_samples=2000, seed=42)

    feature_cols = [
        'patient_age',
        'is_elderly',
        'num_medicines',
        'has_allergy_conflict',
        'max_interaction_severity',
        'total_interaction_count',
        'total_side_effects_count',
        'condition_risk_factor'
    ]

    X = df[feature_cols]
    y = df['risk_level']

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    clf = RandomForestClassifier(
        n_estimators=150,
        max_depth=8,
        min_samples_split=4,
        random_state=42
    )
    clf.fit(X_train, y_train)

    y_pred = clf.predict(X_test)

    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred, average='weighted')
    rec = recall_score(y_test, y_pred, average='weighted')
    f1 = f1_score(y_test, y_pred, average='weighted')
    cm = confusion_matrix(y_test, y_pred)

    print(f"Dataset Size : {len(df)} samples")
    print(f"Train Size   : {len(X_train)} samples")
    print(f"Test Size    : {len(X_test)} samples")
    print("-" * 65)
    print(f"Accuracy     : {acc * 100:.2f}%")
    print(f"Precision    : {prec:.4f}")
    print(f"Recall       : {rec:.4f}")
    print(f"F1 Score     : {f1:.4f}")
    print("-" * 65)
    print("Confusion Matrix (0=Low, 1=Moderate, 2=High):")
    print(cm)
    print("-" * 65)

    importances = clf.feature_importances_
    model_payload = {
        'model': clf,
        'feature_cols': feature_cols,
        'feature_importances': dict(zip(feature_cols, importances)),
        'risk_mapping': {0: 'LOW', 1: 'MODERATE', 2: 'HIGH'}
    }

    joblib.dump(model_payload, model_path)
    print(f"Model payload saved to: {model_path}")
    return clf

if __name__ == '__main__':
    train_and_save_model()
