import os
import django
import sys

# Set up Django settings
sys.path.append("/home/psycho/app-generator")

# Set the Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app-generator.settings")

# Setup Django
django.setup()

import logging
import subprocess
from pathlib import Path
from app.emr.identity.models import (
    Patient,
)  # Adjust this import to your actual app and model location

# Configure logging
logger = logging.getLogger("generate_demography_pdf")
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
logger.addHandler(ch)


def generate_demography_pdf_for_all_patients():
    try:
        # Fetch all patients from the database
        patients = Patient.objects.all()
        logger.info(f"Found {patients.count()} patients in the database.")

        # Loop through each patient and generate a PDF
        for patient in patients:
            try:
                logger.info(
                    f"Generating PDF for Patient ID: {patient.patient_id} - {patient.first_name} {patient.last_name}"
                )

                # Create output directory based on patient information
                base_dir = Path("data/patients/")
                folder_name = (
                    f"{patient.patient_id}-{patient.first_name}-{patient.last_name}"
                )
                output_dir = base_dir / folder_name
                output_dir.mkdir(parents=True, exist_ok=True)

                pdf_filename = f"{folder_name}-demography.pdf"
                pdf_path = output_dir / pdf_filename

                # 1) Read the .tex template from disk
                tex_file_path = output_dir / "demography_temp.tex"
                try:
                    with open(
                        "latex/demography_template.tex", "r", encoding="utf-8"
                    ) as f:
                        latex_template = f.read()
                    logger.info("LaTeX template loaded successfully.")
                except Exception as e:
                    logger.error(f"Error loading LaTeX template: {e}")
                    continue

                # 2) Replace placeholders in the template
                latex_content = latex_template

                latex_content = latex_content.replace(
                    "<<PATIENT-ID>>", str(patient.patient_id)
                )
                latex_content = latex_content.replace(
                    "<<FIRST-NAME>>", patient.first_name or ""
                )
                latex_content = latex_content.replace(
                    "<<LAST-NAME>>", patient.last_name or ""
                )
                latex_content = latex_content.replace(
                    "<<BIRTHDAY>>", str(patient.birthday) if patient.birthday else ""
                )
                latex_content = latex_content.replace("<<PHONE>>", patient.phone or "")
                latex_content = latex_content.replace(
                    "<<ADDRESS>>", patient.address or ""
                )

                # 3) Write the temp .tex file
                with open(tex_file_path, "w", encoding="utf-8") as f:
                    f.write(latex_content)
                logger.info(f"LaTeX content written to {tex_file_path}")

                # 4) Compile with xelatex
                try:
                    logger.info("Attempting LaTeX compilation...")
                    subprocess.run(
                        ["xelatex", "-interaction=nonstopmode", tex_file_path.name],
                        cwd=output_dir,
                        check=True,
                    )
                    logger.info("LaTeX compilation successful.")
                except subprocess.CalledProcessError as e:
                    logger.error(
                        f"Error compiling LaTeX for patient {patient.patient_id}: {e}"
                    )
                    continue

                # 5) Save PDF path to patient.report
                patient.report = str(pdf_path)
                patient.save()
                logger.info(
                    f"PDF generated and saved for Patient ID {patient.patient_id}: {pdf_path}"
                )

            except Exception as e:
                logger.error(
                    f"Error generating PDF for Patient ID {patient.patient_id}: {e}"
                )

    except Exception as e:
        logger.error(f"An error occurred during the PDF generation process: {e}")


# Run the function to generate PDFs for all patients
if __name__ == "__main__":
    generate_demography_pdf_for_all_patients()
