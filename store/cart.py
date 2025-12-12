from decimal import Decimal

from .models import Producto

CART_SESSION_ID = "cart"


class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(CART_SESSION_ID)
        if cart is None:
            cart = self.session[CART_SESSION_ID] = {}
        self.cart = cart

    # ------------------- operaciones básicas -------------------

    def add(self, producto: Producto, quantity=1, override_quantity=False):
        """
        Agrega un producto al carrito o actualiza su cantidad.
        
        """
        product_id = str(producto.id)

        if product_id not in self.cart:
            self.cart[product_id] = {
                "quantity": 0,
                "price": str(producto.valor),  # guardamos como string para serializar
            }

        if override_quantity:
            self.cart[product_id]["quantity"] = quantity
        else:
            self.cart[product_id]["quantity"] += quantity

        # si llega a menos de 1, lo sacamos
        if self.cart[product_id]["quantity"] < 1:
            del self.cart[product_id]

        self.save()

    def remove(self, producto: Producto):
        """Elimina un producto que todavía existe en la BD."""
        product_id = str(producto.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def remove_by_id(self, product_id):
        """Elimina del carrito usando solo el ID (sirve si el producto fue borrado)."""
        product_id = str(product_id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def clear(self):
        """Vacía completamente el carrito."""
        if CART_SESSION_ID in self.session:
            del self.session[CART_SESSION_ID]
            self.session.modified = True

    def save(self):
        self.session[CART_SESSION_ID] = self.cart
        self.session.modified = True

    # ------------------- helpers para vistas/plantillas -------------------

    def __iter__(self):
        """
        Itera sobre los ítems del carrito y adjunta:

        - product: instancia de Producto o None si fue borrado
        - missing: True si el producto ya no existe
        - insufficient_stock: True si la cantidad del carrito es mayor al stock
        - total_price: precio total de ese ítem (0 si no se puede vender)
        """
        product_ids = list(self.cart.keys())
        productos = Producto.objects.filter(id__in=product_ids)
        productos_map = {str(p.id): p for p in productos}

        for product_id in product_ids:
            data = self.cart[product_id]
            quantity = data["quantity"]
            unit_price = Decimal(data["price"])

            producto = productos_map.get(product_id)

            if not producto:
                # producto eliminado de la BD
                yield {
                    "product": None,
                    "product_id": product_id,
                    "quantity": quantity,
                    "unit_price": unit_price,
                    "total_price": Decimal("0"),
                    "missing": True,
                    "insufficient_stock": False,
                }
                continue

            # stock insuficiente o sin stock
            insufficient = quantity > producto.stock or producto.stock <= 0

            total_price = producto.valor * quantity if not insufficient else Decimal("0")

            yield {
                "product": producto,
                "product_id": product_id,
                "quantity": quantity,
                "unit_price": producto.valor,
                "total_price": total_price,
                "missing": False,
                "insufficient_stock": insufficient,
            }

    @property
    def total_quantity(self) -> int:
        """Cantidad total de unidades (no de productos distintos)."""
        return sum(item["quantity"] for item in self.cart.values())

    def get_total_price(self) -> Decimal:
        """Total considerando solo ítems válidos y con stock."""
        total = Decimal("0")
        for item in self:
            total += item["total_price"]
        return total
