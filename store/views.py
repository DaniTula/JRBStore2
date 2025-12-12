# store/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.contrib import messages
from .models import Producto, Genero
from .cart import Cart
from .forms import ProductoForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from .forms import ProductoForm, UserRegisterForm, UserLoginForm


# ---------------------------------------------------------------------------
#  Choices locales para filtros (deben coincidir con lo que guarda tu modelo)
# ---------------------------------------------------------------------------
PLATAFORMA_CHOICES = [
    ("PS3", "PS3"),
    ("PS4", "PS4"),
    ("PS5", "PS5"),
]

FORMATO_CHOICES = [
    ("FISICO", "Físico"),
    ("DIGITAL", "Digital"),
]


# ---------------------------------------------------------------------------
#  PÁGINA PRINCIPAL (CATÁLOGO + BÚSQUEDA + FILTROS)
# ---------------------------------------------------------------------------
def home(request):
    """
    Página principal de la tienda.

    Permite:
    - Buscar por nombre / descripción (parámetro GET: q).
    - Filtrar por plataforma (plataforma).
    - Filtrar por tipo/formato (tipo).
    - Filtrar por uno o varios géneros (generos).
    - Filtrar por rango de precio (precio_min / precio_max).
    """

    productos = Producto.objects.all().order_by("-creado_en")

    # -------------------- Leer parámetros GET --------------------
    q = request.GET.get("q", "").strip()
    plataforma = request.GET.get("plataforma", "").strip()
    tipo = request.GET.get("tipo", "").strip()
    genero_ids_raw = request.GET.getlist("generos")
    precio_min_raw = request.GET.get("precio_min", "").strip()
    precio_max_raw = request.GET.get("precio_max", "").strip()

    # -------------------- Búsqueda (texto libre) --------------------
    if q:
        productos = productos.filter(
            Q(nombre__icontains=q) | Q(descripcion__icontains=q)
        )

    # -------------------- Filtro: plataforma --------------------
    valid_plataformas = {code for code, _ in PLATAFORMA_CHOICES}
    if plataforma and plataforma in valid_plataformas:
        productos = productos.filter(plataforma=plataforma)
    else:
        plataforma = ""  # valor limpio para el template

    # -------------------- Filtro: tipo / formato --------------------
    valid_tipos = {code for code, _ in FORMATO_CHOICES}
    if tipo and tipo in valid_tipos:
        productos = productos.filter(formato=tipo)
    else:
        tipo = ""

    # -------------------- Filtro: géneros (múltiples) --------------------
    selected_generos = []
    if genero_ids_raw:
        try:
            genero_ids = [int(g) for g in genero_ids_raw if g.isdigit()]
        except ValueError:
            genero_ids = []
        if genero_ids:
            productos = productos.filter(generos__id__in=genero_ids).distinct()
            selected_generos = genero_ids

    # -------------------- Filtro: rango de precio --------------------
    def parse_price(value: str):
        """
        Convierte string a entero >= 0.
        Devuelve None si no es válido.
        """
        try:
            v = int(value)
            return v if v >= 0 else 0
        except (TypeError, ValueError):
            return None

    precio_min = parse_price(precio_min_raw) if precio_min_raw else None
    precio_max = parse_price(precio_max_raw) if precio_max_raw else None

    # Si el usuario pone min > max, los invertimos para que tenga sentido.
    if precio_min is not None and precio_max is not None and precio_min > precio_max:
        precio_min, precio_max = precio_max, precio_min

    if precio_min is not None:
        productos = productos.filter(valor__gte=precio_min)
    if precio_max is not None:
        productos = productos.filter(valor__lte=precio_max)

    # -------------------- Datos para el template --------------------
    filters = {
        "q": q,
        "plataforma": plataforma,
        "tipo": tipo,
        "generos": selected_generos,
        "precio_min": precio_min_raw,
        "precio_max": precio_max_raw,
    }

    context = {
        "productos": productos,
        "plataformas": PLATAFORMA_CHOICES,
        "formatos": FORMATO_CHOICES,
        "generos_disponibles": Genero.objects.all().order_by("nombre"),
        "filters": filters,
    }
    return render(request, "store/home.html", context)


