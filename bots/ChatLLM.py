"""Chatbot de videojuegos con LLM (Ollama) + Python sobre BdC-videojuegos.pl"""
import json
import os
from difflib import SequenceMatcher

import ollama
from pyswip import Prolog

CARPETA = os.path.dirname(os.path.abspath(__file__))
RUTA_BC = os.path.join(CARPETA, "BdC-videojuegos.pl").replace("\\", "/")
RUTA_HISTORIAL = os.path.join(CARPETA, "historial_qa.json")

MODELO = "llama3.2"
UMBRAL = 0.6         # qué tan parecida debe ser una pregunta (0 a 1)
MAX_EJEMPLOS = 3     # cuántas preguntas parecidas se le pasan al LLM

RECORDATORIO = (
    "\n\n(Si preguntan por un videojuego o dato que no está en la base de "
    "conocimientos, responde que no tienes información. No uses conocimiento propio.)"
)

SALUDOS = {"hola", "holi", "buenas", "buenos dias", "buenas tardes",
           "buenas noches", "hey", "ey", "que tal", "como estas"}


def bonito(atomo) -> str:
    return str(atomo).replace("_", " ").title()


# ---------- 1. Conocimiento: Prolog -> texto ----------
def cargar_conocimiento(ruta: str) -> str:
    prolog = Prolog()
    prolog.consult(ruta)
    lineas = []
    por_dev, por_genero, por_plat = {}, {}, {}

    for r in prolog.query("juegos(T,A,P,G,M,U,D)"):
        titulo = bonito(r["T"])
        plataformas = [bonito(p) for p in r["P"]]
        meta = "sin metascore" if str(r["M"]) == "na" else r["M"]
        user = "sin user score" if str(r["U"]) == "na" else r["U"]
        lineas.append(
            f"- {titulo}: año {r['A']}, género {bonito(r['G'])}, "
            f"plataformas [{', '.join(plataformas)}], metascore {meta}, "
            f"user score {user}, developer {bonito(r['D'])}."
        )
        por_dev.setdefault(bonito(r["D"]), []).append(titulo)
        por_genero.setdefault(bonito(r["G"]), []).append(titulo)
        for p in plataformas:
            por_plat.setdefault(p, []).append(titulo)

    def agrupar(dic):
        return "\n".join(f"- {k}: {', '.join(v)}." for k, v in dic.items())

    return (
        "FICHA DE CADA JUEGO:\n" + "\n".join(lineas)
        + "\n\nJUEGOS POR DEVELOPER:\n" + agrupar(por_dev)
        + "\n\nJUEGOS POR GÉNERO:\n" + agrupar(por_genero)
        + "\n\nJUEGOS POR PLATAFORMA:\n" + agrupar(por_plat)
    )


# ---------- 2. Prompt del sistema ----------
def construir_prompt_sistema(conocimiento: str) -> str:
    return (
        "Eres un asistente de videojuegos. Tu ÚNICA fuente de información es la "
        "BASE DE CONOCIMIENTOS de abajo.\n"
        "REGLAS:\n"
        "1. Usa solo datos que aparezcan en la base. Nunca uses conocimiento propio.\n"
        "2. Si el juego, developer o dato NO está en la base, responde exactamente: "
        "\"No tengo información sobre eso en mi base de conocimientos.\" "
        "y nada más. No menciones ni sugieras juegos que no estén en la base.\n"
        "3. Si el usuario solo saluda o agradece, responde amablemente y "
        "ofrece ayuda con videojuegos.\n"
        "4. Responde en español, de forma breve.\n\n"
        "SINÓNIMOS: rating, raiting, puntaje, nota, calificación, reseña y score "
        "se refieren al metascore (críticos) y al user score (usuarios). "
        "Estudio, desarrolladora, compañía y creador se refieren al developer. "
        "Fecha de lanzamiento se refiere al año.\n\n"
        "EJEMPLO:\n"
        "Pregunta: ¿Cuándo salió Minecraft?\n"
        "Respuesta: No tengo información sobre eso en mi base de conocimientos.\n\n"
        "BASE DE CONOCIMIENTOS:\n" + conocimiento
    )


