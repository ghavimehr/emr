# apps/emr/oneglance/views.py

import os, json, urllib, requests, base64, jwt, time, logging, subprocess, re
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

from apps.emr.identity.models import *
from apps.emr.rtms.utils import get_rtms_protcols
from apps.emr.files.utils import patient_documents
from apps.common.decorators import group_required



from apps.emr.files.models import Document

logger = logging.getLogger(__name__)



@csrf_exempt
@xframe_options_sameorigin
def oneglance_page(request):
    # Get patient from the session or raise 404 if not found
    patient_db_id = request.session.get("selected_patient_id")
    if not patient_db_id:
        return render(request, 'emr/oneglance/oneglance.html', {"patient": None, "pdfs": []})

    patient = get_object_or_404(Patient, id=patient_db_id)

    documents = patient_documents(
        request=request,
        patient=patient,
        document_type=1,
    )

    # ─── custom sort ────────────────────────────────────────────────────────────
    # 1) split into scan* vs. everything else
    scan_docs = []
    other_docs = []
    for doc in documents:
        title_l = doc['title'].lower()
        if title_l.startswith('scan'):
            scan_docs.append(doc)
        else:
            other_docs.append(doc)

    # 2) build a natural‐sort key
    def natural_key(doc):
        name = doc['title'][:-4]          # strip “.pdf”
        parts = re.split(r'(\d+)', name)  # split into digit vs non‐digit
        key = []
        for part in parts:
            if part.isdigit():
                key.append(int(part))
            else:
                key.append(part.lower())
        return tuple(key)

    # 3) detect “base” files (those whose name exactly matches the start
    #    of at least one other file + ‘-’ suffix)
    names = [d['title'][:-4].lower() for d in other_docs]
    def is_base(doc):
        nm = doc['title'][:-4].lower()
        return any(other.startswith(f"{nm}-") for other in names)

    # 4) sort “others” descending by (is_base, natural_key)
    #    → base files (True) come before variants (False), and
    #      natural_key is reversed for descending
    sorted_others = sorted(
        other_docs,
        key=lambda d: (is_base(d), natural_key(d)),
        reverse=False
    )

    # 5) sort scans ascending by natural_key
    sorted_scans = sorted(scan_docs, key=natural_key)

    # 6) recombine
    documents = sorted_others + sorted_scans
    # ────────────────────────────────────────────────────────────────────────────

    patient_rtms_protcols = get_rtms_protcols(patient)

    context = {
        'page_title'     : _("One-Glance"),
        'page_info'      : _("Patient's Summerized Data"),
        "patient": patient,

        "user_id": request.user.id,
        "user_name": request.user.get_full_name(),

        "documents": documents,
        "document_box_max_height": '200px',
        "document_box_title": "",
        "ds_host": settings.ONLYOFFICE_DOCSERVER_URL,
        "callbackUrl": settings.ONLYOFFICE_CALLBACK,
        "mode": "edit",


        "rtms_list":  patient_rtms_protcols,
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
        os.makedirs(patient_folder, exist_ok=True)

        # Generate the PDF filename (today's Jalali date)

        today_jalali = jdatetime.datetime.now().strftime("%Y-%m-%d")
        index = 0
        while True:
            if index == 0:
                file_name = today_jalali
            else:
                file_name = f"{today_jalali}—{index}"
            pdf_filename = f"{file_name}.pdf"
            pdf_path = os.path.join(patient_folder, "physician_notes", pdf_filename)
            if not os.path.exists(pdf_path):
                break
            index += 1



        # Define LaTeX template file path
        template_path = os.path.join(settings.BASE_DIR, "latex", "handwriting_pages.tex")


        # Generate LaTeX file path
        folder_path = os.path.join(settings.BASE_DIR, "data", str(patient.patient_id), "physician_notes")
        os.makedirs(folder_path, exist_ok=True)
        tex_file_path = os.path.join(folder_path, f"{file_name}.tex")



        # Copy the LaTeX template to the new location
        copyfile(template_path, tex_file_path)


        # # Prepare the patient data for LaTeX
        patient_data = {
            "base_dir": settings.BASE_DIR,
            # Basic fields
            "first_name": patient.first_name,
            "last_name": patient.last_name,
            "ssn": patient.ssn or "---",
            "birthday": patient.age or "---",
            "today": jdatetime.date.today().strftime("%Y/‌%m/‌%d") or "---",
            "patient_id": patient.patient_id or "---",
            "insurance": patient.insurances_display or "---",
        }

        logger.debug("Prepared patient_data for LaTeX injection: %r", patient_data)

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
        rel_path  = os.path.join(str(patient.patient_id), "physician_notes", f"{file_name}.pdf")

        # adding the newly generated PDF to DB
        new_doc = Document.objects.create(
            patient        = patient,
            relative_path  = rel_path,
            file_name      = f"{file_name}.pdf",
            file_extension_id = 1,     # 1 → PDF
            document_type_id = 1,      # 1 → physician note
            protocol_id = 1,
        )

        for ext in ["tex", "aux", "log"]:
            aux_file = os.path.join(settings.BASE_DIR, directory_path, str(patient.patient_id), "physician_notes", f"{file_name}.{ext}")
            if os.path.exists(aux_file):
                os.remove(aux_file)


        # Return the generated PDF details to the client
        documents = patient_documents(
            request=request,
            patient=patient,
            document_type=1,
        )

        if documents is None or len(documents) == 0:
            return JsonResponse({"error": "Failed to generate the document list."}, status=500)

        # Find the newly generated document in the list and return it
        expected = f"{file_name}.pdf"
        new_document = next((doc for doc in documents if doc['title'] == expected), None)

        if new_document:
            return JsonResponse(new_document)
        else:
            return JsonResponse({"error": "Failed to generate the document."}, status=500)

    except Exception as e:
        return JsonResponse({"error": f"An error occurred: {str(e)}"}, status=500)

