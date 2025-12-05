from django.contrib import admin
from .models import Genero, Producto


@admin.register(Genero)
class GeneroAdmin(admin.ModelAdmin):
    list_display = ("id", "nombre")
    search_fields = ("nombre",)


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "nombre",
        "plataforma",
        "formato",
        "estado",
        "valor",
        "stock",
    )
    list_filter = ("plataforma", "formato", "estado", "generos")
    search_fields = ("nombre",)