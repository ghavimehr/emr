import os, traceback
import anthropic
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.template import RequestContext
from django.conf import settings
from datetime import datetime
from apps.common.models import Products, Profile, Article, Newsletter, Prompt, CustomDevelopment, ProjectTypeChoices, BudgetRangeChoices, Ticket
from django.contrib import messages
from apps.support.forms import SupportForm
from django.urls import reverse
from django.core.mail import send_mail
from django.http import HttpResponsePermanentRedirect
# Create your views here.

# LOGGER & Events
from inspect import currentframe
from helpers.logger import *
from helpers.events import *

from helpers.generator.common import *
from helpers.util import file_exists

def index(request):

  # Logger
  func_name  = sys._getframe().f_code.co_name 
  logger( f'[{__name__}->{func_name}(), L:{currentframe().f_lineno}] ' + 'Begin' )

  products = Products.objects.all().order_by('-updated_at')[:3]
  blogs = Article.objects.all().order_by('-created_at')[:3]
  
  context = {
    'segment'        : 'home',
    'page_title'     : request.branding.slogan1,
    'page_info'      : request.branding.slogan2,
    'page_keywords'  : '',
    'page_canonical' : '',
    'products'       : products ,
    'articles'       : blogs,
  }

  return render(request, 'pages/home2.html', context)

def onboarding(request):

  # Logger
  func_name  = sys._getframe().f_code.co_name 
  logger( f'[{__name__}->{func_name}(), L:{currentframe().f_lineno}] ' + 'Begin' )

  context = {
    'segment'        : 'onboarding',
    'page_title'     : 'Onboarding Kit - Resources for students, solo-developers and companies to accomodate with our products and services',
    'page_info'      : 'The kit includes dev tools, production-ready starters and high priority on support.',
    'page_keywords'  : 'onboarding kit, resources for developers, dev tools, premium starters',
    'page_canonical' : 'onboarding-kit/',
  }

  return render(request, 'pages/onboarding-kit.html', context)

def show_dashboard(request):
  products = Products.objects.all()
  products_list = list(products.values())
  return JsonResponse({'products': products_list})

def custom_development(request):

  # Logger
  func_name  = sys._getframe().f_code.co_name 
  logger( f'[{__name__}->{func_name}(), L:{currentframe().f_lineno}] ' + 'Begin' )

  if not request.user.is_authenticated:
    messages.error(request, "You're not authenticated. Please Sign IN")

  if request.method == 'POST':
    form_data = {}
    for attribute, value in request.POST.items():
      if attribute == 'csrfmiddlewaretoken':
        continue

      form_data[attribute] = value
    
    CustomDevelopment.objects.create(**form_data)

    return redirect(request.META.get('HTTP_REFERER'))

  context = {
    'segment'        : 'custom_development',
    'page_title'     : 'Custom Development - Need help Coding an MVP or a Complete Solution? ',
    'page_info'      : 'Get Custom Development Services from a team of experts.',
    'page_keywords'  : 'custom development, custom tools, custom generators, app generator, dashboards, web apps, generated products',
    'page_canonical' : 'custom-development/',
    'project_types'  : ProjectTypeChoices.choices,
    'budget_range'   : BudgetRangeChoices.choices
  }

  return render(request, 'pages/custom-development.html', context)

def terms(request):

  # Logger
  func_name  = sys._getframe().f_code.co_name 
  logger( f'[{__name__}->{func_name}(), L:{currentframe().f_lineno}] ' + 'Begin' )

  context = {
    'segment'        : 'terms',
    'page_title'     : 'Terms - Learn how to use the App-Generator Service',
    'page_info'      : 'AppSee/App-generator Terms of Use',
    'page_keywords'  : 'terms, service terms, AppSeed terms, App-Generator Terms',
    'page_canonical' : 'terms/',
  }

  return render(request, 'pages/terms.html', context)

