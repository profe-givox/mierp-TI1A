from django.urls import include, path
from . import views

urlpatterns = [
    path("", views.home, name =  "home"),
    path('faqs/', views.faqs, name='faqs'),
    path('comunity/', views.comunity, name='comunity'),
    path("allTickets/", views.allTickets, name="allTickets"),
    path('ticket/create/', views.tickets, name='create_ticket'),  # Crear un nuevo ticket
    path('ticket/edit/<int:ticket_id>/', views.tickets, name='edit_ticket'),  # Editar un ticket
]
