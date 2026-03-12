from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Perfil, Deudor, Pago


# ── Perfil inline dentro del User ────────────────────────────────────────────
class PerfilInline(admin.StackedInline):
    model = Perfil
    can_delete = False
    verbose_name_plural = 'Perfil'


class UserAdmin(BaseUserAdmin):
    inlines = (PerfilInline,)


admin.site.unregister(User)
admin.site.register(User, UserAdmin)


# ── Deudor ───────────────────────────────────────────────────────────────────
@admin.register(Deudor)
class DeudorAdmin(admin.ModelAdmin):
    list_display  = ('nombre', 'apellido', 'cedula', 'telefono', 'gestor', 'fecha_registro')
    list_filter   = ('gestor',)
    search_fields = ('nombre', 'apellido', 'cedula')


# ── Pago ─────────────────────────────────────────────────────────────────────
@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display  = ('deudor', 'monto', 'estado', 'fecha_vencimiento', 'fecha_pago')
    list_filter   = ('estado',)
    search_fields = ('deudor__nombre', 'deudor__apellido', 'deudor__cedula')
