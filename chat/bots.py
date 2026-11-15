"""Descubre los .py de la carpeta bots/ y los adapta a una interfaz común.

Un bot es un módulo con las funciones de ChatLLM.py (cargar_conocimiento,
construir_prompt_sistema, es_saludo, buscar_similares, ...). Este adaptador
reutiliza esas funciones, pero sin input()/print(): entrega el texto por trozos
(streaming) para que la web lo muestre mientras se genera.
"""
import importlib.util
import json
import threading
from pathlib import Path

from django.conf import settings

_modulos: dict = {}
_estado: dict = {}          # (clave_sesion, bot) -> {"historial": [...]}
_lock = threading.Lock()


def listar_bots() -> list[str]:
    """Nombres de los .py disponibles (ej. 'ChatLLM.py')."""
    return sorted(p.name for p in Path(settings.BOTS_DIR).glob("*.py")
                  if not p.name.startswith("_"))


def _cargar_modulo(nombre: str):
    if nombre not in listar_bots():
        raise KeyError(nombre)
    if nombre not in _modulos:
        ruta = Path(settings.BOTS_DIR) / nombre
        spec = importlib.util.spec_from_file_location(ruta.stem, ruta)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        # Se construye una sola vez el prompt (lee el .pl con Prolog)
        mod._SISTEMA = {
            "role": "system",
            "content": mod.construir_prompt_sistema(mod.cargar_conocimiento(mod.RUTA_BC)),
        }
        _modulos[nombre] = mod
    return _modulos[nombre]


def _estado_de(clave: str, nombre: str) -> dict:
    with _lock:
        return _estado.setdefault((clave, nombre), {"historial": []})


def reiniciar(clave: str, nombre: str):
    with _lock:
        _estado.pop((clave, nombre), None)


def historial_para_ui(clave: str, nombre: str) -> list[dict]:
    return list(_estado_de(clave, nombre)["historial"])


def responder(clave: str, nombre: str, texto: str):
    """Generador: va entregando la respuesta del bot trozo a trozo."""
    mod = _cargar_modulo(nombre)
    est = _estado_de(clave, nombre)
    historial = est["historial"]          # lista de {"role","content"}

    # Saludos: se resuelven sin LLM (igual que en ChatLLM.py)
    if mod.es_saludo(texto):
        resp = ("¡Hola! Pregúntame por juegos: developers, géneros, "
                "plataformas, puntajes o años de lanzamiento.")
        historial.append({"role": "user", "content": texto})
        historial.append({"role": "assistant", "content": resp})
        yield resp
        return

    historial_qa = mod.cargar_historial()
    mensajes = [mod._SISTEMA]
    ejemplos = mod.bloque_ejemplos(mod.buscar_similares(texto, historial_qa))
    if ejemplos:
        mensajes.append(ejemplos)
    mensajes += historial
    mensajes.append({"role": "user", "content": texto + mod.RECORDATORIO})

    partes = []
    try:
        flujo = mod.ollama.chat(
            model=mod.MODELO,
            messages=mensajes,
            stream=True,
            options={"temperature": 0, "num_ctx": 8192, "num_predict": 400},
            keep_alive="30m",
        )
        for trozo in flujo:
            t = trozo["message"]["content"]
            partes.append(t)
            yield t
    except Exception as e:  # Ollama apagado, modelo no descargado, etc.
        yield f"Error al contactar al modelo ({e}). ¿Está corriendo Ollama?"
        return

    respuesta = "".join(partes)
    historial.append({"role": "user", "content": texto})
    historial.append({"role": "assistant", "content": respuesta})

    # Igual que ChatLLM.py: no se guardan los rechazos
    if "no tengo información" not in respuesta.lower():
        historial_qa = [qa for qa in historial_qa
                        if qa["pregunta"].lower() != texto.lower()]
        historial_qa.append({"pregunta": texto, "respuesta": respuesta})
        mod.guardar_historial(historial_qa)
