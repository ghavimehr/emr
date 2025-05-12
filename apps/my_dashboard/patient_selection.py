from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

from apps.emr.identity.models import Patient  

def patient_search(request):
    """Live search returning JSON."""
    query = request.GET.get('q', '').strip()

    if len(query) < 3:
        return JsonResponse([], safe=False)

    # Split query into individual terms based on space
    search_terms = query.split()

    # Create an initial query set for filtering
    patients_query = Patient.objects.all()

    # Apply filters for each term to match all fields using AND logic
    for term in search_terms:
        patients_query = patients_query.filter(
            Q(patient_id__icontains=term) |
            Q(ssn__icontains=term) |
            Q(first_name__icontains=term) |
            Q(last_name__icontains=term) |
            Q(tags__icontains=term)
        )

    # Limit the results to 10 (adjust as needed)
    patients = patients_query[:10]

    # Prepare the results to send in JSON format
    results = []
    for pat in patients:
        results.append({
            'id': pat.id,
            'patient_id': pat.patient_id,
            'first_name': pat.first_name,
            'last_name': pat.last_name,
            'ssn': pat.ssn,
        })
    
    return JsonResponse(results, safe=False)

@csrf_exempt
def select_patient(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        patient_db_id = data.get('patient_id')
        request.session['selected_patient_id'] = patient_db_id
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'error': 'invalid request'}, status=400)




# # patient_selection/views.py
# from django.db.models import Q
# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt
# import json
#
# from apps.emr.identity.models import Patient  # keep "Patient" in identity
#
# def patient_search(request):
#     """Live search returning JSON."""
#     query = request.GET.get('q', '').strip()
#     if len(query) < 3:
#         return JsonResponse([], safe=False)
#
#     # partial match on multiple fields
#     patients = Patient.objects.filter(
#         Q(patient_id__icontains=query) |
#         Q(ssn__icontains=query) |
#         Q(first_name__icontains=query) |
#         Q(last_name__icontains=query) |
#         Q(tags__icontains=query)
#     )[:10]
#
#     results = []
#     for pat in patients:
#         results.append({
#             'id': pat.id,
#             'patient_id': pat.patient_id,
#             'first_name': pat.first_name,
#             'last_name': pat.last_name,
#         })
#     return JsonResponse(results, safe=False)
#
# @csrf_exempt
# def select_patient(request):
#     if request.method == 'POST':
#         data = json.loads(request.body)
#         patient_db_id = data.get('patient_id')
#         request.session['selected_patient_id'] = patient_db_id
#         return JsonResponse({'status': 'ok'})
#     return JsonResponse({'error': 'invalid request'}, status=400)








#
# # my_dashboard/patient_selection.py
# from django.db.models import Q
# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt
# from django.shortcuts import redirect
# import json
#
# # Suppose your Patient model is also in my_dashboard/models.py
# from apps.emr.identity.models import Patient
#
# def patient_search(request):
#     query = request.GET.get('q', '').strip()
#     if len(query) < 3:
#         return JsonResponse([], safe=False)
#
#     # Example partial match across name, patient_id, ssn, tags:
#     patients = Patient.objects.filter(
#         Q(patient_id__icontains=query) |
#         Q(ssn__icontains=query) |
#         Q(first_name__icontains=query) |
#         Q(last_name__icontains=query) |
#         Q(tags__icontains=query)
#     ).order_by('first_name', 'last_name')[:10]
#
#     results = []
#     for pat in patients:
#         results.append({
#             'id': pat.id,
#             'patient_id': pat.patient_id,
#             'first_name': pat.first_name,
#             'last_name': pat.last_name,
#         })
#     return JsonResponse(results, safe=False)
#
# @csrf_exempt
# def select_patient(request):
#     if request.method == 'POST':
#         data = json.loads(request.body)
#         patient_db_id = data.get('patient_id')
#         request.session['selected_patient_id'] = patient_db_id
#         return JsonResponse({'status': 'ok'})
#     return JsonResponse({'error': 'invalid request'}, status=400)
