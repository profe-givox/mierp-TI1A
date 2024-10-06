from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def home(request):
    return render(request, 'crm/home.html')

def faqs(request):
    return render(request, 'crm/faqs.html')