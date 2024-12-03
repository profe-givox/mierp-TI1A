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
from .models import *
from crm.models import ChatGroup, GroupMessage
from django.http import Http404
from .forms import ChatmessageCreateForm
import shortuuid

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Reseña
from .serializers import ReseñaSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated

# Create your views here.
def home(request):
    # Obtener todos los artículos FAQ
    faq_articles = FAQArticle.objects.all()
    
    # Pasar los artículos al contexto de la plantilla
    return render(request, 'crm/home.html', {'faq_articles': faq_articles})


def faqs(request):
    faq_articles = FAQArticle.objects.filter(category__name="FAQs")  # Filtra por categoría "faqs"
    return render(request, 'crm/faqs.html', {'faq_articles': faq_articles})


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
#Vistas de chat
@login_required
def chat_view(request, chatroom_name='public-chat'):
    # Obtener el grupo de chat o lanzar 404
    chat_group = get_object_or_404(ChatGroup, group_name=chatroom_name)

    chat_messages = chat_group.chat_messages.all()[:30]  # Últimos 30 mensajes
    form = ChatmessageCreateForm()

    other_user = None
    # Validar si es un chat privado y si el usuario pertenece al grupo
    if chat_group.is_private:
        if request.user not in chat_group.members.all():
            raise Http404("No tienes acceso a este chat privado.")
        # Encontrar al otro usuario en el chat privado
        other_user = chat_group.members.exclude(id=request.user.id).first()

    # Manejar solicitudes HTMX para mensajes nuevos
    if request.htmx:
        form = ChatmessageCreateForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.author = request.user
            message.group = chat_group
            message.save()
            context = {'message': message, 'user': request.user}
            return render(request, 'crm/chat_message_p.html', context)

    # Contexto para renderizar la plantilla
    context = {
        'messages': chat_messages,
        'form': form,
        'other_user': other_user,
        'chatroom_name': chatroom_name,
    }
    return render(request, 'crm/chat.html', context)

@login_required
def get_or_create_chatroom(request, username):
    if request.user.username == username:
        return redirect('home')  # Evitar chats con uno mismo

    # Obtener al otro usuario o lanzar 404 si no existe
    other_user = get_object_or_404(User, username=username)

    # Buscar chat privado existente
    chatroom = request.user.chat_groups.filter(is_private=True, members=other_user).first()

    # Si no existe, crear un nuevo chat privado
    if not chatroom:
        chatroom = ChatGroup.objects.create(is_private=True)
        chatroom.members.add(request.user, other_user)

    return redirect('chatroom', chatroom_name=chatroom.group_name)





# ------------------------------------------------------------------------------------
# API DE LAS RESEÑAS
# ------------------------------------------------------------------------------------

class ResenaListCreateView(APIView):
    def get_permissions(self):
        """Define permisos específicos por método."""
        if self.request.method == 'GET':
            return [AllowAny()]  # Permite acceso público a las reseñas
        return [IsAuthenticated()]  # Requiere autenticación para crear una reseña

    def get(self, request, format=None):
        """Obtiene todas las reseñas."""
        reseñas = Reseña.objects.all()
        serializer = ReseñaSerializer(reseñas, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        """Crea una nueva reseña."""
        serializer = ReseñaSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(usuario=request.user)  # Asocia al usuario actual
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class ResenaDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return Reseña.objects.get(pk=pk)
        except Reseña.DoesNotExist:
            return None

    def get(self, request, pk, format=None):
        """Obtiene una reseña por su ID."""
        reseña = self.get_object(pk)
        if reseña is None:
            return Response({"error": "Reseña no encontrada"}, status=status.HTTP_404_NOT_FOUND)
        serializer = ReseñaSerializer(reseña)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        """Actualiza una reseña."""
        reseña = self.get_object(pk)
        if reseña is None:
            return Response({"error": "Reseña no encontrada"}, status=status.HTTP_404_NOT_FOUND)
        if reseña.usuario != request.user:
            return Response({"error": "No tienes permiso para editar esta reseña"}, status=status.HTTP_403_FORBIDDEN)
        serializer = ReseñaSerializer(reseña, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        """Elimina una reseña."""
        reseña = self.get_object(pk)
        if reseña is None:
            return Response({"error": "Reseña no encontrada"}, status=status.HTTP_404_NOT_FOUND)
        if reseña.usuario != request.user:
            return Response({"error": "No tienes permiso para eliminar esta reseña"}, status=status.HTTP_403_FORBIDDEN)
        reseña.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)