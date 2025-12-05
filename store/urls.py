from django.urls import path
from . import views


urlpatterns = [
    path("", views.home, name="home"),
    path("panel/productos/", views.producto_list, name="product_list"),
    path("panel/productos/crear/", views.producto_create, name="product_create"),
    path("panel/productos/<int:pk>/editar/", views.producto_edit, name="product_edit"),
    path("panel/productos/<int:pk>/eliminar/", views.producto_delete, name="product_delete"),
]
