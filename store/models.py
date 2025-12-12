# store/models.py
import datetime
from decimal import Decimal

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Genero(models.Model):
    nombre = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Nombre del género",
    )

    class Meta:
        ordering = ["nombre"]

    def __str__(self) -> str:
        return self.nombre


PLATAFORMA_CHOICES = [
    ("PS3", "PS3"),
    ("PS4", "PS4"),
    ("PS5", "PS5"),
]

FORMATO_CHOICES = [
    ("FISICO", "Físico"),
    ("DIGITAL", "Digital"),
]

ESTADO_CHOICES = [
    ("NUEVO", "Nuevo"),
    ("USADO", "Usado"),
]


class Producto(models.Model):
    nombre = models.CharField(
        max_length=150,
        verbose_name="Nombre del juego",
    )

    # Usamos DateField pero solo nos importa el año
    anio_lanzamiento = models.DateField(
        verbose_name="Año de lanzamiento",
        help_text="Fecha aproximada de lanzamiento del juego.",
    )

    plataforma = models.CharField(
        max_length=10,
        choices=PLATAFORMA_CHOICES,
        verbose_name="Plataforma",
    )

    formato = models.CharField(
        max_length=10,
        choices=FORMATO_CHOICES,
        verbose_name="Formato",
    )

    estado = models.CharField(
        max_length=10,
        choices=ESTADO_CHOICES,
        verbose_name="Estado",
    )

    generos = models.ManyToManyField(
        Genero,
        blank=True,
        verbose_name="Géneros",
        help_text="Puedes seleccionar uno o varios géneros.",
    )

    descripcion = models.TextField(
        verbose_name="Descripción",
        blank=True,
        help_text="Descripción breve para el cliente.",
    )

    valor = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[
            MinValueValidator(Decimal("1000.00")),
            MaxValueValidator(Decimal("100000000.00")),
        ],
        verbose_name="Precio",
        help_text="Precio de venta en CLP (entre 1.000 y 100.000.000).",
    )

    stock = models.PositiveIntegerField(
        default=0,
        validators=[MaxValueValidator(100000)],
        verbose_name="Stock",
        help_text="Cantidad disponible (0 a 100.000).",
    )

    imagen = models.ImageField(
        upload_to="productos/",
        null=True,
        blank=True,
        verbose_name="Imagen del producto",
    )

    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-creado_en"]
        # Evita duplicar el mismo juego en la misma plataforma
        constraints = [
            models.UniqueConstraint(
                fields=["nombre", "plataforma", "formato", "estado"],
                name="unique_producto_por_plataforma_formato_estado",
            )
        ]

    def __str__(self) -> str:
        return f"{self.nombre} ({self.plataforma})"

    # ---- Validación de negocio extra (a nivel de modelo) ----
    def clean(self):
        """
        Validaciones adicionales de negocio.
        Se ejecutan al llamar a full_clean() (Django admin y ModelForm).
        """
        super().clean()

        hoy = datetime.date.today()

        # Solo validamos si anio_lanzamiento tiene un valor
        if self.anio_lanzamiento:
            # 1) Año de lanzamiento no puede ser futuro
            if self.anio_lanzamiento > hoy:
                from django.core.exceptions import ValidationError

                raise ValidationError(
                    {
                        "anio_lanzamiento": "El año de lanzamiento no puede ser una fecha futura."
                    }
                )

            # 2) Año de lanzamiento razonable para videojuegos
            if self.anio_lanzamiento.year < 1970:
                from django.core.exceptions import ValidationError

                raise ValidationError(
                    {
                        "anio_lanzamiento": "El año de lanzamiento debe ser 1970 o posterior."
                    }
                )

        # 3) Si el formato es físico, exigir stock > 0 al crear
        if self.formato == "FISICO" and self.stock == 0:
            from django.core.exceptions import ValidationError

            raise ValidationError(
                {"stock": "Para productos físicos, el stock debe ser mayor a 0."}
            )

        # 4) Valor mínimo por lógica de negocio
        if self.valor is not None and self.valor <= 0:
            from django.core.exceptions import ValidationError

            raise ValidationError({"valor": "El precio debe ser mayor a 0."})

