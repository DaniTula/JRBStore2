from django.shortcuts import render


def home(request):
    """
    Vista principal del sitio.
    Solo renderiza la plantilla con el layout de catálogo.
    Todavía no hay lógica de productos ni filtros.
    """
    return render(request, "store/home.html")