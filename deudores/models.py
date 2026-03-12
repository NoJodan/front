from django.db import models
from django.contrib.auth.models import User


# ──────────── PERFIL DE USUARIO (rol: gestor / admin) ────────────
class Perfil(models.Model):
    ROL_CHOICES = [
        ('gestor', 'Gestor'),
        ('admin', 'Administrador'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    rol  = models.CharField(max_length=10, choices=ROL_CHOICES, default='gestor')

    def _str_(self):
        return f"{self.user.username} ({self.rol})"

    class Meta:
        verbose_name = "Perfil"
        verbose_name_plural = "Perfiles"


# ──────────── DEUDOR ────────────
class Deudor(models.Model):
    gestor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='deudores',
        limit_choices_to={'perfil__rol': 'gestor'},
    )
    nombre           = models.CharField(max_length=100)
    apellido         = models.CharField(max_length=100)
    cedula           = models.CharField(max_length=20, unique=True)
    telefono         = models.CharField(max_length=20, blank=True)
    email            = models.EmailField(blank=True)
    direccion        = models.TextField(blank=True)
    fecha_registro   = models.DateTimeField(auto_now_add=True)

    def _str_(self):
        return f"{self.nombre} {self.apellido} - {self.cedula}"

    class Meta:
        verbose_name = "Deudor"
        verbose_name_plural = "Deudores"


# ──────────── PAGO ────────────
class Pago(models.Model):
    ESTADO_CHOICES = [
        ('pendiente',  'Pendiente'),
        ('pagado',     'Pagado'),
        ('rechazado',  'Rechazado'),
    ]

    deudor                  = models.ForeignKey(Deudor, on_delete=models.CASCADE, related_name='pagos')
    monto                   = models.DecimalField(max_digits=10, decimal_places=2)
    descripcion             = models.TextField(blank=True)
    fecha_vencimiento       = models.DateField()
    fecha_pago              = models.DateField(null=True, blank=True)
    estado                  = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    fecha_registro          = models.DateTimeField(auto_now_add=True)

    # ── Campos nuevos ──
    valor_pago              = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    tipo_pago               = models.CharField(max_length=50, blank=True)
    estado_contable         = models.CharField(max_length=50, blank=True)
    aplica_honorarios       = models.BooleanField(default=False)
    porcentaje_honorarios   = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    porcentaje_iva          = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    valor_antes_honorarios  = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    valor_honorarios        = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    valor_iva               = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    abogado                 = models.CharField(max_length=100, blank=True)
    tipo_convenio           = models.CharField(max_length=100, blank=True)
    valor_ica               = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    valor_renta             = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    valor_50                = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    ingreso_frg             = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    observaciones           = models.TextField(blank=True)
    registrado_por          = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='pagos_registrados')
    fecha_contable          = models.DateField(null=True, blank=True)

    # ── Comprobante al final ──
    comprobante_pdf         = models.FileField(upload_to='comprobantes/', null=True, blank=True)

    def _str_(self):
        return f"Pago de {self.deudor} - ${self.monto} ({self.estado})"

    class Meta:
        verbose_name = "Pago"
        verbose_name_plural = "Pagos"