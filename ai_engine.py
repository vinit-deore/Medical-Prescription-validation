import os
import json
import urllib.request
import urllib.error
import difflib

def suggest_drug_corrections(input_name, known_drugs_list, cutoff=0.6):
    """
    Uses AI/NLP fuzzy string matching to detect typos and suggest exact drug matches.
    Returns (best_match, match_confidence_percentage).
    """
    if not input_name or not known_drugs_list:
        return input_name, 0.0

    clean_input = input_name.strip()
    clean_drugs = [d.strip() for d in known_drugs_list if d and d.strip()]

    # Exact match check
    for d in clean_drugs:
        if d.lower() == clean_input.lower():
            return d, 100.0

    # Fuzzy match using difflib SequenceMatcher
    matches = difflib.get_close_matches(clean_input, clean_drugs, n=1, cutoff=cutoff)
    if matches:
        best_match = matches[0]
        ratio = difflib.SequenceMatcher(None, clean_input.lower(), best_match.lower()).ratio()
        return best_match, round(ratio * 100, 1)

    return clean_input, 0.0

def calculate_ai_risk_score(ml_probs, interaction_results, allergy_conflicts, patient_age, condition_risk):
    """
    Computes a unified AI Risk Score Index from 0 to 100 based on hybrid model features.
    """
    score = 0.0

    # 1. ML Probability contribution (up to 35 points)
    if len(ml_probs) >= 3:
        score += ml_probs[1] * 15.0  # Moderate prob
        score += ml_probs[2] * 35.0  # High prob

    # 2. Interaction severity contribution (up to 40 points)
    has_high_inter = any(i['severity'] == 'HIGH' for i in interaction_results)
    has_mod_inter = any(i['severity'] == 'MODERATE' for i in interaction_results)
    
    if has_high_inter:
        score += 40.0
    elif has_mod_inter:
        score += 22.0
    elif interaction_results:
        score += 10.0

    # 3. Allergy Conflict (up to 15 points)
    if allergy_conflicts:
        score += 15.0

    # 4. Patient Age & Condition Risk (up to 10 points)
    if patient_age >= 65:
        score += 5.0
    if condition_risk >= 2:
        score += 5.0

    final_score = min(int(round(score)), 100)

    if final_score >= 70:
        category = "CRITICAL / HIGH RISK"
    elif final_score >= 40:
        category = "MODERATE RISK"
    else:
        category = "LOW RISK"

    return final_score, category

def query_free_gemini_api(api_key, prompt):
    """
    Queries Google Gemini 1.5 Flash free API endpoint using standard HTTP request.
    """
    if not api_key:
        return None

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key.strip()}"
    headers = {'Content-Type': 'application/json'}
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }

    try:
        req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers=headers, method='POST')
        with urllib.request.urlopen(req, timeout=8) as response:
            res_data = json.loads(response.read().decode('utf-8'))
            candidates = res_data.get('candidates', [])
            if candidates:
                parts = candidates[0].get('content', {}).get('parts', [])
                if parts:
                    return parts[0].get('text', '').strip()
    except Exception as e:
        return f"(Free Gemini API Notice: {e})"

    return None

def generate_ai_clinical_narrative(patient_age, gender, condition, medicines, interactions, allergies, final_risk, gemini_key=None):
    """
    Generates a natural language AI Clinical Reasoning Report.
    Tries free online Gemini API if key is present; falls back smoothly to local intelligent AI reasoning synthesis.
    """
    prompt = f"""
Act as a Clinical Pharmacologist AI. Analyze the following prescription case:
- Patient: {patient_age} year old {gender}
- Condition: {condition}
- Prescribed Drugs: {', '.join(medicines)}
- Recorded Allergies: {allergies}
- Calculated Risk Level: {final_risk}
- Interactions Found: {json.dumps(interactions)}

Provide a concise 3-bullet clinical summary:
1. Primary Pharmacological Mechanism & Interactions
2. Patient-Specific Vulnerabilities (Age, Condition, Allergies)
3. Actionable Clinical Guidance & Monitoring
"""

    # Try Free Online AI (Gemini) if key provided
    if gemini_key and gemini_key.strip():
        online_response = query_free_gemini_api(gemini_key, prompt)
        if online_response and not online_response.startswith("(Free Gemini API Notice"):
            return f"**[Online Gemini AI Response]**\n\n{online_response}"

    # Local Intelligent AI Reasoning Engine (Zero-cost, works 100% offline)
    narrative_parts = []

    # Bullet 1: Interaction & Mechanism
    if interactions:
        inter_descriptions = []
        for item in interactions:
            alt_info = f" (Safer Alternative: {item.get('safer_alternative', 'N/A')})" if item.get('safer_alternative') else ""
            inter_descriptions.append(f"**{item['drug_a']} + {item['drug_b']}** [{item['severity']} Severity]: {item['effect']}{alt_info}")
        narrative_parts.append(f"**1. Pharmacological Mechanism & Interactions:**\n" + "\n".join([f"  • {desc}" for desc in inter_descriptions]))
    else:
        narrative_parts.append("**1. Pharmacological Mechanism:** No high-risk drug-drug interaction pair recorded in current dataset.")

    # Bullet 2: Patient-Specific Vulnerabilities
    vulnerabilities = []
    if patient_age >= 65:
        vulnerabilities.append(f"Elderly patient ({patient_age}y) has reduced metabolic clearance; monitor for heightened sensitivity.")
    if allergies and allergies.lower() != "none":
        vulnerabilities.append(f"Recorded patient allergies ({allergies}) require strict drug class cross-reactivity verification.")
    if condition:
        vulnerabilities.append(f"Underlying condition ({condition}) requires caution regarding drug contraindications.")
    if not vulnerabilities:
        vulnerabilities.append("Standard adult patient parameters with no high-risk systemic vulnerability flagged.")
    
    narrative_parts.append(f"**2. Patient-Specific Vulnerabilities:**\n" + "\n".join([f"  • {v}" for v in vulnerabilities]))

    # Bullet 3: Actionable Clinical Guidance
    guidance = []
    if final_risk in ["HIGH", "CRITICAL / HIGH RISK"]:
        guidance.append("Hold or re-evaluate high-risk combinations prior to dispensing.")
        guidance.append("Consult attending physician regarding recommended safer alternatives.")
        guidance.append("Monitor vital signs and organ function parameters closely.")
    elif final_risk == "MODERATE RISK":
        guidance.append("Proceed with caution. Space dosing times where applicable.")
        guidance.append("Educate patient on early warning side effects.")
    else:
        guidance.append("Prescription parameters within safe baseline in supplied dataset. Clinical review remains mandatory.")

    narrative_parts.append(f"**3. Actionable Clinical Guidance:**\n" + "\n".join([f"  • {g}" for g in guidance]))

    return "\n\n".join(narrative_parts)
