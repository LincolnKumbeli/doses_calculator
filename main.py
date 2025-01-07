from flask import Flask, request, render_template, url_for, redirect

app = Flask(__name__, static_folder='static', template_folder='templates')

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        weight_str = request.form["weight"]
        calc_type = request.form.get("calc_type")
        tbsa_str = request.form.get("tbsa")

        print(f"DEBUG: Received weight: {weight_str}")
        print(f"DEBUG: Received calc_type: {calc_type}")
        print(f"DEBUG: Received tbsa: {tbsa_str}")

        try:
            weight = float(weight_str)
            tbsa = float(tbsa_str) if tbsa_str else None
            
            # Perform calculations
            doses = {}
            bolus_fluids, maintenance_rate, two_thirds_maintenance_rate = {}, None, None
            ett_info = None
            parkland_data = None

            if calc_type == "common":
                doses = calculate_common_doses(weight)
                ett_info = None
            elif calc_type == "emergency":
                doses = calculate_emergency_doses(weight)
                ett_info = None  # Remove ETT info from emergency
            elif calc_type == "RSI and ETT":
                rsi_doses, ett_info = calculate_rsi_ett_doses(weight)
                doses = {
                    "RSI and ETT Medications": rsi_doses,
                    "ETT Information": ett_info
                }
            elif calc_type == "all_drugs":
                doses = calculate_all_drugs(weight)
                print(f"DEBUG: All drugs calculated: {len(doses)} drugs")  # Debug print

            # Calculate fluids for all types
            bolus_fluids, maintenance_rate, two_thirds_maintenance_rate = calculate_fluids(weight)

            # Calculate Parkland formula if TBSA provided
            if tbsa and calc_type == "emergency":
                parkland_total_volume, parkland_first_8_hours, parkland_first_8_hours_rate, parkland_next_16_hours, parkland_next_16_hours_rate = calculate_parkland_formula(weight, tbsa)
                parkland_data = {
                    'total_volume': parkland_total_volume,
                    'first_8_hours': parkland_first_8_hours,
                    'first_8_hours_rate': parkland_first_8_hours_rate,
                    'next_16_hours': parkland_next_16_hours,
                    'next_16_hours_rate': parkland_next_16_hours_rate
                }

            print(f"DEBUG: Calculated doses: {doses}")
            print(f"DEBUG: Maintenance rate: {maintenance_rate}")

            return render_template(
                "index.html",
                weight=weight,
                calc_type=calc_type,
                doses=doses,
                bolus_fluids=bolus_fluids,
                maintenance_rate=maintenance_rate,
                two_thirds_maintenance_rate=two_thirds_maintenance_rate,
                ett_info=ett_info,
                tbsa=tbsa,
                parkland_data=parkland_data
            )
        except ValueError as e:
            print(f"DEBUG: Error: {e}")
            return "Invalid input. Please enter valid numbers."
        except Exception as e:
            print(f"DEBUG: Unexpected error: {e}")
            return f"An error occurred: {str(e)}"
    
    return render_template("index.html")

@app.route("/disease", methods=["GET", "POST"])
def disease():
    diseases = sorted([
        "Reactive Airways Disease",
        "Meningitis",
        "Malaria",
        "Asthma",
        "Conjunctivitis",
        "Disease 4",
        "Disease 5"
    ])
    if request.method == "POST":
        weight_str = request.form["weight"]
        disease = request.form.get("disease")

        print(f"Received disease: {disease}")  # Debug statement

        try:
            weight = float(weight_str)
        except ValueError:
            return "Invalid input. Please enter a valid number for weight."

        if not disease:
            return "Please select a disease."

        # Perform calculations based on the selected disease
        try:
            doses, footnotes, bolus_fluids, maintenance_rate, two_thirds_maintenance_rate = calculate_disease_doses(weight, disease)
            print(f"Calculated doses: {doses}")  # Debug statement
        except Exception as e:
            print(f"Error calculating doses: {e}")  # Debug statement
            return f"An error occurred while calculating doses: {e}"

        return render_template("disease.html", doses=doses, weight=weight, disease=disease, footnotes=footnotes, diseases=diseases, bolus_fluids=bolus_fluids, maintenance_rate=maintenance_rate, two_thirds_maintenance_rate=two_thirds_maintenance_rate)
    else:
        return render_template("disease.html", diseases=diseases)

