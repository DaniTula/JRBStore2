from .cart import Cart


def cart(request):
    """
    Hace disponible en todas las plantillas:
    - cart_total_items: número total de unidades en el carrito
    """
    cart = Cart(request)
    return {
        "cart_total_items": cart.total_quantity,
    }