from flask import Flask, request, render_template, url_for, redirect, flash
from collections import OrderedDict

# Import disease data from a separate file
try:
    from disease_content import disease_data
except ModuleNotFoundError:
    print("⚠️ ERROR: 'disease_content.py' file is missing or not found. Ensure it is in the same directory as 'main.py'.")

# Import drug lists and fluid calculations
from drug_list import drug_data
from common_drugs import common_drugs
from emergency_drugs import emergency_drugs
from rsi_ett_drugs import rsi_ett_drugs
from fluids import calculate_fluids, calculate_parkland_formula

app = Flask(__name__, 
    static_folder='static',
    template_folder='templates'
)
app.secret_key = 'your_secret_key_here'

# Disable template caching
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

def calculate_ett_size(weight):
    """Calculate ETT size and details based on weight"""
    if weight < 3:
        return {
            "Age": "Newborn < 3kg",
            "Internal Diameter (mm)": 3.0,
            "External Diameter (mm)": 4.2,
            "Length at Lip (cm)": 9,
            "Length at Nose (cm)": 10.5,
            "Sucker Size (FG)": 6
        }
    elif weight < 4:
        return {
            "Age": "Newborn 3-4kg",
            "Internal Diameter (mm)": 3.5,
            "External Diameter (mm)": 4.8,
            "Length at Lip (cm)": 10,
            "Length at Nose (cm)": 11.5,
            "Sucker Size (FG)": 8
        }
    elif weight < 6:
        return {
            "Age": "3-6 months",
            "Internal Diameter (mm)": 3.5,
            "External Diameter (mm)": 4.8,
            "Length at Lip (cm)": 11,
            "Length at Nose (cm)": 12.5,
            "Sucker Size (FG)": 8
        }
    elif weight < 8:
        return {
            "Age": "6-12 months",
            "Internal Diameter (mm)": 4.0,
            "External Diameter (mm)": 5.5,
            "Length at Lip (cm)": 12,
            "Length at Nose (cm)": 14,
            "Sucker Size (FG)": 8
        }
    elif weight < 10:
        return {
            "Age": "1-2 years",
            "Internal Diameter (mm)": 4.5,
            "External Diameter (mm)": 6.2,
            "Length at Lip (cm)": 13,
            "Length at Nose (cm)": 15,
            "Sucker Size (FG)": 10
        }
    elif weight < 12:
        return {
            "Age": "2-3 years",
            "Internal Diameter (mm)": 5.0,
            "External Diameter (mm)": 6.9,
            "Length at Lip (cm)": 14,
            "Length at Nose (cm)": 16,
            "Sucker Size (FG)": 10
        }
    elif weight < 14:
        return {
            "Age": "3-4 years",
            "Internal Diameter (mm)": 5.5,
            "External Diameter (mm)": 7.5,
            "Length at Lip (cm)": 15,
            "Length at Nose (cm)": 17,
            "Sucker Size (FG)": 12
        }
    elif weight < 16:
        return {
            "Age": "4-5 years",
            "Internal Diameter (mm)": 6.0,
            "External Diameter (mm)": 8.2,
            "Length at Lip (cm)": 16,
            "Length at Nose (cm)": 18,
            "Sucker Size (FG)": 14
        }
    else:
        return {
            "Age": "5+ years",
            "Internal Diameter (mm)": 6.5,
            "External Diameter (mm)": 8.9,
            "Length at Lip (cm)": 17,
            "Length at Nose (cm)": 19,
            "Sucker Size (FG)": 14
        }

