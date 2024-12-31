from flask import request, render_template, url_for, redirect
from app import app

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        weight_str = request.form["weight"]
        calc_type = request.form.get("calc_type")

        # Input validation (check for weight as a number)
        if not calc_type:
            error_message = "Please select a calculation type."
        else:
            try:
                weight = float(weight_str)
            except ValueError:
                return "Invalid input. Please enter a valid number for weight."

            # Perform calculations based on selection
            if calc_type == "common":
                doses = calculate_doses(weight)
                bolus_fluids, maintenance_rate, two_thirds_maintenance_rate = calculate_fluids(weight)
            elif calc_type == "emergency":
                # Weight-based emergency drug calculations
                doses = {
                    "Drugs": {
                        "Suxamethonium (1-2mg/kg)": f"{round(1 * weight, 2)} to {round(2 * weight, 2)}",
                        "Emergency Drug A (0.1mg/kg)": round(0.1 * weight, 2),
                        "Emergency Drug B (0.2mg/kg)": round(0.2 * weight, 2),
                        # Add more weight-based emergency drugs as needed
                    },
                    "RSI and ETT": {
                        "Drugs": {
                            "RSI Drug A (0.3mg/kg)": round(0.3 * weight, 2),
                            "RSI Drug B (0.4mg/kg)": round(0.4 * weight, 2),
                            # Add more RSI drugs as needed
                        },
                        "ETT Size and Length": {
                            "ETT Size": round(weight / 10, 1),  # Example calculation
                            "ETT Length": round(weight / 5, 1),  # Example calculation
                        }
                    }
                }
                bolus_fluids, maintenance_rate, two_thirds_maintenance_rate = calculate_fluids(weight)
            else:
                return "Invalid calculation type."

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
            return "Invalid input. Please enter a valid number for weight."

        if disease == "Disease 1":
            doses = {"Disease 1 Drug A": weight * 2, "Disease 1 Drug B": weight * 1.5}
        elif disease == "Disease 2":
            doses = {"Disease 2 Drug A": weight * 3, "Disease 2 Drug B": weight * 2}
        else:
            return "Invalid disease selection."

        return render_template("disease.html", doses=doses, weight=weight)
    else:
        return render_template("disease.html")

def calculate_doses(weight):
    doses = {
        "Adrenaline infusion  (0.15mg/kg in 50mL at 1-10 mL/hr)": round(0.15 * weight, 2),
        "Amoxicillin, Flucloxacillin, Chloramphenicol (25mg/kg)": round(25 * weight, 2),
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
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)