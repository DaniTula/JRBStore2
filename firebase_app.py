from pathlib import Path

import firebase_admin
from firebase_admin import credentials, firestore

_firebase_app = None
_db = None


def get_db():
    """
    Devuelve una instancia de Firestore.
    Inicializa Firebase solo la primera vez que se llama.
    """
    global _firebase_app, _db

    if _db is not None:
        return _db

    base_dir = Path(__file__).resolve().parent
    cred_path = base_dir / "firebase-key.json"

    if not cred_path.exists():
        raise FileNotFoundError(
            f"No se encontró el archivo de credenciales de Firebase: {cred_path}"
        )

    cred = credentials.Certificate(str(cred_path))
    _firebase_app = firebase_admin.initialize_app(cred)
    _db = firestore.client()
    return _db