def about(request):

  # Logger
  func_name  = sys._getframe().f_code.co_name 
  logger( f'[{__name__}->{func_name}(), L:{currentframe().f_lineno}] ' + 'Begin' )

  context = {
    'segment'        : 'about',
    'page_title'     : 'About US - Learn more about the team and the mission ',
    'page_info'      : 'More inputs regarding AppSee/App-generator service',
    'page_keywords'  : 'about, about AppSeed, about App-Generator',
    'page_canonical' : 'about/',
  }

  return render(request, 'pages/about.html', context)

def user_profile(request, username):
  profile = get_object_or_404(Profile, user__username=username)
  context = {
    'profile': profile
  }
  return render(request, 'pages/profile.html', context)

def support(request):

  # Logger
  func_name  = sys._getframe().f_code.co_name 
  logger( f'[{__name__}->{func_name}(), L:{currentframe().f_lineno}] ' + 'Begin' )

  if request.method == 'POST':
    form_data = {}
    form_data['user'] = request.user
    for attribute, value in request.POST.items():
      if attribute == 'csrfmiddlewaretoken':
        continue
        
      form_data[attribute] = value
    
    ticket = Ticket.objects.create(**form_data)

    subject = f"App-Generator: {ticket.title}"
    ticket_link = request.build_absolute_uri(reverse('comment_to_ticket', args=[ticket.pk]))
    message = (
      "Hello,\n\n"
      "Your issue has been updated.\n"
      f"Please check the status by accessing this link:\n{ticket_link}\n\n"
      "Thank you!\n"
      "< App-Generator.dev > Support"
    )
    send_mail(
      subject,
      message,
      getattr(settings, 'EMAIL_HOST_USER'),
      [getattr(settings, 'EMAIL_HOST_USER')],
      fail_silently=False,
    )

    return redirect(request.META.get('HTTP_REFERER'))

  if not request.user.is_authenticated:
    messages.error(request, "You're not authenticated. Please Sign IN")

  context = {
    'segment'        : 'support',
    'page_title'     : 'Premium Support via email (support@appseed.us) and Discord',
    'page_info'      : 'Get Support for Dashboards, eCommerce, Presentation Websites',
    'page_keywords'  : 'support, email support, Discord support, Tickets, app generator, dashboards, web apps, generated products, custom development',
    'page_canonical' : 'support/',
    'form'           : SupportForm()
  }

  return render(request, 'pages/support.html', context)


def newsletter(request):
  if request.user.is_authenticated:
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
      email = request.POST.get('email')
      if not Newsletter.objects.filter(email=email).exists():
        Newsletter.objects.create(email=email)
        return JsonResponse({'success': True, 'message': 'You are subscribed!'})
      else:
        return JsonResponse({'success': False, 'message': 'Email is already subscribed!'})
    return JsonResponse({'success': False, 'message': 'Invalid request method.'})
  else:
    return JsonResponse({'success': False, 'message': 'User not authenticated.'})


def create_prompt(request):

  api_key = getattr(settings, 'ANTHROPIC_API_KEY')
  client = anthropic.Anthropic(api_key=api_key)

  user_id = request.user.pk if request.user.is_authenticated else -1

  questions_asked = request.session.get('questions_asked', 0)

  #print(' > AI Questions: ' + str( questions_asked )) 

  if request.user.is_authenticated:

    if questions_asked >= settings.LIMIT_AI_PROMPT_AUTH:
      
      purchase_pro_url = 'https://emr.drarzaghi.com'
      terms_url = reverse('terms')

      response_message  = f'Limit reached. Please <a class="gumroad text-white font-bold" href="{purchase_pro_url}">Upgrade to PRO</a> to ask more questions. <br />'
      response_message += f'<a target="_blank" class="text-white font-bold" href="{terms_url}#pro-account">The benefits</a> being a PRO user are explained in the terms page.' 

      return JsonResponse({'reply': response_message})

  else:

    if questions_asked >= settings.LIMIT_AI_PROMPT_GUEST:

      login_url = reverse('signin')
      terms_url = reverse('terms')

      response_message = f'Limit reached. Please <a class="text-white font-bold" href="{login_url}">login</a> to ask more questions.'

      return JsonResponse({'reply': response_message})

  if request.method == 'POST':

    request.session['questions_asked'] = questions_asked + 1

    question     = request.POST.get('question')
    question_ctx = f"Please provide a text, short answer (maximum 2 sentences) to the following question that should always related to programming and software: {question}"

    response = client.messages.create(
      model="claude-3-5-sonnet-20241022",
      max_tokens=1024,
      messages=[
        {"role": "user", "content": question_ctx}
      ]
    )

    reply_text = response.content[0].text

    Prompt.objects.create(question=question, response=reply_text, user_id=user_id)

    return JsonResponse({'reply': reply_text})

  return redirect(request.META.get('HTTP_REFERER'))

