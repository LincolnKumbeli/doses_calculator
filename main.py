from flask import Flask, request, render_template, url_for, redirect, flash
from collections import OrderedDict
from werkzeug.serving import WSGIRequestHandler
import ssl

app = Flask(__name__, 
    static_folder='static',
    template_folder='templates'  # Points to /doses-app/templates
)
app.secret_key = 'your_secret_key_here'  # Add this for flash messages

# Add these configurations to disable template caching
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        weight_str = request.form.get("weight", "")
        calc_type = request.form.get("calc_type")
        tbsa_str = request.form.get("tbsa", "")  # Get TBSA value if provided
    if request.method == "POST":
        weight_str = request.form.get("weight", "")
        calc_type = request.form.get("calc_type")
        tbsa_str = request.form.get("tbsa", "")  # Get TBSA value if provided

        if not weight_str:
            flash("Please enter a weight value.")
            return render_template("index.html")
        
        if not calc_type:
            flash("Please select a calculation type.")
            return render_template("index.html")

        try:
            weight = float(weight_str)
            tbsa = float(tbsa_str) if tbsa_str else None  # Convert TBSA if provided
            
            if tbsa is not None and (tbsa < 0 or tbsa > 100):  # Validate TBSA
                raise ValueError("TBSA must be between 0 and 100")
                
            if weight <= 0 or weight > 150:  # reasonable weight range
                raise ValueError
        except ValueError:
            flash("Invalid input. Please enter a valid number for weight.")
            return render_template("index.html")

        # Perform calculations based on selection
        doses = {}
        bolus_fluids, maintenance_rate, two_thirds_maintenance_rate = {}, None, None
        if calc_type == "all_drugs":
            doses = calculate_all_drugs(weight)
            return render_template("index.html", doses=doses, weight=weight, calc_type=calc_type)
        elif calc_type == "common":
            doses = calculate_doses(weight)
            bolus_fluids, maintenance_rate, two_thirds_maintenance_rate = calculate_fluids(weight)
        elif calc_type == "emergency":
            doses = calculate_emergency_doses(weight)
            bolus_fluids, maintenance_rate, two_thirds_maintenance_rate = calculate_fluids(weight)
            
            # Calculate Parkland formula if TBSA provided
            parkland_data = None
            if tbsa:
                total_volume, first_8_hours, first_8_hours_rate, next_16_hours, next_16_hours_rate = calculate_parkland_formula(weight, tbsa)
                parkland_data = {
                    'total_volume': round(total_volume, 1),
                    'first_8_hours': round(first_8_hours, 1),
                    'first_8_hours_rate': round(first_8_hours_rate, 1),
                    'next_16_hours': round(next_16_hours, 1),
                    'next_16_hours_rate': round(next_16_hours_rate, 1)
                }
            
            return render_template("index.html",
                doses=doses,
                bolus_fluids=bolus_fluids,
                maintenance_rate=maintenance_rate,
                two_thirds_maintenance_rate=two_thirds_maintenance_rate,
                parkland_data=parkland_data,
                weight=weight,
                tbsa=tbsa,
                calc_type=calc_type)
        elif calc_type == "RSI and ETT":
            doses, ett_info = calculate_rsi_ett_doses(weight)
            bolus_fluids, maintenance_rate, two_thirds_maintenance_rate = calculate_fluids(weight)
            return render_template("index.html", 
                doses=doses, 
                ett_info=ett_info,
                bolus_fluids=bolus_fluids, 
                maintenance_rate=maintenance_rate, 
                two_thirds_maintenance_rate=two_thirds_maintenance_rate, 
                weight=weight, 
                calc_type=calc_type)
        elif calc_type == "disease":
            return redirect(url_for('disease'))
        else:
            flash("Invalid calculation type.")
            return render_template("index.html")

        return render_template("index.html", doses=doses, bolus_fluids=bolus_fluids, maintenance_rate=maintenance_rate, two_thirds_maintenance_rate=two_thirds_maintenance_rate, weight=weight, calc_type=calc_type)
    else:
        return render_template("index.html")

