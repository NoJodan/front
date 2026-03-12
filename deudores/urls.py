from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path('login/',   views.login_view,   name='login'),
    path('logout/',  views.logout_view,  name='logout'),

    # Paneles de inicio
    path('',          views.inicio,        name='inicio'),        # gestor
    path('admin-panel/', views.inicio_admin, name='inicio_admin'), # administrador

    # Deudores (CRUD — solo admin crea/edita/elimina)
    path('deudores/',                        views.lista_deudores,  name='lista_deudores'),
    path('deudor/nuevo/',                    views.crear_deudor,    name='crear_deudor'),
    path('deudor/<int:pk>/',                 views.detalle_deudor,  name='detalle_deudor'),
    path('deudor/<int:pk>/editar/',          views.editar_deudor,   name='editar_deudor'),
    path('deudor/<int:pk>/eliminar/',        views.eliminar_deudor, name='eliminar_deudor'),

    # Gestor: seleccionar y asignarse un deudor disponible
    path('deudores/seleccionar/',            views.seleccionar_deudor, name='seleccionar_deudor'),
    path('deudor/<int:pk>/asignar/',         views.asignar_deudor,     name='asignar_deudor'),

    # Pagos
    path('pagos/',                                    views.lista_pagos,  name='lista_pagos'),
    path('deudor/<int:deudor_pk>/pago/nuevo/',        views.crear_pago,   name='crear_pago_deudor'),
    path('pago/<int:pk>/editar/',                     views.editar_pago,  name='editar_pago'),
    path('pago/<int:pk>/eliminar/',                   views.eliminar_pago, name='eliminar_pago'),
]
