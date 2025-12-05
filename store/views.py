from django.shortcuts import render, get_object_or_404, redirect
from .models import Producto
from .forms import ProductoForm


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
            # Volvemos a la lista de productos al guardar
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
        return redirect("product_list")

    context = {
        "producto": producto,
    }
    return render(request, "store/product_confirm_delete.html", context)
