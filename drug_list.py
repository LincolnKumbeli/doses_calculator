drug_data = {
    'all_drugs': {
        'Albendazole': {'dose_per_kg': 200, 'max_dose': 400, 'frequency': 'Single dose', 'route': 'oral', 'duration': 'single dose'},  # 200mg (max 400mg), oral, single dose
        'Aminophylline': {'dose_per_kg': 5, 'max_dose': 250, 'frequency': 'QID', 'route': 'IV/oral', 'duration': 'as required'},  # 5mg/kg QID (max 250mg), IV/oral, as required
        'Amoxicillin': {'dose_per_kg': 25, 'max_dose': 500, 'frequency': 'TDS', 'route': 'IV/IM/oral', 'duration': '5 days'},  # 25mg/kg TDS (max 500mg/dose), IV/IM/oral, 5 days
        'Ampicillin': {'dose_per_kg': 50, 'max_dose': 2000, 'frequency': 'QID', 'route': 'IV/IM/oral', 'duration': '5-7 days'},  # 50mg/kg QID (max 2g/day), IV/IM/oral, 5-7 days
        'Artemether-Lumefantrine': {'dose_per_kg': 2, 'max_dose': 12, 'frequency': 'BD', 'route': 'oral', 'duration': '3 days'},  # 2mg/kg (A) & 12mg/kg (L) BD, oral, 3 days
        'Artesunate': {'dose_per_kg': 4, 'max_dose': 4, 'frequency': 'daily', 'route': 'oral/IV/rectal', 'duration': '3-5 days'},  # 4mg/kg daily on Day 1, then 2mg/kg daily, oral/IV/rectal, 3-5 days
        'Aspirin': {'dose_per_kg': 10, 'max_dose': 300, 'frequency': 'QID', 'route': 'oral', 'duration': 'as required'},  # 10mg/kg QID (max 300mg/dose), oral, as required
        'Atropine': {'dose_per_kg': 0.6, 'max_dose': 0.6, 'frequency': 'PRN', 'route': 'IM', 'duration': 'as required'},  # 0.6mg/ml, IM, as required
        'Azithromycin': {'dose_per_kg': 30, 'max_dose': 30, 'frequency': 'daily', 'route': 'oral', 'duration': 'varies'},  # 30mg/kg daily, oral, course varies by indication
        'Benzathine Penicillin': {'dose_per_kg': 50000, 'max_dose': 2400000, 'frequency': 'Single dose', 'route': 'IM', 'duration': 'single dose'},  # 50,000 units/kg (max 2.4 million units), IM, single dose
        'Carbamazepine': {'dose_per_kg': 5, 'max_dose': 10, 'frequency': 'BD', 'route': 'oral', 'duration': 'varies'},  # 5-10mg/kg BD, oral, course varies by indication
        'Ceftriaxone': {'dose_per_kg': 50, 'max_dose': 2000, 'frequency': 'BD', 'route': 'IV/IM', 'duration': '5-7 days'},  # 50mg/kg BD (max 2g/day), IV/IM, 5-7 days
        'Chloramphenicol': {'dose_per_kg': 25, 'max_dose': 1000, 'frequency': 'QID', 'route': 'IV/IM/oral', 'duration': '5-7 days'},  # 25mg/kg QID (max 1g/dose), IV/IM/oral, 5-7 days
        'Chloroquine': {'dose_per_kg': 10, 'max_dose': 10, 'frequency': 'daily', 'route': 'oral', 'duration': '3 days'},  # 10mg/kg daily (treatment) / 5mg/kg weekly (prophylaxis), oral, 3 days or weekly
        'Ciprofloxacin': {'dose_per_kg': 10, 'max_dose': 20, 'frequency': 'BD', 'route': 'oral', 'duration': 'varies'},  # 10-20mg/kg BD, oral, course varies by indication
        'Cloxacillin (Flucloxacillin)': {'dose_per_kg': 25, 'max_dose': 50, 'frequency': 'QID', 'route': 'IV/IM/oral', 'duration': '5-7 days'},  # 25-50mg/kg QID (max 500mg/dose), IV/IM/oral, 5-7 days
        'Clofazimine': {'dose_per_kg': 100, 'max_dose': 100, 'frequency': 'daily', 'route': 'oral', 'duration': 'varies'},  # 100mg daily, oral, course varies by indication
        'Cotrimoxazole (Septrin)': {'dose_per_kg': 5, 'max_dose': 5, 'frequency': 'BD', 'route': 'oral', 'duration': '5-7 days'},  # Trimethoprim 5mg/kg BD, oral, 5-7 days
        'Dapsone': {'dose_per_kg': 50, 'max_dose': 100, 'frequency': 'daily', 'route': 'oral', 'duration': '12 weeks'},  # 50mg daily (max 100mg), oral, 12 weeks then maintenance
        'Dexamethasone': {'dose_per_kg': 0.15, 'max_dose': 0.15, 'frequency': 'QID', 'route': 'IV/oral', 'duration': 'varies'},  # 0.15mg/kg QID, IV/oral, course varies by indication
        'Diethylcarbamazine': {'dose_per_kg': 50, 'max_dose': 50, 'frequency': 'TDS', 'route': 'oral', 'duration': '3 weeks'},  # 50mg TDS, oral, 3 weeks
        'Dihydroartemisinin/Piperaquine': {'dose_per_kg': 40, 'max_dose': 40, 'frequency': 'fixed dose', 'route': 'oral', 'duration': 'varies'},  # 40mg/320mg fixed dose, oral, course varies by indication
        'Diazepam': {'dose_per_kg': 0.25, 'max_dose': 10, 'frequency': 'single dose', 'route': 'IV/rectal', 'duration': 'as required'},  # 0.25mg/kg single dose (max 10mg), IV/rectal, as required
        'Digoxin (Lanoxin)': {'dose_per_kg': 50, 'max_dose': 50, 'frequency': '6H', 'route': 'oral', 'duration': 'varies'},  # 50mcg/ml, oral; loading dose every 6 hours for 3 doses, then daily maintenance (10mcg/kg/day)
        'Erythromycin': {'dose_per_kg': 10, 'max_dose': 500, 'frequency': 'QID', 'route': 'oral', 'duration': '5-7 days'},  # 10mg/kg QID (max 500mg/dose), oral, 5-7 days
        'Ethambutol': {'dose_per_kg': 20, 'max_dose': 1600, 'frequency': 'daily', 'route': 'oral', 'duration': 'varies'},  # 20mg/kg daily (max 1.6g/day), oral, as per TB regimen
        'Ferrous Sulphate (Fefol)': {'dose_per_kg': 200, 'max_dose': 200, 'frequency': 'daily', 'route': 'oral', 'duration': 'varies'},  # 200mg daily, oral, course varies by indication
        'Ferrous Fumarate': {'dose_per_kg': 46, 'max_dose': 46, 'frequency': 'daily', 'route': 'oral', 'duration': 'varies'},  # 46mg/5ml daily, oral, course varies by indication
        'Flucloxacillin': {'dose_per_kg': 250, 'max_dose': 250, 'frequency': 'QID', 'route': 'IM/IV/oral', 'duration': '5-7 days'},  # 250mg QID, IM/IV/oral, 5-7 days
        'Furosemide (Lasix)': {'dose_per_kg': 20, 'max_dose': 20, 'frequency': 'PRN', 'route': 'IM/IV', 'duration': 'as required'},  # 20mg/2ml, IM/IV, as required
        'Gentamicin': {'dose_per_kg': 5, 'max_dose': 7.5, 'frequency': 'daily', 'route': 'IV/IM', 'duration': '5-7 days'},  # 5-7.5mg/kg daily, IV/IM, 5-7 days
        'Hydrocortisone': {'dose_per_kg': 0, 'max_dose': 0, 'frequency': 'varies', 'route': 'IV/oral', 'duration': 'varies'},  # Dose varies, IV/oral, course varies by indication
        'Ipecacuanha syrup': {'dose_per_kg': 15, 'max_dose': 15, 'frequency': 'single dose', 'route': 'oral', 'duration': 'single dose'},  # 15ml, single dose, oral
        'Isoniazid': {'dose_per_kg': 10, 'max_dose': 300, 'frequency': 'daily', 'route': 'oral', 'duration': '6-9 months'},  # 10mg/kg daily (max 300mg), oral, 6-9 months
        'Ketamine': {'dose_per_kg': 500, 'max_dose': 500, 'frequency': 'PRN', 'route': 'IM', 'duration': 'as required'},  # 500mg/10ml IM first dose; subsequent doses vary based on weight, as required
        'Magnesium Hydroxide': {'dose_per_kg': 20, 'max_dose': 20, 'frequency': 'PRN', 'route': 'oral', 'duration': 'as required'},  # 2-20ml, oral, as required
        'Mebendazole': {'dose_per_kg': 100, 'max_dose': 100, 'frequency': 'BD', 'route': 'oral', 'duration': '3 days'},  # 100mg BD (3 days inpatient) / single dose outpatient, oral
        'Metronidazole': {'dose_per_kg': 15, 'max_dose': 500, 'frequency': 'TDS', 'route': 'oral/rectal', 'duration': '5-7 days'},  # 15mg/kg TDS (max 500mg/dose), oral/rectal, 5-7 days
        'Morphine': {'dose_per_kg': 0.1, 'max_dose': 10, 'frequency': 'QID', 'route': 'IV/IM', 'duration': 'as required'},  # 0.1mg/kg QID (max 10mg), IV/IM, as required
        'Naloxone': {'dose_per_kg': 0.4, 'max_dose': 0.4, 'frequency': 'PRN', 'route': 'IM/IV', 'duration': 'as required'},  # 0.4mg/ml (0.1mg/kg), IM/IV, as required
        'Nevirapine': {'dose_per_kg': 0, 'max_dose': 0, 'frequency': 'varies', 'route': 'oral', 'duration': 'varies'},  # Infant suspension/tablet, oral, course varies by indication
        'Nitrofurantoin': {'dose_per_kg': 0, 'max_dose': 0, 'frequency': 'varies', 'route': 'oral', 'duration': 'varies'},  # Dose varies, oral, course varies by indication
        'Paracetamol (Suspension)': {'dose_per_kg': 15, 'max_dose': 500, 'frequency': 'QID', 'route': 'oral', 'duration': 'as required'},  # 10-15mg/kg QID (max 500mg/dose), oral
        'Paracetamol (Suppository 125mg)': {'dose_per_kg': 0, 'max_dose': 0, 'frequency': 'QID', 'route': 'PR', 'duration': 'as required'},  # QID, PR
        'Paracetamol (Suppository 250mg)': {'dose_per_kg': 0, 'max_dose': 0, 'frequency': 'QID', 'route': 'PR', 'duration': 'as required'},  # QID, PR
        'Pethidine': {'dose_per_kg': 1, 'max_dose': 100, 'frequency': 'QID', 'route': 'IV/IM', 'duration': 'as required'},  # 1mg/kg QID (max 100mg), IV/IM, as required
        'Phenobarbitone': {'dose_per_kg': 5, 'max_dose': 5, 'frequency': 'daily', 'route': 'oral', 'duration': 'varies'},  # 5mg/kg daily, oral; loading dose once IM/IV varies by weight; maintenance dose varies by weight
        'Phenytoin': {'dose_per_kg': 3, 'max_dose': 3, 'frequency': 'daily', 'route': 'IV/oral', 'duration': 'varies'},  # 3mg/kg daily, IV/oral; maintenance dose varies by weight
        'Promethazine (Phenergan)': {'dose_per_kg': 25, 'max_dose': 25, 'frequency': 'BD', 'route': 'oral', 'duration': 'varies'},  # 25mg BD, oral; 50mg/2ml IM/IV single dose
        'Quinine': {'dose_per_kg': 10, 'max_dose': 10, 'frequency': 'TDS', 'route': 'IV/oral', 'duration': '7 days'},  # 10mg/kg TDS, IV/oral, 7 days
        'Rifampicin': {'dose_per_kg': 15, 'max_dose': 600, 'frequency': 'daily', 'route': 'oral', 'duration': '6-9 months'},  # 15mg/kg daily (max 600mg), oral, 6-9 months
        'Salbutamol (Ventolin)': {'dose_per_kg': 0.15, 'max_dose': 0.15, 'frequency': 'PRN', 'route': 'oral', 'duration': 'as required'},  # 0.15mg, oral; respiratory solution diluted in 4ml normal saline, as required
        'Tinidazole': {'dose_per_kg': 500, 'max_dose': 500, 'frequency': 'daily', 'route': 'oral', 'duration': 'varies'},  # 500mg daily, oral, course varies by indication
        'Zinc': {'fixed_dose': {10: 10, 20: 20}, 'frequency': 'daily', 'route': 'oral', 'duration': 'as required'}  # 5-10mg daily, oral, as required
    },
    'emergency': {
        'Adrenaline': {'dose_per_kg': 0.01, 'max_dose': 1, 'frequency': 'PRN', 'route': 'IM/IV'},
        'Atropine': {'dose_per_kg': 0.02, 'max_dose': 0.6, 'frequency': 'PRN', 'route': 'IV'},
        'Diazepam': {'dose_per_kg': 0.25, 'max_dose': 10, 'frequency': 'PRN', 'route': 'IV/PR'},
        'Hydrocortisone': {'dose_per_kg': 4, 'max_dose': 100, 'frequency': 'PRN', 'route': 'IV'}
    },
    'rsi_ett_drugs': {
        'premedication': {
            'Atropine': {'dose_per_kg': 0.02, 'max_dose': 0.6, 'frequency': 'Once', 'route': 'IV'},
            'Lidocaine': {'dose_per_kg': 1, 'max_dose': 30, 'frequency': 'Once', 'route': 'IV'}
        },
        'sedatives': {
            'Thiopental': {'dose_per_kg': [2, 5], 'max_dose': 150, 'frequency': 'Once', 'route': 'IV'},
            'Etomidate': {'dose_per_kg': [0.2, 0.4], 'max_dose': 12, 'frequency': 'Once', 'route': 'IV'},
            'Ketamine': {'dose_per_kg': [1.5, 2], 'max_dose': 60, 'frequency': 'Once', 'route': 'IV'},
            'Propofol': {'dose_per_kg': [1.5, 3], 'max_dose': 90, 'frequency': 'Once', 'route': 'IV'},
            'Midazolam': {'dose_per_kg': [0.1, 0.2], 'max_dose': 6, 'frequency': 'Once', 'route': 'IV'},
            'Fentanyl': {'dose_per_kg': [0.002, 0.004], 'max_dose': 0.12, 'frequency': 'Once', 'route': 'IV', 'units': 'mg'},
            'Morphine': {'dose_per_kg': [0.1, 0.2], 'max_dose': 6, 'frequency': 'Once', 'route': 'IV'}
        },
        'depolarizing_paralytics': {
            'Succinylcholine': {'dose_per_kg': [1, 2], 'max_dose': 60, 'frequency': 'Once', 'route': 'IV'}
        },
        'non_depolarizing_paralytics': {
            'Rocuronium': {'dose_per_kg': [0.6, 1.2], 'max_dose': 36, 'frequency': 'Once', 'route': 'IV'},
            'Vecuronium': {'dose_per_kg': 0.1, 'max_dose': 3, 'frequency': 'Once', 'route': 'IV'},
            'Pancuronium': {'dose_per_kg': 0.1, 'max_dose': 3, 'frequency': 'Once', 'route': 'IV'}
        }
    }
}