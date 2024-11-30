from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse

from .models import FAQArticle
from .models import Ticket
from .formTicket import TicketForm
from .formComments import CommentForm
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