# ---------- 3. Saludos (se resuelven sin llamar al LLM) ----------
def es_saludo(texto: str) -> bool:
    limpio = texto.lower().strip(" ¡!¿?.,")
    return limpio in SALUDOS


# ---------- 4. Preguntas y respuestas guardadas ----------
def cargar_historial() -> list[dict]:
    if not os.path.exists(RUTA_HISTORIAL):
        return []
    try:
        with open(RUTA_HISTORIAL, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return []


def guardar_historial(historial_qa: list[dict]):
    with open(RUTA_HISTORIAL, "w", encoding="utf-8") as f:
        json.dump(historial_qa, f, ensure_ascii=False, indent=2)


def similitud(a: str, b: str) -> float:
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def buscar_similares(pregunta: str, historial_qa: list[dict]) -> list[dict]:
    puntuados = [(similitud(pregunta, qa["pregunta"]), qa) for qa in historial_qa]
    puntuados = [p for p in puntuados if p[0] >= UMBRAL]
    puntuados.sort(key=lambda p: p[0], reverse=True)
    return [qa for _, qa in puntuados[:MAX_EJEMPLOS]]


def bloque_ejemplos(similares: list[dict]):
    if not similares:
        return None
    texto = ("PREGUNTAS PARECIDAS YA RESPONDIDAS (úsalas como guía; "
             "si contradicen la base de conocimientos, manda la base):\n")
    for qa in similares:
        texto += f"P: {qa['pregunta']}\nR: {qa['respuesta']}\n\n"
    return {"role": "system", "content": texto}


# ---------- 5. Llamada al LLM (con streaming) ----------
def preguntar_llm(mensajes: list[dict]) -> str:
    partes = []
    flujo = ollama.chat(
        model=MODELO,
        messages=mensajes,
        stream=True,
        options={"temperature": 0, "num_ctx": 8192, "num_predict": 400},
        keep_alive="30m",    # mantiene el modelo cargado en memoria
    )
    for trozo in flujo:
        texto = trozo["message"]["content"]
        print(texto, end="", flush=True)   # muestra la respuesta mientras se genera
        partes.append(texto)
    print()
    return "".join(partes)


# ---------- 6. Bucle de conversación ----------
def main():
    conocimiento = cargar_conocimiento(RUTA_BC)
    sistema = {"role": "system", "content": construir_prompt_sistema(conocimiento)}
    historial: list[dict] = []
    historial_qa = cargar_historial()

    print(f"Bot de videojuegos con LLM ({len(historial_qa)} respuestas guardadas) "
          "(escribe 'salir' para terminar)")
    while True:
        texto = input("Tú: ").strip()
        if not texto:
            continue
        if texto.lower() in {"salir", "chao", "adios"}:
            print("Bot: ¡Chao!")
            break

        if es_saludo(texto):
            print("Bot: ¡Hola! Pregúntame por juegos: developers, géneros, "
                  "plataformas, puntajes o años de lanzamiento.")
            continue

        historial.append({"role": "user", "content": texto})

        mensajes = [sistema]
        ejemplos = bloque_ejemplos(buscar_similares(texto, historial_qa))
        if ejemplos:
            mensajes.append(ejemplos)
        mensajes += historial
        # El recordatorio va solo en la copia que se envía, no en el historial
        mensajes[-1] = {"role": "user", "content": texto + RECORDATORIO}

        print("Bot: ", end="", flush=True)
        try:
            respuesta = preguntar_llm(mensajes)
        except Exception as e:
            print(f"\nBot: error al contactar al modelo ({e}). ¿Está corriendo Ollama?")
            historial.pop()
            continue

        historial.append({"role": "assistant", "content": respuesta})

        # No se guardan las respuestas de rechazo, para no reforzar errores
        if "no tengo información" not in respuesta.lower():
            historial_qa = [qa for qa in historial_qa
                            if qa["pregunta"].lower() != texto.lower()]
            historial_qa.append({"pregunta": texto, "respuesta": respuesta})
            guardar_historial(historial_qa)


if __name__ == "__main__":
    main()
