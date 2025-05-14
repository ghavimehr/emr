# # apps/emr/files/views.py

# import os, logging, ipaddress, mimetypes, time, base64, json, jwt, requests


# from django.conf import settings
# from django.http import FileResponse, Http404, HttpResponseForbidden, JsonResponse
# from django.views.decorators.csrf import csrf_exempt
# from django.views.decorators.clickjacking import xframe_options_sameorigin


# logger = logging.getLogger(__name__)

# # pre-compute allowed networks from your settings
# _ALLOWED_NETWORKS = [
#     ipaddress.ip_network(net) for net in getattr(settings, "ONLYOFFICE_ALLOWED_IPS", [])
# ]

# @csrf_exempt
# @xframe_options_sameorigin
# def serve_patient_file(request, path):
#     """
#     Streams back the file at PATIENT_DATA/<path> if the
#     request carries a valid JWT or comes from an allowed IP / authenticated user.
#     """

#     client_ip    = request.META.get("REMOTE_ADDR", "")
#     auth_header  = request.META.get("HTTP_AUTHORIZATION", "")
#     logger.info(
#         "SERVE_PATIENT_FILE ➞ REMOTE_ADDR=%s  AUTHORIZATION=%s  path=%s",
#         client_ip,
#         auth_header or "<none>",
#         path,
#     )

#     # 1) If they sent a Bearer token, validate it first
#     if auth_header.startswith("Bearer "):
#         token = auth_header.split(" ", 1)[1]
#         try:
#             jwt.decode(token, settings.ONLYOFFICE_JWT_SECRET, algorithms=["HS256"])
#         except jwt.PyJWTError as e:
#             logger.warning("Invalid JWT in serve_patient_file: %s", e)
#             return HttpResponseForbidden("Forbidden: invalid token")
#     else:
#         # 2) No JWT: fall back to IP-based or user-based auth
#         try:
#             addr = ipaddress.ip_address(client_ip)
#         except ValueError:
#             return HttpResponseForbidden("Forbidden: invalid IP format")

#         if not any(addr in net for net in _ALLOWED_NETWORKS):
#             # not from an allowed OnlyOffice IP, so require a logged-in user
#             if not request.user.is_authenticated:
#                 return HttpResponseForbidden("Forbidden: login required")

#     # 3) Resolve and serve the file
#     file_path = os.path.join(settings.PATIENT_DATA, path)
#     if not os.path.exists(file_path):
#         raise Http404(f"File not found: {path}")

#     content_type, _ = mimetypes.guess_type(file_path)
#     response = FileResponse(open(file_path, "rb"), content_type=content_type or "application/octet-stream")
#     response["Accept-Ranges"] = "bytes"
#     return response


# @csrf_exempt
# def onlyoffice_callback(request):
#     """
#     ONLYOFFICE save callback:
#      - status=2 means “please save the edited doc”
#      - key is our base64(patient_id/filename)
#      - url is where the new file lives on the Docs server
#     """
#     try:
#         data = json.loads(request.body.decode())
#     except json.JSONDecodeError:
#         return JsonResponse({"error": 1, "message": "Invalid JSON"}, status=400)

#     status = data.get("status")
#     if status in (2, 3, 6, 7):
#         file_url = data.get("url")   # updated file URL on DocumentServer
#         key      = data.get("key")   # base64("patient_id/filename")

#         # Decode key to get patient_id and filename
#         try:
#             raw = base64.urlsafe_b64decode(key.encode()).decode()
#             patient_id, filename = raw.split("/", 1)
#         except Exception as e:
#             logger.error("ONLYOFFICE callback: bad key %r (%s)", key, e)
#             return JsonResponse({"error": 1, "message": "Bad document key"}, status=400)

#         # Build local path
#         local_dir  = os.path.join(settings.PATIENT_DATA, patient_id)
#         local_path = os.path.join(local_dir, filename)
#         if not os.path.isdir(local_dir):
#             logger.error("ONLYOFFICE callback: directory %s does not exist", local_dir)
#             raise Http404

#         # ——————————————
#         #  Fetch the edited file *with* JWT auth
#         # ——————————————
#         # 1) Build a short‐lived JWT for this download
#         jwt_payload = {
#             "url": file_url,
#             "key": key,
#             "exp": int(time.time()) + 300,   # valid for 5 minutes
#         }
#         download_token = jwt.encode(
#             jwt_payload,
#             settings.ONLYOFFICE_JWT_SECRET,
#             algorithm="HS256"
#         )
#         # PyJWT may return bytes in older versions
#         if isinstance(download_token, bytes):
#             download_token = download_token.decode("utf-8")

#         # 2) Send the Authorization header
#         headers = {"Authorization": f"Bearer {download_token}"}

#         try:
#             resp = requests.get(file_url, headers=headers, timeout=30)
#             resp.raise_for_status()
#         except Exception as e:
#             logger.error("ONLYOFFICE callback: failed to download %s (%s)", file_url, e)
#             return JsonResponse({"error": 1, "message": "Cannot fetch updated file"}, status=502)

#         # 3) Overwrite the local file
#         with open(local_path, "wb") as fout:
#             fout.write(resp.content)
#         logger.info("ONLYOFFICE callback: saved updated document to %s", local_path)

#     # ALWAYS reply { error: 0 } so ONLYOFFICE knows you got it
#     return JsonResponse({"error": 0})

import os
import time
import uuid
import logging
import json
import requests
import jwt
import fnmatch
from django.conf import settings
from django.http import JsonResponse, Http404, FileResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.clickjacking import xframe_options_sameorigin
from django.conf import settings
from django.utils.dateparse import parse_datetime


from .models import *

logger = logging.getLogger(__name__)

