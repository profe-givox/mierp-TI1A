from django.shortcuts import render
from django.http import HttpResponse

def index(request):
    return render(request, 'index.html')

def pagos(request):
    return render(request, 'pagos.html')

def cuentas(request):
    return render(request, 'cuentas.html')

def disputas(request):
    return render(request, 'disputas.html')

def informes(request):
    return render(request, 'informes.html')
