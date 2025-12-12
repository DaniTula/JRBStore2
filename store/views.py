# store/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages

from .models import Producto
from .cart import Cart
from .forms import ProductoForm


# ----------------------------- CATÁLOGO / HOME -----------------------------


def home(request):
    """
    Página principal de la tienda.
    Muestra el catálogo de productos disponibles.
    """
    productos = Producto.objects.all().order_by("-creado_en")
    context = {
        "productos": productos,
    }
    return render(request, "store/home.html", context)


# --------------------------- ADMIN PRODUCTOS ---------------------------


def producto_list(request):
    """
    Vista de administración de productos (módulo de stock).
    Muestra una tabla con todos los productos y botones para crear/editar/eliminar.
    """
    productos = Producto.objects.all().order_by("id")
    context = {
        "productos": productos,
    }
    return render(request, "store/product_list.html", context)


def producto_create(request):
    """
    Crea un producto nuevo.
    Muestra un formulario y guarda en la base de datos si los datos son válidos.
    """
    if request.method == "POST":
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            # Podríamos mostrar un mensaje interno para el admin si quieres
            # messages.success(request, "Producto creado correctamente.")
            return redirect("product_list")
    else:
        form = ProductoForm()

    context = {
        "form": form,
        "titulo": "Agregar producto",
    }
    return render(request, "store/product_form.html", context)


def producto_edit(request, pk):
    """
    Edita un producto existente identificado por su ID (pk).
    """
    producto = get_object_or_404(Producto, pk=pk)

    if request.method == "POST":
        form = ProductoForm(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            form.save()
            # messages.success(request, "Producto actualizado correctamente.")
            return redirect("product_list")
    else:
        form = ProductoForm(instance=producto)

    context = {
        "form": form,
        "titulo": f"Editar producto: {producto.nombre}",
    }
    return render(request, "store/product_form.html", context)


def producto_delete(request, pk):
    """
    Elimina un producto existente.
    Pide confirmación antes de borrar definitivamente.
    """
    producto = get_object_or_404(Producto, pk=pk)

    if request.method == "POST":
        producto.delete()
        # messages.info(request, "Producto eliminado.")
        return redirect("product_list")

    context = {
        "producto": producto,
    }
    return render(request, "store/product_confirm_delete.html", context)


# --------------------------- CARRITO DE COMPRAS ---------------------------


def cart_detail(request):
    """
    Muestra el carrito de compras:
    - Lista de productos con cantidad, precio, mensajes de stock/eliminados.
    - Resumen con total productos, envío y total final.
    """
    cart = Cart(request)
    items = list(cart)

    total_products = cart.get_total_price()
    shipping = 0
    if total_products > 0:
        shipping = 3000  # por ejemplo, envío fijo
    grand_total = total_products + shipping

    # Aviso general si hay productos con problemas
    if any(i["missing"] or i["insufficient_stock"] for i in items):
        messages.warning(
            request,
            "Algunos productos del carrito ya no están disponibles o no tienen stock. "
            "Revise los mensajes junto a cada producto antes de continuar.",
        )

    context = {
        "cart_items": items,
        "total_products": total_products,
        "shipping": shipping,
        "grand_total": grand_total,
        "quantity_range": range(1, 11),  # para el select de cantidad (1 a 10)
    }
    return render(request, "store/cart_detail.html", context)


def cart_add(request, product_id):
    """
    Agrega un producto al carrito (cantidad por defecto 1).
    No muestra mensaje de éxito, solo errores cuando no hay stock.
    """
    cart = Cart(request)
    producto = get_object_or_404(Producto, id=product_id)

    # Validación seria: no permitir agregar si no hay stock
    if producto.stock <= 0:
        messages.error(request, f"'{producto.nombre}' no tiene stock disponible.")
        return redirect("cart_detail")

    # Por ahora cantidad fija 1 (se puede editar en el carrito)
    cart.add(producto, quantity=1)

    # OJO: sin messages.success → no aparecerá el mensaje verde
    return redirect("cart_detail")


def cart_remove(request, product_id):
    """
    Elimina un producto del carrito (cuando todavía existe en la BD).
    """
    cart = Cart(request)
    producto = get_object_or_404(Producto, id=product_id)
    cart.remove(producto)
    messages.info(request, f"'{producto.nombre}' se eliminó del carrito.")
    return redirect("cart_detail")


def cart_remove_by_id(request, product_id):
    """
    Elimina un ítem del carrito sin consultar a la BD.
    Sirve cuando el producto ya fue borrado.
    """
    cart = Cart(request)
    cart.remove_by_id(product_id)
    messages.info(
        request,
        "Un producto eliminado ya no está disponible y se quitó del carrito.",
    )
    return redirect("cart_detail")


def cart_update(request, product_id):
    """
    Actualiza la cantidad de un producto desde el carrito.
    - Si la cantidad es 0 o negativa, se elimina del carrito.
    - Si supera el stock, se ajusta al máximo disponible.
    """
    cart = Cart(request)
    producto = get_object_or_404(Producto, id=product_id)

    try:
        quantity = int(request.POST.get("quantity", 1))
    except (TypeError, ValueError):
        quantity = 1

    if quantity < 1:
        cart.remove(producto)
        messages.info(request, f"'{producto.nombre}' se eliminó del carrito.")
        return redirect("cart_detail")

    if quantity > producto.stock:
        quantity = producto.stock
        messages.warning(
            request,
            f"Solo hay {producto.stock} unidades disponibles de '{producto.nombre}'. "
            "Se ajustó la cantidad en el carrito.",
        )

    cart.add(producto, quantity=quantity, override_quantity=True)
    return redirect("cart_detail")