@app.route("/disease", methods=["GET", "POST"])
def disease():
    if request.method == "POST":
        weight_str = request.form["weight"]
        disease = request.form.get("disease")

        try:
            weight = float(weight_str)
        except ValueError:
            flash("Invalid input. Please enter a valid number for weight.")
            return render_template("disease.html")

        # Perform calculations based on the selected disease
        doses, footnotes, bolus_fluids, maintenance_rate, two_thirds_maintenance_rate = calculate_disease_doses(weight, disease)
        return render_template("disease.html", doses=doses, footnotes=footnotes, bolus_fluids=bolus_fluids, maintenance_rate=maintenance_rate, two_thirds_maintenance_rate=two_thirds_maintenance_rate, weight=weight, disease=disease)
    else:
        return render_template("disease.html")

def calculate_doses(weight):
    doses = {
        "Amoxicillin (25mg/kg)": round(25 * weight, 2),
        "Flucloxacillin (25mg/kg)": round(25 * weight, 2),
        "Chloramphenicol (25mg/kg)": round(25 * weight, 2),
        "Buscopan (0.5mg/kg)": round(0.5 * weight, 2),
        "Ceftriaxone (50mg/kg)": round(50 * weight, 2),
        "Crystapen (30mg/kg)": round(30 * weight, 2),
        "Flagyl (7.5mg/kg)": round(7.5 * weight, 2),
        "Gentamicin (5-7mg/kg)": f"{round(5 * weight, 2)} to {round(7 * weight, 2)}",
        "Hydrocortisone (4mg/kg)": round(4 * weight, 2),
        "Lasix (0.5mg/kg)": round(0.5 * weight, 2),
        "Lasix (1mg/kg)": round(1 * weight, 2),
        "Maxolone (0.1 - 0.3/kg)": f"{round(0.1 * weight, 2)} to {round(0.3 * weight, 2)}",
        "Paracetamol 'o' (15mg/kg)": round(15 * weight, 2),
        "Paracetamol 'PR' (25mg/kg)": round(25 * weight, 2),
    }
    return doses

