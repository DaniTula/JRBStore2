from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .models import Producto
from firebase_app import get_db  # usamos el mismo get_db que ya usaste en firebase_test


def producto_to_doc(producto: Producto) -> dict:
    """
    Convierte un Producto de Django en un diccionario listo para guardar en Firestore.
    """
    # Lista de géneros por nombre
    generos = list(producto.generos.values_list("nombre", flat=True))

    # Fecha de lanzamiento en formato ISO (YYYY-MM-DD)
    fecha_lanzamiento = (
        producto.anio_lanzamiento.isoformat()
        if producto.anio_lanzamiento
        else None
    )

    # URL de imagen (si existe)
    image_url = producto.imagen.url if producto.imagen else None

    return {
        "nombre": producto.nombre,
        "anio_lanzamiento": fecha_lanzamiento,
        "plataforma": producto.plataforma,
        "formato": producto.formato,
        "estado": producto.estado,
        "generos": generos,  # lista de strings
        "descripcion": producto.descripcion,
        "valor": float(producto.valor),
        "imagen_url": image_url,
        "stock": producto.stock,
        "creado_en": producto.creado_en.isoformat() if producto.creado_en else None,
        "actualizado_en": producto.actualizado_en.isoformat()
        if producto.actualizado_en
        else None,
    }


@receiver(post_save, sender=Producto)
def sync_producto_firestore(sender, instance: Producto, **kwargs):
    """
    Cada vez que se crea o actualiza un Producto,
    se escribe/actualiza el documento correspondiente en Firestore.
    """
    db = get_db()
    doc_ref = db.collection("productos").document(str(instance.id))
    doc_ref.set(producto_to_doc(instance), merge=True)


@receiver(post_delete, sender=Producto)
def delete_producto_firestore(sender, instance: Producto, **kwargs):
    """
    Cuando se elimina un Producto en Django,
    eliminamos también su documento en Firestore.
    """
    db = get_db()
    db.collection("productos").document(str(instance.id)).delete()
