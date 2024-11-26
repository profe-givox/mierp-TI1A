from django.urls import include, path
from . import views

urlpatterns = [
    path("", views.home, name =  "home"),
    path('faqs/', views.faqs, name='faqs'),
    path('comunity/', views.comunity, name='comunity'),
]
