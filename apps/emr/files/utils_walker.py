# apps/emr/files/utils.py

import os
import fnmatch
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist

from django.conf import settings
from apps.emr.identity.models import Patient
from apps.emr.files.models import (
    Document,
    DocumentType,
    ProtocolAssignment,
    FileExtension,
)


def update_document_index(base_path=None):
    """
    Walk <base_path>/<patient_id>[/<subfolder>/...] and upsert Document rows.
    Protocol is determined by matching rel_path against ProtocolAssignment.path_pattern.
    Files without any matching ProtocolAssignment are skipped.
    """
    base_path = base_path or settings.PATIENT_DATA

    # 1) Load all protocol assignments once, in pattern order
    assignments = list(
        ProtocolAssignment.objects
            .select_related('protocol')
            .order_by('path_pattern')
    )

    # 2) Load your default DocumentType (pk=1)
    default_doc_type = DocumentType.objects.get(pk=1)

    stats = {
        'created': 0,
        'updated': 0,
        'skipped_no_protocol': 0,
        'skipped_no_patient': 0,
        'deleted': 0,
    }

    seen = set()

    # 3) Walk each patient folder
    for patient_dir in sorted(os.listdir(base_path)):
        patient_path = os.path.join(base_path, patient_dir)
        if not os.path.isdir(patient_path):
            continue

        # Lookup Patient by your patient_id field (not PK)
        try:
            patient = Patient.objects.get(patient_id=patient_dir)
        except ObjectDoesNotExist:
            stats['skipped_no_patient'] += 1
            continue

        # 4) Recurse into subfolders and files
        for root, dirs, files in os.walk(patient_path):
            rel_root = os.path.relpath(root, base_path)  # e.g. "628/reports"
            parts    = rel_root.split(os.sep)
            subfolder = rel_root.split(os.sep)[1] if os.sep in rel_root else None


            # Resolve DocumentType (prompt logic omitted for brevity)
            try:
                doc_type = DocumentType.objects.get(
                    representative_relative_path=subfolder
                ) if subfolder else default_doc_type
            except DocumentType.DoesNotExist:
                doc_type = default_doc_type

            for fname in files:
                rel_path = os.path.join(rel_root, fname)  # e.g. "628/reports/scan.pdf"
                seen.add(rel_path)
                # 5) Find the first matching protocol
                protocol = None
                for pa in assignments:
                    if fnmatch.fnmatch(rel_path, pa.path_pattern):
                        protocol = pa.protocol
                        break

                if protocol is None:
                    stats['skipped_no_protocol'] += 1
                    continue

                # 6) Determine or create the FileExtension
                ext = os.path.splitext(fname)[1].lstrip('.').lower()
                ext_obj, _ = FileExtension.objects.get_or_create(
                    code=ext,
                    defaults={'name': ext.upper()}
                )

                # 7) Upsert the Document row
                with transaction.atomic():
                    doc, created = Document.objects.update_or_create(
                        patient=patient,
                        relative_path=rel_path,
                        defaults={
                            'file_extension':  ext_obj,
                            'protocol':        protocol,
                            'document_type':   doc_type,
                            'file_name':       fname,
                        }
                    )
                    if created:
                        stats['created'] += 1
                    else:
                        # detect any FK or filename change
                        changed = False
                        for field, val in (
                            ('file_extension', ext_obj),
                            ('protocol',       protocol),
                            ('document_type',  doc_type),
                            ('file_name',      fname),
                        ):
                            if getattr(doc, field) != val:
                                setattr(doc, field, val)
                                changed = True
                        if changed:
                            doc.save(update_fields=[
                                'file_extension',
                                'protocol',
                                'document_type',
                                'file_name'
                            ])
                            stats['updated'] += 1


    stale = Document.objects.exclude(relative_path__in=seen)
    stats['deleted'] = stale.count()
    stale.delete()

    # 8) Summary
    print(
        f"Indexing complete: {stats['created']} created, "
        f"{stats['updated']} updated, "
        f"{stats['deleted']} deleted, "
        f"{stats['skipped_no_protocol']} skipped (no protocol), "
        f"{stats['skipped_no_patient']} skipped (no patient)"
    )
    return stats
