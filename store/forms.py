import datetime
from decimal import Decimal
from django import forms
from .models import Producto, Genero
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User

class ProductoForm(forms.ModelForm):
    anio_lanzamiento = forms.DateField(
        label="Año de lanzamiento",
        widget=forms.DateInput(
            attrs={
                "type": "date",
                "class": "form-control",
            }
        ),
    )

    generos = forms.ModelMultipleChoiceField(
        queryset=Genero.objects.all(),
        required=False,  # permitimos sin género, pero podrías poner True
        widget=forms.CheckboxSelectMultiple,
        label="Géneros",
    )

    class Meta:
        model = Producto
        fields = [
            "nombre",
            "anio_lanzamiento",
            "plataforma",
            "formato",
            "estado",
            "generos",
            "descripcion",
            "valor",
            "stock",
            "imagen",
        ]

        widgets = {
            "nombre": forms.TextInput(
                attrs={"class": "form-control", "maxlength": 150}
            ),
            "plataforma": forms.Select(attrs={"class": "form-select"}),
            "formato": forms.Select(attrs={"class": "form-select"}),
            "estado": forms.Select(attrs={"class": "form-select"}),
            "descripcion": forms.Textarea(
                attrs={"class": "form-control", "rows": 3}
            ),
            "valor": forms.NumberInput(
                attrs={"class": "form-control", "min": "1000", "step": "500"}
            ),
            "stock": forms.NumberInput(
                attrs={"class": "form-control", "min": "0", "step": "1"}
            ),
            "imagen": forms.ClearableFileInput(attrs={"class": "form-control"}),
        }

    # ---------- Validaciones de formulario ----------

    def clean_nombre(self):
        nombre = self.cleaned_data["nombre"].strip()
        if len(nombre) < 3:
            raise forms.ValidationError(
                "El nombre del juego debe tener al menos 3 caracteres."
            )
        return nombre

    def clean_descripcion(self):
        descripcion = self.cleaned_data.get("descripcion", "").strip()
        if descripcion and len(descripcion) < 10:
            raise forms.ValidationError(
                "Si escribes una descripción, debe tener al menos 10 caracteres."
            )
        return descripcion

    def clean_anio_lanzamiento(self):
        fecha = self.cleaned_data["anio_lanzamiento"]
        hoy = datetime.date.today()

        if fecha > hoy:
            raise forms.ValidationError(
                "El año de lanzamiento no puede ser una fecha futura."
            )

        if fecha.year < 1970:
            raise forms.ValidationError(
                "El año de lanzamiento debe ser igual o posterior a 1970."
            )

        return fecha

    def clean_valor(self):
        valor = self.cleaned_data["valor"]
        if valor < Decimal("1000.00"):
            raise forms.ValidationError(
                "El precio mínimo permitido es de 1.000 CLP."
            )
        if valor > Decimal("100000000.00"):
            raise forms.ValidationError(
                "El precio es demasiado alto. Revisa si hay un error de digitación."
            )
        return valor

    def clean_stock(self):
        stock = self.cleaned_data["stock"]
        if stock > 100000:
            raise forms.ValidationError(
                "El stock no puede ser mayor a 100.000 unidades."
            )
        return stock

    def clean(self):
        """
        Validaciones que dependen de varios campos a la vez.
        """
        cleaned_data = super().clean()
        formato = cleaned_data.get("formato")
        stock = cleaned_data.get("stock")

        # Reforzamos regla: Físico debe tener stock
        if formato == "FISICO" and stock == 0:
            self.add_error(
                "stock",
                "Para productos físicos, el stock debe ser mayor a 0.",
            )

        return cleaned_data
    

class UserRegisterForm(UserCreationForm):

    email = forms.EmailField(
        required=True,
        label="Correo electrónico",
        widget=forms.EmailInput(attrs={"class": "form-control"})
    )
    first_name = forms.CharField(
        required=False,
        label="Nombre",
        widget=forms.TextInput(attrs={"class": "form-control"})
    )
    last_name = forms.CharField(
        required=False,
        label="Apellidos",
        widget=forms.TextInput(attrs={"class": "form-control"})
    )

    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Bootstrap a todos los campos
        for field in self.fields.values():
            if not field.widget.attrs.get("class"):
                field.widget.attrs["class"] = "form-control"

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Ya existe un usuario registrado con este correo.")
        return email


class UserLoginForm(AuthenticationForm):
    """
    Formulario de login con estilos Bootstrap.
    """
    username = forms.CharField(
        label="Usuario o correo",
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Ingresa tu usuario o correo", "autofocus": True}
        ),
    )
    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Ingresa tu contraseña"}
        ),
    )
