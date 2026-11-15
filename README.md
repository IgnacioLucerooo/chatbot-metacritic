# Chatbot de videojuegos (Metacritic) — Prolog + LLM + Django

Chatbot que responde preguntas sobre videojuegos (developer, género, plataformas,
año, metascore y user score) usando **solo** una base de conocimientos en Prolog
construida con datos de [Metacritic](https://www.metacritic.com).

- `bots/BdC-videojuegos.pl` → base de conocimientos (Prolog).
- `bots/ChatLLM.py` → lee la base con `pyswip`, arma el prompt y consulta al LLM
  (`llama3.2` vía Ollama). También funciona solo por consola.
- `chat/` → interfaz web en Django con respuestas en streaming.
- `bots/historial_qa.json` → preguntas ya respondidas que se usan como ejemplos.
  Se crea solo al usar el bot (no está en el repositorio).

## Ejecutar con Docker (recomendado)

Requisitos: solo [Docker](https://www.docker.com/products/docker-desktop/) (incluye Docker Compose).
No hace falta instalar Python, Prolog ni Ollama.

```bash
git clone https://github.com/IgnacioLucerooo/chatbot-metacritic.git
cd chatbot-metacritic
docker compose up --build
```

Luego abrir **http://localhost:8000**.

> La primera vez se descarga el modelo `llama3.2` (~2 GB) dentro del contenedor
> `ollama`; la web parte cuando la descarga termina. Las siguientes veces parte
> de inmediato porque el modelo queda guardado en un volumen de Docker.

Para detener: `Ctrl + C` y luego `docker compose down`.

## Configuración

El proyecto **no usa claves de API ni contraseñas**: el LLM corre localmente con Ollama.
Funciona sin configurar nada; opcionalmente se pueden ajustar variables de entorno
copiando el ejemplo:

```bash
cp .env.example .env      # en Windows: copy .env.example .env
```

| Variable | Para qué sirve | Valor por defecto |
|---|---|---|
| `DJANGO_SECRET_KEY` | Firma las cookies de sesión de Django | Aleatoria en cada arranque |
| `DJANGO_DEBUG` | `1` muestra errores detallados, `0` los oculta | `1` |
| `OLLAMA_HOST` | Dirección del servidor Ollama | `http://ollama:11434` (contenedor) |

El archivo `.env` está en `.gitignore`, así que nunca se sube al repositorio.

## Ejecutar sin Docker

Requisitos: Python 3.11+, [SWI-Prolog](https://www.swi-prolog.org/) y [Ollama](https://ollama.com).

```bash
pip install -r requirements.txt
ollama pull llama3.2          # con Ollama corriendo (por defecto se usa localhost:11434)
python manage.py runserver
```

Versión por consola: `python bots/ChatLLM.py`

## Cómo funciona

1. Prolog carga los hechos `juegos(Titulo, Año, Plataformas, Genero, Metascore, UserScore, Developer)`.
2. Python los convierte a texto (ficha por juego + agrupación por developer, género y plataforma)
   y los pone en el prompt del sistema, con reglas para **no inventar** datos.
3. Los saludos se responden sin llamar al LLM.
4. Se buscan preguntas parecidas en `historial_qa.json` y se agregan como ejemplos.
5. El LLM responde en streaming; si la respuesta no es un rechazo, se guarda en el historial.

## API opcional (FastAPI)

`api.py` expone el mismo bot como `POST /chatllm` (`{"mensaje": "...", "historial": []}`):

```bash
uvicorn api:app --host 0.0.0.0 --port 8001
```