def download_app(request, taskID):

  # check file exists:
  app_zip   = os.path.join( DIR_GEN_APPS, taskID + '.zip' )
  not_found = os.path.join( DIR_GEN_APPS, 'not_found.txt' )
  
  if COMMON.OK == file_exists( app_zip ):
    response = HttpResponse( open( app_zip  ,  'rb').read(), status=200)
    response['Content-Type'] = 'application/x-zip-compressed'
    response['Content-Disposition'] = 'attachment; filename='+taskID+'.zip'
  else:
    response = HttpResponse( open( not_found, 'rb').read(), status=200)
    response['Content-Disposition'] = 'attachment; filename=not_found.txt'

  return response
   
def download_product(request, productID):
  pass

# page_not_found
def handler404(request, *args, **argv):
                                   
  # Logger
  func_name  = sys._getframe().f_code.co_name 
  logger( f'[{__name__}->{func_name}(), L:{currentframe().f_lineno}] ' + 'Begin' )

  try: 

    # apply redirect
    if request.path in settings.REDIRECTS:
      return HttpResponsePermanentRedirect( settings.REDIRECTS[ request.path ] )

    if 'exception' in argv:
      event_404(request, str( argv['exception'] ) )
    else:
      event_404(request, str( argv ) )

  except Exception as e:
    pass

  context = {
    'page_title': 'Error 404 - Page not foumd',
  }

  return render(request, 'pages/error-404.html', context, status=404)

# server_error 
def handler500(request, *args, **argv):

  # Logger
  func_name  = sys._getframe().f_code.co_name 
  logger( f'[{__name__}->{func_name}(), L:{currentframe().f_lineno}] ' + 'Begin' )

  try: 
    
    exc_type, exc_value, exc_traceback = sys.exc_info()
    if exc_value:
      error_message = f"{str(exc_value)}"
      stack_trace = traceback.format_exc()
      event_500(request, error_message + "\n" + stack_trace)

  except Exception as e:
    pass
  
  context = {
    'page_title': 'Error 500 - Server Error',
  }

  return render(request, 'pages/error-500.html', context, status=500)

# bad_request
def handler400(request, *args, **argv):

  # Logger
  func_name  = sys._getframe().f_code.co_name 
  logger( f'[{__name__}->{func_name}(), L:{currentframe().f_lineno}] ' + 'Begin' )

  print (' > args:' + str(args) )
  print (' > argv:' + str(argv) )

  context = {
    'page_title': 'Error 400 - Bad Request',
  }

  return render(request, 'pages/error-400.html', context, status=400)

# permission_denied
def handler403(request, *args, **argv):

  # Logger
  func_name  = sys._getframe().f_code.co_name 
  logger( f'[{__name__}->{func_name}(), L:{currentframe().f_lineno}] ' + 'Begin' )
  
  print (' > args:' + str(args) )
  print (' > argv:' + str(argv) )

  context = {
    'page_title': 'Error 404 - Permission Denied',
  }

  return render(request, 'pages/error-403.html', context, status=403)
