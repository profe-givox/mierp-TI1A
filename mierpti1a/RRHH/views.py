from unittest import loader
from django.http import HttpResponse
from django.shortcuts import render


def horario(request):
    return render(request, 'RRHH/horario.html')