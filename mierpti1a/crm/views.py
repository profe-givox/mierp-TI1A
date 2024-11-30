from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse

from .models import FAQArticle
from .models import Ticket
from .formTicket import TicketForm
from django.contrib.auth.decorators import login_required

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



#Vista para agregar y editar tickets
@login_required
def tickets(request, ticket_id=None):
    if ticket_id:  
        ticket = get_object_or_404(Ticket, id=ticket_id, user=request.user)
        if request.method == 'POST':
            form = TicketForm(request.POST, instance=ticket) 
            if form.is_valid():
                form.save()
                return redirect('allTickets') 
        else:
            form = TicketForm(instance=ticket) 
    else: 
        if request.method == 'POST':
            form = TicketForm(request.POST) 
            if form.is_valid():
                new_ticket = form.save(commit=False)
                new_ticket.user = request.user
                new_ticket.save()
                return redirect('allTickets') 
            form = TicketForm() 
    return render(request, 'crm/ticket.html', {
        'form': form,
        'editing': bool(ticket_id)  
    })

#Vista para mostrar todos los tickets
@login_required
def allTickets(request):
    tickets = Ticket.objects.filter(user=request.user)
    return render(request, 'crm/allTickets.html', {'tickets': tickets})