def calculate_emergency_doses(weight):
    master_doses = get_master_doses()
    emergency_drugs = [
        "Adrenaline infusion (0.15mg/kg in 50mL n/saline at 1-10 mL/hr)",
        "Paraldehyde (0.2mL/kg)",
        "Diazepam (0.2-0.5mg/kg)",
        "Phenytoin (20mg/kg)",
        "Phenobarbitone (20mg/kg)"
    ]
    return {"Drugs": OrderedDict(sorted([(drug, master_doses[drug](weight)) for drug in emergency_drugs], key=lambda x: x[0].lower()))}

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
    
    # Endotracheal Tube Information
    ett_data = [
        {"Age": "Birth", "Weight (kg)": "<0.7", "Internal Diameter (mm)": 2.0, "External Diameter (mm)": 2.9, "At Lip (cm)": 6, "At Nose (cm)": 6.5, "Sucker FG": 6},
        {"Age": "Birth", "Weight (kg)": "<1", "Internal Diameter (mm)": 2.5, "External Diameter (mm)": 3.6, "At Lip (cm)": 6.5, "At Nose (cm)": 7, "Sucker FG": 6},
        {"Age": "Birth", "Weight (kg)": "1.0", "Internal Diameter (mm)": 3.0, "External Diameter (mm)": 4.3, "At Lip (cm)": 7, "At Nose (cm)": 7.5, "Sucker FG": 7},
        {"Age": "Birth", "Weight (kg)": "2.0", "Internal Diameter (mm)": 3.0, "External Diameter (mm)": 4.3, "At Lip (cm)": 8, "At Nose (cm)": 9, "Sucker FG": 7},
        {"Age": "Birth", "Weight (kg)": "3.0", "Internal Diameter (mm)": 3.0, "External Diameter (mm)": 4.3, "At Lip (cm)": 9, "At Nose (cm)": 10.5, "Sucker FG": 7},
        {"Age": "Birth", "Weight (kg)": "3.5", "Internal Diameter (mm)": 3.5, "External Diameter (mm)": 4.9, "At Lip (cm)": 10, "At Nose (cm)": 11, "Sucker FG": 8},
        {"Age": "3 months", "Weight (kg)": "6.0", "Internal Diameter (mm)": 3.5, "External Diameter (mm)": 4.9, "At Lip (cm)": 11, "At Nose (cm)": 12, "Sucker FG": 8},
        {"Age": "1 year", "Weight (kg)": "10", "Internal Diameter (mm)": 4.0, "External Diameter (mm)": 5.6, "At Lip (cm)": 13, "At Nose (cm)": 14, "Sucker FG": 8},
        {"Age": "2 years", "Weight (kg)": "12", "Internal Diameter (mm)": 4.5, "External Diameter (mm)": 6.2, "At Lip (cm)": 14, "At Nose (cm)": 15, "Sucker FG": 8},
        {"Age": "3 years", "Weight (kg)": "14", "Internal Diameter (mm)": 4.5, "External Diameter (mm)": 6.2, "At Lip (cm)": 14.5, "At Nose (cm)": 16, "Sucker FG": 8},
        {"Age": "4 years", "Weight (kg)": "16", "Internal Diameter (mm)": 5.0, "External Diameter (mm)": 6.9, "At Lip (cm)": 15, "At Nose (cm)": 17, "Sucker FG": 10},
        {"Age": "6 years", "Weight (kg)": "20", "Internal Diameter (mm)": 5.5, "External Diameter (mm)": 7.5, "At Lip (cm)": 16, "At Nose (cm)": 19, "Sucker FG": 10},
        {"Age": "8 years", "Weight (kg)": "24", "Internal Diameter (mm)": 6.0, "External Diameter (mm)": 8.2, "At Lip (cm)": 17, "At Nose (cm)": 20, "Sucker FG": 10},
        {"Age": "10 years", "Weight (kg)": "30", "Internal Diameter (mm)": 6.5, "External Diameter (mm)": 8.9, "At Lip (cm)": 18, "At Nose (cm)": 21, "Sucker FG": 12},
        {"Age": "12 years", "Weight (kg)": "38", "Internal Diameter (mm)": 7.0, "External Diameter (mm)": 9.5, "At Lip (cm)": 19, "At Nose (cm)": 22, "Sucker FG": 12},
        {"Age": "14 years", "Weight (kg)": "50", "Internal Diameter (mm)": 7.5, "External Diameter (mm)": 10.2, "At Lip (cm)": 20, "At Nose (cm)": 23, "Sucker FG": 12},
        {"Age": "Adult", "Weight (kg)": "60", "Internal Diameter (mm)": 8.0, "External Diameter (mm)": 10.8, "At Lip (cm)": 21, "At Nose (cm)": 24, "Sucker FG": 12},
        {"Age": "Adult", "Weight (kg)": "70", "Internal Diameter (mm)": 9.0, "External Diameter (mm)": 12.1, "At Lip (cm)": 21, "At Nose (cm)": 25, "Sucker FG": 12},
    ]

    # Determine appropriate ETT size and length for the child's weight
    ett_info = next((ett for ett in ett_data if weight <= float(ett["Weight (kg)"].replace("<", ""))), ett_data[-1])

    return {category: {drug: master_doses[drug](weight) for drug in drugs} for category, drugs in rsi_ett_drugs.items()}, ett_info

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
    doses = OrderedDict()
    footnotes = []
    bolus_fluids, maintenance_rate, two_thirds_maintenance_rate = None, None, None

    disease_drugs = {
        "Reactive Airways Disease": [
            "Salbutamol (0.15mg/kg)",
            "Prednisolone (5mg tabs)",
            "Hydrocortisone (4mg/kg)",
            "Aminophylline (5mg/kg)",
            "Oxygen (0.5-2 L/min by nasal prongs or 4-6 L/min by face mask)"
        ],
        "Meningitis": [
            "Ceftriaxone (50mg/kg)",
            "Gentamicin (5-7mg/kg)",
            "Chloramphenicol (25mg/kg)",
            "Phenobarbitone (20mg/kg)",
            "Paraldehyde (0.2mL/kg)",
            "Phenytoin (20mg/kg)",
            "Paracetamol 'o' (15mg/kg)",
            "Diazepam (0.2-0.5mg/kg)"
        ],
        "Malaria": [
            "Artemether (oily solution, 3.2mg/kg initial, then 1.6mg/kg)",
            "Artemether 20mg + lumefantrine 120mg (Fixed combination)",
            "Paracetamol 'o' (15mg/kg)"
        ],
        "Asthma": [
            "Salbutamol (0.15mg/kg)",
            "Prednisolone (5mg tabs)",
            "Hydrocortisone (4mg/kg)",
            "Aminophylline (5mg/kg)",
            "Oxygen (0.5-2 L/min by nasal prongs or 4-6 L/min by face mask)",
            "Salbutamol Respirator Solution (0.5% solution)"
        ],
        "Pneumonia": [
            "Crystapen (30mg/kg)",
            "Gentamicin (5-7mg/kg)",
            "Amoxicillin (25mg/kg)",
            "Paracetamol 'o' (15mg/kg)",
            "Ceftriaxone (50mg/kg)",
            "Oxygen (0.5-2 L/min by nasal prongs or 4-6 L/min by face mask)"
        ],
        "Sepsis": [
            "Ceftriaxone (50mg/kg)",
            "Gentamicin (5-7mg/kg)",
            "Chloramphenicol (25mg/kg)",
            "Adrenaline infusion (0.15mg/kg in 50mL n/saline at 1-10 mL/hr)",
            "Hydrocortisone (4mg/kg)",
            "Paracetamol 'o' (15mg/kg)"
        ],
        "Conjunctivitis": [
            "Gentamicin (5-7mg/kg)",
            "Penicillin G (30mg/kg)",
            "Chloramphenicol (25mg/kg)"
        ],
        "Anaemia": [
            "Ferrous sulfate (6mg/kg)",
            "Folic acid (5mg/day)",
            "Vitamin C (100mg/day)",
            "Gentamicin (5-7mg/kg)",  # If infection suspected
            "Paracetamol 'o' (15mg/kg)"  # For symptomatic relief
        ],
        "Measles": [
            "Vitamin A (50,000-200,000 IU)",
            "Amoxicillin (25mg/kg)",
            "Paracetamol 'o' (15mg/kg)",
            "Vitamin C (100mg/day)",
            "Gentamicin (5-7mg/kg)",  # If secondary infection
            "Oxygen (0.5-2 L/min by nasal prongs or 4-6 L/min by face mask)"  # If needed
        ],
    }

    # Common footnotes for specific conditions
    disease_footnotes = {
        "Asthma": [
            "Monitor O2 sats - aim for >94%",
            "Administer O2 via nasal prongs (0.5-2 L/min) or face mask (4-6 L/min) if sats <94%",
            "Give aminophylline 6 hourly: add to burette with Hartmann's up to hourly maintenance, run over 1 hour",
            "If no burette, inject aminophylline IV slowly over 15+ minutes q6h",
            "WARNING: Do not give IV aminophylline if given in last 4 hours",
            "Stop aminophylline if headache/vomiting develops",
            "Monitor for tachycardia with repeated salbutamol"
        ],
        "Meningitis": [
            "Start antibiotics within 30 minutes",
            "Monitor GCS and pupils hourly",
            "Watch for seizures - have anticonvulsants ready",
            "Maintain adequate hydration - calculate maintenance fluids",
            "Consider dexamethasone in suspected TB meningitis"
        ],
        "Malaria": [
            "Consider severe malaria if: altered consciousness, severe anemia, respiratory distress",
            "For severe malaria use IV artesunate if available",
            "Give first artemether dose IM stat",
            "Ensure fatty meal with lumefantrine doses",
            "Monitor blood glucose",
            "Check Hb and repeat if severe anemia"
        ],
        "Conjunctivitis": [
            "For neonatal conjunctivitis - treat mother and contacts for STIs",
            "If purulent - take swab for MC&S before starting antibiotics",
            "Apply eye drops/ointment after cleaning discharge",
            "Refer if no improvement after 48 hours of treatment",
            "Warn about hand hygiene to prevent spread"
        ],
        "Anaemia": [
            "Check Hb level if possible",
            "Look for and treat cause (malaria, worms, malnutrition)",
            "Give iron with vitamin C to improve absorption",
            "Caution in malaria - only give iron after malaria treatment",
            "Review in 2 weeks to check response",
            "Continue iron for 3 months after Hb normalizes"
        ],
        "Measles": [
            "Give Vitamin A immediately",
            "Repeat Vitamin A next day and in 2-4 weeks",
            "Age <6m: 50,000 IU, 6-11m: 100,000 IU, >12m: 200,000 IU",
            "Watch for pneumonia, diarrhea, malnutrition",
            "Monitor respiratory rate and O2 sats",
            "Isolate patient - highly infectious",
            "Look for and treat eye complications",
            "Consider HIV testing if severe/complicated"
        ],
    }

    if disease in disease_drugs:
        # Calculate doses for all drugs in the condition
        for drug in disease_drugs[disease]:
            doses[drug] = master_doses[drug](weight)

        # Add condition-specific footnotes
        if disease in disease_footnotes:
            footnotes.extend(disease_footnotes[disease])

        # Add fluid calculations for conditions needing it
        if disease in ["Asthma", "Meningitis", "Sepsis", "Pneumonia"]:
            bolus_fluids, maintenance_rate, two_thirds_maintenance_rate = calculate_fluids(weight)

    return doses, footnotes, bolus_fluids, maintenance_rate, two_thirds_maintenance_rate

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