def get_master_doses():
    return {
        # Note about concentrations and source of doses
        "Note": "DRUGS ARE LISTED BY GENERIC NAME\n1/1000 = 1% (10mg/ml), 1/10000 = 0.1mg/ml\nSource: Drug Doses Frank Shann 2017 Edition",
        "Adrenaline (All indications - 1:1000=1mg/mL, 1:10000=0.1mg/mL, Half-life 2min)": lambda weight: f"""Asthma/Bronch/Croup: {round(0.02 * weight, 3)}mL 1% or {round(0.2 * weight, 3)}mL 1:1000 dilute to 6mL (max 6mL), Ventilator: same doses, Cardiac arrest: {round(0.1 * weight, 3)}mL 1:10000 IV/IC or {round(0.1 * weight, 3)}mL 1:1000 via ETT (repeat prn), Anaphylaxis: IV {round(0.05 * weight, 3)}-{round(0.1 * weight, 3)}mL 1:10000 (repeat prn), IM {round(0.01 * weight, 3)}mL 1:1000 to thigh (max 3 doses q20min), Infusion {round(0.15 * weight, 3)}mg/50mL at 1-10mL/hr""",
        "Adrenaline infusion (0.15mg/kg in 50mL n/saline at 1-10 mL/hr)": lambda weight: round(0.15 * weight, 2),
        "Amoxicillin (25mg/kg)": lambda weight: round(25 * weight, 2),
        "Flucloxacillin (25mg/kg)": lambda weight: round(25 * weight, 2),
        "Chloramphenicol (25mg/kg)": lambda weight: round(25 * weight, 2),
        "Artemether (oily solution, 3.2mg/kg initial, then 1.6mg/kg)": lambda weight: f"Initial: {round(3.2 * weight, 2)}mg IM stat, Then: {round(1.6 * weight, 2)}mg daily until oral therapy possible",
        "Atropine (0.02mg/kg)": lambda weight: round(0.02 * weight, 2),
        "Buscopan (0.5mg/kg)": lambda weight: round(0.5 * weight, 2),
        "Ceftriaxone (50mg/kg)": lambda weight: round(50 * weight, 2),
        "Crystapen (30mg/kg)": lambda weight: round(30 * weight, 2),
        "Diazepam (0.2-0.5mg/kg)": lambda weight: f"{round(0.2 * weight, 2)} to {round(0.5 * weight, 2)}",
        "Etomidate (0.2-0.4mg/kg)": lambda weight: f"{round(0.2 * weight, 2)} to {round(0.4 * weight, 2)}",
        "Fentanyl (2-4mcg/kg)": lambda weight: f"{round(2 * weight, 2)} to {round(4 * weight, 2)}",
        "Flagyl (7.5mg/kg)": lambda weight: round(7.5 * weight, 2),
        "Gentamicin (5-7mg/kg)": lambda weight: f"{round(5 * weight, 2)} to {round(7 * weight, 2)}",
        "Hydrocortisone (4mg/kg)": lambda weight: round(4 * weight, 2),
        "Ketamine (1.5-2mg/kg)": lambda weight: f"{round(1.5 * weight, 2)} to {round(2 * weight, 2)}",
        "Lasix (0.5mg/kg)": lambda weight: round(0.5 * weight, 2),
        "Lasix (1mg/kg)": lambda weight: round(1 * weight, 2),
        "Lignocaine (1.5mg/kg)": lambda weight: round(1.5 * weight, 2),
        "Lumefantrine (4mg/kg)": lambda weight: round(4 * weight, 2),
        "Maxolone (0.1 - 0.3mg/kg)": lambda weight: f"{round(0.1 * weight, 2)} to {round(0.3 * weight, 2)}",
        "Midazolam (0.1-0.2mg/kg)": lambda weight: f"{round(0.1 * weight, 2)} to {round(0.2 * weight, 2)}",
        "Morphine (0.1-0.2mg/kg)": lambda weight: f"{round(0.1 * weight, 2)} to {round(0.2 * weight, 2)}",
        "Paracetamol 'o' (15mg/kg)": lambda weight: round(15 * weight, 2),
        "Paracetamol 'PR' (25mg/kg)": lambda weight: round(25 * weight, 2),
        "Paraldehyde (0.2mL/kg)": lambda weight: round(0.2 * weight, 2),
        "Pancuronium (0.1mg/kg)": lambda weight: round(0.1 * weight, 2),
        "Phenobarbitone (20mg/kg)": lambda weight: round(20 * weight, 2),
        "Phenytoin (20mg/kg)": lambda weight: round(20 * weight, 2),
        "Propofol (1.5-3mg/kg)": lambda weight: f"{round(1.5 * weight, 2)} to {round(3 * weight, 2)}",
        "Rocuronium (1mg/kg)": lambda weight: round(1 * weight, 2),
        "Salbutamol (0.15mg/kg)": lambda weight: round(0.15 * weight, 2),
        "Succinylcholine (1-2mg/kg)": lambda weight: f"{round(1 * weight, 2)} to {round(2 * weight, 2)}",
        "Thiopental (2-5mg/kg)": lambda weight: f"{round(2 * weight, 2)} to {round(5 * weight, 2)}",
        "Vecuronium (0.15-0.3mg/kg)": lambda weight: f"{round(0.15 * weight, 2)} to {round(0.3 * weight, 2)}",
        "Acetaminophen: See paracetamol": lambda weight: "",
        "Acetazolamide (5-10mg/kg (adult 100-250mg) 6-8H (daily for epilepsy), TB hydrocephalus: 25-50mg/kg 6-8H plus frusemide 0.25mg/kg 6H)": lambda weight: f"{round(5 * weight, 2)} to {round(10 * weight, 2)} (daily for epilepsy), {round(25 * weight, 2)} to {round(50 * weight, 2)} plus frusemide 0.25mg/kg 6H (TB hydrocephalus)",
        "Acriflavine hydrochloride (0.1% solution)": lambda weight: round(0.1 * weight, 2),
        "Adenosine (0.1mg/kg)": lambda weight: round(0.1 * weight, 2),
        "Albendazole (200mg for <10kg, 400mg for >10kg)": lambda weight: f"{200 if weight < 10 else 400}",
        "Allopurinol (Oral: 10-20mg/kg daily, max 600mg; IV: 100-150mg/m² q12h for tumor lysis)": lambda weight: f"Oral: {round(10 * weight, 2)} to {round(20 * weight, 2)}mg daily (max 600mg), IV for tumor lysis: 100-150mg/m² q12h",
        "Almotriptan (6.25-12.5mg)": lambda weight: f"{round(6.25 * weight, 2)} to {round(12.5 * weight, 2)}",
        "Amiodarone (5-7mg/kg IV)": lambda weight: f"{round(5 * weight, 2)} to {round(7 * weight, 2)}",
        "Amikacin (15mg/kg IM or IV)": lambda weight: round(15 * weight, 2),
        "Amlodipine (2.5-10mg daily oral)": lambda weight: f"{round(2.5 * weight, 2)} to {round(10 * weight, 2)}",
        "Amphotericin B (0.5-1mg/kg)": lambda weight: f"{round(0.5 * weight, 2)} to {round(1 * weight, 2)}",
        "Aminophylline (5mg/kg)": lambda weight: round(5 * weight, 2),
        "Oxygen (0.5-2 L/min by nasal prongs or 4-6 L/min by face mask)": lambda weight: "0.5-2 L/min by nasal prongs or 4-6 L/min by face mask",
        "Salbutamol Respirator Solution (0.5% solution)": lambda weight: "0.5% solution",
        "Prednisolone (5mg tabs)": lambda weight: "5mg tabs",
        "Penicillin, benzyl (penicillin G, crystalline) (30mg/kg)": lambda weight: round(30 * weight, 2),
        "Penicillin G (30mg/kg)": lambda weight: round(30 * weight, 2),
        "Amitriptyline (Usually 0.5-1mg/kg oral, Enuresis: 1-1.5mg/kg nocte)": lambda weight: f"Usual: {round(0.5 * weight, 2)} to {round(1 * weight, 2)}mg (8H oral), Enuresis: {round(1 * weight, 2)} to {round(1.5 * weight, 2)}mg nocte (max 25mg)",
        "Ampicillin (25mg/kg standard, 50mg/kg severe)": lambda weight: f"Standard: {round(25 * weight, 2)}mg (6H IV/IM/oral), Severe: {round(50 * weight, 2)}mg (max 2g) IV intervals by age: 12H (<1wk), 6H (2-4wk), 3-6H or constant infusion (4+wk)",
        "Ampicillin + flucloxacillin (Combination)": lambda weight: "Not/kg. Child: 125mg/125mg or 250mg/250mg, Adult: 250mg/250mg or 500mg/500mg (6H oral, IM or IV)",
        "Artemether 20mg + lumefantrine 120mg (Fixed combination)": lambda weight: f"{'1 tab' if weight <= 14 else '2 tab' if weight <= 24 else '3 tab' if weight <= 34 else '4 tab'} at 0hr, 8hr, 24hr, 36hr, 48hr and 60hr with fatty food. Repeat if vomiting within 1hr",
    }

    #adrenaline calculations

