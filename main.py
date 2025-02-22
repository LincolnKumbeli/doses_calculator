from flask import Flask, request, render_template, url_for, redirect, flash
from collections import OrderedDict

# Import disease data from a separate file
try:
    from disease_content import disease_data
except ModuleNotFoundError:
    print("⚠️ ERROR: 'disease_content.py' file is missing or not found. Ensure it is in the same directory as 'main.py'.")

app = Flask(__name__, 
    static_folder='static',
    template_folder='templates'
)
app.secret_key = 'your_secret_key_here'

# Disable template caching
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        weight_str = request.form.get("weight", "")
        calc_type = request.form.get("calc_type")

        if not weight_str:
            flash("Please enter a weight value.")
            return render_template("index.html")
        
        if not calc_type:
            flash("Please select a calculation type.")
            return render_template("index.html")

        try:
            weight = float(weight_str)
            if weight <= 0 or weight > 150:
                raise ValueError
        except ValueError:
            flash("Invalid input. Please enter a valid number for weight.")
            return render_template("index.html")

        return render_template("index.html", weight=weight, calc_type=calc_type)
    else:
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