def calculate_doses(weight, category):
    """ Returns calculated drug doses based on weight, capped at max dose if available """
    if category not in drug_data:
        return {}

    calculated_doses = {}
    
    if category == "rsi_ett_drugs":
        # Handle RSI ETT drugs with categories
        for category_name, drugs in drug_data[category].items():
            for drug, details in drugs.items():
                if isinstance(details['dose_per_kg'], list):
                    # Handle range-based dosing
                    min_dose = weight * details['dose_per_kg'][0]
                    max_dose = weight * details['dose_per_kg'][1]
                    min_dose = min(min_dose, details.get('max_dose', min_dose))
                    max_dose = min(max_dose, details.get('max_dose', max_dose))
                    
                    # Special handling for Fentanyl (convert to micrograms)
                    if drug == 'Fentanyl':
                        min_dose *= 1000  # Convert mg to mcg
                        max_dose *= 1000
                        calculated_doses[f"{category_name.replace('_', ' ').title()} - {drug}"] = f"{round(min_dose, 1)}-{round(max_dose, 1)}mcg {details['frequency']} {details['route']}"
                    else:
                        calculated_doses[f"{category_name.replace('_', ' ').title()} - {drug}"] = f"{round(min_dose, 2)}-{round(max_dose, 2)}mg {details['frequency']} {details['route']}"
                else:
                    # Handle single value dosing
                    dose = weight * details['dose_per_kg']
                    dose = min(dose, details.get('max_dose', dose))
                    calculated_doses[f"{category_name.replace('_', ' ').title()} - {drug}"] = f"{round(dose, 2)}mg {details['frequency']} {details['route']}"
    else:
        # Handle other categories as before
        for drug, details in drug_data[category].items():
            if 'dose_per_kg' in details:
                raw_dose = weight * details["dose_per_kg"]
                dose = min(raw_dose, details.get("max_dose", raw_dose))
            elif 'fixed_dose' in details:
                dose = details['fixed_dose'][10] if weight <= 10 else details['fixed_dose'][20]
            else:
                dose = 0

            calculated_doses[drug] = f"{round(dose, 2)}mg {details['frequency']} {details['route']}"

    if category == "all_drugs":
        calculated_doses = dict(sorted(calculated_doses.items()))

    return calculated_doses

def calculate_meningitis_doses(weight):
    """Calculate drug doses for meningitis treatment based on weight"""
    doses = {}
    
    # Ceftriaxone calculation (50mg/kg twice daily)
    # Using 1g/10ml preparation
    ceftriaxone_ml = weight * 50 / 100  # Convert to ml (1g/10ml = 100mg/ml)
    if weight < 3:
        doses['ceftriaxone_dose'] = "Consult specialist"
    elif weight <= 29.9:
        doses['ceftriaxone_dose'] = f"{ceftriaxone_ml:.1f}"
    else:
        doses['ceftriaxone_dose'] = "13.0"  # Maximum dose
    
    # Chloramphenicol calculation (25mg/kg every 6 hours)
    chloramphenicol_mg = weight * 25
    doses['chloramphenicol_dose'] = f"{chloramphenicol_mg:.1f}"
    
    # Benzyl Penicillin (crystalline) calculation
    benzylpen_units = weight * 50000  # Typical pediatric dose
    doses['benzylpen_dose'] = f"{benzylpen_units:,.0f}"
    
    # Phenobarbitone dosing
    if weight < 6:
        doses['phenobarb_loading'] = "¼ ml IM or 2 tabs"
        doses['phenobarb_maintenance'] = "½ tab"
    elif weight < 10:
        doses['phenobarb_loading'] = "½ ml IM or 3 tabs"
        doses['phenobarb_maintenance'] = "1 tab"
    elif weight < 15:
        doses['phenobarb_loading'] = "¾ ml IM or 5 tabs"
        doses['phenobarb_maintenance'] = "2 tabs"
    elif weight < 20:
        doses['phenobarb_loading'] = "1 ml IM or 6 tabs"
        doses['phenobarb_maintenance'] = "3 tabs"
    elif weight < 30:
        doses['phenobarb_loading'] = "1 ml IM or 7 tabs"
        doses['phenobarb_maintenance'] = "4 tabs"
    else:
        doses['phenobarb_loading'] = "1 ml IM or 7 tabs"
        doses['phenobarb_maintenance'] = "Consult specialist"
    
    # Flucloxacillin for skin sepsis (50mg/kg QID)
    fluclox_mg = min(weight * 50, 500)  # max 500mg per dose
    doses['fluclox_dose'] = f"{fluclox_mg:.0f}"
    
    return doses

def calculate_resuscitation_doses(weight):
    """Calculate drug doses for resuscitation based on weight"""
    doses = {}
    
    # Adrenaline calculation (0.1ml/kg of 1:10000 solution)
    # Using 1:1000 solution diluted 1:10
    adrenaline_ml = weight * 0.1
    doses['adrenaline_dose'] = f"{adrenaline_ml:.1f}"
    
    # Narcan calculation (0.1ml/kg of 0.4mg/ml solution)
    narcan_ml = weight * 0.1
    doses['narcan_dose'] = f"{narcan_ml:.1f}"
    
    # Dextrose calculation (5ml/kg of 10% solution)
    dextrose_ml = weight * 5
    doses['dextrose_dose'] = f"{dextrose_ml:.1f}"
    
    return doses