def calculate_adrenaline_asthma(weight): 
    return round(weight * 0.02, 2) 
def calculate_adrenaline_bronchiolitis(weight): 
    return round(weight * 0.02, 2) 
def calculate_adrenaline_croup(weight): 
    return round(weight * 0.02, 2) 
def calculate_adrenaline_cardiac_arrest(weight): 
    return round(weight * 0.1, 2) 
def calculate_adrenaline_anaphylaxis_IV(weight): 
    return round(weight * 0.05, 2) 
def calculate_adrenaline_anaphylaxis_IM(weight): 
    return round(weight * 0.01, 2) 
def calculate_adrenaline_anaphylaxis_infusion(weight): 
    return round(0.15 * weight, 2)

#common drug doses calculations
def calculate_common_doses(weight):
    master_doses = get_master_doses()
    common_drugs = [
        "Amoxicillin (25mg/kg)",
        "Flucloxacillin (25mg/kg)",
        "Chloramphenicol (25mg/kg)",
        "Buscopan (0.5mg/kg)",
        "Ceftriaxone (50mg/kg)",
        "Crystapen (30mg/kg)",
        "Flagyl (7.5mg/kg)",
        "Gentamicin (5-7mg/kg)",
        "Hydrocortisone (4mg/kg)",
        "Lasix (0.5mg/kg)",
        "Lasix (1mg/kg)",
        "Maxolone (0.1 - 0.3mg/kg)",
        "Paracetamol 'o' (15mg/kg)",
        "Paracetamol 'PR' (25mg/kg)",
        "Penicillin, benzyl (penicillin G, crystalline) (30mg/kg)"
    ]
    return {drug: master_doses[drug](weight) for drug in common_drugs}

