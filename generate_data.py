import pandas as pd
import numpy as np

# List of Indian cities
indian_cities = ['Mumbai', 'Delhi', 'Bangalore', 'Hyderabad', 'Ahmedabad', 'Chennai', 'Kolkata', 'Surat', 'Pune', 'Jaipur']

# List of Indian first names and surnames
first_names = ['Aarav', 'Vivaan', 'Aditya', 'Vihaan', 'Arjun', 'Sai', 'Reyansh', 'Ayaan', 'Krishna', 'Ishaan',
                'Anaya', 'Aadhya', 'Diya', 'Aarohi', 'Myra', 'Anvi', 'Siya', 'Prisha', 'Riya', 'Aarna']
surnames = ['Sharma', 'Patel', 'Kumar', 'Singh', 'Reddy', 'Mehta', 'Iyer', 'Gupta', 'Jain', 'Verma']

# Generate sample data
np.random.seed(42)
patient_ids = range(1, 1001)
names = [f"{np.random.choice(first_names)} {np.random.choice(surnames)}" for _ in range(1000)]
ages = np.random.randint(20, 80, size=1000)
genders = np.random.choice(['Male', 'Female'], size=1000)
cities = np.random.choice(indian_cities, size=1000)
body_temperatures = np.random.uniform(36, 37.5, size=1000)  # Celsius
pulse_rates = np.random.randint(60, 100, size=1000)  # beats per minute
respiration_rates = np.random.randint(12, 20, size=1000)  # breaths per minute
blood_pressures = np.random.randint(90, 140, size=1000)  # systolic pressure
blood_oxygens = np.random.uniform(95, 100, size=1000)  # percentage
weights = np.random.uniform(50, 100, size=1000)  # kg
blood_glucose_levels = np.random.randint(70, 140, size=1000)  # mg/dL
diagnoses = np.random.choice(['Healthy', 'At Risk', 'Unwell'], size=1000)

# Create DataFrame
medical_data = pd.DataFrame({
    'Patient_ID': patient_ids,
    'Name': names,
    'Age': ages,
    'Gender': genders,
    'City': cities,
    'Body_Temperature': body_temperatures,
    'Pulse_Rate': pulse_rates,
    'Respiration_Rate': respiration_rates,
    'Blood_Pressure': blood_pressures,
    'Blood_Oxygen': blood_oxygens,
    'Weight': weights,
    'Blood_Glucose_Level': blood_glucose_levels,
    'Diagnosis': diagnoses
})

# Save to Excel file
medical_data.to_excel('medical_dataset_vitals.xlsx', index=False, sheet_name='MedicalData')
