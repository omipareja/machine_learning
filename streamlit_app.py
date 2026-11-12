"""Minimal Streamlit client for the local grade-prediction API."""

import base64
import json
import urllib.error
import urllib.request
from pathlib import Path

import streamlit as st

API_DEFAULT = "http://127.0.0.1:8000"
LOGO = Path("assets/identificador_utp.png")
PROGRAMAS = ["Civil", "Electrica", "Industrial", "Sistemas"]
MENSAJES_TRAIN = {
    "Seed already created": "El modelo ya estaba entrenado.",
    "Seed created successfully": "El modelo se entrenó y quedó guardado.",
}

st.set_page_config(
    page_title="Predicción de nota · UTP",
    layout="centered",
)


def post(base: str, path: str, payload: dict | None = None):
    url = base.rstrip("/") + path
    data = None if payload is None else json.dumps(payload).encode()
    headers = {"Accept": "application/json"}
    if data is not None:
        headers["Content-Type"] = "application/json"
    request = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            raw = response.read().decode()
            return response.status, json.loads(raw) if raw else {}
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode()
        try:
            body = json.loads(raw) if raw else {}
        except json.JSONDecodeError:
            body = {"detail": raw or exc.reason}
        return exc.code, body
    except urllib.error.URLError as exc:
        return None, {"detail": f"No hay conexión con la API: {exc.reason}"}


def texto_error(body: dict) -> str:
    detail = body.get("detail", body)
    if isinstance(detail, list):
        partes = []
        for item in detail:
            lugar = ".".join(str(parte) for parte in item.get("loc", []))
            partes.append(f"{lugar}: {item.get('msg', item)}")
        return "; ".join(partes)
    return str(detail)


def banner():
    logo = base64.b64encode(LOGO.read_bytes()).decode()
    st.markdown(
        f"""
        <style>
          .block-container {{
            padding-top: 2rem;
            max-width: 40rem;
          }}
          header[data-testid="stHeader"] {{
            background: transparent;
          }}
          .banner {{
            background: #003D6D;
            border-radius: 16px;
            padding: 18px 24px;
            margin-bottom: 1.25rem;
          }}
          .banner img {{
            height: 68px;
            width: auto;
            display: block;
          }}
          .nota {{
            color: #A91E2C;
            font-size: 3rem;
            font-weight: 650;
            line-height: 1;
            margin: 0.25rem 0 0;
          }}
        </style>
        <div class="banner">
          <img alt="Universidad Tecnológica de Pereira" src="data:image/png;base64,{logo}" />
        </div>
        """,
        unsafe_allow_html=True,
    )


banner()
st.title("Predicción de nota final")
st.caption("Cliente para probar la API local de rendimiento estudiantil.")

base = st.text_input("URL de la API", value=API_DEFAULT)

if st.button("Entrenar modelo"):
    status, body = post(base, "/train")
    if status == 200:
        mensaje = body.get("message", "")
        st.success(MENSAJES_TRAIN.get(mensaje, mensaje or "Listo."))
    else:
        st.error(texto_error(body))

with st.form("prediccion"):
    programa = st.selectbox("Programa", PROGRAMAS)
    edad, estrato = st.columns(2)
    with edad:
        edad_valor = st.number_input("Edad", min_value=16, max_value=70, value=25, step=1)
    with estrato:
        estrato_valor = st.number_input("Estrato", min_value=1, max_value=6, value=3, step=1)
    promedio = st.number_input(
        "Promedio anterior",
        min_value=0.0,
        max_value=5.0,
        value=3.8,
        step=0.1,
        format="%.1f",
    )
    horas, asistencia = st.columns(2)
    with horas:
        horas_valor = st.number_input(
            "Horas de estudio por semana",
            min_value=0,
            max_value=60,
            value=12,
            step=1,
        )
    with asistencia:
        asistencia_valor = st.number_input(
            "Asistencia (%)",
            min_value=0,
            max_value=100,
            value=85,
            step=1,
        )
    trabaja = st.toggle("Trabaja")
    predecir = st.form_submit_button("Predecir nota", type="primary")

if predecir:
    payload = {
        "programa": programa,
        "edad": int(edad_valor),
        "estrato": int(estrato_valor),
        "promedio_anterior": float(promedio),
        "horas_estudio_semana": int(horas_valor),
        "asistencia_pct": int(asistencia_valor),
        "trabaja": bool(trabaja),
    }
    status, body = post(base, "/predict", payload)
    st.session_state["resultado"] = {"status": status, "body": body, "payload": payload}

resultado = st.session_state.get("resultado")
if resultado:
    status = resultado["status"]
    body = resultado["body"]
    if status == 200 and "nota_final" in body:
        st.markdown(f'<p class="nota">{body["nota_final"]:.2f}</p>', unsafe_allow_html=True)
        st.caption("Nota final estimada, en la escala de 0 a 5.")
    else:
        st.error(texto_error(body))
        if status == 500:
            st.caption("Si el modelo todavía no existe, use Entrenar modelo.")
    with st.expander("Solicitud y respuesta"):
        st.json({"solicitud": resultado["payload"], "estado": status, "respuesta": body})
