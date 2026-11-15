import json

from django.http import Http404, HttpResponseBadRequest, JsonResponse, StreamingHttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from . import bots


def _clave(request) -> str:
    if not request.session.session_key:
        request.session.create()
    return request.session.session_key


def index(request, nombre=None):
    lista = bots.listar_bots()
    if not lista:
        return render(request, "chat/index.html", {"bots": [], "activo": None, "mensajes": []})
    if nombre is None:
        return redirect("bot", nombre=lista[0])
    if nombre not in lista:
        raise Http404("Bot no encontrado")
    mensajes = bots.historial_para_ui(_clave(request), nombre)
    return render(request, "chat/index.html",
                  {"bots": lista, "activo": nombre, "mensajes": mensajes})


@require_POST
def enviar(request, nombre):
    if nombre not in bots.listar_bots():
        raise Http404("Bot no encontrado")
    try:
        texto = json.loads(request.body).get("texto", "").strip()
    except (ValueError, AttributeError):
        return HttpResponseBadRequest("JSON inválido")
    if not texto:
        return HttpResponseBadRequest("Mensaje vacío")
    resp = StreamingHttpResponse(
        bots.responder(_clave(request), nombre, texto),
        content_type="text/plain; charset=utf-8",
    )
    resp["Cache-Control"] = "no-cache"
    resp["X-Accel-Buffering"] = "no"
    return resp


@require_POST
def reiniciar(request, nombre):
    bots.reiniciar(_clave(request), nombre)
    return JsonResponse({"ok": True})
