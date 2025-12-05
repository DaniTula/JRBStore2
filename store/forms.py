from django import forms
from .models import Producto, Genero


class ProductoForm(forms.ModelForm):
    """
    Formulario basado en el modelo Producto.
    """

    class Meta:
        model = Producto
        fields = [
            "nombre",
            "anio_lanzamiento",
            "plataforma",
            "formato",    # Físico / Digital
            "estado",     # Nuevo / Usado
            "generos",    # Varios géneros
            "descripcion",
            "valor",
            "imagen",
            "stock",
        ]
        widgets = {
            "nombre": forms.TextInput(attrs={"class": "form-control"}),

            # DateField → input type="date"
            "anio_lanzamiento": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),

            "plataforma": forms.Select(attrs={"class": "form-select"}),
            "formato": forms.Select(attrs={"class": "form-select"}),
            "estado": forms.Select(attrs={"class": "form-select"}),

            # Múltiples géneros → checkboxes
            "generos": forms.CheckboxSelectMultiple(),

            "descripcion": forms.Textarea(
                attrs={"class": "form-control", "rows": 3}
            ),
            "valor": forms.NumberInput(attrs={"class": "form-control"}),
            "imagen": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "stock": forms.NumberInput(attrs={"class": "form-control"}),
        }