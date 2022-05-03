from django.forms import ModelForm, PasswordInput, TextInput
from django.contrib.auth.password_validation import password_validators_help_text_html
from django.core.validators import validate_email

from .models import Usuario

class registro(ModelForm):
    
    class Meta:
        model = Usuario
        fields = ['usuario', 'email', 'nombre', 'password']
        widgets = {
            'email': TextInput(attrs={'placeholder': "nombre@ejemplo.com"}),
            'password': PasswordInput,
        }
        labels = {
            'usuario': ('Nombre de usuario'),
            'email': ('Correo electrónico'),
            'nombre': ('Nombre completo'),
            'password': ('Contraseña'),
        }
        help_texts = {
            'password': password_validators_help_text_html(password_validators=None),
        }
        error_messages = {
            'usuario': {
                'unique': ("Usuario ya registrado."),
                'required': ("Campo usuario requerido."),
            },
            'email': {
                'unique': ("Correo ya registrado con otro usuario."),
                'required': ("Campo correo requerido."),
            },
            'nombre': {
                'required': ("Campo nombre requerido."),
            },
            'password': {
                'required': ("Campo contraseña requerido."),
            },
        }

    def __init__(self, *args, **kwargs):
        super(registro, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'