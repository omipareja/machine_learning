# Predicción de nota final

API y cliente web que estiman la nota final de un estudiante (escala de 0 a 5) a partir de su programa, edad, estrato, promedio anterior, horas de estudio, asistencia y si trabaja. El modelo es una regresión lineal de scikit-learn, entrenada con `app/data/rendimiento-estudiantes.csv` y guardada en `app/models/modelo.pkl`.

## Cómo funciona

Streamlit no calcula la nota. Junta los datos del formulario y se los manda a la API. FastAPI valida el pedido, carga el modelo guardado y devuelve la nota estimada.

1. `streamlit_app.py` envía `POST /train` o `POST /predict` a `http://127.0.0.1:8000`.
2. `main.py` recibe el pedido y lo deriva al router que corresponde.
3. `POST /train` lee el CSV, ajusta el modelo y lo guarda en `app/models/modelo.pkl`. Si ese archivo ya existe, no vuelve a entrenar.
4. `POST /predict` valida los campos, carga el archivo guardado y responde `nota_final`.

El modelo es un `Pipeline` de scikit-learn. A las variables numéricas les imputa la mediana y las escala. A `programa` le aplica one-hot. Después entra una regresión lineal. `trabaja` se guarda como 0 o 1.

## Estructura

```text
.
├── main.py                         # Crea la API y registra las rutas
├── streamlit_app.py                # Formulario que consume la API
├── pyproject.toml                  # Dependencias y versión de Python
├── app/
│   ├── api/
│   │   ├── seed.py                 # POST /train
│   │   └── predict.py              # POST /predict
│   ├── schemas/
│   │   └── predict.py              # Campos de entrada y de respuesta
│   ├── utils/
│   │   └── train_model.py          # Datos, pipeline y archivo del modelo
│   ├── data/
│   │   └── rendimiento-estudiantes.csv
│   └── models/
│       └── modelo.pkl              # Modelo entrenado
├── assets/
│   └── identificador_utp.png
└── .streamlit/
    └── config.toml                 # Tema visual del cliente
```

Los comandos hay que lanzarlos desde esta raíz: el entrenamiento y el logo usan rutas relativas a esa carpeta.

## Cómo ejecutarlo

Hace falta Python 3.12 y [uv](https://docs.astral.sh/uv/). Todos los comandos se corren desde la raíz del proyecto.

1. Instalar dependencias:

```bash
uv sync
```

2. Levantar la API (queda en `http://127.0.0.1:8000`; la documentación interactiva está en `http://127.0.0.1:8000/docs`):

```bash
uv run python main.py
```

3. En otra terminal, levantar el cliente:

```bash
uv run streamlit run streamlit_app.py
```

4. En la interfaz, pulsar **Entrenar modelo** y después **Predecir nota**. Si `app/models/modelo.pkl` ya existe, el entrenamiento no se repite y la API responde `Seed already created`.

## API

| Método y ruta | Qué hace |
| --- | --- |
| `POST /train` | Entrena el modelo y lo guarda, solo si `modelo.pkl` todavía no existe. |
| `POST /predict` | Devuelve `nota_final` estimada. |

Ejemplo de predicción:

```bash
curl -X POST http://127.0.0.1:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "programa": "Sistemas",
    "edad": 25,
    "estrato": 3,
    "promedio_anterior": 3.8,
    "horas_estudio_semana": 12,
    "asistencia_pct": 85,
    "trabaja": false
  }'
```

`programa` acepta `Civil`, `Electrica`, `Industrial` o `Sistemas`.