def calculate_rheumatic_fever_doses(weight):
    """Calculate drug doses for rheumatic fever treatment based on weight"""
    doses = {}
    
    # Aspirin calculation (25mg/kg every 6 hours)
    aspirin_mg = weight * 25
    doses['aspirin_dose'] = f"{aspirin_mg:.1f}"
    
    # Reduced aspirin dose (12.5mg/kg every 6 hours)
    reduced_aspirin_mg = weight * 12.5
    doses['reduced_aspirin_dose'] = f"{reduced_aspirin_mg:.1f}"
    
    # Frusemide calculation (1mg/kg 6 hourly)
    frusemide_mg = weight * 1
    doses['frusemide_dose'] = f"{frusemide_mg:.1f}"
    
    # Digoxin calculation (10 microgram/kg daily)
    digoxin_mcg = weight * 10
    doses['digoxin_dose'] = f"{digoxin_mcg:.1f}"
    
    # Prednisolone calculation (1mg/kg/day)
    prednisolone_mg = weight * 1
    doses['prednisolone_dose'] = f"{prednisolone_mg:.1f}"
    
    # Benzathine penicillin calculation (37.5mg/kg IM, max 900mg)
    benzathine_mg = min(weight * 37.5, 900)
    doses['benzathine_dose'] = f"{benzathine_mg:.1f}"
    
    return doses

def calculate_snake_bite_doses(weight):
    """Calculate drug doses for snake bite treatment based on weight"""
    doses = {}
    
    # Adrenaline calculation (1:1000 diluted to 2.5ml)
    doses['adrenaline_dose'] = "0.25ml (diluted to 2.5ml)"
    
    # Antivenom dose based on weight
    if weight < 11:
        doses['antivenom_dose'] = "1.0"
    elif weight <= 15:
        doses['antivenom_dose'] = "1.5"
    else:
        doses['antivenom_dose'] = "2.0"
    
    return doses

def calculate_typhoid_doses(weight):
    """Calculate drug doses for typhoid treatment based on weight"""
    doses = {}
    
    # Chloramphenicol calculation (25mg/kg every 6 hours)
    chloramphenicol_mg = weight * 25
    doses['chloramphenicol_dose'] = f"{chloramphenicol_mg:.1f}"
    
    # Ciprofloxacin calculation (15mg/kg twice daily)
    ciprofloxacin_mg = weight * 15
    doses['ciprofloxacin_dose'] = f"{ciprofloxacin_mg:.1f}"
    
    # Amoxicillin calculation (25mg/kg every 6 hours, max 500mg)
    amoxicillin_mg = min(weight * 25, 500)
    doses['amoxicillin_dose'] = f"{amoxicillin_mg:.1f}"
    
    # Cotrimoxazole calculation (20mg/kg twice daily)
    cotrimoxazole_mg = weight * 20
    doses['cotrimoxazole_dose'] = f"{cotrimoxazole_mg:.1f}"
    
    return doses

def calculate_yaws_doses(weight):
    """Calculate drug doses for yaws treatment based on weight"""
    doses = {}
    
    # Azithromycin calculation (30mg/kg stat)
    azithromycin_mg = weight * 30
    doses['azithromycin_dose'] = f"{azithromycin_mg:.1f}"
    
    # Benzathine penicillin dose based on weight ranges
    if weight < 10:
        doses['benzathine_dose'] = "1.0"
    elif weight < 20:
        doses['benzathine_dose'] = "2.0"
    elif weight < 30:
        doses['benzathine_dose'] = "3.0"
    elif weight < 40:
        doses['benzathine_dose'] = "4.0"
    else:
        doses['benzathine_dose'] = "5.0"
    
    return doses

def calculate_osteomyelitis_doses(weight):
    """Calculate drug doses for osteomyelitis treatment based on weight"""
    doses = {}
    
    # Flucloxacillin/Cloxacillin calculation (50mg/kg every 6 hours)
    fluclox_mg = min(weight * 50, 500)  # max 500mg per dose
    doses['fluclox_dose'] = f"{fluclox_mg:.1f}"
    
    # Chloramphenicol calculation (25mg/kg every 6 hours)
    chloramphenicol_mg = weight * 25
    doses['chloramphenicol_dose'] = f"{chloramphenicol_mg:.1f}"
    
    return doses

