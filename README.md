# Centralized Healthcare System (CHS) — Prescription Validation Engine

A beginner-friendly, hackathon/college prototype module built for the **Centralized Healthcare System (CHS)**. This engine automatically validates prescriptions by combining rule-based clinical checks (drug-drug interactions and allergy conflicts) with a machine learning model (RandomForestClassifier) to predict overall prescription risk.

---

## 🚀 1. Project Objective

The primary objective of this module is to assist healthcare workflows by identifying potential drug interaction risks, patient allergy conflicts, and side effects before dispensing medicines. It provides an automated double-check for prescriptions while ensuring safety rules always override ML predictions.

---

## ✨ 2. Key Features

- **Patient Context Integration:** Inputs patient age, gender, allergies, and medical conditions.
- **Dynamic Prescription Builder:** Add multiple medicines with custom dosages.
- **Rule-Based Interaction Checker:** Pairwise check across all prescribed drugs to identify HIGH, MODERATE, or LOW severity interactions.
- **Patient Allergy Alerting:** Flags prescribed drugs matching recorded patient allergies with a HIGH warning.
- **Side Effect Mapping:** Displays known side effects for all prescribed drugs.
- **Machine Learning Risk Prediction:** Uses a `RandomForestClassifier` trained on patient age, medicine count, interaction severity, and allergy conflicts to predict risk levels (`LOW`, `MODERATE`, `HIGH`).
- **Safety Rule Hierarchy:** Known high-risk interactions or allergy conflicts **always** trigger a `HIGH` final risk level and cannot be overridden by ML predictions.
- **Interactive Streamlit Web Dashboard:** Clean, intuitive color-coded UI (Green = LOW, Yellow = MODERATE, Red = HIGH).

---

## 📊 3. Dataset Format

The dataset files reside in `prescription_validator/data/`:

### 1. `drugs.csv`
Contains drug names and their therapeutic categories.
```csv
drug_name,category
Warfarin,Anticoagulant
Aspirin,Antiplatelet / Analgesic
Ibuprofen,NSAID
```

### 2. `interactions.csv`
Contains pairwise drug interaction rules with severity and clinical effect.
```csv
drug_a,drug_b,severity,effect
Warfarin,Aspirin,High,Increased bleeding risk
Simvastatin,Clarithromycin,High,Risk of severe muscle toxicity (rhabdomyolysis)
```

### 3. `side_effects.csv`
Contains drug side effect mappings.
```csv
drug_name,side_effect
Aspirin,Stomach irritation
Aspirin,Nausea
```

---

## 🛠️ 4. Installation

Ensure Python 3.8+ is installed on your system. Install the required dependencies:

```bash
cd prescription_validator
pip install -r requirements.txt
```

---

## 🤖 5. How to Train the Model

To train the Random Forest risk prediction model and save `model/prescription_risk_model.pkl`, run:

```bash
python train_model.py
```

**Outputs:**
- Model file: `model/prescription_risk_model.pkl`
- Evaluation metrics: Accuracy, Precision, Recall, F1 Score, and Confusion Matrix.

*(Note: The Streamlit app will automatically train the model on launch if `prescription_risk_model.pkl` is missing.)*

---

## 🖥️ 6. How to Run the Application

Launch the Streamlit dashboard:

```bash
streamlit run app.py
```

The application will open automatically in your browser (default: `http://localhost:8501`).

---

## 🧪 7. Example Prescriptions for Testing

### Scenario A: High Risk (Drug Interaction + Allergy)
- **Patient Age:** 62
- **Allergies:** Penicillin
- **Prescription:**
  1. `Warfarin` (5 mg)
  2. `Aspirin` (100 mg)
- **Expected Result:**
  - **Risk Level:** `🚨 HIGH RISK`
  - **Drug Interaction:** Warfarin + Aspirin (Severity: HIGH, Increased bleeding risk)
  - **Allergy Check:** Warning if Penicillin is prescribed.

### Scenario B: Moderate Risk
- **Patient Age:** 45
- **Allergies:** None
- **Prescription:**
  1. `Ciprofloxacin` (500 mg)
  2. `Metformin` (850 mg)
- **Expected Result:**
  - **Risk Level:** `⚠️ MODERATE RISK`
  - **Drug Interaction:** Ciprofloxacin + Metformin (Severity: MODERATE, Altered blood glucose levels)

### Scenario C: Low Risk / Safe Combination
- **Patient Age:** 30
- **Allergies:** None
- **Prescription:**
  1. `Paracetamol` (500 mg)
  2. `Amoxicillin` (500 mg)
- **Expected Result:**
  - **Risk Level:** `✅ LOW RISK`
  - **Interaction Check:** "No known interaction found in the supplied dataset."

---

## ⚠️ 8. Limitations & Medical Disclaimer

1. **Academic/Prototype Scope:** Built for college presentations, hackathons, and prototype demonstrations.
2. **Dataset Coverage:** Interaction checks rely on `interactions.csv`. Unrecorded combinations output *"No known interaction found in the supplied dataset"* rather than guaranteeing complete medical safety.
3. **Clinical Validation:** The ML model is trained on synthetic statistical distributions for risk scoring and is **not** approved for real clinical diagnostic use. Clinical review by a healthcare professional is mandatory before dispensing any prescription.
