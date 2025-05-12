import os
import json
import time
import uuid
import logging
import ipaddress
import jwt
import mimetypes
import requests

from django.conf       import settings
from django.http       import (
    FileResponse, Http404, HttpResponseForbidden,
    HttpResponseServerError, JsonResponse
)
from django.urls       import reverse
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.clickjacking import xframe_options_sameorigin

from apps.emr.files.models import Document
from apps.emr.files.utils  import record_access



logger = logging.getLogger(__name__)

@csrf_exempt
@xframe_options_sameorigin
def serve_patient_file(request, key):

    # some logging featurs
    # print(">>> REMOTE_ADDR:", request.META.get("REMOTE_ADDR"))
    # print(">>> HTTP_X_FORWARDED_FOR:", request.META.get("HTTP_X_FORWARDED_FOR"))
    # print(">>> HTTP_X_REAL_IP:", request.META.get("HTTP_X_REAL_IP"))

    try:
        client_ip = request.META.get("REMOTE_ADDR", "")


        # the following two lines remove the ":port" from the client_ip
        if ":" in client_ip:
            client_ip = client_ip.split(":")[0] 



        # (1) IP allow list
        try:
            addr = ipaddress.ip_address(client_ip)
        except ValueError:
            return HttpResponseForbidden("Forbidden: invalid IP")

        allowed = any(
            addr in ipaddress.ip_network(net)
            for net in settings.ONLYOFFICE_ALLOWED_IPS
        )

        # (2) JWT fallback
        if not allowed:
            auth = request.headers.get("Authorization", "")
            if not auth.startswith("Bearer "):
                return HttpResponseForbidden("Forbidden: token missing")
            token = auth.split(" ", 1)[1]
            try:
                payload = jwt.decode(
                    token,
                    settings.ONLYOFFICE_JWT_SECRET,
                    algorithms=["HS256"],
                    options={"require": ["exp","iat","key"]},
                )
            except jwt.PyJWTError as exc:
                logger.warning("JWT decode failed: %s", exc)
                return HttpResponseForbidden("Forbidden: bad token")
            if payload.get("key") != key:
                return HttpResponseForbidden("Forbidden: key mismatch")

        # (3) Lookup document
        try:
            doc = Document.objects.get(id=key)
        except Document.DoesNotExist:
            raise Http404("No such document")

        # (4) File on disk?
        path = os.path.join(settings.PATIENT_DATA, doc.relative_path)
        if not os.path.exists(path):
            raise Http404("File not found on disk")

        # (5) Audit
        # record_access(
        #     document=doc,
        #     user=None,  # or pull user from payload if you fetched it earlier
        #     action="download",
        #     info={"ip": client_ip, "time": now().isoformat(), "by_ip": allowed}
        # )

        # (6) Stream it
        content_type, _ = mimetypes.guess_type(path)
        resp = FileResponse(open(path, "rb"),
                             content_type=content_type or "application/octet-stream")
        resp["Accept-Ranges"] = "bytes"
        return resp

    except Exception as e:
        # catch any unexpected error, log the stack trace, return 500
        logger.exception("Error serving patient file %r from %s", key, client_ip)
        return HttpResponseServerError("Internal Server Error")





# -- Callback endpoint for Document Server --
@csrf_exempt
def onlyoffice_callback(request):
    """
    Handles DS save callbacks. Records edits and saves updated files back to disk.
    """
    try:
        data = json.loads(request.body.decode())
    except json.JSONDecodeError:
        return JsonResponse({'error':1,'message':'Invalid JSON'}, status=400)

    status = data.get('status')
    # statuses with updated URL payload
    if status in (2, 6):

        file_url = data.get('url')
        raw_key = data.get("key", "")
        # lookup document by UUID key
        try:
            constant_key = raw_key.split("_", 1)[0]
            doc_id = uuid.UUID(constant_key)
            doc = Document.objects.get(id=doc_id)
        except (Document.DoesNotExist, ValueError):
            return JsonResponse({'error':1,'message':'Bad document key'}, status=400)

        # fetch the updated file
        token_payload = {'url': file_url, 'exp': int(time.time())+300}
        download_token = jwt.encode(token_payload, settings.ONLYOFFICE_JWT_SECRET, algorithm='HS256')
        if isinstance(download_token, bytes):
            download_token = download_token.decode()
        headers = {'Authorization': f'Bearer {download_token}'}

        try:
            resp = requests.get(file_url, headers=headers, timeout=60)
            resp.raise_for_status()
        except Exception as e:
            logger.error('Callback download failed: %s', e)
            return JsonResponse({'error':1,'message':'Fetch failed'}, status=502)

        # write to host disk
        local_path = os.path.join(settings.PATIENT_DATA, doc.relative_path)
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        with open(local_path, 'wb') as f:
            f.write(resp.content)
        record_access(doc, request.user, 'save' if status==6 else 'edit', info={'status':status})

    # always acknowledge
    return JsonResponse({'error':0})