def calculate_pigbel_doses(weight):
    """Calculate drug doses for pigbel treatment based on weight"""
    doses = {}
    
    # Albendazole calculation (single dose)
    albendazole_mg = weight * 15  # 15mg/kg single dose
    doses['albendazole_dose'] = f"{albendazole_mg:.1f}"
    
    # Tinidazole calculation (single dose)
    tinidazole_mg = weight * 50  # 50mg/kg single dose
    doses['tinidazole_dose'] = f"{tinidazole_mg:.1f}"
    
    # Chloramphenicol calculation (25mg/kg every 6 hours)
    chloramphenicol_mg = weight * 25
    doses['chloramphenicol_dose'] = f"{chloramphenicol_mg:.1f}"
    
    # IV fluid rate calculation
    if weight < 6:
        doses['iv_rate'] = "25ml/hour (7 drops/min)"
    elif weight < 10:
        doses['iv_rate'] = "50ml/hour (13 drops/min)"
    elif weight < 15:
        doses['iv_rate'] = "75ml/hour (20 drops/min)"
    else:
        doses['iv_rate'] = "100ml/hour (25 drops/min)"
    
    return doses

def calculate_parkland_formula(weight, tbsa):
    """Calculate fluid requirements using Parkland formula for burns"""
    # For children: 3ml x %TBSA x weight(kg)
    total_volume = 3 * tbsa * weight
    
    # First 8 hours: 50% of total volume
    first_8_hours = total_volume * 0.5
    first_8_hours_rate = first_8_hours / 8  # ml per hour
    
    # Next 16 hours: remaining 50%
    next_16_hours = total_volume * 0.5
    next_16_hours_rate = next_16_hours / 16  # ml per hour
    
    return total_volume, first_8_hours, first_8_hours_rate, next_16_hours, next_16_hours_rate

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        weight_str = request.form.get("weight", "")
        calc_type = request.form.get("calc_type")
        tbsa_str = request.form.get("tbsa", "")

        if not weight_str:
            flash("Please enter a weight value.")
            return render_template("index.html")
        
        if not calc_type:
            flash("Please select a calculation type.")
            return render_template("index.html")

        try:
            weight = float(weight_str)
            tbsa = float(tbsa_str) if tbsa_str else None

            if tbsa is not None and (tbsa < 0 or tbsa > 100):
                raise ValueError("TBSA must be between 0 and 100")

            if weight <= 0 or weight > 150:
                raise ValueError
        except ValueError:
            flash("Invalid input. Please enter a valid number for weight.")
            return render_template("index.html")

        # Perform calculations based on selection
        doses = calculate_doses(weight, calc_type)
        bolus_fluids, maintenance_rate, two_thirds_maintenance_rate, parkland_data = {}, None, None, None
        ett_info = None

        if calc_type in ["common", "emergency", "rsi_ett_drugs"]:
            bolus_fluids, maintenance_rate, two_thirds_maintenance_rate = calculate_fluids(weight)

        if calc_type == "rsi_ett_drugs":
            ett_info = calculate_ett_size(weight)

        if calc_type == "emergency" and tbsa:
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
            bolus_fluids=bolus_fluids if calc_type in ["common", "emergency", "rsi_ett_drugs"] else None, 
            maintenance_rate=maintenance_rate if calc_type in ["common", "emergency", "rsi_ett_drugs"] else None, 
            two_thirds_maintenance_rate=two_thirds_maintenance_rate if calc_type in ["common", "emergency", "rsi_ett_drugs"] else None, 
            parkland_data=parkland_data,
            ett_info=ett_info,
            weight=weight, 
            calc_type=calc_type
        )
    
    return render_template("index.html")

