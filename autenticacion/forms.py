from django.forms import ModelForm, PasswordInput, TextInput, CharField
from django.contrib.auth.password_validation import password_validators_help_text_html, validate_password
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from .models import Usuario

class Registro(ModelForm):

    error_messages = {
        "password_mismatch": _("The two password fields didn’t match."),
    }

    password1 = CharField(
        label=("Contraseña"),
        strip=False,
        widget=PasswordInput(attrs={"autocomplete": "new-password"}),
        help_text=password_validators_help_text_html(),
    )
    password2 = CharField(
        label=("Contraseña (confirmación)"),
        widget=PasswordInput(attrs={"autocomplete": "new-password"}),
        strip=False,
        help_text=("Ingrese la misma contraseña que antes para confirmar."),
    )
    
    class Meta:
        model = Usuario
        fields = ['usuario', 'email', 'nombre']
        widgets = {
            'usaurio': TextInput(attrs={'autofocus': True}),
            'email': TextInput(attrs={'placeholder': "nombre@ejemplo.com"}),
        }
        labels = {
            'usuario': ('Nombre de usuario'),
            'email': ('Correo electrónico'),
            'nombre': ('Nombre completo'),
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
        super(Registro, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError(
                self.error_messages["password_mismatch"],
                code="password_mismatch",
            )
        return password2

    def _post_clean(self):
        super()._post_clean()
        # Validate the password after self.instance is updated with form data
        # by super().
        password = self.cleaned_data.get("password2")
        if password:
            try:
                validate_password(password, self.instance)
            except ValidationError as error:
                self.add_error("password2", error)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user
