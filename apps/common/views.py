from django.http import HttpResponse
from django.shortcuts import render
from datetime import datetime
from django.utils.translation import activate
from django.shortcuts import redirect
from django.utils.translation import get_language

def switch_language(request, lang_code):
    activate(lang_code)
    return redirect(request.META.get('HTTP_REFERER', '/'))