@app.route("/disease", methods=["GET", "POST"])
def disease():
    categories = {
        "Assessment Tools and Protocols": [
            "Checklist for infants: less than 2 months",
            "Checklist for sick children: 2 months - 5 years",
            "Dose and site of vaccines",
            "Immunisation",
            "Paediatric rules",
            "PNG immunization schedule"
        ],
        "Emergency and Critical Care": [
            "Burns and scalds",
            "Child abuse and rape treatment",
            "Convulsions",
            "Meningitis or severe sepsis",
            "Poisoning",
            "Resuscitation",
            "Snake bite"
        ],
        "Infections and Fever": [
            "Fever",
            "HIV infection",
            "HIV - Prevention of HIV infection in children",
            "Malaria",
            "Measles",
            "Multi-drug resistant (MDR) TB",
            "Pulmonary TB",
            "Sexually transmitted infections (STIs)",
            "Tuberculosis",
            "Typhoid"
        ],
        "Respiratory System": [
            "Asthma",
            "Colds and URTI",
            "Pertussis (Whooping cough)",
            "Pneumonia or bronchiolitis"
        ],
        "Gastrointestinal System": [
            "Diarrhoea - Bloody (dysentery)",
            "Diarrhoea - Lasting more than 7 days",
            "Diarrhoea - Mild",
            "Diarrhoea - Moderate",
            "Diarrhoea - Severe",
            "Diarrhoea due to cholera",
            "Pigbel"
        ],
        "Nutrition": [
            "Anaemia",
            "Breastfeeding and nutrition",
            "Malnutrition - Diagnosis",
            "Malnutrition - Inpatient treatment",
            "Medicine for mothers to take home",
            "Milk mixtures",
            "Moderate malnutrition: summary",
            "Oedema (swelling)",
            "Severe malnutrition: summary"
        ],
        "Neonatal Care": [
            "Babies – Born Before Arrival (BBA)",
            "Babies less than 2.2kg weight",
            "Babies – Drug doses: for babies less than 4 weeks of age",
            "Babies – Neonatal infections"
        ],
        "ENT and Eye": [
            "Conjunctivitis",
            "Lymph gland enlargement",
            "Otitis media - Acute",
            "Otitis media - Chronic"
        ],
        "Other Conditions": [
            "Osteomyelitis, septic arthritis, and pyomyositis",
            "Rheumatic fever and rheumatic heart disease",
            "Skin diseases",
            "Urinary symptoms",
            "Yaws"
        ],
        "Dosage and Fluid Calculations": [
            "IV and oral fluid calculation (using either Paediatric or Adult burette)",
            "Tables of drug doses"
        ]
    }

    if request.method == "POST":
        disease = request.form.get("disease")
        return redirect(url_for('disease_page', disease=disease))

    return render_template("disease.html", categories=categories)

@app.route("/disease/<disease>")
def disease_page(disease):
    management_protocol = disease_data.get(disease, "No management details available for this condition.")
    return render_template('disease_page.html', disease=disease, management_protocol=management_protocol)

@app.route("/calculate_meningitis", methods=["POST"])
def calculate_meningitis():
    try:
        weight = float(request.form.get("weight", 0))
        if weight <= 0 or weight > 150:
            flash("Please enter a valid weight between 0 and 150 kg")
            return redirect(url_for('disease_page', disease="Meningitis or severe sepsis"))
        
        doses = calculate_meningitis_doses(weight)
        
        # Get the base management protocol
        management_protocol = disease_data["Meningitis or severe sepsis"]
        
        # Generate the calculator results HTML
        calculator_results = f"""
        <div class="calculator-results mb-4">
            <h4>Calculated doses for {weight}kg:</h4>
            <ul class="list-unstyled">
                <li>• Ceftriaxone {doses['ceftriaxone_dose']}ml IV/IM twice daily</li>
                <li>• Chloramphenicol {doses['chloramphenicol_dose']}mg IV/IM 6 hourly</li>
                <li>• Benzyl Penicillin {doses['benzylpen_dose']} units IM 3 hourly</li>
                <li>• Phenobarbitone: {doses['phenobarb_loading']} then {doses['phenobarb_maintenance']} daily</li>
                <li>• Flucloxacillin {doses['fluclox_dose']}mg IV/IM/oral QID</li>
            </ul>
            <hr>
        </div>
        """
        
        # Insert calculator results after the calculator form
        insert_point = '<button type="submit" class="btn btn-primary mt-2">Calculate Doses</button>\n                </form>\n            </div>'
        modified_protocol = management_protocol.replace(insert_point, f'{insert_point}\n            {calculator_results}')
        
        return render_template('disease_page.html',
                             disease="Meningitis or severe sepsis",
                             management_protocol=modified_protocol)
    
    except ValueError:
        flash("Please enter a valid number for weight")
        return redirect(url_for('disease_page', disease="Meningitis or severe sepsis"))

