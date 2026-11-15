"""API REST opcional (FastAPI) sobre el mismo bot. No la usa la interfaz Django.

Ejecutar:  uvicorn api:app --host 0.0.0.0 --port 8001
"""
import os
import sys

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import ollama

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "bots"))

from ChatLLM import (  # noqa: E402
    RUTA_BC, cargar_conocimiento, construir_prompt_sistema,
    es_saludo, cargar_historial, guardar_historial,
    buscar_similares, bloque_ejemplos, MODELO, RECORDATORIO,
)

app = FastAPI()

# Permitir peticiones desde otro frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

cliente_ollama = ollama.Client(
    host=os.getenv("OLLAMA_HOST", "http://host.docker.internal:11434")
)

conocimiento = cargar_conocimiento(RUTA_BC)
SISTEMA = {"role": "system", "content": construir_prompt_sistema(conocimiento)}


class MensajeEntrada(BaseModel):
    mensaje: str
    historial: list[dict] = []  # El frontend mantiene el historial de la sesión


@app.post("/chatllm")
def chat_llm(datos: MensajeEntrada):
    texto = datos.mensaje.strip()
    if es_saludo(texto):
        return {"respuesta": "¡Hola! Pregúntame por juegos: developers, géneros, "
                             "plataformas, puntajes o años."}

    historial_qa = cargar_historial()
    mensajes = [SISTEMA]
    ejemplos = bloque_ejemplos(buscar_similares(texto, historial_qa))
    if ejemplos:
        mensajes.append(ejemplos)

    mensajes += datos.historial
    mensajes.append({"role": "user", "content": texto + RECORDATORIO})

    res = cliente_ollama.chat(
        model=MODELO,
        messages=mensajes,
        options={"temperature": 0, "num_ctx": 8192, "num_predict": 400},
    )
    respuesta = res["message"]["content"]

    if "no tengo información" not in respuesta.lower():
        historial_qa = [qa for qa in historial_qa
                        if qa["pregunta"].lower() != texto.lower()]
        historial_qa.append({"pregunta": texto, "respuesta": respuesta})
        guardar_historial(historial_qa)

    return {"respuesta": respuesta}
