from flask import Flask, request, render_template_string

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        try:
            weight = float(request.form["weight"])
            doses = calculate_doses(weight)
            bolus_fluids, maintenance_rate, two_thirds_maintenance_rate = calculate_fluids(weight)
            return render_template_string("""
                 <style>
                    body {
                        font-family: Arial, sans-serif;
                    }
                </style>
                <h1>PNG Common Drug Doses and Fluid Rate Calculator</h1>
                <h2>Child's Weight: {{ weight }} kg</h2>
                <h1>Drug Doses (mg)</h1>
                <ul>
                {% for drug, dose in doses.items() %}
                    <li>{{ drug }}: {{ dose }} mg</li>
                {% endfor %}
                </ul>
                <h1>Fluid Requirements</h1>
                <ul>
                {% for bolus, volume in bolus_fluids.items() %}
                    <li>{{ bolus }}: {{ volume }} mL</li>
                {% endfor %}
                </ul>
                <p>Maintenance Rate (4:2:1 Rule): {{ maintenance_rate }} mL/hour</p>
                <p>Two Thirds Maintenance Rate (⅔ MR): {{ two_thirds_maintenance_rate }} mL/hour</p>
                <p>Use ⅔ MR for patients having severe malnutrition, heart failure, meningitis or head injury    
                <p><strong><a href="/">Go back</a></strong></p>
                <footer>
                    <p>&copy; 2024 Lincoln Kumbeli - still under development so use at your own risk</p>
                </footer>
            """, doses=doses, bolus_fluids=bolus_fluids, maintenance_rate=maintenance_rate, two_thirds_maintenance_rate=two_thirds_maintenance_rate, weight = weight)
        except ValueError:
            return "Invalid input. Please enter a valid number."
    return render_template_string("""
        <style>
            body {
                font-family: Arial, sans-serif;
            }
        </style>
        <h1>PNG Common Drug Doses and Fluid Rate Calculator</h1>
        <form method="post">
            Enter the child's weight in kg: <input type="text" name="weight">
            <input type="submit" value="Calculate">
        </form>
              <footer>
            <p>&copy; 2024 Lincoln Kumbeli - still under development so use at your own risk</p>
        </footer>                    
    """)

def calculate_doses(weight):
    doses = {
        "Amoxicillin, Flucloxacillin, Chloramphenicol (25mg/kg)": 25 * weight,
        "Ceftriaxone (50mg/kg)": 50 * weight,
        "Lasix (1mg/kg)": 1 * weight,
        "Lasix (0.5mg/kg)": 0.5 * weight,
        "Hydrocortisone (4mg/kg)": 4 * weight,
        "Flagyl (7.5mg/kg)": 7.5 * weight,
        "Paracetamol (15mg/kg)": 15 * weight,
        "Crystapen (30mg/kg)": 30 * weight,
        "Gentamicin (5mg/kg)": 5 * weight,
    
    }
    return doses

def calculate_fluids(weight):
    bolus_fluids = {
        "Bolus (10mL/kg)": 10 * weight,
        "Bolus (15mL/kg)": 15 * weight,
        "Bolus (20mL/kg)": 20 * weight
    }

    if weight <= 10:
        maintenance_rate = 4 * weight
    elif weight <= 30:
        maintenance_rate = (4 * 10) + (2 * (weight - 10))
    else:
        maintenance_rate = (4 * 10) + (2 * 20) + (1 * (weight - 30))

    two_thirds_maintenance_rate = round(maintenance_rate * 2 / 3, 1)
    
    return bolus_fluids, maintenance_rate, two_thirds_maintenance_rate

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)