from apps.emr.identity.models import Patient

def selected_patient(request):
    patient_db_id = request.session.get('selected_patient_id')
    if not patient_db_id:
        return {'selected_patient': None}
    try:
        pat = Patient.objects.get(id=patient_db_id)
        return {'selected_patient': pat}
    except Patient.DoesNotExist:
        return {'selected_patient': None}
