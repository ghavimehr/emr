import os
import subprocess
import logging
from datetime import datetime
from django.conf import settings
from apps.emr.identity.models import Patient
from shutil import copyfile
from jdatetime import datetime as jdatetime
from django.utils.translation import gettext as _

from apps.emr.files.models import Document

logger = logging.getLogger(__name__)

save_tex = False
save_aux = False
save_log = False




def agreement_generator(patient_id):
    logger.info(f"demographic_report called for patient_id={patient_id}")
    message = ""
    pdf_path = None

    try:
        # Get the patient data
        patient = Patient.objects.get(id=patient_id)
    except Patient.DoesNotExist:
        message = f"Patient with ID {patient_id} does not exist."
        return message, pdf_path

    # Check the report and edit history
    report = patient.report if patient.report else {}
    edit_history = patient.edit_history if patient.edit_history else {}

    # Get the latest date from report and edit_history
    report_date = max(report.keys(), default=None)
    edit_history_date = max(edit_history.keys(), default=None)

    # Generate the report (new report)
    version_number = len(report) + 1

    base_data_dir = os.path.join(settings.BASE_DIR, "data")
    target_folder_rel_path = os.path.join(str(patient.patient_id), "agreement")
    target_folder_path = os.path.join(base_data_dir, target_folder_rel_path)


    os.makedirs(target_folder_path, exist_ok=True)

    if not os.path.exists(target_folder_path):
        os.makedirs(target_folder_path)

    # Copy the LaTeX template into the patient's folder
    template_path = os.path.join(settings.BASE_DIR, "latex", "commitment_letter.tex")

    tex_file_path = os.path.join(
        target_folder_path,
        f"commitment_letter-{version_number}.tex",
    )


    copyfile(template_path, tex_file_path)


    # Prepare patient data for LaTeX file (favor .name_fa over .name)
    patient_data = {
        "base_dir": settings.BASE_DIR,
        # Basic fields
        "first_name": patient.first_name,
        "last_name": patient.last_name,
        "ssn": patient.ssn,
        "birthday": patient.jbirthday.strftime("%Y/‌%m/‌%d") if patient.jbirthday else "---",
        # Use the Persian name if it exists, else fallback
        "ethnicity": patient.ethnicity_display or "---",
        "marital_status": patient.marital_status or "---",
        "education_level": patient.education_level or "---",
        "blood_group": patient.blood_group or "---",
        "gender": patient.gender or "---",
        "language_option": patient.language_option or "---",
        "occupation": patient.occupation or "---",
        "dominanthand": patient.dominanthand or "---",
        "insurance": patient.insurances_display or "---",
        # For phone, messenger, height, etc.
        "phone": patient.phone or "---",
        "messenger1": patient.messenger1 or "---",
        "messenger2": patient.messenger2 or "---",
        "height": patient.height if patient.height else "---",
        "weight": patient.weight if patient.weight else "---",
        "tags": patient.tags or "---",
        "address": patient.address or "---",
        # Patient ID
        "patient_id": patient.patient_id,
        # legal text
        "patient": format_patient_name(
            patient.first_name, patient.last_name, patient.ssn, patient.gender
        )
        or "بیمار",
        "today": get_jalali_date() or "",
    }

    # Inject data into the LaTeX template
    with open(tex_file_path, "r") as tex_file:
        tex_content = tex_file.read()

    # Replace placeholders with actual patient data (underscore -> dash, fallback to `---` if missing)
    for key, value in patient_data.items():
        placeholder = f'<<{key.replace("_", "-")}>>'
        tex_content = tex_content.replace(placeholder, str(value) if value else "---")
        tex_content = tex_content.replace("<<base-dir>>", str(settings.BASE_DIR))

    # Write the populated LaTeX file
    with open(tex_file_path, "w") as tex_file:
        tex_file.write(tex_content)

    # Compile the LaTeX file to PDF using xelatex
    try:
        process = subprocess.Popen(
            [
                "/usr/local/texlive/2024/bin/x86_64-linux/xelatex",
                "-output-directory",
                target_folder_path,
                tex_file_path,
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.PIPE,
        )
        # Send newline to simulate pressing "Enter" if there's a recoverable error
        stdout, stderr = process.communicate(input=b"\n")


        if process.returncode == 0:
            base_name = f"commitment_letter-{version_number}.pdf"
            new_doc = Document.objects.create(
                patient        = patient,
                relative_path  = f"{target_folder_rel_path}/{base_name}",
                file_name      = base_name,
                file_extension_id = 1,     # 1 → PDF
                document_type_id = 101,      # 101 → Agreements
                protocol_id = 4,             # read-only legal and payment
            )

        if process.returncode != 0:
            message = (
                f"_(Error generating PDF for patient) {patient_id}. "
                f"_(LaTeX compilation failed.)\n{stderr.decode('utf-8')}"
            )
            return message, None
    except subprocess.CalledProcessError as e:
        message = (
            f"Error generating PDF for patient {patient_id}. LaTeX compilation failed."
        )
        return message, None



    # # Define the path of the generated PDF
    # pdf_path = os.path.join(
    #     target_folder_path,
    #     f"commitment_letter-{version_number}.pdf",
    # )

    for ext in ["tex", "aux", "log"]:
        aux_file = os.path.join(target_folder_path, f"commitment_letter-{version_number}.{ext}")
        if os.path.exists(aux_file):
            os.remove(aux_file)


    # Save the version info to the report column
    if report_date:
        report[report_date] = version_number
    else:
        # If there's no previous date key, store the new date/time
        report[datetime.now().strftime("%Y-%m-%d %H:%M:%S")] = version_number

    patient.report = report
    patient.save()

    message = (
        f"Report successfully generated for patient {patient.first_name} {patient.last_name}. "
        f"PDF saved at: {pdf_path}"
    )
    return message, new_doc


PERSIAN_WEEKDAYS = {
    "Saturday": "شنبه",
    "Sunday": "یکشنبه",
    "Monday": "دوشنبه",
    "Tuesday": "سه شنبه",
    "Wednesday": "چهارشنبه",
    "Thursday": "پنجشنبه",
    "Friday": "جمعه",
}

PERSIAN_MONTHS = {
    "Farvardin": "فروردین",
    "Ordibehesht": "اردیبهشت",
    "Khordad": "خرداد",
    "Tir": "تیر",
    "Mordad": "مرداد",
    "Shahrivar": "شهریور",
    "Mehr": "مهر",
    "Aban": "آبان",
    "Azar": "آذر",
    "Dey": "دی",
    "Bahman": "بهمن",
    "Esfand": "اسفند",
}


def format_patient_name(first_name, last_name, ssn, gender):
    """
    Formats the patient information based on gender.

    :param first_name: Patient's first name
    :param last_name: Patient's last name
    :param ssn: Patient's national ID
    :param gender: Patient's gender ("male", "female", or other)
    :return: Formatted patient information string
    """
    ssnt = f"ِدارنده‌ی شماره‌ی ملی {ssn}" if ssn else ""
    if gender == "male":
        return f"آقای {first_name} {last_name} {ssnt}"
    elif gender == "female":
        return f"خانم {first_name} {last_name} {ssnt}"
    else:
        return f"{first_name} {last_name} {ssnt}"


def get_jalali_date():
    jalali_date = jdatetime.today()

    # Convert English weekday and month names to Persian
    week_day_en = jalali_date.strftime("%A")  # English weekday
    month_en = jalali_date.strftime("%B")  # English month

    week_day_fa = PERSIAN_WEEKDAYS.get(week_day_en, week_day_en)
    month_fa = PERSIAN_MONTHS.get(month_en, month_en)

    day = jalali_date.day
    year = jalali_date.year

    return f"مورخ {week_day_fa} {day} {month_fa} ماه سال {year}"