@app.route("/calculate_resuscitation", methods=["POST"])
def calculate_resuscitation():
    try:
        weight = float(request.form.get("weight", 0))
        if weight <= 0 or weight > 150:
            flash("Please enter a valid weight between 0 and 150 kg")
            return redirect(url_for('disease_page', disease="Resuscitation"))
        
        doses = calculate_resuscitation_doses(weight)
        
        # Get the base management protocol
        management_protocol = disease_data["Resuscitation"]
        
        # Generate the calculator results HTML
        calculator_results = f"""
        <div class="calculator-results mb-4">
            <h4>Calculated doses for {weight}kg:</h4>
            <ul class="list-unstyled">
                <li>• Adrenaline (1:10000) {doses['adrenaline_dose']}ml IV/IM/ETT</li>
                <li>• Narcan {doses['narcan_dose']}ml IV/IM/sublingual</li>
                <li>• 10% Dextrose {doses['dextrose_dose']}ml IV over 5 minutes</li>
            </ul>
            <hr>
        </div>
        """
        
        # Insert calculator results after the calculator form
        insert_point = '<button type="submit" class="btn btn-primary mt-2">Calculate Doses</button>\n                </form>\n            </div>'
        modified_protocol = management_protocol.replace(insert_point, f'{insert_point}\n            {calculator_results}')
        
        return render_template('disease_page.html',
                             disease="Resuscitation",
                             management_protocol=modified_protocol)
    
    except ValueError:
        flash("Please enter a valid number for weight")
        return redirect(url_for('disease_page', disease="Resuscitation"))

@app.route("/calculate_rheumatic_fever", methods=["POST"])
def calculate_rheumatic_fever():
    try:
        weight = float(request.form.get("weight", 0))
        if weight <= 0 or weight > 150:
            flash("Please enter a valid weight between 0 and 150 kg")
            return redirect(url_for('disease_page', disease="Rheumatic fever and rheumatic heart disease"))
        
        doses = calculate_rheumatic_fever_doses(weight)
        
        # Get the base management protocol
        management_protocol = disease_data["Rheumatic fever and rheumatic heart disease"]
        
        # Generate the calculator results HTML
        calculator_results = f"""
        <div class="calculator-results mb-4">
            <h4>Calculated doses for {weight}kg:</h4>
            <ul class="list-unstyled">
                <li>• Aspirin {doses['aspirin_dose']}mg every 6 hours (until fever subsides)</li>
                <li>• Reduced Aspirin {doses['reduced_aspirin_dose']}mg every 6 hours (after fever subsides)</li>
                <li>• Frusemide {doses['frusemide_dose']}mg 6 hourly (if in heart failure)</li>
                <li>• Digoxin {doses['digoxin_dose']}mcg daily (if in heart failure)</li>
                <li>• Prednisolone {doses['prednisolone_dose']}mg daily (if severe heart failure)</li>
                <li>• Benzathine Penicillin {doses['benzathine_dose']}mg IM monthly (prophylaxis)</li>
            </ul>
            <hr>
        </div>
        """
        
        # Insert calculator results after the calculator form
        insert_point = '<button type="submit" class="btn btn-primary mt-2">Calculate Doses</button>\n                </form>\n            </div>'
        modified_protocol = management_protocol.replace(insert_point, f'{insert_point}\n            {calculator_results}')
        
        return render_template('disease_page.html',
                             disease="Rheumatic fever and rheumatic heart disease",
                             management_protocol=modified_protocol)
    
    except ValueError:
        flash("Please enter a valid number for weight")
        return redirect(url_for('disease_page', disease="Rheumatic fever and rheumatic heart disease"))

@app.route("/calculate_snake_bite", methods=["POST"])
def calculate_snake_bite():
    try:
        weight = float(request.form.get("weight", 0))
        if weight <= 0 or weight > 150:
            flash("Please enter a valid weight between 0 and 150 kg")
            return redirect(url_for('disease_page', disease="Snake bite"))
        
        doses = calculate_snake_bite_doses(weight)
        
        # Get the base management protocol
        management_protocol = disease_data["Snake bite"]
        
        # Generate the calculator results HTML
        calculator_results = f"""
        <div class="calculator-results mb-4">
            <h4>Calculated doses for {weight}kg:</h4>
            <ul class="list-unstyled">
                <li>• Adrenaline (1:1000) {doses['adrenaline_dose']} SC/IM</li>
                <li>• Snake Antivenom {doses['antivenom_dose']} vial(s) in 100ml IV fluid over 30-60 minutes</li>
            </ul>
            <hr>
        </div>
        """
        
        # Insert calculator results after the calculator form
        insert_point = '<button type="submit" class="btn btn-primary mt-2">Calculate Doses</button>\n                </form>\n            </div>'
        modified_protocol = management_protocol.replace(insert_point, f'{insert_point}\n            {calculator_results}')
        
        return render_template('disease_page.html',
                             disease="Snake bite",
                             management_protocol=modified_protocol)
    
    except ValueError:
        flash("Please enter a valid number for weight")
        return redirect(url_for('disease_page', disease="Snake bite"))

