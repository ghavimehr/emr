# apps/emr/oneglance/views.py

import os, json, urllib, requests, base64, jwt, time, logging, subprocess
from pathlib import Path

from django.shortcuts import render, get_object_or_404
from django.http import FileResponse, Http404, HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.urls import reverse
from django.contrib import messages
from django.utils.translation import gettext as _
from django.utils.translation import activate

from jdatetime import datetime as jdatetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from shutil import copyfile


from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponseBadRequest
from django.utils.decorators import method_decorator

# from apps.emr.oneglance.models import OnlyOfficeAnnotation


# allowing click-jaking
from django.views.decorators.clickjacking import xframe_options_sameorigin

from apps.emr.identity.models import Patient
# from apps.emr.files.models import FilePermission
# from apps.common.views_sliding_panel import document_box_generator
from apps.emr.files.utils import patient_documents
from apps.common.get_localized_name import get_localized_name





from django.urls import reverse

logger = logging.getLogger(__name__)


@csrf_exempt
@xframe_options_sameorigin
def oneglance_page(request):
    # Get patient from the session or raise 404 if not found
    patient_db_id = request.session.get("selected_patient_id")
    if not patient_db_id:
        return render(request, 'emr/oneglance/oneglance.html', {"patient": None, "pdfs": []})

    patient = get_object_or_404(Patient, id=patient_db_id)

    # Define the directory path to check for files
    # You could pass this in via the URL or use a default value.
    directory_path = request.GET.get("directory_path", "data")  # Use the `data` folder as the default.
    file_extension = request.GET.get("file_extension", "pdf")  # Default file extension is "pdf"
    
    # Get the list of files to exclude
    exclude_files = request.GET.getlist("exclude_files", [])  # List of filenames to exclude (e.g., "example.pdf")
    
    # Special fields
    selected_insurances = (
        patient.get_selected_insurances()
    )
    insurance_list = []
    for insurance in selected_insurances:
        insurance_list.append(get_localized_name(insurance))
    insurance_on_view = ", ".join(insurance_list) or "---"

    selected_ethnicities = patient.get_selected_ethnicities()  
    ethnicity_list = []
    for eth in selected_ethnicities:
        ethnicity_list.append(get_localized_name(eth))
    ethnicity_on_view = ", ".join(ethnicity_list) or "---"


    documents = patient_documents(
        request=request,
        patient=patient,
        document_type=1,
    )

    context = {
        'page_title'     : _("One-Glance"),
        'page_info'      : _("Patient's Summerized Data"),
        "documents": documents,
        "title": "",
        "patient": patient,
        "user_id": request.user.id,
        "user_name": request.user.get_full_name(),
        "ds_host": settings.ONLYOFFICE_DOCSERVER_URL,
        "callbackUrl": settings.ONLYOFFICE_CALLBACK,
        "insurance": insurance_on_view,
        "ethnicity": ethnicity_on_view,
        "mode": "edit"
    }

    # Render the oneglance page with the generated documents
    return render(request, 'emr/oneglance/oneglance.html', context)


