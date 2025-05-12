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


django.setup()

from apps.emr.identity.models import Patient  # Replace 'your_app' with your actual app name

# Load CSV file that contains the phone numbers and existing first_name, last_name columns
csv_file = "data_base_input_output/rTMS_protcols_cleaned_2_selected.csv"
df_csv = pd.read_csv(csv_file)

# Convert the phone numbers to strings and pad with zeros to ensure 11-digit format
df_csv['phone'] = df_csv['phone'].astype(str).str.zfill(11)

# Get the list of phone numbers from the CSV
phone_numbers = df_csv['phone'].tolist()

# Query the Patient model for patients whose phone number is in the CSV list
patients_qs = Patient.objects.filter(phone__in=phone_numbers).values('phone', 'first_name', 'last_name', 'id')

# Convert the QuerySet into a DataFrame
df_patients = pd.DataFrame(list(patients_qs))

# If there are matching patients, rename columns to avoid conflict with CSV's columns
if not df_patients.empty:
    df_patients = df_patients.rename(columns={
        'first_name': 'db_first_name',
        'last_name': 'db_last_name',
        'id': 'patient_id'
    })
else:
    print("No matching patients found in the database.")

# Merge the original CSV DataFrame with the patients DataFrame on the 'phone' column
# This merge will duplicate CSV rows if there are multiple patients for the same phone number.
df_merged = pd.merge(df_csv, df_patients, on='phone', how='left')

# Save the merged DataFrame to a new CSV file
output_csv = "updated_phone_numbers.csv"
df_merged.to_csv(output_csv, index=False)

print(f"CSV file has been updated with database columns and saved as '{output_csv}'.")
