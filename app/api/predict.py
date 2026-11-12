import pandas as pd
from fastapi import APIRouter

from app.schemas.predict import PredictRequest, PredictResponse
from app.utils.train_model import load_model

router = APIRouter()

@router.post('/predict', response_model=PredictResponse)
def predict(request: PredictRequest):
    """ Realiza una predicción con el modelo cargado y retorna la nota final """
    modelo = load_model() 
    fila = pd.DataFrame([request.model_dump(mode="json")])
    fila["trabaja"] = fila["trabaja"].astype(int)
    prediccion = modelo.predict(fila)
    return PredictResponse(nota_final=float(prediccion[0]))
