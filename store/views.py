from django.shortcuts import render
from django.http import HttpResponse
from firebase_app import get_db


def home(request):
    return HttpResponse("Bienvenido a JRBStore2 🐍🛒 - Store funcionando.")

def firebase_test(request):
    db = get_db()
    # Creamos / actualizamos un documento de prueba
    doc_ref = db.collection("tests").document("jrbstore2")
    doc_ref.set({
        "mensaje": "Hola desde Django + Firebase",
        "ok": True,
    })
    return HttpResponse("Firebase OK: se escribió el documento en Firestore.")