callbackUrl = settings.ONLYOFFICE_CALLBACK

def patient_documents(
    request,
    patient,
    *,
    file_name: str = None,
    document_type: int = None,
    protocol: int = None,
    extension: str = None,
    exclude: str = None,
    created_from: str = None,
    created_to: str = None,
    updated_from: str = None,
    updated_to: str = None,
):
    """
    Old name = document_box_generator()
    Returns a LIST of OnlyOffice payload dicts for all Documents
    belonging to `patient`, optionally filtered by any of:
      • file_name (substring)
      • document_type (FK id)
      • protocol (FK id)
      • extension (file_extension.code)
      • exclude (comma-separated file_name values)
      • created_from / created_to (ISO datetimes)
      • updated_from / updated_to (ISO datetimes)

    You can pass filters here as kwargs, or omit them and rely on request.GET.
    """
    qs = Document.objects.filter(patient=patient)

    # capture all kw-args into a dict for lookup
    param_map = {
        'file_name':      file_name,
        'document_type':  document_type,
        'protocol':       protocol,
        'extension':      extension,
        'exclude':        exclude,
        'created_from':   created_from,
        'created_to':     created_to,
        'updated_from':   updated_from,
        'updated_to':     updated_to,
    }

    def _param(name):
        # first check if caller passed it as a kwarg
        val = param_map.get(name)
        if val is not None:
            return val
        # otherwise fall back to GET
        return request.GET.get(name)

    # 1) file_name substring
    fn_val = _param('file_name')
    if fn_val:
        qs = qs.filter(file_name__icontains=fn_val)

    # 2) document_type FK
    dt_val = _param('document_type')
    if dt_val:
        qs = qs.filter(document_type_id=dt_val)

    # 3) protocol FK
    pr_val = _param('protocol')
    if pr_val:
        qs = qs.filter(protocol_id=pr_val)

    # 4) extension (file_extension.code)
    ex_val = _param('extension')
    if ex_val:
        qs = qs.filter(file_extension__code__iexact=ex_val)

    # 5) exclude specific filenames
    excl = _param('exclude')
    if excl:
        for name in excl.split(','):
            qs = qs.exclude(file_name__iexact=name.strip())

    # 6) created_at window
    cf = _param('created_from')
    if cf:
        dt = parse_datetime(cf)
        if dt:
            qs = qs.filter(created_at__gte=dt)
    ct = _param('created_to')
    if ct:
        dt = parse_datetime(ct)
        if dt:
            qs = qs.filter(created_at__lte=dt)

    # 7) updated_at window
    uf = _param('updated_from')
    if uf:
        dt = parse_datetime(uf)
        if dt:
            qs = qs.filter(updated_at__gte=dt)
    ut = _param('updated_to')
    if ut:
        dt = parse_datetime(ut)
        if dt:
            qs = qs.filter(updated_at__lte=dt)

    # 8) final ordering
    qs = qs.order_by('relative_path')

    # 9) build payloads & log view access
    documents = []
    for doc in qs:
        payload = generate_document_payload(doc, request.user, request)
        documents.append(payload)
        record_access(doc, request.user, action='view')

    return documents



# -- Helper functions --

def get_effective_permissions(user, document):
    """
    Return a dict of OnlyOffice permission flags for this user-document pair,
    OR-merging all the user's groups under the document's protocol.
    """
    return document.protocol.get_perms_for_user(user)


def get_document_key(document):
    """Use the Document's UUID as the DS key"""
    constant_key = str(document.id) # UUID
    version  = int(time.time() * 1000)
    version_key = f"{constant_key}_{version}" # needed for OnlyOffice
    return {
        'constant_key' : constant_key,
        'version' : version,
        'version_key' : version_key,
    }


def get_document_url(document, request):
    """Build the absolute URL for DS to fetch the file"""
    rel = reverse('files:serve_patient_file', kwargs={'key': document.id})
    return request.build_absolute_uri(rel)



def generate_document_payload(document, user, request):
    """
    Build the OnlyOffice editor payload (key, url, token, permissions)
    for a single Document instance.
    """
    permissions = get_effective_permissions(user, document)
    mode = 'edit' if permissions.get('edit') else 'view'
    key = get_document_key(document)
    url = get_document_url(document, request)
    callbackUrl = settings.ONLYOFFICE_CALLBACK
    title = document.file_name
    ext = document.file_extension.code          # e.g. 'pdf', 'docx', etc.

    payload_jwt = {
        'iat': int(time.time()),
        'exp': int(time.time()) + getattr(settings, 'ONLYOFFICE_JWT_EXPIRE', 7200),
        "referenceData": {"fileKey": key['constant_key'] },
        'document': {
            'key': key['version_key'],
            'url': url,
            'fileType': ext,
            'title': title,
            'permissions': permissions,
        },
        'documentType': ext,
        'editorConfig': {
            'mode': mode,
            'callbackUrl': settings.ONLYOFFICE_CALLBACK,
        },
        'user': {
            'id': str(user.id),
            'name': user.get_full_name(),
        },
    }
    token = jwt.encode(payload_jwt, settings.ONLYOFFICE_JWT_SECRET, algorithm='HS256')
    if isinstance(token, bytes):
        token = token.decode()

    return {
        'key':         key['version_key'],
        'referenceData': key['constant_key'],
        'url':         url,
        'token':       token,
        'permissions': permissions,
        'extension':   ext,           # so your front end knows the file type
        'title':       title,
        'documentType': document.document_type.name,  # optional: show the folder/category
    }


def record_access(document, user, action, info=None):
    """Log every view/edit/save action in DocumentAccessLog"""
    DocumentAccessLog.objects.create(
        document=document,
        user=user if user.is_authenticated else None,
        action=action,
        info=info or {}
    )

