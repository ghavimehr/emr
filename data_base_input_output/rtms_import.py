import os
import sys
import django
import csv

# Set up the Django environment
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

# Import the necessary models
from apps.emr.identity.models import *
from apps.emr.rtms.models import *

def convert_int(value):
    """Helper function: convert string to int, or return None if blank or invalid."""
    v = value.strip()
    if not v:
        return None
    try:
        return int(v)
    except ValueError:
        return None

def import_rtms_from_csv(csv_file_path):
    with open(csv_file_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            # Retrieve Patient using the CSV "id" field
            patient_id = convert_int(row.get('id', ''))
            if patient_id is None:
                print("Skipping row: missing or invalid patient id.")
                continue
            try:
                patient = Patient.objects.get(id=patient_id)
            except Patient.DoesNotExist:
                print(f"Patient with id {patient_id} does not exist.")
                continue

            # Retrieve PulseType using CSV "pulse_type" field
            pulse_type_id = convert_int(row.get('pulse_type', ''))
            if pulse_type_id is not None:
                try:
                    pulse_type = PulseType.objects.get(id=pulse_type_id)
                except PulseType.DoesNotExist:
                    print(f"PulseType with id {pulse_type_id} does not exist. Setting to None.")
                    pulse_type = None
            else:
                pulse_type = None

            # Map CSV fields to RTMS fields.
            # Note: The CSV column "MT" is not used since there is no matching field.
            rtms_data = {
                'identity_patient': patient,
                'total_sessions': convert_int(row.get('total_session', '')),
                'pulse_type': pulse_type,
                'first_power': convert_int(row.get('first_power', '')),
                'unknown_variable_1': convert_int(row.get('unknown_variable_1', '')),
                'unknown_variable_2': convert_int(row.get('unknown_variable_2', '')),
                'total_pulse': convert_int(row.get('total_puls', '')),  # CSV column is "total_puls"
                'dlpfc_l': convert_int(row.get('DLPFC_l', '')),
                'dlpfc_r': convert_int(row.get('DLPFC_r', '')),
                'ofc_l': convert_int(row.get('OFC_L', '')),
                'ofc_r': convert_int(row.get('OFC_R', '')),
                'somatosensory_l': convert_int(row.get('SOMATOSENSORY_L', '')),
                'somatosensory_r': convert_int(row.get('SOMATOSENSORY_R', '')),
                'parietal_l': convert_int(row.get('parietal_L', '')),
                'parietal_r': convert_int(row.get('Parietal_r', '')),
                'occipital_l': convert_int(row.get('OCCIPITAL_l', '')),
                'occipital_middle': convert_int(row.get('OCCIPITAL_MIDDLE', '')),
                'occipital_inf': convert_int(row.get('OCCIPITAL_INF', '')),
                'occipital_r': convert_int(row.get('OCCIPITAL_r', '')),
                'm1_l': convert_int(row.get('M1_L', '')),
                'm1_r': convert_int(row.get('M1_R', '')),
                'sma_l': convert_int(row.get('SMA_L', '')),
                'sma_r': convert_int(row.get('SMA_R', '')),
                'r_post_central': convert_int(row.get('R_POST_CENTRAl', '')),
                'l_poat_central': convert_int(row.get('L_POAT_CENTRAL', '')),
                'broca_l': convert_int(row.get('Broca_l', '')),
                'broca_r': convert_int(row.get('Broca_r', '')),
                'sub_temporal_r': convert_int(row.get('sub_Temporal_R', '')),
                'sub_temporal_l': convert_int(row.get('sub_Temporal_l', '')),
                'middle_temporal_l': convert_int(row.get('middle_temporal_l', '')),
                'middle_temporal_r': convert_int(row.get('middle_temporal_r', '')),
            }

            # Create the RTMS record
            rtms_obj = RTMS.objects.create(**rtms_data)
            print(f"Created RTMS record for Patient id {patient_id}")

if __name__ == '__main__':
    # Update this path to point to your CSV file
    csv_file_path = 'data_base_input_output/input_no_date.csv'
    import_rtms_from_csv(csv_file_path)
