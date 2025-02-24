def calculate_fluids(weight):
    """ Returns bolus fluids, maintenance rate, and two-thirds maintenance rate """
    bolus_fluids = {
        "Normal Saline 20mL/kg": round(weight * 20, 1),
        "Ringer’s Lactate 10mL/kg": round(weight * 10, 1),
    }
    maintenance_rate = round(4 * min(weight, 10) + 2 * min(max(weight - 10, 0), 10) + 1 * max(weight - 20, 0), 1)
    two_thirds_maintenance_rate = round(maintenance_rate * 0.67, 1)
    return bolus_fluids, maintenance_rate, two_thirds_maintenance_rate

def calculate_parkland_formula(weight, tbsa):
    """ Returns Parkland formula fluid resuscitation for burns """
    total_volume = weight * 4 * tbsa
    first_8_hours = total_volume * 0.5
    first_8_hours_rate = first_8_hours / 8
    next_16_hours = total_volume * 0.5
    next_16_hours_rate = next_16_hours / 16
    return total_volume, first_8_hours, first_8_hours_rate, next_16_hours, next_16_hours_rate
