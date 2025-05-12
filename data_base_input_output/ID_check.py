import os
import sys
import django
import pandas as pd

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

# Set up Django environment (update 'your_project.settings' to your actual settings module)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from apps.emr.identity.models import Patient   # Replace 'your_app' with your actual app name

# Load the CSV file that contains the 'id' column (assumed to be Patient's primary key)
csv_file = "data_base_input_output/final_id_check.csv"  # Adjust the filename as needed
df_csv = pd.read_csv(csv_file)
id_list = df_csv['id'].tolist()

# Query the Patient model for these ids, retrieving first_name and last_name
patients_qs = Patient.objects.filter(id__in=id_list).values('id', 'first_name', 'last_name')
df_patients = pd.DataFrame(list(patients_qs))

# Rename the columns from the database to avoid overwriting existing CSV columns.
df_patients = df_patients.rename(columns={
    'first_name': 'db_first_name',
    'last_name': 'db_last_name'
})

# Merge the full original CSV DataFrame with the database results on the 'id' column.
df_merged = pd.merge(df_csv, df_patients, on='id', how='left')

# Save the output CSV file containing the id, first_name, and last_name columns.
# If you only want the two name columns, you can adjust the columns list accordingly.
output_csv = "data_base_input_output/final_id_checked.csv"
df_merged.to_csv(output_csv, index=False)

print(f"Output CSV file with first_name and last_name has been saved as '{output_csv}'.")