# ---------------------------------------------------------------------------
#  MÓDULO DE STOCK / CRUD DE PRODUCTOS (PANEL ADMIN)
# ---------------------------------------------------------------------------
def producto_list(request):
    """
    Vista de administración de productos (módulo de stock).
    Muestra una tabla con todos los productos y botones para crear/editar/eliminar.
    """
    productos = Producto.objects.all().order_by("id")
    context = {"productos": productos}
    return render(request, "store/product_list.html", context)


def producto_create(request):
    """
    Crea un producto nuevo.
    Muestra un formulario y guarda en la base de datos si los datos son válidos.
    """
    if request.method == "POST":
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            producto = form.save()
            messages.success(request, f"Producto '{producto.nombre}' creado correctamente.")
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
            producto = form.save()
            messages.success(request, f"Producto '{producto.nombre}' actualizado correctamente.")
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
        nombre = producto.nombre
        producto.delete()
        messages.info(request, f"Producto '{nombre}' eliminado correctamente.")
        return redirect("product_list")

    context = {"producto": producto}
    return render(request, "store/product_confirm_delete.html", context)


# ---------------------------------------------------------------------------
#  CARRITO DE COMPRAS
# ---------------------------------------------------------------------------
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
        # Envío fijo de ejemplo
        shipping = 3000

    grand_total = total_products + shipping

    # Si hay productos con problemas, se muestra un aviso general
    if any(i.get("missing") or i.get("insufficient_stock") for i in items):
        messages.warning(
            request,
            "Algunos productos del carrito ya no están disponibles o no tienen stock. "
            "Revisa los mensajes junto a cada producto antes de continuar.",
        )

    context = {
        "cart_items": items,
        "total_products": total_products,
        "shipping": shipping,
        "grand_total": grand_total,
        "quantity_range": range(1, 11),  # para el select de cantidad (1..10)
    }
    return render(request, "store/cart_detail.html", context)


def cart_add(request, product_id):
    """
    Agrega un producto al carrito (cantidad por defecto 1).
    """
    cart = Cart(request)
    producto = get_object_or_404(Producto, id=product_id)

    # Validación de stock
    if producto.stock < 1:
        messages.warning(
            request,
            f"El producto '{producto.nombre}' ya no tiene stock disponible."
        )
        return redirect("cart_detail")

    quantity = 1
    # 👇 AQUÍ EL CAMBIO IMPORTANTE: usar `producto` como parámetro POSICIONAL
    cart.add(producto, quantity=quantity)

    # Sin mensaje de éxito estridente
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
    Se usa cuando el producto ya fue borrado de la base de datos.
    """
    cart = Cart(request)
    cart.remove_by_id(product_id)
    messages.info(
        request,
        "Un producto que ya no existe en la tienda fue eliminado del carrito.",
    )
    return redirect("cart_detail")


def cart_update(request, product_id):
    """
    Actualiza la cantidad de un producto desde el carrito.
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

    # 👇 También aquí: parámetro posicional
    cart.add(producto, quantity=quantity, override_quantity=True)
    return redirect("cart_detail")


# --------------------------- AUTENTICACIÓN Y CUENTA ---------------------------

def register(request):
    """
    Registro de nuevos clientes.
    Crea un usuario y lo inicia sesión automáticamente.
    """
    if request.user.is_authenticated:
        return redirect("account_dashboard")

    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(
                request,
                f"Bienvenido/a, {user.get_full_name() or user.username}. "
                "Tu cuenta ha sido creada correctamente."
            )
            return redirect("account_dashboard")
    else:
        form = UserRegisterForm()

    return render(request, "accounts/register.html", {"form": form})


def login_view(request):
    """
    Inicio de sesión de usuarios existentes.
    """
    if request.user.is_authenticated:
        return redirect("account_dashboard")

    if request.method == "POST":
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(
                request,
                f"Bienvenido de nuevo, {user.get_full_name() or user.username}."
            )
            next_url = request.GET.get("next") or "account_dashboard"
            return redirect(next_url)
    else:
        form = UserLoginForm(request)

    return render(request, "accounts/login.html", {"form": form})


@login_required
def logout_view(request):
    """
    Cierre de sesión.
    """
    logout(request)
    messages.info(request, "Has cerrado sesión correctamente.")
    return redirect("home")


@login_required
def account_dashboard(request):
    """
    Panel de cuenta.
    - Si es staff/admin: muestra accesos rápidos al panel de gestión.
    - Si es cliente: resumen simple de su cuenta.
    """
    return render(request, "accounts/dashboard.html", {})




