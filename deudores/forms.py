from django import forms
from django.core.exceptions import ValidationError
from .models import Deudor, Pago


class DeudorForm(forms.ModelForm):
    class Meta:
        model  = Deudor
        fields = ['nombre', 'apellido', 'cedula', 'telefono', 'email', 'direccion']
        widgets = {
            'nombre':    forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Juan'}),
            'apellido':  forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Pérez'}),
            'cedula':    forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Número de identificación'}),
            'telefono':  forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+57 300...'}),
            'email':     forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'correo@ejemplo.com'}),
            'direccion': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Dirección de residencia o local'}),
        }


class PagoForm(forms.ModelForm):
    class Meta:
        model  = Pago
        fields = [
            'monto', 'descripcion', 'fecha_vencimiento', 'fecha_pago', 'estado',
            'valor_pago', 'tipo_pago', 'estado_contable', 'aplica_honorarios',
            'porcentaje_honorarios', 'porcentaje_iva', 'valor_antes_honorarios',
            'valor_honorarios', 'valor_iva', 'abogado', 'tipo_convenio',
            'valor_ica', 'valor_renta', 'valor_50', 'ingreso_frg',
            'observaciones', 'registrado_por', 'fecha_contable',
            'comprobante_pdf',
        ]
        widgets = {
            'monto':                  forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Monto en pesos'}),
            'descripcion':            forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Detalles de la transacción'}),
            'fecha_vencimiento':      forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'fecha_pago':             forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'estado':                 forms.Select(attrs={'class': 'form-select'}),
            'valor_pago':             forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Valor del pago'}),
            'tipo_pago':              forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: transferencia, efectivo'}),
            'estado_contable':        forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Estado contable'}),
            'aplica_honorarios':      forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'porcentaje_honorarios':  forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '% honorarios'}),
            'porcentaje_iva':         forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '% IVA'}),
            'valor_antes_honorarios': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Valor antes de honorarios'}),
            'valor_honorarios':       forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Valor honorarios'}),
            'valor_iva':              forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Valor IVA'}),
            'abogado':                forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del abogado'}),
            'tipo_convenio':          forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tipo de convenio'}),
            'valor_ica':              forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Valor ICA'}),
            'valor_renta':            forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Valor renta'}),
            'valor_50':               forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Valor 50%'}),
            'ingreso_frg':            forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ingreso FRG'}),
            'observaciones':          forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Observaciones'}),
            'registrado_por':         forms.Select(attrs={'class': 'form-select'}),
            'fecha_contable':         forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'comprobante_pdf':        forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': '.pdf,application/pdf'}),
        }

    def clean_comprobante_pdf(self):
        archivo = self.cleaned_data.get('comprobante_pdf')
        if archivo:
            nombre = getattr(archivo, 'name', '')
            content_type = getattr(archivo, 'content_type', '')
            es_pdf = (
                nombre.lower().endswith('.pdf') or
                content_type == 'application/pdf'
            )
            if not es_pdf:
                raise ValidationError('Solo se permiten archivos en formato PDF.')
        return archivo