@app.route("/calculate_typhoid", methods=["POST"])
def calculate_typhoid():
    try:
        weight = float(request.form.get("weight", 0))
        if weight <= 0 or weight > 150:
            flash("Please enter a valid weight between 0 and 150 kg")
            return redirect(url_for('disease_page', disease="Typhoid"))
        
        doses = calculate_typhoid_doses(weight)
        
        # Get the base management protocol
        management_protocol = disease_data["Typhoid"]
        
        # Generate the calculator results HTML
        calculator_results = f"""
        <div class="calculator-results mb-4">
            <h4>Calculated doses for {weight}kg:</h4>
            <ul class="list-unstyled">
                <li>• Chloramphenicol {doses['chloramphenicol_dose']}mg 6 hourly (first line)</li>
                <li>• Ciprofloxacin {doses['ciprofloxacin_dose']}mg twice daily (if not responding to CMP)</li>
                <li>• Amoxicillin {doses['amoxicillin_dose']}mg 6 hourly (alternative)</li>
                <li>• Cotrimoxazole {doses['cotrimoxazole_dose']}mg twice daily (alternative)</li>
            </ul>
            <hr>
        </div>
        """
        
        # Insert calculator results after the calculator form
        insert_point = '<button type="submit" class="btn btn-primary mt-2">Calculate Doses</button>\n                </form>\n            </div>'
        modified_protocol = management_protocol.replace(insert_point, f'{insert_point}\n            {calculator_results}')
        
        return render_template('disease_page.html',
                             disease="Typhoid",
                             management_protocol=modified_protocol)
    
    except ValueError:
        flash("Please enter a valid number for weight")
        return redirect(url_for('disease_page', disease="Typhoid"))

@app.route("/calculate_yaws", methods=["POST"])
def calculate_yaws():
    try:
        weight = float(request.form.get("weight", 0))
        if weight <= 0 or weight > 150:
            flash("Please enter a valid weight between 0 and 150 kg")
            return redirect(url_for('disease_page', disease="Yaws"))
        
        doses = calculate_yaws_doses(weight)
        
        # Get the base management protocol
        management_protocol = disease_data["Yaws"]
        
        # Generate the calculator results HTML
        calculator_results = f"""
        <div class="calculator-results mb-4">
            <h4>Calculated doses for {weight}kg:</h4>
            <ul class="list-unstyled">
                <li>• Azithromycin {doses['azithromycin_dose']}mg oral stat</li>
                <li>• Benzathine Penicillin {doses['benzathine_dose']}ml IM stat</li>
            </ul>
            <hr>
        </div>
        """
        
        # Insert calculator results after the calculator form
        insert_point = '<button type="submit" class="btn btn-primary mt-2">Calculate Doses</button>\n                </form>\n            </div>'
        modified_protocol = management_protocol.replace(insert_point, f'{insert_point}\n            {calculator_results}')
        
        return render_template('disease_page.html',
                             disease="Yaws",
                             management_protocol=modified_protocol)
    
    except ValueError:
        flash("Please enter a valid number for weight")
        return redirect(url_for('disease_page', disease="Yaws"))

@app.route("/calculate_osteomyelitis", methods=["POST"])
def calculate_osteomyelitis():
    try:
        weight = float(request.form.get("weight", 0))
        if weight <= 0 or weight > 150:
            flash("Please enter a valid weight between 0 and 150 kg")
            return redirect(url_for('disease_page', disease="Osteomyelitis, septic arthritis, and pyomyositis"))
        
        doses = calculate_osteomyelitis_doses(weight)
        
        # Get the base management protocol
        management_protocol = disease_data["Osteomyelitis, septic arthritis, and pyomyositis"]
        
        # Generate the calculator results HTML
        calculator_results = f"""
        <div class="calculator-results mb-4">
            <h4>Calculated doses for {weight}kg:</h4>
            <ul class="list-unstyled">
                <li>• Flucloxacillin/Cloxacillin {doses['fluclox_dose']}mg every 6 hours</li>
                <li>• Chloramphenicol {doses['chloramphenicol_dose']}mg every 6 hours (if flucloxacillin not available)</li>
            </ul>
            <hr>
        </div>
        """
        
        # Insert calculator results after the calculator form
        insert_point = '<button type="submit" class="btn btn-primary mt-2">Calculate Doses</button>\n                </form>\n            </div>'
        modified_protocol = management_protocol.replace(insert_point, f'{insert_point}\n            {calculator_results}')
        
        return render_template('disease_page.html',
                             disease="Osteomyelitis, septic arthritis, and pyomyositis",
                             management_protocol=modified_protocol)
    
    except ValueError:
        flash("Please enter a valid number for weight")
        return redirect(url_for('disease_page', disease="Osteomyelitis, septic arthritis, and pyomyositis"))

