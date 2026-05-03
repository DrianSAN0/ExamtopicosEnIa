# Topicos IA: Logistica-IA (Gestion de Inventario)

Agente de IA para gestion de inventarios en una red logistica de almacenes.
Permite consultar stock, ubicacion y estado de productos mediante lenguaje natural.

## Stack
- **Motor de IA:** DSPy con patron ReAct
- **Modelo:** gpt-4o-mini (OpenAI)
- **Backend:** FastAPI
- **Base de Datos:** SQLite
- **Python:** 3.12

## Como clonar y correr el proyecto

### 1. Clonar el repositorio
```bash
git clone https://github.com/DrianSAN0/ExamtopicosEnIa.git
cd ExamtopicosEnIa
```

### 2. Crear el archivo .env
Crear un archivo llamado .env en la raiz del proyecto:
```env
OPENAI_API_KEY=tu_clave_openai_aqui
```

### 3. Instalar dependencias
```bash
pip install uv
uv sync
```

### 4. Correr el servidor
```bash
uv run fastapi dev api.py
```

### 5. Probar la API
Abrir en el navegador: http://127.0.0.1:8000/docs

## Endpoints
- POST /logistics/queries - Consulta sincrona al agente
- POST /logistics/async_queries - Consulta asincrona
- GET /logistics/async_queries - Obtener resultado de consulta asincrona

## Ejemplos de consultas
- Cuantos monitores disponibles hay en Madrid?
- Que productos tienen estado DAMAGED en Barcelona?
- Muestra el inventario completo del almacen 1