def calculate_emergency_doses(weight):
    master_doses = get_master_doses()
    emergency_drugs = [
        "Adrenaline infusion (0.15mg/kg in 50mL n/saline at 1-10 mL/hr)",
        "Paraldehyde (0.2mL/kg)",
        "Diazepam (0.2-0.5mg/kg)",
        "Phenytoin (20mg/kg)",
        "Phenobarbitone (20mg/kg)"
    ]
    return {drug: master_doses[drug](weight) for drug in emergency_drugs}

def calculate_rsi_ett_doses(weight):
    master_doses = get_master_doses()
    rsi_ett_drugs = {
        "Pre-medication": [
            "Atropine (0.02mg/kg)",
            "Lignocaine (1.5mg/kg)"
        ],
        "Sedatives": [
            "Thiopental (2-5mg/kg)",
            "Ketamine (1.5-2mg/kg)",
            "Propofol (1.5-3mg/kg)",
            "Etomidate (0.2-0.4mg/kg)",
            "Midazolam (0.1-0.2mg/kg)",
            "Morphine (0.1-0.2mg/kg)",
            "Fentanyl (2-4mcg/kg)"
        ],
        "Depolarizing Paralytics": [
            "Succinylcholine (1-2mg/kg)"
        ],
        "Non-Depolarizing Paralytics": [
            "Vecuronium (0.15-0.3mg/kg)",
            "Pancuronium (0.1mg/kg)",
            "Rocuronium (1mg/kg)"
        ]
    }
    
    ett_data = [
        {"Weight (kg)": "<0.7", "Internal Diameter (mm)": 2.0, "External Diameter (mm)": 2.9, "At Lip (cm)": 6, "At Nose (cm)": 7},
        {"Weight (kg)": "<1", "Internal Diameter (mm)": 2.5, "External Diameter (mm)": 3.6, "At Lip (cm)": 6.5, "At Nose (cm)": 7.5},
        {"Weight (kg)": "1.0", "Internal Diameter (mm)": 3.0, "External Diameter (mm)": 4.3, "At Lip (cm)": 7, "At Nose (cm)": 8},
        {"Weight (kg)": "2.0", "Internal Diameter (mm)": 3.0, "External Diameter (mm)": 4.3, "At Lip (cm)": 8, "At Nose (cm)": 9},
        {"Weight (kg)": "3.0", "Internal Diameter (mm)": 3.0, "External Diameter (mm)": 4.3, "At Lip (cm)": 9, "At Nose (cm)": 10},
        {"Weight (kg)": "3.5", "Internal Diameter (mm)": 3.5, "External Diameter (mm)": 4.9, "At Lip (cm)": 10, "At Nose (cm)": 11},
        {"Weight (kg)": "6.0", "Internal Diameter (mm)": 3.5, "External Diameter (mm)": 4.9, "At Lip (cm)": 11, "At Nose (cm)": 12},
        {"Weight (kg)": "10", "Internal Diameter (mm)": 4.0, "External Diameter (mm)": 5.6, "At Lip (cm)": 13, "At Nose (cm)": 14},
        {"Weight (kg)": "12", "Internal Diameter (mm)": 4.5, "External Diameter (mm)": 6.2, "At Lip (cm)": 14, "At Nose (cm)": 15},
        {"Weight (kg)": "14", "Internal Diameter (mm)": 4.5, "External Diameter (mm)": 6.2, "At Lip (cm)": 14.5, "At Nose (cm)": 16},
        {"Weight (kg)": "16", "Internal Diameter (mm)": 5.0, "External Diameter (mm)": 6.9, "At Lip (cm)": 15, "At Nose (cm)": 17},
        {"Weight (kg)": "20", "Internal Diameter (mm)": 5.5, "External Diameter (mm)": 7.5, "At Lip (cm)": 16, "At Nose (cm)": 19},
        {"Weight (kg)": "24", "Internal Diameter (mm)": 6.0, "External Diameter (mm)": 8.2, "At Lip (cm)": 17, "At Nose (cm)": 20},
        {"Weight (kg)": "30", "Internal Diameter (mm)": 6.5, "External Diameter (mm)": 8.9, "At Lip (cm)": 18, "At Nose (cm)": 21},
        {"Weight (kg)": "38", "Internal Diameter (mm)": 7.0, "External Diameter (mm)": 9.5, "At Lip (cm)": 19, "At Nose (cm)": 22},
        {"Weight (kg)": "50", "Internal Diameter (mm)": 7.5, "External Diameter (mm)": 10.2, "At Lip (cm)": 20, "At Nose (cm)": 23},
        {"Weight (kg)": "60", "Internal Diameter (mm)": 8.0, "External Diameter (mm)": 10.8, "At Lip (cm)": 21, "At Nose (cm)": 24},
        {"Weight (kg)": "70", "Internal Diameter (mm)": 9.0, "External Diameter (mm)": 12.1, "At Lip (cm)": 21, "At Nose (cm)": 25}
    ]

    # Find appropriate ETT size based on weight
    ett_info = next((ett for ett in ett_data if weight <= float(ett["Weight (kg)"].replace("<", ""))), ett_data[-1])

    return {category: {drug: master_doses[drug](weight) for drug in drugs} for category, drugs in rsi_ett_drugs.items()}, ett_info