def calculate_adrenaline_doses(weight):
    return {
        "Asthma/Bronch/Croup": f"{round(0.02 * weight, 3)}mL 1% or {round(0.2 * weight, 3)}mL 1:1000 dilute to 6mL (max 6mL)",
        "Cardiac arrest": f"{round(0.1 * weight, 3)}mL 1:10000 IV/IC or {round(0.1 * weight, 3)}mL 1:1000 via ETT",
        "Anaphylaxis IV": f"{round(0.05 * weight, 3)}-{round(0.1 * weight, 3)}mL 1:10000",
        "Anaphylaxis IM": f"{round(0.01 * weight, 3)}mL 1:1000 to thigh (max 3 doses q20min)",
        "Infusion": f"{round(0.15 * weight, 3)}mg/50mL at 1-10mL/hr"
    }

def get_master_doses():
    return {
        "Note": "DRUGS ARE LISTED BY GENERIC NAME\n1/1000 = 1% (10mg/ml), 1/10000 = 0.1mg/ml\nSource: Drug Doses Frank Shann 2017 Edition",
        # All drug definitions with lambdas as provided in your list
        "Acetaminophen: See paracetamol": lambda weight: "",
        "Acetazolamide (5-10mg/kg (adult 100-250mg) 6-8H (daily for epilepsy), TB hydrocephalus: 25-50mg/kg 6-8H plus frusemide 0.25mg/kg 6H)": lambda weight: f"{round(5 * weight, 2)} to {round(10 * weight, 2)} (daily for epilepsy), {round(25 * weight, 2)} to {round(50 * weight, 2)} plus frusemide 0.25mg/kg 6H (TB hydrocephalus)",
        "Acriflavine hydrochloride (0.1% solution)": lambda weight: round(0.1 * weight, 2),
        "Adenosine (0.1mg/kg)": lambda weight: round(0.1 * weight, 2),
        "Adrenaline (All indications - 1:1000=1mg/mL, 1:10000=0.1mg/mL, Half-life 2min)": lambda weight: f"""Asthma/Bronch/Croup: {round(0.02 * weight, 3)}mL 1% or {round(0.2 * weight, 3)}mL 1:1000 dilute to 6mL (max 6mL), Ventilator: same doses, Cardiac arrest: {round(0.1 * weight, 3)}mL 1:10000 IV/IC or {round(0.1 * weight, 3)}mL 1:1000 via ETT (repeat prn), Anaphylaxis: IV {round(0.05 * weight, 3)}-{round(0.1 * weight, 3)}mL 1:10000 (repeat prn), IM {round(0.01 * weight, 3)}mL 1:1000 to thigh (max 3 doses q20min), Infusion {round(0.15 * weight, 3)}mg/50mL at 1-10mL/hr""",
        "Adrenaline infusion (0.15mg/kg in 50mL n/saline at 1-10 mL/hr)": lambda weight: round(0.15 * weight, 2),
        "Albendazole (200mg for <10kg, 400mg for >10kg)": lambda weight: f"{200 if weight < 10 else 400}",
        "Allopurinol (Oral: 10-20mg/kg daily, max 600mg; IV: 100-150mg/m² q12h for tumor lysis)": lambda weight: f"Oral: {round(10 * weight, 2)} to {round(20 * weight, 2)}mg daily (max 600mg), IV for tumor lysis: 100-150mg/m² q12h",
        "Almotriptan (6.25-12.5mg)": lambda weight: f"{round(6.25 * weight, 2)} to {round(12.5 * weight, 2)}",
        "Amikacin (15mg/kg IM or IV)": lambda weight: round(15 * weight, 2),
        "Amiodarone (5-7mg/kg IV)": lambda weight: f"{round(5 * weight, 2)} to {round(7 * weight, 2)}",
        "Amlodipine (2.5-10mg daily oral)": lambda weight: f"{round(2.5 * weight, 2)} to {round(10 * weight, 2)}",
        "Amitriptyline (Usually 0.5-1mg/kg oral, Enuresis: 1-1.5mg/kg nocte)": lambda weight: f"Usual: {round(0.5 * weight, 2)} to {round(1 * weight, 2)}mg (8H oral), Enuresis: {round(1 * weight, 2)} to {round(1.5 * weight, 2)}mg nocte (max 25mg)",
        "Aminophylline (5mg/kg)": lambda weight: round(5 * weight, 2),
        "Amoxicillin (25mg/kg)": lambda weight: round(25 * weight, 2),
        "Amphotericin B (0.5-1mg/kg)": lambda weight: f"{round(0.5 * weight, 2)} to {round(1 * weight, 2)}",
        "Ampicillin (25mg/kg standard, 50mg/kg severe)": lambda weight: f"Standard: {round(25 * weight, 2)}mg (6H IV/IM/oral), Severe: {round(50 * weight, 2)}mg (max 2g) IV intervals by age: 12H (<1wk), 6H (2-4wk), 3-6H or constant infusion (4+wk)",
        "Ampicillin + flucloxacillin (Combination)": lambda weight: "Not/kg. Child: 125mg/125mg or 250mg/250mg, Adult: 250mg/250mg or 500mg/500mg (6H oral, IM or IV)",
        "Artemether (oily solution, 3.2mg/kg initial, then 1.6mg/kg)": lambda weight: f"Initial: {round(3.2 * weight, 2)}mg IM stat, Then: {round(1.6 * weight, 2)}mg daily until oral therapy possible",
        "Artemether 20mg + lumefantrine 120mg (Fixed combination)": lambda weight: f"{'1 tab' if weight <= 14 else '2 tab' if weight <= 24 else '3 tab' if weight <= 34 else '4 tab'} at 0hr, 8hr, 24hr, 36hr, 48hr and 60hr with fatty food. Repeat if vomiting within 1hr",
        "Atropine (0.02mg/kg)": lambda weight: round(0.02 * weight, 2),
        "Baclofen (0.2-1mg/kg)": lambda weight: f"Initial: {round(0.2 * weight, 2)}mg (8H oral), Increase every 3 days to {round(1 * weight, 2)}mg (max 50mg) 8H. Intrathecal: {round(2 * weight, 2)}-{round(20 * weight, 2)}mcg/24hr (max 1000mcg)",
        "Benzathine penicillin (1mg = 1250u)": lambda weight: f"Standard: {round(25 * weight, 2)}mg (max 900mg) IM once, Venereal disease: {round(40 * weight, 2)}mg (max 1.8g) IM once, Strep prophylaxis: {round(25 * weight, 2)}mg (max 900mg) IM 3-4 weekly OR {round(10 * weight, 2)}mg IM 2 weekly",
        "Benzhexol (>3yr: 0.02-0.3mg/kg)": lambda weight: f"Initial: {round(0.02 * weight, 3)}mg (8H oral), increase to {round(0.1 * weight, 3)}-{round(0.3 * weight, 3)}mg (max 5mg) 8H oral",
        "Buscopan (0.5mg/kg)": lambda weight: round(0.5 * weight, 2),
        "Ceftriaxone (50mg/kg)": lambda weight: round(50 * weight, 2),
        "Chloramphenicol (25mg/kg)": lambda weight: round(25 * weight, 2),
        "Crystapen (30mg/kg)": lambda weight: round(30 * weight, 2),
        "Diazepam (0.2-0.5mg/kg)": lambda weight: f"{round(0.2 * weight, 2)} to {round(0.5 * weight, 2)}",
        "Etomidate (0.2-0.4mg/kg)": lambda weight: f"{round(0.2 * weight, 2)} to {round(0.4 * weight, 2)}",
        "Fentanyl (2-4mcg/kg)": lambda weight: f"{round(2 * weight, 2)} to {round(4 * weight, 2)}",
        "Flagyl (7.5mg/kg)": lambda weight: round(7.5 * weight, 2),
        "Flucloxacillin (25mg/kg)": lambda weight: round(25 * weight, 2),
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
        "Oxygen (0.5-2 L/min by nasal prongs or 4-6 L/min by face mask)": lambda weight: "0.5-2 L/min by nasal prongs or 4-6 L/min by face mask",
        "Pancuronium (0.1mg/kg)": lambda weight: round(0.1 * weight, 2),
        "Paracetamol 'o' (15mg/kg)": lambda weight: round(15 * weight, 2),
        "Paracetamol 'PR' (25mg/kg)": lambda weight: round(25 * weight, 2),
        "Paraldehyde (0.2mL/kg)": lambda weight: round(0.2 * weight, 2),
        "Penicillin G (30mg/kg)": lambda weight: round(30 * weight, 2),
        "Penicillin, benzyl (penicillin G, crystalline) (30mg/kg)": lambda weight: round(30 * weight, 2),
        "Phenobarbitone (20mg/kg)": lambda weight: round(20 * weight, 2),
        "Phenytoin (20mg/kg)": lambda weight: round(20 * weight, 2),
        "Prednisolone (5mg tabs)": lambda weight: "5mg tabs",
        "Propofol (1.5-3mg/kg)": lambda weight: f"{round(1.5 * weight, 2)} to {round(3 * weight, 2)}",
        "Rocuronium (1mg/kg)": lambda weight: round(1 * weight, 2),
        "Salbutamol (0.15mg/kg)": lambda weight: round(0.15 * weight, 2),
        "Salbutamol Respirator Solution (0.5% solution)": lambda weight: "0.5% solution",
        "Succinylcholine (1-2mg/kg)": lambda weight: f"{round(1 * weight, 2)} to {round(2 * weight, 2)}",
        "Thiopental (2-5mg/kg)": lambda weight: f"{round(2 * weight, 2)} to {round(5 * weight, 2)}",
        "Vecuronium (0.15-0.3mg/kg)": lambda weight: f"{round(0.15 * weight, 2)} to {round(0.3 * weight, 2)}",
        # Add missing drug calculations
        "Ferrous sulfate (6mg/kg)": lambda weight: round(6 * weight, 2),
        "Folic acid (5mg/day)": lambda weight: "5mg/day",
        "Vitamin C (100mg/day)": lambda weight: "100mg/day",
        "Penicillin G (30mg/kg)": lambda weight: round(30 * weight, 2),
        
        # Make sure all strings are properly terminated
        "Oxygen (0.5-2 L/min by nasal prongs or 4-6 L/min by face mask)": 
            lambda weight: "0.5-2 L/min by nasal prongs or 4-6 L/min by face mask",
        
        # Ensure proper formatting for complex doses
        "Artemether (oily solution, 3.2mg/kg initial, then 1.6mg/kg)": 
            lambda weight: f"Initial: {round(3.2 * weight, 2)}mg IM stat, Then: {round(1.6 * weight, 2)}mg daily",
    }

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
    return OrderedDict(sorted([(drug, master_doses[drug](weight)) for drug in common_drugs], key=lambda x: x[0].lower()))

