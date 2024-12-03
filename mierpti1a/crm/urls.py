from django.urls import include, path
from . import views
from .views import *

urlpatterns = [
    path("", views.home, name="home"),
    path('faqs/', views.faqs, name='faqs'),
    path('comunity/', views.comunity, name='comunity'),
    path("allTickets/", views.allTickets, name="allTickets"),
    path('ticket/', views.tickets, name='ticket'),
    path('solutions/<int:ticket_id>/', views.solutions, name='solutions'),
    path('controlPanel/', views.allTicketsAdmin, name='controlPanel'),
    path("chat/", views.chat_view, name="chat"),  # Ruta para el chat general
    path("chat/<str:chatroom_name>/", views.chat_view, name="chat_with_name"),  # Ruta para chats específicos
    path('chat/new/<str:username>/', views.get_or_create_chatroom, name='new-private-chat'),  # Mover esta ruta arriba
    path('chat/<username>', get_or_create_chatroom, name="start-chat"),
    path('chat/room/<chatroom_name>', chat_view, name="chatroom"),
]
