from django.contrib import admin
from .models import Producto, Genero

@admin.register(Genero)
class GeneroAdmin(admin.ModelAdmin):
    list_display = ("nombre",)
    search_fields = ("nombre",)

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "plataforma", "formato", "estado", "valor", "stock")
    list_filter = ("plataforma", "formato", "estado", "generos")
    search_fields = ("nombre",)