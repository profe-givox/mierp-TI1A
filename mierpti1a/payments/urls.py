from django.urls import path
from . import views 

urlpatterns = [
    path('pagos/', views.generarPagos, name = 'pagos'),
    path('api_pagos/', views.api_pagos , name = 'pagos'),


    path('pagosCliente/', views.pagosClientes, name = 'pagosClientes'),
    path('api/pagos-por-cliente/', views.api_pagos_por_cliente, name='api_pagos_por_cliente'),

    path('generarPedido/', views.generarPedido,  name='generarPedido'),
    path('succesful/', views.pagoExitoso, name='mostrar_html'),
]