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
    for drug, details in drug_data[category].items():
        if 'dose_per_kg' in details:
            raw_dose = weight * details["dose_per_kg"]
            dose = min(raw_dose, details.get("max_dose", raw_dose))  # Cap at max dose if present
        elif 'fixed_dose' in details:
            dose = details['fixed_dose'][10] if weight <= 10 else details['fixed_dose'][20]
        else:
            dose = 0

        calculated_doses[drug] = f"{round(dose, 2)}mg {details['frequency']} {details['route']}"

    if category == "all_drugs":
        calculated_doses = dict(sorted(calculated_doses.items()))  # Sort alphabetically

    return calculated_doses

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
