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
from apps.emr.identity.models import Patient, Gender, DominantHand

def update_patients_from_csv(csv_file_path):
    with open(csv_file_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            patient_pk = row['id']
            gender_id = row['gender_id']
            dominanthand_id = row['identity_dominanthand_id']

            try:
                # Retrieve the patient based on the primary key
                patient = Patient.objects.get(id=patient_pk)
            except Patient.DoesNotExist:
                print(f"Patient with id {patient_pk} does not exist.")
                continue

            # Handle gender_id: if it's not empty, retrieve the Gender instance; otherwise, set to None
            if gender_id.strip():
                try:
                    gender_instance = Gender.objects.get(id=int(gender_id))
                except (Gender.DoesNotExist, ValueError):
                    print(f"Gender with id {gender_id} does not exist or is invalid.")
                    gender_instance = None
            else:
                gender_instance = None

            # Handle dominanthand_id: if it's not empty, retrieve the DominantHand instance; otherwise, set to None
            if dominanthand_id.strip():
                try:
                    dominanthand_instance = DominantHand.objects.get(id=int(dominanthand_id))
                except (DominantHand.DoesNotExist, ValueError):
                    print(f"DominantHand with id {dominanthand_id} does not exist or is invalid.")
                    dominanthand_instance = None
            else:
                dominanthand_instance = None

            # Update the patient record with the new foreign key values
            patient.gender = gender_instance
            patient.dominanthand = dominanthand_instance
            patient.save()

            print(f"Updated Patient {patient_pk}: Gender {gender_id}, Dominant Hand {dominanthand_id}")


if __name__ == '__main__':
    # Update this path to the location of your CSV file
    csv_file_path = 'data_base_input_output/input_identity.csv'
    update_patients_from_csv(csv_file_path)
