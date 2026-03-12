from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Sum, Count, Q
from django.db import models
from .models import Deudor, Pago, Perfil
from .forms import DeudorForm, PagoForm


# ── Helpers ──────────────────────────────────────────────────────────────────

def get_rol(user):
    """Devuelve el rol del usuario: 'admin' o 'gestor'."""
    try:
        return user.perfil.rol
    except Perfil.DoesNotExist:
        return 'gestor'


def es_admin(user):
    return get_rol(user) == 'admin'


# ── AUTH ──────────────────────────────────────────────────────────────────────

def login_view(request):
    if request.user.is_authenticated:
        return redirect('inicio' if get_rol(request.user) == 'gestor' else 'inicio_admin')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('inicio' if get_rol(user) == 'gestor' else 'inicio_admin')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')
    return render(request, 'deudores/login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


# ── INICIO GESTOR ──────────────────────────────────────────────────────────────

@login_required(login_url='login')
def inicio(request):
    """Panel de control del gestor — solo ve sus deudores asignados."""
    mis_deudores = Deudor.objects.filter(gestor=request.user)

    total_deudores   = mis_deudores.count()
    total_pagos      = Pago.objects.filter(deudor__gestor=request.user).count()
    pagos_rechazados = Pago.objects.filter(deudor__gestor=request.user, estado='rechazado').count()

    deudores_recientes = mis_deudores.annotate(
        total_pendiente=Sum('pagos__monto', filter=Q(pagos__estado='pendiente'))
    ).order_by('-fecha_registro')[:5]

    return render(request, 'deudores/inicio.html', {
        'total_deudores':    total_deudores,
        'total_pagos':       total_pagos,
        'pagos_rechazados':  pagos_rechazados,
        'deudores_recientes': deudores_recientes,
    })


# ── INICIO ADMIN ──────────────────────────────────────────────────────────────

@login_required(login_url='login')
def inicio_admin(request):
    """Panel de control del administrador."""
    if not es_admin(request.user):
        return redirect('inicio')

    gestores = User.objects.filter(perfil__rol='gestor').annotate(
        total_deudores=Count('deudores')
    )
    total_gestores  = gestores.count()
    total_deudores  = Deudor.objects.count()

    # Entidades: si aún no tienes el modelo, devuelve 0 sin romper
    try:
        from .models import Entidad
        total_entidades = Entidad.objects.count()
    except Exception:
        total_entidades = 0

    gestores_recientes = gestores.order_by('-date_joined')[:5]

    return render(request, 'deudores/inicio_admin.html', {
        'total_gestores':    total_gestores,
        'total_entidades':   total_entidades,
        'total_deudores':    total_deudores,
        'gestores_recientes': gestores_recientes,
    })


# ── DEUDORES ──────────────────────────────────────────────────────────────────

@login_required(login_url='login')
def lista_deudores(request):
    """
    Admin ve todos los deudores.
    Gestor ve solo los suyos.
    """
    if es_admin(request.user):
        qs = Deudor.objects.select_related('gestor').annotate(
            total_pagos=Count('pagos'),
            total_abonado=Sum('pagos__monto', filter=Q(pagos__estado='pagado')),
            total_pendiente=Sum('pagos__monto', filter=Q(pagos__estado='pendiente')),
        )
    else:
        qs = Deudor.objects.filter(gestor=request.user).annotate(
            total_pagos=Count('pagos'),
            total_abonado=Sum('pagos__monto', filter=Q(pagos__estado='pagado')),
            total_pendiente=Sum('pagos__monto', filter=Q(pagos__estado='pendiente')),
        )
    return render(request, 'deudores/lista_deudores.html', {'deudores': qs})


@login_required(login_url='login')
def detalle_deudor(request, pk):
    deudor = get_object_or_404(Deudor, pk=pk)

    # Gestor solo puede ver sus propios deudores
    if not es_admin(request.user) and deudor.gestor != request.user:
        messages.error(request, 'No tienes acceso a este deudor.')
        return redirect('lista_deudores')

    pagos = deudor.pagos.all().order_by('-fecha_registro')
    total_abonado   = pagos.filter(estado='pagado').aggregate(Sum('monto'))['monto__sum'] or 0
    total_pendiente = pagos.filter(estado='pendiente').aggregate(Sum('monto'))['monto__sum'] or 0
    total_rechazado = pagos.filter(estado='rechazado').aggregate(Sum('monto'))['monto__sum'] or 0

    return render(request, 'deudores/detalle_deudor.html', {
        'deudor':          deudor,
        'pagos':           pagos,
        'total_abonado':   total_abonado,
        'total_pendiente': total_pendiente,
        'total_rechazado': total_rechazado,
    })


@login_required(login_url='login')
def crear_deudor(request):
    """Solo administradores pueden crear deudores."""
    if not es_admin(request.user):
        messages.error(request, 'Solo los administradores pueden crear deudores.')
        return redirect('inicio')

    form = DeudorForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Deudor creado exitosamente.')
        return redirect('lista_deudores')
    return render(request, 'deudores/crear_deudor.html', {'form': form})


@login_required(login_url='login')
def editar_deudor(request, pk):
    if not es_admin(request.user):
        return redirect('inicio')
    deudor = get_object_or_404(Deudor, pk=pk)
    form = DeudorForm(request.POST or None, instance=deudor)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Deudor actualizado correctamente.')
        return redirect('detalle_deudor', pk=pk)
    return render(request, 'deudores/editar_deudor.html', {'form': form, 'deudor': deudor})


@login_required(login_url='login')
def eliminar_deudor(request, pk):
    if not es_admin(request.user):
        return redirect('inicio')
    deudor = get_object_or_404(Deudor, pk=pk)
    if request.method == 'POST':
        deudor.delete()
        messages.success(request, 'Deudor eliminado correctamente.')
        return redirect('lista_deudores')
    return render(request, 'deudores/eliminar_deudor.html', {'deudor': deudor})


# ── SELECCIONAR / ASIGNAR DEUDOR (gestor) ────────────────────────────────────

@login_required(login_url='login')
def seleccionar_deudor(request):
    """
    Muestra al gestor los deudores disponibles:
    - sin gestor asignado, O
    - cuyo gestor esté inactivo (is_active=False)
    """
    if es_admin(request.user):
        return redirect('inicio_admin')

    deudores_disponibles = Deudor.objects.filter(
        Q(gestor__isnull=True) | Q(gestor__is_active=False)
    ).select_related('gestor')

    return render(request, 'deudores/seleccionar_deudor.html', {
        'deudores_disponibles': deudores_disponibles,
    })


@login_required(login_url='login')
def asignar_deudor(request, pk):
    """Asigna el deudor seleccionado al gestor actual."""
    if es_admin(request.user):
        return redirect('inicio_admin')

    if request.method == 'POST':
        deudor = get_object_or_404(Deudor, pk=pk)

        # Verificar que sigue disponible
        if deudor.gestor and deudor.gestor.is_active:
            messages.error(request, 'Este deudor ya fue asignado a otro gestor.')
            return redirect('seleccionar_deudor')

        deudor.gestor = request.user
        deudor.save()
        messages.success(request, f'{deudor.nombre} {deudor.apellido} fue agregado a tu cartera.')
        return redirect('lista_deudores')

    return redirect('seleccionar_deudor')


# ── PAGOS ─────────────────────────────────────────────────────────────────────

@login_required(login_url='login')
def crear_pago(request, deudor_pk):
    """
    Nuevo pago vinculado directamente al deudor.
    Se accede desde el perfil del deudor — el deudor queda preseleccionado.
    """
    deudor = get_object_or_404(Deudor, pk=deudor_pk)

    # Gestor solo puede agregar pagos a sus propios deudores
    if not es_admin(request.user) and deudor.gestor != request.user:
        messages.error(request, 'No tienes permiso para agregar pagos a este deudor.')
        return redirect('lista_deudores')

    form = PagoForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        pago = form.save(commit=False)
        pago.deudor = deudor
        pago.save()
        messages.success(request, 'Pago registrado exitosamente.')
        return redirect('detalle_deudor', pk=deudor.pk)

    return render(request, 'deudores/nuevo_pago.html', {
        'form':   form,
        'deudor': deudor,
    })


@login_required(login_url='login')
def lista_pagos(request):
    estado = request.GET.get('estado', '')
    if es_admin(request.user):
        pagos = Pago.objects.select_related('deudor').order_by('-fecha_registro')
    else:
        pagos = Pago.objects.filter(deudor__gestor=request.user).select_related('deudor').order_by('-fecha_registro')

    if estado:
        pagos = pagos.filter(estado=estado)
    return render(request, 'deudores/lista_pagos.html', {'pagos': pagos, 'estado': estado})


@login_required(login_url='login')
def editar_pago(request, pk):
    pago = get_object_or_404(Pago, pk=pk)

    if not es_admin(request.user) and pago.deudor.gestor != request.user:
        messages.error(request, 'No tienes permiso para editar este pago.')
        return redirect('lista_deudores')

    form = PagoForm(request.POST or None, request.FILES or None, instance=pago)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Pago actualizado correctamente.')
        return redirect('detalle_deudor', pk=pago.deudor.pk)
    return render(request, 'deudores/editar_pago.html', {'form': form, 'pago': pago})


@login_required(login_url='login')
def eliminar_pago(request, pk):
    pago = get_object_or_404(Pago, pk=pk)
    deudor_pk = pago.deudor.pk

    if not es_admin(request.user) and pago.deudor.gestor != request.user:
        messages.error(request, 'No tienes permiso para eliminar este pago.')
        return redirect('lista_deudores')

    if request.method == 'POST':
        pago.delete()
        messages.success(request, 'Pago eliminado correctamente.')
        return redirect('detalle_deudor', pk=deudor_pk)
    return render(request, 'deudores/eliminar_pago.html', {'pago': pago})
