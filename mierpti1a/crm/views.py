from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.urls import reverse

from .models import FAQArticle
from .models import Ticket
from .formTicket import TicketForm
from .formComments import CommentForm
from .FormTicketsAdmin import TicketUpdateForm
from django.contrib.auth.decorators import login_required
from RRHH.models import Empleado

import json

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
def tickets(request):
    if request.method == 'POST':
        form = TicketForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False) 
            ticket.user = request.user 
            ticket.save() 
            return redirect('allTickets')  
    else:
        form = TicketForm()
    
    return render(request, 'crm/ticket.html', {'form': form})

#Vista para obtener los comentarios del ticket
@login_required
def solutions(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    comments = ticket.comments.all()
    
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.ticket = ticket
            comment.created_by = request.user 
            comment.save()
            return redirect('solutions', ticket_id=ticket.id)
    else:
        form = CommentForm()

    return render(request, 'crm/solutions.html', {
        'ticket': ticket,
        'comments': comments,
        'form': form,
    })

#Vista para mostrar todos los tickets
@login_required
def allTickets(request):
    tickets = Ticket.objects.filter(user=request.user)
    return render(request, 'crm/allTickets.html', {'tickets': tickets})




#Vistas para los del equipo de soporte de los tickets

#Vista para mostrar todo los tickets
@login_required
def allTicketsAdmin(request):
    if request.method == 'POST':
        for ticket in Ticket.objects.all():
            status = request.POST.get(f'status_{ticket.id}')
            assigned_to_id = request.POST.get(f'assigned_to_{ticket.id}')
            
            if status:
                ticket.status = status

            if assigned_to_id:
                assigned_to = Empleado.objects.get(id=assigned_to_id)
                ticket.assigned_to = assigned_to
            else:
                ticket.assigned_to = None

            ticket.save()

        return HttpResponseRedirect(reverse('controlPanel'))
    else:
        tickets = Ticket.objects.all()
        status_choices = Ticket._meta.get_field('status').choices
        empleados = Empleado.objects.all()

        return render(request, 'admin/controlPanel.html', {
            'tickets': tickets,
            'status_choices': status_choices,
            'empleados': empleados,
        })