def calculate_all_drugs(weight):
    master_doses = get_master_doses()
    # Filter out the Note key and non-callable items
    all_drugs = [drug for drug in master_doses.keys() if drug != "Note" and callable(master_doses[drug])]
    # Calculate doses for all drugs
    return {drug: master_doses[drug](weight) for drug in sorted(all_drugs)}

def calculate_fluids(weight):
    bolus_fluids = {
        "Bolus (10mL/kg)": 10 * weight,
        "Bolus (15mL/kg)": 15 * weight,
        "Bolus (20mL/kg)": 20 * weight,
    }

    if weight <= 10:
        maintenance_rate = 4 * weight
    elif weight <= 30:
        maintenance_rate = (4 * 10) + (2 * (weight - 10))
    else:
        maintenance_rate = (4 * 10) + (2 * 20) + (1 * (weight - 30))

    two_thirds_maintenance_rate = round(maintenance_rate * 2 / 3, 1)

    return bolus_fluids, maintenance_rate, two_thirds_maintenance_rate

def calculate_disease_doses(weight, disease):
    master_doses = get_master_doses()
    footnotes = []
    bolus_fluids, maintenance_rate, two_thirds_maintenance_rate = None, None, None
    if disease == "Reactive Airways Disease":
        disease_drugs = [
            "Salbutamol (0.15mg/kg)",
            "Amoxicillin (25mg/kg)",
            "Hydrocortisone (4mg/kg)"
        ]
    elif disease == "Meningitis":
        disease_drugs = [
            "Ceftriaxone (50mg/kg)",
            "Gentamicin (5-7mg/kg)",
            "Paracetamol 'o' (15mg/kg)",
            "Chloramphenicol (25mg/kg)",
            "Phenobarbitone (20mg/kg)",
            "Paraldehyde (0.2mL/kg)",
            "Phenytoin (20mg/kg)"
        ]
    elif disease == "Malaria":
        disease_drugs = [
            "Artemether (3.2mg/kg)",
            "Lumefantrine (4mg/kg)"
        ]
    elif disease == "Asthma":
        bolus_fluids, maintenance_rate, two_thirds_maintenance_rate = calculate_fluids(weight)
        disease_drugs = [
            "Salbutamol (0.15mg/kg)",
            "Prednisolone (5mg tabs)",
            "Hydrocortisone (4mg/kg)",
            "Aminophylline (5mg/kg)",
            "Crystapen (30mg/kg)",
            "Amoxicillin (25mg/kg)"
        ]
        footnotes.append("Oxygen: 0.5-2 L/min by nasal prongs or 4-6 L/min by face mask")
        footnotes.append("Salbutamol Respirator Solution: 0.5% solution")
        footnotes.append("I.V. fluid: Hartman’s solution or 0.45% NaCl + 5% dextrose")
        footnotes.append("Give aminophylline 6 hourly; add into the burette and add Hartmann’s solution up to the hourly maintenance amount. Run this over one hour, then continue the dextrose saline at maintenance rate. If you do not have a burette, inject the aminophylline intravenously slowly over at least 15 minutes every 6 hours.")
        footnotes.append("IV Aminophylline can be dangerous – Do not give IV aminophylline if the child has already had aminophylline in the last 4 hours. Stop giving aminophylline if the child gets a headache or starts vomiting.")
    elif disease == "Conjunctivitis":
        disease_drugs = [
            "Gentamicin (5-7mg/kg)",
            "Penicillin G (30mg/kg)"
        ]
        footnotes.append("Treat the mother and father and contacts for STIs if STI is suspected.")
        footnotes.append("Refer any patient to the hospital if conjunctivitis does not improve after 2 days of treatment.")
        gentamicin_dose = master_doses["Gentamicin (5-7mg/kg)"](weight)
        penicillin_g_dose = master_doses["Penicillin G (30mg/kg)"](weight)
  
    elif disease == "Disease 4":
        disease_drugs = [
            "Disease 4 Drug A",
            "Disease 4 Drug B"
        ]
    elif disease == "Disease 5":
        disease_drugs = [
            "Disease 5 Drug A",
            "Disease 5 Drug B"
        ]
    else:
        raise ValueError("Invalid disease selection.")
    
    return {drug: master_doses[drug](weight) if callable(master_doses[drug]) else drug.split(":")[0] + ": " + master_doses[drug] for drug in disease_drugs}, footnotes, bolus_fluids, maintenance_rate, two_thirds_maintenance_rate

def calculate_paraldehyde_dose(weight):
    if weight < 6:
        return "Paraldehyde: 1 ml IM"
    elif weight < 10:
        return "Paraldehyde: 1 ½ ml IM"
    elif weight < 15:
        return "Paraldehyde: 2 ½ ml IM"
    elif weight < 20:
        return "Paraldehyde: 3 ml IM"
    elif weight < 30:
        return "Paraldehyde: 4 ml IM"
    else:
        return "Paraldehyde: 5 ml IM"

def calculate_parkland_formula(weight, tbsa):
    total_volume = 3 * weight * tbsa
    first_8_hours = total_volume / 2
    next_16_hours = total_volume / 2
    first_8_hours_rate = first_8_hours / 8
    next_16_hours_rate = next_16_hours / 16
    return total_volume, first_8_hours, first_8_hours_rate, next_16_hours, next_16_hours_rate

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)