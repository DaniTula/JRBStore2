from django.db import models


class Genero(models.Model):
    """
    Género de juego (Acción, Aventura, etc.).
    Permite que un producto tenga varios géneros.
    """
    nombre = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nombre


class Producto(models.Model):
    """
    Modelo principal de productos de la tienda.
    """

    # Opciones fijas para la plataforma
    PLATAFORMA_PS3 = "PS3"
    PLATAFORMA_PS4 = "PS4"
    PLATAFORMA_PS5 = "PS5"

    PLATAFORMA_CHOICES = [
        (PLATAFORMA_PS3, "PS3"),
        (PLATAFORMA_PS4, "PS4"),
        (PLATAFORMA_PS5, "PS5"),
    ]

    # FORMATO: físico / digital
    FORMATO_FISICO = "fisico"
    FORMATO_DIGITAL = "digital"

    FORMATO_CHOICES = [
        (FORMATO_FISICO, "Físico"),
        (FORMATO_DIGITAL, "Digital"),
    ]

    # ESTADO: nuevo / usado
    ESTADO_NUEVO = "nuevo"
    ESTADO_USADO = "usado"

    ESTADO_CHOICES = [
        (ESTADO_NUEVO, "Nuevo"),
        (ESTADO_USADO, "Usado"),
    ]

    nombre = models.CharField(max_length=200)

    # AHORA ES UNA FECHA (ej: 2011-11-11)
    anio_lanzamiento = models.DateField()

    plataforma = models.CharField(
        max_length=10,
        choices=PLATAFORMA_CHOICES,
    )

    formato = models.CharField(
        max_length=10,
        choices=FORMATO_CHOICES,
    )

    estado = models.CharField(
        max_length=10,
        choices=ESTADO_CHOICES,
        default=ESTADO_NUEVO,
    )

    # VARIOS GÉNEROS (Acción, Aventura, etc.)
    generos = models.ManyToManyField(
        Genero,
        blank=True,
        related_name="productos",
    )

    descripcion = models.TextField(blank=True)
    valor = models.DecimalField(max_digits=10, decimal_places=2)

    imagen = models.ImageField(
        upload_to="productos/",
        blank=True,
        null=True,
    )

    stock = models.PositiveIntegerField(default=0)

    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nombre
