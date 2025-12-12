import logging

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .models import Producto
from firebase_app import get_db

logger = logging.getLogger(__name__)


def producto_to_doc(producto: Producto) -> dict:
    generos = list(producto.generos.values_list("nombre", flat=True))
    fecha_lanzamiento = (
        producto.anio_lanzamiento.isoformat()
        if producto.anio_lanzamiento
        else None
    )
    imagen_url = producto.imagen.url if producto.imagen else None

    return {
        "nombre": producto.nombre,
        "anio_lanzamiento": fecha_lanzamiento,
        "plataforma": producto.plataforma,
        "formato": producto.formato,
        "estado": producto.estado,
        "generos": generos,
        "descripcion": producto.descripcion,
        "valor": float(producto.valor),
        "stock": producto.stock,
        "imagen_url": imagen_url,
        "creado_en": producto.creado_en.isoformat()
        if producto.creado_en
        else None,
        "actualizado_en": producto.actualizado_en.isoformat()
        if producto.actualizado_en
        else None,
    }


@receiver(post_save, sender=Producto)
def sync_producto_firestore(sender, instance: Producto, **kwargs):
    try:
        db = get_db()
        doc_ref = db.collection("productos").document(str(instance.id))
        doc_ref.set(producto_to_doc(instance), merge=True)
    except Exception as e:
        # No rompemos la app, solo dejamos log
        logger.error(
            "Error al sincronizar producto %s con Firebase: %s",
            instance.id,
            str(e),
        )


@receiver(post_delete, sender=Producto)
def delete_producto_firestore(sender, instance: Producto, **kwargs):
    try:
        db = get_db()
        db.collection("productos").document(str(instance.id)).delete()
    except Exception as e:
        logger.error(
            "Error al eliminar producto %s de Firebase: %s",
            instance.id,
            str(e),
        )

