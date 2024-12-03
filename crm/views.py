from django.shortcuts import render
from django.http import HttpResponse

from .models import FAQArticle

# Create your views here.
def home(request):
    # Obtener todos los artículos FAQ
    faq_articles = FAQArticle.objects.all()
    
    # Pasar los artículos al contexto de la plantilla
    return render(request, 'crm/home.html', {'faq_articles': faq_articles})

def faqs(request):
    faq_articles = FAQArticle.objects.filter(category__name="FAQs")  # Filtra por categoría "faqs"
    return render(request, 'crm/faqs.html', {'faq_articles': faq_articles})

def comunity(request):
    return render(request, 'crm/comunity.html')