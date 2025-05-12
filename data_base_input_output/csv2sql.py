import os
import sys
import django
import pandas as pd

# Add the project root to sys.path so that Django can locate your modules.
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

# Set the Django settings module (your settings are in core/settings.py)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

# Initialize Django
django.setup()

# Import your models (replace 'myapp' with the actual name of your Django app)
from apps.emr.identity.models import Patient, Occupation

def safe_int(value):
    """Convert a value to an integer, returning None if the value is missing."""
    if pd.isna(value):
        return None
    try:
        return int(value)
    except Exception:
        return None

def safe_value(value):
    """Return None if the value is missing, otherwise return the value."""
    if pd.isna(value) or value == '':
        return None
    return value

def format_ssn(ssn):
    """
    Ensures the SSN has exactly 10 characters.
    - If ssn is missing, returns None.
    - If ssn has less than 10 characters, pads with leading zeros.
    - Returns None if the result is not exactly 10 characters.
    """
    if pd.isna(ssn) or ssn == '':
        return None
    ssn_str = str(ssn).strip()
    if len(ssn_str) < 10:
        ssn_str = ssn_str.zfill(10)
    if len(ssn_str) == 10:
        return ssn_str
    return None

def format_phone(phone):
    """
    Ensures the phone number has exactly 11 digits.
    - If phone is missing, returns None.
    - If phone has 10 digits, adds a '0' to the left.
    - If phone has exactly 11 digits, returns it as is.
    - Otherwise, returns None.
    """
    if pd.isna(phone) or phone == '':
        return None
    phone_str = str(phone).strip()
    if len(phone_str) == 10:
        return "0" + phone_str
    elif len(phone_str) == 11:
        return phone_str
    else:
        return None

# Load your CSV file (ensure that the CSV header matches your column names)
csv_file = '/home/psycho/app-generator/data_base_input_output/patient_list_cleaned_2.2_part3.csv'
df = pd.read_csv(csv_file)

# Lists to keep track of rows with errors and their corresponding error logs.
error_rows = []
error_logs = []

# Iterate over each row and attempt to create Patient records.
for index, row in df.iterrows():
    try:
        # Convert patient_id safely.
        patient_id = safe_int(row.get('patient_id'))
        # Skip the row if patient_id is missing or already exists.
        if patient_id is None or Patient.objects.filter(patient_id=patient_id).exists():
            continue

        # Process the occupation value from CSV.
        occupation_value = row.get('occupation_id')
        if pd.isna(occupation_value) or occupation_value == '':
            occupation_obj = None
        else:
            # Register or retrieve the Occupation using the CSV value in the fname field.
            occupation_obj, created = Occupation.objects.get_or_create(fname=occupation_value)

        # Create the Patient record with formatted values.
        Patient.objects.create(
            first_name=safe_value(row.get('first_name', '')),
            last_name=safe_value(row.get('last_name', '')),
            patient_id=patient_id,
            phone=format_phone(row.get('phone')),
            ssn=format_ssn(row.get('ssn')),
            education_level_id=safe_int(row.get('education_level_id')),
            marital_status_id=safe_int(row.get('marital_status_id')),
            occupation=occupation_obj,  # Set the foreign key.
            address=safe_value(row.get('address', ''))
        )
    except Exception as e:
        error_msg = f"Row {index}: {str(e)}"
        print(error_msg)
        error_logs.append(error_msg)
        # Append the row (as a dict) so that later we can reconstruct the error CSV.
        error_rows.append(row)

# Write error log messages to a file if there are any errors.
if error_logs:
    with open('error_log.txt', 'w') as log_file:
        log_file.write("\n".join(error_logs))
    print("Errors logged in error_log.txt")

# If there are rows with errors, write them to a new CSV file (with header).
if error_rows:
    error_df = pd.DataFrame(error_rows)
    error_df.to_csv('error_rows.csv', index=False)
    print("Rows with errors saved to error_rows.csv")
else:
    print("CSV import complete without errors!")