@app.route("/calculate_pigbel", methods=["POST"])
def calculate_pigbel():
    try:
        weight = float(request.form.get("weight", 0))
        if weight <= 0 or weight > 150:
            flash("Please enter a valid weight between 0 and 150 kg")
            return redirect(url_for('disease_page', disease="Pigbel"))
        
        doses = calculate_pigbel_doses(weight)
        
        # Get the base management protocol
        management_protocol = disease_data["Pigbel"]
        
        # Generate the calculator results HTML
        calculator_results = f"""
        <div class="calculator-results mb-4">
            <h4>Calculated doses for {weight}kg:</h4>
            <ul class="list-unstyled">
                <li>• IV Fluid Rate: {doses['iv_rate']}</li>
                <li>• Albendazole: {doses['albendazole_dose']}mg single dose</li>
                <li>• Tinidazole: {doses['tinidazole_dose']}mg single dose (if malnourished)</li>
                <li>• Chloramphenicol: {doses['chloramphenicol_dose']}mg every 6 hours (if severe)</li>
            </ul>
            <hr>
        </div>
        """
        
        # Insert calculator results after the calculator form
        insert_point = '<button type="submit" class="btn btn-primary mt-2">Calculate Doses</button>\n                </form>\n            </div>'
        modified_protocol = management_protocol.replace(insert_point, f'{insert_point}\n            {calculator_results}')
        
        return render_template('disease_page.html',
                             disease="Pigbel",
                             management_protocol=modified_protocol)
    
    except ValueError:
        flash("Please enter a valid number for weight")
        return redirect(url_for('disease_page', disease="Pigbel"))

@app.route("/calculate_burns", methods=["POST"])
def calculate_burns():
    try:
        weight = float(request.form.get("weight", 0))
        tbsa = float(request.form.get("tbsa", 0))
        
        if weight <= 0 or weight > 150:
            flash("Please enter a valid weight between 0 and 150 kg")
            return redirect(url_for('disease_page', disease="Burns and scalds"))
            
        if tbsa <= 0 or tbsa > 100:
            flash("Please enter a valid TBSA between 0 and 100%")
            return redirect(url_for('disease_page', disease="Burns and scalds"))
        
        total_volume, first_8_hours, first_8_hours_rate, next_16_hours, next_16_hours_rate = calculate_parkland_formula(weight, tbsa)
        
        # Get the base management protocol
        management_protocol = disease_data["Burns and scalds"]
        
        # Generate the calculator results HTML
        calculator_results = f"""
        <div class="calculator-results mb-4">
            <h4>Parkland Formula Calculations for {weight}kg with {tbsa}% TBSA:</h4>
            <div class="table-responsive">
                <table class="table table-bordered">
                    <thead>
                        <tr>
                            <th>Time Period</th>
                            <th>Volume (ml)</th>
                            <th>Rate (ml/hour)</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>First 8 hours</td>
                            <td>{first_8_hours:.1f}</td>
                            <td>{first_8_hours_rate:.1f}</td>
                        </tr>
                        <tr>
                            <td>Next 16 hours</td>
                            <td>{next_16_hours:.1f}</td>
                            <td>{next_16_hours_rate:.1f}</td>
                        </tr>
                        <tr>
                            <td><strong>Total 24 hours</strong></td>
                            <td><strong>{total_volume:.1f}</strong></td>
                            <td>-</td>
                        </tr>
                    </tbody>
                </table>
            </div>
            <div class="alert alert-info">
                <strong>Note:</strong> This is the initial fluid requirement. Adjust based on clinical response and urine output.
            </div>
            <hr>
        </div>
        """
        
        # Insert calculator results after the calculator form
        insert_point = '<button type="submit" class="btn btn-success mt-2">Calculate Fluid Requirements</button>\n                </form>\n            </div>'
        modified_protocol = management_protocol.replace(insert_point, f'{insert_point}\n            {calculator_results}')
        
        return render_template('disease_page.html',
                             disease="Burns and scalds",
                             management_protocol=modified_protocol)
    
    except ValueError:
        flash("Please enter valid numbers for weight and TBSA")
        return redirect(url_for('disease_page', disease="Burns and scalds"))

@app.after_request
def add_header(response):
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
