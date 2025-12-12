from django.urls import path
from . import views


urlpatterns = [
    # Página principal / catálogo
    path("", views.home, name="home"),

    # Panel productos (stock)
    path("panel/productos/", views.producto_list, name="product_list"),
    path("panel/productos/crear/", views.producto_create, name="product_create"),
    path("panel/productos/<int:pk>/editar/", views.producto_edit, name="product_edit"),
    path("panel/productos/<int:pk>/eliminar/", views.producto_delete, name="product_delete"),

    # Carrito
    path("carrito/", views.cart_detail, name="cart_detail"),
    path("carrito/agregar/<int:product_id>/", views.cart_add, name="cart_add"),
    path("carrito/eliminar/<int:product_id>/", views.cart_remove, name="cart_remove"),
    path(
        "carrito/eliminar-id/<int:product_id>/",
        views.cart_remove_by_id,
        name="cart_remove_by_id",
    ),
    path("carrito/actualizar/<int:product_id>/", views.cart_update, name="cart_update"),
    
     # Autenticación / cuenta
    path("accounts/login/", views.login_view, name="login"),
    path("accounts/logout/", views.logout_view, name="logout"),
    path("accounts/registro/", views.register, name="register"),
    path("mi-cuenta/", views.account_dashboard, name="account_dashboard"),
]