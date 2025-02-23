from django.http import JsonResponse
import datetime

def welcome(request):
    return JsonResponse({'message': 'Welcome to Django with React!'})

def get_login_message(request):
    now = datetime.datetime.now()
    message = f"Welcome to the Login Page! Current time from Django: {now}"
    return JsonResponse({"message": message})

def get_search_message(request):
    now = datetime.datetime.now()
    message = f"Welcome to the Login Page! Current time from Django: {now}"
    return JsonResponse({"message": message})