@csrf_exempt
@xframe_options_sameorigin
def generate_pdf(request):
    try:
        # Get patient from the session or raise 404 if not found
        patient_db_id = request.session.get("selected_patient_id")
        if not patient_db_id:
            return JsonResponse({"error": "No patient selected."}, status=400)

        patient = get_object_or_404(Patient, id=patient_db_id)

        # Define directory path and file extension
        directory_path = request.GET.get("directory_path", "data")  # Use `data` folder by default
        file_extension = request.GET.get("file_extension", "pdf")  # Default is `pdf`
        patient_folder = os.path.join(settings.BASE_DIR, directory_path, str(patient.patient_id))

        # Generate the PDF filename (today's Jalali date)

        today_jalali = jdatetime.today().strftime("%Y-%m-%d")  # Today's date in Jalali format
        index = 1

        # Find the highest existing index
        while os.path.exists(os.path.join(settings.BASE_DIR, directory_path, str(patient.patient_id), f"{today_jalali}-{index}.pdf")):
            index += 1
        
        # Create the filename with index
        if index == 1:
            file_name = f"{today_jalali}"
        else:
            file_name = f"{today_jalali}-{index}"

        # Path to save the new PDF
        file_path = os.path.join(settings.BASE_DIR, directory_path, str(patient.patient_id), file_name)
        os.makedirs(patient_folder, exist_ok=True) 

        # Debugging: Check if directory exists and is writable
        if not os.path.isdir(os.path.dirname(file_path)):
            return JsonResponse({"error": f"Directory does not exist: {os.path.dirname(file_path)}"}, status=500)

        # Define LaTeX template file path
        template_path = os.path.join(settings.BASE_DIR, "latex", "handwriting_pages.tex")

        # Generate LaTeX file path
        tex_file_path = os.path.join(settings.BASE_DIR, "data", str(patient.patient_id), f"{file_name}.tex")

        # Copy the LaTeX template to the new location
        copyfile(template_path, tex_file_path)

        selected_insurances = (
            patient.get_selected_insurances()
        )  # returns a queryset for M2M
        insurance_list = []
        for insurance in selected_insurances:
            insurance_list.append(get_localized_name(insurance))
        # Prepare the patient data for LaTeX
        patient_data = {
            "base_dir": settings.BASE_DIR,
            # Basic fields
            "first_name": patient.first_name,
            "last_name": patient.last_name,
            "ssn": patient.ssn,
            "birthday": (
                patient.birthday.strftime("%d\\slash%m\\slash%Y")
                if patient.birthday
                else "---"
            ),
            "today": today_jalali,
            "patient_id": patient.patient_id,
            "insurance": ", ".join(insurance_list) or "---",
        }

        # Inject patient data into LaTeX template
        with open(tex_file_path, "r") as tex_file:
            tex_content = tex_file.read()

        for key, value in patient_data.items():
            placeholder = f'<<{key.replace("_", "-")}>>'
            tex_content = tex_content.replace(placeholder, str(value) if value else "---")

        # Write the populated LaTeX file
        with open(tex_file_path, "w") as tex_file:
            tex_file.write(tex_content)

        # Compile the LaTeX file to PDF using XeLaTeX
        try:
            process = subprocess.Popen(
                [
                    "/usr/local/texlive/2024/bin/x86_64-linux/xelatex",  # Adjust path if needed
                    "-output-directory",
                    os.path.dirname(tex_file_path),
                    tex_file_path,
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            stdout, stderr = process.communicate(input=b"\n")

            if process.returncode != 0:
                message = f"Error generating PDF for patient {patient.patient_id}. LaTeX compilation failed.\n{stderr.decode('utf-8')}"
                return JsonResponse({"error": message}, status=500)
        except subprocess.CalledProcessError as e:
            return JsonResponse({"error": "Error during LaTeX compilation."}, status=500)

        # Define the path of the generated PDF
        pdf_path = os.path.join(
            settings.BASE_DIR,
            directory_path,
            str(patient.patient_id),
            f"{file_name}.pdf"
        )

        for ext in ["tex", "aux", "log"]:
            aux_file = os.path.join(settings.BASE_DIR, directory_path, str(patient.patient_id), f"{file_name}.{ext}")
            if os.path.exists(aux_file):
                os.remove(aux_file)


        # Return the generated PDF details to the client
        documents = document_box_generator(
            patient=patient,
            directory_path=directory_path,
            file_extension="pdf",
            exclude_files=[],
            request=request,
        )

        if documents is None or len(documents) == 0:
            return JsonResponse({"error": "Failed to generate the document list."}, status=500)

        # Find the newly generated document in the list and return it
        new_document = next((doc for doc in documents if doc['label'] == f"{file_name}"), None)

        if new_document:
            return JsonResponse(new_document)
        else:
            return JsonResponse({"error": "Failed to generate the document."}, status=500)

    except Exception as e:
        return JsonResponse({"error": f"An error occurred: {str(e)}"}, status=500)