def calculate_all_drugs(weight):
    master_doses = get_master_doses()
    result = OrderedDict()
    result["Note"] = master_doses["Note"]
    
    drug_items = [(k, v) for k, v in master_doses.items() if k != "Note" and callable(v)]
    sorted_drug_items = sorted(drug_items, key=lambda x: x[0].lower())
    
    for drug, calculator in sorted_drug_items:
        result[drug] = calculator(weight)
    
    return result

def calculate_parkland_formula(weight, tbsa):
    """
    Calculate fluid requirements using Parkland formula
    Formula: 4 * weight * %TBSA = Total volume for 24 hours
    First 8 hours: 50% of total
    Next 16 hours: 50% of total
    """
    total_volume = 4 * weight * tbsa  # mL for 24 hours
    first_8_hours = total_volume / 2
    next_16_hours = total_volume / 2
    first_8_hours_rate = first_8_hours / 8  # mL/hour
    next_16_hours_rate = next_16_hours / 16  # mL/hour
    
    return total_volume, first_8_hours, first_8_hours_rate, next_16_hours, next_16_hours_rate

@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 0 minutes.
    """
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response

if __name__ == "__main__":
    try:
        import socket
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        
        print(f"Server starting on {local_ip}")
        print("Try these URLs:")
        print(f"* Local computer: http://localhost:5000")
        print(f"* Same network: http://{local_ip}:5000")
        
        app.run(
            host="0.0.0.0",
            port=5000,
            debug=True,
            use_reloader=True
        )
    except Exception as e:
        print(f"Error starting server: {e}")
        print("Try accessing manually at:")
        print("* http://localhost:5000")
        print("* http://127.0.0.1:5000")
        print("* http://localhost:5000")
        print(f"Error starting server: {e}")
        print("Try accessing manually at:")
        print("* http://localhost:5000")
        print("* http://127.0.0.1:5000")
        print("* http://127.0.0.1:5000")